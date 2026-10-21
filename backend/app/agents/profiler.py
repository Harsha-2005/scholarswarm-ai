# backend/app/agents/profiler.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.config import settings
from app.schemas import StudentProfile, GitHubProject
from app.tools.pdf_parser import extract_text_from_pdf
from app.tools.github_tool import fetch_github_dossier
import json

def run_profiler_agent(state: dict) -> dict:
    """
    Agent 1: Ingests Resume and Marksheet PDFs, calls GitHub API,
    and synthesizes a structured StudentProfile using Gemini.
    """
    logs = list(state.get("recovery_logs", []))
    resume_path = state.get("resume_text_path", "sample_data/rahul_resume.pdf")
    marksheet_path = state.get("marksheet_text_path", "sample_data/rahul_marksheet.pdf")
    github_input = state.get("github_username", "rahul-ai-dev")

    # 1. Extract Resume Text
    resume_text, r_logs = extract_text_from_pdf(resume_path, "Resume")
    logs.extend(r_logs)

    # 2. Extract Marksheet Text
    marksheet_text, m_logs = extract_text_from_pdf(marksheet_path, "Marksheet")
    logs.extend(m_logs)

    # 3. Fetch GitHub Dossier
    gh_data, g_logs = fetch_github_dossier(github_input)
    logs.extend(g_logs)

    # 4. Synthesize with Gemini
    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.1
    ).with_structured_output(StudentProfile)

    prompt = f"""
    You are the Profiler Agent for an AI Scholarship Finder. Analyze the provided student credentials, 
    resume, academic marksheet, and GitHub developer dossier to build a comprehensive StudentProfile JSON.

    --- RESUME TEXT ---
    {resume_text[:4000]}

    --- MARKSHEET / TRANSCRIPT TEXT ---
    {marksheet_text[:3000]}

    --- GITHUB DOSSIER ---
    {json.dumps(gh_data, indent=2)}

    Extract accurate academic standing (CGPA, scale), technical skills, core projects from GitHub, 
    academic highlights, and identify missing standard credentials (e.g., IELTS/TOEFL score, GRE, etc.).
    """

    try:
        profile = llm.invoke([HumanMessage(content=prompt)])
        # Ensure GitHub projects from dossier are correctly mapped if LLM missed details
        if gh_data and not profile.github_projects:
            profile.github_projects = [
                GitHubProject(
                    name=p["name"],
                    url=p["url"],
                    description=p["description"],
                    primary_language=p["primary_language"],
                    stars=p["stars"],
                    topics=p["topics"],
                    readme_excerpt=p["readme_excerpt"]
                ) for p in gh_data.get("top_projects", [])
            ]
        logs.append(f"[SUCCESS] Profiler Agent successfully synthesized profile for {profile.full_name} ({profile.cgpa}/{profile.cgpa_scale} CGPA).")
    except Exception as e:
        logs.append(f"[ERROR] Profiler Agent LLM synthesis failed: {str(e)}")
        # Fallback default profile for Rahul
        profile = StudentProfile(
            full_name="Rahul Sharma",
            current_degree="B.Tech Computer Science and Engineering",
            university="Lovely Professional University",
            location="Jalandhar, India",
            cgpa=8.2,
            cgpa_scale=10.0,
            target_countries=state.get("target_countries", ["Canada", "Germany", "Singapore"]),
            target_fields=["Artificial Intelligence", "Machine Learning", "Computer Science"],
            technical_skills=["Python", "PyTorch", "FastAPI", "TensorFlow", "Git"],
            missing_standard_credentials=["IELTS Score", "GRE Score", "Official LORs"]
        )

    return {
        "student_profile": profile,
        "resume_text": resume_text,
        "marksheet_text": marksheet_text,
        "recovery_logs": logs
    }