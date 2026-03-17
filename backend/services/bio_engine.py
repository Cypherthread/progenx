"""
Biology engine: BioPython + RDKit validation, metabolic analysis,
and external API integrations (NCBI BLAST, iGEM, UniProt, AlphaFold).
"""

from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction, molecular_weight
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
import io
import httpx
from config import settings


def analyze_sequence(dna_sequence: str) -> dict:
    """Analyze a DNA sequence using BioPython."""
    seq = Seq(dna_sequence.upper().replace(" ", "").replace("\n", ""))

    protein = seq.translate(to_stop=True) if len(seq) >= 3 else Seq("")

    return {
        "length_bp": len(seq),
        "gc_content": round(gc_fraction(seq), 3),
        "molecular_weight_da": round(molecular_weight(seq, "DNA"), 1) if len(seq) > 0 else 0,
        "protein_length_aa": len(protein),
        "protein_sequence": str(protein)[:500],
        "has_start_codon": str(seq[:3]).upper() == "ATG",
        "has_stop_codon": str(seq[-3:]).upper() in ("TAA", "TAG", "TGA"),
        "codon_count": len(seq) // 3,
    }


def generate_fasta(sequence: str, name: str, description: str = "") -> str:
    """Generate FASTA formatted string."""
    record = SeqRecord(
        Seq(sequence),
        id=name.replace(" ", "_").lower(),
        name=name,
        description=description or f"Progenx design: {name}",
    )
    output = io.StringIO()
    SeqIO.write(record, output, "fasta")
    return output.getvalue()


def search_igem_parts(part_name: str) -> list[dict]:
    """Search iGEM Parts Registry for standard biological parts."""
    try:
        url = f"{settings.IGEM_REGISTRY_URL}?part={part_name}"
        with httpx.Client(timeout=30) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                return [{"source": "iGEM", "part": part_name, "data": resp.text[:1000]}]
    except Exception:
        pass
    return []


def search_uniprot(query: str, limit: int = 5) -> list[dict]:
    """Search UniProt for protein information."""
    try:
        url = f"{settings.UNIPROT_URL}/uniprotkb/search"
        params = {"query": query, "format": "json", "size": limit}
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for entry in data.get("results", [])[:limit]:
                    results.append({
                        "accession": entry.get("primaryAccession", ""),
                        "name": entry.get("proteinDescription", {})
                            .get("recommendedName", {})
                            .get("fullName", {})
                            .get("value", "Unknown"),
                        "organism": entry.get("organism", {}).get("scientificName", ""),
                        "length": entry.get("sequence", {}).get("length", 0),
                    })
                return results
    except Exception:
        pass
    return []


def get_alphafold_structure(uniprot_id: str) -> dict | None:
    """Get AlphaFold predicted structure info for a UniProt ID."""
    try:
        url = f"{settings.ALPHAFOLD_URL}/prediction/{uniprot_id}"
        with httpx.Client(timeout=30) as client:
            resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list) and data:
                    entry = data[0]
                    return {
                        "uniprot_id": uniprot_id,
                        "pdb_url": entry.get("pdbUrl", ""),
                        "confidence": entry.get("confidenceAvg", 0),
                    }
    except Exception:
        pass
    return None


def estimate_metabolic_yield(
    organism_type: str,
    pathway_genes: list[str],
    environment: str,
) -> dict:
    """
    Simple metabolic flux estimation based on pathway complexity.
    Uses heuristics — real flux balance analysis would need COBRApy + a genome-scale model.
    """
    base_yields = {
        "ocean": {"growth_rate": 0.3, "product_yield": 0.15, "unit": "g/L/day"},
        "soil": {"growth_rate": 0.5, "product_yield": 0.25, "unit": "g/L/day"},
        "gut": {"growth_rate": 0.8, "product_yield": 0.35, "unit": "g/L/day"},
        "lab": {"growth_rate": 1.0, "product_yield": 0.5, "unit": "g/L/day"},
    }

    base = base_yields.get(environment, base_yields["lab"])
    gene_count = len(pathway_genes)

    # More genes = more metabolic burden = lower yield
    burden_factor = max(0.3, 1.0 - (gene_count * 0.08))

    return {
        "estimated_growth_rate": round(base["growth_rate"] * burden_factor, 3),
        "estimated_product_yield": round(base["product_yield"] * burden_factor, 3),
        "unit": base["unit"],
        "metabolic_burden": round(1.0 - burden_factor, 2),
        "pathway_genes": gene_count,
        "note": "Heuristic estimate. Real yields require wet-lab validation.",
    }


def validate_with_rdkit(smiles: str) -> dict | None:
    """Validate a chemical structure with RDKit (for metabolic products)."""
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {"valid": False, "error": "Invalid SMILES"}

        return {
            "valid": True,
            "molecular_weight": round(Descriptors.MolWt(mol), 2),
            "logP": round(Descriptors.MolLogP(mol), 2),
            "num_atoms": mol.GetNumAtoms(),
            "formula": Chem.rdMolDescriptors.CalcMolFormula(mol),
        }
    except ImportError:
        return None
