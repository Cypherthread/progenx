import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useState } from 'react'
import AuthModal from './AuthModal'

export default function Header() {
  const { user, logout } = useAuth()
  const [showAuth, setShowAuth] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  const isLanding = location.pathname === '/'

  // Dark frosted glass on landing, dark frosted on other pages too
  const headerBg = isLanding
    ? 'bg-[#080C14]/70 backdrop-blur-xl border-gray-800/50'
    : 'bg-[#0B1120]/80 backdrop-blur-xl border-gray-800/50'

  return (
    <>
      <header className={`border-b sticky top-0 z-50 ${headerBg}`}>
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <img src="/images/logo-progenx.png" alt="Progenx" className="h-7" />
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-6 text-sm">
            <Link to="/studio" className="text-gray-400 hover:text-cyan-400 transition-colors">Design Studio</Link>
            <Link to="/history" className="text-gray-400 hover:text-cyan-400 transition-colors">My Designs</Link>
            <Link to="/pricing" className="text-gray-400 hover:text-cyan-400 transition-colors">Pricing</Link>
          </nav>

          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="text-sm text-gray-500 hidden sm:inline">
                  {user.tier === 'free'
                    ? `${user.designs_this_month}/${user.monthly_limit} designs`
                    : 'Pro'}
                </span>
                <button
                  onClick={logout}
                  className="text-sm text-gray-500 hover:text-gray-300 transition-colors hidden md:inline"
                >
                  Log out
                </button>
              </>
            ) : (
              <button
                onClick={() => setShowAuth(true)}
                className="px-4 py-2 progenx-gradient text-white rounded-lg text-sm font-medium hover:opacity-90 transition-opacity hidden md:inline"
              >
                Sign in
              </button>
            )}

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2 rounded-md hover:bg-white/5 text-gray-400"
              aria-label="Menu"
            >
              {mobileOpen ? (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                  <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-5 h-5">
                  <path d="M4 6h16M4 12h16M4 18h16" strokeLinecap="round" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden border-t border-gray-800 bg-[#0B1120]/95 backdrop-blur-xl px-4 py-3 space-y-1">
            <Link to="/studio" onClick={() => setMobileOpen(false)} className="block py-2.5 text-sm text-gray-300 hover:text-cyan-400">Design Studio</Link>
            <Link to="/history" onClick={() => setMobileOpen(false)} className="block py-2.5 text-sm text-gray-300 hover:text-cyan-400">My Designs</Link>
            <Link to="/pricing" onClick={() => setMobileOpen(false)} className="block py-2.5 text-sm text-gray-300 hover:text-cyan-400">Pricing</Link>
            <div className="pt-2 border-t border-gray-800 mt-2">
              {user ? (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">
                    {user.tier === 'free'
                      ? `${user.designs_this_month}/${user.monthly_limit} designs this month`
                      : 'Pro plan'}
                  </span>
                  <button onClick={() => { logout(); setMobileOpen(false) }} className="text-sm text-red-400">Log out</button>
                </div>
              ) : (
                <button
                  onClick={() => { setShowAuth(true); setMobileOpen(false) }}
                  className="w-full py-2.5 progenx-gradient text-white rounded-lg text-sm font-medium"
                >
                  Sign in
                </button>
              )}
            </div>
          </div>
        )}
      </header>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
