# backend/app/agents/auditor.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.config import settings
from app.schemas import VerifiedOpportunity
from app.tools.scraper_tool import scrape_webpage_markdown
import uuid

def run_auditor_agent(state) -> dict:
    """
    Agent 3: Scrapes candidate URLs, verifies requirements against student profile,
    computes eligibility gaps, and checks if at least 10 valid opportunities are found.
    """
    logs = list(state.get("recovery_logs", []))
    profile = state.get("student_profile")
    candidates = state.get("candidate_urls", [])
    existing_verified = list(state.get("verified_opportunities", []))
    already_checked_urls = {v.official_url for v in existing_verified}
    retry_count = state.get("retry_count", 0)

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.0
    ).with_structured_output(VerifiedOpportunity)

    verified_opps = list(existing_verified)

    for cand in candidates[:14]:
        if len(verified_opps) >= 11:
            break
        url = cand.get("url", "")
        if not url or url in already_checked_urls:
            continue

        page_text, sc_logs = scrape_webpage_markdown(url)
        logs.extend(sc_logs)

        # If live scrape is blocked or short, fall back to Tavily search snippet so we don't lose valid opportunities
        if not page_text or len(page_text) < 150:
            snippet = cand.get("snippet", "")
            if len(snippet) >= 50:
                logs.append(f"[RECOVERY] Direct scrape blocked on {url}. Using search index snippet fallback.")
                page_text = f"Title: {cand.get('title', '')}\nURL: {url}\nSummary: {snippet}"
            else:
                logs.append(f"[WARN] Skipping URL due to insufficient content: {url}")
                continue

        prompt = f"""
        You are the Auditor & Verifier Agent. Analyze the webpage content for a university program or scholarship 
        and cross-reference it against the student profile.

        --- STUDENT PROFILE ---
        Name: {profile.full_name}
        CGPA: {profile.cgpa}/{profile.cgpa_scale}
        Degree: {profile.current_degree}
        Technical Skills: {profile.technical_skills}
        Missing Credentials Detected: {profile.missing_standard_credentials}

        --- WEBPAGE CONTENT (Source: {url}) ---
        {page_text[:7000]}

        Extract and evaluate:
        1. University / Body name, Program name, Scholarship name, Country.
        2. Official URL ({url}).
        3. Exact funding details (stipend, tuition waiver, or award amount).
        4. Application deadline (or standard intake window if exact date isn't listed).
        5. Minimum GPA required and language/test requirements (IELTS, TOEFL, GRE).
        6. Determine eligibility status: "ELIGIBLE", "CONDITIONAL_MISSING_INFO", or "INELIGIBLE".
        7. List missing_info_for_student (e.g., "IELTS 6.5+ score required", "2 Academic LORs").
        8. Provide a fit_score (0-100) and personalized why_it_fits linking the student's CGPA and projects.
        9. Step-by-step how_to_apply_steps.
        10. A short verbatim verification_quote from the text.
        """

        try:
            opp = llm.invoke([HumanMessage(content=prompt)])
            opp.id = f"opp-{uuid.uuid4().hex[:6]}"
            opp.official_url = url
            verified_opps.append(opp)
            already_checked_urls.add(url)
            logs.append(f"[SUCCESS] Verified ({len(verified_opps)}): {opp.university_or_body} — {opp.scholarship_name}")
        except Exception as e:
            logs.append(f"[WARN] Failed to extract structured opportunity from {url}: {str(e)[:120]}")

    new_retry_count = retry_count
    if len(verified_opps) < 8 and retry_count < 1:
        new_retry_count += 1
        logs.append(
            f"[RECOVERY] Verified count ({len(verified_opps)}) below threshold. "
            f"Triggering self-healing loop back to Scout Agent..."
        )

    return {
        "verified_opportunities": verified_opps,
        "retry_count": new_retry_count,
        "recovery_logs": logs
    }