"""
SBOL3 Export — Standard exchange format for synthetic biology designs.

Exports Progenx designs to SBOL3 (Synthetic Biology Open Language v3),
the standard used by iGEM, Benchling, and the synbio community.

SBOL3 files can be imported into:
  - Benchling (via SBOL import)
  - SynBioHub (community repository)
  - SBOL Visual tools
  - iGEM Registry submissions

Uses pySBOL3 (pip install sbol3).
"""

import json
import tempfile
import os

try:
    import sbol3
    SBOL_AVAILABLE = True
except ImportError:
    SBOL_AVAILABLE = False


# Sequence Ontology URIs for part types
SO = "https://identifiers.org/SO:"
PART_TYPE_MAP = {
    "promoter": f"{SO}0000167",
    "rbs": f"{SO}0000139",
    "cds": f"{SO}0000316",
    "terminator": f"{SO}0000141",
    "gene": f"{SO}0000704",
    "origin_of_replication": f"{SO}0000296",
    "operator": f"{SO}0000057",
    "insulator": f"{SO}0000627",
    "engineered_region": f"{SO}0000804",
}

# Systems Biology Ontology for roles
SBO = "https://identifiers.org/SBO:"
ROLE_MAP = {
    "kill_switch": f"{SBO}0000642",  # inhibitor
    "reporter": f"{SBO}0000011",  # product
    "resistance": f"{SBO}0000642",  # inhibitor
}


def export_design_sbol3(
    design_name: str,
    host_organism: str,
    gene_circuit: dict,
    dna_sequence: str,
    gene_sequences: dict,
    assembly_plan: dict,
    safety_score: float,
    design_id: str = "",
) -> str | None:
    """Export a Progenx design to SBOL3 format.

    Returns SBOL3 content as a string (sorted N-Triples RDF format),
    or None if pySBOL3 is not available.
    """
    if not SBOL_AVAILABLE:
        return None

    # Namespace for this design
    namespace = "https://progenx.ai/designs/"
    sbol3.set_namespace(namespace)

    doc = sbol3.Document()

    # Sanitize design name for use as display_id (SBOL3 requires alphanumeric + underscore)
    safe_name = "".join(c if c.isalnum() else "_" for c in design_name)[:50] or "design"

    # Create the main plasmid component
    plasmid = sbol3.Component(
        identity=f"{namespace}{safe_name}",
        types=[sbol3.SBO_DNA],
    )
    plasmid.name = design_name
    plasmid.description = f"Designed by Progenx for {host_organism}. Safety score: {safety_score:.0%}."
    if design_id:
        plasmid.description += f" Progenx ID: {design_id}"

    # Add the full DNA sequence
    if dna_sequence:
        seq = sbol3.Sequence(
            identity=f"{namespace}{safe_name}_seq",
            elements=dna_sequence.upper(),
            encoding=sbol3.IUPAC_DNA_ENCODING,
        )
        doc.add(seq)
        plasmid.sequences.append(seq)

    # Add gene features from the circuit
    genes = gene_circuit.get("genes", [])
    position = 1  # running bp position

    for i, gene in enumerate(genes):
        gene_name = gene.get("name", f"gene_{i}")
        safe_gene = "".join(c if c.isalnum() else "_" for c in gene_name)

        # Determine part type
        gene_func = gene.get("function", "").lower()
        if "promoter" in gene_func:
            part_type = PART_TYPE_MAP["promoter"]
        elif "terminator" in gene_func:
            part_type = PART_TYPE_MAP["terminator"]
        elif "rbs" in gene_func or "ribosome" in gene_func:
            part_type = PART_TYPE_MAP["rbs"]
        else:
            part_type = PART_TYPE_MAP["cds"]

        # Get sequence length from gene_sequences if available
        gene_data = gene_sequences.get(gene_name, {})
        if isinstance(gene_data, str):
            try:
                gene_data = json.loads(gene_data)
            except (json.JSONDecodeError, TypeError):
                gene_data = {}

        seq_len = gene_data.get("length", gene.get("size_bp", 1000))
        if isinstance(seq_len, str):
            try:
                seq_len = int(seq_len)
            except ValueError:
                seq_len = 1000

        # Create a SubComponent for this gene
        gene_component = sbol3.Component(
            identity=f"{namespace}{safe_gene}",
            types=[sbol3.SBO_DNA],
            roles=[part_type],
        )
        gene_component.name = gene_name
        gene_component.description = gene.get("function", "")

        # Add individual gene sequence if available
        raw_seq = gene_data.get("raw_sequence", "")
        if raw_seq and len(raw_seq) > 10:
            gene_seq = sbol3.Sequence(
                identity=f"{namespace}{safe_gene}_seq",
                elements=raw_seq[:5000],
                encoding=sbol3.IUPAC_DNA_ENCODING if _is_dna(raw_seq) else sbol3.IUPAC_PROTEIN_ENCODING,
            )
            doc.add(gene_seq)
            gene_component.sequences.append(gene_seq)

        doc.add(gene_component)

        # Add as SubComponent of the plasmid with location
        sub = sbol3.SubComponent(
            instance_of=gene_component,
        )
        end_pos = position + seq_len - 1
        sub.locations.append(sbol3.Range(
            sequence=plasmid.sequences[0] if plasmid.sequences else None,
            start=position,
            end=end_pos,
        ))
        plasmid.features.append(sub)
        position = end_pos + 1

    # Add regulatory elements
    promoters = gene_circuit.get("promoters", [])
    for prom in promoters:
        if prom:
            safe_prom = "".join(c if c.isalnum() else "_" for c in prom)
            prom_comp = sbol3.Component(
                identity=f"{namespace}promoter_{safe_prom}",
                types=[sbol3.SBO_DNA],
                roles=[PART_TYPE_MAP["promoter"]],
            )
            prom_comp.name = prom
            doc.add(prom_comp)

    terminators = gene_circuit.get("terminators", [])
    for term in terminators:
        if term:
            safe_term = "".join(c if c.isalnum() else "_" for c in term)
            term_comp = sbol3.Component(
                identity=f"{namespace}terminator_{safe_term}",
                types=[sbol3.SBO_DNA],
                roles=[PART_TYPE_MAP["terminator"]],
            )
            term_comp.name = term
            doc.add(term_comp)

    # Add assembly metadata
    if assembly_plan:
        ori = assembly_plan.get("origin_of_replication", {})
        if ori.get("name"):
            safe_ori = "".join(c if c.isalnum() else "_" for c in ori["name"])
            ori_comp = sbol3.Component(
                identity=f"{namespace}ori_{safe_ori}",
                types=[sbol3.SBO_DNA],
                roles=[PART_TYPE_MAP["origin_of_replication"]],
            )
            ori_comp.name = ori["name"]
            ori_comp.description = ori.get("rationale", "")
            doc.add(ori_comp)

    doc.add(plasmid)

    # Serialize to sorted N-Triples (standard SBOL3 exchange format)
    tmp = tempfile.mktemp(suffix=".nt")
    try:
        doc.write(tmp, sbol3.SORTED_NTRIPLES)
        with open(tmp, "r") as f:
            return f.read()
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _is_dna(seq: str) -> bool:
    """Check if a sequence is DNA (vs protein)."""
    dna_chars = set("ATCGN")
    return len(set(seq.upper()) - dna_chars) == 0
