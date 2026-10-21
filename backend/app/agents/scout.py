# backend/app/agents/scout.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.config import settings
from app.tools.search_tool import search_scholarships_and_programs
from typing import List

def run_scout_agent(state: dict) -> dict:
    """
    Agent 2: Generates search queries tailored to the student's profile 
    and discovers candidate university programs and scholarships across target countries.
    """
    logs = list(state.get("recovery_logs", []))
    profile = state.get("student_profile")
    target_countries = profile.target_countries if profile else ["Canada", "Germany", "Singapore"]
    retry_count = state.get("retry_count", 0)

    logs.append(f"[INFO] Scout Agent initiating discovery for countries: {target_countries} (Attempt {retry_count + 1})...")

    # Generate targeted search queries
    queries = [
        f"Master Computer Science AI scholarship international students {country} 2026 2027"
        for country in target_countries
    ]
    queries.append("DAAD scholarship computer science Germany deadlines")
    queries.append("fully funded master artificial intelligence canada international students")

    all_candidates = []
    seen_urls = set()

    for q in queries:
        results, s_logs = search_scholarships_and_programs(q, max_results=4)
        logs.extend(s_logs)
        for r in results:
            url = r.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_candidates.append({
                    "title": r.get("title"),
                    "url": url,
                    "snippet": r.get("content", "")
                })

    logs.append(f"[SUCCESS] Scout Agent gathered {len(all_candidates)} unique candidate URLs.")
    return {
        "candidate_urls": all_candidates,
        "recovery_logs": logs
    }