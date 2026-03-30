import { useCallback } from 'react'
import { Activity, AlertTriangle, Shield, Zap } from 'lucide-react'
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { usePolling } from '../hooks/usePolling.js'
import StatCard from '../components/StatCard.jsx'
import { api } from '../utils/api.js'
import { attackColor, formatTs } from '../utils/helpers.js'

const PALETTE = ['#00d4ff','#39d353','#f0a500','#ff4757','#bd93f9','#ff6b35','#ff4db8']

const card = {
  background: 'var(--bg-surface)', border: '1px solid var(--border)',
  borderRadius: 'var(--radius-lg)', padding: '18px 20px',
}

const cardTitle = {
  fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.08em',
  textTransform: 'uppercase', marginBottom: 16,
}

const Tip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, padding: '10px 14px', fontSize: 12 }}>
      <div style={{ color: 'var(--text-secondary)', marginBottom: 4 }}>{label}</div>
      {payload.map(p => <div key={p.name} style={{ color: p.color }}>{p.name}: {p.value}</div>)}
    </div>
  )
}

export default function Overview() {
  const fetchStats  = useCallback(() => api.stats(), [])
  const fetchAlerts = useCallback(() => api.alerts({ limit: 8 }), [])

  const { data: stats }      = usePolling(fetchStats,  10000)
  const { data: alertsData } = usePolling(fetchAlerts,  8000)

  const attackRate = stats ? (stats.attack_rate * 100).toFixed(1) : '—'

  const pieData = Object.entries(stats?.by_attack_type ?? {}).map(([name, value], i) => ({
    name, value, fill: PALETTE[i % PALETTE.length],
  }))

  return (
    <div style={{ padding: '28px 32px', flex: 1 }}>
      <div style={{ marginBottom: 28 }}>
        <div style={{ fontFamily: 'var(--font-display)', fontSize: 22, fontWeight: 700 }}>System Overview</div>
        <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
          Real-time network intrusion detection · CICIDS2017
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 16, marginBottom: 24 }}>
        <StatCard label="Total Analyzed"   value={stats?.total_analyzed?.toLocaleString() ?? '—'} sub="network flows"   color="var(--accent-cyan)"   icon={Activity} />
        <StatCard label="Threats Detected" value={stats?.total_alerts?.toLocaleString() ?? '—'}   sub={`${attackRate}% rate`} color="var(--accent-red)" icon={AlertTriangle} />
        <StatCard label="Last 24h"         value={stats?.recent_24h ?? '—'}                        sub="new alerts"      color="var(--accent-amber)"  icon={Zap} />
        <StatCard label="Status"           value="ONLINE"                                           sub="3 models active" color="var(--accent-green)"  icon={Shield} />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 16, marginBottom: 24 }}>
        <div style={card}>
          <div style={cardTitle}>Attack Type Distribution</div>
          {pieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={pieData} layout="vertical" margin={{ left: 20, right: 20 }}>
                <XAxis type="number" tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
                <YAxis dataKey="name" type="category" width={90} tick={{ fill: 'var(--text-secondary)', fontSize: 11 }} />
                <Tooltip content={<Tip />} />
                <Bar dataKey="value" radius={[0,3,3,0]}>
                  {pieData.map((entry, i) => (
                    <rect key={i} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '40px 0' }}>No threat data yet</div>
          )}
        </div>

        <div style={card}>
          <div style={cardTitle}>By Severity</div>
          {Object.entries(stats?.by_severity ?? {}).length > 0 ? (
            Object.entries(stats.by_severity).map(([sev, cnt]) => (
              <div key={sev} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10, fontSize: 12 }}>
                <span style={{ color: 'var(--text-secondary)' }}>{sev}</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{cnt}</span>
              </div>
            ))
          ) : (
            <div style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '40px 0' }}>No data yet</div>
          )}
        </div>
      </div>

      <div style={card}>
        <div style={cardTitle}>Recent Alerts</div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr>
              {['Time','Type','Severity','Confidence','Src IP'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '6px 10px', fontSize: 10, color: 'var(--text-muted)', borderBottom: '1px solid var(--border)' }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(alertsData?.alerts ?? []).map(a => (
              <tr key={a.id} style={{ borderBottom: '1px solid var(--border)' }}>
                <td style={{ padding: '8px 10px', fontSize: 11, color: 'var(--text-secondary)' }}>{formatTs(a.timestamp)}</td>
                <td style={{ padding: '8px 10px', fontSize: 11, color: attackColor(a.attack_type), fontWeight: 500 }}>{a.attack_type}</td>
                <td style={{ padding: '8px 10px' }}>
                  <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 3, background: `${attackColor(a.attack_type)}22`, color: attackColor(a.attack_type) }}>
                    {a.severity_label}
                  </span>
                </td>
                <td style={{ padding: '8px 10px', fontSize: 11 }}>{(a.confidence * 100).toFixed(1)}%</td>
                <td style={{ padding: '8px 10px', fontSize: 11, color: 'var(--text-muted)' }}>{a.source_ip ?? '—'}</td>
              </tr>
            ))}
            {!alertsData?.alerts?.length && (
              <tr><td colSpan={5} style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>No alerts yet</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}