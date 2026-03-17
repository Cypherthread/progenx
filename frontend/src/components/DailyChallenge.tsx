import { useState, useEffect } from 'react'
import { challenges, type Challenge } from '@/lib/api'

interface Props {
  onSelect: (prompt: string) => void
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

  const difficultyColor = (d: string) => {
    switch (d) {
      case 'beginner': return 'bg-green-500/20 text-green-400'
      case 'intermediate': return 'bg-yellow-500/20 text-yellow-400'
      case 'advanced': return 'bg-red-500/20 text-red-400'
      default: return 'bg-gray-800 text-gray-400'
    }
  }

  const categoryIcon = (c: string) => {
    switch (c) {
      case 'climate': return '🌍'
      case 'agriculture': return '🌾'
      case 'health': return '💊'
      case 'energy': return '⚡'
      case 'sustainability': return '♻️'
      default: return '🧬'
    }
  }

  return (
    <div className="space-y-3">
      {challenge && (
        <div className="border border-cyan-500/30 rounded-xl p-4 bg-cyan-500/5">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
              Today's Climate Challenge
            </span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${difficultyColor(challenge.difficulty)}`}>
              {challenge.difficulty}
            </span>
          </div>
          <h3 className="font-medium text-sm mb-1 text-white">
            {categoryIcon(challenge.category)} {challenge.title}
          </h3>
          <p className="text-xs text-gray-500 mb-3">{challenge.impact}</p>
          <button
            onClick={() => onSelect(challenge.prompt)}
            className="px-3 py-1.5 bg-cyan-600 text-white rounded-lg text-xs font-medium hover:bg-cyan-500"
          >
            Try This Challenge
          </button>
        </div>
      )}

      <button
        onClick={loadAll}
        className="text-xs text-cyan-400 font-medium hover:text-cyan-300"
      >
        {showAll ? 'Hide challenges' : 'Browse all challenges'}
      </button>

      {showAll && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-64 overflow-y-auto">
          {allChallenges.map((c) => (
            <button
              key={c.id}
              onClick={() => onSelect(c.prompt)}
              className="text-left p-3 border border-gray-800 rounded-lg bg-gray-900/30 hover:border-cyan-500/30 hover:bg-gray-900/60 transition-colors"
            >
              <div className="flex items-center gap-1 mb-1">
                <span className="text-sm">{categoryIcon(c.category)}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${difficultyColor(c.difficulty)}`}>
                  {c.difficulty}
                </span>
              </div>
              <p className="text-xs font-medium text-gray-300">{c.title}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
