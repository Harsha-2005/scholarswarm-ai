# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class GitHubProject(BaseModel):
    name: str
    url: str
    description: Optional[str]
    primary_language: str
    stars: int
    topics: List[str] = []
    readme_excerpt: Optional[str] = None

class StudentProfile(BaseModel):
    full_name: str
    current_degree: str
    university: str
    location: str
    cgpa: float
    cgpa_scale: float = 10.0
    target_countries: List[str]
    target_fields: List[str]
    technical_skills: List[str]
    github_projects: List[GitHubProject] = []
    academic_highlights: List[str] = Field(default_factory=list, description="Key subjects/achievements")
    missing_standard_credentials: List[str] = Field(default_factory=list, description="e.g. IELTS, GRE not found")

class CandidateOpportunity(BaseModel):
    university_or_body: str
    program_name: str
    scholarship_name: str
    country: str
    official_url: str

class VerifiedOpportunity(BaseModel):
    id: str
    university_or_body: str
    program_name: str
    scholarship_name: str
    country: str
    official_url: str
    funding_details: str = Field(description="Exact stipend, tuition waiver or award amount")
    deadline: str
    min_gpa_required: str
    language_or_test_reqs: List[str] = []
    eligibility_status: Literal["ELIGIBLE", "CONDITIONAL_MISSING_INFO", "INELIGIBLE"]
    missing_info_for_student: List[str] = Field(default_factory=list)
    fit_score: int = Field(ge=0, le=100)
    why_it_fits: str = Field(description="Explanation linking CGPA and GitHub projects")
    how_to_apply_steps: List[str] = []
    verification_quote: str = Field(description="Short verbatim snippet from official page")

class SwarmState(BaseModel):
    resume_text: str = ""
    marksheet_text: str = ""
    github_username: str = ""
    target_countries: List[str] = Field(default_factory=lambda: ["Canada", "Germany", "Singapore"])
    
    student_profile: Optional[StudentProfile] = None
    candidate_urls: List[dict] = []
    verified_opportunities: List[VerifiedOpportunity] = []
    top_5_matches: List[VerifiedOpportunity] = []
    sop_draft: str = ""
    
    retry_count: int = 0
    recovery_logs: List[str] = []