# backend/app/main.py
import sys
import os
import uuid
import json
import shutil
from typing import List, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from app.schemas import SwarmState
from app.graph.workflow import create_scholar_swarm_graph

app = FastAPI(title="ScholarSwarm AI Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

swarm_app = create_scholar_swarm_graph()
run_states = {}

UPLOAD_DIR = os.path.join(BACKEND_DIR, "sample_data", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/api/v1/swarm/start")
async def start_swarm(
    github_username: str = Form("torvalds"),
    target_countries: str = Form("Canada, Germany, Singapore"),
    resume_file: Optional[UploadFile] = File(None),
    marksheet_file: Optional[UploadFile] = File(None),
):
    run_id = uuid.uuid4().hex[:8]
    countries_list = [c.strip() for c in target_countries.split(",") if c.strip()]

    resume_path = os.path.join(BACKEND_DIR, "sample_data", "rahul_resume.pdf")
    marksheet_path = os.path.join(BACKEND_DIR, "sample_data", "rahul_marksheet.pdf")

    if resume_file and resume_file.filename:
        resume_path = os.path.join(UPLOAD_DIR, f"{run_id}_resume.pdf")
        with open(resume_path, "wb") as f:
            shutil.copyfileobj(resume_file.file, f)

    if marksheet_file and marksheet_file.filename:
        marksheet_path = os.path.join(UPLOAD_DIR, f"{run_id}_marksheet.pdf")
        with open(marksheet_path, "wb") as f:
            shutil.copyfileobj(marksheet_file.file, f)

    initial_state = SwarmState(
        resume_text_path=resume_path,
        marksheet_text_path=marksheet_path,
        github_username=github_username.strip() or "torvalds",
        target_countries=countries_list or ["Canada", "Germany", "Singapore"],
    )
    run_states[run_id] = initial_state.model_dump()
    return {"status": "started", "run_id": run_id}


@app.get("/api/v1/swarm/stream/{run_id}")
async def stream_swarm(run_id: str):
    async def event_generator():
        state_data = run_states.get(run_id)
        if not state_data:
            state_data = SwarmState().model_dump()

        accumulated = dict(state_data)
        sent_log_count = 0

        yield {
            "event": "log",
            "data": json.dumps({"message": f"🚀 Initializing ScholarSwarm (Run ID: {run_id})..."})
        }

        try:
            async for event in swarm_app.astream(SwarmState(**state_data)):
                for node_name, node_output in event.items():
                    if isinstance(node_output, dict):
                        accumulated.update(node_output)
                        all_logs = accumulated.get("recovery_logs", [])
                        new_logs = all_logs[sent_log_count:]
                        sent_log_count = len(all_logs)

                        # Serialize student profile immediately when Profiler completes
                        profile_obj = accumulated.get("student_profile")
                        profile_dict = (
                            profile_obj.model_dump()
                            if hasattr(profile_obj, "model_dump")
                            else (profile_obj if isinstance(profile_obj, dict) else None)
                        )

                        yield {
                            "event": "node_complete",
                            "data": json.dumps({
                                "node": node_name,
                                "new_logs": new_logs,
                                "student_profile": profile_dict if node_name == "profiler" else None,
                            })
                        }

            # Prepare final payload from accumulated state (no duplicate invoke!)
            profile_obj = accumulated.get("student_profile")
            profile_dict = (
                profile_obj.model_dump()
                if hasattr(profile_obj, "model_dump")
                else (profile_obj or {})
            )

            top_5_raw = accumulated.get("top_5_matches", [])
            top_5_list = [
                m.model_dump() if hasattr(m, "model_dump") else m for m in top_5_raw
            ]

            verified_raw = accumulated.get("verified_opportunities", [])
            verified_list = [
                v.model_dump() if hasattr(v, "model_dump") else v for v in verified_raw
            ]

            yield {
                "event": "complete",
                "data": json.dumps({
                    "student_profile": profile_dict,
                    "top_5_matches": top_5_list,
                    "verified_opportunities": verified_list,
                    "verified_count": len(verified_list),
                    "sop_draft": accumulated.get("sop_draft", ""),
                    "logs": accumulated.get("recovery_logs", []),
                })
            }
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(event_generator())


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ScholarSwarm AI — Autonomous Scholarship Finder</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans">
  <!-- Header -->
  <header class="border-b border-slate-800 bg-slate-900/70 backdrop-blur sticky top-0 z-20">
    <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <span class="text-2xl">🎓</span>
        <div>
          <h1 class="text-xl font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            ScholarSwarm AI
          </h1>
          <p class="text-xs text-slate-400">Autonomous 5-Agent Scholarship & University Discovery Swarm</p>
        </div>
      </div>
      <a href="/docs" target="_blank" class="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700">
        API Swagger Docs ↗
      </a>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-6 py-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
    <!-- Left Column: Input & Enriched Student Dossier -->
    <section class="lg:col-span-4 space-y-6">
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
        <h2 class="text-base font-semibold mb-4 flex items-center gap-2">
          <span>📄</span> 1. Student Profile & Credentials
        </h2>
        <form id="swarmForm" class="space-y-4">
          <div>
            <label class="block text-xs text-slate-400 mb-1">Resume PDF (Leave blank to use Rahul's Sample Resume)</label>
            <input type="file" name="resume_file" accept=".pdf" class="w-full text-xs text-slate-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-indigo-600/20 file:text-indigo-300 hover:file:bg-indigo-600/30" />
          </div>
          <div>
            <label class="block text-xs text-slate-400 mb-1">Marksheet PDF (Leave blank to use Rahul's Marksheet)</label>
            <input type="file" name="marksheet_file" accept=".pdf" class="w-full text-xs text-slate-300 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-indigo-600/20 file:text-indigo-300 hover:file:bg-indigo-600/30" />
          </div>
          <div>
            <label class="block text-xs text-slate-400 mb-1">GitHub Username or URL</label>
            <input type="text" name="github_username" value="karpathy" class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500" />
          </div>
          <div>
            <label class="block text-xs text-slate-400 mb-1">Target Countries (Comma-separated)</label>
            <input type="text" name="target_countries" value="Canada, Germany, Singapore" class="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-indigo-500" />
          </div>
          <button type="submit" id="launchBtn" class="w-full py-2.5 px-4 bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white font-semibold rounded-xl shadow-md transition">
            🚀 Launch Agent Swarm
          </button>
        </form>
      </div>

      <!-- Enriched Student Profile Card -->
      <div id="profileCard" class="bg-slate-900 border border-slate-800 rounded-2xl p-5 hidden">
        <h3 class="text-sm font-semibold text-indigo-400 mb-3">👤 Enriched Student Dossier</h3>
        <div id="profileContent" class="space-y-2 text-xs text-slate-300"></div>
      </div>
    </section>

    <!-- Right Column: Agent Stepper, Live Telemetry & Results -->
    <section class="lg:col-span-8 space-y-6">
      <!-- 5-Agent Swarm Stepper -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-5">
        <h2 class="text-sm font-semibold text-slate-300 mb-4">🤖 Autonomous Agent Swarm Pipeline</h2>
        <div class="grid grid-cols-5 gap-2 text-center text-xs">
          <div id="node-profiler" class="p-3 rounded-xl border border-slate-800 bg-slate-950">1. Profiler</div>
          <div id="node-scout" class="p-3 rounded-xl border border-slate-800 bg-slate-950">2. Scout</div>
          <div id="node-auditor" class="p-3 rounded-xl border border-slate-800 bg-slate-950">3. Auditor</div>
          <div id="node-strategist" class="p-3 rounded-xl border border-slate-800 bg-slate-950">4. Strategist</div>
          <div id="node-sop_writer" class="p-3 rounded-xl border border-slate-800 bg-slate-950">5. SOP Writer</div>
        </div>

        <!-- Live Telemetry Terminal -->
        <div id="terminal" class="mt-4 bg-slate-950 border border-slate-800 rounded-xl p-4 h-48 overflow-y-auto font-mono text-xs space-y-1 text-slate-300">
          <div class="text-slate-500">// Ready. Click "Launch Agent Swarm" to begin live research...</div>
        </div>
      </div>

      <!-- Results Tabs -->
      <div id="resultsSection" class="bg-slate-900 border border-slate-800 rounded-2xl p-5 hidden">
        <div class="flex gap-2 border-b border-slate-800 pb-3 mb-4">
          <button onclick="switchTab('top5')" id="tab-top5" class="px-4 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white">🏆 Top 5 Best Matches</button>
          <button onclick="switchTab('all')" id="tab-all" class="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300">🌐 All Verified Opportunities</button>
          <button onclick="switchTab('sop')" id="tab-sop" class="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300">✍️ Tailored SOP Draft</button>
        </div>

        <div id="panel-top5" class="space-y-4"></div>
        <div id="panel-all" class="hidden overflow-x-auto"></div>
        <div id="panel-sop" class="hidden">
          <pre id="sopContent" class="whitespace-pre-wrap bg-slate-950 border border-slate-800 rounded-xl p-5 text-xs text-slate-200 leading-relaxed"></pre>
        </div>
      </div>
    </section>
  </main>

  <script>
    const nodes = ['profiler', 'scout', 'auditor', 'strategist', 'sop_writer'];

    function appendLog(msg) {
      const term = document.getElementById('terminal');
      const div = document.createElement('div');
      if (msg.includes('[SUCCESS]')) div.className = 'text-emerald-400';
      else if (msg.includes('[RECOVERY]') || msg.includes('[WARN]')) div.className = 'text-amber-400';
      else if (msg.includes('[ERROR]')) div.className = 'text-rose-400';
      div.textContent = msg;
      term.appendChild(div);
      term.scrollTop = term.scrollHeight;
    }

    function highlightNode(doneNode) {
      const el = document.getElementById('node-' + doneNode);
      if (el) {
        el.className = 'p-3 rounded-xl border border-emerald-500/50 bg-emerald-500/10 text-emerald-300 font-semibold';
      }
    }

    function switchTab(tab) {
      ['top5', 'all', 'sop'].forEach(t => {
        document.getElementById('panel-' + t).classList.toggle('hidden', t !== tab);
        document.getElementById('tab-' + t).className = t === tab
          ? 'px-4 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 text-white'
          : 'px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300';
      });
    }

    function renderProfile(p) {
      if (!p || !p.full_name) return;
      document.getElementById('profileCard').classList.remove('hidden');
      document.getElementById('profileContent').innerHTML = `
        <div class="text-sm font-bold text-white">${p.full_name}</div>
        <div>${p.current_degree} • ${p.university}</div>
        <div class="inline-block px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 font-semibold">CGPA: ${p.cgpa} / ${p.cgpa_scale}</div>
        <div class="pt-2"><span class="text-slate-400">Skills:</span> ${(p.technical_skills || []).join(', ')}</div>
        <div><span class="text-amber-400">Missing Info Detected:</span> ${(p.missing_standard_credentials || []).join(', ') || 'None'}</div>
      `;
    }

    document.getElementById('swarmForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('launchBtn');
      btn.disabled = true;
      btn.textContent = '⏳ Swarm Running...';
      document.getElementById('terminal').innerHTML = '';
      nodes.forEach(n => {
        document.getElementById('node-' + n).className = 'p-3 rounded-xl border border-slate-800 bg-slate-950';
      });

      const formData = new FormData(e.target);
      const res = await fetch('/api/v1/swarm/start', { method: 'POST', body: formData });
      const { run_id } = await res.json();

      const evtSource = new EventSource('/api/v1/swarm/stream/' + run_id);

      evtSource.addEventListener('log', (e) => {
        const data = JSON.parse(e.data);
        appendLog(data.message);
      });

      evtSource.addEventListener('node_complete', (e) => {
        const data = JSON.parse(e.data);
        highlightNode(data.node);
        (data.new_logs || []).forEach(appendLog);
        if (data.student_profile) renderProfile(data.student_profile);
      });

      evtSource.addEventListener('complete', (e) => {
        const data = JSON.parse(e.data);
        evtSource.close();
        btn.disabled = false;
        btn.textContent = '🚀 Launch Agent Swarm';
        appendLog('🎉 Swarm Execution Complete! Verified ' + data.verified_count + ' opportunities.');

        renderProfile(data.student_profile);
        document.getElementById('resultsSection').classList.remove('hidden');

        // Render Top 5
        document.getElementById('panel-top5').innerHTML = (data.top_5_matches || []).map((m, idx) => `
          <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <div class="flex justify-between items-start">
              <div>
                <span class="text-xs font-bold text-indigo-400">#${idx + 1} Match (${m.fit_score}% Fit) • ${m.country}</span>
                <h4 class="text-base font-bold text-white">${m.university_or_body} — ${m.scholarship_name}</h4>
                <p class="text-xs text-slate-400">${m.program_name}</p>
              </div>
              <span class="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300">${m.eligibility_status}</span>
            </div>
            <p class="text-xs text-slate-300">${m.why_it_fits}</p>
            <div class="grid grid-cols-2 gap-2 text-xs bg-slate-900 p-3 rounded-lg">
              <div><span class="text-slate-400">💰 Funding:</span> ${m.funding_details}</div>
              <div><span class="text-slate-400">📅 Deadline:</span> ${m.deadline}</div>
              <div class="col-span-2"><span class="text-amber-400">⚠️ Missing Info:</span> ${(m.missing_info_for_student || []).join(', ') || 'None'}</div>
            </div>
            <div class="text-xs">
              <a href="${m.official_url}" target="_blank" class="text-cyan-400 hover:underline">🔗 Official Source URL ↗</a>
            </div>
          </div>
        `).join('');

        // Render All Verified Table
        document.getElementById('panel-all').innerHTML = `
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-slate-800 text-slate-400">
                <th class="py-2 px-3">University / Body</th>
                <th class="py-2 px-3">Scholarship / Program</th>
                <th class="py-2 px-3">Country</th>
                <th class="py-2 px-3">Status</th>
                <th class="py-2 px-3">Fit</th>
                <th class="py-2 px-3">Source</th>
              </tr>
            </thead>
            <tbody>
              ${(data.verified_opportunities || []).map(v => `
                <tr class="border-b border-slate-800/60">
                  <td class="py-2 px-3 font-medium">${v.university_or_body}</td>
                  <td class="py-2 px-3">${v.scholarship_name}</td>
                  <td class="py-2 px-3">${v.country}</td>
                  <td class="py-2 px-3">${v.eligibility_status}</td>
                  <td class="py-2 px-3 font-bold text-indigo-400">${v.fit_score}%</td>
                  <td class="py-2 px-3"><a href="${v.official_url}" target="_blank" class="text-cyan-400 underline">Verify ↗</a></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `;

        // Render SOP
        document.getElementById('sopContent').textContent = data.sop_draft || '';
      });

      evtSource.addEventListener('error', (e) => {
        evtSource.close();
        btn.disabled = false;
        btn.textContent = '🚀 Launch Agent Swarm';
        appendLog('[ERROR] Stream connection closed or encountered an error.');
      });
    });
  </script>
</body>
</html>
    """