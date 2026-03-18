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
import hashlib
import anthropic
from openai import OpenAI

from config import settings
from services.ncbi_client import fetch_genes_batch, lookup_gene
from services.codon_optimizer import optimize_protein_to_dna
from services.fba_engine import run_fba
from services.assembly_planner import plan_assembly
from services.plasmid_visualizer import generate_plasmid_map
from services.bio_engine import analyze_sequence, generate_fasta
from services.esm_scorer import score_variants
from services.genbank_exporter import design_to_genbank

# ── Design cache ─────────────────────────────────────────────────────
# In-memory cache keyed by (prompt_hash, environment, safety, complexity).
# Avoids redundant LLM calls for identical prompts. Survives until restart.
_design_cache: dict[str, dict] = {}
MAX_CACHE_SIZE = 500


def _cache_key(prompt: str, environment: str, safety_level: float, complexity: float) -> str:
    """Deterministic cache key for a design request."""
    raw = f"{prompt.strip().lower()}|{environment}|{safety_level:.1f}|{complexity:.1f}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _llm_call(system: str, user_msg: str, user_tier: str = "free") -> str:
    """Route LLM call: free tier -> Ollama (local, $0), pro tier -> Claude API.
    Returns raw text response from the model.
    Falls back from Ollama -> Claude if Ollama is unavailable (and vice versa)."""
    errors = []

    if user_tier in ("pro", "admin") and settings.ANTHROPIC_API_KEY:
        # Pro tier: try Claude first
        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system,
                messages=[{"role": "user", "content": user_msg}],
            )
            return response.content[0].text.strip()
        except Exception as e:
            errors.append(f"Claude: {e}")
            print(f"[LLM] Claude failed: {e}, falling back to Ollama")

    # Free tier, or Claude fallback: try Ollama
    try:
        client = OpenAI(
            base_url=settings.OLLAMA_BASE_URL,
            api_key="ollama",
            timeout=120.0,
        )
        response = client.chat.completions.create(
            model=settings.OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=4096,
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        errors.append(f"Ollama: {e}")
        print(f"[LLM] Ollama failed: {e}")

    # Both failed — try Claude as last resort (even for free tier)
    if settings.ANTHROPIC_API_KEY and "Claude" not in str(errors[0]) if errors else True:
        try:
            print("[LLM] Ollama unavailable, falling back to Claude API")
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=system,
                messages=[{"role": "user", "content": user_msg}],
            )
            return response.content[0].text.strip()
        except Exception as e:
            errors.append(f"Claude fallback: {e}")

    # Nothing works
    raise RuntimeError(
        f"No LLM available. Errors: {'; '.join(errors)}. "
        f"Ensure Ollama is running ('ollama serve') or set ANTHROPIC_API_KEY."
    )

import re as _re


def _parse_llm_json(raw: str) -> dict:
    """Robustly extract JSON from LLM output.
    Handles markdown fences, preamble text, trailing commentary,
    and other common LLM formatting issues."""
    text = raw.strip()

    # Strip markdown code fences (```json ... ``` or ``` ... ```)
    if "```" in text:
        # Find content between first ``` and last ```
        parts = text.split("```")
        for part in parts[1:]:
            # Skip the language identifier line (e.g., "json\n")
            candidate = part.strip()
            if candidate.lower().startswith("json"):
                candidate = candidate[4:].strip()
            if candidate.startswith("{"):
                text = candidate
                break

    # If still not starting with {, try to find JSON object in the text
    if not text.startswith("{"):
        # Find the first { and last } to extract embedded JSON
        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace > first_brace:
            text = text[first_brace:last_brace + 1]

    # Strip trailing ``` if still present
    if text.endswith("```"):
        text = text[:-3].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Last resort: try to fix common JSON issues
        # Remove trailing commas before } or ]
        fixed = _re.sub(r',\s*([}\]])', r'\1', text)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            raise ValueError(
                f"Could not parse LLM response as JSON. "
                f"First 200 chars: {raw[:200]!r}. Error: {e}"
            )


def _self_consistency_check(system: str, user_msg: str, user_tier: str, n_runs: int = 3) -> dict:
    """Run the same LLM prompt multiple times and measure gene selection consistency.

    How it works:
    1. Makes n_runs independent LLM calls with the same prompt
    2. Extracts the gene list from each response
    3. Counts how many runs each gene appears in
    4. Returns the most consistent design + a consistency report

    Genes appearing in 3/3 runs = high confidence (model "knows" this gene)
    Genes appearing in 1/3 runs = low confidence (model is guessing)

    Cost: n_runs × base LLM cost. For Ollama = $0. For Claude = ~$0.03.
    """
    designs = []
    gene_votes = {}  # gene_name -> count of appearances

    for i in range(n_runs):
        try:
            raw = _llm_call(system, user_msg, user_tier)
            design = _parse_llm_json(raw)
            designs.append(design)

            # Count gene votes
            genes = design.get("gene_circuit", {}).get("genes", [])
            for g in genes:
                name = g.get("name", "").lower()
                if name:
                    gene_votes[name] = gene_votes.get(name, 0) + 1
        except Exception as e:
            print(f"[CONSISTENCY] Run {i+1}/{n_runs} failed: {e}")
            continue

    if not designs:
        raise RuntimeError("All consistency check runs failed")

    # Score each design by how many of its genes are consistent
    best_design = None
    best_score = -1
    for design in designs:
        genes = design.get("gene_circuit", {}).get("genes", [])
        score = sum(gene_votes.get(g.get("name", "").lower(), 0) for g in genes)
        if score > best_score:
            best_score = score
            best_design = design

    # Build consistency report
    consistency = {}
    for gene_name, count in gene_votes.items():
        consistency[gene_name] = {
            "votes": count,
            "out_of": len(designs),
            "confidence": "high" if count == len(designs) else "medium" if count >= 2 else "low",
        }

    total_genes = len(gene_votes)
    high_conf = sum(1 for v in consistency.values() if v["confidence"] == "high")
    overall = high_conf / max(total_genes, 1)

    best_design["_consistency"] = {
        "runs": len(designs),
        "gene_consistency": consistency,
        "overall_score": round(overall, 2),
        "summary": (
            f"{len(designs)}/{n_runs} runs succeeded. "
            f"{high_conf}/{total_genes} genes consistent across all runs "
            f"({overall:.0%} agreement)."
        ),
    }

    print(f"[CONSISTENCY] {best_design['_consistency']['summary']}")
    return best_design


SYSTEM_PROMPT = """You are Progenx's bioengineering AI. You design gene circuits based on user prompts.

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
2. PREFER these verified genes (we have curated accessions for instant lookup):
   petase, mhetase, phaA, phaB, phaC, rbcL, rbcS, ccmK, ccmM,
   nifH, nifD, nifK, alkB, opdA, cutinase, cah, ccdA, ccdB, gfp
3. Gene names must be standard symbols (lowercase). Do NOT invent gene names.
4. Choose chassis organisms that are real and appropriate for the environment.
   Supported chassis with full optimization: Escherichia coli K-12, Pseudomonas putida KT2440, Synechococcus elongatus PCC 7942.
5. Include realistic regulatory elements from iGEM registry (BBa_B0034, BBa_B0030, etc.).
6. Be honest about limitations — if 10x improvement is unrealistic, say so.
7. If unsure about a gene, use well-characterized alternatives from the verified list above.
{tier_rules}
Environment: {environment}
Safety level (0-1): {safety_level}
Complexity (0-1): {complexity}
"""

# Extra rules for free tier (Ollama) — constrain to verified genes/chassis only
FREE_TIER_RULES = """8. CRITICAL: ONLY use genes from the verified list in rule 2. Do NOT use any gene not on that list.
9. CRITICAL: ONLY use these chassis organisms: Escherichia coli K-12, Pseudomonas putida KT2440, or Synechococcus elongatus PCC 7942."""

# Pro tier (Claude) gets more flexibility with validation layers as safety net
PRO_TIER_RULES = """8. You may use genes beyond the verified list, but prefer verified genes when possible.
9. You may suggest any well-characterized chassis organism appropriate for the application."""


def generate_design(
    prompt: str,
    environment: str = "ocean",
    safety_level: float = 0.7,
    complexity: float = 0.5,
    user_tier: str = "free",
) -> dict:
    """Full design pipeline: LLM → NCBI → codon opt → FBA → assembly → visualization.
    Free tier uses Ollama (local, $0). Pro tier uses Claude (best quality)."""

    # Check cache first (serves identical prompts without any LLM call)
    cache_k = _cache_key(prompt, environment, safety_level, complexity)
    if cache_k in _design_cache:
        print(f"[CACHE] Serving cached design for prompt hash {cache_k}")
        cached = _design_cache[cache_k].copy()
        cached["model_used"] = cached.get("model_used", "") + " (cached)"
        return cached

    # Step 1: LLM designs the gene circuit (Ollama for free, Claude for Pro)
    tier_rules = FREE_TIER_RULES if user_tier == "free" else PRO_TIER_RULES
    system = SYSTEM_PROMPT.format(
        tagline=settings.TAGLINE,
        environment=environment,
        safety_level=safety_level,
        complexity=complexity,
        tier_rules=tier_rules,
    )

    user_msg = f"Design request: {prompt}\n\nReturn ONLY valid JSON."

    if user_tier in ("pro", "admin"):
        # Pro tier: run 3x self-consistency check for higher accuracy
        design = _self_consistency_check(system, user_msg, user_tier, n_runs=3)
    else:
        # Free tier: single call (faster, $0)
        raw = _llm_call(system, user_msg, user_tier)
        try:
            design = _parse_llm_json(raw)
        except ValueError:
            print("[LLM] First response had invalid JSON, retrying...")
            raw = _llm_call(
                "You must return ONLY valid JSON. No commentary, no markdown. Fix any syntax errors.",
                f"The following JSON has errors. Fix it and return ONLY the corrected JSON:\n\n{raw[:3000]}",
                user_tier,
            )
            design = _parse_llm_json(raw)

    chassis = design.get("host_organism", "Escherichia coli K-12")
    gene_circuit = design.get("gene_circuit", {})
    genes = gene_circuit.get("genes", [])
    pathway_gene_names = [g["name"] for g in genes]

    # Step 1.5: Post-LLM validation — check if registry genes match their intended function
    # Catches the case where LLM says petase="skin exopeptidase" (it's actually PET plastic hydrolase)
    for gene in genes:
        gene_name = gene.get("name", "")
        registry_entry = lookup_gene(gene_name)
        if registry_entry:
            # Override the LLM's function description with the registry's authoritative one
            registry_desc = registry_entry.get("description", "")
            llm_function = gene.get("function", "")
            if registry_desc and llm_function:
                gene["function"] = registry_desc
                gene["source_organism"] = registry_entry.get("organism", gene.get("source_organism", ""))
                if llm_function.lower() != registry_desc.lower():
                    gene["function_override"] = (
                        f"LLM described this as '{llm_function}'. "
                        f"Actual function: {registry_desc}"
                    )

    # Step 2: Fetch real sequences from NCBI
    # Pass full gene dicts so NCBI client can filter by organism and validate function
    # Skip LLM function validation for free tier (saves Haiku API calls)
    ncbi_results = fetch_genes_batch(genes, validate_function=(user_tier in ("pro", "admin")))

    gene_sequences = {}
    codon_optimized = {}
    total_construct_bp = 0
    non_registry_genes = []
    conceptual_genes = []

    for gene in genes:
        name = gene["name"]
        ncbi = ncbi_results.get(name, {})
        seq = ncbi.get("sequence", "")

        # Track genes that came from search (not verified registry)
        source = ncbi.get("source", "not_found")
        if source != "ncbi_registry":
            non_registry_genes.append(name)
        if ncbi.get("conceptual_only"):
            conceptual_genes.append(name)

        gene_sequences[name] = {
            "raw_sequence": seq,
            "accession": ncbi.get("accession", ""),
            "length": ncbi.get("length", 0),
            "source": source,
            "type": ncbi.get("type", "unknown"),
            "description": ncbi.get("description", ncbi.get("function", "")),
            "function_validation": ncbi.get("function_validation"),
            "conceptual_only": ncbi.get("conceptual_only", False),
            "warning": ncbi.get("warning", ""),
            "confidence": ncbi.get("confidence", "unknown"),
            "confidence_reason": ncbi.get("confidence_reason", ""),
        }

        # ESM-2 variant scoring (protein sequences only, Pro tier)
        if seq and ncbi.get("type") == "protein" and user_tier in ("pro", "admin"):
            esm_result = score_variants(seq)
            if esm_result:
                gene_sequences[name]["variant_predictions"] = esm_result

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

    # Step 4: Assembly planning (with primer design if DNA available)
    assembly = plan_assembly(
        genes=genes,
        chassis=chassis,
        environment=environment,
        total_construct_bp=total_construct_bp,
        codon_optimized=codon_optimized,
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
        design_name=design.get("design_name", "pProgenx"),
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

    # Step 7: Generate GenBank format
    genbank_content = ""
    if full_sequence:
        genbank_content = design_to_genbank(
            design_name=design.get("design_name", "pProgenx"),
            dna_sequence=full_sequence,
            genes=genes,
            promoters=gene_circuit.get("promoters", []),
            terminators=gene_circuit.get("terminators", []),
            assembly=assembly,
            host_organism=chassis,
            codon_optimized=codon_optimized,
        )

    # Compile yield string
    if fba_results.get("source") == "cobra_fba":
        yield_str = (
            f"Growth: {fba_results['adjusted_growth_rate']} h⁻¹ | "
            f"Titer: ~{fba_results['estimated_titer_g_per_L']} g/L | "
            f"Model: {fba_results['model_used']}"
        )
    else:
        yield_str = fba_results.get("summary", "N/A")

    # Conceptual-only banner when non-registry genes are used
    is_conceptual = bool(non_registry_genes)
    conceptual_banner = ""
    if is_conceptual:
        conceptual_banner = settings.CONCEPTUAL_ONLY_BANNER
        if conceptual_genes:
            conceptual_banner += (
                f" Genes with no verified biological parts: "
                f"{', '.join(conceptual_genes)}."
            )

    result = {
        "design_name": design.get("design_name", "Untitled"),
        "organism_summary": design.get("organism_summary", ""),
        "host_organism": chassis,
        "gene_circuit": gene_circuit,
        "gene_sequences": gene_sequences,
        "codon_optimized": codon_optimized,
        "dna_sequence": full_sequence,
        "fasta_content": fasta_content,
        "genbank_content": genbank_content,
        "plasmid_map": plasmid,
        "fba_results": fba_results,
        "assembly_plan": assembly,
        "safety_considerations": design.get("safety_considerations", ""),
        "simulated_yield": yield_str,
        "estimated_cost": _estimate_cost(total_construct_bp),
        "target_product": design.get("target_product", ""),
        "refinement_notes": design.get("refinement_notes", ""),
        "model_used": (
            f"{'claude-sonnet-4' if user_tier == 'pro' else f'ollama/{settings.OLLAMA_MODEL}'}"
            " + ncbi + cobra"
        ),
        "sequence_analysis": seq_analysis,
        "disclaimer": settings.DISCLAIMER,
        "is_conceptual": is_conceptual,
        "conceptual_banner": conceptual_banner,
        "non_registry_genes": non_registry_genes,
        "conceptual_genes": conceptual_genes,
        "consistency": design.get("_consistency"),
    }

    # Cache the result for future identical prompts
    if len(_design_cache) < MAX_CACHE_SIZE:
        _design_cache[cache_k] = result

    return result


def _estimate_cost(total_bp: int) -> str:
    """Estimate DNA synthesis cost based on bp."""
    if total_bp <= 0:
        return "Contact vendor for quote"
    # Gene synthesis pricing (2026): Twist ~$0.05-0.07/bp, IDT ~$0.07-0.10/bp
    low = total_bp * 0.05
    high = total_bp * 0.10
    return f"${low:,.0f} - ${high:,.0f} (gene synthesis at $0.05-0.10/bp, 2026 pricing)"


REFINE_SYSTEM = """You are Progenx's refinement assistant. The user has an existing design and wants changes.

Return valid JSON with the same structure as the original, plus "refinement_summary" explaining changes.
Only modify what the user asked for. Preserve working elements. Use real gene names only."""


def refine_design(
    original_design: dict,
    refinement_request: str,
    conversation_history: list[dict],
    user_tier: str = "free",
) -> dict:
    """Refine an existing design via LLM + re-run pipeline.
    Free tier uses Ollama, Pro tier uses Claude."""

    # Build conversation context for the refinement LLM call
    # _llm_call doesn't support multi-turn, so we flatten history into the user message
    history_text = ""
    for m in conversation_history[-10:]:
        history_text += f"\n[{m['role']}]: {m['content']}\n"

    user_msg = (
        f"Conversation so far:{history_text}\n\n"
        f"Current design:\n{json.dumps(original_design, indent=2, default=str)}\n\n"
        f"Refinement: {refinement_request}\n\nReturn ONLY valid JSON."
    )

    raw = _llm_call(REFINE_SYSTEM, user_msg, user_tier)
    refined = _parse_llm_json(raw)

    # Re-run the same pipeline with refined genes
    chassis = refined.get("host_organism", original_design.get("host_organism", "E. coli"))
    gene_circuit = refined.get("gene_circuit", {})
    genes = gene_circuit.get("genes", [])
    pathway_gene_names = [g["name"] for g in genes]

    # Pass full gene dicts for organism-filtered search + function validation
    ncbi_results = fetch_genes_batch(genes, validate_function=(user_tier in ("pro", "admin")))
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
        "model_used": (
            f"{'claude-sonnet-4' if user_tier == 'pro' else f'ollama/{settings.OLLAMA_MODEL}'}"
            " + ncbi + cobra"
        ),
        "disclaimer": settings.DISCLAIMER,
    }
