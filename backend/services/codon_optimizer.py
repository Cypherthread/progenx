"""
Codon optimization for chassis organisms.

Uses BioPython codon usage tables to optimize protein-coding sequences
for expression in the target chassis organism.
"""

from Bio.Seq import Seq
from Bio.Data import CodonTable
import random

# Codon usage tables (frequency per 1000 codons) for common chassis organisms
# Source: Kazusa Codon Usage Database
CODON_USAGE = {
    "e_coli": {
        "TTT": 22.0, "TTC": 16.2, "TTA": 13.8, "TTG": 13.4,
        "CTT": 11.4, "CTC": 10.9, "CTA": 3.9, "CTG": 52.6,
        "ATT": 30.1, "ATC": 24.6, "ATA": 4.6, "ATG": 27.1,
        "GTT": 18.3, "GTC": 15.2, "GTA": 10.9, "GTG": 25.9,
        "TCT": 8.5, "TCC": 8.6, "TCA": 7.2, "TCG": 8.8,
        "CCT": 7.1, "CCC": 5.5, "CCA": 8.4, "CCG": 22.9,
        "ACT": 8.9, "ACC": 22.9, "ACA": 7.1, "ACG": 14.4,
        "GCT": 15.3, "GCC": 25.3, "GCA": 20.1, "GCG": 33.1,
        "TAT": 16.3, "TAC": 12.2, "TAA": 2.0, "TAG": 0.2,
        "CAT": 12.8, "CAC": 9.5, "CAA": 15.3, "CAG": 28.9,
        "AAT": 17.7, "AAC": 21.5, "AAA": 33.6, "AAG": 10.3,
        "GAT": 32.2, "GAC": 19.1, "GAA": 39.4, "GAG": 18.2,
        "TGT": 5.2, "TGC": 6.3, "TGA": 1.0, "TGG": 15.2,
        "CGT": 20.7, "CGC": 21.5, "CGA": 3.6, "CGG": 5.6,
        "AGT": 8.8, "AGC": 15.8, "AGA": 2.1, "AGG": 1.2,
        "GGT": 24.7, "GGC": 28.9, "GGA": 8.0, "GGG": 11.1,
    },
    "p_putida": {
        "TTT": 11.5, "TTC": 24.0, "TTA": 3.4, "TTG": 12.6,
        "CTT": 9.2, "CTC": 18.8, "CTA": 2.9, "CTG": 42.0,
        "ATT": 16.0, "ATC": 29.0, "ATA": 2.4, "ATG": 24.5,
        "GTT": 10.0, "GTC": 20.5, "GTA": 5.3, "GTG": 29.0,
        "TCT": 5.8, "TCC": 14.5, "TCA": 5.0, "TCG": 12.0,
        "CCT": 5.2, "CCC": 10.5, "CCA": 7.8, "CCG": 20.0,
        "ACT": 5.8, "ACC": 28.0, "ACA": 5.5, "ACG": 12.8,
        "GCT": 10.8, "GCC": 32.5, "GCA": 14.5, "GCG": 28.0,
        "TAT": 8.5, "TAC": 16.0, "TAA": 1.8, "TAG": 0.4,
        "CAT": 7.8, "CAC": 14.2, "CAA": 11.0, "CAG": 28.5,
        "AAT": 10.5, "AAC": 22.0, "AAA": 18.0, "AAG": 20.5,
        "GAT": 20.5, "GAC": 25.8, "GAA": 28.0, "GAG": 25.5,
        "TGT": 3.8, "TGC": 8.5, "TGA": 1.2, "TGG": 16.0,
        "CGT": 10.5, "CGC": 25.0, "CGA": 4.2, "CGG": 10.0,
        "AGT": 5.5, "AGC": 18.0, "AGA": 2.0, "AGG": 2.5,
        "GGT": 14.5, "GGC": 34.5, "GGA": 9.0, "GGG": 10.5,
    },
    "s_elongatus": {
        "TTT": 14.0, "TTC": 22.5, "TTA": 5.0, "TTG": 15.0,
        "CTT": 12.0, "CTC": 16.5, "CTA": 4.0, "CTG": 30.0,
        "ATT": 18.0, "ATC": 26.0, "ATA": 4.0, "ATG": 25.0,
        "GTT": 12.0, "GTC": 18.0, "GTA": 7.0, "GTG": 25.0,
        "TCT": 8.0, "TCC": 14.0, "TCA": 7.0, "TCG": 10.0,
        "CCT": 8.0, "CCC": 10.0, "CCA": 10.0, "CCG": 16.0,
        "ACT": 8.0, "ACC": 22.0, "ACA": 8.0, "ACG": 12.0,
        "GCT": 14.0, "GCC": 28.0, "GCA": 16.0, "GCG": 22.0,
        "TAT": 10.0, "TAC": 16.0, "TAA": 1.5, "TAG": 0.5,
        "CAT": 9.0, "CAC": 12.0, "CAA": 14.0, "CAG": 24.0,
        "AAT": 12.0, "AAC": 20.0, "AAA": 22.0, "AAG": 16.0,
        "GAT": 22.0, "GAC": 22.0, "GAA": 30.0, "GAG": 22.0,
        "TGT": 4.0, "TGC": 7.0, "TGA": 1.0, "TGG": 14.0,
        "CGT": 12.0, "CGC": 20.0, "CGA": 5.0, "CGG": 8.0,
        "AGT": 7.0, "AGC": 14.0, "AGA": 3.0, "AGG": 2.0,
        "GGT": 16.0, "GGC": 28.0, "GGA": 10.0, "GGG": 8.0,
    },
}

# Map chassis names to codon table keys
CHASSIS_MAP = {
    "escherichia coli": "e_coli",
    "e. coli": "e_coli",
    "e. coli k-12": "e_coli",
    "pseudomonas putida": "p_putida",
    "p. putida": "p_putida",
    "synechococcus elongatus": "s_elongatus",
    "s. elongatus": "s_elongatus",
    "synechocystis": "s_elongatus",  # close enough
}

STOP_CODONS = {"TAA", "TAG", "TGA"}


def _normalize_chassis_key(chassis: str) -> str:
    """Normalize chassis name to a codon table key using substring matching.
    Handles strain suffixes like 'Pseudomonas putida KT2440'."""
    chassis_lower = chassis.lower().strip()
    if chassis_lower in CHASSIS_MAP:
        return CHASSIS_MAP[chassis_lower]
    for key, table_key in CHASSIS_MAP.items():
        if key in chassis_lower:
            return table_key
    return "e_coli"


def _best_codons_for_chassis(chassis: str) -> dict[str, str]:
    """Build a reverse map: amino acid -> best codon for chassis."""
    key = _normalize_chassis_key(chassis)
    usage = CODON_USAGE[key]
    table = CodonTable.standard_dna_table

    aa_best: dict[str, tuple[str, float]] = {}
    for codon, aa in table.forward_table.items():
        freq = usage.get(codon, 0)
        if aa not in aa_best or freq > aa_best[aa][1]:
            aa_best[aa] = (codon, freq)

    return {aa: codon for aa, (codon, _) in aa_best.items()}


def optimize_protein_to_dna(protein_seq: str, chassis: str = "E. coli") -> dict:
    """
    Codon-optimize a protein sequence for the target chassis organism.
    Returns the optimized DNA coding sequence.
    """
    best_codons = _best_codons_for_chassis(chassis)

    codons = []
    for aa in protein_seq.upper():
        if aa == "*":
            break
        codon = best_codons.get(aa)
        if codon:
            codons.append(codon)

    # Add stop codon (TAA preferred in E. coli, TAG in some others)
    codons.append("TAA")

    optimized_dna = "".join(codons)

    # Calculate CAI-like score (ratio of used codons to best codons)
    key = _normalize_chassis_key(chassis)
    usage = CODON_USAGE[key]
    table = CodonTable.standard_dna_table

    total_score = 0
    for codon in codons[:-1]:  # skip stop
        aa = table.forward_table.get(codon, "")
        if not aa:
            continue
        # Find max freq for this amino acid
        max_freq = max(
            usage.get(c, 0) for c, a in table.forward_table.items() if a == aa
        )
        codon_freq = usage.get(codon, 0)
        if max_freq > 0:
            total_score += codon_freq / max_freq

    cai = total_score / len(codons[:-1]) if codons[:-1] else 0

    # GC content
    gc = (optimized_dna.count("G") + optimized_dna.count("C")) / len(optimized_dna) if optimized_dna else 0

    return {
        "optimized_dna": optimized_dna,
        "length_bp": len(optimized_dna),
        "protein_length_aa": len(protein_seq.rstrip("*")),
        "chassis": chassis,
        "cai_score": round(cai, 3),
        "gc_content": round(gc, 3),
        "stop_codon": "TAA",
    }


def optimize_dna_for_chassis(dna_seq: str, chassis: str = "E. coli") -> dict:
    """
    Re-optimize an existing DNA sequence for a different chassis.
    Translates to protein first, then codon-optimizes.
    """
    seq = Seq(dna_seq.upper().replace(" ", "").replace("\n", ""))
    # Trim to multiple of 3
    trimmed = str(seq[:len(seq) - len(seq) % 3])
    protein = str(Seq(trimmed).translate(to_stop=True))
    return optimize_protein_to_dna(protein, chassis)
