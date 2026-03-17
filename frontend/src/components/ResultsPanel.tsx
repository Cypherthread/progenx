import type { DesignResponse } from '@/lib/api'
import GeneCircuit from './GeneCircuit'
import ShareButton from './ShareButton'

interface Props {
  design: DesignResponse
}

export default function ResultsPanel({ design }: Props) {
  function downloadFasta() {
    const blob = new Blob([design.fasta_content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${design.design_name.replace(/\s+/g, '_')}.fasta`
    a.click()
    URL.revokeObjectURL(url)
  }

  function downloadGenBank() {
    if (!design.genbank_content) return
    const blob = new Blob([design.genbank_content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${design.design_name.replace(/\s+/g, '_')}.gb`
    a.click()
    URL.revokeObjectURL(url)
  }

  function safetyColor(score: number) {
    if (score >= 0.8) return 'text-green-600 bg-green-50 border-green-200'
    if (score >= 0.5) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const fba = design.fba_results || {} as any
  const assembly = design.assembly_plan || {} as any
  const geneSeqs = design.gene_sequences || {}
  const codonOpt = design.codon_optimized || {}
  const plasmid = design.plasmid_map_data || {} as any

  return (
    <div className="space-y-5">
      {/* Disclaimer Banner */}
      <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg px-4 py-2.5 text-xs text-amber-300 font-medium">
        {design.disclaimer || 'EDUCATIONAL/EXPERIMENTAL ONLY — NOT LAB-READY WITHOUT EXPERT REVIEW'}
      </div>

      {/* Conceptual Design Banner */}
      {design.conceptual_banner && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 text-sm text-red-300 font-semibold">
          {design.conceptual_banner}
        </div>
      )}

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold">{design.design_name}</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {design.host_organism} | {design.generation_time_sec}s | {design.model_used}
          </p>
        </div>
        <ShareButton designId={design.id} designName={design.design_name} generationTime={design.generation_time_sec} />
      </div>

      {/* Summary */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
        <h3 className="text-sm font-medium mb-2">Organism Summary</h3>
        <p className="text-sm text-muted-foreground whitespace-pre-wrap">{design.organism_summary}</p>
      </div>

      {/* Safety Score */}
      <div className={`rounded-xl p-4 border ${safetyColor(design.safety_score)}`}>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium">Safety Score</h3>
          <span className="text-lg font-bold">{Math.round(design.safety_score * 100)}%</span>
        </div>
        <p className="text-sm mb-2">{design.dual_use_assessment}</p>
        {design.safety_flags.length > 0 && (
          <ul className="text-xs space-y-1 mt-2">
            {design.safety_flags.map((flag, i) => (
              <li key={i} className="flex items-start gap-1">
                <span className="mt-0.5">&#9888;</span><span>{flag}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Gene Circuit (visual) */}
      <GeneCircuit circuitJson={JSON.stringify(design.gene_circuit)} />

      {/* NCBI Sequence Provenance */}
      {Object.keys(geneSeqs).length > 0 && (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
          <h3 className="text-sm font-medium mb-3">Gene Sequences (NCBI)</h3>
          <div className="space-y-2">
            {Object.entries(geneSeqs).map(([name, data]: [string, any]) => (
              <div key={name} className="flex items-start justify-between text-sm border-b last:border-0 pb-2 last:pb-0">
                <div>
                  <span className="font-medium">{name}</span>
                  <span className="text-muted-foreground text-xs ml-2">
                    {data.accession && `[${data.accession}]`}
                  </span>
                  <p className="text-xs text-muted-foreground">{data.description || data.function || ''}</p>
                </div>
                <div className="text-right shrink-0 ml-3">
                  <span className={`text-xs px-1.5 py-0.5 rounded ${
                    data.source === 'ncbi_registry' ? 'bg-green-100 text-green-700' :
                    data.source === 'ncbi_search' ? 'bg-blue-100 text-blue-700' :
                    data.source === 'unsupported_biology' ? 'bg-red-100 text-red-700' :
                    data.conceptual_only ? 'bg-orange-100 text-orange-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {data.source === 'ncbi_registry' ? 'Verified' :
                     data.source === 'ncbi_search' ? 'NCBI search' :
                     data.source === 'unsupported_biology' ? 'No known parts' :
                     data.conceptual_only ? 'Conceptual only' : 'pending'}
                  </span>
                  {data.length > 0 && <p className="text-xs text-muted-foreground mt-0.5">{data.length} {data.type === 'protein' ? 'aa' : 'bp'}</p>}
                  {data.confidence && data.confidence !== 'unknown' && (
                    <span className={`text-[10px] px-1 py-0.5 rounded mt-0.5 inline-block ${
                      data.confidence === 'high' ? 'bg-green-50 text-green-700' :
                      data.confidence === 'medium' ? 'bg-blue-50 text-blue-700' :
                      data.confidence === 'low' ? 'bg-yellow-50 text-yellow-700' :
                      'bg-red-50 text-red-700'
                    }`} title={data.confidence_reason || ''}>
                      {data.confidence} confidence
                    </span>
                  )}
                  {data.function_validation && !data.function_validation.match && (
                    <p className="text-[10px] text-red-600 mt-0.5">Function mismatch ({(data.function_validation.score * 100).toFixed(0)}%)</p>
                  )}
                </div>
                {data.warning && (
                  <p className="text-xs text-red-400 mt-1 w-full">{data.warning}</p>
                )}
                {data.variant_predictions?.beneficial_mutations?.length > 0 && (
                  <div className="w-full mt-1.5 pt-1.5 border-t border-gray-100">
                    <p className="text-[10px] text-emerald-700 font-medium mb-0.5">
                      ESM-2 predicted improvements ({data.variant_predictions.total_beneficial} found):
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {data.variant_predictions.beneficial_mutations.slice(0, 5).map((m: any) => (
                        <span key={m.notation} className="text-[10px] px-1.5 py-0.5 bg-emerald-50 text-emerald-700 rounded font-mono" title={`Score: +${m.score}`}>
                          {m.notation}
                        </span>
                      ))}
                      {data.variant_predictions.beneficial_mutations.length > 5 && (
                        <span className="text-[10px] text-gray-400">
                          +{data.variant_predictions.beneficial_mutations.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Codon Optimization */}
      {Object.keys(codonOpt).length > 0 && (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
          <h3 className="text-sm font-medium mb-3">Codon-Optimized Sequences</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-3">
            {Object.entries(codonOpt).map(([name, data]: [string, any]) => (
              <div key={name} className="bg-gray-800/50 rounded-lg p-2 text-center">
                <p className="text-xs font-medium">{name}</p>
                <p className="text-sm font-bold">{data.length_bp?.toLocaleString()} bp</p>
                {data.cai_score != null && <p className="text-[10px] text-muted-foreground">CAI: {data.cai_score}</p>}
                <p className="text-[10px] text-muted-foreground">GC: {((data.gc_content || 0) * 100).toFixed(1)}%</p>
              </div>
            ))}
          </div>
          <p className="text-xs text-muted-foreground">Optimized for {design.host_organism}</p>
        </div>
      )}

      {/* Plasmid Map */}
      {plasmid.png_base64 && (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
          <h3 className="text-sm font-medium mb-2">Construct Map</h3>
          <img
            src={`data:image/${plasmid.png_base64.startsWith('PHN2') ? 'svg+xml' : 'png'};base64,${plasmid.png_base64}`}
            alt="Plasmid map"
            className="w-full max-w-lg mx-auto"
          />
          {plasmid.total_length_bp && (
            <p className="text-xs text-muted-foreground text-center mt-2">{plasmid.total_length_bp.toLocaleString()} bp total</p>
          )}
        </div>
      )}

      {/* FBA Results */}
      {fba.summary && (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
          <h3 className="text-sm font-medium mb-3">
            Flux Balance Analysis
            {fba.source === 'cobra_fba' && <span className="text-xs ml-2 px-1.5 py-0.5 bg-green-100 text-green-700 rounded">COBRApy</span>}
            {fba.source === 'heuristic_fallback' && <span className="text-xs ml-2 px-1.5 py-0.5 bg-yellow-100 text-yellow-700 rounded">Heuristic</span>}
          </h3>
          {fba.source !== 'no_model' ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
            <Metric label="WT Growth" value={fba.wild_type_growth_rate != null ? `${fba.wild_type_growth_rate} h⁻¹` : 'N/A'} />
            <Metric label="With Burden" value={fba.burdened_growth_rate != null ? `${fba.burdened_growth_rate} h⁻¹` : 'N/A'} />
            <Metric label="Growth Hit" value={fba.growth_reduction_pct != null ? `-${fba.growth_reduction_pct}%` : 'N/A'} />
            <Metric label="Max Titer (theoretical)" value={fba.estimated_titer_g_per_L != null ? `${fba.estimated_titer_g_per_L} g/L` : 'N/A'} />
          </div>
          ) : (
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 mb-3">
            <p className="text-sm text-amber-300 font-medium">No metabolic model available for this chassis organism.</p>
            <p className="text-xs text-amber-400 mt-1">FBA predictions require a genome-scale model. Supported: E. coli (iJO1366), P. putida (iJN1463).</p>
          </div>
          )}
          {fba.model_used && fba.model_used !== 'heuristic_fallback' && (
            <p className="text-xs text-muted-foreground">
              Model: {fba.model_used} ({fba.model_genes} genes, {fba.model_reactions} reactions) |
              Burden: {fba.metabolic_burden_estimate} | {fba.heterologous_genes} heterologous genes
            </p>
          )}
          <pre className="text-xs font-mono bg-gray-800/50 p-3 rounded-lg mt-2 whitespace-pre-wrap">{fba.summary}</pre>
        </div>
      )}

      {/* Assembly Plan */}
      {assembly.summary && (
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
          <h3 className="text-sm font-medium mb-3">Assembly Plan</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
            {assembly.origin_of_replication && (
              <div className="bg-gray-800/50 rounded-lg p-3">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Origin</p>
                <p className="text-sm font-medium">{assembly.origin_of_replication.name}</p>
                <p className="text-xs text-muted-foreground">{assembly.origin_of_replication.copy_number}</p>
                <p className="text-xs text-muted-foreground mt-1">{assembly.origin_of_replication.rationale}</p>
              </div>
            )}
            {assembly.selection_marker && (
              <div className="bg-gray-800/50 rounded-lg p-3">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Selection</p>
                <p className="text-sm font-medium">{assembly.selection_marker.name}</p>
                <p className="text-xs text-muted-foreground mt-1">{assembly.selection_marker.rationale}</p>
              </div>
            )}
            {assembly.assembly_method && (
              <div className="bg-gray-800/50 rounded-lg p-3">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Assembly</p>
                <p className="text-sm font-medium">{assembly.assembly_method.name}</p>
                <p className="text-xs text-muted-foreground">{assembly.assembly_method.description}</p>
                {assembly.assembly_method.steps && (
                  <ol className="text-xs text-muted-foreground mt-1 list-decimal list-inside space-y-0.5">
                    {assembly.assembly_method.steps.map((s: string, i: number) => <li key={i}>{s}</li>)}
                  </ol>
                )}
              </div>
            )}
            {assembly.kill_switch && (
              <div className="bg-red-500/10 rounded-lg p-3 border border-red-500/30">
                <p className="text-xs font-semibold uppercase tracking-wider text-red-400">Biocontainment</p>
                <p className="text-sm font-medium text-red-300">{assembly.kill_switch.name}</p>
                <p className="text-xs text-red-400 mt-1">{assembly.kill_switch.mechanism}</p>
              </div>
            )}
          </div>
          {assembly.rbs_notes && (
            <div className="text-xs text-muted-foreground mt-2">
              <strong>RBS:</strong> {assembly.rbs_notes.strategy}
              <br /><em>{assembly.rbs_notes.tool_note}</em>
            </div>
          )}
          {(assembly.primers?.length ?? 0) > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-100">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Suggested Primers</p>
              <div className="space-y-1.5">
                {assembly.primers!.map((p: any) => (
                  <div key={p.gene} className="bg-gray-800/50 rounded-lg p-2">
                    <p className="text-xs font-medium mb-1">{p.gene}</p>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <p className="text-[10px] text-muted-foreground">Forward (Tm {p.forward?.tm}°C)</p>
                        <p className="text-[10px] font-mono break-all">{p.forward?.sequence}</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-muted-foreground">Reverse (Tm {p.reverse?.tm}°C)</p>
                        <p className="text-[10px] font-mono break-all">{p.reverse?.sequence}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <p className="text-[10px] text-muted-foreground mt-1">
                SantaLucia (1998) nearest-neighbor model. 500 nM primer, 50 mM Na+. Verify with NEB Tm Calculator before ordering.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Metric label="Simulated Yield" value={design.simulated_yield} />
        <Metric label="Synthesis Cost" value={design.estimated_cost} />
        <Metric label="Construct Size" value={`${design.dna_sequence.length.toLocaleString()} bp`} />
        <Metric label="Target Product" value={design.target_product || 'N/A'} />
      </div>

      {/* DNA Sequence + FASTA download */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium">Codon-Optimized Construct Sequence</h3>
          <div className="flex gap-2">
            <button onClick={downloadFasta} className="px-3 py-1.5 bg-primary text-white rounded-md text-xs font-medium hover:opacity-90">
              FASTA
            </button>
            {design.genbank_content && (
              <button onClick={downloadGenBank} className="px-3 py-1.5 bg-emerald-600 text-white rounded-md text-xs font-medium hover:opacity-90">
                GenBank
              </button>
            )}
            <button onClick={() => navigator.clipboard.writeText(design.dna_sequence)} className="px-3 py-1.5 border rounded-md text-xs font-medium hover:bg-secondary">
              Copy
            </button>
          </div>
        </div>
        <pre className="text-xs font-mono bg-gray-800/50 p-3 rounded-lg overflow-x-auto max-h-32">
          {design.dna_sequence.match(/.{1,80}/g)?.join('\n') || 'No sequence'}
        </pre>
      </div>

      {/* Vendor links */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-4">
        <h3 className="text-sm font-medium mb-1">Ready to Build?</h3>
        <p className="text-xs text-muted-foreground mb-3">
          Sequences undergo additional IGSC biosecurity screening before synthesis.
        </p>
        <div className="flex gap-2">
          <a href="https://www.twistbioscience.com" target="_blank" rel="noopener noreferrer"
            className="px-4 py-2 border rounded-md text-xs font-medium hover:bg-white">Twist Bioscience</a>
          <a href="https://www.idtdna.com" target="_blank" rel="noopener noreferrer"
            className="px-4 py-2 border rounded-md text-xs font-medium hover:bg-white">IDT</a>
        </div>
      </div>

      {/* Disclaimer (bottom) */}
      <div className="text-xs text-muted-foreground bg-amber-500/10 border border-amber-500/30 p-3 rounded-lg">
        <strong>DISCLAIMER:</strong> {design.disclaimer}
      </div>
    </div>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-lg p-3">
      <p className="text-[10px] text-muted-foreground uppercase tracking-wider">{label}</p>
      <p className="text-sm font-medium mt-1 break-words">{value || 'N/A'}</p>
    </div>
  )
}
