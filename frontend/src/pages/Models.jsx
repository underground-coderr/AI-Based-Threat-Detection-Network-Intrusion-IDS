import { useCallback } from 'react'
import { usePolling } from '../hooks/usePolling.js'
import { api } from '../utils/api.js'

const MODEL_COLORS = { random_forest: '#00d4ff', xgboost: '#39d353', lstm: '#bd93f9' }
const MODEL_LABELS = { random_forest: 'Random Forest', xgboost: 'XGBoost', lstm: 'LSTM' }

function Bar({ value, color }) {
  return (
    <div style={{ height: 4, background: 'var(--border)', borderRadius: 2, marginTop: 4, overflow: 'hidden' }}>
      <div style={{ height: '100%', width: `${(value ?? 0) * 100}%`, background: color, borderRadius: 2, transition: 'width 0.5s ease' }} />
    </div>
  )
}

export default function Models() {
  const fetchReport = useCallback(() => api.modelReport(), [])
  const { data } = usePolling(fetchReport, 60000)

  const models  = data?.models  ?? {}
  const classes = data?.class_names ?? []

  return (
    <div style={{ padding: '28px 32px' }}>
      <div style={{ fontFamily: 'var(--font-display)', fontSize: 22, fontWeight: 700, marginBottom: 6 }}>Model Performance</div>
      <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginBottom: 28 }}>Evaluation metrics from test set</div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 16, marginBottom: 24 }}>
        {['random_forest','xgboost','lstm'].map(name => {
          const m     = models[name] ?? {}
          const color = MODEL_COLORS[name]
          const f1    = m.f1 ?? m.macro_f1
          return (
            <div key={name} style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderTop: `2px solid ${color}`, borderRadius: 'var(--radius-lg)', padding: '20px 22px' }}>
              <div style={{ fontFamily: 'var(--font-display)', fontSize: 16, fontWeight: 700, color, marginBottom: 16 }}>
                {MODEL_LABELS[name]}
              </div>
              {m.status === 'not_trained' ? (
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Not trained yet</div>
              ) : f1 != null ? (
                <>
                  <div style={{ marginBottom: 12 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11 }}>
                      <span style={{ color: 'var(--text-secondary)' }}>F1 Score</span>
                      <span style={{ color, fontWeight: 600 }}>{(f1 * 100).toFixed(1)}%</span>
                    </div>
                    <Bar value={f1} color={color} />
                  </div>
                  {m.accuracy != null && (
                    <div style={{ marginBottom: 12 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11 }}>
                        <span style={{ color: 'var(--text-secondary)' }}>Accuracy</span>
                        <span style={{ color, fontWeight: 600 }}>{(m.accuracy * 100).toFixed(1)}%</span>
                      </div>
                      <Bar value={m.accuracy} color={color} />
                    </div>
                  )}
                </>
              ) : (
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Run evaluate.py to see metrics</div>
              )}
            </div>
          )
        })}
      </div>

      <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border)', borderRadius: 'var(--radius-lg)', padding: '20px 22px' }}>
        <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase', marginBottom: 16 }}>Attack Classes</div>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          {classes.map(c => (
            <span key={c} style={{ padding: '3px 10px', borderRadius: 3, fontSize: 11, background: 'var(--bg-elevated)', border: '1px solid var(--border)', color: c === 'BENIGN' ? 'var(--accent-green)' : 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
              {c}
            </span>
          ))}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 20 }}>
          {[
            { label: 'Dataset',    value: 'CICIDS2017' },
            { label: 'Features',   value: data?.n_features ?? '—' },
            { label: 'Test Split', value: '20%' },
            { label: 'Balancing',  value: 'SMOTE' },
          ].map(({ label, value }) => (
            <div key={label} style={{ padding: '12px 16px', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.06em', marginBottom: 4 }}>{label}</div>
              <div style={{ fontSize: 14, fontWeight: 600 }}>{value}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}