# backend/app/agents/strategist.py
from app.schemas import VerifiedOpportunity
from typing import List

def run_strategist_agent(state: dict) -> dict:
    """
    Agent 4: Scores, ranks, and filters verified opportunities down to the Top 5 matches.
    """
    logs = list(state.get("recovery_logs", []))
    verified_opps: List[VerifiedOpportunity] = state.get("verified_opportunities", [])

    # Sort by eligibility and fit score
    status_priority = {"ELIGIBLE": 2, "CONDITIONAL_MISSING_INFO": 1, "INELIGIBLE": 0}
    
    sorted_opps = sorted(
        verified_opps,
        key=lambda x: (status_priority.get(x.eligibility_status, 0), x.fit_score),
        reverse=True
    )

    top_5 = sorted_opps[:5]
    logs.append(f"[SUCCESS] Strategist Agent selected top {len(top_5)} matches from {len(verified_opps)} verified opportunities.")

    return {
        "top_5_matches": top_5,
        "recovery_logs": logs
    }