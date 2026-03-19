import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useState, useEffect } from 'react'
import AuthModal from './AuthModal'

export default function Header() {
  const { user, logout } = useAuth()
  const location = useLocation()
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
          <Link to="/" className="flex items-center gap-2 shrink-0 transition-transform duration-200 hover:scale-105">
            <img src="/images/logo-progenx.png" alt="Progenx" className="h-10 sm:h-12 lg:h-14" />
          </Link>

          {/* Desktop nav — centered */}
          <nav className="hidden md:flex items-center gap-1">
            {[
              { to: '/studio', label: 'Design Studio' },
              { to: '/explore', label: 'Explore' },
              { to: '/history', label: 'My Designs' },
              { to: '/pricing', label: 'Pricing' },
              ...(user?.tier === 'admin' ? [{ to: '/analytics', label: 'Analytics' }] : []),
            ].map(({ to, label }) => {
              const isActive = location.pathname === to || (to !== '/' && location.pathname.startsWith(to))
              return (
                <Link
                  key={to}
                  to={to}
                  className={`relative px-4 py-2 text-sm rounded-lg hover:bg-white/5 transition-all ${
                    to === '/analytics'
                      ? isActive ? 'text-purple-300' : 'text-purple-400 hover:text-purple-300'
                      : isActive ? 'text-white' : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {label}
                  {isActive && (
                    <span className="absolute bottom-0.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400/50" />
                  )}
                </Link>
              )
            })}
          </nav>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="text-[10px] hidden sm:inline tabular-nums mr-1">
                  {user.tier === 'free' ? (
                    <span className="text-gray-600">{user.designs_this_month}/{user.monthly_limit}</span>
                  ) : (
                    <span className={user.tier === 'admin' ? 'text-purple-400 font-semibold' : 'text-amber-400 font-semibold'}>
                      {user.tier === 'admin' ? 'Admin' : 'Pro'}
                    </span>
                  )}
                </span>
                <Link
                  to="/account"
                  className="hidden md:flex items-center relative group/avatar"
                  title={user.tier === 'free' ? 'Account' : `${user.tier.charAt(0).toUpperCase() + user.tier.slice(1)} Account`}
                >
                  {/* Crown for pro/admin */}
                  {(user.tier === 'pro' || user.tier === 'admin') && (
                    <svg viewBox="0 0 24 14" className="absolute -top-2.5 left-1/2 -translate-x-1/2 w-5 h-3 z-10" fill="none">
                      <path d="M2 12L5 4L9 8L12 2L15 8L19 4L22 12H2Z" fill={user.tier === 'admin' ? '#A78BFA' : '#FBBF24'} stroke={user.tier === 'admin' ? '#7C3AED' : '#D97706'} strokeWidth="1" />
                    </svg>
                  )}
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-200 ${
                    user.tier === 'admin' ? 'bg-purple-500/20 border-2 border-purple-500/50 group-hover/avatar:ring-2 group-hover/avatar:ring-purple-400/30' :
                    user.tier === 'pro' ? 'bg-amber-500/20 border-2 border-amber-500/50 group-hover/avatar:ring-2 group-hover/avatar:ring-amber-400/30' :
                    'bg-gray-800 border border-gray-700 group-hover/avatar:ring-2 group-hover/avatar:ring-cyan-400/20'
                  }`}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className={`w-4 h-4 ${
                      user.tier === 'admin' ? 'text-purple-400' :
                      user.tier === 'pro' ? 'text-amber-400' :
                      'text-gray-500'
                    }`}>
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                  </div>
                </Link>
              </>
            ) : (
              <button
                onClick={() => setShowAuth(true)}
                className="hidden md:inline px-4 py-2 text-sm font-medium text-white bg-cyan-600 hover:bg-cyan-500 rounded-lg transition-colors shadow-sm shadow-cyan-500/20"
              >
                Sign in
              </button>
            )}

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2.5 rounded-lg hover:bg-white/5 text-gray-400"
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
        <div
          className={`md:hidden border-t border-gray-800/50 bg-[#0A0E18]/98 backdrop-blur-xl overflow-hidden transition-all duration-300 ease-in-out ${
            mobileOpen ? 'max-h-[400px] opacity-100' : 'max-h-0 opacity-0'
          }`}
        >
          <div className="px-4 py-3 space-y-1">
            {[
              { to: '/studio', label: 'Design Studio' },
              { to: '/explore', label: 'Explore' },
              { to: '/history', label: 'My Designs' },
              { to: '/pricing', label: 'Pricing' },
              ...(user?.tier === 'admin' ? [{ to: '/analytics', label: 'Analytics' }] : []),
            ].map(({ to, label }) => {
              const isActive = location.pathname === to || (to !== '/' && location.pathname.startsWith(to))
              return (
                <Link
                  key={to}
                  to={to}
                  onClick={() => setMobileOpen(false)}
                  className={`block py-3 px-3 text-sm hover:bg-white/5 rounded-lg transition-colors ${
                    to === '/analytics'
                      ? isActive ? 'text-purple-300 bg-purple-500/5' : 'text-purple-400 hover:text-purple-300'
                      : isActive ? 'text-white bg-white/5' : 'text-gray-300 hover:text-white'
                  }`}
                >
                  {label}
                </Link>
              )
            })}
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
        </div>
      </header>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
