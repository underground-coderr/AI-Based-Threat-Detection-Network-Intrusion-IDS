import { useState } from 'react'
import { Send, RefreshCw, Zap } from 'lucide-react'
import { api } from '../utils/api.js'
import { attackColor } from '../utils/helpers.js'

const PRESETS = {
  'Normal HTTP': { 'SYN Flag Count': 1, 'Flow Duration': 50000, 'Total Fwd Packets': 10, 'Flow Bytes/s': 1200, 'FIN Flag Count': 1 },
  'Port Scan':   { 'SYN Flag Count': 1, 'Flow Duration': 500,   'Total Fwd Packets': 1,  'Flow Bytes/s': 800,  'RST Flag Count': 1 },
  'DoS Attack':  { 'SYN Flag Count': 850, 'Flow Duration': 5000000, 'Total Fwd Packets': 5000, 'Flow Bytes/s': 9000000, 'FIN Flag Count': 0 },
  'Brute Force': { 'SYN Flag Count': 1, 'Flow Duration': 30000000, 'Total Fwd Packets': 300, 'Flow Bytes/s': 4200, 'ACK Flag Count': 280 },
}

export default function Detect() {
  const [preset,      setPreset]      = useState('Normal HTTP')
  const [featureText, setFeatureText] = useState(JSON.stringify(PRESETS['Normal HTTP'], null, 2))
  const [result,      setResult]      = useState(null)
  const [loading,     setLoading]     = useState(false)
  const [error,       setError]       = useState(null)

  function loadPreset(name) {
    setPreset(name)
    setFeatureText(JSON.stringify(PRESETS[name], null, 2))
    setResult(null)
    setError(null)
  }

  async function submit() {
    setLoading(true)
    setError(null)
    try {
      const features = JSON.parse(featureText)
      const res = await api.detect({ features })
      setResult(res)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  const sevColor = result ? attackColor(result.attack_type) : 'var(--text-muted)'

  return (
    <div style={{ padding: '28px 32px' }}>
      <div style={{ fontFamily: 'var(--font-display)', fontSize: 22, fontWeight: 700, marginBottom: 6 }}>Live Detection</div>
      <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 28 }}>Submit a network flow for real-time analysis</div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '20px 22px' }}>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 14 }}>Feature Vector</div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 16 }}>
            {Object.keys(PRESETS).map(name => (
              <button key={name} onClick={() => loadPreset(name)} style={{
                padding: '5px 12px', fontSize: 11, borderRadius: 'var(--radius-sm)', cursor: 'pointer', fontFamily: 'var(--font-mono)', transition: 'all 0.15s',
                border: `1px solid ${preset === name ? 'var(--accent-cyan)' : 'var(--border)'}`,
                background: preset === name ? 'rgba(0,212,255,0.08)' : 'var(--bg-elevated)',
                color: preset === name ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              }}>{name}</button>
            ))}
          </div>

          <textarea
            value={featureText}
            onChange={e => { setFeatureText(e.target.value); setPreset(null) }}
            style={{ width: '100%', minHeight: 200, background: 'var(--bg-base)', border: '1px solid var(--border)', borderRadius: 'var(--radius-md)', color: 'var(--text-primary)', fontFamily: 'var(--font-mono)', fontSize: 12, padding: 14, resize: 'vertical', outline: 'none' }}
            spellCheck={false}
          />

          <button onClick={submit} disabled={loading} style={{
            display: 'flex', alignItems: 'center', gap: 8, marginTop: 14,
            background: loading ? 'var(--bg-elevated)' : 'var(--accent-cyan)',
            color: loading ? 'var(--text-muted)' : 'var(--bg-base)',
            border: 'none', borderRadius: 'var(--radius-sm)', padding: '9px 20px',
            fontSize: 12, fontFamily: 'var(--font-mono)', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer',
          }}>
            {loading ? <RefreshCw size={13} /> : <Send size={13} />}
            {loading ? 'Analyzing...' : 'Run Detection'}
          </button>

          {error && <div style={{ marginTop: 12, fontSize: 12, color: 'var(--accent-red)' }}>Error: {error}</div>}
        </div>

        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '20px 22px' }}>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 14 }}>Result</div>

          {!result ? (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 260, color: 'var(--text-muted)', gap: 10 }}>
              <Zap size={28} color="var(--border)" />
              <div style={{ fontSize: 12 }}>Submit a flow to see results</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div style={{ padding: 20, borderRadius: 'var(--radius-md)', border: `1px solid ${sevColor}`, background: `${sevColor}14`, textAlign: 'center' }}>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 800, color: sevColor }}>{result.attack_type}</div>
                <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
                  {result.severity_label} · {(result.confidence * 100).toFixed(1)}% confidence
                </div>
              </div>

              <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.06em' }}>MODEL BREAKDOWN</div>
              {Object.entries(result.model_results ?? {}).map(([model, r]) => (
                <div key={model} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border)' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: 11 }}>{model.toUpperCase()}</span>
                  <span style={{ color: (r.is_attack || r.label === 'ATTACK') ? 'var(--accent-red)' : 'var(--accent-green)', fontSize: 11, fontWeight: 500 }}>
                    {r.label} · {(r.confidence * 100).toFixed(1)}%
                  </span>
                </div>
              ))}

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)' }}>
                <span>Ensemble votes</span>
                <span style={{ color: 'var(--text-primary)' }}>{result.ensemble_votes?.attack}/{result.ensemble_votes?.total} attack</span>
              </div>

              {result.should_alert && (
                <div style={{ padding: '8px 12px', background: 'rgba(255,71,87,0.1)', border: '1px solid rgba(255,71,87,0.3)', borderRadius: 'var(--radius-sm)', fontSize: 11, color: 'var(--accent-red)' }}>
                  Alert raised · ID #{result.alert_id}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}