import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { explore, type DesignResponse } from '@/lib/api'

export default function Explore() {
  const navigate = useNavigate()
  const [designs, setDesigns] = useState<DesignResponse[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<DesignResponse | null>(null)

  useEffect(() => {
    explore.list()
      .then(setDesigns)
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

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

  return (
    <>
      <Helmet>
        <title>Explore Designs | Progenx</title>
        <meta name="description" content="Browse published bioengineering designs from the Progenx community. Plastic-eating microbes, nitrogen fixers, carbon capture organisms, and more." />
      </Helmet>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold text-white mb-2">Explore Designs</h1>
          <p className="text-gray-500 max-w-lg mx-auto">
            Real designs published by the Progenx community. Click any design to see the full details, or fork it into your own studio.
          </p>
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
          <div className="text-center py-20 border border-dashed border-gray-700 rounded-xl bg-gray-900/30">
            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-8 h-8 text-gray-500">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" strokeLinecap="round" />
              </svg>
            </div>
            <h3 className="font-semibold text-gray-200 mb-2">No published designs yet</h3>
            <p className="text-sm text-gray-500 mb-4 max-w-sm mx-auto">
              Be the first to publish. Design something in the studio, then click "Share" to make it public.
            </p>
            <button
              onClick={() => navigate('/studio')}
              className="px-6 py-2 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500"
            >
              Open Studio
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {designs.map((d) => {
              const genes = d.gene_circuit?.genes || []
              return (
                <button
                  key={d.id}
                  onClick={() => setSelected(d)}
                  className="text-left bg-gray-900/50 border border-gray-800 rounded-xl p-5 hover:border-cyan-500/30 hover:bg-gray-900/80 transition-all group"
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

                  <p className="text-sm text-gray-400 line-clamp-3 mb-3">
                    {d.organism_summary.slice(0, 150)}...
                  </p>

                  {/* Gene chips */}
                  <div className="flex flex-wrap gap-1">
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
              )
            })}
          </div>
        )}
      </div>

      {/* Design detail modal */}
      {selected && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-start justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-[#0F1629] border border-gray-800 rounded-2xl shadow-2xl w-full max-w-3xl my-8 relative">
            {/* Close */}
            <button
              onClick={() => setSelected(null)}
              className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-lg text-gray-500 hover:text-white hover:bg-gray-800 transition-colors z-10"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4">
                <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
              </svg>
            </button>

            <div className="p-6 space-y-4">
              <div>
                <h2 className="text-xl font-bold text-white">{selected.design_name}</h2>
                <p className="text-sm text-gray-500 mt-1">
                  {selected.host_organism} | {selected.dna_sequence.length.toLocaleString()} bp | Safety {Math.round(selected.safety_score * 100)}%
                </p>
              </div>

              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
                <h3 className="text-sm font-medium text-white mb-2">What it does</h3>
                <p className="text-sm text-gray-400 whitespace-pre-wrap leading-relaxed">{selected.organism_summary}</p>
              </div>

              {/* Gene list */}
              <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
                <h3 className="text-sm font-medium text-white mb-3">Gene Circuit</h3>
                <div className="space-y-2">
                  {(selected.gene_circuit?.genes || []).map((g: any, i: number) => (
                    <div key={i} className="flex items-center justify-between text-sm py-1 border-b border-gray-800 last:border-0">
                      <div>
                        <span className="font-medium text-white">{g.name}</span>
                        <span className="text-gray-500 ml-2">{g.function}</span>
                      </div>
                      <span className="text-xs text-gray-600">{g.source_organism}</span>
                    </div>
                  ))}
                </div>
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
