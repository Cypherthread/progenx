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
        <h1 className="text-2xl font-bold mb-4">Sign in to view your designs</h1>
      </div>
    )
  }

  function safetyBadge(score: number) {
    if (score >= 0.8) return 'bg-green-100 text-green-700'
    if (score >= 0.5) return 'bg-yellow-100 text-yellow-700'
    return 'bg-red-100 text-red-700'
  }

  async function openDesign(id: string) {
    await loadDesign(id)
    navigate('/studio')
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">My Designs</h1>

      {history.length === 0 ? (
        <div className="text-center py-20 border-2 border-dashed rounded-xl">
          <div className="text-5xl mb-4">🔬</div>
          <h3 className="font-semibold mb-2">No designs yet</h3>
          <p className="text-sm text-muted-foreground mb-4">
            Head to the Design Studio to create your first organism.
          </p>
          <button
            onClick={() => navigate('/studio')}
            className="px-6 py-2 bg-primary text-white rounded-md text-sm font-medium hover:opacity-90"
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
              className="w-full text-left p-4 bg-white border rounded-xl hover:border-primary hover:shadow-md transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium truncate">{design.design_name || 'Untitled'}</h3>
                  <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                    {design.organism_summary.slice(0, 150)}...
                  </p>
                </div>
                <div className="ml-4 flex flex-col items-end gap-1 shrink-0">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${safetyBadge(design.safety_score)}`}>
                    Safety: {Math.round(design.safety_score * 100)}%
                  </span>
                  <span className="text-[10px] text-muted-foreground">
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
