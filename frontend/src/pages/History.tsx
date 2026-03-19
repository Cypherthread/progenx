import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useAuth } from '@/hooks/useAuth'
import { useDesign } from '@/hooks/useDesign'
import { useAnalytics } from '@/hooks/useAnalytics'

export default function History() {
  useAnalytics('history')
  const user = useAuth((s) => s.user)
  const { history, loadHistory, loadDesign } = useDesign()
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState<'newest' | 'oldest' | 'safety'>('newest')

  useEffect(() => {
    if (user) loadHistory()
  }, [user, loadHistory])

  const filtered = useMemo(() => {
    let list = [...history]

    // Search filter
    if (search.trim()) {
      const q = search.toLowerCase()
      list = list.filter(d =>
        (d.design_name || '').toLowerCase().includes(q) ||
        (d.organism_summary || '').toLowerCase().includes(q) ||
        (d.host_organism || '').toLowerCase().includes(q) ||
        (d.gene_circuit?.genes || []).some((g: any) => g.name?.toLowerCase().includes(q))
      )
    }

    // Sort
    if (sort === 'oldest') list.reverse()
    if (sort === 'safety') list.sort((a, b) => b.safety_score - a.safety_score)

    return list
  }, [history, search, sort])

  if (!user) {
    return (
      <>
        <Helmet><title>My Designs | Progenx</title></Helmet>
        <div className="max-w-3xl mx-auto px-4 py-20 text-center">
          <h1 className="text-2xl font-bold mb-4 text-white">Sign in to view your designs</h1>
          <p className="text-sm text-gray-500">Your design history will appear here after you sign in.</p>
        </div>
      </>
    )
  }

  function safetyColor(score: number) {
    if (score >= 0.8) return 'bg-green-500/20 text-green-400'
    if (score >= 0.5) return 'bg-yellow-500/20 text-yellow-400'
    return 'bg-red-500/20 text-red-400'
  }

  function chassisShort(organism: string) {
    if (!organism) return ''
    if (organism.toLowerCase().includes('coli')) return 'E. coli'
    if (organism.toLowerCase().includes('putida')) return 'P. putida'
    if (organism.toLowerCase().includes('elongatus')) return 'S. elongatus'
    return organism.split(' ').slice(0, 2).join(' ')
  }

  async function openDesign(id: string) {
    await loadDesign(id)
    navigate('/studio')
  }

  return (
    <>
      <Helmet>
        <title>My Designs | Progenx</title>
        <meta name="robots" content="noindex" />
      </Helmet>

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl sm:text-4xl font-bold text-white mb-2">
              <span className="gradient-underline">My Designs</span>
            </h1>
            <p className="text-sm text-gray-500 mt-2">{history.length} design{history.length !== 1 ? 's' : ''} total</p>
          </div>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
            {/* Search */}
            <div className={`relative group ${search ? 'search-focused' : ''}`}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="search-icon w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-600 transition-colors group-focus-within:text-cyan-400">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" strokeLinecap="round" />
              </svg>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search designs..."
                className="pl-9 pr-3 py-2 bg-gray-900/50 border border-gray-800 rounded-lg text-xs text-white placeholder-gray-600 focus:outline-none focus:border-cyan-500/50 focus:bg-gray-900/80 w-full sm:w-52 transition-all"
                onFocus={(e) => e.target.parentElement?.classList.add('search-focused')}
                onBlur={(e) => { if (!search) e.target.parentElement?.classList.remove('search-focused') }}
              />
            </div>

            {/* Sort — pill-shaped segmented control */}
            <div className="flex bg-gray-900/60 border border-gray-700/50 rounded-full p-1 backdrop-blur-sm">
              {([
                { key: 'newest', label: 'Newest' },
                { key: 'oldest', label: 'Oldest' },
                { key: 'safety', label: 'Safety' },
              ] as const).map(({ key, label }) => (
                <button
                  key={key}
                  onClick={() => setSort(key)}
                  className={`px-3 py-1 text-[10px] font-medium rounded-full transition-all duration-200 ${
                    sort === key
                      ? 'bg-cyan-600 text-white shadow-lg shadow-cyan-500/20'
                      : 'text-gray-500 hover:text-white'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        </div>

        {history.length === 0 ? (
          <div className="text-center py-20 border border-dashed border-gray-700 rounded-xl bg-gray-900/30">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-8 h-8 text-gray-500">
                <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
                <rect x="9" y="3" width="6" height="4" rx="1" />
              </svg>
            </div>
            <h3 className="font-semibold mb-2 text-gray-200">No designs yet</h3>
            <p className="text-sm text-gray-500 mb-4">
              Head to the Design Studio to create your first organism.
            </p>
            <button
              onClick={() => navigate('/studio')}
              className="px-6 py-2 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500"
            >
              Open Studio
            </button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-sm text-gray-500">No designs match "{search}"</p>
            <button onClick={() => setSearch('')} className="text-xs text-cyan-400 hover:text-cyan-300 mt-2">
              Clear search
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filtered.map((design) => {
              const genes = design.gene_circuit?.genes || []
              const geneColors = ['#06B6D4', '#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#EC4899']
              return (
                <button
                  key={design.id}
                  onClick={() => openDesign(design.id)}
                  className="text-left bg-gray-900/50 border border-gray-800 rounded-xl overflow-hidden hover:border-cyan-500/30 hover:bg-gray-900/80 active:border-cyan-500/50 active:bg-cyan-500/5 transition-all duration-200 group hover:-translate-y-0.5 hover:shadow-lg hover:shadow-cyan-500/5"
                >
                  {/* Top accent gradient bar */}
                  <div className="h-0.5 bg-gradient-to-r from-cyan-500 to-blue-500" />
                  <div className="p-5">
                  <div className="flex items-start justify-between mb-2">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-white group-hover:text-cyan-300 transition-colors truncate">
                          {design.design_name || 'Untitled'}
                        </h3>
                        {/* Gene color dots */}
                        {genes.length > 0 && (
                          <div className="flex items-center gap-0.5 shrink-0">
                            {genes.slice(0, 5).map((_: any, i: number) => (
                              <div
                                key={i}
                                className="w-1.5 h-1.5 rounded-full opacity-60"
                                style={{ backgroundColor: geneColors[i % geneColors.length] }}
                              />
                            ))}
                          </div>
                        )}
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {chassisShort(design.host_organism)}
                        {design.dna_sequence.length > 0 && <> | {design.dna_sequence.length.toLocaleString()} bp</>}
                        {design.generation_time_sec > 0 && <> | {design.generation_time_sec}s</>}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 ml-3 shrink-0">
                      {design.is_public && (
                        <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-cyan-500/15 text-cyan-400">
                          Public
                        </span>
                      )}
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${safetyColor(design.safety_score)}`}>
                        {Math.round(design.safety_score * 100)}%
                      </span>
                    </div>
                  </div>

                  <p className="text-sm text-gray-400 line-clamp-2 mb-3 leading-relaxed">
                    {design.organism_summary}
                  </p>

                  {/* Gene chips */}
                  {genes.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {genes.slice(0, 5).map((g: any, i: number) => (
                        <span key={i} className="text-[10px] px-1.5 py-0.5 bg-gray-800 text-gray-400 rounded-md">
                          {g.name}
                        </span>
                      ))}
                      {genes.length > 5 && (
                        <span className="text-[10px] text-gray-600">+{genes.length - 5}</span>
                      )}
                    </div>
                  )}
                  </div>{/* close inner p-5 wrapper */}
                </button>
              )
            })}
          </div>
        )}
      </div>
    </>
  )
}
