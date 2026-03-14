import { useMemo } from 'react'

interface Props {
  mapJson: string
}

const GENE_COLORS = [
  '#2563eb', '#dc2626', '#16a34a', '#d97706', '#7c3aed',
  '#0891b2', '#e11d48', '#65a30d', '#ea580c', '#8b5cf6',
]

export default function PlasmidMap({ mapJson }: Props) {
  const figure = useMemo(() => {
    try {
      return typeof mapJson === 'string' ? JSON.parse(mapJson) : mapJson
    } catch {
      return null
    }
  }, [mapJson])

  // Extract gene info from the plotly data traces
  const genes = useMemo(() => {
    if (!figure?.data) return []
    return figure.data
      .filter((trace: any) => trace.name && trace.name !== 'Backbone' && trace.name !== 'Origin' && trace.line?.width === 12)
      .map((trace: any, i: number) => ({
        name: trace.name,
        color: trace.line?.color || GENE_COLORS[i % GENE_COLORS.length],
        startAngle: trace.theta?.[0] || i * 72,
        endAngle: trace.theta?.[trace.theta.length - 1] || (i + 1) * 72,
        hover: trace.hovertemplate?.replace(/<[^>]*>/g, '') || trace.name,
      }))
  }, [figure])

  const title = figure?.layout?.title?.text || 'Plasmid Map'
  const titleParts = title.split('<br><sub>')
  const mainTitle = titleParts[0]
  const subtitle = titleParts[1]?.replace('</sub>', '') || ''

  // SVG plasmid rendering
  const cx = 200
  const cy = 200
  const r = 140
  const geneR = 155
  const labelR = 185

  function arcPath(startDeg: number, endDeg: number, radius: number) {
    const startRad = (startDeg - 90) * Math.PI / 180
    const endRad = (endDeg - 90) * Math.PI / 180
    const x1 = cx + radius * Math.cos(startRad)
    const y1 = cy + radius * Math.sin(startRad)
    const x2 = cx + radius * Math.cos(endRad)
    const y2 = cy + radius * Math.sin(endRad)
    const largeArc = endDeg - startDeg > 180 ? 1 : 0
    return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`
  }

  function labelPos(startDeg: number, endDeg: number, radius: number) {
    const midDeg = (startDeg + endDeg) / 2
    const midRad = (midDeg - 90) * Math.PI / 180
    return {
      x: cx + radius * Math.cos(midRad),
      y: cy + radius * Math.sin(midRad),
      anchor: midDeg > 90 && midDeg < 270 ? 'end' : 'start',
    }
  }

  return (
    <div className="bg-white rounded-xl border p-4">
      <svg viewBox="0 0 400 400" className="w-full max-w-md mx-auto" style={{ maxHeight: 400 }}>
        {/* Backbone circle */}
        <circle cx={cx} cy={cy} r={r} fill="none" stroke="#d1d5db" strokeWidth="3" />

        {/* Gene arcs */}
        {genes.map((gene: any, i: number) => {
          const label = labelPos(gene.startAngle, gene.endAngle, labelR)
          return (
            <g key={i}>
              <path
                d={arcPath(gene.startAngle, gene.endAngle, geneR)}
                fill="none"
                stroke={gene.color}
                strokeWidth="14"
                strokeLinecap="round"
              >
                <title>{gene.hover}</title>
              </path>
              <text
                x={label.x}
                y={label.y}
                textAnchor={label.anchor as any}
                dominantBaseline="central"
                fontSize="11"
                fontWeight="600"
                fill={gene.color}
              >
                {gene.name}
              </text>
            </g>
          )
        })}

        {/* Origin of replication */}
        <g>
          <rect x={cx - 8} y={cy + r - 4} width="16" height="8" rx="2" fill="#000" />
          <text x={cx} y={cy + r + 18} textAnchor="middle" fontSize="9" fill="#666">ori</text>
        </g>

        {/* Center label */}
        <text x={cx} y={cy - 8} textAnchor="middle" fontSize="13" fontWeight="700" fill="#1a1a1a">
          {mainTitle.length > 28 ? mainTitle.slice(0, 28) + '...' : mainTitle}
        </text>
        {subtitle && (
          <text x={cx} y={cy + 12} textAnchor="middle" fontSize="11" fill="#888">
            {subtitle}
          </text>
        )}
      </svg>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 justify-center mt-3">
        {genes.map((gene: any, i: number) => (
          <div key={i} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: gene.color }} />
            <span className="text-xs text-muted-foreground">{gene.name}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
