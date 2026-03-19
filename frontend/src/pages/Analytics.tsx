import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useAuth } from '@/hooks/useAuth'

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

const API_BASE = import.meta.env.PROD
  ? 'https://api.progenx.ai/api'
  : '/api'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface OverviewStats {
  total_sessions: number
  unique_users: number
  pages_viewed: number
  avg_session_duration_seconds: number
}

interface PageViewEntry {
  page: string
  views: number
}

interface ClickEntry {
  element: string
  page: string
  count: number
}

interface ScrollDepthEntry {
  page: string
  reached_25: number
  reached_50: number
  reached_75: number
  reached_100: number
}

interface FunnelStep {
  step: string
  count: number
  pct_of_first: number
}

interface FeatureEntry {
  feature: string
  uses: number
}

interface Suggestion {
  type: 'warning' | 'idea'
  text: string
}

interface DashboardData {
  overview: OverviewStats
  page_views: PageViewEntry[]
  clicks: ClickEntry[]
  scroll_depth: ScrollDepthEntry[]
  funnel: FunnelStep[]
  feature_usage: FeatureEntry[]
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`
  const m = Math.floor(seconds / 60)
  const s = Math.round(seconds % 60)
  return `${m}m ${s}s`
}

async function apiFetch<T>(path: string): Promise<T> {
  const token = localStorage.getItem('pf_token')
  const headers: Record<string, string> = {}
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, { headers })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function Analytics() {
  const navigate = useNavigate()
  const user = useAuth((s) => s.user)

  const [range, setRange] = useState<'7d' | '30d'>('7d')
  const [dashboard, setDashboard] = useState<DashboardData | null>(null)
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Redirect non-admin users
  useEffect(() => {
    if (user && user.tier !== 'admin') {
      navigate('/')
    }
  }, [user, navigate])

  // Fetch data
  useEffect(() => {
    if (!user || user.tier !== 'admin') return

    let cancelled = false
    setLoading(true)
    setError(null)

    Promise.all([
      apiFetch<DashboardData>(`/analytics/dashboard?range=${range}`),
      apiFetch<Suggestion[]>(`/analytics/suggestions?range=${range}`),
    ])
      .then(([d, s]) => {
        if (cancelled) return
        setDashboard(d)
        setSuggestions(s)
      })
      .catch((e) => {
        if (cancelled) return
        setError(e.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [user, range])

  // Guard: must be admin
  if (!user || user.tier !== 'admin') {
    return null
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  return (
    <>
      <Helmet>
        <title>Analytics | Progenx</title>
        <meta name="robots" content="noindex" />
      </Helmet>

      <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">Analytics</h1>
          <div className="flex gap-1 bg-gray-900/50 border border-gray-800 rounded-lg p-0.5">
            <button
              onClick={() => setRange('7d')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                range === '7d'
                  ? 'bg-cyan-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Last 7 days
            </button>
            <button
              onClick={() => setRange('30d')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                range === '30d'
                  ? 'bg-cyan-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Last 30 days
            </button>
          </div>
        </div>

        {/* Loading / Error */}
        {loading && (
          <div className="flex items-center justify-center py-20">
            <svg className="w-6 h-6 animate-spin text-cyan-500" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-20" />
              <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
            </svg>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-sm text-red-400">
            Failed to load analytics: {error}
          </div>
        )}

        {dashboard && !loading && (
          <>
            {/* Overview Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <OverviewCard
                label="Sessions"
                value={dashboard.overview.total_sessions.toLocaleString()}
                icon={
                  <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                }
                iconStroke={
                  <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                }
              />
              <OverviewCard
                label="Unique Users"
                value={dashboard.overview.unique_users.toLocaleString()}
                icon={
                  <path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                }
              />
              <OverviewCard
                label="Pages Viewed"
                value={dashboard.overview.pages_viewed.toLocaleString()}
                icon={
                  <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                }
              />
              <OverviewCard
                label="Avg Session"
                value={formatDuration(dashboard.overview.avg_session_duration_seconds)}
                icon={
                  <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                }
              />
            </div>

            {/* Page Views Chart */}
            <Section title="Page Views">
              {dashboard.page_views.length === 0 ? (
                <EmptyState text="No page view data yet" />
              ) : (
                <PageViewsChart data={dashboard.page_views} />
              )}
            </Section>

            {/* Click Heatmap */}
            <Section title="Click Heatmap">
              {dashboard.clicks.length === 0 ? (
                <EmptyState text="No click data yet" />
              ) : (
                <ClickTable data={dashboard.clicks} />
              )}
            </Section>

            {/* Scroll Depth */}
            <Section title="Scroll Depth">
              {dashboard.scroll_depth.length === 0 ? (
                <EmptyState text="No scroll data yet" />
              ) : (
                <ScrollDepthBars data={dashboard.scroll_depth} />
              )}
            </Section>

            {/* Funnel */}
            <Section title="Conversion Funnel">
              {dashboard.funnel.length === 0 ? (
                <EmptyState text="No funnel data yet" />
              ) : (
                <FunnelVis data={dashboard.funnel} />
              )}
            </Section>

            {/* Feature Usage */}
            <Section title="Feature Usage">
              {dashboard.feature_usage.length === 0 ? (
                <EmptyState text="No feature usage data yet" />
              ) : (
                <FeatureTable data={dashboard.feature_usage} />
              )}
            </Section>

            {/* Suggestions */}
            <Section title="Suggestions">
              {suggestions.length === 0 ? (
                <EmptyState text="No suggestions available" />
              ) : (
                <SuggestionsList data={suggestions} />
              )}
            </Section>
          </>
        )}
      </div>
    </>
  )
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">
      <h2 className="text-sm font-semibold text-white mb-4">{title}</h2>
      {children}
    </div>
  )
}

function EmptyState({ text }: { text: string }) {
  return <p className="text-xs text-gray-600 py-4 text-center">{text}</p>
}

function OverviewCard({
  label,
  value,
  icon,
  iconStroke,
}: {
  label: string
  value: string
  icon: React.ReactNode
  iconStroke?: React.ReactNode
}) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5 flex items-start gap-3">
      <div className="w-9 h-9 rounded-lg bg-cyan-500/10 flex items-center justify-center shrink-0">
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="w-4.5 h-4.5 text-cyan-400"
        >
          {icon}
          {iconStroke}
        </svg>
      </div>
      <div>
        <p className="text-xs text-gray-500">{label}</p>
        <p className="text-lg font-bold text-white mt-0.5">{value}</p>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Page Views — CSS-only horizontal bar chart
// ---------------------------------------------------------------------------

function PageViewsChart({ data }: { data: PageViewEntry[] }) {
  const max = Math.max(...data.map((d) => d.views), 1)

  return (
    <div className="space-y-2">
      {data.map((entry) => (
        <div key={entry.page} className="flex items-center gap-3">
          <span className="text-xs text-gray-400 w-28 truncate shrink-0" title={entry.page}>
            {entry.page}
          </span>
          <div className="flex-1 h-6 bg-gray-800/50 rounded overflow-hidden relative">
            <div
              className="h-full bg-gradient-to-r from-cyan-600 to-cyan-400 rounded transition-all duration-500"
              style={{ width: `${(entry.views / max) * 100}%` }}
            />
            <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-gray-300 font-medium">
              {entry.views.toLocaleString()}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Click Heatmap — sorted table
// ---------------------------------------------------------------------------

function ClickTable({ data }: { data: ClickEntry[] }) {
  const sorted = [...data].sort((a, b) => b.count - a.count)
  const max = sorted[0]?.count || 1

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-gray-800">
            <th className="text-left py-2 text-gray-500 font-medium">Element</th>
            <th className="text-left py-2 text-gray-500 font-medium">Page</th>
            <th className="text-right py-2 text-gray-500 font-medium">Clicks</th>
            <th className="w-32 py-2" />
          </tr>
        </thead>
        <tbody>
          {sorted.slice(0, 20).map((row, i) => (
            <tr key={i} className="border-b border-gray-800/50">
              <td className="py-2 text-gray-300 font-medium max-w-[200px] truncate" title={row.element}>
                {row.element}
              </td>
              <td className="py-2 text-gray-500">{row.page}</td>
              <td className="py-2 text-right text-white font-medium tabular-nums">
                {row.count.toLocaleString()}
              </td>
              <td className="py-2 pl-3">
                <div className="h-2 bg-gray-800/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-500/60 rounded-full"
                    style={{ width: `${(row.count / max) * 100}%` }}
                  />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Scroll Depth — horizontal stacked bars per page
// ---------------------------------------------------------------------------

function ScrollDepthBars({ data }: { data: ScrollDepthEntry[] }) {
  return (
    <div className="space-y-4">
      {data.map((entry) => {
        const total = entry.reached_25 || 1
        const segments = [
          { label: '25%', value: entry.reached_25, color: 'bg-cyan-400/30' },
          { label: '50%', value: entry.reached_50, color: 'bg-cyan-400/50' },
          { label: '75%', value: entry.reached_75, color: 'bg-cyan-400/70' },
          { label: '100%', value: entry.reached_100, color: 'bg-cyan-400' },
        ]

        return (
          <div key={entry.page}>
            <p className="text-xs text-gray-400 mb-1.5">{entry.page}</p>
            <div className="flex gap-1 h-7">
              {segments.map((seg) => {
                const pct = total > 0 ? (seg.value / total) * 100 : 0
                return (
                  <div
                    key={seg.label}
                    className={`${seg.color} rounded flex items-center justify-center transition-all relative group`}
                    style={{ width: `${Math.max(pct, 4)}%` }}
                  >
                    <span className="text-[9px] text-white font-medium">
                      {seg.label}
                    </span>
                    <span className="absolute -top-6 left-1/2 -translate-x-1/2 text-[10px] bg-gray-800 text-gray-300 px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                      {seg.value.toLocaleString()} users
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        )
      })}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Funnel Visualization — horizontal steps with drop-off
// ---------------------------------------------------------------------------

function FunnelVis({ data }: { data: FunnelStep[] }) {
  const maxCount = data[0]?.count || 1

  return (
    <div className="space-y-0">
      {data.map((step, i) => {
        const widthPct = (step.count / maxCount) * 100
        const prevCount = i > 0 ? data[i - 1].count : step.count
        const dropOff = prevCount > 0 ? ((prevCount - step.count) / prevCount) * 100 : 0

        return (
          <div key={step.step} className="flex items-center gap-3 py-1.5">
            {/* Step label */}
            <span className="text-xs text-gray-400 w-20 shrink-0 capitalize truncate" title={step.step}>
              {step.step}
            </span>

            {/* Bar */}
            <div className="flex-1 relative">
              <div
                className="h-8 bg-gradient-to-r from-cyan-600 to-cyan-500 rounded flex items-center px-3 transition-all duration-500"
                style={{ width: `${Math.max(widthPct, 6)}%` }}
              >
                <span className="text-[10px] text-white font-bold whitespace-nowrap">
                  {step.count.toLocaleString()}
                </span>
              </div>
            </div>

            {/* Drop-off indicator */}
            <div className="w-20 shrink-0 text-right">
              {i === 0 ? (
                <span className="text-[10px] text-gray-600">100%</span>
              ) : (
                <span className={`text-[10px] font-medium ${dropOff > 50 ? 'text-red-400' : dropOff > 25 ? 'text-amber-400' : 'text-green-400'}`}>
                  {dropOff > 0 ? `-${dropOff.toFixed(0)}%` : '0%'} drop
                </span>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Feature Usage — ranked list
// ---------------------------------------------------------------------------

function FeatureTable({ data }: { data: FeatureEntry[] }) {
  const sorted = [...data].sort((a, b) => b.uses - a.uses)
  const max = sorted[0]?.uses || 1

  return (
    <div className="space-y-2">
      {sorted.map((entry) => (
        <div key={entry.feature} className="flex items-center gap-3">
          <span className="text-xs text-gray-400 w-36 truncate shrink-0" title={entry.feature}>
            {entry.feature}
          </span>
          <div className="flex-1 h-5 bg-gray-800/50 rounded overflow-hidden relative">
            <div
              className="h-full bg-gradient-to-r from-purple-600/60 to-purple-400/60 rounded transition-all duration-500"
              style={{ width: `${(entry.uses / max) * 100}%` }}
            />
            <span className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-gray-300 font-medium">
              {entry.uses.toLocaleString()}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Suggestions List
// ---------------------------------------------------------------------------

function SuggestionsList({ data }: { data: Suggestion[] }) {
  return (
    <div className="space-y-2">
      {data.map((s, i) => (
        <div
          key={i}
          className={`flex items-start gap-3 p-3 rounded-lg border ${
            s.type === 'warning'
              ? 'bg-amber-500/5 border-amber-500/20'
              : 'bg-cyan-500/5 border-cyan-500/20'
          }`}
        >
          {/* Icon */}
          <div className="shrink-0 mt-0.5">
            {s.type === 'warning' ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 text-amber-400">
                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                <path d="M12 9v4M12 17h.01" strokeLinecap="round" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 text-cyan-400">
                <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            )}
          </div>
          <p className={`text-xs leading-relaxed ${s.type === 'warning' ? 'text-amber-300' : 'text-cyan-300'}`}>
            {s.text}
          </p>
        </div>
      ))}
    </div>
  )
}
