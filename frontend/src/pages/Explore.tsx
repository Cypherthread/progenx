import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { explore, type DesignResponse, type ExploreComment } from '@/lib/api'
import { useAuth } from '@/hooks/useAuth'
import { toast } from '@/components/Toast'
import { useAnalytics, track } from '@/hooks/useAnalytics'

export default function Explore() {
  useAnalytics('explore')
  const navigate = useNavigate()
  const { user } = useAuth()
  const [designs, setDesigns] = useState<DesignResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [sort, setSort] = useState<'bumps' | 'newest'>('bumps')
  const [selected, setSelected] = useState<DesignResponse | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [comments, setComments] = useState<ExploreComment[]>([])
  const [bumpCount, setBumpCount] = useState(0)
  const [bumped, setBumped] = useState(false)
  const [commentText, setCommentText] = useState('')
  const [commenting, setCommenting] = useState(false)
  // Track bumps client-side for card counts
  const [cardBumps, setCardBumps] = useState<Record<string, number>>({})
  const [cardBumped, setCardBumped] = useState<Set<string>>(new Set())

  useEffect(() => {
    setLoading(true)
    explore.list(sort)
      .then((data) => {
        setDesigns(data)
        // Initialize card bump counts from response
        const counts: Record<string, number> = {}
        data.forEach(d => { counts[d.id] = d.bump_count ?? 0 })
        setCardBumps(counts)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [sort])

  function openDetail(d: DesignResponse) {
    setSelected(d)
    setComments([])
    setBumpCount(cardBumps[d.id] ?? 0)
    setBumped(cardBumped.has(d.id))
    setCommentText('')
    setDetailLoading(true)
    explore.get(d.id)
      .then((detail) => {
        setComments(detail.comments)
        setBumpCount(detail.bump_count)
      })
      .catch(() => {})
      .finally(() => setDetailLoading(false))
  }

  async function handleBump(designId: string, fromCard = false) {
    track('click', { page: 'explore', element: 'bump', value: designId })
    if (!user) {
      toast('Sign in to bump designs', 'info')
      return
    }
    try {
      const result = await explore.bump(designId)
      // Update card-level state
      setCardBumps(prev => ({ ...prev, [designId]: result.bump_count }))
      setCardBumped(prev => {
        const next = new Set(prev)
        if (result.bumped) next.add(designId)
        else next.delete(designId)
        return next
      })
      // Update modal state if open
      if (!fromCard && selected?.id === designId) {
        setBumpCount(result.bump_count)
        setBumped(result.bumped)
      }
    } catch {
      toast('Could not bump design', 'error')
    }
  }

  async function handleComment() {
    if (!user) {
      toast('Sign in to comment', 'info')
      return
    }
    if (!selected || !commentText.trim()) return
    setCommenting(true)
    try {
      const c = await explore.comment(selected.id, commentText.trim())
      setComments(prev => [{ ...c, created_at: new Date().toISOString() }, ...prev])
      setCommentText('')
      toast('Comment posted')
    } catch {
      toast('Could not post comment', 'error')
    } finally {
      setCommenting(false)
    }
  }

  function safetyColor(score: number) {
    if (score >= 0.8) return 'text-green-400'
    if (score >= 0.5) return 'text-yellow-400'
    return 'text-red-400'
  }

  function chassisShort(organism: string) {
    if (organism.toLowerCase().includes('coli')) return 'E. coli'
    if (organism.toLowerCase().includes('putida')) return 'P. putida'
    if (organism.toLowerCase().includes('elongatus')) return 'S. elongatus'
    return organism.split(' ').slice(0, 2).join(' ')
  }

  function timeAgo(iso: string) {
    const diff = Date.now() - new Date(iso).getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return 'just now'
    if (mins < 60) return `${mins}m ago`
    const hrs = Math.floor(mins / 60)
    if (hrs < 24) return `${hrs}h ago`
    const days = Math.floor(hrs / 24)
    if (days < 30) return `${days}d ago`
    return `${Math.floor(days / 30)}mo ago`
  }

  return (
    <>
      <Helmet>
        <title>Explore Designs | Progenx</title>
        <meta name="description" content="Browse published bioengineering designs from the Progenx community. Plastic-eating microbes, nitrogen fixers, carbon capture organisms, and more." />
      </Helmet>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between mb-10 gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-white mb-3">
              <span className="gradient-underline">Explore Designs</span>
            </h1>
            <p className="text-gray-500 max-w-lg">
              Real designs published by the Progenx community. Bump the ones you like, leave feedback, or fork into your own studio.
            </p>
          </div>

          {/* Sort toggle — pill-shaped segmented control */}
          <div className="flex bg-gray-900/60 border border-gray-700/50 rounded-full p-1 shrink-0 backdrop-blur-sm">
            <button
              onClick={() => setSort('bumps')}
              className={`px-4 py-1.5 text-xs font-medium rounded-full transition-all duration-200 ${
                sort === 'bumps'
                  ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Most Bumped
            </button>
            <button
              onClick={() => setSort('newest')}
              className={`px-4 py-1.5 text-xs font-medium rounded-full transition-all duration-200 ${
                sort === 'newest'
                  ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Newest
            </button>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1,2,3,4,5,6].map(i => (
              <div key={i} className="bg-gray-900/50 border border-gray-800 rounded-xl p-5 animate-pulse">
                <div className="h-5 bg-gray-800 rounded w-2/3 mb-3" />
                <div className="h-3 bg-gray-800 rounded w-1/2 mb-4" />
                <div className="h-16 bg-gray-800 rounded mb-3" />
                <div className="h-3 bg-gray-800 rounded w-1/3" />
              </div>
            ))}
          </div>
        ) : designs.length === 0 ? (
          <div className="text-center py-24 border border-dashed border-gray-700/50 rounded-2xl bg-gradient-to-b from-gray-900/40 to-gray-900/20">
            <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20 flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-10 h-10 text-cyan-400/60">
                <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <h3 className="font-bold text-xl text-white mb-2">The gallery awaits its first design</h3>
            <p className="text-sm text-gray-400 mb-6 max-w-md mx-auto leading-relaxed">
              Create a custom organism in the Design Studio, then publish it to share with the community. Your design could inspire the next breakthrough.
            </p>
            <button
              onClick={() => navigate('/studio')}
              className="px-8 py-2.5 bg-cyan-600 text-white rounded-full text-sm font-medium hover:bg-cyan-500 shadow-lg shadow-cyan-500/20 transition-all hover:shadow-cyan-500/30"
            >
              Open Design Studio
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {designs.map((d) => {
              const genes = d.gene_circuit?.genes || []
              const bumps = cardBumps[d.id] ?? 0
              const isBumped = cardBumped.has(d.id)
              return (
                <div
                  key={d.id}
                  className="bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden hover:border-cyan-500/30 hover:bg-gray-900/80 active:border-cyan-500/50 active:bg-cyan-500/5 transition-all duration-200 group flex flex-col hover:-translate-y-0.5 hover:shadow-lg hover:shadow-cyan-500/5"
                >
                  {/* Top accent gradient bar */}
                  <div className="h-0.5 bg-gradient-to-r from-cyan-500 to-blue-500" />
                  <div className="p-5 flex flex-col flex-1">
                  <button
                    onClick={() => openDetail(d)}
                    className="text-left flex-1"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-white group-hover:text-cyan-300 transition-colors">
                        {d.design_name || 'Untitled'}
                      </h3>
                      <span className={`text-xs font-bold ${safetyColor(d.safety_score)}`}>
                        {Math.round(d.safety_score * 100)}%
                      </span>
                    </div>

                    <p className="text-xs text-gray-500 mb-3">
                      {chassisShort(d.host_organism)} | {genes.length} genes | {d.dna_sequence.length.toLocaleString()} bp
                    </p>

                    <p className="text-sm text-gray-400 line-clamp-3 mb-3 leading-relaxed">
                      {d.organism_summary}
                    </p>

                    {/* Gene chips */}
                    <div className="flex flex-wrap gap-1 mb-3">
                      {genes.slice(0, 4).map((g: any, i: number) => (
                        <span key={i} className="text-[10px] px-1.5 py-0.5 bg-gray-800 text-gray-400 rounded-md">
                          {g.name}
                        </span>
                      ))}
                      {genes.length > 4 && (
                        <span className="text-[10px] text-gray-600">+{genes.length - 4}</span>
                      )}
                    </div>
                  </button>

                  {/* Bump button on card */}
                  <div className="flex items-center justify-between pt-3 border-t border-gray-800/50">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleBump(d.id, true) }}
                      className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
                        isBumped
                          ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                          : 'text-gray-500 hover:text-cyan-400 hover:bg-gray-800 active:bg-cyan-500/10 border border-transparent'
                      }`}
                    >
                      <svg viewBox="0 0 24 24" fill={isBumped ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
                        <path d="M12 19V5M5 12l7-7 7 7" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      {bumps > 0 && <span>{bumps}</span>}
                      <span>{isBumped ? 'Bumped' : 'Bump'}</span>
                    </button>
                    <button
                      onClick={() => openDetail(d)}
                      className="text-[10px] text-gray-600 hover:text-gray-400 transition-colors"
                    >
                      View details
                    </button>
                  </div>
                  </div>{/* close inner p-5 wrapper */}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Design detail modal */}
      {selected && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-start justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-[#0F1629] border border-gray-800 rounded-2xl shadow-2xl w-full max-w-3xl my-8 relative overflow-hidden max-h-[calc(100vh-2rem)] overflow-y-auto">
            {/* Close */}
            <button
              onClick={() => setSelected(null)}
              className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:text-white hover:bg-gray-800/50 transition-colors z-10"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
              </svg>
            </button>

            {/* Gradient header area */}
            <div className="bg-gradient-to-br from-cyan-500/8 via-blue-500/5 to-transparent px-6 pt-6 pb-4 pr-14">
              {/* Title — pr-14 keeps it clear of the absolute close button */}
              <h2 className="text-xl font-bold text-white">{selected.design_name}</h2>
              <p className="text-sm text-gray-500 mt-1">
                {selected.host_organism} | {selected.dna_sequence.length.toLocaleString()} bp | Safety {Math.round(selected.safety_score * 100)}%
              </p>
              {/* Bump button — below title, not competing with close X */}
              <div className="mt-3">
                <button
                  onClick={() => {
                    handleBump(selected.id)
                    const el = document.getElementById('modal-bump-icon')
                    if (el) {
                      el.classList.remove('bump-animate')
                      void el.offsetWidth
                      el.classList.add('bump-animate')
                    }
                  }}
                  className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    bumped
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                      : 'text-gray-400 hover:text-cyan-400 border border-gray-700 hover:border-cyan-500/30 hover:bg-gray-800'
                  }`}
                >
                  <svg id="modal-bump-icon" viewBox="0 0 24 24" fill={bumped ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
                    <path d="M12 19V5M5 12l7-7 7 7" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  <span>{bumpCount}</span>
                  <span>{bumped ? 'Bumped' : 'Bump'}</span>
                </button>
              </div>
            </div>

            <div className="px-6 pb-6 space-y-4">
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
                <h3 className="text-sm font-medium text-white mb-2">What it does</h3>
                <p className="text-sm text-gray-400 whitespace-pre-wrap leading-relaxed">{selected.organism_summary}</p>
              </div>

              {/* Gene list */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
                <h3 className="text-sm font-medium text-white mb-3">Gene Circuit</h3>
                <div className="space-y-2">
                  {(selected.gene_circuit?.genes || []).map((g: any, i: number) => (
                    <div key={i} className="flex items-start justify-between gap-2 text-sm py-1.5 border-b border-gray-800 last:border-0">
                      <div className="min-w-0">
                        <span className="font-medium text-white">{g.name}</span>
                        <span className="text-gray-500 ml-2 text-xs">{g.function}</span>
                      </div>
                      <span className="text-[10px] text-gray-600 shrink-0 mt-0.5">{g.source_organism}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Comments section */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
                <h3 className="text-sm font-medium text-white mb-3">
                  Comments {comments.length > 0 && <span className="text-gray-500 font-normal">({comments.length})</span>}
                </h3>

                {/* Comment input */}
                {user ? (
                  <div className="flex gap-2 mb-4 items-start">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-cyan-500/30 to-blue-500/30 border border-cyan-500/30 flex items-center justify-center shrink-0 mt-0.5">
                      <span className="text-[10px] font-bold text-cyan-300 uppercase">
                        {(user.name || user.email || '?')[0]}
                      </span>
                    </div>
                    <input
                      type="text"
                      value={commentText}
                      onChange={(e) => setCommentText(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && !commenting && handleComment()}
                      placeholder="Share your thoughts on this design..."
                      maxLength={2000}
                      className="flex-1 px-3 py-2 bg-gray-800/50 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/50"
                    />
                    <button
                      onClick={handleComment}
                      disabled={!commentText.trim() || commenting}
                      className="px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500 disabled:opacity-30 disabled:cursor-not-allowed shrink-0"
                    >
                      {commenting ? '...' : 'Post'}
                    </button>
                  </div>
                ) : (
                  <p className="text-xs text-gray-600 mb-4">Sign in to leave a comment.</p>
                )}

                {/* Comment list */}
                {detailLoading ? (
                  <div className="space-y-3">
                    {[1,2].map(i => (
                      <div key={i} className="animate-pulse">
                        <div className="h-3 bg-gray-800 rounded w-1/4 mb-1" />
                        <div className="h-3 bg-gray-800 rounded w-3/4" />
                      </div>
                    ))}
                  </div>
                ) : comments.length === 0 ? (
                  <p className="text-xs text-gray-600">No comments yet. Be the first.</p>
                ) : (
                  <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
                    {comments.map((c) => (
                      <div key={c.id} className="border-b border-gray-800/50 pb-3 last:border-0 last:pb-0 flex gap-3">
                        {/* Avatar circle */}
                        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/20 flex items-center justify-center shrink-0 mt-0.5">
                          <span className="text-[10px] font-bold text-cyan-400 uppercase">
                            {(c.author || '?')[0]}
                          </span>
                        </div>
                        <div className="min-w-0 flex-1">
                          <div className="flex items-center gap-2 mb-0.5">
                            <span className="text-xs font-medium text-gray-200">{c.author}</span>
                            {c.created_at && (
                              <span className="text-[10px] text-gray-600/70">{timeAgo(c.created_at)}</span>
                            )}
                          </div>
                          <p className="text-sm text-gray-400 leading-relaxed">{c.text}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => {
                    navigate('/studio', { state: { prompt: selected.organism_summary.slice(0, 200) } })
                    setSelected(null)
                  }}
                  className="flex-1 py-3 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500"
                >
                  Fork this design into Studio
                </button>
                <button
                  onClick={() => setSelected(null)}
                  className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg text-sm hover:bg-gray-800"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
