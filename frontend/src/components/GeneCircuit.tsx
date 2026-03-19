import { useMemo } from 'react'

interface Props {
  circuitJson: string
}

const GENE_COLORS = [
  '#60A5FA', '#34D399', '#FBBF24', '#A78BFA', '#F87171',
  '#22D3EE', '#F472B6', '#A3E635', '#FB923C', '#818CF8',
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
    <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-5 space-y-5">
      <h3 className="text-sm font-semibold text-white">Gene Circuit</h3>

      {/* Linear construct diagram */}
      <div className="overflow-x-auto pb-2">
        <div className="flex items-center gap-1 min-w-fit py-3 px-1">
          <div className="text-[10px] text-gray-500 font-mono font-bold mr-2 px-1.5 py-0.5 bg-gray-800/60 border border-gray-700/50 rounded">5'</div>

          {circuit.genes.map((gene, i) => {
            const color = GENE_COLORS[i % GENE_COLORS.length]
            const promoter = circuit.promoters?.[i]
            return (
              <div key={i} className="flex items-center gap-1">
                {promoter && (
                  <div className="flex flex-col items-center mr-0.5" title={`Promoter: ${promoter}`}>
                    <span className="text-[8px] text-emerald-400 font-medium whitespace-nowrap mb-0.5">{promoter}</span>
                    <svg width="14" height="14" viewBox="0 0 16 16">
                      <path d="M4 12 L4 6 L12 6" fill="none" stroke="#34D399" strokeWidth="2" />
                      <path d="M9 3 L12 6 L9 9" fill="none" stroke="#34D399" strokeWidth="2" />
                    </svg>
                  </div>
                )}

                <div
                  className="relative group cursor-default"
                  title={`${gene.name}: ${gene.function}\nSource: ${gene.source_organism}`}
                >
                  <div
                    className="h-9 min-w-[72px] rounded-md flex items-center justify-center px-3"
                    style={{ backgroundColor: color + '20', border: `1.5px solid ${color}`, boxShadow: `0 1px 4px ${color}30` }}
                  >
                    <span className="text-xs font-bold tracking-wide" style={{ color }}>{gene.name}</span>
                  </div>
                  <div
                    className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-[5px] w-0 h-0"
                    style={{
                      borderTop: '6px solid transparent',
                      borderBottom: '6px solid transparent',
                      borderLeft: `6px solid ${color}`,
                    }}
                  />
                </div>

                {i < circuit.genes.length - 1 && (
                  <div className="w-3 h-px bg-gray-600 mx-0.5" />
                )}
              </div>
            )
          })}

          {circuit.terminators?.[0] && (
            <div className="flex flex-col items-center ml-1" title={`Terminator: ${circuit.terminators[0]}`}>
              <svg width="14" height="18" viewBox="0 0 16 20">
                <line x1="8" y1="18" x2="8" y2="4" stroke="#F87171" strokeWidth="2" />
                <line x1="3" y1="4" x2="13" y2="4" stroke="#F87171" strokeWidth="2" />
              </svg>
              <span className="text-[8px] text-red-400 font-medium mt-0.5">{circuit.terminators[0]}</span>
            </div>
          )}

          <div className="text-[10px] text-gray-500 font-mono font-bold ml-2 px-1.5 py-0.5 bg-gray-800/60 border border-gray-700/50 rounded">3'</div>
        </div>
      </div>

      {/* Gene details */}
      <div className="space-y-3">
        {circuit.genes.map((gene, i) => {
          const color = GENE_COLORS[i % GENE_COLORS.length]
          return (
            <div key={i} className="flex items-start gap-3 pl-3 py-1" style={{ borderLeft: `2px solid ${color}` }}>
              <div
                className="w-2.5 h-2.5 rounded-sm mt-1.5 shrink-0"
                style={{ backgroundColor: color }}
              />
              <div className="min-w-0">
                <span className="text-sm font-semibold text-white">{gene.name}</span>
                <span className="text-sm text-gray-400">: {gene.function}</span>
                <p className="text-xs text-gray-500 mt-0.5">
                  Source: <em className="text-gray-400">{gene.source_organism}</em>
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Regulatory elements */}
      {circuit.regulatory_elements?.length > 0 && (
        <div className="pt-3 border-t border-gray-800">
          <p className="text-xs font-medium text-gray-500 mb-2">Regulatory Elements</p>
          <div className="flex flex-wrap gap-1.5">
            {circuit.regulatory_elements.map((el, i) => (
              <span key={i} className="text-xs px-2.5 py-1 bg-gray-800 text-gray-300 rounded-md border border-gray-700">{el}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
