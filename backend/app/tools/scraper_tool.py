# backend/app/tools/scraper_tool.py
import requests
from bs4 import BeautifulSoup
from typing import Tuple, List
from app.config import settings

def scrape_webpage_markdown(url: str) -> Tuple[str, List[str]]:
    """
    Scrapes any live university or scholarship URL using Jina Reader API (https://r.jina.ai/<url>)
    which converts web pages into clean LLM-ready Markdown. Falls back to BeautifulSoup if needed.
    """
    logs: List[str] = []
    if not url or not url.startswith("http"):
        logs.append(f"[WARN] Invalid URL passed to scraper: {url}")
        return "", logs

    # Try Jina Reader Proxy first
    jina_url = f"https://r.jina.ai/{url}"
    try:
        headers = {"Accept": "text/markdown", "User-Agent": "ScholarSwarm-Agent"}
        if settings.TAVILY_API_KEY:  # Optional header bearer if needed by Jina
            pass
        
        resp = requests.get(jina_url, headers=headers, timeout=12)
        if resp.status_code == 200 and len(resp.text.strip()) > 100:
            logs.append(f"[SUCCESS] Scraped {url} via Jina Reader ({len(resp.text)} chars).")
            return resp.text[:15000], logs  # Cap at 15k chars for token efficiency
    except Exception as e:
        logs.append(f"[WARN] Jina Reader proxy failed for {url} ({str(e)}). Falling back to BeautifulSoup...")

    # Fallback: Standard BeautifulSoup Scraper
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        
        soup = BeautifulSoup(resp.text, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.extract()
            
        text = soup.get_text(separator="\n", strip=True)
        logs.append(f"[RECOVERY] Scraped {url} via BeautifulSoup fallback ({len(text)} chars).")
        return text[:15000], logs

    except Exception as e:
        logs.append(f"[ERROR] Failed to scrape URL {url}: {str(e)}")
        return "", logs