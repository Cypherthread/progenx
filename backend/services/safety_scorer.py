"""
Safety and dual-use assessment engine.

Every design goes through mandatory safety scoring before being returned to the user.

Two layers:
1. Built-in pattern matching (always runs — regex patterns, gene name checks,
   resistance marker detection)
2. SecureDNA hazard screening (optional — POST DNA to local synthclient for
   comprehensive biosecurity screening against 400+ known threats)

Flags are raised for:
- Known pathogenic sequences (regex + SecureDNA)
- Antibiotic resistance markers without containment
- Toxin-producing genes
- Dual-use research of concern (DURC) patterns
- Select agents and export-controlled organisms (SecureDNA)
- Environmental release risks
"""

import re
import json
from Bio.Seq import Seq
from config import settings

# ── Built-in pattern matching (always available) ─────────────────────

# Known dangerous sequence motifs (simplified — SecureDNA provides
# comprehensive screening against 400+ threats with functional variants).
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


# ── SecureDNA integration ────────────────────────────────────────────

# SecureDNA synthclient URL (run as sidecar container or local process)
# Register for certificates at: https://securedna.org/cert-request/
# Docker: ghcr.io/securedna/synthclient
SECUREDNA_URL = getattr(settings, "SECUREDNA_URL", "") or ""


def _screen_securedna(dna_sequence: str) -> dict | None:
    """Screen a DNA sequence against SecureDNA's hazard database.
    Returns screening result or None if SecureDNA is not configured/available.

    SecureDNA checks 400+ biological threats including:
    - US Select Agents (HHS/USDA/APHIS)
    - Australia Group pathogens
    - EU/PRC export-controlled organisms
    - Potential Pandemic Pathogens
    - Toxin genes with functional variant coverage

    Privacy: sequences are cryptographically blinded before leaving the server.
    The synthclient runs locally — raw DNA never touches SecureDNA's servers.
    """
    if not SECUREDNA_URL:
        return None

    if not dna_sequence or len(dna_sequence) < 30:
        return None  # SecureDNA needs at least 30 bp

    import httpx

    fasta = f">protoforge_screen\n{dna_sequence}"

    try:
        resp = httpx.post(
            f"{SECUREDNA_URL}/v1/screen",
            json={
                "fasta": fasta,
                "region": "all",
                "provider_reference": "protoforge",
            },
            timeout=30,
        )

        if resp.status_code == 200:
            data = resp.json()
            return {
                "screened": True,
                "permission": data.get("synthesis_permission", "unknown"),
                "hits": data.get("hits_by_record", []),
            }
        elif resp.status_code == 429:
            print("[SecureDNA] Rate limited — skipping hazard screen")
            return {"screened": False, "reason": "rate_limited"}
        else:
            print(f"[SecureDNA] Error {resp.status_code}: {resp.text[:200]}")
            return {"screened": False, "reason": f"http_{resp.status_code}"}

    except Exception as e:
        print(f"[SecureDNA] Connection error: {e}")
        return {"screened": False, "reason": str(e)}


def _parse_securedna_hits(securedna_result: dict) -> list[str]:
    """Convert SecureDNA hit data into human-readable safety flags."""
    flags = []
    if not securedna_result or not securedna_result.get("screened"):
        return flags

    permission = securedna_result.get("permission", "unknown")
    if permission == "denied":
        flags.append(
            "CRITICAL — SecureDNA DENIED synthesis: sequence matches known "
            "biological threat(s) in international biosecurity databases."
        )

    for record in securedna_result.get("hits", []):
        for hazard in record.get("hits_by_hazard", []):
            org = hazard.get("most_likely_organism", {})
            org_name = org.get("name", "unknown organism")
            org_type = org.get("organism_type", "unknown")
            tags = org.get("tags", [])

            tag_str = ""
            if tags:
                readable_tags = []
                for t in tags:
                    if "SelectAgent" in t:
                        readable_tags.append("US Select Agent")
                    elif "AustraliaGroup" in t:
                        readable_tags.append("Australia Group controlled")
                    elif "PotentialPandemic" in t:
                        readable_tags.append("Potential Pandemic Pathogen")
                    elif "EuropeanUnion" in t:
                        readable_tags.append("EU export controlled")
                    elif "PRCExportControl" in t:
                        readable_tags.append("PRC export controlled")
                if readable_tags:
                    tag_str = f" [{', '.join(readable_tags)}]"

            regions = hazard.get("hit_regions", [])
            bp_info = ""
            if regions:
                start = regions[0].get("seq_range_start", "?")
                end = regions[-1].get("seq_range_end", "?")
                bp_info = f" (bp {start}-{end})"

            flags.append(
                f"SECUREDNA HAZARD: Matches {org_type} '{org_name}'{tag_str}{bp_info}"
            )

    return flags


# ── Main scoring function ────────────────────────────────────────────

def score_safety(
    dna_sequence: str,
    organism_summary: str,
    gene_circuit: str,
) -> dict:
    """Score a design for safety and dual-use concerns.

    Runs two layers:
    1. Built-in pattern matching (always runs)
    2. SecureDNA hazard screening (if synthclient is configured)
    """
    flags = []
    score = 1.0  # Start at 1.0 (safe), deduct for concerns

    combined_text = f"{organism_summary} {gene_circuit}".lower()

    # ── Layer 1: Built-in pattern matching ────────────────────────

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

    # ── Layer 2: SecureDNA hazard screening ───────────────────────

    securedna_result = _screen_securedna(dna_sequence)
    securedna_flags = []

    if securedna_result:
        securedna_flags = _parse_securedna_hits(securedna_result)
        flags.extend(securedna_flags)

        # SecureDNA denial is a hard override
        if securedna_result.get("permission") == "denied":
            score = 0.0

    # ── Final scoring ────────────────────────────────────────────

    score = max(0.0, min(1.0, score))

    # Dual-use assessment summary
    if score == 0.0:
        dual_use = (
            "BLOCKED: SecureDNA identified this sequence as matching known biological "
            "threats. This design CANNOT be synthesized through any compliant vendor. "
            "Do not attempt to order synthesis of this sequence."
        )
    elif score < 0.3:
        dual_use = "HIGH RISK: This design contains elements associated with select agents or biosecurity concerns. It cannot be synthesized through standard vendors."
    elif score < 0.6:
        dual_use = "MODERATE CONCERN: This design contains elements that may trigger additional screening by DNA synthesis providers. Review and justify each flagged element."
    elif flags:
        dual_use = "LOW CONCERN: Minor flags noted. Standard biosafety practices apply. Review flags before proceeding."
    else:
        dual_use = "MINIMAL CONCERN: No significant dual-use or safety flags detected. Standard biosafety practices apply."

    # Screening method disclosure
    screening_method = "Built-in pattern matching (4 pathogen patterns, 11 dual-use genes, 13 resistance markers)"
    if securedna_result and securedna_result.get("screened"):
        screening_method += " + SecureDNA hazard screening (400+ biological threats with functional variant coverage)"
    elif SECUREDNA_URL:
        screening_method += " (SecureDNA configured but screening failed — see logs)"

    return {
        "score": round(score, 2),
        "flags": flags,
        "dual_use_assessment": dual_use,
        "disclaimer": DISCLAIMER,
        "resistance_markers": resistance_found,
        "screening_method": screening_method,
        "securedna_result": securedna_result,
    }
