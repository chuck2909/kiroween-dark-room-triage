# Dark Room Triage

Passive, low-data passive reconnaissance for quick security triage. Paste a domain → get assets, a tech hint, top CVEs, exposures, and analyst checks. Built with Kiro (Specs, Steering, Hooks) + FastAPI + Next.js.

## Architecture

```
├── api/                    # FastAPI backend
│   ├── main.py             # API endpoints
│   ├── test_main.py        # Tests
│   ├── requirements.txt    # Python dependencies
│   └── evidence.log        # Evidence metadata (auto-rotated at 1MB)
├── frontend/               # Next.js UI
│   ├── app/
│   │   ├── page.tsx        # Main triage interface
│   │   └── layout.tsx      # Root layout
│   ├── package.json
│   └── tsconfig.json
├── .kiro/
│   ├── spec/               # Feature specifications
│   ├── steering/           # Development standards
│   ├── hooks/              # Agent hooks (tests/snapshots)
│   └── mcp.json            # MCP server configuration (scaffold)
```

## Local Demo URLs

- **API:** http://127.0.0.1:8000  (OpenAPI: http://127.0.0.1:8000/docs)  
- **UI:**  http://localhost:3000

## Run Locally (exact commands)

```bash
# --- API ---
cd api

# create venv on first run
python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt

# or, if venv already exists:
source .venv/bin/activate

uvicorn main:app --reload --port 8000

# --- UI ---
cd ../frontend

npm install   # first time only

# create UI env file if missing:
echo 'NEXT_PUBLIC_API_BASE=http://localhost:8000' > .env.local

npm run dev
```

## Environment Variables

```bash
# api/.env (or export in your shell)
LOW_DATA=true                 # keep bandwidth tiny (caps + 15 min cache)
STUB_MODE=true                # default stubbed data (no external calls)
MCP_SERVERS_PATH=../.kiro/mcp.json
NVD_API_KEY=                  # optional; improves NVD rate limits in real mode
# GITHUB_TOKEN optional; GitHub lookups are stubbed when LOW_DATA=true
```

## Optional: Real-mode CVEs (one small call, then cached)

```bash
# API terminal only
export STUB_MODE=false
# optional: export NVD_API_KEY=your_key
uvicorn main:app --reload --port 8000
```

## Features

- POST /triage → assets, tech hint, capped CVEs, exposures, analyst checks
- Low-data policy → ≤8 CVEs, response size cap, 15-min cache
- Stub mode → zero external calls for local dev & demos
- Evidence log → simple metadata with rotation
- Hooks/Steering → auto tests & consistent style via .kiro/*

## Tests

```bash
cd api
source .venv/bin/activate
pytest -v
```

## MCP / Kiro usage

- Specs: .kiro/spec/dark-room-triage.spec.md (contract: inputs/outputs/limits)
- Steering: .kiro/steering/* (API standards + response style)
- Agent Hooks: .kiro/hooks/* (on-save tests, snapshot metadata)
- MCP: .kiro/mcp.json scaffold; real CVE lookup currently uses a tiny NVD GET and is ready to swap to an MCP HTTP tool.

## Acceptance Criteria

✅ ≤15s response (quick) • ✅ ≤8 CVEs per brief • ✅ Sources include tool+timestamp
✅ 400 on bad target; 502 on upstream error • ✅ Passive only—no intrusive scans


## How I Used Kiro (First-Timer)

**Starting with Vibe.** I’m new to Kiro, so I began in *Vibe* mode to talk through what I wanted: a super-simple “paste a domain → get a triage brief.” Vibe helped me scaffold both the FastAPI backend and the Next.js page quickly.

**Spec first, then iterate.** I saved a spec at `.kiro/spec/dark-room-triage.spec.md` that spelled out inputs/outputs, guardrails (≤8 CVEs, ≤15s in quick mode), and “passive only” rules. That spec made it easy to keep the API and UI in sync while I learned.

**Agent hooks for feedback.** I used hooks in `.kiro/hooks/` (like a pytest-on-save) so when I edited `main.py`, tests ran automatically. The render/snapshot hooks helped capture small artifacts and timestamps so I could see progress without digging.

**Steering docs for consistency.** The files in `.kiro/steering/` nudged Kiro toward short, analyst-friendly output and kept basic API style consistent while I was still figuring things out.

**MCP, but low-data.** I set up `.kiro/mcp.json` to wire external lookups, but during development I ran in “low-data / stub mode” so I didn’t burn bandwidth. The code is ready for real CVE/GitHub lookups with caching and caps when I flip that on.