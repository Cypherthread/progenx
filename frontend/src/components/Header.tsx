import { Link } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useState } from 'react'
import AuthModal from './AuthModal'

export default function Header() {
  const { user, logout } = useAuth()
  const [showAuth, setShowAuth] = useState(false)

  return (
    <>
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full dna-gradient flex items-center justify-center">
              <span className="text-white font-bold text-sm">P</span>
            </div>
            <span className="font-semibold text-lg">ProtoForge</span>
          </Link>

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
                  className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  Log out
                </button>
              </>
            ) : (
              <button
                onClick={() => setShowAuth(true)}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:opacity-90 transition-opacity"
              >
                Sign in
              </button>
            )}
          </div>
        </div>
      </header>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
