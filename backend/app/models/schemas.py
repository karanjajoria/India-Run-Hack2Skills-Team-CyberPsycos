from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class JobDescription(BaseModel):
    title: str = ""
    must_have_skills: List[str] = []
    preferred_skills: List[str] = []
    min_years_experience: int = 0
    domain: str = ""
    seniority: str = ""
    behavioral_indicators: List[str] = []
    raw_text: str = ""


class WorkExperience(BaseModel):
    company: str = ""
    role: str = ""
    years: float = 0.0
    description: str = ""
    skills_used: List[str] = []


class CandidateProfile(BaseModel):
    id: str
    name: str = "Unknown"
    raw_text: str = ""
    summary: str = ""
    skills: List[str] = []
    experiences: List[WorkExperience] = []
    total_years: float = 0.0
    education: str = ""
    certifications: List[str] = []
    projects: List[str] = []


class ScoreBreakdown(BaseModel):
    semantic_fit: float = 0.0
    skill_match: float = 0.0
    experience_relevance: float = 0.0
    recency_progression: float = 0.0
    total: float = 0.0


class CandidateResult(BaseModel):
    id: str
    name: str
    rank: int
    score: float
    fit_band: str  # "Strong", "Good", "Moderate", "Weak"
    score_breakdown: ScoreBreakdown
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    explanation: str = ""
    highlights: List[str] = []


class RankingRequest(BaseModel):
    job_description_text: str
    candidate_texts: Optional[List[Dict[str, str]]] = None  # [{"name": ..., "text": ...}]


class RankingResponse(BaseModel):
    job_parsed: JobDescription
    shortlist: List[CandidateResult]
    total_candidates: int
    processing_time_seconds: float
