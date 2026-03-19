interface Props {
  environment: string
  setEnvironment: (v: string) => void
  safetyLevel: number
  setSafetyLevel: (v: number) => void
  complexity: number
  setComplexity: (v: number) => void
}

const ENVIRONMENTS = [
  {
    value: 'ocean',
    label: 'Marine',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
        <path d="M2 12c1.5-2 3.5-3 5.5-3s4 1 5.5 3c1.5-2 3.5-3 5.5-3s4 1 5.5 3" />
        <path d="M2 17c1.5-2 3.5-3 5.5-3s4 1 5.5 3c1.5-2 3.5-3 5.5-3s4 1 5.5 3" opacity="0.5" />
      </svg>
    ),
    desc: 'Salt-tolerant organisms',
  },
  {
    value: 'soil',
    label: 'Terrestrial',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
        <path d="M12 2v6M8 6l4-4 4 4" />
        <path d="M4 14c2-1 4-2 8-2s6 1 8 2" />
        <path d="M2 20h20" />
      </svg>
    ),
    desc: 'Soil and plant systems',
  },
  {
    value: 'gut',
    label: 'Gut / Body',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
        <circle cx="12" cy="12" r="9" />
        <path d="M9 9c0 1.5 1.5 2 3 2s3 .5 3 2-1.5 2-3 2-3 .5-3 2" />
      </svg>
    ),
    desc: 'Probiotics and in-vivo',
  },
  {
    value: 'lab',
    label: 'Laboratory',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5">
        <path d="M9 3h6M10 3v7.4L6 18h12l-4-7.6V3" />
        <path d="M8 15h8" />
      </svg>
    ),
    desc: 'Controlled conditions',
  },
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
    <div className="space-y-5">
      {/* Environment selector */}
      <div>
        <label className="text-xs font-semibold uppercase tracking-widest text-gray-500 block mb-2.5">
          Target Environment
        </label>
        <div className="grid grid-cols-2 gap-2">
          {ENVIRONMENTS.map((env) => (
            <button
              key={env.value}
              onClick={() => setEnvironment(env.value)}
              className={`relative p-3 rounded-xl text-left transition-all duration-200 ${
                environment === env.value
                  ? 'bg-cyan-500/10 border-2 border-cyan-500/50 shadow-lg shadow-cyan-500/5'
                  : 'bg-gray-900/50 border border-gray-800 hover:border-gray-700 hover:bg-gray-900/80'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <div className={`${environment === env.value ? 'text-cyan-400' : 'text-gray-500'} transition-colors`}>
                  {env.icon}
                </div>
                <div>
                  <p className={`text-sm font-medium ${environment === env.value ? 'text-white' : 'text-gray-300'}`}>
                    {env.label}
                  </p>
                  <p className="text-[10px] text-gray-600">{env.desc}</p>
                </div>
              </div>
              {environment === env.value && (
                <div className="absolute top-2 right-2 w-2 h-2 bg-cyan-400 rounded-full" />
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Safety + Complexity */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-3">
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-semibold uppercase tracking-widest text-gray-500">
              Safety
            </label>
            <span className={`text-xs font-bold tabular-nums ${
              safetyLevel >= 0.7 ? 'text-green-400' : safetyLevel >= 0.4 ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {Math.round(safetyLevel * 100)}%
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={safetyLevel}
            onChange={(e) => setSafetyLevel(parseFloat(e.target.value))}
            className="w-full accent-cyan-500 h-1.5"
          />
          <div className="flex justify-between text-[9px] text-gray-600 mt-1">
            <span>Minimal</span>
            <span>Maximum</span>
          </div>
        </div>

        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-3">
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-semibold uppercase tracking-widest text-gray-500">
              Complexity
            </label>
            <span className="text-xs font-bold tabular-nums text-cyan-400">
              {complexity <= 0.33 ? 'Simple' : complexity <= 0.66 ? 'Medium' : 'Advanced'}
            </span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={complexity}
            onChange={(e) => setComplexity(parseFloat(e.target.value))}
            className="w-full accent-cyan-500 h-1.5"
          />
          <div className="flex justify-between text-[9px] text-gray-600 mt-1">
            <span>Fewer genes</span>
            <span>More genes</span>
          </div>
        </div>
      </div>
    </div>
  )
}
