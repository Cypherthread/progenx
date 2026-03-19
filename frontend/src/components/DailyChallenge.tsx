import { useState, useEffect } from 'react'
import { challenges, type Challenge } from '@/lib/api'

interface Props {
  onSelect: (prompt: string) => void
}

const CATEGORY_ICONS: Record<string, string> = {
  climate: '🌍',
  agriculture: '🌾',
  health: '💊',
  energy: '⚡',
  sustainability: '♻️',
  materials: '🧪',
  bioremediation: '🌊',
  food: '🍃',
}

export default function DailyChallenge({ onSelect }: Props) {
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [allChallenges, setAllChallenges] = useState<Challenge[]>([])
  const [showAll, setShowAll] = useState(false)
  const [loadError, setLoadError] = useState(false)

  useEffect(() => {
    challenges.daily()
      .then(setChallenge)
      .catch(() => setLoadError(true))
  }, [])

  async function loadAll() {
    if (allChallenges.length === 0) {
      try {
        const all = await challenges.all()
        setAllChallenges(all)
      } catch {
        return
      }
    }
    setShowAll(!showAll)
  }

  if (loadError || !challenge) return null

  function difficultyStyle(d: string) {
    if (d === 'beginner') return 'bg-green-500/20 text-green-400'
    if (d === 'intermediate') return 'bg-yellow-500/20 text-yellow-400'
    return 'bg-red-500/20 text-red-400'
  }

  return (
    <div className="space-y-3">
      {/* Featured challenge */}
      <div className="relative overflow-hidden rounded-xl border border-cyan-500/20 bg-gradient-to-br from-cyan-500/5 to-transparent">
        <div className="absolute top-0 right-0 w-20 h-20 bg-cyan-500/5 rounded-bl-[40px]" />

        <div className="p-4 relative">
          <div className="flex items-center gap-2 mb-2.5">
            <span className="text-[10px] font-bold uppercase tracking-widest text-cyan-400">
              Today's Challenge
            </span>
            <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-medium ${difficultyStyle(challenge.difficulty)}`}>
              {challenge.difficulty}
            </span>
          </div>

          <h3 className="font-semibold text-white text-sm mb-1.5">
            {CATEGORY_ICONS[challenge.category] || '🧬'} {challenge.title}
          </h3>

          <p className="text-xs text-gray-500 mb-3 leading-relaxed">{challenge.impact}</p>

          <button
            onClick={() => onSelect(challenge.prompt)}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-medium transition-colors"
          >
            Try This Challenge
          </button>
        </div>
      </div>

      {/* Toggle all */}
      <button
        onClick={loadAll}
        className="text-xs text-gray-500 hover:text-cyan-400 font-medium transition-colors flex items-center gap-1"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={`w-3 h-3 transition-transform ${showAll ? 'rotate-180' : ''}`}>
          <path d="M6 9l6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        {showAll ? 'Hide challenges' : 'Browse all challenges'}
      </button>

      {/* All challenges list — shows 3 at a time */}
      {showAll && allChallenges.length > 0 && (
        <div className="space-y-2 max-h-[320px] overflow-y-auto pr-1">
          {allChallenges.map((c) => (
            <button
              key={c.id}
              onClick={() => onSelect(c.prompt)}
              className="w-full text-left p-3 border border-gray-800 rounded-xl bg-gray-900/30 hover:border-cyan-500/20 hover:bg-gray-900/60 active:border-cyan-500/40 active:bg-cyan-500/10 transition-all group"
            >
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-sm shrink-0">{CATEGORY_ICONS[c.category] || '🧬'}</span>
                <p className="text-sm font-medium text-gray-300 group-hover:text-white">{c.title}</p>
                <span className={`text-[9px] px-1.5 py-0.5 rounded-full shrink-0 ml-auto ${difficultyStyle(c.difficulty)}`}>
                  {c.difficulty}
                </span>
              </div>
              <p className="text-xs text-gray-500 leading-relaxed line-clamp-2">{c.impact}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
