"""
Primer design and melting temperature calculation.

Implements the SantaLucia (1998) nearest-neighbor thermodynamic model
for DNA melting temperature prediction. Generates basic primer suggestions
for Gibson and Golden Gate assembly.

References:
  - SantaLucia J Jr. (1998) PNAS 95:1460-1465
  - Nearest-neighbor parameters from the unified model
  - TeselaGen sequence-utils (MIT) used as algorithm reference
"""

import math

# ── SantaLucia (1998) Nearest-Neighbor Parameters ───────────────────
# deltaH in cal/mol, deltaS in cal/(mol·K)
# Format: {dinucleotide: (deltaH, deltaS)}
NN_PARAMS = {
    "AA": (-7900, -22.2), "TT": (-7900, -22.2),
    "AT": (-7200, -20.4),
    "TA": (-7200, -21.3),
    "CA": (-8500, -22.7), "TG": (-8500, -22.7),
    "GT": (-8400, -22.4), "AC": (-8400, -22.4),
    "CT": (-7800, -21.0), "AG": (-7800, -21.0),
    "GA": (-8200, -22.2), "TC": (-8200, -22.2),
    "CG": (-10600, -27.2),
    "GC": (-9800, -24.4),
    "GG": (-8000, -19.9), "CC": (-8000, -19.9),
}

# Initiation parameters
INIT_GC = (100, -2.8)   # deltaH, deltaS for terminal G or C
INIT_AT = (2300, 4.1)    # deltaH, deltaS for terminal A or T

# Gas constant
R = 1.987  # cal/(mol·K)


def calculate_tm(
    sequence: str,
    primer_conc_nM: float = 500.0,
    monovalent_mM: float = 50.0,
) -> float | None:
    """Calculate melting temperature using SantaLucia nearest-neighbor model.

    Args:
        sequence: DNA primer sequence (5' to 3', uppercase ACGT only)
        primer_conc_nM: Primer concentration in nM (default 500 nM = 0.5 uM)
        monovalent_mM: Monovalent cation concentration in mM (default 50 mM Na+)

    Returns:
        Melting temperature in degrees Celsius, or None if sequence is invalid.
    """
    seq = sequence.upper().replace(" ", "")

    # Validate
    if len(seq) < 8:
        return None
    if not all(c in "ACGT" for c in seq):
        return None

    # Sum nearest-neighbor parameters
    sum_dH = 0.0  # cal/mol
    sum_dS = 0.0  # cal/(mol·K)

    for i in range(len(seq) - 1):
        dinuc = seq[i:i+2]
        if dinuc in NN_PARAMS:
            dH, dS = NN_PARAMS[dinuc]
            sum_dH += dH
            sum_dS += dS
        else:
            return None  # Unknown dinucleotide

    # Initiation parameters based on terminal bases
    if seq[0] in "GC":
        sum_dH += INIT_GC[0]
        sum_dS += INIT_GC[1]
    else:
        sum_dH += INIT_AT[0]
        sum_dS += INIT_AT[1]

    if seq[-1] in "GC":
        sum_dH += INIT_GC[0]
        sum_dS += INIT_GC[1]
    else:
        sum_dH += INIT_AT[0]
        sum_dS += INIT_AT[1]

    # Primer concentration (convert nM to M)
    ct = primer_conc_nM * 1e-9

    # Tm calculation (non-self-complementary)
    # Tm = dH / (dS + R * ln(Ct/4)) - 273.15
    tm_kelvin = sum_dH / (sum_dS + R * math.log(ct / 4))
    tm_celsius = tm_kelvin - 273.15

    # Salt correction (SantaLucia 1998)
    # Tm_corrected = Tm + 16.6 * log10([Na+])
    salt_M = monovalent_mM / 1000.0
    tm_corrected = tm_celsius + 16.6 * math.log10(salt_M)

    return round(tm_corrected, 1)


def gc_content(sequence: str) -> float:
    """Calculate GC content as a fraction (0-1)."""
    seq = sequence.upper()
    gc = sum(1 for c in seq if c in "GC")
    return gc / max(len(seq), 1)


def design_primers_for_gene(
    dna_sequence: str,
    gene_name: str,
    target_tm: float = 60.0,
    min_length: int = 18,
    max_length: int = 30,
) -> dict:
    """Design forward and reverse primers for a gene.

    Starts at min_length and extends until Tm reaches target.
    Returns primer sequences, Tm, GC content, and length.
    """
    seq = dna_sequence.upper().replace(" ", "")

    if len(seq) < min_length * 2:
        return {"error": f"Sequence too short ({len(seq)} bp) for primer design"}

    # Forward primer — starts at 5' end of coding sequence
    fwd = _design_single_primer(seq, target_tm, min_length, max_length, "forward")

    # Reverse primer — starts at 3' end, reverse complement
    rev_region = seq[-(max_length + 5):]
    rev = _design_single_primer(
        _reverse_complement(rev_region),
        target_tm, min_length, max_length, "reverse"
    )

    return {
        "gene": gene_name,
        "forward": fwd,
        "reverse": rev,
        "expected_product_bp": len(seq),
        "note": (
            "Primers designed using SantaLucia (1998) nearest-neighbor Tm model. "
            "Conditions: 500 nM primer, 50 mM Na+. Verify with your lab's Tm calculator "
            "(e.g., NEB Tm Calculator) before ordering."
        ),
    }


def _design_single_primer(
    template: str,
    target_tm: float,
    min_length: int,
    max_length: int,
    direction: str,
) -> dict:
    """Design a single primer by extending from the start of template."""
    best = None

    for length in range(min_length, min(max_length + 1, len(template) + 1)):
        primer_seq = template[:length]
        tm = calculate_tm(primer_seq)

        if tm is None:
            continue

        candidate = {
            "sequence": primer_seq,
            "length": length,
            "tm": tm,
            "gc": round(gc_content(primer_seq), 3),
            "direction": direction,
        }

        # Check if primer meets basic quality criteria
        gc_frac = gc_content(primer_seq)
        gc_ok = 0.35 <= gc_frac <= 0.65

        if best is None:
            best = candidate

        # Accept if within 2°C of target and GC is acceptable
        if abs(tm - target_tm) <= 2.0 and gc_ok:
            return candidate

        # Track closest to target
        if abs(tm - target_tm) < abs(best["tm"] - target_tm):
            best = candidate

        # Stop if we've overshot the target significantly
        if tm > target_tm + 5.0:
            break

    return best or {"error": f"Could not design {direction} primer"}


def _reverse_complement(seq: str) -> str:
    """Return the reverse complement of a DNA sequence."""
    complement = {"A": "T", "T": "A", "G": "C", "C": "G"}
    return "".join(complement.get(c, c) for c in reversed(seq.upper()))


def design_gibson_overlaps(
    gene_sequences: dict[str, str],
    overlap_length: int = 30,
) -> list[dict]:
    """Design Gibson Assembly overlap sequences between adjacent genes.

    For each junction between adjacent genes, generates the overlap region
    that should be added to primers for PCR amplification.
    """
    gene_names = list(gene_sequences.keys())
    overlaps = []

    for i in range(len(gene_names) - 1):
        name_a = gene_names[i]
        name_b = gene_names[i + 1]
        seq_a = gene_sequences[name_a]
        seq_b = gene_sequences[name_b]

        if not seq_a or not seq_b:
            continue

        # Overlap = last N bp of gene A + first N bp of gene B
        overlap_a = seq_a[-overlap_length:]
        overlap_b = seq_b[:overlap_length]

        # Forward primer for gene B gets 3' end of gene A as overhang
        # Reverse primer for gene A gets 5' RC of gene B as overhang

        overlaps.append({
            "junction": f"{name_a} → {name_b}",
            "overlap_from_a": overlap_a,
            "overlap_from_b": overlap_b,
            "fwd_primer_overhang": overlap_a,  # Add to fwd primer of gene B
            "rev_primer_overhang": _reverse_complement(overlap_b),  # Add to rev primer of gene A
            "overlap_tm": calculate_tm(overlap_a),
            "length": overlap_length,
        })

    return overlaps
