import { useCallback } from 'react'

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

// Arc dial component
function ArcDial({
  value,
  onChange,
  label,
  color,
  displayValue,
  min = 0,
  max = 1,
  leftLabel,
  rightLabel,
}: {
  value: number
  onChange: (v: number) => void
  label: string
  color: string
  displayValue: string
  min?: number
  max?: number
  leftLabel: string
  rightLabel: string
}) {
  const normalized = (value - min) / (max - min)
  const startAngle = -130
  const endAngle = 130
  const currentAngle = startAngle + normalized * (endAngle - startAngle)
  const cx = 60
  const cy = 55
  const r = 38

  function angleToXY(angle: number): [number, number] {
    const rad = (angle - 90) * Math.PI / 180
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)]
  }

  const [sx, sy] = angleToXY(startAngle)
  const [ex, ey] = angleToXY(currentAngle)
  const [fx, fy] = angleToXY(endAngle)
  const largeArc = (currentAngle - startAngle) > 180 ? 1 : 0
  const trackLargeArc = (endAngle - startAngle) > 180 ? 1 : 0

  // Handle click/drag on the arc
  const handleInteraction = useCallback((clientX: number, clientY: number, svgEl: SVGSVGElement) => {
    const rect = svgEl.getBoundingClientRect()
    const x = clientX - rect.left - (rect.width / 2)
    const y = clientY - rect.top - (rect.height * 0.46)
    let angle = Math.atan2(y, x) * 180 / Math.PI + 90
    if (angle < -180) angle += 360
    if (angle > 180) angle -= 360
    const clamped = Math.max(startAngle, Math.min(endAngle, angle))
    const newNorm = (clamped - startAngle) / (endAngle - startAngle)
    // Smooth: step by 5% instead of jumping
    const stepped = Math.round(newNorm * 20) / 20
    onChange(min + stepped * (max - min))
  }, [onChange, min, max])

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4 flex flex-col items-center">
      <label className="text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">{label}</label>
      <svg
        viewBox="0 0 120 80"
        className="w-full max-w-[160px] cursor-pointer select-none touch-none"
        onClick={(e) => handleInteraction(e.clientX, e.clientY, e.currentTarget)}
        onMouseDown={(e) => {
          e.preventDefault()
          const svg = e.currentTarget
          handleInteraction(e.clientX, e.clientY, svg)
          const move = (ev: MouseEvent) => { ev.preventDefault(); handleInteraction(ev.clientX, ev.clientY, svg) }
          const up = () => { document.removeEventListener('mousemove', move); document.removeEventListener('mouseup', up) }
          document.addEventListener('mousemove', move)
          document.addEventListener('mouseup', up)
        }}
        onTouchStart={(e) => {
          const svg = e.currentTarget
          const touch = e.touches[0]
          handleInteraction(touch.clientX, touch.clientY, svg)
          const move = (ev: TouchEvent) => { ev.preventDefault(); handleInteraction(ev.touches[0].clientX, ev.touches[0].clientY, svg) }
          const end = () => { document.removeEventListener('touchmove', move); document.removeEventListener('touchend', end) }
          document.addEventListener('touchmove', move, { passive: false })
          document.addEventListener('touchend', end)
        }}
      >
        {/* Track (background arc) */}
        <path
          d={`M ${sx} ${sy} A ${r} ${r} 0 ${trackLargeArc} 1 ${fx} ${fy}`}
          fill="none"
          stroke="#1F2937"
          strokeWidth="5"
          strokeLinecap="round"
        />
        {/* Tick marks at 0%, 25%, 50%, 75%, 100% */}
        {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
          const tickAngle = startAngle + pct * (endAngle - startAngle)
          const tickRad = (tickAngle - 90) * Math.PI / 180
          const innerR = r - 4
          const outerR = r + 4
          const tx1 = cx + innerR * Math.cos(tickRad)
          const ty1 = cy + innerR * Math.sin(tickRad)
          const tx2 = cx + outerR * Math.cos(tickRad)
          const ty2 = cy + outerR * Math.sin(tickRad)
          return (
            <line
              key={pct}
              x1={tx1} y1={ty1} x2={tx2} y2={ty2}
              stroke="#374151"
              strokeWidth={pct === 0.5 ? 1.5 : 1}
              opacity={pct === 0.5 ? 0.6 : 0.35}
            />
          )
        })}
        {/* Active arc */}
        <path
          d={`M ${sx} ${sy} A ${r} ${r} 0 ${largeArc} 1 ${ex} ${ey}`}
          fill="none"
          stroke={color}
          strokeWidth="5"
          strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 4px ${color}40)` }}
        />
        {/* Thumb dot */}
        <circle cx={ex} cy={ey} r="6" fill={color} stroke="#0B1120" strokeWidth="2" style={{ filter: `drop-shadow(0 0 6px ${color}60)` }} />
        {/* Center value */}
        <text x={cx} y={cy + 2} textAnchor="middle" dominantBaseline="central"
          fontSize="14" fontWeight="700" fill="white"
          style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
          {displayValue}
        </text>
      </svg>
      <div className="flex justify-between w-full px-2 mt-1">
        <span className="text-[9px] text-gray-600">{leftLabel}</span>
        <span className="text-[9px] text-gray-600">{rightLabel}</span>
      </div>
    </div>
  )
}

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
        <label className="text-[10px] font-semibold uppercase tracking-widest text-gray-500 block mb-2.5">
          Target Environment
        </label>
        <div className="grid grid-cols-2 gap-2">
          {ENVIRONMENTS.map((env) => (
            <button
              key={env.value}
              onClick={() => setEnvironment(env.value)}
              className={`relative p-3 rounded-xl text-left transition-all duration-300 ${
                environment === env.value
                  ? 'bg-cyan-500/10 border-2 border-cyan-500/50 shadow-lg shadow-cyan-500/5 ring-1 ring-inset ring-cyan-400/10'
                  : 'bg-gray-900/50 border border-gray-800 hover:border-gray-700 hover:bg-gray-900/80 active:border-cyan-500/30 active:bg-cyan-500/5'
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

      {/* Arc dials */}
      <div className="grid grid-cols-2 gap-3">
        <ArcDial
          value={safetyLevel}
          onChange={setSafetyLevel}
          label="Safety"
          color={safetyLevel >= 0.7 ? '#34D399' : safetyLevel >= 0.4 ? '#FBBF24' : '#F87171'}
          displayValue={`${Math.round(safetyLevel * 100)}%`}
          leftLabel="Minimal"
          rightLabel="Maximum"
        />
        <ArcDial
          value={complexity}
          onChange={setComplexity}
          label="Complexity"
          color="#22D3EE"
          displayValue={complexity <= 0.33 ? 'Low' : complexity <= 0.66 ? 'Med' : 'High'}
          leftLabel="Simple"
          rightLabel="Advanced"
        />
      </div>
    </div>
  )
}
