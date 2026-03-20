import { useState, useMemo, useCallback, useRef } from 'react'

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
  const [tooltipPos, setTooltipPos] = useState<{ x: number; y: number } | null>(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const isPanning = useRef(false)
  const panStart = useRef({ x: 0, y: 0, panX: 0, panY: 0 })

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect()
    setTooltipPos({ x: e.clientX - rect.left, y: e.clientY - rect.top })
    if (isPanning.current) {
      const dx = e.clientX - panStart.current.x
      const dy = e.clientY - panStart.current.y
      setPan({ x: panStart.current.panX + dx / zoom, y: panStart.current.panY + dy / zoom })
    }
  }, [zoom])

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault()
    setZoom(prev => Math.max(0.5, Math.min(4, prev - e.deltaY * 0.002)))
  }, [])

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 0) {
      isPanning.current = true
      panStart.current = { x: e.clientX, y: e.clientY, panX: pan.x, panY: pan.y }
    }
  }, [pan])

  const handleMouseUp = useCallback(() => {
    isPanning.current = false
  }, [])

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
    let endDeg = toAngle(endBp)
    // Enforce minimum arc span so small features render as curves, not squares
    const minSpan = 12
    if (endDeg - startDeg < minSpan) {
      endDeg = startDeg + minSpan
    }
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
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-white">Construct Map</h3>
          <p className="text-[10px] text-gray-600 mt-0.5">Click any feature to inspect. {totalLength.toLocaleString()} bp circular.</p>
        </div>
        {activeFeature && (
          <span className="text-[10px] px-2 py-1 bg-cyan-500/10 text-cyan-400 rounded-md">
            {activeFeature.label} selected
          </span>
        )}
      </div>

      <div
        className="relative mx-auto max-w-full overflow-hidden rounded-lg"
        style={{ maxWidth: 460, cursor: isPanning.current ? 'grabbing' : zoom > 1 ? 'grab' : 'default' }}
        onMouseMove={handleMouseMove}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={() => { isPanning.current = false }}
      >
        {/* Zoom controls */}
        <div className="absolute top-2 right-2 z-10 flex flex-col gap-1">
          <button onClick={() => setZoom(prev => Math.min(4, prev + 0.3))} className="w-7 h-7 flex items-center justify-center bg-gray-800/80 border border-gray-700/50 rounded-md text-gray-400 hover:text-white hover:bg-gray-700/80 text-sm font-bold transition-colors">+</button>
          <button onClick={() => setZoom(prev => Math.max(0.5, prev - 0.3))} className="w-7 h-7 flex items-center justify-center bg-gray-800/80 border border-gray-700/50 rounded-md text-gray-400 hover:text-white hover:bg-gray-700/80 text-sm font-bold transition-colors">-</button>
          {zoom !== 1 && <button onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }) }} className="w-7 h-7 flex items-center justify-center bg-gray-800/80 border border-gray-700/50 rounded-md text-gray-500 hover:text-white hover:bg-gray-700/80 text-[9px] transition-colors">1:1</button>}
        </div>
        {/* Floating tooltip for hovered feature */}
        {hoveredIdx !== null && tooltipPos && (
          <div
            className="absolute z-10 pointer-events-none px-2.5 py-1.5 bg-gray-900/95 border border-gray-700 rounded-lg shadow-lg text-xs text-white font-medium whitespace-nowrap transition-opacity duration-150"
            style={{ left: tooltipPos.x + 12, top: tooltipPos.y - 8, transform: 'translateY(-100%)' }}
          >
            {features[hoveredIdx].label}
            <span className="text-gray-500 ml-1.5">{features[hoveredIdx].type}</span>
          </div>
        )}
        <svg
          viewBox={`${-30 - pan.x * zoom} ${-10 - pan.y * zoom} ${560 / zoom} ${520 / zoom}`}
          className="w-full transition-[viewBox] duration-100"
        >
          {/* Glow filter */}
          <defs>
            <filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <filter id="glowStrong" x="-200%" y="-200%" width="500%" height="500%">
              <feGaussianBlur stdDeviation="6" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Background ring with subtle double track */}
          <circle cx={cx} cy={cy} r={baseR} fill="none" stroke="#111827" strokeWidth="24" opacity="0.3" />
          <circle cx={cx} cy={cy} r={baseR} fill="none" stroke="#1F2937" strokeWidth="2" />

          {/* Origin marker (0 bp = top) */}
          {(() => {
            const [ox, oy] = polarToXY(baseR, 0)
            return <circle cx={ox} cy={oy} r="3" fill="#4B5563" />
          })()}

          {/* Tick marks: minor every 500bp, major every 1000bp */}
          {Array.from({ length: Math.floor(totalLength / 500) }).map((_, i) => {
            const bp = (i + 1) * 500
            const isMajor = bp % 1000 === 0
            const innerR = isMajor ? baseR - 26 : baseR - 22
            const outerR = baseR - 18
            const [x1, y1] = polarToXY(innerR, toAngle(bp))
            const [x2, y2] = polarToXY(outerR, toAngle(bp))
            return (
              <g key={i}>
                <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#374151" strokeWidth={isMajor ? 1.5 : 0.5} opacity={isMajor ? 0.5 : 0.25} />
                {isMajor && (() => {
                  const [tx, ty] = polarToXY(baseR - 32, toAngle(bp))
                  return (
                    <text x={tx} y={ty} textAnchor="middle" dominantBaseline="central" fontSize="7" fill="#4B5563"
                      style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
                      {(bp / 1000).toFixed(0)}k
                    </text>
                  )
                })()}
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
                  className="transition-all duration-300 ease-out"
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

          {/* Center info with gradient background and subtle glow */}
          <circle cx={cx} cy={cy} r={70} fill="url(#centerGlow)" opacity="0.4" />
          <circle cx={cx} cy={cy} r={52} fill="url(#centerGradient)" />
          <circle cx={cx} cy={cy} r={52} fill="none" stroke="#1E293B" strokeWidth="1" />
          <defs>
            <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#06B6D4" stopOpacity="0.12" />
              <stop offset="70%" stopColor="#06B6D4" stopOpacity="0.03" />
              <stop offset="100%" stopColor="#06B6D4" stopOpacity="0" />
            </radialGradient>
            <radialGradient id="centerGradient" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#111827" />
              <stop offset="100%" stopColor="#0B1120" />
            </radialGradient>
          </defs>
          <text x={cx} y={cy - 14} textAnchor="middle" fontSize="10" fontWeight="700" fill="white"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
            {designName.length > 18 ? designName.slice(0, 18) + '...' : designName}
          </text>
          <text x={cx} y={cy + 2} textAnchor="middle" fontSize="13" fontWeight="800" fill="#06B6D4"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
            {totalLength.toLocaleString()}
          </text>
          <text x={cx} y={cy + 16} textAnchor="middle" fontSize="8" fill="#4B5563"
            style={{ fontFamily: 'Inter, system-ui, sans-serif' }}>
            base pairs
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
      <div className="flex flex-wrap items-center justify-center gap-2 mt-3 pt-3 border-t border-gray-800">
        {[
          { label: 'Genes', color: '#60A5FA' },
          { label: 'Promoters', color: '#34D399' },
          { label: 'Terminators', color: '#F87171' },
          { label: 'Kill Switch', color: '#EF4444' },
          { label: 'Marker', color: '#FBBF24' },
          { label: 'Origin', color: '#9CA3AF' },
        ].map((item) => (
          <span
            key={item.label}
            className="inline-flex items-center gap-1.5 text-[10px] text-gray-400 px-2 py-0.5 rounded-full border"
            style={{ borderColor: item.color + '30', backgroundColor: item.color + '08' }}
          >
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: item.color }} />
            {item.label}
          </span>
        ))}
      </div>
    </div>
  )
}
