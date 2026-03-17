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
    </div>
  )
}
