import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import Header from '@/components/Header'
import Landing from '@/pages/Landing'
import Studio from '@/pages/Studio'
import History from '@/pages/History'
import Pricing from '@/pages/Pricing'

export default function App() {
  const loadUser = useAuth((s) => s.loadUser)

  useEffect(() => {
    loadUser()
  }, [loadUser])

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/studio" element={<Studio />} />
          <Route path="/history" element={<History />} />
          <Route path="/pricing" element={<Pricing />} />
        </Routes>
      </main>
      <footer className="border-t py-6 text-center text-sm text-muted-foreground">
        <p>ProtoForge v0.1 — Educational & Research Use Only</p>
        <p className="mt-1 text-xs max-w-2xl mx-auto px-4">
          Designs are computational predictions, not validated constructs. Any laboratory
          implementation must comply with institutional biosafety requirements and all applicable regulations.
        </p>
      </footer>
    </div>
  )
}
