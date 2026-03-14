"""
LLM orchestration layer (v2).

Pipeline:
1. Claude designs the gene circuit (real gene names, chassis, pathway logic)
2. NCBI Entrez fetches actual CDS sequences for each gene
3. Codon optimizer adapts sequences for the chassis organism
4. COBRApy runs FBA for realistic yield predictions
5. Assembly planner generates ori, marker, kill switch, cloning strategy
6. Plasmid visualizer renders accurate construct map
7. Safety scorer evaluates the complete design
"""

import json
import anthropic

from config import settings
from services.ncbi_client import fetch_genes_batch
from services.codon_optimizer import optimize_protein_to_dna
from services.fba_engine import run_fba
from services.assembly_planner import plan_assembly
from services.plasmid_visualizer import generate_plasmid_map
from services.bio_engine import analyze_sequence, generate_fasta

SYSTEM_PROMPT = """You are ProtoForge's bioengineering AI. You design gene circuits based on user prompts.

VALUE PROPOSITION: {tagline}

Return ONLY valid JSON (no markdown fences) with these exact keys:
- design_name: Catchy name for this organism/construct
- organism_summary: 2-3 paragraph plain-English explanation accessible to non-experts
- host_organism: Chassis organism (e.g., "Escherichia coli K-12", "Pseudomonas putida KT2440", "Synechococcus elongatus PCC 7942")
- gene_circuit: Object with:
  - genes: list of objects with "name" (standard gene symbol, lowercase), "function" (one line), "source_organism" (full species name)
  - promoters: list of promoter names (real: Ptac, PlacUV5, psbA2, etc.)
  - terminators: list of terminator names (real: rrnB T1, etc.)
  - regulatory_elements: list (real iGEM parts: BBa_B0034, etc.)
- pathway_genes: list of gene name strings (must match gene_circuit.genes[].name exactly)
- target_product: the main metabolic product name (e.g., "PHA bioplastic", "ammonia", "ethanol")
- metabolic_products: list of all products
- safety_considerations: key biosafety notes
- refinement_notes: suggestions for improvement

CRITICAL RULES:
1. Use ONLY real genes from published literature. Every gene name must be findable in NCBI/UniProt.
2. Gene names must be standard symbols: petase, mhetase, phaA, phaB, phaC, rbcL, nifH, alkB, etc.
3. Choose chassis organisms that are real and appropriate for the environment.
4. Include realistic regulatory elements from iGEM registry or published literature.
5. Be honest about limitations — if 10x improvement is unrealistic, say so.
6. Do NOT invent gene names. If unsure, use well-characterized alternatives.

Environment: {environment}
Safety level (0-1): {safety_level}
Complexity (0-1): {complexity}
"""


def generate_design(
    prompt: str,
    environment: str = "ocean",
    safety_level: float = 0.7,
    complexity: float = 0.5,
) -> dict:
    """Full design pipeline: LLM → NCBI → codon opt → FBA → assembly → visualization."""

    # Step 1: Claude designs the gene circuit
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    system = SYSTEM_PROMPT.format(
        tagline=settings.TAGLINE,
        environment=environment,
        safety_level=safety_level,
        complexity=complexity,
    )

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=system,
        messages=[
            {"role": "user", "content": f"Design request: {prompt}\n\nReturn ONLY valid JSON."}
        ],
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:-3].strip()

    design = json.loads(raw)

    chassis = design.get("host_organism", "Escherichia coli K-12")
    gene_circuit = design.get("gene_circuit", {})
    genes = gene_circuit.get("genes", [])
    pathway_gene_names = [g["name"] for g in genes]

    # Step 2: Fetch real sequences from NCBI
    ncbi_results = fetch_genes_batch(pathway_gene_names)

    gene_sequences = {}
    codon_optimized = {}
    total_construct_bp = 0

    for gene in genes:
        name = gene["name"]
        ncbi = ncbi_results.get(name, {})
        seq = ncbi.get("sequence", "")

        gene_sequences[name] = {
            "raw_sequence": seq,
            "accession": ncbi.get("accession", ""),
            "length": ncbi.get("length", 0),
            "source": ncbi.get("source", "not_found"),
            "type": ncbi.get("type", "unknown"),
            "description": ncbi.get("description", ncbi.get("function", "")),
        }

        # Codon optimize if we got a protein sequence
        if seq and ncbi.get("type") == "protein":
            opt = optimize_protein_to_dna(seq, chassis)
            codon_optimized[name] = opt
            gene["size_bp"] = opt["length_bp"]
            total_construct_bp += opt["length_bp"]
        elif seq and ncbi.get("type") == "nucleotide":
            gene["size_bp"] = len(seq)
            total_construct_bp += len(seq)
            codon_optimized[name] = {
                "optimized_dna": seq,
                "length_bp": len(seq),
                "chassis": chassis,
                "cai_score": None,
                "gc_content": round((seq.count("G") + seq.count("C")) / max(len(seq), 1), 3),
                "note": "Native nucleotide sequence (not codon-optimized)",
            }
        else:
            gene["size_bp"] = 900  # estimate

    # Step 3: Run FBA
    fba_results = run_fba(
        chassis=chassis,
        pathway_genes=pathway_gene_names,
        target_product=design.get("target_product", ""),
        environment=environment,
    )

    # Step 4: Assembly planning
    assembly = plan_assembly(
        genes=genes,
        chassis=chassis,
        environment=environment,
        total_construct_bp=total_construct_bp,
    )

    # Step 5: Generate plasmid map
    plasmid = generate_plasmid_map(
        genes=genes,
        promoters=gene_circuit.get("promoters", []),
        terminators=gene_circuit.get("terminators", []),
        ori=assembly["origin_of_replication"],
        marker=assembly["selection_marker"],
        kill_switch=assembly["kill_switch"],
        total_length=assembly["estimated_total_size_bp"],
        design_name=design.get("design_name", "pProtoForge"),
    )

    # Step 6: Build combined FASTA
    fasta_parts = []
    for name, opt in codon_optimized.items():
        dna = opt.get("optimized_dna", "")
        if dna:
            fasta_parts.append(f">{name}_codon_optimized_{chassis.replace(' ', '_')}\n")
            for j in range(0, len(dna), 60):
                fasta_parts.append(dna[j:j+60] + "\n")
            fasta_parts.append("\n")

    fasta_content = "".join(fasta_parts)

    # Build full construct sequence for analysis
    full_sequence = "".join(opt.get("optimized_dna", "") for opt in codon_optimized.values())
    if full_sequence:
        seq_analysis = analyze_sequence(full_sequence)
    else:
        seq_analysis = {}

    # Compile yield string
    if fba_results.get("source") == "cobra_fba":
        yield_str = (
            f"Growth: {fba_results['adjusted_growth_rate']} h⁻¹ | "
            f"Titer: ~{fba_results['estimated_titer_g_per_L']} g/L | "
            f"Model: {fba_results['model_used']}"
        )
    else:
        yield_str = fba_results.get("summary", "N/A")

    return {
        "design_name": design.get("design_name", "Untitled"),
        "organism_summary": design.get("organism_summary", ""),
        "host_organism": chassis,
        "gene_circuit": gene_circuit,
        "gene_sequences": gene_sequences,
        "codon_optimized": codon_optimized,
        "dna_sequence": full_sequence,
        "fasta_content": fasta_content,
        "plasmid_map": plasmid,
        "fba_results": fba_results,
        "assembly_plan": assembly,
        "safety_considerations": design.get("safety_considerations", ""),
        "simulated_yield": yield_str,
        "estimated_cost": _estimate_cost(total_construct_bp),
        "target_product": design.get("target_product", ""),
        "refinement_notes": design.get("refinement_notes", ""),
        "model_used": "claude-sonnet-4 + ncbi + cobra",
        "sequence_analysis": seq_analysis,
        "disclaimer": settings.DISCLAIMER,
    }


def _estimate_cost(total_bp: int) -> str:
    """Estimate DNA synthesis cost based on bp."""
    if total_bp <= 0:
        return "Contact vendor for quote"
    # Typical gene synthesis: $0.07-0.15/bp (2026 pricing)
    low = total_bp * 0.07
    high = total_bp * 0.15
    return f"${low:,.0f} - ${high:,.0f} (gene synthesis at $0.07-0.15/bp)"


REFINE_SYSTEM = """You are ProtoForge's refinement assistant. The user has an existing design and wants changes.

Return valid JSON with the same structure as the original, plus "refinement_summary" explaining changes.
Only modify what the user asked for. Preserve working elements. Use real gene names only."""


def refine_design(
    original_design: dict,
    refinement_request: str,
    conversation_history: list[dict],
) -> dict:
    """Refine an existing design via Claude + re-run pipeline."""
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    messages = [{"role": m["role"], "content": m["content"]} for m in conversation_history[-10:]]
    messages.append({
        "role": "user",
        "content": (
            f"Current design:\n{json.dumps(original_design, indent=2, default=str)}\n\n"
            f"Refinement: {refinement_request}\n\nReturn ONLY valid JSON."
        ),
    })

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=REFINE_SYSTEM,
        messages=messages,
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        if raw.endswith("```"):
            raw = raw[:-3].strip()

    refined = json.loads(raw)

    # Re-run the same pipeline with refined genes
    chassis = refined.get("host_organism", original_design.get("host_organism", "E. coli"))
    gene_circuit = refined.get("gene_circuit", {})
    genes = gene_circuit.get("genes", [])
    pathway_gene_names = [g["name"] for g in genes]

    ncbi_results = fetch_genes_batch(pathway_gene_names)
    codon_optimized = {}
    total_bp = 0

    for gene in genes:
        name = gene["name"]
        ncbi = ncbi_results.get(name, {})
        seq = ncbi.get("sequence", "")
        if seq and ncbi.get("type") == "protein":
            opt = optimize_protein_to_dna(seq, chassis)
            codon_optimized[name] = opt
            gene["size_bp"] = opt["length_bp"]
            total_bp += opt["length_bp"]
        else:
            gene["size_bp"] = 900
            total_bp += 900

    fba_results = run_fba(chassis, pathway_gene_names, refined.get("target_product", ""), original_design.get("environment", "lab"))

    assembly = plan_assembly(genes, chassis, original_design.get("environment", "lab"), total_bp)

    plasmid = generate_plasmid_map(
        genes=genes,
        promoters=gene_circuit.get("promoters", []),
        terminators=gene_circuit.get("terminators", []),
        ori=assembly["origin_of_replication"],
        marker=assembly["selection_marker"],
        kill_switch=assembly["kill_switch"],
        total_length=assembly["estimated_total_size_bp"],
        design_name=refined.get("design_name", "Refined"),
    )

    full_sequence = "".join(opt.get("optimized_dna", "") for opt in codon_optimized.values())
    fasta_parts = []
    for name, opt in codon_optimized.items():
        dna = opt.get("optimized_dna", "")
        if dna:
            fasta_parts.append(f">{name}_optimized\n")
            for j in range(0, len(dna), 60):
                fasta_parts.append(dna[j:j + 60] + "\n")

    return {
        "design_name": refined.get("design_name", original_design.get("design_name", "")),
        "organism_summary": refined.get("organism_summary", ""),
        "host_organism": chassis,
        "gene_circuit": gene_circuit,
        "gene_sequences": {n: ncbi_results.get(n, {}) for n in pathway_gene_names},
        "codon_optimized": codon_optimized,
        "dna_sequence": full_sequence,
        "fasta_content": "".join(fasta_parts),
        "plasmid_map": plasmid,
        "fba_results": fba_results,
        "assembly_plan": assembly,
        "simulated_yield": fba_results.get("summary", ""),
        "estimated_cost": _estimate_cost(total_bp),
        "refinement_summary": refined.get("refinement_summary", "Design updated."),
        "model_used": "claude-sonnet-4 + ncbi + cobra",
        "disclaimer": settings.DISCLAIMER,
    }
