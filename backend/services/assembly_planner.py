"""
Assembly planning: ori selection, resistance markers, kill switches,
and cloning strategy (Golden Gate / Gibson).
"""


def plan_assembly(
    genes: list[dict],
    chassis: str,
    environment: str,
    total_construct_bp: int,
) -> dict:
    """
    Generate a complete assembly plan for the construct.
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

    return {
        "origin_of_replication": ori,
        "selection_marker": marker,
        "assembly_method": method,
        "kill_switch": kill_switch,
        "rbs_notes": rbs,
        "estimated_total_size_bp": full_size,
        "parts_count": n_parts,
        "summary": _build_summary(ori, marker, method, kill_switch, rbs, full_size, genes),
    }


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
