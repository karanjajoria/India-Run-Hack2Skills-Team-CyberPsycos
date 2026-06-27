import time
import uuid
from typing import List, Dict, Tuple
from app.models.schemas import (
    JobDescription,
    CandidateProfile,
    CandidateResult,
    ScoreBreakdown,
    RankingResponse,
)
from app.services.vector_store import upsert_candidates, search_candidates, clear_collection

# ─── Scoring weights ──────────────────────────────────────────────────────────
WEIGHTS = {
    "semantic_fit": 0.35,
    "skill_match": 0.25,
    "experience_relevance": 0.20,
    "recency_progression": 0.10,
    "behavioral": 0.10,
}

FIT_BANDS = [
    (80, "Strong"),
    (65, "Good"),
    (45, "Moderate"),
    (0, "Weak"),
]


def _fit_band(score: float) -> str:
    for threshold, label in FIT_BANDS:
        if score >= threshold:
            return label
    return "Weak"


def _skill_overlap(candidate_skills: List[str], jd_skills: List[str]) -> Tuple[List[str], List[str], float]:
    """Return (matched, missing, ratio)."""
    if not jd_skills:
        return [], [], 1.0
    candidate_lower = {s.lower() for s in candidate_skills}
    matched, missing = [], []
    for skill in jd_skills:
        if skill.lower() in candidate_lower or any(skill.lower() in cs for cs in candidate_lower):
            matched.append(skill)
        else:
            missing.append(skill)
    ratio = len(matched) / len(jd_skills) if jd_skills else 1.0
    return matched, missing, ratio


def _experience_score(candidate: CandidateProfile, jd: JobDescription) -> float:
    years_needed = max(jd.min_years_experience, 1)
    years_have = candidate.total_years
    years_ratio = min(years_have / years_needed, 1.5) / 1.5

    domain_hits = 0
    domain_words = set(jd.domain.lower().split()) | {jd.title.lower()}
    for exp in candidate.experiences:
        desc_lower = (exp.description + " " + exp.role).lower()
        if any(dw in desc_lower for dw in domain_words if dw):
            domain_hits += 1
    domain_score = min(domain_hits / max(len(candidate.experiences), 1), 1.0)

    return years_ratio * 0.6 + domain_score * 0.4


def _recency_score(candidate: CandidateProfile, jd: JobDescription) -> float:
    if not candidate.experiences:
        return 0.3
    recent_exp = candidate.experiences[0]
    jd_skills_lower = [s.lower() for s in jd.must_have_skills]
    recent_skill_hit = sum(
        1 for s in jd_skills_lower
        if s in recent_exp.description.lower() or s in " ".join(recent_exp.skills_used).lower()
    )
    recency = min(recent_skill_hit / max(len(jd_skills_lower), 1), 1.0)
    progression = min(len(candidate.experiences) / 5, 1.0)
    return recency * 0.7 + progression * 0.3


def score_candidate(
    candidate: CandidateProfile,
    jd: JobDescription,
    semantic_score: float,
) -> Tuple[ScoreBreakdown, List[str], List[str]]:
    matched, missing_must, must_ratio = _skill_overlap(candidate.skills, jd.must_have_skills)
    _, _, pref_ratio = _skill_overlap(candidate.skills, jd.preferred_skills)
    skill_score = must_ratio * 0.7 + pref_ratio * 0.3

    exp_score = _experience_score(candidate, jd)
    recency = _recency_score(candidate, jd)

    behavioral = 0.5
    if jd.behavioral_indicators:
        hits = sum(1 for b in jd.behavioral_indicators if b.lower() in candidate.raw_text.lower())
        behavioral = min(hits / len(jd.behavioral_indicators), 1.0)

    total = (
        semantic_score * WEIGHTS["semantic_fit"]
        + skill_score * WEIGHTS["skill_match"]
        + exp_score * WEIGHTS["experience_relevance"]
        + recency * WEIGHTS["recency_progression"]
        + behavioral * WEIGHTS["behavioral"]
    ) * 100

    breakdown = ScoreBreakdown(
        semantic_fit=round(semantic_score * 100, 1),
        skill_match=round(skill_score * 100, 1),
        experience_relevance=round(exp_score * 100, 1),
        recency_progression=round(recency * 100, 1),
        total=round(total, 1),
    )
    return breakdown, matched, missing_must


def _fallback_semantic(candidate: CandidateProfile, jd: JobDescription) -> float:
    """Simple keyword overlap when embeddings unavailable."""
    jd_words = set(jd.raw_text.lower().split())
    cand_words = set(candidate.raw_text.lower().split())
    if not jd_words:
        return 0.5
    overlap = len(jd_words & cand_words) / len(jd_words)
    return min(overlap * 3, 1.0)  # scale up since raw overlap is low


def rank_candidates(
    jd: JobDescription,
    candidates: List[CandidateProfile],
    use_llm_explanations: bool = True,
) -> List[CandidateResult]:
    """Full ranking pipeline: embed → store → retrieve → rerank → explain."""
    from app.core.config import settings

    use_embeddings = True
    semantic_scores: Dict[str, float] = {}

    try:
        from app.services.embeddings import embed_text, embed_texts

        # Build candidate text representations
        candidate_texts = [
            f"{c.name}\n{c.summary}\n{' '.join(c.skills)}\n"
            + "\n".join(e.description for e in c.experiences)
            + "\n".join(c.projects)
            for c in candidates
        ]

        vecs = embed_texts(candidate_texts)

        # Clear and repopulate Qdrant
        clear_collection()
        points = [
            {
                "id": c.id,
                "vector": vecs[i],
                "payload": {
                    "name": c.name,
                    "skills": c.skills,
                    "total_years": c.total_years,
                    "summary": c.summary,
                },
            }
            for i, c in enumerate(candidates)
        ]
        upsert_candidates(points)

        # Embed JD and search
        jd_text = (
            f"{jd.title} {jd.domain}\n"
            f"Must have: {', '.join(jd.must_have_skills)}\n"
            f"Preferred: {', '.join(jd.preferred_skills)}\n"
            f"{jd.raw_text[:500]}"
        )
        jd_vec = embed_text(jd_text)
        top_retrieved = search_candidates(jd_vec, top_k=min(len(candidates), settings.top_k_retrieve))

        for hit in top_retrieved:
            semantic_scores[hit["id"]] = hit["score"]

    except Exception as e:
        print(f"⚠️  Embeddings unavailable ({e.__class__.__name__}), using keyword fallback")
        use_embeddings = False
        # Use keyword overlap as fallback semantic score
        for c in candidates:
            semantic_scores[c.id] = _fallback_semantic(c, jd)

    # Score all candidates (use retrieved order if embeddings worked, else all)
    scored = []
    for c in candidates:
        sem_score = semantic_scores.get(c.id, 0.3)
        breakdown, matched, missing = score_candidate(c, jd, sem_score)
        scored.append((c, breakdown, matched, missing))

    # Sort by total score
    scored.sort(key=lambda x: x[1].total, reverse=True)

    # Build output for top N
    output = []
    for rank, (candidate, breakdown, matched, missing) in enumerate(scored[: settings.top_k_shortlist], start=1):
        explanation = (
            f"{candidate.name} brings {candidate.total_years:.0f} years of experience "
            f"with {len(matched)} matched skills."
        )
        highlights = matched[:3] if matched else ["Profile reviewed"]

        if use_llm_explanations and settings.groq_api_key:
            try:
                from app.services.llm import generate_explanation
                explanation, highlights = generate_explanation(
                    candidate, jd, matched, missing, breakdown.total
                )
            except Exception as e:
                print(f"⚠️  LLM explanation failed for {candidate.name}: {e.__class__.__name__}")

        output.append(
            CandidateResult(
                id=candidate.id,
                name=candidate.name,
                rank=rank,
                score=breakdown.total,
                fit_band=_fit_band(breakdown.total),
                score_breakdown=breakdown,
                matched_skills=matched,
                missing_skills=missing,
                explanation=explanation,
                highlights=highlights,
            )
        )

    return output
