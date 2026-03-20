"""
Assembly planning: ori selection, resistance markers, kill switches,
cloning strategy (Golden Gate / Gibson), and primer design.
"""

from services.primer_designer import design_primers_for_gene, calculate_tm


def plan_assembly(
    genes: list[dict],
    chassis: str,
    environment: str,
    total_construct_bp: int,
    codon_optimized: dict | None = None,
) -> dict:
    """
    Generate a complete assembly plan for the construct.
    Optionally includes primer design if codon-optimized DNA sequences are provided.
    """
    n_parts = len(genes) + 2  # genes + promoter region + terminator region
    total_bp = total_construct_bp

    # 1. Origin of replication
    ori = _select_ori(chassis, total_bp)

    # 2. Antibiotic resistance marker
    marker = _select_marker(chassis)

    # 3. Assembly method
    method = _select_assembly_method(n_parts, total_bp)

    # 4. Kill switch / biocontainment
    kill_switch = _select_kill_switch(environment)

    # 5. RBS notes
    rbs = _rbs_notes(genes)

    # 6. Estimated construct size
    overhead = ori["size_bp"] + marker["size_bp"] + kill_switch["size_bp"] + 500  # regulatory
    full_size = total_bp + overhead

    # 7. Primer design (if DNA sequences available)
    primers = _design_primers(genes, codon_optimized)

    # 8. Assembly compatibility check (restriction site scan)
    compatibility = _check_assembly_compatibility(method["name"], genes, codon_optimized)

    result = {
        "origin_of_replication": ori,
        "selection_marker": marker,
        "assembly_method": method,
        "kill_switch": kill_switch,
        "rbs_notes": rbs,
        "estimated_total_size_bp": full_size,
        "parts_count": n_parts,
        "assembly_compatibility": compatibility,
        "summary": _build_summary(ori, marker, method, kill_switch, rbs, full_size, genes),
    }

    if primers:
        result["primers"] = primers

    return result


def _design_primers(genes: list[dict], codon_optimized: dict | None) -> list[dict] | None:
    """Design primers for each gene if codon-optimized DNA is available."""
    if not codon_optimized:
        return None

    primers = []
    for gene in genes:
        name = gene.get("name", "")
        opt = codon_optimized.get(name, {})
        dna = opt.get("optimized_dna", "")

        if not dna or len(dna) < 50:
            continue

        result = design_primers_for_gene(dna, name, target_tm=60.0)
        if "error" not in result:
            primers.append(result)

    return primers if primers else None


def _select_ori(chassis: str, construct_bp: int) -> dict:
    chassis_lower = chassis.lower()

    if "putida" in chassis_lower or "pseudomonas" in chassis_lower:
        return {
            "name": "pBBR1",
            "copy_number": "medium (~15 copies)",
            "size_bp": 1800,
            "rationale": "Broad-host-range ori compatible with Pseudomonas. pBBR1 provides stable medium-copy replication without requiring specific host factors.",
            "alternative": "pRO1600 (lower copy, more stable for large inserts)",
        }
    elif "synechococcus" in chassis_lower or "cyanobact" in chassis_lower or "synechocystis" in chassis_lower:
        return {
            "name": "RSF1010",
            "copy_number": "low (~10 copies)",
            "size_bp": 2100,
            "rationale": "Broad-host-range ori that replicates in cyanobacteria. Alternatively, integrate into neutral site I (NSI) on chromosome for maximum stability.",
            "alternative": "Chromosomal integration at NSI (preferred for production)",
        }
    else:
        # E. coli and others
        if construct_bp > 10000:
            return {
                "name": "p15A",
                "copy_number": "low (~15 copies)",
                "size_bp": 1200,
                "rationale": "Low-copy ori reduces metabolic burden for large constructs. Compatible with pMB1-based plasmids for two-plasmid systems.",
                "alternative": "pSC101 (~5 copies, even lower burden)",
            }
        else:
            return {
                "name": "pMB1 (ColE1)",
                "copy_number": "medium-high (~20-40 copies)",
                "size_bp": 900,
                "rationale": "Standard high-copy E. coli ori. Good for initial characterization and protein expression.",
                "alternative": "p15A (lower copy for production strains)",
            }


def _select_marker(chassis: str) -> dict:
    chassis_lower = chassis.lower()

    if "putida" in chassis_lower or "pseudomonas" in chassis_lower:
        return {
            "name": "gentamicin resistance (aacC1)",
            "gene": "aacC1",
            "size_bp": 530,
            "rationale": "Gentamicin is effective in Pseudomonas. Kanamycin resistance often has background in environmental isolates.",
        }
    elif "synechococcus" in chassis_lower or "cyanobact" in chassis_lower:
        return {
            "name": "spectinomycin resistance (aadA)",
            "gene": "aadA",
            "size_bp": 790,
            "rationale": "Spectinomycin/streptomycin resistance is the standard selectable marker for cyanobacterial transformations.",
        }
    else:
        return {
            "name": "kanamycin resistance (nptII)",
            "gene": "nptII",
            "size_bp": 795,
            "rationale": "Standard E. coli selection marker. Well-characterized, moderate spectrum.",
        }


def _select_assembly_method(n_parts: int, total_bp: int) -> dict:
    if n_parts <= 4 and total_bp < 8000:
        return {
            "name": "Gibson Assembly",
            "description": "Single-step isothermal assembly. Add 20-40bp overlaps between adjacent fragments.",
            "steps": [
                "Design primers with 20-40bp overlaps to adjacent fragments",
                "PCR-amplify each part with overlap primers",
                "Mix all fragments with Gibson Assembly Master Mix (NEB E2611)",
                "Incubate 50°C for 60 min",
                "Transform into competent cells",
            ],
            "cost_note": "~$80 for Gibson mix + primers",
            "max_parts": 6,
        }
    else:
        return {
            "name": "Golden Gate (BsaI Type IIS)",
            "description": "Modular, scarless assembly using BsaI restriction sites. Ideal for multi-gene pathways.",
            "steps": [
                "Clone each gene into BsaI entry vectors with standardized overhangs",
                "Design 4bp fusion sites between parts (avoid palindromes)",
                f"Combine all {n_parts} parts + destination vector in one-pot reaction",
                "Cycle: 37°C 5min / 16°C 5min × 30 cycles, then 60°C 5min",
                "Transform into competent cells, blue/white screen",
            ],
            "cost_note": "~$120 for enzymes + entry vectors",
            "max_parts": 12,
        }


def _select_kill_switch(environment: str) -> dict:
    if environment in ("ocean", "soil"):
        return {
            "name": "ccdA/ccdB toxin-antitoxin + auxotrophy",
            "genes": ["ccdB (toxin)", "ccdA (antitoxin, under inducible control)"],
            "size_bp": 900,
            "mechanism": (
                "CcdB inhibits DNA gyrase, killing the cell. CcdA antitoxin is expressed "
                "from an IPTG-inducible promoter — cells die without inducer. Additionally, "
                "delete thyA (thymidylate synthase) to create thymidine auxotrophy, "
                "preventing survival outside supplemented media."
            ),
            "rationale": "Dual containment required for environmental release organisms. Toxin-antitoxin provides active killing; auxotrophy provides passive containment.",
        }
    elif environment == "gut":
        return {
            "name": "mazE/mazF toxin-antitoxin",
            "genes": ["mazF (toxin)", "mazE (antitoxin, constitutive)"],
            "size_bp": 750,
            "mechanism": (
                "MazF is an mRNA interferase that cleaves cellular mRNAs. MazE antitoxin "
                "is unstable (half-life ~30min) and must be continuously expressed. "
                "Loss of plasmid → no MazE → MazF kills cell."
            ),
            "rationale": "Post-segregational killing ensures plasmid maintenance in gut environment. MazEF is well-characterized and FDA-reviewed in probiotic contexts.",
        }
    else:
        return {
            "name": "ccdA/ccdB toxin-antitoxin",
            "genes": ["ccdB (toxin)", "ccdA (antitoxin)"],
            "size_bp": 600,
            "mechanism": (
                "Standard post-segregational killing system. CcdB toxin is always expressed; "
                "CcdA antitoxin on the plasmid neutralizes it. Plasmid loss → cell death."
            ),
            "rationale": "Lab containment. Prevents plasmid-free escapees from outcompeting engineered strain.",
        }


def _rbs_notes(genes: list[dict]) -> dict:
    return {
        "strategy": "Bicistronic Design (BCD) for first gene, community RBS (B0034) for pathway genes",
        "details": [
            "Gene 1: Use BCD2 (bicistronic design element) for reliable translation initiation independent of mRNA context",
            "Pathway genes: iGEM BBa_B0034 (strong RBS, ~0.3 au) or BBa_B0032 (medium, ~0.3 au)",
            "Balance expression: First enzyme in pathway gets strongest RBS; last enzyme gets weakest to prevent intermediate accumulation",
        ],
        "tool_note": "For precise RBS strength: use Salis Lab RBS Calculator (salislab.net/software) to predict translation initiation rates",
    }


def _build_summary(ori, marker, method, kill_switch, rbs, full_size, genes) -> str:
    gene_names = [g.get("name", "?") for g in genes]
    return (
        f"ASSEMBLY PLAN\n"
        f"═══════════════════════════════════════\n"
        f"Construct size: ~{full_size:,} bp\n"
        f"Genes: {' → '.join(gene_names)}\n"
        f"\n"
        f"Origin: {ori['name']} ({ori['copy_number']})\n"
        f"  {ori['rationale']}\n"
        f"\n"
        f"Selection: {marker['name']}\n"
        f"  {marker['rationale']}\n"
        f"\n"
        f"Assembly: {method['name']}\n"
        f"  {method['description']}\n"
        f"\n"
        f"Biocontainment: {kill_switch['name']}\n"
        f"  {kill_switch['mechanism']}\n"
        f"\n"
        f"RBS: {rbs['strategy']}\n"
    )


# Common Type IIS and restriction enzyme recognition sites
RESTRICTION_SITES = {
    # Type IIS (used in Golden Gate / MoClo)
    "BsaI": "GGTCTC",
    "BsaI_rc": "GAGACC",
    "BpiI": "GAAGAC",
    "BpiI_rc": "GTCTTC",
    "BbsI": "GAAGAC",
    "BbsI_rc": "GTCTTC",
    "SapI": "GCTCTTC",
    "SapI_rc": "GAAGAGC",
    # Common 6-cutters (used in restriction/ligation cloning)
    "EcoRI": "GAATTC",
    "BamHI": "GGATCC",
    "HindIII": "AAGCTT",
    "XbaI": "TCTAGA",
    "SpeI": "ACTAGT",
    "PstI": "CTGCAG",
    "NotI": "GCGGCCGC",
}

# Which enzymes matter for each assembly method
ASSEMBLY_ENZYMES = {
    "Golden Gate": ["BsaI", "BsaI_rc"],
    "Golden Gate (BsaI Type IIS)": ["BsaI", "BsaI_rc"],
    "Gibson Assembly": [],  # Gibson doesn't use restriction enzymes
    "MoClo": ["BsaI", "BsaI_rc", "BpiI", "BpiI_rc"],
}


def _check_assembly_compatibility(
    method_name: str,
    genes: list[dict],
    codon_optimized: dict | None,
) -> dict:
    """Check if gene sequences contain restriction sites that would
    interfere with the chosen assembly method.

    This catches a real lab failure mode: internal BsaI sites in a gene
    will cause Golden Gate assembly to cut in the wrong place, producing
    incorrect constructs or no colonies.
    """
    relevant_enzymes = ASSEMBLY_ENZYMES.get(method_name, [])
    if not relevant_enzymes:
        return {
            "compatible": True,
            "method": method_name,
            "issues": [],
            "note": f"{method_name} does not use restriction enzymes — no site conflicts possible.",
        }

    issues = []

    for gene in genes:
        name = gene.get("name", "unknown")

        # Check codon-optimized DNA first (this is what gets built)
        dna = ""
        if codon_optimized:
            opt = codon_optimized.get(name, {})
            if isinstance(opt, dict):
                dna = opt.get("optimized_dna", "")

        if not dna:
            continue

        dna_upper = dna.upper()
        for enz_name in relevant_enzymes:
            site = RESTRICTION_SITES.get(enz_name, "")
            if not site:
                continue

            # Find all occurrences
            pos = 0
            while True:
                idx = dna_upper.find(site, pos)
                if idx == -1:
                    break
                issues.append({
                    "gene": name,
                    "enzyme": enz_name.replace("_rc", " (reverse complement)"),
                    "site": site,
                    "position": idx + 1,
                    "warning": f"Internal {enz_name.replace('_rc', '')} site in {name} at position {idx + 1} — "
                               f"this will cause incorrect cutting during {method_name} assembly.",
                    "fix": f"Mutate the internal site with a synonymous codon change (silent mutation at position {idx + 1}).",
                })
                pos = idx + 1

    return {
        "compatible": len(issues) == 0,
        "method": method_name,
        "issues": issues,
        "note": (
            f"All genes are compatible with {method_name} — no internal restriction site conflicts found."
            if not issues else
            f"Found {len(issues)} internal restriction site{'s' if len(issues) != 1 else ''} that will interfere with {method_name}. "
            f"These must be removed by silent mutation before assembly."
        ),
    }
