from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class GitHubProject(BaseModel):
    name: str = Field(description="Repository or project name")
    url: str = Field(description="URL to the repository or project")
    description: Optional[str] = Field(default="", description="Short description of the project")
    languages: List[str] = Field(default_factory=list, description="Programming languages used")
    stars: int = Field(default=0, description="Star count if applicable")
    key_tech_extracted: List[str] = Field(
        default_factory=list,
        description="Specific frameworks, architectures, or AI models extracted from README or resume"
    )

class AcademicSubjectRecord(BaseModel):
    course_name: str
    grade_or_score: str
    relevance_to_target: str = Field(description="High, Medium, or Low relevance to target Masters program")

class StudentProfile(BaseModel):
    full_name: str
    email: Optional[str] = None
    location: str = Field(description="City and Country of the student")
    current_degree: str = Field(description="e.g., B.Tech in Computer Science and Engineering")
    university: str = Field(description="Current university name")
    graduation_year: Optional[str] = None
    cgpa: float = Field(description="Cumulative Grade Point Average as a float")
    cgpa_scale: float = Field(default=10.0, description="Scale of the CGPA, e.g., 10.0 or 4.0")
    percentage_equivalent: Optional[float] = Field(default=None, description="Approximate percentage if applicable")
    
    target_countries: List[str] = Field(description="Countries the student wants to apply to")
    target_degree_level: str = Field(default="Master's (MS / M.Eng / MSc)", description="Target degree level")
    target_fields: List[str] = Field(description="Target specializations, e.g., Artificial Intelligence, Machine Learning, Data Science")
    financial_need_Constraint: str = Field(description="Summary of budget constraint or need for full/partial scholarship")
    
    technical_skills: List[str] = Field(description="Verified programming languages, tools, and frameworks")
    github_and_portfolio_projects: List[GitHubProject] = Field(description="Enriched projects from GitHub and Resume")
    strongest_academic_subjects: List[AcademicSubjectRecord] = Field(description="Key relevant subjects from marksheet")
    achievements_and_publications: List[str] = Field(default_factory=list)
    
    # Crucial for Hackathon Requirement #3: "compare requirements with profile and identify missing information"
    detected_credentials_present: List[str] = Field(
        description="Standard application documents/scores confirmed present (e.g., 'Academic Transcripts', 'Resume', 'GitHub Portfolio')"
    )
    missing_standard_credentials: List[str] = Field(
        description="Standard study-abroad requirements NOT found in student's profile (e.g., 'IELTS/TOEFL English Proficiency Score', 'GRE Score', 'Letters of Recommendation (LOR)', 'Passport validity', 'Formal Research Publication')"
    )
    profiler_summary: str = Field(description="A concise 3-sentence executive summary of the student's competitive positioning")