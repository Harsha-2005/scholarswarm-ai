# backend/verify_setup.py
import requests
from app.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI

def test_all_keys():
    print("=== ScholarSwarm Environment & API Key Verification ===\n")

    # 1. Verify GitHub Classic PAT
    print("1. Testing GitHub Personal Access Token (Classic)...")
    if not settings.GITHUB_TOKEN:
        print("   [FAIL] GITHUB_TOKEN is empty in .env")
    else:
        headers = {"Authorization": f"token {settings.GITHUB_TOKEN}"}
        r = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
        if r.status_code == 200:
            limit = r.json().get("rate", {}).get("limit")
            remaining = r.json().get("rate", {}).get("remaining")
            print(f"   [PASS] GitHub Token valid! Rate limit: {remaining}/{limit} requests/hr.")
        else:
            print(f"   [FAIL] GitHub returned status {r.status_code}: {r.text}")

    # 2. Verify Tavily Search API Key
    print("\n2. Testing Tavily Search API Key...")
    if not settings.TAVILY_API_KEY:
        print("   [FAIL] TAVILY_API_KEY is empty in .env")
    else:
        r = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.TAVILY_API_KEY,
                "query": "DAAD scholarship Computer Science Germany",
                "max_results": 1
            },
            timeout=15
        )
        if r.status_code == 200:
            results = r.json().get("results", [])
            print(f"   [PASS] Tavily API valid! Sample URL found: {results[0]['url'] if results else 'None'}")
        else:
            print(f"   [FAIL] Tavily returned status {r.status_code}: {r.text}")

    # 3. Verify Gemini API Key
    print("\n3. Testing Google Gemini API Key...")
    if not settings.GEMINI_API_KEY:
        print("   [FAIL] GEMINI_API_KEY is empty in .env")
    else:
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=settings.GEMINI_API_KEY
            )
            res = llm.invoke("Reply with the exact word: READY")
            print(f"   [PASS] Gemini API valid! Model replied: {res.content.strip()}")
        except Exception as e:
            print(f"   [FAIL] Gemini error: {e}")

if __name__ == "__main__":
    test_all_keys()