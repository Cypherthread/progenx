import { useMemo } from 'react'

interface Props {
  circuitJson: string
}

const GENE_COLORS = [
  '#2563eb', '#dc2626', '#16a34a', '#d97706', '#7c3aed',
  '#0891b2', '#e11d48', '#65a30d', '#ea580c', '#8b5cf6',
]

interface Gene {
  name: string
  function: string
  source_organism: string
}

interface Circuit {
  genes: Gene[]
  promoters: string[]
  terminators: string[]
  regulatory_elements: string[]
}

export default function GeneCircuit({ circuitJson }: Props) {
  const circuit = useMemo<Circuit | null>(() => {
    try {
      const parsed = typeof circuitJson === 'string' ? JSON.parse(circuitJson) : circuitJson
      if (parsed?.genes) return parsed
      return null
    } catch {
      return null
    }
  }, [circuitJson])

  if (!circuit || !circuit.genes?.length) return null

  return (
    <div className="bg-white border rounded-xl p-4 space-y-4">
      <h3 className="text-sm font-medium">Gene Circuit</h3>

      {/* Linear construct diagram */}
      <div className="overflow-x-auto">
        <div className="flex items-center gap-0.5 min-w-fit py-2">
          {/* 5' end */}
          <div className="text-xs text-muted-foreground font-mono mr-1">5'</div>

          {circuit.genes.map((gene, i) => {
            const color = GENE_COLORS[i % GENE_COLORS.length]
            const promoter = circuit.promoters?.[i]
            return (
              <div key={i} className="flex items-center gap-0.5">
                {/* Promoter arrow */}
                {promoter && (
                  <div className="flex flex-col items-center" title={`Promoter: ${promoter}`}>
                    <span className="text-[9px] text-green-600 font-medium whitespace-nowrap">{promoter}</span>
                    <svg width="16" height="16" viewBox="0 0 16 16">
                      <path d="M4 12 L4 6 L12 6" fill="none" stroke="#16a34a" strokeWidth="2" />
                      <path d="M9 3 L12 6 L9 9" fill="none" stroke="#16a34a" strokeWidth="2" />
                    </svg>
                  </div>
                )}

                {/* Gene block */}
                <div
                  className="relative group cursor-default"
                  title={`${gene.name}: ${gene.function}\nSource: ${gene.source_organism}`}
                >
                  <div
                    className="h-10 min-w-[80px] rounded flex items-center justify-center px-2"
                    style={{ backgroundColor: color + '20', border: `2px solid ${color}` }}
                  >
                    <span className="text-xs font-semibold" style={{ color }}>{gene.name}</span>
                  </div>
                  {/* Arrow tip on right */}
                  <div
                    className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-[6px] w-0 h-0"
                    style={{
                      borderTop: '8px solid transparent',
                      borderBottom: '8px solid transparent',
                      borderLeft: `8px solid ${color}`,
                    }}
                  />
                </div>

                {/* Connector line */}
                {i < circuit.genes.length - 1 && (
                  <div className="w-4 h-0.5 bg-gray-300 mx-1" />
                )}
              </div>
            )
          })}

          {/* Terminator */}
          {circuit.terminators?.[0] && (
            <div className="flex flex-col items-center ml-1" title={`Terminator: ${circuit.terminators[0]}`}>
              <svg width="16" height="20" viewBox="0 0 16 20">
                <line x1="8" y1="18" x2="8" y2="4" stroke="#dc2626" strokeWidth="2" />
                <line x1="3" y1="4" x2="13" y2="4" stroke="#dc2626" strokeWidth="2" />
              </svg>
              <span className="text-[9px] text-red-600 font-medium">{circuit.terminators[0]}</span>
            </div>
          )}

          {/* 3' end */}
          <div className="text-xs text-muted-foreground font-mono ml-1">3'</div>
        </div>
      </div>

      {/* Gene details table */}
      <div className="space-y-2">
        {circuit.genes.map((gene, i) => (
          <div key={i} className="flex items-start gap-3 text-sm">
            <div
              className="w-3 h-3 rounded-sm mt-0.5 shrink-0"
              style={{ backgroundColor: GENE_COLORS[i % GENE_COLORS.length] }}
            />
            <div className="min-w-0">
              <span className="font-medium">{gene.name}</span>
              <span className="text-muted-foreground"> — {gene.function}</span>
              <span className="text-xs text-muted-foreground block">
                Source: <em>{gene.source_organism}</em>
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Regulatory elements */}
      {circuit.regulatory_elements?.length > 0 && (
        <div className="pt-2 border-t">
          <p className="text-xs font-medium text-muted-foreground mb-1">Regulatory Elements</p>
          <div className="flex flex-wrap gap-1.5">
            {circuit.regulatory_elements.map((el, i) => (
              <span key={i} className="text-xs px-2 py-0.5 bg-secondary rounded-full">{el}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
