import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import Header from '@/components/Header'
import ToastContainer from '@/components/Toast'
import CookieConsent from '@/components/CookieConsent'
import Landing from '@/pages/Landing'
import Studio from '@/pages/Studio'
import History from '@/pages/History'
import Explore from '@/pages/Explore'
import Pricing from '@/pages/Pricing'
import Account from '@/pages/Account'
import Terms from '@/pages/Terms'
import Privacy from '@/pages/Privacy'
import Analytics from '@/pages/Analytics'
import ResetPassword from '@/pages/ResetPassword'

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
          <Route path="/terms" element={<Terms />} />
          <Route path="/privacy" element={<Privacy />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/reset-password" element={<ResetPassword />} />
        </Routes>
      </main>
      <ToastContainer />
      <CookieConsent />
    </div>
  )
}
