import { useState, useCallback } from 'react'
import { CheckCheck } from 'lucide-react'
import { usePolling } from '../hooks/usePolling.js'
import { api } from '../utils/api.js'
import { attackColor, formatTs, formatDate } from '../utils/helpers.js'

export default function Alerts() {
  const [sevFilter,  setSevFilter]  = useState('')
  const [typeFilter, setTypeFilter] = useState('')

  const fetchAlerts = useCallback(() => api.alerts({
    limit: 100,
    ...(sevFilter  ? { severity:    sevFilter  } : {}),
    ...(typeFilter ? { attack_type: typeFilter } : {}),
  }), [sevFilter, typeFilter])

  const { data, refresh } = usePolling(fetchAlerts, 8000)
  const alerts = data?.alerts ?? []

  async function ackAll() {
    for (const a of alerts.filter(x => !x.is_acknowledged)) {
      await api.acknowledge(a.id)
    }
    refresh()
  }

  const sel = {
    background: 'var(--bg-elevated)', border: '1px solid var(--border)',
    color: 'var(--text-primary)', borderRadius: 'var(--radius-sm)',
    padding: '6px 10px', fontSize: 11, fontFamily: 'var(--font-mono)', cursor: 'pointer',
  }

  return (
    <div style={{ padding: '28px 32px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 22, fontWeight: 700 }}>Alerts</div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>{data?.total ?? 0} total</div>
        </div>
        <button onClick={ackAll} style={{ display: 'flex', alignItems: 'center', gap: 6, background: 'var(--bg-elevated)', border: '1px solid var(--border)', color: 'var(--accent-green)', borderRadius: 'var(--radius-sm)', padding: '7px 14px', fontSize: 11, cursor: 'pointer', fontFamily: 'var(--font-mono)' }}>
          <CheckCheck size={13} /> Acknowledge All
        </button>
      </div>

      <div style={{ display: 'flex', gap: 10, marginBottom: 18 }}>
        <select style={sel} value={sevFilter} onChange={e => setSevFilter(e.target.value)}>
          <option value="">All Severities</option>
          {['Critical','High','Medium','Low','None'].map(s => <option key={s}>{s}</option>)}
        </select>
        <select style={sel} value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          <option value="">All Types</option>
          {['DoS','DDoS','PortScan','BruteForce','WebAttack','Bot'].map(t => <option key={t}>{t}</option>)}
        </select>
      </div>

      <table style={{ width: '100%', borderCollapse: 'collapse', background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
        <thead>
          <tr>
            {['ID','Date','Time','Type','Severity','Confidence','Status'].map(h => (
              <th key={h} style={{ textAlign: 'left', padding: '10px 14px', fontSize: 10, color: 'var(--text-muted)', borderBottom: '1px solid var(--border)', background: 'var(--bg-elevated)' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {alerts.map(a => (
            <tr key={a.id} style={{ borderBottom: '1px solid var(--border)', opacity: a.is_acknowledged ? 0.5 : 1 }}>
              <td style={{ padding: '9px 14px', fontSize: 11, color: 'var(--text-muted)' }}>#{a.id}</td>
              <td style={{ padding: '9px 14px', fontSize: 11, color: 'var(--text-secondary)' }}>{formatDate(a.timestamp)}</td>
              <td style={{ padding: '9px 14px', fontSize: 11, color: 'var(--text-secondary)' }}>{formatTs(a.timestamp)}</td>
              <td style={{ padding: '9px 14px', fontSize: 11, color: attackColor(a.attack_type), fontWeight: 500 }}>{a.attack_type}</td>
              <td style={{ padding: '9px 14px' }}>
                <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 3, background: `${attackColor(a.attack_type)}22`, color: attackColor(a.attack_type) }}>
                  {a.severity_label}
                </span>
              </td>
              <td style={{ padding: '9px 14px', fontSize: 11 }}>{(a.confidence * 100).toFixed(1)}%</td>
              <td style={{ padding: '9px 14px' }}>
                {a.is_acknowledged
                  ? <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>ACK</span>
                  : <span style={{ fontSize: 10, color: 'var(--accent-amber)', animation: 'pulse-dot 2s infinite' }}>NEW</span>
                }
              </td>
            </tr>
          ))}
          {!alerts.length && (
            <tr><td colSpan={7} style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)' }}>No alerts match filters</td></tr>
          )}
        </tbody>
      </table>
    </div>
  )
}