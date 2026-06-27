import json
import re
from typing import List
from groq import Groq
from app.core.config import settings
from app.models.schemas import JobDescription, CandidateProfile, WorkExperience

client = Groq(api_key=settings.groq_api_key) if settings.groq_api_key else None


def _call_llm(prompt: str, system: str = "") -> str:
    """Call Groq LLM and return text response."""
    if not client:
        return "{}"
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.1,
        max_tokens=1500,
    )
    return response.choices[0].message.content.strip()


def _parse_json_response(text: str) -> dict:
    """Safely extract JSON from LLM response."""
    # Strip markdown fences
    text = re.sub(r"```json|```", "", text).strip()
    try:
        return json.loads(text)
    except Exception:
        # Try to find JSON object in text
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return {}


def parse_job_description(jd_text: str) -> JobDescription:
    """Use LLM to extract structured info from JD."""
    system = (
        "You are a precise recruiter assistant. Extract structured information from job descriptions. "
        "Return ONLY valid JSON, no markdown, no explanation."
    )
    prompt = f"""Extract the following from this job description and return as JSON:
{{
  "title": "job title",
  "must_have_skills": ["skill1", "skill2"],
  "preferred_skills": ["skill1"],
  "min_years_experience": 0,
  "domain": "industry/domain",
  "seniority": "junior/mid/senior/lead/principal",
  "behavioral_indicators": ["trait1"]
}}

Job Description:
{jd_text[:3000]}"""

    raw = _call_llm(prompt, system)
    data = _parse_json_response(raw)
    return JobDescription(raw_text=jd_text, **{k: v for k, v in data.items() if k in JobDescription.model_fields})


def parse_candidate_profile(candidate_id: str, raw_text: str, name: str = "Unknown") -> CandidateProfile:
    """Use LLM to extract structured info from resume/profile text."""
    system = (
        "You are a resume parser. Extract structured data from candidate resumes. "
        "Return ONLY valid JSON, no markdown, no explanation."
    )
    prompt = f"""Parse this resume and return JSON:
{{
  "name": "full name or '{name}'",
  "summary": "2-sentence professional summary",
  "skills": ["skill1", "skill2"],
  "experiences": [
    {{"company": "", "role": "", "years": 1.0, "description": "what they did", "skills_used": []}}
  ],
  "total_years": 0.0,
  "education": "degree and institution",
  "certifications": ["cert1"],
  "projects": ["project description"]
}}

Resume:
{raw_text[:3000]}"""

    raw = _call_llm(prompt, system)
    data = _parse_json_response(raw)

    # Build experiences list
    experiences = []
    for exp in data.get("experiences", []):
        try:
            experiences.append(WorkExperience(**exp))
        except Exception:
            pass

    return CandidateProfile(
        id=candidate_id,
        name=data.get("name", name),
        raw_text=raw_text,
        summary=data.get("summary", ""),
        skills=data.get("skills", []),
        experiences=experiences,
        total_years=float(data.get("total_years", 0)),
        education=data.get("education", ""),
        certifications=data.get("certifications", []),
        projects=data.get("projects", []),
    )


def generate_explanation(
    candidate: CandidateProfile,
    jd: JobDescription,
    matched_skills: List[str],
    missing_skills: List[str],
    score: float,
) -> tuple[str, List[str]]:
    """Generate human-readable explanation and highlights for a candidate."""
    system = "You are a helpful recruiter writing brief, honest candidate evaluations. Be specific and evidence-based."
    prompt = f"""Write a 2-3 sentence recruiter note for this candidate and list 3 specific evidence highlights.

Job: {jd.title} | Domain: {jd.domain}
Candidate: {candidate.name} | Score: {score:.0f}/100
Matched skills: {', '.join(matched_skills[:8]) or 'none'}
Missing must-haves: {', '.join(missing_skills[:5]) or 'none'}
Experience: {candidate.total_years} years
Summary: {candidate.summary[:300]}

Return JSON:
{{
  "explanation": "recruiter note here",
  "highlights": ["specific highlight 1", "specific highlight 2", "specific highlight 3"]
}}"""

    raw = _call_llm(prompt, system)
    data = _parse_json_response(raw)
    explanation = data.get("explanation", f"Candidate scored {score:.0f}/100 with {len(matched_skills)} matched skills.")
    highlights = data.get("highlights", matched_skills[:3])
    return explanation, highlights
