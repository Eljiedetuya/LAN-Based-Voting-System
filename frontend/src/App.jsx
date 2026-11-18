import { useEffect, useState } from 'react'

export default function App() {
  const [status, setStatus] = useState({ state: 'checking', message: 'Checking local API…' })
  useEffect(() => {
    const controller = new AbortController()
    fetch('/api/health/', { credentials: 'same-origin', signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) throw new Error(`API returned HTTP ${response.status}`)
        return response.json()
      })
      .then((data) => setStatus({ state: 'ready', message: `Django API: ${data.status}` }))
      .catch((error) => {
        if (error.name !== 'AbortError') setStatus({ state: 'error', message: `Cannot reach local API: ${error.message}` })
      })
    return () => controller.abort()
  }, [])
  return <main className="shell">
    <header className="brand"><span aria-hidden="true">▣</span> School Election Portal</header>
    <section className="panel" aria-labelledby="title">
      <p className="eyebrow">PHASE 7 · DEVELOPMENT ENVIRONMENT</p>
      <h1 id="title">Setup check</h1>
      <p>This is a starter scaffold, not an active election or voting interface.</p>
      <div className={`status ${status.state}`} role="status" aria-live="polite">{status.message}</div>
      <p className="footnote">Vote submission, authentication, and dashboards are intentionally not implemented yet.</p>
    </section>
  </main>
}
