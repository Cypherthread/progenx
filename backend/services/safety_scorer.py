"""
Safety and dual-use assessment engine.

Every design goes through mandatory safety scoring before being returned to the user.
Flags are raised for:
- Known pathogenic sequences
- Antibiotic resistance markers without containment
- Toxin-producing genes
- Dual-use research of concern (DURC) patterns
- Environmental release risks
"""

import re
import json
from Bio.Seq import Seq

# Known dangerous sequence motifs (simplified for MVP — production would use
# a comprehensive database like the IGSC screening guidelines).
# These patterns are intentionally specific to reduce false positives on
# codon-optimized synbio constructs. Real screening uses BLAST against
# select agent databases (IGSC framework).
FLAGGED_PATTERNS = {
    "botulinum_toxin": r"ATGCCAAAA(?:TTA|CTG).{300,500}TGCTGA",
    "anthrax_pagA": r"ATGAAAAAACGG.{200,}GAAGATTAT",
    "ricin_rta": r"ATGGATCCGATTGATGTAAAC.{300,}AACTGG",
    "smallpox_crmB": r"ATGATCGATTACGAT.{400,}TACGATCGA",
}

# Gene names that raise dual-use flags
DUAL_USE_GENE_NAMES = [
    "pagA", "lef", "cya",  # Anthrax
    "rta", "rtb",  # Ricin
    "botA", "botB",  # Botulinum
    "eboGP", "vp40",  # Ebola
    "crmB",  # Smallpox
]

# Antibiotic resistance markers (flag if used without containment context)
RESISTANCE_MARKERS = [
    "ampR", "kanR", "tetR", "cmR", "bla", "aadA", "cat",
    "nptII", "hph", "ble", "ermB", "vanA", "mecA",
]

DISCLAIMER = (
    "DISCLAIMER: This design is for educational and research purposes only. "
    "ProtoForge outputs are computational predictions, not validated constructs. "
    "Any laboratory implementation must comply with institutional biosafety "
    "committees (IBC), NIH Guidelines for Research Involving Recombinant or "
    "Synthetic Nucleic Acid Molecules, and all applicable local, national, and "
    "international biosafety regulations. Do not synthesize or release engineered "
    "organisms without proper authorization and containment."
)


def score_safety(
    dna_sequence: str,
    organism_summary: str,
    gene_circuit: str,
) -> dict:
    """Score a design for safety and dual-use concerns."""
    flags = []
    score = 1.0  # Start at 1.0 (safe), deduct for concerns

    combined_text = f"{organism_summary} {gene_circuit}".lower()

    # Check for known dangerous sequence patterns
    for name, pattern in FLAGGED_PATTERNS.items():
        if re.search(pattern, dna_sequence, re.IGNORECASE):
            flags.append(f"CRITICAL: Sequence matches known pathogenic pattern ({name})")
            score -= 0.5

    # Check for dual-use gene names in the design
    for gene in DUAL_USE_GENE_NAMES:
        if gene.lower() in combined_text:
            flags.append(f"DUAL-USE CONCERN: Design references {gene}, a known select agent gene")
            score -= 0.3

    # Check for antibiotic resistance markers
    resistance_found = []
    for marker in RESISTANCE_MARKERS:
        if marker.lower() in combined_text:
            resistance_found.append(marker)

    if resistance_found:
        flags.append(
            f"BIOSAFETY: Contains antibiotic resistance marker(s): {', '.join(resistance_found)}. "
            "Ensure proper containment and do not use for environmental release."
        )
        score -= 0.1 * len(resistance_found)

    # Check for environmental release language
    env_release_terms = ["environmental release", "open field", "wild release", "uncontained"]
    for term in env_release_terms:
        if term in combined_text:
            flags.append(f"RISK: Design mentions '{term}' — environmental release requires extensive regulatory approval")
            score -= 0.2

    # Sequence-level checks
    if len(dna_sequence) > 50000:
        flags.append("NOTE: Large construct (>50kb) — may require specialized synthesis")

    # Check GC content extremes
    if dna_sequence:
        gc = (dna_sequence.upper().count("G") + dna_sequence.upper().count("C")) / len(dna_sequence)
        if gc > 0.7 or gc < 0.3:
            flags.append(f"WARNING: Extreme GC content ({gc:.1%}) may affect expression and stability")

    score = max(0.0, min(1.0, score))

    # Dual-use assessment summary
    if score < 0.3:
        dual_use = "HIGH RISK: This design contains elements associated with select agents or biosecurity concerns. It cannot be synthesized through standard vendors."
    elif score < 0.6:
        dual_use = "MODERATE CONCERN: This design contains elements that may trigger additional screening by DNA synthesis providers. Review and justify each flagged element."
    elif flags:
        dual_use = "LOW CONCERN: Minor flags noted. Standard biosafety practices apply. Review flags before proceeding."
    else:
        dual_use = "MINIMAL CONCERN: No significant dual-use or safety flags detected. Standard biosafety practices apply."

    return {
        "score": round(score, 2),
        "flags": flags,
        "dual_use_assessment": dual_use,
        "disclaimer": DISCLAIMER,
        "resistance_markers": resistance_found,
    }
