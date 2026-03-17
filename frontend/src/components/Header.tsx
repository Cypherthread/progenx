import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useState, useEffect } from 'react'
import AuthModal from './AuthModal'

export default function Header() {
  const { user, logout } = useAuth()
  const [showAuth, setShowAuth] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <>
      <header className={`sticky top-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-[#0A0E18]/95 backdrop-blur-md border-b border-cyan-500/10 shadow-lg shadow-black/20'
          : 'bg-[#080C14] border-b border-gray-800/30'
      }`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-20 flex items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 shrink-0">
            <img src="/images/logo-progenx.png" alt="Progenx" className="h-12 sm:h-14" />
          </Link>

          {/* Desktop nav — centered */}
          <nav className="hidden md:flex items-center gap-1">
            {[
              { to: '/studio', label: 'Design Studio' },
              { to: '/history', label: 'My Designs' },
              { to: '/pricing', label: 'Pricing' },
            ].map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                className="px-4 py-2 text-sm text-gray-400 hover:text-white rounded-lg hover:bg-white/5 transition-all"
              >
                {label}
              </Link>
            ))}
          </nav>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="text-xs text-gray-500 hidden sm:inline tabular-nums">
                  {user.tier === 'free'
                    ? `${user.designs_this_month}/${user.monthly_limit}`
                    : 'Pro'}
                </span>
                <button
                  onClick={logout}
                  className="text-xs text-gray-500 hover:text-gray-300 transition-colors hidden md:inline"
                >
                  Log out
                </button>
              </>
            ) : (
              <button
                onClick={() => setShowAuth(true)}
                className="hidden md:inline px-4 py-2 text-sm font-medium text-white bg-cyan-600 hover:bg-cyan-500 rounded-lg transition-colors"
              >
                Sign in
              </button>
            )}

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2 rounded-lg hover:bg-white/5 text-gray-400"
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
          <div className="md:hidden border-t border-gray-800/50 bg-[#0A0E18]/98 backdrop-blur-xl px-4 py-3 space-y-0.5">
            {[
              { to: '/studio', label: 'Design Studio' },
              { to: '/history', label: 'My Designs' },
              { to: '/pricing', label: 'Pricing' },
            ].map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className="block py-2.5 px-3 text-sm text-gray-300 hover:text-white hover:bg-white/5 rounded-lg"
              >
                {label}
              </Link>
            ))}
            <div className="pt-2 border-t border-gray-800/50 mt-2">
              {user ? (
                <div className="flex items-center justify-between px-3 py-2">
                  <span className="text-sm text-gray-500">
                    {user.tier === 'free'
                      ? `${user.designs_this_month}/${user.monthly_limit} designs`
                      : 'Pro plan'}
                  </span>
                  <button onClick={() => { logout(); setMobileOpen(false) }} className="text-sm text-red-400">Log out</button>
                </div>
              ) : (
                <button
                  onClick={() => { setShowAuth(true); setMobileOpen(false) }}
                  className="w-full py-2.5 bg-cyan-600 text-white rounded-lg text-sm font-medium"
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
