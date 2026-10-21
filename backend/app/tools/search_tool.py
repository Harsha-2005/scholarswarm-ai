# backend/app/tools/search_tool.py
import requests
from typing import List, Dict, Any, Tuple
from app.config import settings

def search_scholarships_and_programs(query: str, max_results: int = 5) -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Executes live web search using the Tavily API optimized for AI agent discovery.
    Returns: (list of result dicts with url, title, snippet; telemetry logs)
    """
    logs: List[str] = []
    if not settings.TAVILY_API_KEY:
        logs.append("[ERROR] TAVILY_API_KEY is missing.")
        return [], logs

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
                "include_answer": True
            },
            timeout=15
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        logs.append(f"[SUCCESS] Tavily search for '{query}' returned {len(results)} results.")
        return results, logs

    except Exception as e:
        logs.append(f"[ERROR] Tavily search failed for query '{query}': {str(e)}")
        return [], logs