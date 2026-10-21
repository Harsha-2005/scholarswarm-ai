# backend/app/agents/sop_writer.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.config import settings
import json

def run_sop_writer_agent(state: dict) -> dict:
    """
    Agent 5: Generates a tailored Statement of Purpose (SOP) draft 
    grounded in the student's actual GitHub projects and academic profile for the #1 Top Match.
    """
    logs = list(state.get("recovery_logs", []))
    profile = state.get("student_profile")
    top_5 = state.get("top_5_matches", [])

    if not top_5:
        logs.append("[WARN] No top matches available for SOP generation.")
        return {"sop_draft": "No matching opportunities available to draft SOP.", "recovery_logs": logs}

    target_opp = top_5[0]

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3
    )

    prompt = f"""
    You are an expert Academic Admissions Writer. Write a compelling, professional 600-800 word 
    Statement of Purpose (SOP) draft for the student applying to the following program.

    --- STUDENT PROFILE ---
    Name: {profile.full_name}
    Current Degree: {profile.current_degree} at {profile.university}
    CGPA: {profile.cgpa}/{profile.cgpa_scale}
    Technical Skills: {profile.technical_skills}
    GitHub Projects & Repos: {json.dumps([p.dict() for p in profile.github_projects], indent=2)}

    --- TARGET OPPORTUNITY ---
    University / Body: {target_opp.university_or_body}
    Program: {target_opp.program_name}
    Scholarship: {target_opp.scholarship_name}
    Country: {target_opp.country}

    Guidelines:
    1. Ground the SOP strictly in the student's real GitHub projects and academic background. Do not invent achievements.
    2. Bridge their actual technical experience (e.g. PyTorch, NLP, AI engineering) with the target university's focus.
    3. Include placeholder tags like [INSERT PERSONAL MOTIVATION] where the student can personalize further.
    """

    try:
        res = llm.invoke([HumanMessage(content=prompt)])
        sop_text = res.content
        logs.append(f"[SUCCESS] SOP Writer generated tailored SOP draft for {target_opp.university_or_body}.")
    except Exception as e:
        logs.append(f"[ERROR] SOP generation failed: {str(e)}")
        sop_text = "Failed to generate SOP draft."

    return {
        "sop_draft": sop_text,
        "recovery_logs": logs
    }