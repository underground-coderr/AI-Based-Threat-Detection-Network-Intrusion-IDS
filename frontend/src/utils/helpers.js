export const ATTACK_COLORS = {
  BENIGN:     '#39d353',
  DoS:        '#f0a500',
  DDoS:       '#ff4757',
  PortScan:   '#00d4ff',
  BruteForce: '#bd93f9',
  WebAttack:  '#ff6b35',
  Bot:        '#ff4db8',
  ATTACK:     '#f0a500',
}

export function attackColor(type) {
  return ATTACK_COLORS[type] ?? '#8b949e'
}

export function formatTs(ts) {
  if (!ts) return '—'
  return new Date(ts).toLocaleTimeString('en-US', { hour12: false })
}

export function formatDate(ts) {
  if (!ts) return '—'
  return new Date(ts).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}