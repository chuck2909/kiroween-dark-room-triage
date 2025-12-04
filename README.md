# Dark Room Triage

Passive reconnaissance tool for security triage using MCP-based lookups.

## Architecture

```
├── api/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── test_main.py       # Tests
│   ├── requirements.txt   # Python dependencies
│   └── evidence.log       # MCP call metadata (auto-rotated at 1MB)
├── frontend/              # Next.js UI
│   ├── app/
│   │   ├── page.tsx      # Main triage interface
│   │   └── layout.tsx    # Root layout
│   ├── package.json
│   └── tsconfig.json
├── .kiro/
│   ├── spec/             # Feature specifications
│   ├── steering/         # Development standards
│   ├── hooks/            # Agent hooks
│   └── mcp.json          # MCP server configuration
```

## Quick Start

### Backend
```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Run Tests
```bash
cd api
pytest -v
```

## Features

- **POST /triage**: Submit domain/product for passive reconnaissance
- **LOW_DATA mode**: Caps results to 10, 15min cache, 200KB response limit
- **Dry-run mocks**: Local development without MCP dependencies
- **Auto-rotation**: Evidence log rotates at 1MB
- **Agent Hooks**: Auto-test on save, render briefs, snapshot metadata

## MCP Servers

Configured in `.kiro/mcp.json`:
- **cvefeed**: CVE search and product lookup
- **github**: Code search and repo metadata

Set `GITHUB_TOKEN` environment variable for GitHub access.

## Environment Variables

```bash
export LOW_DATA=true          # Enable data caps and caching
export GITHUB_TOKEN=ghp_xxx   # GitHub API token
```

## Acceptance Criteria

✅ ≤15s response time (quick mode)  
✅ ≤8 CVEs per brief  
✅ Sources include tool + timestamp  
✅ 400 on bad target, 502 on upstream error  
✅ Passive only—no intrusive scanning
