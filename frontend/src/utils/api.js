const BASE = '/api'

async function request(path, options = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export const api = {
  health:      ()        => request('/health'),
  stats:       ()        => request('/stats'),
  alerts:      (p = {})  => request('/alerts?' + new URLSearchParams(p)),
  detect:      (body)    => request('/detect', { method: 'POST', body: JSON.stringify(body) }),
  acknowledge: (id)      => request(`/alerts/${id}/acknowledge`, { method: 'PATCH' }),
  modelReport: ()        => request('/model-report'),
}