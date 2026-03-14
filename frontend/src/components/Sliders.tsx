interface Props {
  environment: string
  setEnvironment: (v: string) => void
  safetyLevel: number
  setSafetyLevel: (v: number) => void
  complexity: number
  setComplexity: (v: number) => void
}

const ENVIRONMENTS = [
  { value: 'ocean', label: 'Ocean', icon: '🌊' },
  { value: 'soil', label: 'Soil', icon: '🌱' },
  { value: 'gut', label: 'Gut', icon: '🧬' },
  { value: 'lab', label: 'Lab', icon: '🧪' },
]

export default function Sliders({
  environment,
  setEnvironment,
  safetyLevel,
  setSafetyLevel,
  complexity,
  setComplexity,
}: Props) {
  return (
    <div className="space-y-4 p-4 bg-secondary/50 rounded-xl">
      {/* Environment */}
      <div>
        <label className="text-xs font-medium text-muted-foreground block mb-2">
          Target Environment
        </label>
        <div className="grid grid-cols-4 gap-2">
          {ENVIRONMENTS.map((env) => (
            <button
              key={env.value}
              onClick={() => setEnvironment(env.value)}
              className={`py-2 px-2 rounded-md text-xs font-medium transition-all text-center ${
                environment === env.value
                  ? 'bg-primary text-white shadow-sm'
                  : 'bg-white hover:bg-gray-100'
              }`}
            >
              <span className="block text-base mb-0.5">{env.icon}</span>
              {env.label}
            </button>
          ))}
        </div>
      </div>

      {/* Safety + Complexity side by side */}
      <div className="grid grid-cols-2 gap-4">
        {/* Safety Level */}
        <div>
          <label className="text-xs font-medium text-muted-foreground block mb-2">
            Safety: {Math.round(safetyLevel * 100)}%
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={safetyLevel}
            onChange={(e) => setSafetyLevel(parseFloat(e.target.value))}
            className="w-full accent-primary"
          />
          <div className="flex justify-between text-[10px] text-muted-foreground mt-1">
            <span>Low</span>
            <span>Max</span>
          </div>
        </div>

        {/* Complexity */}
        <div>
          <label className="text-xs font-medium text-muted-foreground block mb-2">
            Complexity: {Math.round(complexity * 100)}%
          </label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={complexity}
            onChange={(e) => setComplexity(parseFloat(e.target.value))}
            className="w-full accent-accent"
          />
          <div className="flex justify-between text-[10px] text-muted-foreground mt-1">
            <span>Simple</span>
            <span>Complex</span>
          </div>
        </div>
      </div>
    </div>
  )
}
