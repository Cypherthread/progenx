import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useAuth } from '@/hooks/useAuth'
import { billing, auth } from '@/lib/api'
import { toast } from '@/components/Toast'

export default function Account() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [deleting, setDeleting] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState('')

  if (!user) {
    navigate('/')
    return null
  }

  async function handleManageBilling() {
    try {
      const { portal_url } = await billing.portal()
      window.location.href = portal_url
    } catch {
      toast('Billing portal not available yet', 'info')
    }
  }

  async function handleDeleteAccount() {
    if (confirmDelete !== user!.email) return
    setDeleting(true)
    try {
      await auth.me() // verify auth is still valid
      // Call delete endpoint
      const token = localStorage.getItem('pf_token')
      const res = await fetch(
        `${import.meta.env.PROD ? 'https://progenx-api.onrender.com' : ''}/api/auth/account`,
        { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } }
      )
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
  const tierColor = user.tier === 'admin' ? 'text-purple-400 bg-purple-500/20' : user.tier === 'pro' ? 'text-cyan-400 bg-cyan-500/20' : 'text-gray-400 bg-gray-800'

  return (
    <>
      <Helmet>
        <title>Account Settings | Progenx</title>
        <meta name="robots" content="noindex" />
      </Helmet>

      <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
        <h1 className="text-2xl font-bold text-white">Account Settings</h1>

        {/* Profile */}
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-white mb-4">Profile</h2>
          <div className="space-y-3">
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
            <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-cyan-500 rounded-full transition-all"
                style={{ width: `${Math.min(100, (user.designs_this_month / user.monthly_limit) * 100)}%` }}
              />
            </div>
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

              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={handleManageBilling}
                  className="px-4 py-2.5 border border-gray-700 text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-800"
                >
                  Update Payment Method
                </button>
                <button
                  onClick={handleManageBilling}
                  className="px-4 py-2.5 border border-gray-700 text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-800"
                >
                  View Invoices
                </button>
              </div>

              <div className="pt-3 border-t border-gray-800">
                <button
                  onClick={async () => {
                    if (confirm('Are you sure you want to cancel your Pro plan? You will keep access until the end of your current billing period.')) {
                      handleManageBilling()
                    }
                  }}
                  className="text-sm text-red-400 hover:text-red-300 transition-colors"
                >
                  Cancel Plan
                </button>
                <p className="text-[10px] text-gray-600 mt-1">
                  You'll keep Pro access until the end of your current billing period. After that, your account reverts to the free tier.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* API Keys (Pro only) */}
        {(user.tier === 'pro' || user.tier === 'admin') && (
          <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">
            <h2 className="text-sm font-semibold text-white mb-2">API Access</h2>
            <p className="text-xs text-gray-500 mb-3">
              Generate API keys to access Progenx programmatically. Keys use the same endpoints as the web app.
            </p>
            <button
              onClick={async () => {
                try {
                  const token = localStorage.getItem('pf_token')
                  const res = await fetch(
                    `${import.meta.env.PROD ? 'https://progenx-api.onrender.com' : ''}/api/auth/api-key`,
                    { method: 'POST', headers: { Authorization: `Bearer ${token}` } }
                  )
                  const data = await res.json()
                  if (data.api_key) {
                    await navigator.clipboard.writeText(data.api_key)
                    toast('API key created and copied to clipboard. Save it now.')
                  } else {
                    toast(data.detail || 'Could not create API key', 'error')
                  }
                } catch {
                  toast('Could not create API key', 'error')
                }
              }}
              className="px-4 py-2 border border-gray-700 text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-800"
            >
              Generate New API Key
            </button>
          </div>
        )}

        {/* Danger zone */}
        <div className="bg-red-500/5 border border-red-500/20 rounded-xl p-5">
          <h2 className="text-sm font-semibold text-red-400 mb-2">Danger Zone</h2>
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
            />
            <button
              onClick={handleDeleteAccount}
              disabled={confirmDelete !== user.email || deleting}
              className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-500 disabled:opacity-30 disabled:cursor-not-allowed"
            >
              {deleting ? 'Deleting...' : 'Delete My Account'}
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
