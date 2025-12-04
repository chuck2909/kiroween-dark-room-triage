# Triage Brief Style Guide

## Structure
All triage briefs follow this exact structure:

### 1. Assets
- List discovered assets/domains
- Include confidence scores
- Note any subdomains or related properties

### 2. Tech
- Technology stack identified
- Versions when available
- Framework and library details

### 3. CVEs
- Maximum 8 CVEs per brief
- Sort by severity (Critical → High → Medium)
- Include: CVE-ID, CVSS score, summary
- Link to official CVE entry

### 4. Exposures
- Potential security exposures
- Misconfigurations
- Public code leaks
- Sensitive data exposure

### 5. Checks
- Recommended verification steps
- Manual checks to perform
- Tools to run for deeper analysis

### 6. Appendix
- Sources with timestamps
- Tool versions used
- Query parameters
- Limitations and caveats

## Formatting
- Use markdown tables for structured data
- Keep descriptions concise (1-2 sentences)
- Include severity badges: 🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low
- Timestamp format: ISO 8601
