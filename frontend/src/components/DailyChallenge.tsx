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
}

export default function DailyChallenge({ onSelect }: Props) {
  const [challenge, setChallenge] = useState<Challenge | null>(null)
  const [allChallenges, setAllChallenges] = useState<Challenge[]>([])
  const [showAll, setShowAll] = useState(false)

  useEffect(() => {
    challenges.daily().then(setChallenge).catch(() => {})
  }, [])

  async function loadAll() {
    if (allChallenges.length === 0) {
      const all = await challenges.all()
      setAllChallenges(all)
    }
    setShowAll(!showAll)
  }

  if (!challenge) return null

  return (
    <div className="space-y-3">
      {/* Featured challenge */}
      <div className="relative overflow-hidden rounded-xl border border-cyan-500/20 bg-gradient-to-br from-cyan-500/5 to-transparent">
        {/* Decorative corner */}
        <div className="absolute top-0 right-0 w-20 h-20 bg-cyan-500/5 rounded-bl-[40px]" />

        <div className="p-4 relative">
          <div className="flex items-center gap-2 mb-2.5">
            <span className="text-[10px] font-bold uppercase tracking-widest text-cyan-400">
              Today's Challenge
            </span>
            <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-medium ${
              challenge.difficulty === 'beginner' ? 'bg-green-500/20 text-green-400' :
              challenge.difficulty === 'intermediate' ? 'bg-yellow-500/20 text-yellow-400' :
              'bg-red-500/20 text-red-400'
            }`}>
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

      {/* All challenges grid */}
      {showAll && (
        <div className="grid grid-cols-1 gap-1.5 max-h-60 overflow-y-auto pr-1">
          {allChallenges.map((c) => (
            <button
              key={c.id}
              onClick={() => onSelect(c.prompt)}
              className="text-left p-3 border border-gray-800 rounded-lg bg-gray-900/30 hover:border-cyan-500/20 hover:bg-gray-900/60 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-sm shrink-0">{CATEGORY_ICONS[c.category] || '🧬'}</span>
                  <p className="text-xs font-medium text-gray-300 group-hover:text-white truncate">{c.title}</p>
                </div>
                <span className={`text-[9px] px-1.5 py-0.5 rounded-full shrink-0 ml-2 ${
                  c.difficulty === 'beginner' ? 'bg-green-500/15 text-green-400' :
                  c.difficulty === 'intermediate' ? 'bg-yellow-500/15 text-yellow-400' :
                  'bg-red-500/15 text-red-400'
                }`}>
                  {c.difficulty}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
