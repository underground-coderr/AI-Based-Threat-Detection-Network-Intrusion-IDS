import { useState, useEffect, useCallback } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar.jsx'
import Overview from './pages/Overview.jsx'
import Alerts from './pages/Alerts.jsx'
import Detect from './pages/Detect.jsx'
import Models from './pages/Models.jsx'
import { api } from './utils/api.js'

export default function App() {
  const [engineReady, setEngineReady] = useState(false)

  const checkHealth = useCallback(async () => {
    try {
      const data = await api.health()
      setEngineReady(data.status === 'ok')
    } catch {
      setEngineReady(false)
    }
  }, [])

  useEffect(() => {
    checkHealth()
    const t = setInterval(checkHealth, 15000)
    return () => clearInterval(t)
  }, [checkHealth])

  return (
    <BrowserRouter>
      <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
        <Sidebar engineReady={engineReady} />
        <main style={{ flex: 1, overflowY: 'auto', background: 'var(--bg-base)' }}>
          <Routes>
            <Route path="/"        element={<Overview />} />
            <Route path="/alerts"  element={<Alerts />} />
            <Route path="/detect"  element={<Detect />} />
            <Route path="/models"  element={<Models />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}