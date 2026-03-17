"""
GenBank format export for Progenx designs.

Generates standard GenBank flat files (.gb) from design output,
including feature annotations for genes, promoters, terminators,
ori, markers, and kill switches.

GenBank is the standard interchange format used by SnapGene,
Benchling, Geneious, ApE, and most molecular biology software.

Reference: NCBI GenBank flat file format specification
https://www.ncbi.nlm.nih.gov/Sitemap/samplerecord.html
"""

from datetime import datetime


def design_to_genbank(
    design_name: str,
    dna_sequence: str,
    genes: list[dict],
    promoters: list[str],
    terminators: list[str],
    assembly: dict,
    host_organism: str = "",
    codon_optimized: dict | None = None,
) -> str:
    """Convert a Progenx design to GenBank flat file format.

    Returns a string in GenBank format that can be saved as .gb and opened
    in SnapGene, Benchling, Geneious, ApE, or any GenBank-compatible tool.
    """
    if not dna_sequence:
        return ""

    seq_len = len(dna_sequence)
    locus_name = design_name.replace(" ", "_")[:16]  # GenBank locus max 16 chars
    date_str = datetime.now().strftime("%d-%b-%Y").upper()
    topology = "circular"

    lines = []

    # LOCUS line
    lines.append(
        f"LOCUS       {locus_name:<16s} {seq_len:>7d} bp    DNA     {topology}   SYN {date_str}"
    )

    # DEFINITION
    lines.append(f"DEFINITION  {design_name}, designed by Progenx.")

    # ACCESSION
    lines.append("ACCESSION   .")

    # VERSION
    lines.append("VERSION     .")

    # KEYWORDS
    lines.append("KEYWORDS    synthetic biology; Progenx; AI-designed.")

    # SOURCE
    if host_organism:
        lines.append(f"SOURCE      {host_organism}")
        lines.append(f"  ORGANISM  {host_organism}")
    else:
        lines.append("SOURCE      synthetic construct")
        lines.append("  ORGANISM  synthetic construct")

    # COMMENT
    lines.append("COMMENT     Designed by Progenx (AI-powered bioengineering platform).")
    lines.append("            EDUCATIONAL/EXPERIMENTAL ONLY — NOT LAB-READY WITHOUT EXPERT REVIEW.")
    lines.append("            Sequences are computational predictions. Lab validation required.")

    # FEATURES
    lines.append("FEATURES             Location/Qualifiers")

    # Source feature (required)
    lines.append(f"     source          1..{seq_len}")
    lines.append(f'                     /organism="{host_organism or "synthetic construct"}"')
    lines.append('                     /mol_type="other DNA"')
    lines.append(f'                     /note="Designed by Progenx"')

    # Track current position for feature placement
    current_pos = 1

    # Promoter features
    for i, prom in enumerate(promoters or []):
        start = 21 + i * 60
        end = start + 49
        if end <= seq_len:
            lines.append(f"     promoter        {start}..{end}")
            lines.append(f'                     /label="{prom}"')
            lines.append(f'                     /note="Promoter: {prom}"')

    # Gene/CDS features
    gene_pos = 101  # start after promoter region
    for i, gene in enumerate(genes or []):
        gene_name = gene.get("name", f"gene_{i}")
        gene_size = gene.get("size_bp", 900)
        gene_start = gene_pos
        gene_end = gene_pos + gene_size - 1
        function = gene.get("function", "")
        source_org = gene.get("source_organism", "")

        if gene_end <= seq_len:
            # Gene feature
            lines.append(f"     gene            {gene_start}..{gene_end}")
            lines.append(f'                     /gene="{gene_name}"')
            if function:
                lines.append(f'                     /note="{function}"')

            # CDS feature
            lines.append(f"     CDS             {gene_start}..{gene_end}")
            lines.append(f'                     /gene="{gene_name}"')
            lines.append(f'                     /codon_start=1')
            if function:
                lines.append(f'                     /product="{function}"')
            if source_org:
                lines.append(f'                     /note="Source: {source_org}"')
            lines.append(f'                     /label="{gene_name}"')

        gene_pos = gene_end + 31  # 30bp spacing for RBS

    # Terminator features
    term_pos = gene_pos + 70
    for i, term in enumerate(terminators or []):
        start = term_pos + i * 40
        end = start + 29
        if end <= seq_len:
            lines.append(f"     terminator      {start}..{end}")
            lines.append(f'                     /label="{term}"')

    # Assembly features (ori, marker, kill switch)
    asm_pos = term_pos + len(terminators or []) * 40 + 100

    # Kill switch
    ks = assembly.get("kill_switch", {})
    if ks:
        ks_size = ks.get("size_bp", 600)
        ks_end = asm_pos + ks_size - 1
        if ks_end <= seq_len:
            lines.append(f"     misc_feature    complement({asm_pos}..{ks_end})")
            ks_name = ks.get("name", "kill switch").split("/")[0].split("(")[0].strip()
            lines.append(f'                     /label="{ks_name}"')
            lines.append(f'                     /note="Biocontainment: {ks.get("mechanism", "")[:80]}"')
        asm_pos = ks_end + 51

    # Selection marker
    marker = assembly.get("selection_marker", {})
    if marker:
        marker_size = marker.get("size_bp", 795)
        marker_end = asm_pos + marker_size - 1
        if marker_end <= seq_len:
            lines.append(f"     CDS             complement({asm_pos}..{marker_end})")
            lines.append(f'                     /gene="{marker.get("gene", "marker")}"')
            lines.append(f'                     /product="{marker.get("name", "selection marker")}"')
            lines.append(f'                     /label="{marker.get("gene", "marker")}"')
        asm_pos = marker_end + 51

    # Origin of replication
    ori = assembly.get("origin_of_replication", {})
    if ori:
        ori_size = ori.get("size_bp", 900)
        ori_end = asm_pos + ori_size - 1
        if ori_end <= seq_len:
            lines.append(f"     rep_origin      {asm_pos}..{ori_end}")
            lines.append(f'                     /label="{ori.get("name", "ori")}"')
            lines.append(f'                     /note="{ori.get("copy_number", "")}"')

    # ORIGIN (sequence data)
    lines.append("ORIGIN")

    # Format sequence in GenBank style: 10-char groups, 6 groups per line
    seq_lower = dna_sequence.lower()
    for i in range(0, len(seq_lower), 60):
        chunk = seq_lower[i:i+60]
        # Split into groups of 10
        groups = [chunk[j:j+10] for j in range(0, len(chunk), 10)]
        line_num = i + 1
        lines.append(f"{line_num:>9d} {' '.join(groups)}")

    lines.append("//")

    return "\n".join(lines) + "\n"
