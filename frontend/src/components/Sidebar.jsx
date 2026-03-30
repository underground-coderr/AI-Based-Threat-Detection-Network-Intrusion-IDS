import { NavLink } from 'react-router-dom'
import { Shield, Activity, Bell, Zap, BarChart2 } from 'lucide-react'

const NAV = [
  { to: '/',       icon: Activity,  label: 'Overview' },
  { to: '/alerts', icon: Bell,      label: 'Alerts'   },
  { to: '/detect', icon: Zap,       label: 'Detect'   },
  { to: '/models', icon: BarChart2, label: 'Models'   },
]

export default function Sidebar({ engineReady }) {
  return (
    <aside style={{
      width: 210, minHeight: '100vh',
      background: 'var(--bg-surface)',
      borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column', flexShrink: 0,
    }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 10,
        padding: '24px 20px 20px',
        borderBottom: '1px solid var(--border)',
      }}>
        <Shield size={22} color="var(--accent-cyan)" />
        <div>
          <div style={{ fontFamily: 'var(--font-display)', fontSize: 18, fontWeight: 700 }}>
            ThreatNet
          </div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.08em' }}>
            IDS v1.0
          </div>
        </div>
      </div>

      <nav style={{ flex: 1, padding: '12px 0' }}>
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink key={to} to={to} end={to === '/'}
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '9px 20px', textDecoration: 'none', fontSize: 12,
              color: isActive ? 'var(--accent-cyan)' : 'var(--text-secondary)',
              borderLeft: `2px solid ${isActive ? 'var(--accent-cyan)' : 'transparent'}`,
              background: isActive ? 'rgba(0,212,255,0.05)' : 'transparent',
              transition: 'all 0.15s',
            })}>
            <Icon size={14} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div style={{
        padding: '16px 20px', borderTop: '1px solid var(--border)',
        fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.05em',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
          <span style={{
            width: 6, height: 6, borderRadius: '50%', flexShrink: 0,
            background: engineReady ? 'var(--accent-green)' : 'var(--accent-amber)',
            animation: engineReady ? 'pulse-dot 2s infinite' : 'none',
          }} />
          {engineReady ? 'ENGINE ONLINE' : 'ENGINE OFFLINE'}
        </div>
        CICIDS2017 DATASET
      </div>
    </aside>
  )
}