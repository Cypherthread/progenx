import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import Header from '@/components/Header'
import ToastContainer from '@/components/Toast'
import Landing from '@/pages/Landing'
import Studio from '@/pages/Studio'
import History from '@/pages/History'
import Explore from '@/pages/Explore'
import Pricing from '@/pages/Pricing'
import Account from '@/pages/Account'

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
          <Route path="/explore" element={<Explore />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/account" element={<Account />} />
        </Routes>
      </main>
      <ToastContainer />
    </div>
  )
}
