"""
NCBI Entrez client for fetching real gene sequences.

Uses BioPython Bio.Entrez to pull exact CDS from GenBank.
Includes a hardcoded lookup table of common synbio gene accession IDs
for instant retrieval without LLM guessing.
"""

from Bio import Entrez, SeqIO
from io import StringIO
from config import settings

Entrez.email = settings.NCBI_EMAIL
if settings.NCBI_API_KEY:
    Entrez.api_key = settings.NCBI_API_KEY

# Hardcoded accession IDs for common synthetic biology genes.
# Prefer protein accessions — they get codon-optimized for the chassis anyway,
# avoiding partial/whole-genome nucleotide fetch bugs.
# expected_aa: expected protein length for post-fetch validation.
# description: authoritative label (overrides whatever NCBI returns).
GENE_REGISTRY: dict[str, dict] = {
    # PET degradation (Ideonella sakaiensis 201-F6, Yoshida et al. 2016 Science)
    "petase": {
        "accession": "GAP38373.1",  # full 290 aa PETase
        "organism": "Ideonella sakaiensis 201-F6",
        "description": "PET hydrolase (PETase/IsPETase) — hydrolyzes PET to MHET",
        "type": "protein",
        "expected_aa": 290,
    },
    "mhetase": {
        "accession": "A0A0K8P8E7",  # UniProt full-length MHETase (~600 aa)
        "organism": "Ideonella sakaiensis 201-F6",
        "description": "MHET hydrolase — hydrolyzes MHET to TPA + ethylene glycol",
        "type": "protein",
        "expected_aa": 600,
    },
    # PHA bioplastic biosynthesis (Cupriavidus necator / Ralstonia eutropha)
    # From phaCAB operon (J04987). NCBI annotations on these old accessions
    # have swapped labels — we override descriptions with correct assignments.
    "phaa": {
        "accession": "P14611",  # UniProt beta-ketothiolase (phaA) ~394 aa
        "organism": "Cupriavidus necator (Ralstonia eutropha)",
        "description": "Beta-ketothiolase (PhaA) — acetyl-CoA to acetoacetyl-CoA",
        "type": "protein",
        "expected_aa": 394,
    },
    "phab": {
        "accession": "P14697",  # UniProt acetoacetyl-CoA reductase (phaB) ~246 aa
        "organism": "Cupriavidus necator",
        "description": "Acetoacetyl-CoA reductase (PhaB) — NADPH-dependent reduction",
        "type": "protein",
        "expected_aa": 246,
    },
    "phac": {
        "accession": "P23608",  # UniProt PHA synthase (phaC) ~589 aa
        "organism": "Cupriavidus necator",
        "description": "PHA synthase (PhaC) — polymerizes 3HB-CoA to PHB",
        "type": "protein",
        "expected_aa": 589,
    },
    # Carbon fixation (Synechococcus elongatus PCC 7942)
    "rbcl": {
        "accession": "WP_011243425.1",
        "organism": "Synechococcus elongatus PCC 7942",
        "description": "RuBisCO large subunit — CO2 fixation",
        "type": "protein",
        "expected_aa": 470,
    },
    "rbcs": {
        "accession": "WP_011243426.1",
        "organism": "Synechococcus elongatus PCC 7942",
        "description": "RuBisCO small subunit",
        "type": "protein",
        "expected_aa": 113,
    },
    "ccmk": {
        "accession": "WP_011378036.1",
        "organism": "Synechococcus elongatus PCC 7942",
        "description": "Carboxysome shell protein CcmK2",
        "type": "protein",
        "expected_aa": 100,
    },
    "ccmm": {
        "accession": "WP_011378041.1",
        "organism": "Synechococcus elongatus PCC 7942",
        "description": "Carboxysome scaffolding protein CcmM",
        "type": "protein",
        "expected_aa": 220,
    },
    # Nitrogen fixation (Klebsiella pneumoniae)
    "nifh": {
        "accession": "AAA25157.1",
        "organism": "Klebsiella pneumoniae",
        "description": "Nitrogenase Fe protein (dinitrogenase reductase)",
        "type": "protein",
        "expected_aa": 296,
    },
    "nifd": {
        "accession": "AAA25159.1",
        "organism": "Klebsiella pneumoniae",
        "description": "Nitrogenase MoFe protein alpha subunit",
        "type": "protein",
        "expected_aa": 480,
    },
    "nifk": {
        "accession": "AAA25161.1",
        "organism": "Klebsiella pneumoniae",
        "description": "Nitrogenase MoFe protein beta subunit",
        "type": "protein",
        "expected_aa": 520,
    },
    # Hydrocarbon degradation
    "alkb": {
        "accession": "CAB54050.1",
        "organism": "Pseudomonas putida GPo1",
        "description": "Alkane hydroxylase — oxidizes medium-chain n-alkanes (C5-C12)",
        "type": "protein",
        "expected_aa": 401,
    },
    # Organophosphate degradation (Horne et al. 2002, canonical opdA)
    "opda": {
        "accession": "AAK85308.1",  # 384 aa phosphotriesterase (Horne et al. 2002)
        "organism": "Agrobacterium radiobacter",
        "description": "Organophosphate-degrading hydrolase (OpdA) — degrades organophosphate pesticides",
        "type": "protein",
        "expected_aa": 384,
    },
    # Cutinase / polyester degradation (Fusarium solani pisi)
    # IMPORTANT: NCBI gene symbol "cutA" collides with bacterial divalent-cation
    # tolerance protein. Use this registry entry to force the correct enzyme.
    "cutinase": {
        "accession": "P00590",  # UniProt Q99174/P00590 mature cutinase ~230 aa
        "organism": "Fusarium solani pisi",
        "description": "Cutinase — serine esterase for polyester/cutin degradation",
        "type": "protein",
        "expected_aa": 230,
    },
    # Carbonic anhydrase
    "cah": {
        "accession": "WP_004224004.1",
        "organism": "Neisseria gonorrhoeae",
        "description": "Carbonic anhydrase — CO2 hydration",
        "type": "protein",
        "expected_aa": 250,
    },
    # Kill switch components
    "ccdb": {
        "accession": "AAA23071.1",
        "organism": "Escherichia coli",
        "description": "CcdB toxin — DNA gyrase inhibitor (kill switch)",
        "type": "protein",
        "expected_aa": 101,
    },
    "ccda": {
        "accession": "AAA23070.1",
        "organism": "Escherichia coli",
        "description": "CcdA antitoxin — neutralizes CcdB",
        "type": "protein",
        "expected_aa": 72,
    },
    # GFP reporter (protein only — nuccore U62637.1 returns whole vector)
    "gfp": {
        "accession": "AAB02576.1",
        "organism": "Aequorea victoria",
        "description": "Green fluorescent protein (reporter)",
        "type": "protein",
        "expected_aa": 238,
    },
}

# Aliases: map ambiguous gene symbols Claude might use to the correct registry key.
# This prevents NCBI gene symbol collisions (e.g., "cutA" → bacterial protein, not cutinase).
GENE_ALIASES: dict[str, str] = {
    "cuta": "cutinase",      # bacterial cutA is NOT fungal cutinase
    "cut": "cutinase",
    "fscutinase": "cutinase",
}


def lookup_gene(gene_name: str) -> dict | None:
    """Check the hardcoded registry for a common synbio gene.
    Also checks GENE_ALIASES to resolve ambiguous gene symbols."""
    key = gene_name.lower().replace("-", "").replace("_", "")
    # Direct match
    entry = GENE_REGISTRY.get(key)
    if entry:
        return entry
    # Alias match (e.g., "cutA" → "cutinase")
    alias_key = GENE_ALIASES.get(key)
    if alias_key:
        print(f"[NCBI] Alias redirect: {gene_name} → {alias_key} (avoiding gene symbol collision)")
        return GENE_REGISTRY.get(alias_key)
    return None


def fetch_protein_sequence(accession: str) -> dict | None:
    """Fetch a protein sequence from NCBI by accession ID."""
    try:
        handle = Entrez.efetch(db="protein", id=accession, rettype="fasta", retmode="text")
        text = handle.read()
        handle.close()
        record = SeqIO.read(StringIO(text), "fasta")
        return {
            "accession": accession,
            "sequence": str(record.seq),
            "length": len(record.seq),
            "description": record.description,
            "type": "protein",
        }
    except Exception as e:
        return {"error": str(e), "accession": accession}


def fetch_nucleotide_sequence(accession: str) -> dict | None:
    """Fetch a nucleotide sequence from NCBI by accession ID."""
    try:
        handle = Entrez.efetch(db="nucleotide", id=accession, rettype="fasta", retmode="text")
        text = handle.read()
        handle.close()
        record = SeqIO.read(StringIO(text), "fasta")
        return {
            "accession": accession,
            "sequence": str(record.seq),
            "length": len(record.seq),
            "description": record.description,
            "type": "nucleotide",
        }
    except Exception as e:
        return {"error": str(e), "accession": accession}


def _validate_protein_length(gene_name: str, length: int, expected_aa: int) -> str | None:
    """Validate fetched protein length against expected range.
    Returns warning message if outside tolerance, None if OK."""
    if not expected_aa:
        return None
    low = expected_aa * 0.5
    high = expected_aa * 1.5
    if length < low:
        return (f"[NCBI] WARNING: {gene_name} returned {length} aa, "
                f"expected ~{expected_aa} aa (too short, <{low:.0f} aa)")
    if length > high:
        return (f"[NCBI] WARNING: {gene_name} returned {length} aa, "
                f"expected ~{expected_aa} aa (too large, >{high:.0f} aa)")
    return None


def fetch_cds_for_gene(gene_name: str) -> dict:
    """
    Fetch the real coding sequence for a gene.
    Strategy: protein accession (registry) → NCBI search → not_found.
    Protein sequences are preferred because they get codon-optimized for
    the target chassis anyway, avoiding partial-CDS / whole-genome bugs.
    Post-fetch validation checks length against expected range.
    """
    entry = lookup_gene(gene_name)
    if entry:
        result = fetch_protein_sequence(entry["accession"])
        if result and "error" not in result:
            expected_aa = entry.get("expected_aa", 0)
            warning = _validate_protein_length(gene_name, result["length"], expected_aa)
            if warning:
                print(warning + " — trying NCBI search fallback.")
            else:
                result["gene_name"] = gene_name
                result["organism"] = entry["organism"]
                # Use registry description (authoritative) instead of NCBI's
                result["function"] = entry["description"]
                result["source"] = "ncbi_registry"
                return result

    # Not in registry or registry fetch failed — search NCBI
    return search_ncbi_gene(gene_name)


# Max protein size for a single pathway enzyme (aa). Anything larger is
# likely a polyprotein, fusion, or wrong hit. Typical synbio genes: 100-1000 aa.
MAX_REASONABLE_PROTEIN_AA = 1500


def search_ncbi_gene(gene_name: str) -> dict:
    """Search NCBI for a gene by name and return the best CDS result.
    Fetches up to 5 hits and picks the first reasonably-sized one."""
    try:
        handle = Entrez.esearch(db="protein", term=f"{gene_name}[Gene Name]", retmax=5)
        results = Entrez.read(handle)
        handle.close()

        for acc_id in results.get("IdList", []):
            result = fetch_protein_sequence(acc_id)
            if result and "error" not in result:
                # Skip absurdly large proteins (polyproteins, wrong hits)
                if result["length"] > MAX_REASONABLE_PROTEIN_AA:
                    print(f"[NCBI] Skipping {gene_name} hit {acc_id}: "
                          f"{result['length']} aa exceeds {MAX_REASONABLE_PROTEIN_AA} aa max")
                    continue
                result["gene_name"] = gene_name
                result["source"] = "ncbi_search"
                return result
    except Exception:
        pass

    return {
        "gene_name": gene_name,
        "sequence": "",
        "error": f"Could not find sequence for {gene_name}",
        "source": "not_found",
    }


def fetch_genes_batch(gene_names: list[str]) -> dict[str, dict]:
    """Fetch sequences for multiple genes, using registry for speed."""
    results = {}
    for name in gene_names:
        results[name] = fetch_cds_for_gene(name)
    return results
