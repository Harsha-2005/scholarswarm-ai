# Engineering Note: ScholarSwarm AI
**TetraNoodle AI Hackathon 2026**

## 1. Most Interesting Experiment: Single-Pass vs. Batched Multi-Source Verification in Cyclical Agent Graphs
During the development of ScholarSwarm, our most interesting experiment centered on how the **Scout Agent** (discovery) and **Auditor Agent** (verification and eligibility gap analysis) exchanged and verified live web data.

Initially, we experimented with a **1-to-1 sequential LLM verification loop**, where the Scout Agent discovered 15–19 candidate URLs via Tavily Search, and the Auditor Agent invoked the LLM independently on every single scraped webpage (15+ LLM calls per run). While conceptually simple, this created two major bottlenecks:
1. **Aggregator Fragmentation:** Many high-ranking scholarship search results are university department portals or curated scholarship directories containing 3–5 distinct scholarships on a single page, while other URLs are dead links or social media posts.
2. **Rate-Limit Starvation:** Firing 15+ back-to-back structured-output LLM requests immediately saturated the Gemini API Free Tier quota (5 requests/minute), causing cascading `HTTP 429` failures and triggering repeated self-healing loops.

**The Breakthrough:** We redesigned the Auditor Agent to use **Two-Stage Evidence Aggregation & Batched Structured Synthesis**. First, a deterministic Python scraping pipeline filters out low-signal social domains and extracts clean Markdown from up to 12 live URLs using a tiered proxy (Jina Reader API $\rightarrow$ BeautifulSoup4 fallback $\rightarrow$ Search Index Snippet fallback). Next, the Auditor Agent bundles these multi-source Markdown excerpts into a single 22,000-character evidence context window and performs **one batched structured-output reasoning pass** (`BatchVerifiedOpportunities`). 

This experiment yielded three major improvements:
* **80% Reduction in API Calls:** Total LLM invocations for the entire 5-agent swarm dropped from ~17 calls to just **3 calls** (`Profiler`, `Auditor`, `SOP Writer`), completely eliminating `429` rate-limit errors.
* **Cross-Source Deduplication:** Because the Auditor Agent sees all scraped sources simultaneously, it naturally deduplicates identical scholarships mentioned across multiple websites and extracts multiple distinct opportunities from official university funding pages.
* **Sub-30-Second Execution:** End-to-end swarm execution time dropped from over 2 minutes to ~25 seconds.

---

## 2. Biggest Technical Challenge: Surviving "Wild Web" Anti-Bot Firewalls & Dynamic Profile Injection
Our biggest technical challenge was building a **fault-tolerant web research pipeline** that never crashes when encountering real-world university portals, scanned PDFs, or unexpected student profiles ("The Final Surprise").

We encountered and solved three specific failure modes:
1. **Anti-Bot & Cloudflare Blocks on University Portals:** Direct HTTP requests to university domains frequently failed with `HTTP 403 Forbidden`, `ReadTimeout`, or JavaScript-empty shells. We solved this by engineering a **3-Tier Self-Healing Scraper (`scraper_tool.py`)**:
   * **Tier 1 (Primary):** Jina Reader Markdown Proxy (`https://r.jina.ai/<url>`) to render clean, LLM-friendly Markdown.
   * **Tier 2 (Fallback):** Local `BeautifulSoup4` HTML DOM stripper if the proxy times out.
   * **Tier 3 (Last Resort):** If a site completely blocks scraping (<150 characters returned), the Auditor automatically falls back to the indexed search snippet captured by the Scout Agent so valid opportunities are never lost.
2. **Scanned vs. Digital PDF Credentials:** Students often upload scanned image marksheets rather than digital text PDFs. In `pdf_parser.py`, we implemented an automatic character-density threshold: if `PyMuPDF` (`fitz`) extracts fewer than 50 characters, the tool automatically renders the PDF pages to 150-DPI PNG buffers in memory and invokes **Gemini Vision OCR** to recover the transcript tables.
3. **Zero-Hardcoding for Dynamic Profile Adaptation:** To ensure the system can handle any surprise student profile during live judging without code edits, all search query formulations, GPA scale normalizations, and SOP narrative prompts are dynamically parameterized from the runtime `SwarmState` Pydantic schema.