export default function StatCard({ label, value, sub, color, icon: Icon }) {
  return (
    <div style={{
      background: 'var(--bg-surface)', border: '1px solid var(--border)',
      borderLeft: `3px solid ${color || 'var(--border)'}`,
      borderRadius: 'var(--radius-lg)', padding: '18px 20px',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
        <span style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
          {label}
        </span>
        {Icon && <Icon size={14} color={color || 'var(--text-muted)'} />}
      </div>
      <div style={{ fontFamily: 'var(--font-display)', fontSize: 28, fontWeight: 700, color: color || 'var(--text-primary)', lineHeight: 1 }}>
        {value ?? '—'}
      </div>
      {sub && <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 6 }}>{sub}</div>}
    </div>
  )
}