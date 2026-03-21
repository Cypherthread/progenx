"""
Seed script for Explore gallery — inserts 6 showcase designs.

Run from backend/:
    source venv/bin/activate
    python scripts/seed_explore.py

Uses DATABASE_URL from .env. Defaults to local SQLite (progenx.db).
"""

import os
import sys
import json
import uuid
import random

# Add backend dir to path for project imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed — load .env manually
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, init_db
from models import User, Design

SHOWCASE_EMAIL = "showcase@progenx.ai"
SHOWCASE_NAME = "ProGenX Team"


def generate_dna(length: int, seed: int) -> str:
    """Generate a deterministic pseudo-random DNA string."""
    rng = random.Random(seed)
    return "".join(rng.choice("ATCG") for _ in range(length))


def main():
    db_url = os.getenv("DATABASE_URL", "sqlite:///./progenx.db")

    # Print target without leaking credentials
    if "postgresql" in db_url:
        print("Target: PostgreSQL (from DATABASE_URL)")
        # External Render connections require SSL
        if "sslmode" not in db_url:
            db_url += "?sslmode=require"
    else:
        print(f"Target: {db_url}")
        # Only run init_db for local SQLite (adds missing columns).
        # Production PostgreSQL is already migrated by the running app.
        init_db()

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    # --- Showcase user ---
    user = session.query(User).filter(User.email == SHOWCASE_EMAIL).first()
    if not user:
        import bcrypt

        random_pw = uuid.uuid4().hex
        pw_hash = bcrypt.hashpw(random_pw.encode(), bcrypt.gensalt()).decode()
        user = User(
            id=str(uuid.uuid4()),
            email=SHOWCASE_EMAIL,
            hashed_password=pw_hash,
            name=SHOWCASE_NAME,
            tier="pro",
        )
        session.add(user)
        session.commit()
        print(f"Created showcase user: {user.id}")
    else:
        print(f"Using existing showcase user: {user.id}")

    # --- Check for existing showcase designs ---
    existing = session.query(Design).filter(Design.user_id == user.id).count()
    if existing > 0:
        print(f"\nWARNING: {existing} designs already exist for this user.")
        print("Delete them first or you'll get duplicates.")
        confirm = input("Continue anyway? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return

    now = datetime.utcnow()

    designs_data = [
        # --- 1. Microplastic PET Degradation ---
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
                    {
                        "name": "petase",
                        "function": "PET hydrolase — cleaves ester bonds in polyethylene terephthalate",
                        "source_organism": "Ideonella sakaiensis",
                        "size_bp": 879,
                    },
                    {
                        "name": "mhetase",
                        "function": "MHET hydrolase — converts MHET to terephthalic acid and ethylene glycol",
                        "source_organism": "Ideonella sakaiensis",
                        "size_bp": 1800,
                    },
                    {
                        "name": "gfp",
                        "function": "Green fluorescent protein reporter for expression monitoring",
                        "source_organism": "Aequorea victoria",
                        "size_bp": 720,
                    },
                ],
                "promoters": ["T7", "lac"],
                "terminators": ["rrnB T1", "T7 terminator"],
            },
            "gene_sequences": {
                "petase": {"source": "ncbi_registry", "accession": "A0A0K8P6T7", "length": 879, "confidence": "high"},
                "mhetase": {"source": "ncbi_registry", "accession": "A0A0K8P8E7", "length": 1800, "confidence": "high"},
                "gfp": {"source": "ncbi_registry", "accession": "P42212", "length": 720, "confidence": "high"},
            },
            "safety_score": 0.92,
            "bump_count": 47,
            "days_ago": 28,
            "dna_length": 7400,
            "environment": "ocean",
            "target_product": "Terephthalic acid",
            "simulated_yield": "0.34 g/L (theoretical)",
            "estimated_cost": "$2,400 — $3,200",
            "generation_time_sec": 14.7,
        },
        # --- 2. Enhanced Carbon Capture ---
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
                    {
                        "name": "rbcL",
                        "function": "RuBisCO large subunit — carbon fixation catalyst",
                        "source_organism": "Synechococcus elongatus",
                        "size_bp": 1428,
                    },
                    {
                        "name": "rbcS",
                        "function": "RuBisCO small subunit — modulates CO2/O2 specificity factor",
                        "source_organism": "Synechococcus elongatus",
                        "size_bp": 369,
                    },
                    {
                        "name": "ccmK",
                        "function": "Carboxysome shell protein — CO2 concentrating mechanism",
                        "source_organism": "Synechococcus elongatus",
                        "size_bp": 312,
                    },
                    {
                        "name": "ccmM",
                        "function": "Carboxysome scaffold — organizes RuBisCO inside microcompartment",
                        "source_organism": "Synechococcus elongatus",
                        "size_bp": 672,
                    },
                    {
                        "name": "cah",
                        "function": "Carbonic anhydrase — CO2/HCO3- interconversion",
                        "source_organism": "Neisseria gonorrhoeae",
                        "size_bp": 700,
                    },
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
            "safety_score": 0.95,
            "bump_count": 34,
            "days_ago": 22,
            "dna_length": 8200,
            "environment": "industrial",
            "target_product": "Fixed carbon (3-phosphoglycerate)",
            "simulated_yield": "2.1x wild-type CO2 fixation rate (theoretical)",
            "estimated_cost": "$3,100 — $4,500",
            "generation_time_sec": 18.3,
        },
        # --- 3. Nitrogen Fixation ---
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
                    {
                        "name": "nifH",
                        "function": "Nitrogenase Fe protein — electron donor to MoFe protein",
                        "source_organism": "Klebsiella oxytoca",
                        "size_bp": 882,
                    },
                    {
                        "name": "nifD",
                        "function": "Nitrogenase MoFe protein alpha subunit — N2 binding and reduction",
                        "source_organism": "Klebsiella oxytoca",
                        "size_bp": 1440,
                    },
                    {
                        "name": "nifK",
                        "function": "Nitrogenase MoFe protein beta subunit — structural scaffold",
                        "source_organism": "Klebsiella oxytoca",
                        "size_bp": 1560,
                    },
                ],
                "promoters": ["nifH native", "lac"],
                "terminators": ["rrnB T1", "T7 terminator"],
            },
            "gene_sequences": {
                "nifH": {"source": "ncbi_registry", "accession": "P00459", "length": 882, "confidence": "high"},
                "nifD": {"source": "ncbi_registry", "accession": "P00464", "length": 1440, "confidence": "high"},
                "nifK": {"source": "ncbi_registry", "accession": "P00465", "length": 1560, "confidence": "high"},
            },
            "safety_score": 0.88,
            "bump_count": 41,
            "days_ago": 17,
            "dna_length": 8600,
            "environment": "soil",
            "target_product": "Ammonia (NH3)",
            "simulated_yield": "12.4 nmol NH3/min/mg protein (theoretical)",
            "estimated_cost": "$2,800 — $3,600",
            "generation_time_sec": 16.1,
        },
        # --- 4. PHA Bioplastic ---
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
                    {
                        "name": "phaA",
                        "function": "Acetyl-CoA acetyltransferase — condenses two acetyl-CoA to acetoacetyl-CoA",
                        "source_organism": "Cupriavidus necator",
                        "size_bp": 1179,
                    },
                    {
                        "name": "phaB",
                        "function": "Acetoacetyl-CoA reductase — NADPH-dependent reduction to 3-HB-CoA",
                        "source_organism": "Cupriavidus necator",
                        "size_bp": 741,
                    },
                    {
                        "name": "phaC",
                        "function": "PHA synthase — polymerizes monomers into PHB granules",
                        "source_organism": "Cupriavidus necator",
                        "size_bp": 1770,
                    },
                ],
                "promoters": ["Ptac", "alkB native"],
                "terminators": ["rrnB T1"],
            },
            "gene_sequences": {
                "phaA": {"source": "ncbi_registry", "accession": "P14611", "length": 1179, "confidence": "high"},
                "phaB": {"source": "ncbi_registry", "accession": "P14697", "length": 741, "confidence": "high"},
                "phaC": {"source": "ncbi_registry", "accession": "P23608", "length": 1770, "confidence": "high"},
            },
            "safety_score": 0.94,
            "bump_count": 28,
            "days_ago": 12,
            "dna_length": 8400,
            "environment": "industrial",
            "target_product": "Polyhydroxybutyrate (PHB)",
            "simulated_yield": "0.42 g PHB/g glucose (theoretical)",
            "estimated_cost": "$1,900 — $2,700",
            "generation_time_sec": 12.9,
        },
        # --- 5. Petroleum Remediation ---
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
                    {
                        "name": "alkB",
                        "function": "Alkane hydroxylase — terminal oxidation of C5-C12 alkanes",
                        "source_organism": "Pseudomonas putida",
                        "size_bp": 1170,
                    },
                    {
                        "name": "opdA",
                        "function": "Organophosphate-degrading enzyme — hydrolyzes P-O and P-S bonds",
                        "source_organism": "Agrobacterium radiobacter",
                        "size_bp": 1100,
                    },
                    {
                        "name": "gfp",
                        "function": "Fluorescent biosensor reporter linked to alkB promoter",
                        "source_organism": "Aequorea victoria",
                        "size_bp": 720,
                    },
                ],
                "promoters": ["alkB native", "Ptac"],
                "terminators": ["rrnB T1", "T7 terminator"],
            },
            "gene_sequences": {
                "alkB": {"source": "ncbi_registry", "accession": "P12691", "length": 1170, "confidence": "high"},
                "opdA": {"source": "ncbi_registry", "accession": "Q44256", "length": 1100, "confidence": "high"},
                "gfp": {"source": "ncbi_registry", "accession": "P42212", "length": 720, "confidence": "high"},
            },
            "safety_score": 0.90,
            "bump_count": 19,
            "days_ago": 7,
            "dna_length": 7700,
            "environment": "soil",
            "target_product": "Degraded hydrocarbons (alcohols, aldehydes)",
            "simulated_yield": "68% C12 alkane degradation in 72h (theoretical)",
            "estimated_cost": "$2,200 — $3,000",
            "generation_time_sec": 15.4,
        },
        # --- 6. Pesticide Detoxification ---
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
                    {
                        "name": "opdA",
                        "function": "Organophosphate hydrolase — cleaves P-O/P-S/P-F bonds in pesticides",
                        "source_organism": "Agrobacterium radiobacter",
                        "size_bp": 1100,
                    },
                    {
                        "name": "cutinase",
                        "function": "Cutin hydrolase — degrades waxy cuticle to expose trapped pesticides",
                        "source_organism": "Fusarium solani",
                        "size_bp": 660,
                    },
                    {
                        "name": "gfp",
                        "function": "Green fluorescent protein for field expression monitoring",
                        "source_organism": "Aequorea victoria",
                        "size_bp": 720,
                    },
                ],
                "promoters": ["T7", "lac"],
                "terminators": ["rrnB T1", "T7 terminator"],
            },
            "gene_sequences": {
                "opdA": {"source": "ncbi_registry", "accession": "Q44256", "length": 1100, "confidence": "high"},
                "cutinase": {"source": "ncbi_registry", "accession": "P00590", "length": 660, "confidence": "high"},
                "gfp": {"source": "ncbi_registry", "accession": "P42212", "length": 720, "confidence": "high"},
            },
            "safety_score": 0.91,
            "bump_count": 23,
            "days_ago": 3,
            "dna_length": 7200,
            "environment": "soil",
            "target_product": "Degraded organophosphates (diethyl phosphate, p-nitrophenol)",
            "simulated_yield": "94% parathion hydrolysis in 4h (theoretical)",
            "estimated_cost": "$2,100 — $2,800",
            "generation_time_sec": 11.2,
        },
    ]

    # --- Insert designs ---
    inserted_ids = []

    for i, d in enumerate(designs_data):
        dna = generate_dna(d["dna_length"], seed=i + 42)
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
        session.add(design)
        inserted_ids.append((design.id, d["design_name"], d["bump_count"]))

    session.commit()

    # --- Report ---
    print("\n=== Showcase designs inserted ===\n")
    print(f"Showcase user: {user.id} ({SHOWCASE_EMAIL})\n")
    print("Design IDs (for rollback):")
    for did, name, bumps in inserted_ids:
        print(f"  {did}  {bumps} bumps  {name}")
    print(f"\nRollback SQL:")
    print(f"  DELETE FROM designs WHERE user_id = '{user.id}';")
    print(f"  DELETE FROM users WHERE id = '{user.id}';")
    print(f"\nTotal: {len(inserted_ids)} designs inserted, all marked public.")


if __name__ == "__main__":
    main()
