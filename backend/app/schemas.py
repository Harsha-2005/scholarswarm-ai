# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any

class GitHubProject(BaseModel):
    name: str = ""
    url: str = ""
    description: Optional[str] = ""
    primary_language: str = "Unknown"
    stars: int = 0
    topics: List[str] = Field(default_factory=list)
    readme_excerpt: Optional[str] = ""

class StudentProfile(BaseModel):
    full_name: str = "Rahul Sharma"
    current_degree: str = "B.Tech Computer Science and Engineering"
    university: str = "Lovely Professional University"
    location: str = "Jalandhar, India"
    cgpa: float = 8.2
    cgpa_scale: float = 10.0
    target_countries: List[str] = Field(default_factory=lambda: ["Canada", "Germany", "Singapore"])
    target_fields: List[str] = Field(default_factory=lambda: ["Artificial Intelligence", "Machine Learning", "Computer Science"])
    technical_skills: List[str] = Field(default_factory=list)
    github_projects: List[GitHubProject] = Field(default_factory=list)
    academic_highlights: List[str] = Field(default_factory=list, description="Key subjects/achievements")
    missing_standard_credentials: List[str] = Field(default_factory=list, description="e.g. IELTS, GRE not found")

class CandidateOpportunity(BaseModel):
    university_or_body: str
    program_name: str
    scholarship_name: str
    country: str
    official_url: str

class VerifiedOpportunity(BaseModel):
    id: str = Field(default="opp-1", description="Unique ID")
    university_or_body: str = Field(description="University or funding organization name")
    program_name: str = Field(description="Degree program name, e.g. MSc in Artificial Intelligence")
    scholarship_name: str = Field(description="Scholarship or funding program name")
    country: str = Field(description="Country of the university/scholarship")
    official_url: str = Field(default="", description="Official webpage URL")
    funding_details: str = Field(description="Exact stipend, tuition waiver, or award amount")
    deadline: str = Field(description="Application deadline or intake window")
    min_gpa_required: str = Field(description="Minimum GPA/CGPA requirement")
    language_or_test_reqs: List[str] = Field(default_factory=list, description="Required tests like IELTS, TOEFL, GRE")
    eligibility_status: Literal["ELIGIBLE", "CONDITIONAL_MISSING_INFO", "INELIGIBLE"] = "CONDITIONAL_MISSING_INFO"
    missing_info_for_student: List[str] = Field(default_factory=list, description="Gaps between requirements and student profile")
    fit_score: int = Field(default=80, ge=0, le=100)
    why_it_fits: str = Field(description="Explanation linking student CGPA and GitHub projects")
    how_to_apply_steps: List[str] = Field(default_factory=list)
    verification_quote: str = Field(default="", description="Short verbatim snippet from official page")

class SwarmState(BaseModel):
    resume_text_path: str = "sample_data/rahul_resume.pdf"
    marksheet_text_path: str = "sample_data/rahul_marksheet.pdf"
    resume_text: str = ""
    marksheet_text: str = ""
    github_username: str = "torvalds"
    target_countries: List[str] = Field(default_factory=lambda: ["Canada", "Germany", "Singapore"])
    
    student_profile: Optional[StudentProfile] = None
    candidate_urls: List[dict] = Field(default_factory=list)
    verified_opportunities: List[VerifiedOpportunity] = Field(default_factory=list)
    top_5_matches: List[VerifiedOpportunity] = Field(default_factory=list)
    sop_draft: str = ""
    
    retry_count: int = 0
    recovery_logs: List[str] = Field(default_factory=list)

    # Allow dict-like .get() access inside LangGraph nodes
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)