import { useState, useEffect, useCallback, useRef } from 'react'

export function usePolling(fetchFn, intervalMs = 5000) {
  const [data,    setData]    = useState(null)
  const [error,   setError]   = useState(null)
  const [loading, setLoading] = useState(true)
  const timer = useRef(null)

  const run = useCallback(async () => {
    try {
      const result = await fetchFn()
      setData(result)
      setError(null)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, [fetchFn])

  useEffect(() => {
    run()
    timer.current = setInterval(run, intervalMs)
    return () => clearInterval(timer.current)
  }, [run, intervalMs])

  return { data, error, loading, refresh: run }
}