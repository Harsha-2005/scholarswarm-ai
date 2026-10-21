# backend/app/graph/workflow.py
from langgraph.graph import StateGraph, END
from app.schemas import SwarmState
from app.agents.profiler import run_profiler_agent
from app.agents.scout import run_scout_agent
from app.agents.auditor import run_auditor_agent
from app.agents.strategist import run_strategist_agent
from app.agents.sop_writer import run_sop_writer_agent

def check_verification_threshold(state: SwarmState) -> str:
    """
    Self-Healing Conditional Edge:
    If verified opportunities < 8 and retry_count == 1 (just incremented once), loop back to scout.
    Otherwise proceed to strategist.
    """
    verified_count = len(state.get("verified_opportunities", []))
    retry_count = state.get("retry_count", 0)

    if verified_count < 8 and retry_count == 1:
        return "retry_scout"
    return "proceed_strategist"

def create_scholar_swarm_graph():
    workflow = StateGraph(SwarmState)

    workflow.add_node("profiler", run_profiler_agent)
    workflow.add_node("scout", run_scout_agent)
    workflow.add_node("auditor", run_auditor_agent)
    workflow.add_node("strategist", run_strategist_agent)
    workflow.add_node("sop_writer", run_sop_writer_agent)

    workflow.set_entry_point("profiler")
    workflow.add_edge("profiler", "scout")
    workflow.add_edge("scout", "auditor")

    workflow.add_conditional_edges(
        "auditor",
        check_verification_threshold,
        {
            "retry_scout": "scout",
            "proceed_strategist": "strategist"
        }
    )

    workflow.add_edge("strategist", "sop_writer")
    workflow.add_edge("sop_writer", END)

    return workflow.compile()