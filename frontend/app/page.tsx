'use client';

import { useState } from 'react';

interface TriageResult {
  assets: string[];
  tech: string[];
  cves: Array<{
    cve_id: string;
    cvss: number;
    summary: string;
    severity: string;
  }>;
  exposures: string[];
  checks: string[];
  sources: Array<{ tool: string; timestamp: string }>;
}

export default function Home() {
  const [target, setTarget] = useState('');
  const [depth, setDepth] = useState<'quick' | 'standard'>('quick');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TriageResult | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/triage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target, depth, include_enrichment: true }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    const badges: Record<string, string> = {
      Critical: '🔴',
      High: '🟠',
      Medium: '🟡',
      Low: '🟢',
    };
    return badges[severity] || '⚪';
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem', fontFamily: 'system-ui' }}>
      <h1 style={{ fontSize: '2rem', marginBottom: '1rem' }}>🕵️ Relic Recon</h1>
      <p style={{ color: '#666', marginBottom: '2rem' }}>Passive reconnaissance and security triage</p>

      <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
          <input
            type="text"
            value={target}
            onChange={(e) => setTarget(e.target.value)}
            placeholder="Enter domain or product name"
            required
            style={{
              flex: 1,
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem',
            }}
          />
          <select
            value={depth}
            onChange={(e) => setDepth(e.target.value as 'quick' | 'standard')}
            style={{
              padding: '0.75rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem',
            }}
          >
            <option value="quick">Quick</option>
            <option value="standard">Standard</option>
          </select>
          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '0.75rem 2rem',
              background: loading ? '#ccc' : '#000',
              color: '#fff',
              border: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              cursor: loading ? 'not-allowed' : 'pointer',
            }}
          >
            {loading ? 'Analyzing...' : 'Triage'}
          </button>
        </div>
      </form>

      {error && (
        <div style={{ padding: '1rem', background: '#fee', border: '1px solid #fcc', borderRadius: '4px', marginBottom: '1rem' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div>
          <Section title="Assets">
            <ul>{result.assets.map((a, i) => <li key={i}>{a}</li>)}</ul>
          </Section>

          <Section title="Technology">
            <ul>{result.tech.map((t, i) => <li key={i}>{t}</li>)}</ul>
          </Section>

          <Section title="CVEs">
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ background: '#f5f5f5' }}>
                  <th style={thStyle}>Severity</th>
                  <th style={thStyle}>CVE ID</th>
                  <th style={thStyle}>CVSS</th>
                  <th style={thStyle}>Summary</th>
                </tr>
              </thead>
              <tbody>
                {result.cves.map((cve, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={tdStyle}>{getSeverityBadge(cve.severity)} {cve.severity}</td>
                    <td style={tdStyle}>{cve.cve_id}</td>
                    <td style={tdStyle}>{cve.cvss}</td>
                    <td style={tdStyle}>{cve.summary}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Section>

          <Section title="Exposures">
            <ul>{result.exposures.map((e, i) => <li key={i}>{e}</li>)}</ul>
          </Section>

          <Section title="Recommended Checks">
            <ul>{result.checks.map((c, i) => <li key={i}>{c}</li>)}</ul>
          </Section>

          <Section title="Sources">
            <ul>
              {result.sources.map((s, i) => (
                <li key={i}>{s.tool} - {new Date(s.timestamp).toLocaleString()}</li>
              ))}
            </ul>
          </Section>
        </div>
      )}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ marginBottom: '2rem' }}>
      <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', borderBottom: '2px solid #000', paddingBottom: '0.5rem' }}>
        {title}
      </h2>
      {children}
    </div>
  );
}

const thStyle: React.CSSProperties = {
  textAlign: 'left',
  padding: '0.75rem',
  fontWeight: 'bold',
};

const tdStyle: React.CSSProperties = {
  padding: '0.75rem',
};
