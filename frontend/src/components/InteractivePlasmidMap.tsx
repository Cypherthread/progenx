import { useState, useMemo } from 'react'

interface Feature {
  start: number
  end: number
  label: string
  type: string
  color?: string
  color_index?: number
  strand?: number
}

interface Props {
  features: Feature[]
  totalLength: number
  designName: string
  featureData?: { name: string; start: number; end: number; size_bp: number; function: string; source?: string }[]
}

const COLORS = [
  '#60A5FA', '#34D399', '#FBBF24', '#A78BFA', '#F87171',
  '#22D3EE', '#F472B6', '#A3E635', '#FB923C', '#818CF8',
]

const TYPE_COLORS: Record<string, string> = {
  promoter: '#34D399',
  terminator: '#F87171',
  kill_switch: '#EF4444',
  marker: '#FBBF24',
  ori: '#9CA3AF',
}

export default function InteractivePlasmidMap({ features, totalLength, designName, featureData }: Props) {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null)
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null)

  const cx = 250
  const cy = 250
  const baseR = 160

  function getColor(f: Feature, i: number): string {
    if (f.type === 'gene') return COLORS[(f.color_index ?? i) % COLORS.length]
    return TYPE_COLORS[f.type] || '#6B7280'
  }

  function getRadius(f: Feature): number {
    if (f.type === 'gene') return baseR + 4
    if (f.type === 'ori' || f.type === 'marker' || f.type === 'kill_switch') return baseR - 8
    return baseR - 16 // promoter, terminator
  }

  function getWidth(f: Feature): number {
    if (f.type === 'gene') return 20
    if (f.type === 'ori' || f.type === 'marker' || f.type === 'kill_switch') return 16
    return 8
  }

  function toAngle(bp: number): number {
    return (bp / totalLength) * 360
  }

  function polarToXY(r: number, angleDeg: number): [number, number] {
    const rad = ((angleDeg - 90) * Math.PI) / 180
    return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)]
  }

  function arcPath(startBp: number, endBp: number, r: number): string {
    const startDeg = toAngle(startBp)
    const endDeg = toAngle(endBp)
    const [x1, y1] = polarToXY(r, startDeg)
    const [x2, y2] = polarToXY(r, endDeg)
    const span = endDeg - startDeg
    const large = span > 180 ? 1 : 0
    return `M ${x1.toFixed(1)} ${y1.toFixed(1)} A ${r} ${r} 0 ${large} 1 ${x2.toFixed(1)} ${y2.toFixed(1)}`
  }

  const featureInfo = useMemo(() => {
    const map: Record<string, { function: string; source: string; size_bp: number }> = {}
    for (const fd of featureData || []) {
      map[fd.name] = { function: fd.function, source: fd.source || '', size_bp: fd.size_bp }
    }
    return map
  }, [featureData])

  const activeFeature = selectedIdx !== null ? features[selectedIdx] : hoveredIdx !== null ? features[hoveredIdx] : null
  const activeInfo = activeFeature ? featureInfo[activeFeature.label] : null

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-white">Construct Map</h3>
        {activeFeature && (
          <span className="text-xs text-gray-400">
            Click a feature for details
          </span>
        )}
      </div>

      <div className="relative max-w-lg mx-auto">
        <svg viewBox="0 0 500 500" className="w-full" style={{ maxHeight: 500 }}>
          {/* Glow filter */}
          <defs>
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <filter id="glowStrong" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="8" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Background ring */}
          <circle cx={cx} cy={cy} r={baseR} fill="none" stroke="#1F2937" strokeWidth="2" />

          {/* Tick marks every 1000 bp */}
          {Array.from({ length: Math.floor(totalLength / 1000) }).map((_, i) => {
            const bp = (i + 1) * 1000
            const [x1, y1] = polarToXY(baseR - 24, toAngle(bp))
            const [x2, y2] = polarToXY(baseR - 20, toAngle(bp))
            const [tx, ty] = polarToXY(baseR - 30, toAngle(bp))
            return (
              <g key={i} opacity={0.3}>
                <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#4B5563" strokeWidth="1" />
                <text x={tx} y={ty} textAnchor="middle" dominantBaseline="central" fontSize="7" fill="#4B5563">
                  {bp >= 1000 ? `${(bp / 1000).toFixed(0)}k` : bp}
                </text>
              </g>
            )
          })}

          {/* Feature arcs */}
          {features.map((f, i) => {
            const color = getColor(f, i)
            const r = getRadius(f)
            const w = getWidth(f)
            const isHovered = hoveredIdx === i
            const isSelected = selectedIdx === i
            const isActive = isHovered || isSelected
            const dimmed = (hoveredIdx !== null || selectedIdx !== null) && !isActive

            return (
              <g
                key={i}
                onMouseEnter={() => setHoveredIdx(i)}
                onMouseLeave={() => setHoveredIdx(null)}
                onClick={() => setSelectedIdx(selectedIdx === i ? null : i)}
                className="cursor-pointer"
              >
                <path
                  d={arcPath(f.start, f.end, r)}
                  fill="none"
                  stroke={color}
                  strokeWidth={isActive ? w + 4 : w}
                  strokeLinecap="round"
                  opacity={dimmed ? 0.25 : isActive ? 1 : 0.8}
                  filter={isActive ? 'url(#glowStrong)' : undefined}
                  className="transition-all duration-200"
                />

                {/* Direction arrow for genes */}
                {f.type === 'gene' && (toAngle(f.end) - toAngle(f.start)) > 8 && (() => {
                  const arrowDeg = toAngle(f.end) - 2
                  const [ax, ay] = polarToXY(r, arrowDeg)
                  const [a1x, a1y] = polarToXY(r - 7, arrowDeg - 4)
                  const [a2x, a2y] = polarToXY(r + 7, arrowDeg - 4)
                  return (
                    <polygon
                      points={`${ax.toFixed(1)},${ay.toFixed(1)} ${a1x.toFixed(1)},${a1y.toFixed(1)} ${a2x.toFixed(1)},${a2y.toFixed(1)}`}
                      fill={color}
                      opacity={dimmed ? 0.25 : 0.9}
                    />
                  )
                })()}

                {/* Label */}
                {(f.type === 'gene' || (toAngle(f.end) - toAngle(f.start)) > 10) && (() => {
                  const midDeg = (toAngle(f.start) + toAngle(f.end)) / 2
                  const labelR = f.type === 'gene' ? baseR + 38 : baseR + 30
                  const [lx, ly] = polarToXY(labelR, midDeg)
                  const anchor = midDeg > 90 && midDeg < 270 ? 'end' : 'start'

                  return (
                    <text
                      x={lx}
                      y={ly + 3}
                      textAnchor={anchor}
                      fontSize={f.type === 'gene' ? '11' : '9'}
                      fontWeight={f.type === 'gene' ? '600' : '500'}
                      fill={isActive ? '#FFFFFF' : color}
                      opacity={dimmed ? 0.3 : 1}
                      className="transition-all duration-200"
                      style={{ fontFamily: 'Inter, system-ui, sans-serif' }}
                    >
                      {f.label}
                    </text>
                  )
                })()}
              </g>
            )
          })}

          {/* Center info */}
          <circle cx={cx} cy={cy} r={50} fill="#0F172A" stroke="#1E293B" strokeWidth="1" />
          <text x={cx} y={cy - 12} textAnchor="middle" fontSize="11" fontWeight="700" fill="white"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
            {designName.length > 20 ? designName.slice(0, 20) + '...' : designName}
          </text>
          <text x={cx} y={cy + 4} textAnchor="middle" fontSize="10" fill="#06B6D4"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
            {totalLength.toLocaleString()} bp
          </text>
          <text x={cx} y={cy + 18} textAnchor="middle" fontSize="8" fill="#4B5563"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
            circular construct
          </text>
        </svg>
      </div>

      {/* Feature info panel */}
      {activeFeature && (
        <div className="mt-3 p-3 bg-gray-800/50 border border-gray-700 rounded-lg">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: getColor(activeFeature, selectedIdx ?? hoveredIdx ?? 0) }} />
            <span className="text-sm font-semibold text-white">{activeFeature.label}</span>
            <span className="text-xs text-gray-500">{activeFeature.type}</span>
          </div>
          <p className="text-xs text-gray-400">
            Position: {activeFeature.start.toLocaleString()} - {activeFeature.end.toLocaleString()} bp
            ({(activeFeature.end - activeFeature.start).toLocaleString()} bp)
          </p>
          {activeInfo && (
            <>
              {activeInfo.function && <p className="text-xs text-gray-300 mt-1">{activeInfo.function}</p>}
              {activeInfo.source && <p className="text-xs text-gray-500 mt-0.5">Source: {activeInfo.source}</p>}
            </>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="flex flex-wrap items-center justify-center gap-4 mt-3 pt-3 border-t border-gray-800">
        {[
          { label: 'Genes', color: '#60A5FA' },
          { label: 'Promoters', color: '#34D399' },
          { label: 'Terminators', color: '#F87171' },
          { label: 'Kill Switch', color: '#EF4444' },
          { label: 'Marker', color: '#FBBF24' },
          { label: 'Origin', color: '#9CA3AF' },
        ].map((item) => (
          <div key={item.label} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }} />
            <span className="text-[10px] text-gray-500">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
