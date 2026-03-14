"""
Flux Balance Analysis (FBA) engine using COBRApy.

Loads genome-scale metabolic models and runs FBA to predict
realistic growth rates, product yields, and metabolic flux.
"""

import os
import json
import cobra
from cobra.io import load_json_model, read_sbml_model
from pathlib import Path
from config import settings

_models_cache: dict[str, cobra.Model] = {}

# Genome-scale models available from BiGG
# These are downloaded on first use
AVAILABLE_MODELS = {
    "e_coli": {
        "bigg_id": "iJO1366",
        "organism": "Escherichia coli K-12 MG1655",
        "description": "E. coli genome-scale model (1366 genes, 2251 reactions)",
    },
    "p_putida": {
        "bigg_id": "iJN1463",
        "organism": "Pseudomonas putida KT2440",
        "description": "P. putida genome-scale model (1463 genes, 2044 reactions)",
    },
}

CHASSIS_TO_MODEL = {
    "escherichia coli": "e_coli",
    "e. coli": "e_coli",
    "e. coli k-12": "e_coli",
    "pseudomonas putida": "p_putida",
    "p. putida": "p_putida",
    # Fallback to E. coli for organisms without a model
    "synechococcus elongatus": "e_coli",
    "synechocystis": "e_coli",
    "klebsiella": "e_coli",
}


def _download_model(model_key: str) -> str:
    """Download a BiGG model JSON file if not cached locally."""
    model_dir = Path(settings.FBA_MODELS_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)

    info = AVAILABLE_MODELS.get(model_key)
    if not info:
        raise ValueError(f"No model available for {model_key}")

    bigg_id = info["bigg_id"]
    local_path = model_dir / f"{bigg_id}.json"

    if local_path.exists():
        return str(local_path)

    # Download from BiGG
    import httpx
    url = f"http://bigg.ucsd.edu/static/models/{bigg_id}.json"
    with httpx.Client(timeout=120) as client:
        resp = client.get(url)
        resp.raise_for_status()
        local_path.write_bytes(resp.content)

    return str(local_path)


def _load_model(chassis: str) -> cobra.Model:
    """Load (and cache) the appropriate genome-scale model."""
    model_key = CHASSIS_TO_MODEL.get(chassis.lower().strip(), "e_coli")

    if model_key in _models_cache:
        return _models_cache[model_key].copy()

    model_path = _download_model(model_key)
    model = load_json_model(model_path)
    _models_cache[model_key] = model
    return model.copy()


def run_fba(
    chassis: str,
    pathway_genes: list[str],
    target_product: str = "",
    environment: str = "lab",
) -> dict:
    """
    Run flux balance analysis for the given chassis and pathway.

    Returns predicted growth rate, yields, and flux distribution summary.
    """
    try:
        model = _load_model(chassis)
    except Exception as e:
        return _fallback_fba(chassis, pathway_genes, environment, str(e))

    results = {}

    # 1. Wild-type growth (baseline)
    wt_solution = model.optimize()
    results["wild_type_growth_rate"] = round(wt_solution.objective_value, 4) if wt_solution.status == "optimal" else 0

    # 2. Estimate metabolic burden from heterologous genes
    # Each foreign gene adds ~0.01-0.03 mmol/gDW/h protein synthesis burden
    n_genes = len(pathway_genes)
    protein_burden = n_genes * 0.02  # mmol ATP / gDW / h estimate

    # Reduce ATP maintenance to simulate burden
    atpm_id = None
    for rxn in model.reactions:
        if "ATPM" in rxn.id or "atpm" in rxn.id.lower():
            atpm_id = rxn.id
            break

    if atpm_id:
        atpm_rxn = model.reactions.get_by_id(atpm_id)
        original_lb = atpm_rxn.lower_bound
        atpm_rxn.lower_bound = original_lb + protein_burden

    # 3. Run FBA with burden
    burdened_solution = model.optimize()
    results["burdened_growth_rate"] = round(burdened_solution.objective_value, 4) if burdened_solution.status == "optimal" else 0
    results["growth_reduction_pct"] = round(
        (1 - results["burdened_growth_rate"] / results["wild_type_growth_rate"]) * 100, 1
    ) if results["wild_type_growth_rate"] > 0 else 0

    # 4. Environment adjustments
    env_factors = {
        "lab": 1.0,
        "ocean": 0.3,  # nutrient-limited, cold
        "soil": 0.5,   # variable nutrients
        "gut": 0.7,    # rich but competitive
    }
    env_factor = env_factors.get(environment, 1.0)

    results["environment"] = environment
    results["adjusted_growth_rate"] = round(results["burdened_growth_rate"] * env_factor, 4)

    # 5. Estimate product yield using theoretical maximum
    # Use the fraction of carbon flux not going to biomass
    biomass_carbon_fraction = 0.5  # typical
    carbon_available = 1.0 - (results["adjusted_growth_rate"] / max(results["wild_type_growth_rate"], 0.01))
    theoretical_yield = max(0, carbon_available * 0.4)  # 40% theoretical conversion

    results["theoretical_product_yield_g_per_g_substrate"] = round(theoretical_yield, 3)
    results["estimated_titer_g_per_L"] = round(theoretical_yield * 10, 2)  # assuming 10 g/L substrate

    # 6. Key flux summary
    results["model_used"] = AVAILABLE_MODELS.get(
        CHASSIS_TO_MODEL.get(chassis.lower().strip(), "e_coli"), {}
    ).get("bigg_id", "unknown")
    results["model_genes"] = len(model.genes)
    results["model_reactions"] = len(model.reactions)
    results["heterologous_genes"] = n_genes
    results["metabolic_burden_estimate"] = f"{protein_burden:.3f} mmol ATP/gDW/h"

    # 7. Summary string
    results["summary"] = (
        f"FBA prediction using {results['model_used']} ({results['model_genes']} genes, "
        f"{results['model_reactions']} reactions):\n"
        f"  Wild-type growth rate: {results['wild_type_growth_rate']} h⁻¹\n"
        f"  With {n_genes}-gene pathway burden: {results['burdened_growth_rate']} h⁻¹ "
        f"({results['growth_reduction_pct']}% reduction)\n"
        f"  In {environment} environment: {results['adjusted_growth_rate']} h⁻¹\n"
        f"  Theoretical product yield: {results['theoretical_product_yield_g_per_g_substrate']} g/g substrate\n"
        f"  Estimated titer: {results['estimated_titer_g_per_L']} g/L\n"
        f"  Note: Real yields require wet-lab validation. FBA provides upper bounds."
    )

    results["source"] = "cobra_fba"

    return results


def _fallback_fba(chassis: str, pathway_genes: list[str], environment: str, error: str) -> dict:
    """Heuristic fallback when COBRApy model is unavailable."""
    base_growth = {"lab": 0.8, "ocean": 0.25, "soil": 0.4, "gut": 0.55}
    growth = base_growth.get(environment, 0.8)
    n_genes = len(pathway_genes)
    burden = n_genes * 0.05
    adjusted = max(0.05, growth * (1 - burden))

    return {
        "wild_type_growth_rate": growth,
        "burdened_growth_rate": round(adjusted, 4),
        "growth_reduction_pct": round(burden * 100, 1),
        "adjusted_growth_rate": round(adjusted, 4),
        "environment": environment,
        "theoretical_product_yield_g_per_g_substrate": round(max(0, (1 - adjusted / growth) * 0.3), 3),
        "estimated_titer_g_per_L": round(max(0, (1 - adjusted / growth) * 3), 2),
        "heterologous_genes": n_genes,
        "model_used": "heuristic_fallback",
        "model_genes": 0,
        "model_reactions": 0,
        "metabolic_burden_estimate": f"{burden:.3f} (heuristic)",
        "summary": (
            f"Heuristic estimate (COBRApy model unavailable: {error}):\n"
            f"  Estimated growth: {adjusted} h⁻¹ in {environment}\n"
            f"  {n_genes}-gene burden: ~{burden*100:.0f}% growth reduction\n"
            f"  Note: Install COBRApy models for genome-scale FBA predictions."
        ),
        "source": "heuristic_fallback",
    }
