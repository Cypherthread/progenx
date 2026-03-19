import { useState, useEffect, useCallback } from 'react'

// ---------------------------------------------------------------------------
// Consent storage key & shape
// ---------------------------------------------------------------------------

const CONSENT_KEY = 'pgx_consent'

export interface ConsentState {
  analytics: boolean
  timestamp: string
}

// ---------------------------------------------------------------------------
// Read / write consent
// ---------------------------------------------------------------------------

export function getConsent(): ConsentState | null {
  try {
    const raw = localStorage.getItem(CONSENT_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (typeof parsed.analytics !== 'boolean' || typeof parsed.timestamp !== 'string') return null
    return parsed as ConsentState
  } catch {
    return null
  }
}

function setConsent(analytics: boolean) {
  const state: ConsentState = { analytics, timestamp: new Date().toISOString() }
  localStorage.setItem(CONSENT_KEY, JSON.stringify(state))
}

// ---------------------------------------------------------------------------
// Global event bus so external code can reopen the banner
// ---------------------------------------------------------------------------

type Listener = () => void
const listeners: Set<Listener> = new Set()

/** Call this from anywhere (e.g. footer "Cookie Settings" link) to reopen the banner. */
export function openCookieSettings() {
  listeners.forEach((fn) => fn())
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CookieConsent() {
  const [visible, setVisible] = useState(() => getConsent() === null)

  // Subscribe to external "reopen" requests
  useEffect(() => {
    const handler = () => setVisible(true)
    listeners.add(handler)
    return () => { listeners.delete(handler) }
  }, [])

  const accept = useCallback(() => {
    setConsent(true)
    setVisible(false)
  }, [])

  const reject = useCallback(() => {
    setConsent(false)
    setVisible(false)
  }, [])

  if (!visible) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[90] px-4 pb-4 pointer-events-none">
      <div className="max-w-lg mx-auto bg-[#0F1629] border border-gray-800 rounded-xl shadow-2xl p-5 pointer-events-auto">
        <p className="text-sm text-gray-300 mb-1">
          We use first-party analytics (page views, scroll depth, performance metrics) to
          improve your experience. No data is shared with third parties.
        </p>
        <a href="/privacy" className="text-xs text-cyan-500 hover:text-cyan-400 inline-block mb-4">
          Privacy Policy
        </a>

        <div className="flex items-center gap-3">
          <button
            onClick={reject}
            className="flex-1 px-4 py-2.5 border border-gray-600 text-gray-300 rounded-lg text-sm font-medium hover:bg-white/5 transition-colors"
          >
            Reject
          </button>
          <button
            onClick={accept}
            className="flex-1 px-4 py-2.5 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500 transition-colors"
          >
            Accept
          </button>
        </div>
      </div>
    </div>
  )
}
