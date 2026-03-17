import { Link } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useState } from 'react'
import AuthModal from './AuthModal'

export default function Header() {
  const { user, logout } = useAuth()
  const [showAuth, setShowAuth] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  return (
    <>
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <img src="/images/logo-progenx.png" alt="Progenx" className="h-8" />
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-6 text-sm">
            <Link to="/studio" className="hover:text-primary transition-colors">Design Studio</Link>
            <Link to="/history" className="hover:text-primary transition-colors">My Designs</Link>
            <Link to="/pricing" className="hover:text-primary transition-colors">Pricing</Link>
          </nav>

          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="text-sm text-muted-foreground hidden sm:inline">
                  {user.tier === 'free'
                    ? `${user.designs_this_month}/${user.monthly_limit} designs`
                    : 'Pro'}
                </span>
                <button
                  onClick={logout}
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors hidden md:inline"
                >
                  Log out
                </button>
              </>
            ) : (
              <button
                onClick={() => setShowAuth(true)}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:opacity-90 transition-opacity hidden md:inline"
              >
                Sign in
              </button>
            )}

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2 rounded-md hover:bg-gray-100"
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
          <div className="md:hidden border-t bg-white px-4 py-3 space-y-1">
            <Link
              to="/studio"
              onClick={() => setMobileOpen(false)}
              className="block py-2 text-sm hover:text-primary"
            >
              Design Studio
            </Link>
            <Link
              to="/history"
              onClick={() => setMobileOpen(false)}
              className="block py-2 text-sm hover:text-primary"
            >
              My Designs
            </Link>
            <Link
              to="/pricing"
              onClick={() => setMobileOpen(false)}
              className="block py-2 text-sm hover:text-primary"
            >
              Pricing
            </Link>
            <div className="pt-2 border-t mt-2">
              {user ? (
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">
                    {user.tier === 'free'
                      ? `${user.designs_this_month}/${user.monthly_limit} designs this month`
                      : 'Pro plan'}
                  </span>
                  <button
                    onClick={() => { logout(); setMobileOpen(false) }}
                    className="text-sm text-red-600"
                  >
                    Log out
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => { setShowAuth(true); setMobileOpen(false) }}
                  className="w-full py-2 bg-primary text-white rounded-md text-sm font-medium"
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
