from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class RunRequest(BaseModel):
    job_text: str = Field(..., description="Job description text (paste from LinkedIn/JD)")
    resume_text: str = Field(..., description="Your resume plain text")
    company_name: Optional[str] = None
    role_title: Optional[str] = None
    job_url: Optional[str] = None

class RunResponse(BaseModel):
    jd_summary: Dict[str, Any]
    ats_keywords: List[str]
    company_research: Dict[str, Any]
    tailored_resume_bullets: List[str]
    cover_letter: str
    interview_pack: Dict[str, Any]
    verifier_report: Dict[str, Any]
    execution_log: Dict[str, Any]
    run_id: str
    job_id: str

class ScoreRequest(BaseModel):
    job_text: str
    resume_text: str

class DiffResponse(BaseModel):
    bullets_diff: str
    cover_letter_diff: str
