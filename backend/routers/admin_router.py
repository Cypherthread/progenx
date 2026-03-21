# TEMPORARY — remove after seeding production

import os
import json
import uuid
import random
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Header
from sqlalchemy.orm import Session
from fastapi import Depends

from database import get_db
from models import User, Design, AuditLog

router = APIRouter()

SHOWCASE_EMAIL = "showcase@progenx.ai"
SHOWCASE_NAME = "ProGenX Team"


def _require_admin(x_admin_secret: str = Header(...)):
    """Validate admin secret from request header."""
    expected = os.getenv("ADMIN_SECRET", "")
    if not expected:
        raise HTTPException(status_code=503, detail="ADMIN_SECRET not configured")
    if x_admin_secret != expected:
        raise HTTPException(status_code=403, detail="Invalid admin secret")


def _generate_dna(length: int, seed: int) -> str:
    rng = random.Random(seed)
    return "".join(rng.choice("ATCG") for _ in range(length))


@router.post("/seed-explore")
def seed_explore(db: Session = Depends(get_db), _auth=Depends(_require_admin)):
    """One-time seed of Explore gallery. Idempotent — skips if already seeded."""

    # Idempotency check
    existing_user = db.query(User).filter(User.email == SHOWCASE_EMAIL).first()
    if existing_user:
        count = db.query(Design).filter(Design.user_id == existing_user.id).count()
        if count > 0:
            return {
                "status": "already_seeded",
                "message": f"{count} showcase designs already exist",
                "user_id": existing_user.id,
            }

    # Create showcase user
    import bcrypt
    pw_hash = bcrypt.hashpw(uuid.uuid4().hex.encode(), bcrypt.gensalt()).decode()
    user = existing_user or User(
        id=str(uuid.uuid4()),
        email=SHOWCASE_EMAIL,
        hashed_password=pw_hash,
        name=SHOWCASE_NAME,
        tier="pro",
    )
    if not existing_user:
        db.add(user)
        db.flush()

    now = datetime.utcnow()

    designs_data = [
        {
            "design_name": "Microplastic PET Degradation System",
            "host_organism": "Escherichia coli K-12",
            "organism_summary": (
                "Engineered E. coli expressing PETase and MHETase from Ideonella "
                "sakaiensis for enzymatic breakdown of polyethylene terephthalate "
                "(PET) microplastics into terephthalic acid and ethylene glycol. "
                "GFP reporter enables real-time monitoring of expression levels in "
                "environmental samples. Designed for ocean and freshwater "
                "microplastic contamination remediation, with codon-optimized "
                "sequences for high-level expression in E. coli and a ccdA/ccdB "
                "kill switch for biocontainment."
            ),
            "gene_circuit": {
                "genes": [
                    {"name": "petase", "function": "PET hydrolase — cleaves ester bonds in polyethylene terephthalate", "source_organism": "Ideonella sakaiensis", "size_bp": 879},
                    {"name": "mhetase", "function": "MHET hydrolase — converts MHET to terephthalic acid and ethylene glycol", "source_organism": "Ideonella sakaiensis", "size_bp": 1800},
                    {"name": "gfp", "function": "Green fluorescent protein reporter for expression monitoring", "source_organism": "Aequorea victoria", "size_bp": 720},
                ],
                "promoters": ["T7", "lac"],
                "terminators": ["rrnB T1", "T7 terminator"],
            },
            "gene_sequences": {
                "petase": {"source": "ncbi_registry", "accession": "A0A0K8P6T7", "length": 879, "confidence": "high"},
                "mhetase": {"source": "ncbi_registry", "accession": "A0A0K8P8E7", "length": 1800, "confidence": "high"},
                "gfp": {"source": "ncbi_registry", "accession": "P42212", "length": 720, "confidence": "high"},
            },
            "safety_score": 0.92, "bump_count": 47, "days_ago": 28,
            "dna_length": 7400, "environment": "ocean",
            "target_product": "Terephthalic acid",
            "simulated_yield": "0.34 g/L (theoretical)",
            "estimated_cost": "$2,400 — $3,200",
            "generation_time_sec": 14.7,
        },
        {
            "design_name": "Enhanced Photosynthetic Carbon Capture",
            "host_organism": "Synechococcus elongatus PCC 7942",
            "organism_summary": (
                "Overexpression of RuBisCO large and small subunits alongside "
                "carboxysome shell proteins and carbonic anhydrase to enhance CO2 "
                "fixation rates in the cyanobacterium S. elongatus. Carbonic "
                "anhydrase accelerates CO2/HCO3- interconversion within the "
                "carboxysome microcompartment, increasing local CO2 concentration "
                "at the RuBisCO active site. Targets industrial flue gas capture, "
                "carbon credit generation, and algal biofuel precursor production."
            ),
            "gene_circuit": {
                "genes": [
                    {"name": "rbcL", "function": "RuBisCO large subunit — carbon fixation catalyst", "source_organism": "Synechococcus elongatus", "size_bp": 1428},
                    {"name": "rbcS", "function": "RuBisCO small subunit — modulates CO2/O2 specificity factor", "source_organism": "Synechococcus elongatus", "size_bp": 369},
                    {"name": "ccmK", "function": "Carboxysome shell protein — CO2 concentrating mechanism", "source_organism": "Synechococcus elongatus", "size_bp": 312},
                    {"name": "ccmM", "function": "Carboxysome scaffold — organizes RuBisCO inside microcompartment", "source_organism": "Synechococcus elongatus", "size_bp": 672},
                    {"name": "cah", "function": "Carbonic anhydrase — CO2/HCO3- interconversion", "source_organism": "Neisseria gonorrhoeae", "size_bp": 700},
                ],
                "promoters": ["Ptrc", "PcpcB"],
                "terminators": ["rrnB T1"],
            },
            "gene_sequences": {
                "rbcL": {"source": "ncbi_registry", "accession": "P00880", "length": 1428, "confidence": "high"},
                "rbcS": {"source": "ncbi_registry", "accession": "P04716", "length": 369, "confidence": "high"},
                "ccmK": {"source": "ncbi_registry", "accession": "Q31QA8", "length": 312, "confidence": "high"},
                "ccmM": {"source": "ncbi_registry", "accession": "Q31RA5", "length": 672, "confidence": "high"},
                "cah": {"source": "ncbi_registry", "accession": "Q9K785", "length": 700, "confidence": "high"},
            },
            "safety_score": 0.95, "bump_count": 34, "days_ago": 22,
            "dna_length": 8200, "environment": "industrial",
            "target_product": "Fixed carbon (3-phosphoglycerate)",
            "simulated_yield": "2.1x wild-type CO2 fixation rate (theoretical)",
            "estimated_cost": "$3,100 — $4,500",
            "generation_time_sec": 18.3,
        },
        {
            "design_name": "Biological Nitrogen Fixation Cassette",
            "host_organism": "Escherichia coli K-12",
            "organism_summary": (
                "Transfer of the core nitrogenase complex (nifHDK) from Klebsiella "
                "oxytoca into E. coli to enable atmospheric nitrogen fixation in a "
                "non-diazotrophic host. NifH provides the electron transfer "
                "component (Fe protein), while NifD and NifK form the catalytic "
                "MoFe protein heterotetramer. Designed as a soil inoculant for "
                "sustainable agriculture, reducing dependency on energy-intensive "
                "Haber-Bosch synthetic fertilizer. Includes anaerobic-responsive "
                "promoter elements for oxygen-sensitive nitrogenase protection."
            ),
            "gene_circuit": {
                "genes": [
                    {"name": "nifH", "function": "Nitrogenase Fe protein — electron donor to MoFe protein", "source_organism": "Klebsiella oxytoca", "size_bp": 882},
                    {"name": "nifD", "function": "Nitrogenase MoFe protein alpha subunit — N2 binding and reduction", "source_organism": "Klebsiella oxytoca", "size_bp": 1440},
                    {"name": "nifK", "function": "Nitrogenase MoFe protein beta subunit — structural scaffold", "source_organism": "Klebsiella oxytoca", "size_bp": 1560},
                ],
                "promoters": ["nifH native", "lac"],
                "terminators": ["rrnB T1", "T7 terminator"],
            },
            "gene_sequences": {
                "nifH": {"source": "ncbi_registry", "accession": "P00459", "length": 882, "confidence": "high"},
                "nifD": {"source": "ncbi_registry", "accession": "P00464", "length": 1440, "confidence": "high"},
                "nifK": {"source": "ncbi_registry", "accession": "P00465", "length": 1560, "confidence": "high"},
            },
            "safety_score": 0.88, "bump_count": 41, "days_ago": 17,
            "dna_length": 8600, "environment": "soil",
            "target_product": "Ammonia (NH3)",
            "simulated_yield": "12.4 nmol NH3/min/mg protein (theoretical)",
            "estimated_cost": "$2,800 — $3,600",
            "generation_time_sec": 16.1,
        },
        {
            "design_name": "PHA Bioplastic Production from Waste Carbon",
            "host_organism": "Pseudomonas putida KT2440",
            "organism_summary": (
                "Heterologous expression of the polyhydroxyalkanoate (PHA) "
                "biosynthesis operon from Cupriavidus necator in P. putida KT2440 "
                "for production of biodegradable polyhydroxybutyrate (PHB) from "
                "waste carbon feedstocks. PhaA catalyzes acetyl-CoA condensation, "
                "PhaB performs NADPH-dependent reduction, and PhaC polymerizes "
                "3-hydroxybutyryl-CoA into PHB granules. P. putida's native "
                "solvent tolerance enables direct conversion of industrial waste "
                "streams — including lignin hydrolysates and plastic pyrolysis "
                "oil — into compostable bioplastic pellets."
            ),
            "gene_circuit": {
                "genes": [
                    {"name": "phaA", "function": "Acetyl-CoA acetyltransferase — condenses two acetyl-CoA to acetoacetyl-CoA", "source_organism": "Cupriavidus necator", "size_bp": 1179},
                    {"name": "phaB", "function": "Acetoacetyl-CoA reductase — NADPH-dependent reduction to 3-HB-CoA", "source_organism": "Cupriavidus necator", "size_bp": 741},
                    {"name": "phaC", "function": "PHA synthase — polymerizes monomers into PHB granules", "source_organism": "Cupriavidus necator", "size_bp": 1770},
                ],
                "promoters": ["Ptac", "alkB native"],
                "terminators": ["rrnB T1"],
            },
            "gene_sequences": {
                "phaA": {"source": "ncbi_registry", "accession": "P14611", "length": 1179, "confidence": "high"},
                "phaB": {"source": "ncbi_registry", "accession": "P14697", "length": 741, "confidence": "high"},
                "phaC": {"source": "ncbi_registry", "accession": "P23608", "length": 1770, "confidence": "high"},
            },
            "safety_score": 0.94, "bump_count": 28, "days_ago": 12,
            "dna_length": 8400, "environment": "industrial",
            "target_product": "Polyhydroxybutyrate (PHB)",
            "simulated_yield": "0.42 g PHB/g glucose (theoretical)",
            "estimated_cost": "$1,900 — $2,700",
            "generation_time_sec": 12.9,
        },
        {
            "design_name": "Petroleum Hydrocarbon Remediation System",
            "host_organism": "Pseudomonas putida KT2440",
            "organism_summary": (
                "Engineered P. putida combining alkane hydroxylase (AlkB) for "
                "medium-chain hydrocarbon oxidation with organophosphate-degrading "
                "enzyme (OpdA) for treatment of co-contaminated industrial sites. "
                "AlkB catalyzes the terminal hydroxylation of C5-C12 alkanes — "
                "the rate-limiting step in aerobic hydrocarbon degradation. OpdA "
                "provides broad-spectrum organophosphate hydrolysis for sites with "
                "mixed petroleum and pesticide contamination. GFP reporter linked "
                "to the alkB promoter functions as a real-time hydrocarbon "
                "biosensor, enabling field monitoring of remediation progress."
            ),
            "gene_circuit": {
                "genes": [
                    {"name": "alkB", "function": "Alkane hydroxylase — terminal oxidation of C5-C12 alkanes", "source_organism": "Pseudomonas putida", "size_bp": 1170},
                    {"name": "opdA", "function": "Organophosphate-degrading enzyme — hydrolyzes P-O and P-S bonds", "source_organism": "Agrobacterium radiobacter", "size_bp": 1100},
                    {"name": "gfp", "function": "Fluorescent biosensor reporter linked to alkB promoter", "source_organism": "Aequorea victoria", "size_bp": 720},
                ],
                "promoters": ["alkB native", "Ptac"],
                "terminators": ["rrnB T1", "T7 terminator"],
            },
            "gene_sequences": {
                "alkB": {"source": "ncbi_registry", "accession": "P12691", "length": 1170, "confidence": "high"},
                "opdA": {"source": "ncbi_registry", "accession": "Q44256", "length": 1100, "confidence": "high"},
                "gfp": {"source": "ncbi_registry", "accession": "P42212", "length": 720, "confidence": "high"},
            },
            "safety_score": 0.90, "bump_count": 19, "days_ago": 7,
            "dna_length": 7700, "environment": "soil",
            "target_product": "Degraded hydrocarbons (alcohols, aldehydes)",
            "simulated_yield": "68% C12 alkane degradation in 72h (theoretical)",
            "estimated_cost": "$2,200 — $3,000",
            "generation_time_sec": 15.4,
        },
        {
            "design_name": "Organophosphate Pesticide Detoxification System",
            "host_organism": "Escherichia coli K-12",
            "organism_summary": (
                "Dual-enzyme system for agricultural pesticide remediation "
                "combining OpdA organophosphate hydrolase with fungal cutinase. "
                "OpdA hydrolyzes the phosphoester bonds in organophosphate "
                "pesticides including parathion, chlorpyrifos, and methyl "
                "parathion — converting them to non-toxic metabolites. Cutinase "
                "from Fusarium solani degrades the protective waxy cutin layer on "
                "plant surfaces and soil particles where pesticides preferentially "
                "accumulate, increasing OpdA substrate access. GFP reporter "
                "enables monitoring of enzyme expression under field conditions. "
                "Targets drinking water decontamination, agricultural runoff "
                "treatment, and soil remediation near high-use cropland."
            ),
            "gene_circuit": {
                "genes": [
                    {"name": "opdA", "function": "Organophosphate hydrolase — cleaves P-O/P-S/P-F bonds in pesticides", "source_organism": "Agrobacterium radiobacter", "size_bp": 1100},
                    {"name": "cutinase", "function": "Cutin hydrolase — degrades waxy cuticle to expose trapped pesticides", "source_organism": "Fusarium solani", "size_bp": 660},
                    {"name": "gfp", "function": "Green fluorescent protein for field expression monitoring", "source_organism": "Aequorea victoria", "size_bp": 720},
                ],
                "promoters": ["T7", "lac"],
                "terminators": ["rrnB T1", "T7 terminator"],
            },
            "gene_sequences": {
                "opdA": {"source": "ncbi_registry", "accession": "Q44256", "length": 1100, "confidence": "high"},
                "cutinase": {"source": "ncbi_registry", "accession": "P00590", "length": 660, "confidence": "high"},
                "gfp": {"source": "ncbi_registry", "accession": "P42212", "length": 720, "confidence": "high"},
            },
            "safety_score": 0.91, "bump_count": 23, "days_ago": 3,
            "dna_length": 7200, "environment": "soil",
            "target_product": "Degraded organophosphates (diethyl phosphate, p-nitrophenol)",
            "simulated_yield": "94% parathion hydrolysis in 4h (theoretical)",
            "estimated_cost": "$2,100 — $2,800",
            "generation_time_sec": 11.2,
        },
    ]

    inserted = []

    for i, d in enumerate(designs_data):
        dna = _generate_dna(d["dna_length"], seed=i + 42)
        created = now - timedelta(days=d["days_ago"])

        design = Design(
            id=str(uuid.uuid4()),
            user_id=user.id,
            prompt=f"Design a {d['design_name'].lower()} using {d['host_organism']}",
            organism_type="bacteria",
            environment=d["environment"],
            safety_level=0.7,
            complexity=0.5,
            design_name=d["design_name"],
            host_organism=d["host_organism"],
            organism_summary=d["organism_summary"],
            gene_circuit=json.dumps(d["gene_circuit"]),
            gene_sequences=json.dumps(d["gene_sequences"]),
            codon_optimized=json.dumps({}),
            dna_sequence=dna,
            fasta_content=f">{d['design_name'].replace(' ', '_')}\n{dna}",
            plasmid_map_data=json.dumps({}),
            fba_results=json.dumps({}),
            assembly_plan=json.dumps({}),
            safety_score=d["safety_score"],
            safety_flags=json.dumps([]),
            dual_use_assessment="No dual-use concerns identified.",
            simulated_yield=d["simulated_yield"],
            estimated_cost=d["estimated_cost"],
            target_product=d["target_product"],
            generation_time_sec=d["generation_time_sec"],
            model_used="claude-sonnet",
            status="complete",
            is_public=True,
            bump_count=d["bump_count"],
            created_at=created,
            updated_at=created,
        )
        db.add(design)
        inserted.append({"id": design.id, "name": d["design_name"], "bumps": d["bump_count"]})

    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="admin_seed_explore",
        details=json.dumps({"designs_inserted": len(inserted)}),
    )
    db.add(audit)
    db.commit()

    return {
        "status": "seeded",
        "showcase_user_id": user.id,
        "designs": inserted,
        "rollback_sql": f"DELETE FROM designs WHERE user_id = '{user.id}'; DELETE FROM users WHERE id = '{user.id}';",
    }
