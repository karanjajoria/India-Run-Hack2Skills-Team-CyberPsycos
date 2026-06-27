import time
import uuid
import json
import csv
import io
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.models.schemas import RankingResponse, CandidateResult
from app.services.parser import extract_text_from_file, clean_text
from app.services.llm import parse_job_description, parse_candidate_profile
from app.services.ranker import rank_candidates

router = APIRouter(prefix="/api", tags=["ranking"])


@router.post("/rank", response_model=RankingResponse)
async def rank(request: Request):
    """
    Accepts multipart/form-data with:
      - jd_text (str, optional)
      - jd_file (file, optional)
      - candidate_files (one or more files, optional)
      - candidate_texts (JSON string: [{name, text}], optional)
    """
    start = time.time()

    form = await request.form()

    # ── 1. Get JD text ────────────────────────────────────────────────────────
    raw_jd = None

    jd_file = form.get("jd_file")
    if jd_file and hasattr(jd_file, "filename") and jd_file.filename:
        content = await jd_file.read()
        raw_jd = extract_text_from_file(jd_file.filename, content)

    if not raw_jd:
        jd_text = form.get("jd_text", "")
        if jd_text and jd_text.strip():
            raw_jd = jd_text.strip()

    if not raw_jd:
        raise HTTPException(status_code=400, detail="Provide a job description (jd_text or jd_file).")

    raw_jd = clean_text(raw_jd)

    # ── 2. Parse JD ───────────────────────────────────────────────────────────
    jd_parsed = parse_job_description(raw_jd)

    # ── 3. Collect candidate inputs ───────────────────────────────────────────
    candidate_inputs = []  # List of (id, name, text)

    # Multiple files — form.getlist returns all values for a key
    candidate_files = form.getlist("candidate_files")
    for f in candidate_files:
        if hasattr(f, "filename") and f.filename:
            content = await f.read()
            text = extract_text_from_file(f.filename, content)
            name = f.filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()
            candidate_inputs.append((str(uuid.uuid4()), name, clean_text(text)))

    # Pasted text candidates
    candidate_texts_raw = form.get("candidate_texts", "")
    if candidate_texts_raw:
        try:
            parsed_texts = json.loads(candidate_texts_raw)
            for item in parsed_texts:
                text = item.get("text", "").strip()
                if text:
                    name = item.get("name", "Candidate").strip() or "Candidate"
                    candidate_inputs.append((str(uuid.uuid4()), name, clean_text(text)))
        except Exception as e:
            pass  # Ignore malformed JSON

    if not candidate_inputs:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one candidate (via candidate_files or candidate_texts)."
        )

    # ── 4. Parse each candidate ───────────────────────────────────────────────
    candidates = []
    for cid, name, text in candidate_inputs:
        profile = parse_candidate_profile(cid, text, name)
        candidates.append(profile)

    # ── 5. Rank ───────────────────────────────────────────────────────────────
    shortlist = rank_candidates(jd_parsed, candidates, use_llm_explanations=True)

    elapsed = round(time.time() - start, 2)

    return RankingResponse(
        job_parsed=jd_parsed,
        shortlist=shortlist,
        total_candidates=len(candidates),
        processing_time_seconds=elapsed,
    )


@router.post("/export/csv")
async def export_csv(results: List[CandidateResult]):
    """Export shortlist to CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rank", "Name", "Score", "Fit Band",
        "Semantic Fit", "Skill Match", "Experience", "Recency",
        "Matched Skills", "Missing Skills", "Explanation"
    ])
    for r in results:
        writer.writerow([
            r.rank, r.name, r.score, r.fit_band,
            r.score_breakdown.semantic_fit, r.score_breakdown.skill_match,
            r.score_breakdown.experience_relevance, r.score_breakdown.recency_progression,
            "; ".join(r.matched_skills), "; ".join(r.missing_skills),
            r.explanation,
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=talentiq_shortlist.csv"},
    )


@router.get("/health")
async def health():
    return {"status": "ok", "service": "TalentIQ API"}
