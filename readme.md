# 🎓 ScholarSwarm AI — Autonomous 5-Agent Scholarship & University Finder
**Built for the TetraNoodle AI Hackathon 2026**

ScholarSwarm AI is a multi-agent decision-support swarm built with **LangGraph, FastAPI, Google Gemini, Tavily Search, and GitHub REST API**. It ingests a student's unstructured Resume PDF, Academic Marksheet PDF, and live GitHub profile, autonomously researches global university programs and scholarships, audits eligibility gaps with verifiable source URLs, ranks the Top 5 matches, and drafts a tailored Statement of Purpose (SOP).

## ✨ Key Features
- **5 Specialized AI Agents:** `ProfilerAgent` -> `ScoutAgent` -> `AuditorAgent` -> `StrategistAgent` -> `SOPWriterAgent`.
- **Real Internet Research & Enrichment:** Live GitHub REST API repository/README inspection + Tavily web discovery + Jina Reader/BeautifulSoup live scraping.
- **3-Tier Self-Healing & Failure Recovery:**
  1. **OCR Fallback:** Automatically switches from `PyMuPDF` to `Gemini Vision OCR` if a scanned marksheet PDF is uploaded.
  2. **Scraper Resilience:** Automatically falls back from `Jina Reader API` to `BeautifulSoup4` to `Search Index Snippets` when university firewalls block automated requests.
  3. **Cyclical Graph Recovery:** Conditional LangGraph edge routes execution back to `ScoutAgent` if verification yields insufficient valid opportunities.
- **Surprise-Profile Ready:** Zero hardcoded student assumptions—upload any Resume/Marksheet PDF, GitHub handle, and target countries directly from the Mission Control Web UI.

## 🚀 Quickstart

### 1. Clone & Install Dependencies
```bash
git clone <your-repo-url>
cd scholarswarm-ai
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
pip install beautifulsoup4 sse-starlette pymupdf python-multipart