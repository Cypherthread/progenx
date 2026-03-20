"""
SBOL3 Export — Standard exchange format for synthetic biology designs.

Exports Progenx designs to SBOL3 (Synthetic Biology Open Language v3),
the standard used by the synbio community for part exchange.

SBOL3 files can be imported into:
  - SynBioHub (community repository — native SBOL3 support)
  - SBOL Visual tools (e.g., VisBOL, SBOLDesigner)
  - Other SBOL3-compatible tools

Note: Benchling, iGEM Registry, and SnapGene use SBOL2 or GenBank format.
For those tools, use sbol_utilities to convert SBOL3 -> SBOL2, or export
GenBank format separately.

Uses pySBOL3 (pip install sbol3).
"""

import json
import logging
import tempfile
import os
import threading

try:
    import sbol3
    SBOL_AVAILABLE = True
except ImportError:
    SBOL_AVAILABLE = False

logger = logging.getLogger(__name__)

# Lock to protect sbol3.set_namespace() global state from concurrent access
_namespace_lock = threading.Lock()

# Sequence Ontology URIs for part types
SO = "https://identifiers.org/SO:"
PART_TYPE_MAP = {
    "promoter": f"{SO}0000167",       # SO:0000167 promoter
    "rbs": f"{SO}0000139",            # SO:0000139 ribosome_entry_site
    "cds": f"{SO}0000316",            # SO:0000316 CDS
    "terminator": f"{SO}0000141",     # SO:0000141 terminator
    "gene": f"{SO}0000316",           # Map "gene" to CDS — in synbio context, genes are coding sequences
    "origin_of_replication": f"{SO}0000296",  # SO:0000296 origin_of_replication
    "operator": f"{SO}0000057",       # SO:0000057 operator
    "insulator": f"{SO}0000627",      # SO:0000627 insulator
    "engineered_region": f"{SO}0000804",  # SO:0000804 engineered_region
    "resistance_marker": f"{SO}0001645",  # SO:0001645 antibiotic_resistant
    "selectable_marker": f"{SO}0001645",  # alias
    "enhancer": f"{SO}0000165",       # SO:0000165 enhancer
    "5_utr": f"{SO}0000204",          # SO:0000204 five_prime_UTR
    "3_utr": f"{SO}0000205",          # SO:0000205 three_prime_UTR
    "signal_peptide": f"{SO}0000418", # SO:0000418 signal_peptide
}

# Systems Biology Ontology for interaction roles
SBO = "https://identifiers.org/SBO:"
ROLE_MAP = {
    "kill_switch": f"{SBO}0000020",   # SBO:0000020 inhibitor
    "reporter": f"{SBO}0000011",      # SBO:0000011 product
    "resistance": f"{SBO}0000020",    # SBO:0000020 inhibitor
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
    output_format: str = "turtle",
) -> str | None:
    """Export a Progenx design to SBOL3 format.

    Args:
        output_format: "turtle" (default, .ttl) or "ntriples" (.nt) or "jsonld" (.jsonld)

    Returns SBOL3 content as a string, or None if pySBOL3 is not available.
    """
    if not SBOL_AVAILABLE:
        return None

    # Per-design namespace prevents identity collisions across designs
    design_slug = design_id or "unknown"
    namespace = f"https://progenx.ai/designs/{design_slug}/"

    # Protect global namespace state from concurrent requests
    with _namespace_lock:
        sbol3.set_namespace(namespace)
        doc = _build_document(
            namespace, design_name, host_organism, gene_circuit,
            dna_sequence, gene_sequences, assembly_plan, safety_score,
            design_id,
        )

    # Choose serialization format
    format_map = {
        "turtle": (sbol3.TURTLE, ".ttl"),
        "ntriples": (sbol3.SORTED_NTRIPLES, ".nt"),
        "jsonld": (sbol3.JSONLD, ".jsonld"),
    }
    sbol_format, suffix = format_map.get(output_format, (sbol3.TURTLE, ".ttl"))

    # Validate before writing
    report = doc.validate()
    if report:
        for issue in report:
            logger.warning("SBOL3 validation: %s", issue)

    # Use NamedTemporaryFile (not deprecated mktemp) for safe temp file handling
    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as tmp:
        tmp_path = tmp.name
    try:
        doc.write(tmp_path, sbol_format)
        with open(tmp_path, "r") as f:
            return f.read()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _build_document(
    namespace: str,
    design_name: str,
    host_organism: str,
    gene_circuit: dict,
    dna_sequence: str,
    gene_sequences: dict,
    assembly_plan: dict,
    safety_score: float,
    design_id: str,
) -> "sbol3.Document":
    """Build the SBOL3 Document object. Separated for testability."""
    doc = sbol3.Document()

    # Sanitize design name for use as display_id (SBOL3 requires alphanumeric + underscore)
    safe_name = _sanitize_display_id(design_name) or "design"

    # Track used identities to avoid duplicate crashes
    _used_identities: set[str] = set()

    def _unique_identity(base: str) -> str:
        """Return a unique identity, appending _2, _3, etc. if needed."""
        identity = f"{namespace}{base}"
        if identity not in _used_identities:
            _used_identities.add(identity)
            return identity
        counter = 2
        while f"{identity}_{counter}" in _used_identities:
            counter += 1
        unique = f"{identity}_{counter}"
        _used_identities.add(unique)
        return unique

    # Create the main plasmid component with circular topology
    plasmid_identity = _unique_identity(safe_name)
    plasmid = sbol3.Component(
        identity=plasmid_identity,
        types=[sbol3.SBO_DNA, sbol3.SO_CIRCULAR],
    )
    plasmid.name = design_name
    plasmid.description = (
        f"Designed by Progenx for {host_organism}. "
        f"Safety score: {safety_score:.0%}."
    )
    if design_id:
        plasmid.description += f" Progenx ID: {design_id}"

    # Add the full DNA sequence
    has_parent_seq = False
    if dna_sequence and len(dna_sequence.strip()) > 0:
        seq_identity = _unique_identity(f"{safe_name}_seq")
        seq = sbol3.Sequence(
            identity=seq_identity,
            elements=dna_sequence.upper(),
            encoding=sbol3.IUPAC_DNA_ENCODING,
        )
        doc.add(seq)
        plasmid.sequences.append(seq)
        has_parent_seq = True

    # Add gene features from the circuit as SubComponents of the plasmid
    genes = gene_circuit.get("genes", [])
    position = 1  # running bp position (SBOL3 Range is 1-based, inclusive both ends)

    for i, gene in enumerate(genes):
        gene_name = gene.get("name", f"gene_{i}")
        safe_gene = _sanitize_display_id(gene_name) or f"gene_{i}"

        # Determine part type from function annotation
        gene_func = gene.get("function", "").lower()
        if "promoter" in gene_func:
            part_type = PART_TYPE_MAP["promoter"]
        elif "terminator" in gene_func:
            part_type = PART_TYPE_MAP["terminator"]
        elif "rbs" in gene_func or "ribosome" in gene_func:
            part_type = PART_TYPE_MAP["rbs"]
        else:
            part_type = PART_TYPE_MAP["cds"]

        # Get sequence data
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

        # Determine if this gene's raw sequence is DNA or protein
        raw_seq = gene_data.get("raw_sequence", "") if isinstance(gene_data, dict) else ""
        is_dna = _is_dna(raw_seq) if raw_seq else True

        # Create Component for this gene with correct type
        gene_identity = _unique_identity(safe_gene)
        gene_component = sbol3.Component(
            identity=gene_identity,
            types=[sbol3.SBO_DNA if is_dna else sbol3.SBO_PROTEIN],
            roles=[part_type],
        )
        gene_component.name = gene_name
        gene_component.description = gene.get("function", "")

        # Add individual gene sequence if available
        if raw_seq and len(raw_seq) > 10:
            if len(raw_seq) > 50000:
                logger.warning(
                    "Gene %s sequence truncated from %d to 50000 chars for SBOL3 export",
                    gene_name, len(raw_seq),
                )
            gene_seq_identity = _unique_identity(f"{safe_gene}_seq")
            gene_seq = sbol3.Sequence(
                identity=gene_seq_identity,
                elements=raw_seq[:50000].upper(),
                encoding=sbol3.IUPAC_DNA_ENCODING if is_dna else sbol3.IUPAC_PROTEIN_ENCODING,
            )
            doc.add(gene_seq)
            gene_component.sequences.append(gene_seq)

        doc.add(gene_component)

        # Add as SubComponent of the plasmid with location (only if parent sequence exists)
        sub = sbol3.SubComponent(instance_of=gene_component)
        if has_parent_seq:
            end_pos = position + seq_len - 1
            sub.locations.append(sbol3.Range(
                sequence=plasmid.sequences[0],
                start=position,
                end=end_pos,
            ))
            position = end_pos + 1
        plasmid.features.append(sub)

    # Add regulatory elements as SubComponents (not disconnected top-level Components)
    promoters = gene_circuit.get("promoters", [])
    for prom in promoters:
        if not prom:
            continue
        safe_prom = _sanitize_display_id(prom) or "promoter"
        prom_identity = _unique_identity(f"promoter_{safe_prom}")
        prom_comp = sbol3.Component(
            identity=prom_identity,
            types=[sbol3.SBO_DNA],
            roles=[PART_TYPE_MAP["promoter"]],
        )
        prom_comp.name = prom
        doc.add(prom_comp)
        # Link to plasmid as SubComponent (no location — position unknown)
        prom_sub = sbol3.SubComponent(instance_of=prom_comp)
        plasmid.features.append(prom_sub)

    terminators = gene_circuit.get("terminators", [])
    for term in terminators:
        if not term:
            continue
        safe_term = _sanitize_display_id(term) or "terminator"
        term_identity = _unique_identity(f"terminator_{safe_term}")
        term_comp = sbol3.Component(
            identity=term_identity,
            types=[sbol3.SBO_DNA],
            roles=[PART_TYPE_MAP["terminator"]],
        )
        term_comp.name = term
        doc.add(term_comp)
        # Link to plasmid as SubComponent
        term_sub = sbol3.SubComponent(instance_of=term_comp)
        plasmid.features.append(term_sub)

    # Add assembly metadata (ori, resistance marker) as SubComponents
    if assembly_plan:
        ori = assembly_plan.get("origin_of_replication", {})
        if isinstance(ori, dict) and ori.get("name"):
            safe_ori = _sanitize_display_id(ori["name"]) or "ori"
            ori_identity = _unique_identity(f"ori_{safe_ori}")
            ori_comp = sbol3.Component(
                identity=ori_identity,
                types=[sbol3.SBO_DNA],
                roles=[PART_TYPE_MAP["origin_of_replication"]],
            )
            ori_comp.name = ori["name"]
            ori_comp.description = ori.get("rationale", "")
            doc.add(ori_comp)
            ori_sub = sbol3.SubComponent(instance_of=ori_comp)
            plasmid.features.append(ori_sub)

        marker = assembly_plan.get("selection_marker", assembly_plan.get("resistance_marker", {}))
        if isinstance(marker, dict) and marker.get("name"):
            safe_marker = _sanitize_display_id(marker["name"]) or "marker"
            marker_identity = _unique_identity(f"marker_{safe_marker}")
            marker_comp = sbol3.Component(
                identity=marker_identity,
                types=[sbol3.SBO_DNA],
                roles=[PART_TYPE_MAP["resistance_marker"]],
            )
            marker_comp.name = marker["name"]
            marker_comp.description = marker.get("rationale", "")
            doc.add(marker_comp)
            marker_sub = sbol3.SubComponent(instance_of=marker_comp)
            plasmid.features.append(marker_sub)

    doc.add(plasmid)
    return doc


def _sanitize_display_id(name: str) -> str:
    """Sanitize a name for use as an SBOL3 displayId.

    SBOL3 requires displayId to match [a-zA-Z_][a-zA-Z0-9_]*.
    """
    sanitized = "".join(c if c.isalnum() or c == "_" else "_" for c in name)[:50]
    # Ensure it starts with a letter or underscore (not a digit)
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"
    return sanitized


def _is_dna(seq: str) -> bool:
    """Check if a sequence is DNA (vs protein).

    Recognizes full IUPAC DNA alphabet including ambiguity codes:
    A, T, C, G, N, R, Y, S, W, K, M, B, D, H, V
    """
    if not seq:
        return True  # Empty sequence defaults to DNA context
    iupac_dna_chars = set("ATCGNRYSWKMBDHV")
    return len(set(seq.upper()) - iupac_dna_chars) == 0
