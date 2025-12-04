# Foundation Standards

## Project Philosophy
- Minimal, focused implementations
- Security-first approach
- Passive reconnaissance only
- No intrusive scanning or active probing

## Code Standards
- Type hints required (Python)
- TypeScript strict mode (Next.js)
- Error handling at all boundaries
- Logging with structured context

## Performance
- Response times: ≤15s for quick operations
- Data caps: 200KB max response size
- Caching: 15min in-memory for LOW_DATA mode
- Result limits: N=10 for external lookups

## Security
- No secrets in code or config files
- Environment variables for credentials
- Input validation on all endpoints
- Rate limiting on public endpoints
