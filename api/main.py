from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import logging
import asyncio
import httpx

app = FastAPI(title="Relic Recon API")

# Runtime flags/env
STUB_MODE = os.getenv("STUB_MODE", "true").lower() == "true"   
LOW_DATA = os.getenv("LOW_DATA", "true").lower() == "true"    
NVD_API_KEY = os.getenv("NVD_API_KEY", "").strip()             
MAX_RESULTS = 10 if LOW_DATA else 25

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory cache
cache: Dict[str, tuple[Any, datetime]] = {}
CACHE_TTL = timedelta(minutes=15)
MAX_RESPONSE_SIZE = 200 * 1024  # 200KB

class TriageRequest(BaseModel):
    target: str = Field(..., min_length=1)
    depth: Literal["quick", "standard"] = "quick"
    include_enrichment: bool = True

    @validator("target")
    def validate_target(cls, v):
        if not v or not v.strip():
            raise ValueError("Target cannot be empty")
        return v.strip()

class TriageResponse(BaseModel):
    assets: List[str]
    tech: List[str]
    cves: List[Dict[str, Any]]
    exposures: List[str]
    checks: List[str]
    sources: List[Dict[str, str]]

def get_cached(key: str) -> Optional[Any]:
    if key in cache:
        data, timestamp = cache[key]
        if datetime.now() - timestamp < CACHE_TTL:
            return data
        del cache[key]
    return None

def set_cached(key: str, data: Any):
    cache[key] = (data, datetime.now())

async def mock_cve_search(target: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Mock CVE search for dry-run/local dev"""
    await asyncio.sleep(0.1)
    return [
        {
            "cve_id": f"CVE-2024-{1000 + i}",
            "cvss": 7.5 - (i * 0.5),
            "summary": f"Vulnerability in {target} component {i+1}",
            "severity": "High" if i < 3 else "Medium"
        }
        for i in range(min(3, limit))
    ]

async def mock_github_search(target: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Mock GitHub code search for dry-run/local dev"""
    await asyncio.sleep(0.1)
    return [
        {
            "repo": f"example/repo-{i+1}",
            "file": f"config/{target}.yml",
            "snippet": f"Potential exposure in {target} configuration"
        }
        for i in range(min(2, limit))
    ]

#NVD helper functions
async def _http_get_json(url: str, params: dict, headers: dict, size_cap: int = 200_000, timeout: float = 8.0):
    async with httpx.AsyncClient(timeout=timeout) as client:
        r = await client.get(url, params=params, headers=headers)
        r.raise_for_status()
        cl = r.headers.get("content-length")
        if cl and cl.isdigit() and int(cl) > size_cap:
            raise HTTPException(502, "Upstream too large")
        return r.json()

async def _lookup_cves_nvd(keyword: str, limit: int):
    """
    Low-data CVE lookup via NVD v2 API. Hard-capped results + brief fields.
    Works without NVD_API_KEY, but the key improves rate limits.
    """
    headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}
    params = {
        "keywordSearch": keyword,
        "resultsPerPage": max(1, min(limit, 10)),  # hard cap for data use
    }
    data = await _http_get_json(
        "https://services.nvd.nist.gov/rest/json/cves/2.0",
        params=params,
        headers=headers,
    )
    items = []
    for v in data.get("vulnerabilities", []):
        c = v.get("cve", {})
        cve_id = c.get("id")
        descs = c.get("descriptions", [])
        summary = (descs[0]["value"] if descs else "N/A")[:240]
        metrics = c.get("metrics", {})
        cvss, severity = 0.0, "Unknown"
        if "cvssMetricV31" in metrics:
            m = metrics["cvssMetricV31"][0]
            cvss = m.get("cvssData", {}).get("baseScore", 0.0)
            severity = m.get("baseSeverity", "Unknown").title()
        elif "cvssMetricV2" in metrics:
            m = metrics["cvssMetricV2"][0]
            cvss = m.get("cvssData", {}).get("baseScore", m.get("baseScore", 0.0))
            severity = "High" if cvss and float(cvss) >= 7 else "Medium"
        items.append({"cve_id": cve_id, "cvss": cvss or 0.0, "summary": summary, "severity": severity})
    return items

@app.get("/health")
async def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.post("/triage", response_model=TriageResponse)
async def triage(request: TriageRequest, req: Request):
    # include the mode in the cache key so stub/real don’t mix
    cache_key = f"{request.target}:{request.depth}:{request.include_enrichment}:{'stub' if STUB_MODE else 'nvd'}"

    # cache check keeps bandwidth tiny
    if LOW_DATA:
        cached = get_cached(cache_key)
        if cached:
            logger.info(f"Cache hit for {request.target}")
            return cached

    try:
        # smaller caps in LOW_DATA, slightly larger otherwise
        limit = 5 if request.depth == "quick" else MAX_RESULTS
        timeout = 10 if request.depth == "quick" else 20

        if STUB_MODE:
            # no external calls
            cves_task = asyncio.create_task(mock_cve_search(request.target, limit))
            github_task = asyncio.create_task(mock_github_search(request.target, limit))
            cves, github_results = await asyncio.wait_for(
                asyncio.gather(cves_task, github_task),
                timeout=timeout
            )
            sources = [
                {"tool": "stub-cve", "timestamp": datetime.utcnow().isoformat()},
                {"tool": "stub-github", "timestamp": datetime.utcnow().isoformat()},
            ]
        else:
            # one small, capped NVD request; exposures still mocked
            cves = await asyncio.wait_for(_lookup_cves_nvd(request.target, limit), timeout=timeout)
            github_results = await asyncio.wait_for(mock_github_search(request.target, 2), timeout=timeout)
            sources = [
                {"tool": "nvd", "timestamp": datetime.utcnow().isoformat()},
                {"tool": "stub-github", "timestamp": datetime.utcnow().isoformat()},
            ]

        response = TriageResponse(
            assets=[request.target],
            tech=["Unknown"],
            cves=cves[:8],  # UI safety cap
            exposures=[r["snippet"] for r in github_results],
            checks=[
                "Verify CVE applicability to in-scope assets",
                "Review exposed configurations (passive only)",
                "Check TLS/headers and CSP",
                "Enumerate subdomains (passive)",
            ],
            sources=sources,
        )

        if LOW_DATA:
            set_cached(cache_key, response)

        log_evidence(request.target, response)
        return response

    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timeout")
    except Exception as e:
        logger.error(f"Triage error: {e}")
        raise HTTPException(status_code=502, detail="Upstream service error")

def log_evidence(target: str, response: TriageResponse):
    """Log MCP call metadata to evidence.log with rotation"""
    log_file = "api/evidence.log"
    max_size = 1024 * 1024  # 1MB
    
    try:
        if os.path.exists(log_file) and os.path.getsize(log_file) > max_size:
            os.rename(log_file, f"{log_file}.{datetime.now().strftime('%Y%m%d%H%M%S')}")
        
        with open(log_file, "a") as f:
            f.write(f"{datetime.utcnow().isoformat()} | {target} | {len(response.cves)} CVEs | {len(response.exposures)} exposures\n")
    except Exception as e:
        logger.error(f"Evidence logging error: {e}")
