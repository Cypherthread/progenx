import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useDesign } from '@/hooks/useDesign'

export default function History() {
  const user = useAuth((s) => s.user)
  const { history, loadHistory, loadDesign } = useDesign()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) loadHistory()
  }, [user, loadHistory])

  if (!user) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-20 text-center">
        <h1 className="text-2xl font-bold mb-4 text-white">Sign in to view your designs</h1>
      </div>
    )
  }

  function safetyBadge(score: number) {
    if (score >= 0.8) return 'bg-green-500/20 text-green-400'
    if (score >= 0.5) return 'bg-yellow-500/20 text-yellow-400'
    return 'bg-red-500/20 text-red-400'
  }

  async function openDesign(id: string) {
    await loadDesign(id)
    navigate('/studio')
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6 text-white">My Designs</h1>

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
      ) : (
        <div className="space-y-3">
          {history.map((design) => (
            <button
              key={design.id}
              onClick={() => openDesign(design.id)}
              className="w-full text-left p-4 bg-gray-900/50 border border-gray-800 rounded-xl hover:border-cyan-500/30 hover:bg-gray-900/80 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium truncate text-white">{design.design_name || 'Untitled'}</h3>
                  <p className="text-sm text-gray-500 mt-1 line-clamp-2">
                    {design.organism_summary.slice(0, 150)}...
                  </p>
                </div>
                <div className="ml-4 flex flex-col items-end gap-1 shrink-0">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${safetyBadge(design.safety_score)}`}>
                    Safety: {Math.round(design.safety_score * 100)}%
                  </span>
                  <span className="text-[10px] text-gray-600">
                    {design.generation_time_sec}s | {design.dna_sequence.length.toLocaleString()} bp
                  </span>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
