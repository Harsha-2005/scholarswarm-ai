🎓 ScholarSwarm AI — Autonomous 5-Agent Scholarship & University Finder

Built for the TetraNoodle AI Hackathon 2026 | Individual Challenge

ScholarSwarm AI is an autonomous, self-healing multi-agent decision-support platform designed to democratize access to funded international higher education. Instead of functioning as a static chatbot, ScholarSwarm orchestrates a team of 5 specialized AI agents over a cyclical LangGraph state machine.

Given a student's unstructured credentials (Resume PDF, Academic Marksheet PDF, and live GitHub profile), the swarm autonomously enriches their technical dossier, conducts real-time internet research across global university and scholarship portals, audits eligibility and missing credentials against official requirements, ranks the Top 5 Best-Fit Opportunities, and drafts a personalized, non-hallucinated Statement of Purpose (SOP)—streaming every thought, tool invocation, and failure-recovery action live to a real-time Mission Control Web UI.

📖 Table of Contents

The Problem Statement ("Meet Rahul")

Core Capabilities & Hackathon Rubric Alignment

System Architecture & Agent Workflow Diagram

Deep-Dive: The 5 Autonomous Agent Roles

Self-Healing & Failure Recovery Engineering

"The Final Surprise" Readiness (Zero-Code Adaptability)

Technology Stack

Repository Directory Structure

Installation, Configuration & Quickstart

API Endpoints & Real-Time SSE Protocol

🎯 1. The Problem Statement ("Meet Rahul")

Meet Rahul, a final-year B.Tech Computer Science and Engineering student from Jalandhar with an 8.2 CGPA and a strong portfolio of AI/ML projects on GitHub. Rahul dreams of pursuing a Master's degree abroad—ideally in Canada, Germany, or Singapore—but his family cannot afford steep international tuition fees.

While scholarships and funded research programs exist, discovering and verifying them requires navigating dozens of fragmented university websites, decoding complex GPA/language prerequisites, tracking deadlines, and writing tailored admissions essays.

ScholarSwarm AI automates this entire research and preparation pipeline end-to-end:

Understands the Student: Parses PDF resumes and academic transcripts while inspecting live GitHub repositories, languages, and README documentation.

Explores the Live Web: Discovers 10+ real, currently active university programs and scholarships across target countries.

Audits Eligibility & Gaps: Visits official program pages, cross-references requirements against the student's profile, and explicitly flags missing credentials (e.g., missing IELTS/TOEFL, GRE, or LORs).

Recommends the Top 5 Matches: Scores and ranks the best opportunities with transparent explanations of fit, exact funding coverage, deadlines, and application steps.

Drafts Application Materials: Generates a grounded 600–800 word Statement of Purpose (SOP) connecting the student's actual GitHub projects and academic record to the target university.

Streams Live Telemetry: Provides an interactive web dashboard where users upload documents, trigger the swarm, and watch agents collaborate in real time.

🏆 2. Core Capabilities & Hackathon Rubric Alignment

Evaluation Criterion

Marks

How ScholarSwarm AI Delivers

AI agents working together autonomously

30

5 distinct agents (Profiler, Scout, Auditor, Strategist, SOP Writer) orchestrated via a cyclical LangGraph StateGraph exchanging a strictly typed SwarmState Pydantic model.

Real internet research & profile enrichment

25

Queries the live GitHub REST API (repos, languages, stars, READMEs), Tavily Search API (live query discovery), and Jina Reader / BeautifulSoup4 (live webpage Markdown scraping).

Correct results with trustworthy sources

20

Every verified opportunity includes a clickable official_url, extracted funding_details, deadline, min_gpa_required, and a verbatim verification_quote from the source page.

Working website & demonstration

10

Full-featured Mission Control Dashboard served via FastAPI with Server-Sent Events (SSE) for real-time agent stepper status, live terminal logs, Top 5 cards, 10+ verified table, and SOP studio.

Creativity, problem-solving & handling failures

15

4-layer self-healing architecture: Scanned PDF Vision OCR fallback, 3-tier anti-bot web scraper fallback, batched LLM rate-limit protection, and conditional graph retry loops.

Total

100

End-to-end production-grade implementation.

🏗️ 3. System Architecture & Agent Workflow Diagram

Visual Workflow (Mermaid Diagram)

flowchart TD
    subgraph UI ["💻 Mission Control Web UI (FastAPI + Tailwind + SSE)"]
        Inputs["📄 Resume PDF + Marksheet PDF\n🐙 GitHub Username + 🌍 Target Countries"]
        Stream["⚡ Real-Time Telemetry Terminal\n(Live Agent Logs, Tool Calls & Recovery Alerts)"]
        Outputs["🏆 Top 5 Matches | 🌐 10+ Verified Table | ✍️ Custom SOP Draft"]
    end

    subgraph Swarm ["🐝 ScholarSwarm LangGraph State Machine (SwarmState)"]
        A1["1️⃣ Profiler Agent\n(Credential & Codebase Investigator)"]
        A2["2️⃣ Scout Agent\n(Autonomous Search Strategist)"]
        A3["3️⃣ Auditor Agent\n(Web Scraper & Eligibility Gap Analyst)"]
        A4["4️⃣ Strategist Agent\n(Multi-Criteria Scorer & Top-5 Ranker)"]
        A5["5️⃣ SOP Writer Agent\n(Grounded Admissions Copywriter)"]
    end

    subgraph Tools ["🛠️ External APIs & 3-Tier Resilience Layer"]
        T1["PyMuPDF (fitz) ➔ Gemini Vision OCR Fallback"]
        T2["GitHub REST API (Profile, Top Repos, Languages, READMEs)"]
        T3["Tavily Search API (Advanced Depth Live Discovery)"]
        T4["Jina Reader API ➔ BeautifulSoup4 ➔ Search Snippet Fallback"]
    end

    Inputs -->|HTTP POST /api/v1/swarm/start| A1
    A1 <--> T1
    A1 <--> T2
    A1 -->|Synthesized StudentProfile JSON| A2
    A2 <--> T3
    A2 -->|15-19 Unique Candidate URLs| A3
    A3 <--> T4
    A3 -->|Conditional Self-Healing Loop\nif Verified Opportunities < Threshold| A2
    A3 -->|10+ VerifiedOpportunity Objects| A4
    A4 -->|Ranked Top 5 Best Matches| A5
    A5 -->|Tailored 700-Word SOP Draft| Outputs
    Swarm -.->|SSE Stream /api/v1/swarm/stream/{run_id}| Stream


ASCII System Architecture

+-----------------------------------------------------------------------------------+
|                        MISSION CONTROL FRONTEND (HTML5 / Tailwind / JS)           |
|  [ Upload PDFs & Links ] ---> [ Live Agent Swarm Telemetry (SSE) ] ---> [ Results ]|
+-----------------------------------------+-----------------------------------------+
                                          |
                              HTTP POST / SSE EventStream
                                          v
+-----------------------------------------------------------------------------------+
|                              API GATEWAY LAYER (FastAPI)                          |
|  - GET  /                           (Serves Interactive Mission Control UI)       |
|  - POST /api/v1/swarm/start         (Ingests PDFs/Forms & Initializes SwarmState) |
|  - GET  /api/v1/swarm/stream/{id}   (Streams Live Node Transitions & Final State) |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                     AGENT SWARM ORCHESTRATOR (LangGraph StateGraph)               |
|                                                                                   |
|   [1. Profiler Agent] ===> [2. Scout Agent] ===> [3. Auditor & Verifier Agent]    |
|     (PDF + GitHub)          (Tavily Discovery)     (Multi-URL Scrape & Gap Audit) |
|                                  ^                             |                  |
|                                  +--- (Self-Healing Retry) ----+                  |
|                                                                v                  |
|                            [5. SOP Writer Agent] <=== [4. Strategist Agent]       |
|                              (Grounded SOP Draft)       (Score & Rank Top 5)      |
+-----------------------------------------------------------------------------------+


🤖 4. Deep-Dive: The 5 Autonomous Agent Roles

Agent 1: The Holistic Profiler (app/agents/profiler.py)

Objective: Transform raw, multi-modal student documents and codebases into a canonical StudentProfile schema.

Tools Used: extract_text_from_pdf (pdf_parser.py) and fetch_github_dossier (github_tool.py).

Workflow:

Extracts text from the uploaded Resume PDF and Academic Marksheet PDF using PyMuPDF. If a scanned image PDF is detected (fewer than $50$ characters extracted), it automatically triggers a Gemini Vision OCR fallback.

Queries the GitHub REST API (authenticated via Classic PAT) to fetch the student's bio, public repositories sorted by stars and activity, primary programming languages, and the raw README.md contents of their top projects.

Uses Gemini structured output (with_structured_output(StudentProfile)) to synthesize CGPA, degree, technical skills, academic highlights, and baseline missing credentials (e.g., missing IELTS, TOEFL, GRE, or LORs).

Agent 2: The Global Opportunity Scout (app/agents/scout.py)

Objective: Formulate high-recall search queries tailored to the student's domain and target countries to discover real scholarship and degree pages.

Tools Used: search_scholarships_and_programs (search_tool.py powered by Tavily Search API).

Workflow:

Reads target_countries and target_fields from the StudentProfile state.

Executes targeted web searches across each country for funded Master's programs, national scholarships (e.g., DAAD in Germany, OGS/McCall MacBain in Canada, SINGA/NUS in Singapore), and university fellowships.

Deduplicates URLs and passes 15–19 unique candidate opportunities with search index snippets to the Auditor Agent.

Agent 3: The Eligibility Auditor & Verifier (app/agents/auditor.py)

Objective: Visit candidate web pages, verify program authenticity, extract hard requirements, and compute eligibility gaps against the student's profile.

Tools Used: scrape_webpage_markdown (scraper_tool.py).

Workflow:

Filters out low-signal social media links and scrapes candidate URLs into clean Markdown using the Jina Reader API (https://r.jina.ai/<url>), falling back to BeautifulSoup4 or search index snippets if a university firewall blocks automated scraping.

Cross-references each opportunity against the student's cgpa, current_degree, technical_skills, and missing_standard_credentials.

Populates 10+ VerifiedOpportunity objects containing:

eligibility_status: "ELIGIBLE", "CONDITIONAL_MISSING_INFO", or "INELIGIBLE"

missing_info_for_student: Explicit gap checklist (e.g., "Requires IELTS 6.5+ (Missing from profile)", "Requires 2 Academic LORs").

fit_score ($0\text{--}100$), why_it_fits, funding_details, deadline, how_to_apply_steps, and a verbatim verification_quote.

Self-Healing Conditional Edge: If the number of verified opportunities falls below the minimum threshold, LangGraph routes execution back to ScoutAgent for a recovery pass.

Agent 4: The Matchmaker Strategist (app/agents/strategist.py)

Objective: Evaluate all 10+ verified opportunities and distill them into the Top 5 Best Matches.

Workflow:

Applies a deterministic priority matrix sorting first by eligibility_status (ELIGIBLE > CONDITIONAL_MISSING_INFO > INELIGIBLE) and second by fit_score ($0\text{--}100$).

Selects the top 5 highest-value matches and prepares them for featured rendering on the dashboard and downstream SOP generation.

Agent 5: The Narrative Architect (app/agents/sop_writer.py)

Objective: Draft a compelling, truthful Statement of Purpose (SOP) for the student's #1 ranked opportunity.

Workflow:

Ingests the full StudentProfile (including extracted GitHub project descriptions and README excerpts) alongside the top-ranked VerifiedOpportunity.

Generates a 600–800 word academic Statement of Purpose that connects the student's real coursework, 8.2 CGPA, and actual GitHub repositories to the target university's program and country.

Strict Anti-Hallucination Guardrail: Never invents student achievements; inserts explicit [INSERT PERSONAL MOTIVATION] placeholder tags where personal anecdotes are required.

🛡️ 5. Self-Healing & Failure Recovery Engineering

A core requirement of the hackathon (15 marks) is handling failures gracefully. ScholarSwarm implements four distinct resilience mechanisms that log visible [WARN] and [RECOVERY] telemetry badges directly to the user interface:

Scanned PDF Vision OCR Fallback (pdf_parser.py):

Failure Mode: A student uploads a scanned image marksheet PDF with no selectable text layer (fewer than $50$ characters extracted via PyMuPDF).

Recovery: Automatically renders each PDF page into a 150-DPI PNG buffer in memory, encodes it as Base64, and invokes Gemini Vision to perform structured OCR.

3-Tier Web Scraping Resilience (scraper_tool.py & auditor.py):

Failure Mode: University portals block automated scrapers with Cloudflare HTTP 403 errors or connection timeouts.

Recovery: Tier 1 attempts Jina Reader Markdown Proxy (https://r.jina.ai/). If Tier 1 times out or fails, Tier 2 automatically switches to a local BeautifulSoup4 HTML parser that strips <script>, <style>, and <nav> tags. If the site is a hard JavaScript SPA or blocks Tier 2, Tier 3 falls back to the Tavily Search Index Snippet so valid scholarships are never discarded.

GitHub API Authentication & Graceful Degradation (github_tool.py):

Failure Mode: Invalid GitHub username (404), expired token (401), or a student profile without a GitHub account.

Recovery: Automatically strips @ handles or full URLs down to the username; if a token returns 401, it retries unauthenticated; if the user has no GitHub profile, it logs a warning and continues synthesis using Resume and Marksheet data alone.

Batched LLM Synthesis & Cyclical Graph Recovery (auditor.py & workflow.py):

Failure Mode: Sequential per-URL LLM calls exhausting API rate limits (HTTP 429), or broken search results yielding zero verified opportunities.

Recovery: Bundles scraped Markdown evidence into a batched structured-output call to stay well within API rate limits, and uses a conditional LangGraph edge (check_verification_threshold) to loop back to ScoutAgent if verification yields insufficient results.

🔄 6. "The Final Surprise" Readiness (Zero-Code Adaptability)

During live judging, shortlisted participants receive a completely different student profile to test whether the system can adapt without rewriting code. ScholarSwarm is engineered for zero-code adaptability:

Live PDF Uploads in the Web UI: Upload any new student's Resume PDF and Marksheet PDF directly from the browser form (POST /api/v1/swarm/start).

Dynamic Country & GitHub Inputs: Change target countries (e.g., "UK, Australia, USA, Netherlands") and GitHub username directly in the UI before clicking Launch Agent Swarm.

Dynamic Schema Extraction: ProfilerAgent dynamically infers full_name, current_degree, university, cgpa, cgpa_scale, target_fields, and technical_skills directly from the uploaded documents.

🧰 7. Technology Stack

Backend Framework: Python 3.12, FastAPI, Uvicorn, sse-starlette (Server-Sent Events), python-multipart

Agent Orchestration: LangGraph (StateGraph), LangChain Core, Pydantic v2 (Structured Outputs)

LLM & Vision Backbone: Google Gemini (gemini-3.8-flash via langchain-google-genai)

Web Search & Scraping: Tavily Search API (advanced depth), Jina Reader API (r.jina.ai), BeautifulSoup4 (bs4), requests

Document & Codebase Ingestion: PyMuPDF (fitz), GitHub REST API v3 (Authenticated via Classic Personal Access Token)

Frontend UI: HTML5, Tailwind CSS (CDN), Vanilla JavaScript with native EventSource SSE client

📂 8. Repository Directory Structure

scholarswarm-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI server, SSE streaming endpoint & Mission Control UI
│   │   ├── config.py               # Environment variable loader & model configuration
│   │   ├── schemas.py              # Pydantic v2 models (StudentProfile, VerifiedOpportunity, SwarmState)
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── profiler.py         # Agent 1: PDF + GitHub ingestion & StudentProfile synthesis
│   │   │   ├── scout.py            # Agent 2: Dynamic query formulation & Tavily web discovery
│   │   │   ├── auditor.py          # Agent 3: Web scraping, eligibility verification & gap analysis
│   │   │   ├── strategist.py       # Agent 4: Multi-criteria sorting & Top 5 selection
│   │   │   └── sop_writer.py       # Agent 5: Grounded Statement of Purpose generator
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   └── workflow.py         # LangGraph StateGraph wiring & conditional self-healing loop
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── pdf_parser.py       # PyMuPDF text extractor + Gemini Vision OCR fallback
│   │       ├── github_tool.py      # GitHub REST API wrapper (profile, top repos, languages, READMEs)
│   │       ├── search_tool.py      # Tavily Search API integration
│   │       └── scraper_tool.py     # Jina Reader Markdown proxy + BeautifulSoup4 fallback
│   ├── sample_data/
│   │   ├── rahul_resume.pdf        # Generated sample Resume for Rahul Sharma (8.2 CGPA, B.Tech CSE)
│   │   └── rahul_marksheet.pdf     # Generated sample Academic Transcript / Marksheet for Rahul
│   ├── generte_rahul_docs.py       # Script to generate Rahul's sample Resume & Marksheet PDFs
│   ├── verify_setup.py             # Diagnostic script to verify GitHub, Tavily & Gemini API keys
│   ├── requirements.txt            # Python package dependencies
│   └── .env                        # Local environment keys (Excluded via .gitignore)
├── .gitignore
└── README.md


🚀 9. Installation, Configuration & Quickstart

Prerequisites

Python 3.10+ (Tested on Python 3.12)

API Keys for:

Google Gemini API Key (Google AI Studio)

Tavily Search API Key (Tavily)

GitHub Personal Access Token (Classic) (GitHub Developer Settings)

Step 1: Clone the Repository & Create Virtual Environment

git clone <your-github-repo-url>
cd scholarswarm-ai
python -m venv venv
.\venv\Scripts\activate


Step 2: Install Dependencies

pip install -r backend/requirements.txt
pip install beautifulsoup4 sse-starlette pymupdf python-multipart


Step 3: Configure Environment Variables (backend/.env)

Create a .env file inside the backend/ directory:

GEMINI_API_KEY="AIzaSyYourGeminiKeyHere"
GOOGLE_API_KEY="AIzaSyYourGeminiKeyHere"
GEMINI_MODEL="gemini-3.8-flash"
TAVILY_API_KEY="tvly-YourTavilyKeyHere"
GITHUB_TOKEN="ghp_YourGitHubClassicTokenHere"


Step 4: Verify API Keys & Generate Sample PDFs

Run the setup verification script and generate Rahul's sample Resume and Marksheet PDFs:

cd backend
python verify_setup.py
python generte_rahul_docs.py


Step 5: Launch the ScholarSwarm Server

From inside the backend/ directory, start the FastAPI server:

python -m uvicorn app.main:app --reload --port 8000


Step 6: Open the Mission Control Dashboard

Web Dashboard: Open http://127.0.0.1:8000/ in your browser.

Swagger API Docs: Open http://127.0.0.1:8000/docs to inspect the REST/SSE endpoints.

📡 10. API Endpoints & Real-Time SSE Protocol

Method

Endpoint

Description

GET

/

Serves the interactive ScholarSwarm Mission Control Dashboard UI.

POST

/api/v1/swarm/start

Accepts multipart/form-data (resume_file, marksheet_file, github_username, target_countries), initializes SwarmState, and returns a unique run_id.

GET

/api/v1/swarm/stream/{run_id}

Opens a Server-Sent Events (SSE) stream emitting real-time log, node_complete, and complete JSON payloads as each LangGraph agent finishes.

GET

/docs

Serves the interactive Swagger UI OpenAPI documentation for testing endpoints directly in the browser.

GET

/redoc

Serves the ReDoc OpenAPI specification interface.

GET

/openapi.json

Returns the raw OpenAPI 3.1 JSON schema for the ScholarSwarm FastAPI service.

📜 License & Hackathon Rules Compliance

Built individually for the TetraNoodle AI Hackathon 2026.

Uses 100% real public scholarship and university opportunities with verifiable source URLs.

Generates application drafts only (does not auto-submit real university applications without consent).