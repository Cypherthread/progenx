import { useEffect, useRef } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { getConsent } from '@/components/CookieConsent'
import type { ConsentState } from '@/components/CookieConsent'

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const API_BASE = import.meta.env.PROD
  ? 'https://progenx-api.onrender.com/api'
  : '/api'

const FLUSH_INTERVAL_MS = 10_000
const MAX_BUFFER = 200
const PREFS_KEY = 'pgx_prefs'
const CONSENT_KEY = 'pgx_consent'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type AnalyticsEventType =
  | 'page_view'
  | 'click'
  | 'scroll_depth'
  | 'funnel_step'
  | 'time_on_page'
  | 'section_view'
  | 'feature_use'
  | 'rage_click'
  | 'error'
  | 'web_vital'
  | 'referral'

export interface AnalyticsEvent {
  event_type: AnalyticsEventType | string
  session_id: string
  user_id: string | null
  timestamp: string
  page?: string
  element?: string
  value?: string
  metadata?: Record<string, any>
}

// ---------------------------------------------------------------------------
// Consent helpers (exported for external use)
// ---------------------------------------------------------------------------

/** Returns true only if the user has explicitly accepted analytics. */
export function hasAnalyticsConsent(): boolean {
  const consent = getConsent()
  return consent !== null && consent.analytics === true
}

/** Revoke analytics consent — sets analytics to false and clears session. */
export function revokeAnalyticsConsent(): void {
  const state: ConsentState = { analytics: false, timestamp: new Date().toISOString() }
  localStorage.setItem(CONSENT_KEY, JSON.stringify(state))
}

// Event types that are allowed without consent (essential / error tracking)
const CONSENT_EXEMPT_TYPES = new Set<string>(['error'])

// ---------------------------------------------------------------------------
// Session ID (persists in sessionStorage — survives navigation, not new tabs)
// ---------------------------------------------------------------------------

const SESSION_KEY = 'pgx_session_id'

function generateId(): string {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`
}

function getSessionId(): string {
  let id = sessionStorage.getItem(SESSION_KEY)
  if (!id) {
    id = generateId()
    sessionStorage.setItem(SESSION_KEY, id)
  }
  return id
}

// ---------------------------------------------------------------------------
// User ID helper — reads Zustand store outside React tree
// ---------------------------------------------------------------------------

function getUserId(): string | null {
  try {
    return useAuth.getState().user?.id ?? null
  } catch {
    return null
  }
}

// ---------------------------------------------------------------------------
// Event buffer + flush
// ---------------------------------------------------------------------------

let buffer: AnalyticsEvent[] = []
let flushTimer: ReturnType<typeof setInterval> | null = null

function flush() {
  if (buffer.length === 0) return

  const payload = [...buffer]
  buffer = []

  const body = JSON.stringify({ events: payload })
  const token = localStorage.getItem('pf_token')
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (token) headers['Authorization'] = `Bearer ${token}`

  if (typeof navigator.sendBeacon === 'function') {
    const blob = new Blob([body], { type: 'application/json' })
    const sent = navigator.sendBeacon(`${API_BASE}/analytics/events`, blob)
    if (sent) return
  }

  fetch(`${API_BASE}/analytics/events`, {
    method: 'POST',
    headers,
    body,
    keepalive: true,
  }).catch(() => {})
}

let initialized = false

function ensureFlushTimer() {
  if (flushTimer) return
  flushTimer = setInterval(flush, FLUSH_INTERVAL_MS)

  if (typeof window !== 'undefined') {
    window.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') flush()
    })
    window.addEventListener('pagehide', flush)
  }

  // One-time global initializations
  if (!initialized) {
    initialized = true
    captureReferral()
    captureUtmParams()
    setupRageClickDetection()
    setupErrorTracking()
    setupWebVitals()
  }
}

// ---------------------------------------------------------------------------
// Standalone track function
// ---------------------------------------------------------------------------

export function track(
  eventType: AnalyticsEventType | string,
  props?: {
    page?: string
    element?: string
    value?: string
    metadata?: Record<string, any>
  },
) {
  // Gate behind consent — exempt types (error tracking) always pass through
  if (!CONSENT_EXEMPT_TYPES.has(eventType) && !hasAnalyticsConsent()) {
    return
  }

  ensureFlushTimer()

  buffer.push({
    event_type: eventType,
    session_id: getSessionId(),
    user_id: getUserId(),
    timestamp: new Date().toISOString(),
    page: props?.page,
    element: props?.element,
    value: props?.value,
    metadata: props?.metadata,
  })

  if (buffer.length >= MAX_BUFFER) flush()
}

// ---------------------------------------------------------------------------
// UTM & Referrer Capture (runs once per session)
// ---------------------------------------------------------------------------

function captureUtmParams() {
  const params = new URLSearchParams(window.location.search)
  const utm: Record<string, string> = {}
  for (const key of ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content']) {
    const val = params.get(key)
    if (val) utm[key] = val
  }
  if (Object.keys(utm).length > 0) {
    track('referral', {
      element: 'utm',
      value: utm.utm_source || 'unknown',
      metadata: utm,
    })
    // Store for attribution
    sessionStorage.setItem('pgx_utm', JSON.stringify(utm))
  }
}

function captureReferral() {
  const referrer = document.referrer
  if (!referrer || referrer.includes(window.location.hostname)) return
  try {
    const url = new URL(referrer)
    track('referral', {
      element: 'referrer',
      value: url.hostname,
      metadata: { full_referrer: referrer },
    })
  } catch {}
}

// ---------------------------------------------------------------------------
// Rage Click Detection
// Fires when a user clicks the same spot 3+ times within 1 second
// ---------------------------------------------------------------------------

function setupRageClickDetection() {
  let clicks: { x: number; y: number; t: number }[] = []
  const THRESHOLD = 3
  const WINDOW_MS = 1000
  const RADIUS = 30

  document.addEventListener('click', (e) => {
    const now = Date.now()
    clicks.push({ x: e.clientX, y: e.clientY, t: now })

    // Purge old clicks
    clicks = clicks.filter(c => now - c.t < WINDOW_MS)

    // Check for cluster
    const nearby = clicks.filter(c =>
      Math.abs(c.x - e.clientX) < RADIUS && Math.abs(c.y - e.clientY) < RADIUS
    )

    if (nearby.length >= THRESHOLD) {
      const target = e.target as HTMLElement
      const element = target.tagName.toLowerCase() +
        (target.className ? `.${String(target.className).split(' ')[0]}` : '') +
        (target.textContent ? ` "${target.textContent.slice(0, 30)}"` : '')
      track('rage_click', {
        page: window.location.pathname,
        element,
        value: String(nearby.length),
        metadata: {
          x: e.clientX,
          y: e.clientY,
          tag: target.tagName,
          text: target.textContent?.slice(0, 50),
        },
      })
      clicks = [] // Reset after detecting
    }
  }, { passive: true })
}

// ---------------------------------------------------------------------------
// Error Tracking (JS errors + unhandled promise rejections)
// ---------------------------------------------------------------------------

function setupErrorTracking() {
  window.addEventListener('error', (e) => {
    track('error', {
      page: window.location.pathname,
      element: 'js_error',
      value: e.message?.slice(0, 200),
      metadata: {
        filename: e.filename,
        lineno: e.lineno,
        colno: e.colno,
      },
    })
  })

  window.addEventListener('unhandledrejection', (e) => {
    const reason = e.reason instanceof Error ? e.reason.message : String(e.reason)
    track('error', {
      page: window.location.pathname,
      element: 'promise_rejection',
      value: reason.slice(0, 200),
    })
  })
}

// ---------------------------------------------------------------------------
// Core Web Vitals (LCP, FID, CLS) — no external lib needed
// ---------------------------------------------------------------------------

function setupWebVitals() {
  // Largest Contentful Paint
  if ('PerformanceObserver' in window) {
    try {
      const lcpObs = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const last = entries[entries.length - 1] as any
        if (last) {
          track('web_vital', {
            element: 'LCP',
            value: String(Math.round(last.startTime)),
            metadata: { ms: Math.round(last.startTime) },
          })
        }
        lcpObs.disconnect()
      })
      lcpObs.observe({ type: 'largest-contentful-paint', buffered: true })
    } catch {}

    // First Input Delay
    try {
      const fidObs = new PerformanceObserver((list) => {
        const entry = list.getEntries()[0] as any
        if (entry) {
          track('web_vital', {
            element: 'FID',
            value: String(Math.round(entry.processingStart - entry.startTime)),
            metadata: { ms: Math.round(entry.processingStart - entry.startTime) },
          })
        }
        fidObs.disconnect()
      })
      fidObs.observe({ type: 'first-input', buffered: true })
    } catch {}

    // Cumulative Layout Shift
    try {
      let clsValue = 0
      const clsObs = new PerformanceObserver((list) => {
        for (const entry of list.getEntries() as any[]) {
          if (!entry.hadRecentInput) {
            clsValue += entry.value
          }
        }
      })
      clsObs.observe({ type: 'layout-shift', buffered: true })

      // Report CLS when page becomes hidden
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'hidden' && clsValue > 0) {
          track('web_vital', {
            element: 'CLS',
            value: clsValue.toFixed(4),
            metadata: { score: clsValue },
          })
          clsObs.disconnect()
        }
      }, { once: true })
    } catch {}
  }
}

// ---------------------------------------------------------------------------
// User Preferences (persisted in localStorage, no auth needed)
// ---------------------------------------------------------------------------

export interface UserPrefs {
  lastEnvironment?: string
  lastSafetyLevel?: number
  lastComplexity?: number
  dismissedBanners?: string[]
  recentDesignIds?: string[]
  theme?: string
}

export function getPrefs(): UserPrefs {
  try {
    const raw = localStorage.getItem(PREFS_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

export function setPrefs(updates: Partial<UserPrefs>) {
  const current = getPrefs()
  localStorage.setItem(PREFS_KEY, JSON.stringify({ ...current, ...updates }))
}

export function addRecentDesign(designId: string) {
  const prefs = getPrefs()
  const recent = prefs.recentDesignIds || []
  const updated = [designId, ...recent.filter(id => id !== designId)].slice(0, 20)
  setPrefs({ recentDesignIds: updated })
}

export function dismissBanner(bannerId: string) {
  const prefs = getPrefs()
  const dismissed = prefs.dismissedBanners || []
  if (!dismissed.includes(bannerId)) {
    setPrefs({ dismissedBanners: [...dismissed, bannerId] })
  }
}

export function isBannerDismissed(bannerId: string): boolean {
  const prefs = getPrefs()
  return (prefs.dismissedBanners || []).includes(bannerId)
}

// ---------------------------------------------------------------------------
// React Hook — auto page view, time-on-page, scroll depth sentinels
// ---------------------------------------------------------------------------

export function useAnalytics(pageName: string) {
  const mountTime = useRef(Date.now())

  useEffect(() => {
    mountTime.current = Date.now()
    track('page_view', { page: pageName })

    return () => {
      const seconds = Math.round((Date.now() - mountTime.current) / 1000)
      track('time_on_page', {
        page: pageName,
        value: String(seconds),
        metadata: { duration_seconds: seconds },
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pageName])

  // Scroll depth tracking
  useEffect(() => {
    const thresholds = [25, 50, 75, 100]
    const tracked = new Set<number>()
    const sentinels: HTMLDivElement[] = []

    const raf = requestAnimationFrame(() => {
      const scrollContainer = document.documentElement

      thresholds.forEach((pct) => {
        const sentinel = document.createElement('div')
        sentinel.style.position = 'absolute'
        sentinel.style.left = '0'
        sentinel.style.width = '1px'
        sentinel.style.height = '1px'
        sentinel.style.pointerEvents = 'none'
        sentinel.style.opacity = '0'
        sentinel.setAttribute('data-scroll-sentinel', String(pct))

        const docHeight = Math.max(
          scrollContainer.scrollHeight,
          document.body.scrollHeight,
        )
        sentinel.style.top = `${(docHeight * pct) / 100}px`

        document.body.appendChild(sentinel)
        sentinels.push(sentinel)
      })

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return
            const pct = Number(
              (entry.target as HTMLElement).getAttribute('data-scroll-sentinel'),
            )
            if (pct && !tracked.has(pct)) {
              tracked.add(pct)
              track('scroll_depth', {
                page: pageName,
                value: `${pct}%`,
                metadata: { depth_percent: pct },
              })
            }
          })
        },
        { threshold: 0 },
      )

      sentinels.forEach((s) => observer.observe(s))
      ;(sentinels as any).__observer = observer
    })

    return () => {
      cancelAnimationFrame(raf)
      const observer = (sentinels as any).__observer as IntersectionObserver | undefined
      if (observer) observer.disconnect()
      sentinels.forEach((s) => s.remove())
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pageName])

  return { track }
}
