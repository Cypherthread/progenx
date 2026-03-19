import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useAuth } from '@/hooks/useAuth'
import { billing } from '@/lib/api'
import { toast } from '@/components/Toast'
import { useAnalytics } from '@/hooks/useAnalytics'

const API_BASE = import.meta.env.PROD ? 'https://api.progenx.ai' : ''

const SAFE_REDIRECT_HOSTS = ['checkout.stripe.com', 'billing.stripe.com']
function isSafeRedirect(url: string): boolean {
  try {
    const parsed = new URL(url)
    return SAFE_REDIRECT_HOSTS.some(h => parsed.hostname === h || parsed.hostname.endsWith(`.${h}`))
  } catch {
    return false
  }
}

export default function Account() {
  useAnalytics('account')
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [deleting, setDeleting] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState('')
  const [apiKeys, setApiKeys] = useState<{ id: string; name: string; created_at: string; last_used: string | null }[]>([])
  const [generatingKey, setGeneratingKey] = useState(false)

  useEffect(() => {
    if (user && (user.tier === 'pro' || user.tier === 'admin')) {
      loadApiKeys()
    }
  }, [user])

  async function loadApiKeys() {
    try {
      const token = localStorage.getItem('pf_token')
      const res = await fetch(`${API_BASE}/api/auth/api-keys`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        setApiKeys(data)
      }
    } catch {}
  }

  if (!user) {
    navigate('/')
    return null
  }

  async function handleManageBilling() {
    try {
      const { portal_url } = await billing.portal()
      if (isSafeRedirect(portal_url)) {
        window.location.href = portal_url
      } else {
        toast('Invalid billing URL', 'error')
      }
    } catch {
      toast('Billing portal not available yet', 'info')
    }
  }

  async function handleGenerateKey() {
    setGeneratingKey(true)
    try {
      const token = localStorage.getItem('pf_token')
      const res = await fetch(`${API_BASE}/api/auth/api-key`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      const data = await res.json()
      if (data.api_key) {
        await navigator.clipboard.writeText(data.api_key)
        toast('API key created and copied to clipboard. Save it now, it won\'t be shown again.')
        loadApiKeys()
      } else {
        toast(data.detail || 'Could not create API key', 'error')
      }
    } catch {
      toast('Could not create API key', 'error')
    } finally {
      setGeneratingKey(false)
    }
  }

  async function handleRevokeKey(keyId: string) {
    if (!confirm('Revoke this API key? Any applications using it will stop working.')) return
    try {
      const token = localStorage.getItem('pf_token')
      const res = await fetch(`${API_BASE}/api/auth/api-key/${keyId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        toast('API key revoked')
        setApiKeys(prev => prev.filter(k => k.id !== keyId))
      } else {
        toast('Could not revoke key', 'error')
      }
    } catch {
      toast('Could not revoke key', 'error')
    }
  }

  async function handleDeleteAccount() {
    if (confirmDelete !== user!.email) return
    setDeleting(true)
    try {
      const token = localStorage.getItem('pf_token')
      const res = await fetch(`${API_BASE}/api/auth/account`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        toast('Account deleted. All your data has been removed.', 'info')
        logout()
        navigate('/')
      } else {
        toast('Could not delete account. Try again.', 'error')
      }
    } catch {
      toast('Could not delete account', 'error')
    } finally {
      setDeleting(false)
    }
  }

  const tierLabel = user.tier === 'admin' ? 'Admin' : user.tier === 'pro' ? 'Pro' : 'Free'
  const tierColor = user.tier === 'admin'
    ? 'text-purple-400 bg-purple-500/20'
    : user.tier === 'pro'
      ? 'text-cyan-400 bg-cyan-500/20'
      : 'text-gray-400 bg-gray-800'

  return (
    <>
      <Helmet>
        <title>Account Settings | Progenx</title>
        <meta name="robots" content="noindex" />
      </Helmet>

      <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
        <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
          <span className="gradient-underline">Account Settings</span>
        </h1>

        {/* Profile */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-5">Profile</h2>

          {/* Large avatar circle */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 mb-6">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border-2 border-cyan-500/30 flex items-center justify-center">
              <span className="text-2xl font-bold text-cyan-400 uppercase">
                {(user.name || user.email || '?')[0]}
              </span>
            </div>
            <div>
              <p className="text-lg font-semibold text-white">{user.name || 'Not set'}</p>
              <p className="text-sm text-gray-500">{user.email}</p>
            </div>
            <span className={`sm:ml-auto text-xs px-2.5 py-1 rounded-full font-semibold ${tierColor}`}>
              {tierLabel}
            </span>
          </div>

          <div className="space-y-3 border-t border-gray-800 pt-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Name</span>
              <span className="text-sm text-white font-medium">{user.name || 'Not set'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Email</span>
              <span className="text-sm text-white font-medium">{user.email}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Plan</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${tierColor}`}>
                {tierLabel}
              </span>
            </div>
          </div>
        </div>

        {/* Usage */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">Usage This Month</h2>
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-gray-400">Designs generated</span>
            <span className="text-sm text-white font-bold">
              {user.designs_this_month}
              {user.tier === 'free' && <span className="text-gray-500 font-normal"> / {user.monthly_limit}</span>}
              {user.tier !== 'free' && <span className="text-gray-500 font-normal"> (unlimited)</span>}
            </span>
          </div>
          {user.tier === 'free' && (
            <>
              <div className="w-full h-3 bg-gray-800 rounded-full overflow-hidden mb-2">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    user.designs_this_month >= user.monthly_limit
                      ? 'bg-gradient-to-r from-red-500 to-red-400'
                      : 'bg-gradient-to-r from-cyan-500 to-blue-500'
                  }`}
                  style={{ width: `${Math.min(100, (user.designs_this_month / user.monthly_limit) * 100)}%` }}
                />
              </div>
              {user.designs_this_month >= user.monthly_limit && (
                <p className="text-xs text-amber-400">
                  Limit reached. Resets at the start of next month, or upgrade to Pro for unlimited.
                </p>
              )}
            </>
          )}
        </div>

        {/* Plan */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">Plan & Billing</h2>
          {user.tier === 'free' ? (
            <div>
              <p className="text-sm text-gray-400 mb-3">
                You're on the Free plan with {user.monthly_limit} designs per month.
                Upgrade to Pro for unlimited designs and Claude AI.
              </p>
              <button
                onClick={() => navigate('/pricing')}
                className="px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500"
              >
                Upgrade to Pro for $29/month
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center gap-3 p-3 bg-gray-800/30 border border-gray-700 rounded-lg">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  user.tier === 'admin' ? 'bg-purple-500/20' : 'bg-amber-500/20'
                }`}>
                  <svg viewBox="0 0 24 14" className="w-5 h-3" fill="none">
                    <path d="M2 12L5 4L9 8L12 2L15 8L19 4L22 12H2Z" fill={user.tier === 'admin' ? '#A78BFA' : '#FBBF24'} />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">{tierLabel} Plan</p>
                  <p className="text-xs text-gray-500">Unlimited designs, Claude AI, full validation</p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <button
                  onClick={handleManageBilling}
                  className="px-4 py-2.5 border border-gray-700 text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
                >
                  Update Payment
                </button>
                <button
                  onClick={handleManageBilling}
                  className="px-4 py-2.5 border border-gray-700 text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors"
                >
                  View Invoices
                </button>
              </div>

              <div className="pt-3 border-t border-gray-800">
                <button
                  onClick={() => {
                    if (confirm('Are you sure you want to cancel your Pro plan? You will keep access until the end of your current billing period.')) {
                      handleManageBilling()
                    }
                  }}
                  className="text-sm text-red-400 hover:text-red-300 transition-colors"
                >
                  Cancel Plan
                </button>
                <p className="text-[10px] text-gray-600 mt-1">
                  You'll keep Pro access until the end of your current billing period.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* API Keys (Pro only) */}
        {(user.tier === 'pro' || user.tier === 'admin') && (
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="text-sm font-semibold text-white">API Access</h2>
                <p className="text-xs text-gray-500 mt-0.5">
                  Programmatic access to the same endpoints as the web app.
                </p>
              </div>
              <button
                onClick={handleGenerateKey}
                disabled={generatingKey}
                className="px-3 py-1.5 bg-cyan-600 text-white rounded-lg text-xs font-medium hover:bg-cyan-500 disabled:opacity-50 shrink-0"
              >
                {generatingKey ? 'Creating...' : 'New Key'}
              </button>
            </div>

            {apiKeys.length > 0 ? (
              <div className="border border-gray-700/50 rounded-lg overflow-hidden">
                {/* Table header */}
                <div className="grid grid-cols-[1fr_auto_auto] sm:grid-cols-[1fr_auto_auto_auto] gap-4 px-4 py-2.5 bg-gray-800/40 border-b border-gray-700/50 text-[10px] font-semibold text-gray-500 uppercase tracking-wider">
                  <span>Key Name</span>
                  <span>Created</span>
                  <span className="hidden sm:block">Last Used</span>
                  <span></span>
                </div>
                {apiKeys.map((key, idx) => (
                  <div key={key.id} className={`grid grid-cols-[1fr_auto_auto] sm:grid-cols-[1fr_auto_auto_auto] gap-4 items-center px-4 py-3 ${idx < apiKeys.length - 1 ? 'border-b border-gray-800/50' : ''} hover:bg-gray-800/20 transition-colors`}>
                    <span className="text-xs font-medium text-white truncate">{key.name}</span>
                    <span className="text-[10px] text-gray-500 whitespace-nowrap">
                      {new Date(key.created_at).toLocaleDateString()}
                    </span>
                    <span className="hidden sm:block text-[10px] text-gray-500 whitespace-nowrap">
                      {key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Never'}
                    </span>
                    <button
                      onClick={() => handleRevokeKey(key.id)}
                      className="text-[10px] text-red-400 hover:text-red-300 px-2 py-1 rounded hover:bg-red-500/10 transition-colors whitespace-nowrap"
                    >
                      Revoke
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gray-600">No API keys yet. Keys are prefixed with pgx_ and shown once on creation.</p>
            )}
          </div>
        )}

        {/* Danger zone */}
        <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-5 danger-stripes">
          <div className="flex items-center gap-2 mb-2">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 text-red-400">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
              <path d="M12 9v4M12 17h.01" strokeLinecap="round" />
            </svg>
            <h2 className="text-sm font-semibold text-red-400">Danger Zone</h2>
          </div>
          <p className="text-xs text-gray-500 mb-3">
            Permanently delete your account and all designs. This cannot be undone.
          </p>
          <div className="space-y-2">
            <input
              type="text"
              value={confirmDelete}
              onChange={(e) => setConfirmDelete(e.target.value)}
              placeholder={`Type "${user.email}" to confirm`}
              className="w-full px-3 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-600 focus:outline-none focus:border-red-500/50"
              autoComplete="off"
            />
            <button
              onClick={handleDeleteAccount}
              disabled={confirmDelete !== user.email || deleting}
              className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-500 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              {deleting ? (
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-20" />
                    <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                  </svg>
                  Deleting...
                </span>
              ) : 'Delete My Account'}
            </button>
          </div>
        </div>

        {/* Logout */}
        <button
          onClick={() => { logout(); navigate('/') }}
          className="w-full py-3 border border-gray-800 text-gray-400 rounded-xl text-sm font-medium hover:bg-gray-900/50 hover:text-white transition-colors"
        >
          Log Out
        </button>
      </div>
    </>
  )
}
