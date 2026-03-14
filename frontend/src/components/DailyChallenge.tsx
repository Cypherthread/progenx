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
      case 'beginner': return 'bg-green-100 text-green-700'
      case 'intermediate': return 'bg-yellow-100 text-yellow-700'
      case 'advanced': return 'bg-red-100 text-red-700'
      default: return 'bg-gray-100 text-gray-700'
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
      {/* Daily Challenge */}
      {challenge && (
        <div className="dna-gradient rounded-xl p-[1px]">
          <div className="bg-white rounded-[11px] p-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-primary">
                Today's Climate Challenge
              </span>
              <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${difficultyColor(challenge.difficulty)}`}>
                {challenge.difficulty}
              </span>
            </div>
            <h3 className="font-medium text-sm mb-1">
              {categoryIcon(challenge.category)} {challenge.title}
            </h3>
            <p className="text-xs text-muted-foreground mb-3">{challenge.impact}</p>
            <button
              onClick={() => onSelect(challenge.prompt)}
              className="px-3 py-1.5 bg-primary text-white rounded-md text-xs font-medium hover:opacity-90"
            >
              Try This Challenge
            </button>
          </div>
        </div>
      )}

      {/* Show More */}
      <button
        onClick={loadAll}
        className="text-xs text-primary font-medium hover:underline"
      >
        {showAll ? 'Hide challenges' : 'Browse all challenges'}
      </button>

      {showAll && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-64 overflow-y-auto">
          {allChallenges.map((c) => (
            <button
              key={c.id}
              onClick={() => onSelect(c.prompt)}
              className="text-left p-3 border rounded-lg hover:bg-secondary/50 transition-colors"
            >
              <div className="flex items-center gap-1 mb-1">
                <span className="text-sm">{categoryIcon(c.category)}</span>
                <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${difficultyColor(c.difficulty)}`}>
                  {c.difficulty}
                </span>
              </div>
              <p className="text-xs font-medium">{c.title}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
