# Relic Recon Spec

## Overview
Passive reconnaissance tool that accepts a domain/target and performs MCP-based lookups to generate a security triage brief.

## Requirements

### Inputs
```json
{
  "target": "string (required)",
  "depth": "quick|standard (default: quick)",
  "include_enrichment": "boolean (default: true)"
}
```

### Process Flow
1. Normalize target (domain/product name)
2. MCP cvefeed.search_cves(product_hint=target) - cap N=10
3. MCP github.code_search(query=target) - cap N=10
4. Deduplicate and normalize results
5. Rank likely exposures
6. Generate JSON response + markdown brief

### Outputs

#### JSON Response
```json
{
  "assets": [],
  "tech": [],
  "cves": [],
  "exposures": [],
  "checks": [],
  "sources": [{"tool": "string", "timestamp": "ISO8601"}]
}
```

#### Markdown Brief (brief.md)
Sections:
- Assets
- Tech
- CVEs
- Exposures
- Checks
- Appendix (sources)

### Acceptance Criteria
- ≤15s response time for quick path
- ≤8 CVEs in brief
- Sources list includes tool + timestamp
- 400 on bad target
- 502 on upstream MCP error
- Passive only—no intrusive scanning

### Constraints
- LOW_DATA mode: cap results to 10, in-memory cache 15m, abort response >200KB
- Dry-run mocks for local dev
- No secrets in config; read env at runtime
