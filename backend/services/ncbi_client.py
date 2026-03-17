"""
NCBI Entrez client for fetching real gene sequences.

Uses BioPython Bio.Entrez to pull exact CDS from GenBank.
Includes a hardcoded lookup table of common synbio gene accession IDs
for instant retrieval without LLM guessing.

Hardening layers:
- Unsupported biology detection (e.g., no known Li+ selective transporters)
- Organism-filtered NCBI searches
- LLM-based function validation (rejects wrong-protein hits)
- UniProt keyword search fallback stub
"""

import json
from Bio import Entrez, SeqIO
from io import StringIO
from config import settings

Entrez.email = settings.NCBI_EMAIL
if settings.NCBI_API_KEY:
    Entrez.api_key = settings.NCBI_API_KEY


# ── Unsupported biology registry ─────────────────────────────────────
# Functions with no known biological parts. If the intended function
# matches any of these keywords, we return early with a warning instead
# of fetching wrong proteins from NCBI by gene-name collision.
UNSUPPORTED_BIOLOGY: list[dict] = [
    {
        "keywords": [
            "lithium transport", "lithium uptake", "lithium binding",
            "lithium-binding", "lithium concentrat", "lithium extract",
            "lithium antiporter", "li+ transport", "li+ uptake",
            "li+ binding", "lithium-selective", "lithium ion channel",
        ],
        "warning": (
            "No selective Li+ transporters exist in published literature. "
            "Li+ and Na+ are too similar (76 pm vs 102 pm ionic radius) for any "
            "characterized biological system to discriminate at industrial ratios. "
            "This function has no characterized biological parts yet. "
            "Consider: chemical precipitation, ion-exchange resins, or "
            "engineered crown ether-based biosorbents as real alternatives."
        ),
    },
]


def _check_unsupported_biology(intended_function: str) -> str | None:
    """Check if the intended function matches a known unsupported biology case.
    Returns warning message if matched, None otherwise."""
    if not intended_function:
        return None
    func_lower = intended_function.lower()
    for entry in UNSUPPORTED_BIOLOGY:
        for keyword in entry["keywords"]:
            if keyword in func_lower:
                return entry["warning"]
    return None


# ── Hardcoded gene registry ──────────────────────────────────────────
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
    # FIXED March 2026: previous WP_ accessions pointed to wrong proteins
    "rbcl": {
        "accession": "ABB57456.1",  # verified: Form I RuBisCO large subunit, 472 aa
        "organism": "Synechococcus elongatus PCC 7942",
        "description": "RuBisCO large subunit — CO2 fixation (ribulose-1,5-bisphosphate carboxylase/oxygenase)",
        "type": "protein",
        "expected_aa": 472,
    },
    "rbcs": {
        "accession": "Q31NB2",  # UniProt Swiss-Prot: RuBisCO small subunit, 111 aa
        "organism": "Synechococcus elongatus PCC 7942",
        "description": "RuBisCO small subunit — CO2 fixation",
        "type": "protein",
        "expected_aa": 111,
    },
    "ccmk": {
        "accession": "ABB57451.1",  # verified: CcmK2, 102 aa, locus Synpcc7942_1421
        "organism": "Synechococcus elongatus PCC 7942",
        "description": "Carboxysome shell protein CcmK2 — CO2-concentrating mechanism",
        "type": "protein",
        "expected_aa": 102,
    },
    "ccmm": {
        "accession": "ABB57453.1",  # verified: CcmM, 539 aa (full-length CcmM58)
        "organism": "Synechococcus elongatus PCC 7942",
        "description": "Carboxysome scaffolding protein CcmM — organizes RuBisCO in carboxysomes",
        "type": "protein",
        "expected_aa": 539,
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
    # Carbonic anhydrase (E. coli — well-characterized, expressible)
    "cah": {
        "accession": "WP_251761524.1",  # verified: 220 aa carbonate dehydratase, E. coli
        "organism": "Escherichia coli",
        "description": "Carbonic anhydrase (carbonate dehydratase) — CO2 hydration to bicarbonate",
        "type": "protein",
        "expected_aa": 220,
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
    # mazEF toxin-antitoxin (common kill switch, E. coli)
    "maze": {
        "accession": "P0AE72",
        "organism": "Escherichia coli K-12",
        "description": "Antitoxin MazE — neutralizes MazF endoribonuclease toxin",
        "type": "protein",
        "expected_aa": 82,
    },
    "mazf": {
        "accession": "P0AE70",
        "organism": "Escherichia coli K-12",
        "description": "Endoribonuclease toxin MazF — mRNA interferase (cleaves at ACA sequences)",
        "type": "protein",
        "expected_aa": 111,
    },
    # Quorum sensing
    "luxs": {
        "accession": "P45578",
        "organism": "Escherichia coli K-12",
        "description": "S-ribosylhomocysteine lyase (LuxS) — produces AI-2 quorum sensing autoinducer",
        "type": "protein",
        "expected_aa": 171,
    },
    # lac repressor (most common regulatory element in synbio)
    "laci": {
        "accession": "P03023",
        "organism": "Escherichia coli K-12",
        "description": "Lac repressor (LacI) — DNA-binding transcriptional regulator of lac operon",
        "type": "protein",
        "expected_aa": 360,
    },
    # Laccase (bacterial, expressible in E. coli)
    "laccase": {
        "accession": "P07788",
        "organism": "Bacillus subtilis 168",
        "description": "CotA laccase — multicopper oxidase for lignin/phenolic compound degradation",
        "type": "protein",
        "expected_aa": 513,
    },
    # Catalase
    "kate": {
        "accession": "P21179",
        "organism": "Escherichia coli K-12",
        "description": "Catalase HPII — decomposes hydrogen peroxide to water and oxygen",
        "type": "protein",
        "expected_aa": 753,
    },
    # Polyphosphate kinase
    "ppk1": {
        "accession": "P0A7B1",
        "organism": "Escherichia coli K-12",
        "description": "Polyphosphate kinase — polymerizes ATP terminal phosphate into polyphosphate",
        "type": "protein",
        "expected_aa": 688,
    },
}

# Aliases: map ambiguous gene symbols Claude might use to the correct registry key.
# This prevents NCBI gene symbol collisions (e.g., "cutA" → bacterial protein, not cutinase).
GENE_ALIASES: dict[str, str] = {
    "cuta": "cutinase",      # bacterial cutA is NOT fungal cutinase
    "cut": "cutinase",
    "fscutinase": "cutinase",
    "lccase": "laccase",     # common misspelling
    "lcc": "laccase",
    "cota": "laccase",       # CotA = B. subtilis laccase
    "catalase": "kate",      # generic "catalase" → katE
    "ppk": "ppk1",           # common abbreviation
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


# ── LLM function validation ─────────────────────────────────────────

def _validate_function_match(intended_function: str, ncbi_description: str) -> dict:
    """Use LLM to validate if NCBI result matches intended function.
    Returns {"score": float 0-1, "match": bool, "reason": str}."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": (
                    f"Does this protein match the intended biological function?\n\n"
                    f"Intended function: {intended_function}\n"
                    f"NCBI result description: {ncbi_description}\n\n"
                    f"Return ONLY valid JSON: {{\"score\": 0.0-1.0, \"reason\": \"one sentence\"}}\n"
                    f"Score 1.0 = perfect functional match, 0.0 = completely different protein.\n"
                    f"Be strict: a lactate permease is NOT a lithium transporter (score ~0.1)."
                ),
            }],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            if raw.endswith("```"):
                raw = raw[:-3].strip()
        result = json.loads(raw)
        score = float(result.get("score", 0))
        return {
            "score": score,
            "match": score >= 0.7,
            "reason": result.get("reason", ""),
        }
    except Exception as e:
        # If validation fails, be conservative — flag but don't block
        print(f"[NCBI] Function validation error: {e}")
        return {"score": 0.5, "match": True, "reason": f"Validation unavailable: {e}"}


# ── UniProt keyword fallback ────────────────────────────────────────

def search_uniprot_keyword(keyword: str) -> dict:
    """Search UniProt by functional keyword when NCBI gene-name search fails.
    Stub — returns not_found with guidance for manual lookup."""
    # TODO: implement real UniProt API search (https://rest.uniprot.org/uniprotkb/search)
    clean_keyword = keyword.replace(" ", "+")
    return {
        "gene_name": keyword,
        "sequence": "",
        "error": (
            f"UniProt keyword search not yet implemented. "
            f"Manual lookup: https://www.uniprot.org/uniprotkb?query={clean_keyword}"
        ),
        "source": "uniprot_stub",
        "uniprot_url": f"https://www.uniprot.org/uniprotkb?query={clean_keyword}",
    }


# Max protein size for a single pathway enzyme (aa). Anything larger is
# likely a polyprotein, fusion, or wrong hit. Typical synbio genes: 100-1000 aa.
MAX_REASONABLE_PROTEIN_AA = 1500


def fetch_cds_for_gene(
    gene_name: str,
    organism: str = "",
    intended_function: str = "",
    validate_function: bool = True,
) -> dict:
    """
    Fetch the real coding sequence for a gene.

    Strategy:
    0. Check if the intended function is unsupported in biology
    1. Protein accession from hardcoded registry (highest confidence)
    2. Organism-filtered NCBI search + LLM function validation
    3. Unfiltered NCBI search + LLM function validation
    4. UniProt keyword search stub
    5. Return not_found with conceptual_only flag

    Protein sequences are preferred because they get codon-optimized for
    the target chassis anyway, avoiding partial-CDS / whole-genome bugs.
    """
    # Step 0: Check if this function is unsupported in biology
    unsupported_warning = _check_unsupported_biology(intended_function)
    if unsupported_warning:
        print(f"[NCBI] UNSUPPORTED BIOLOGY for {gene_name}: {unsupported_warning}")
        return {
            "gene_name": gene_name,
            "sequence": "",
            "error": unsupported_warning,
            "source": "unsupported_biology",
            "warning": unsupported_warning,
            "conceptual_only": True,
            "confidence": "none",
            "confidence_reason": "No known biological parts exist for this function.",
        }

    # Step 1: Check hardcoded registry (highest confidence)
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
                result["function"] = entry["description"]
                result["source"] = "ncbi_registry"
                result["confidence"] = "high"
                result["confidence_reason"] = (
                    f"Verified accession {entry['accession']} from curated registry. "
                    f"Expected ~{expected_aa} aa, got {result['length']} aa."
                )
                return result

    # Step 2: Organism-filtered NCBI search
    if organism:
        result = search_ncbi_gene(gene_name, organism=organism)
        if result.get("source") == "ncbi_search" and result.get("sequence"):
            if intended_function and validate_function:
                validation = _validate_function_match(
                    intended_function, result.get("description", "")
                )
                result["function_validation"] = validation
                if not validation["match"]:
                    print(
                        f"[NCBI] FUNCTION MISMATCH for {gene_name}: "
                        f"intended='{intended_function}', "
                        f"got='{result.get('description', '')}' "
                        f"(score={validation['score']:.2f}: {validation['reason']})"
                    )
                    # Don't return — fall through to unfiltered search
                else:
                    result["confidence"] = "medium"
                    result["confidence_reason"] = (
                        f"NCBI search filtered by organism '{organism}'. "
                        f"LLM validation score: {validation['score']:.0%}."
                    )
                    return result
            else:
                result["confidence"] = "low"
                result["confidence_reason"] = (
                    f"NCBI search filtered by organism '{organism}'. "
                    f"No LLM function validation performed (free tier)."
                )
                return result

    # Step 3: Unfiltered NCBI search (broader, less precise)
    result = search_ncbi_gene(gene_name)
    if result.get("source") == "ncbi_search" and result.get("sequence"):
        if intended_function and validate_function:
            validation = _validate_function_match(
                intended_function, result.get("description", "")
            )
            result["function_validation"] = validation
            if not validation["match"]:
                print(
                    f"[NCBI] FUNCTION MISMATCH for {gene_name} (unfiltered): "
                    f"intended='{intended_function}', "
                    f"got='{result.get('description', '')}' "
                    f"(score={validation['score']:.2f}: {validation['reason']})"
                )
                # Fall through to UniProt stub
            else:
                result["confidence"] = "low"
                result["confidence_reason"] = (
                    f"Unfiltered NCBI search (no organism constraint). "
                    f"LLM validation score: {validation['score']:.0%}. "
                    f"Gene may not be from the intended source organism."
                )
                return result
        else:
            result["confidence"] = "low"
            result["confidence_reason"] = (
                "Unfiltered NCBI search with no organism constraint "
                "and no LLM function validation. Verify manually."
            )
            return result

    # Step 4: UniProt keyword fallback stub
    if intended_function:
        print(f"[NCBI] No valid hit for {gene_name}, trying UniProt keyword: {intended_function}")
        uniprot_result = search_uniprot_keyword(intended_function)
        if uniprot_result.get("sequence"):
            return uniprot_result

    # Step 5: No valid result found
    return {
        "gene_name": gene_name,
        "sequence": "",
        "error": (
            f"No known gene for this function in biology: "
            f"{intended_function or gene_name}. "
            f"NCBI search returned proteins that do not match the intended function."
        ),
        "source": "not_found",
        "conceptual_only": True,
        "confidence": "none",
        "confidence_reason": (
            "Could not find a verified sequence for this gene. "
            "NCBI search results did not match the intended function."
        ),
    }


def search_ncbi_gene(gene_name: str, organism: str = "") -> dict:
    """Search NCBI for a gene by name, optionally filtered by organism.
    Fetches up to 5 hits and picks the first reasonably-sized one."""
    try:
        if organism:
            term = f"{gene_name}[Gene Name] AND {organism}[Organism]"
        else:
            term = f"{gene_name}[Gene Name]"

        handle = Entrez.esearch(db="protein", term=term, retmax=5)
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
                result["search_organism"] = organism or "any"
                return result
    except Exception:
        pass

    return {
        "gene_name": gene_name,
        "sequence": "",
        "error": f"Could not find sequence for {gene_name}" + (f" in {organism}" if organism else ""),
        "source": "not_found",
    }


def fetch_genes_batch(
    genes: list[dict | str],
    validate_function: bool = True,
) -> dict[str, dict]:
    """Fetch sequences for multiple genes, using registry for speed.
    Accepts either gene name strings or gene dicts with
    'name', 'source_organism', 'function' keys.
    Set validate_function=False to skip LLM validation calls (free tier)."""
    results = {}
    for gene in genes:
        if isinstance(gene, str):
            name = gene
            organism = ""
            function = ""
        else:
            name = gene.get("name", "")
            organism = gene.get("source_organism", "")
            function = gene.get("function", "")
        results[name] = fetch_cds_for_gene(
            name, organism=organism, intended_function=function,
            validate_function=validate_function,
        )
    return results
