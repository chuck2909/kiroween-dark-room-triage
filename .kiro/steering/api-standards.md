# API Standards

## REST Conventions
- POST /triage - Submit triage request
- GET /health - Health check endpoint
- Standard HTTP status codes

## Request/Response
- Content-Type: application/json
- Accept gzip compression
- Include request ID in headers

## Error Responses
```json
{
  "error": "string",
  "detail": "string",
  "request_id": "string",
  "timestamp": "ISO8601"
}
```

## Status Codes
- 200: Success
- 400: Bad request (invalid target)
- 429: Rate limit exceeded
- 502: Upstream service error (MCP failure)
- 503: Service unavailable

## Validation
- Target: non-empty string, valid domain or product name
- Depth: enum ["quick", "standard"]
- Include_enrichment: boolean

## Performance
- Timeout: 15s for quick, 30s for standard
- Max response size: 200KB
- Cache headers for GET endpoints
