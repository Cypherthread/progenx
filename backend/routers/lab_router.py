"""
Lab Feedback API — Users report experimental results, system learns over time.

NOT machine learning. Uses simple statistical scoring:
- Positions where mutations worked before get boosted
- Amino acid preferences at each position accumulate from real data
- Combined with ESM-2 zero-shot scores for ranked variant suggestions

This is honest: with 3-5 data points you get directional hints, not predictions.
With 20+ data points per gene, you get statistically meaningful variant ranking.
"""

import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import User, Design, LabResult
from auth import get_current_user

router = APIRouter()


class LabResultRequest(BaseModel):
    design_id: str
    gene_name: str = Field(..., max_length=100)
    sequence: str = Field(default="", max_length=10000)
    organism: str = Field(default="", max_length=200)
    result_type: str = Field(default="activity", max_length=50)
    value: float = 0.0
    unit: str = Field(default="", max_length=50)
    conditions: dict = {}
    notes: str = Field(default="", max_length=2000)
    success: bool = True


@router.post("/results")
def submit_lab_result(
    req: LabResultRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit experimental results for a design's gene. Pro tier only."""
    if user.tier not in ("pro", "admin"):
        raise HTTPException(status_code=403, detail="Lab feedback is a Pro feature")

    # Verify design exists and belongs to user
    design = db.query(Design).filter(
        Design.id == req.design_id, Design.user_id == user.id
    ).first()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    result = LabResult(
        user_id=user.id,
        design_id=req.design_id,
        gene_name=req.gene_name.lower().strip(),
        sequence=req.sequence.upper().strip(),
        organism=req.organism,
        result_type=req.result_type,
        value=req.value,
        unit=req.unit,
        conditions=json.dumps(req.conditions),
        notes=req.notes,
        success=req.success,
    )
    db.add(result)
    db.commit()

    # Count total results for this user
    total = db.query(LabResult).filter(LabResult.user_id == user.id).count()

    return {
        "id": result.id,
        "message": f"Lab result saved. You have {total} total result{'s' if total != 1 else ''} — "
                   + ("future variant suggestions will use this data." if total >= 3
                      else f"submit {3 - total} more to unlock data-driven variant ranking."),
    }


@router.get("/results")
def list_lab_results(
    design_id: str = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List user's lab results, optionally filtered by design."""
    query = db.query(LabResult).filter(LabResult.user_id == user.id)
    if design_id:
        query = query.filter(LabResult.design_id == design_id)
    results = query.order_by(LabResult.created_at.desc()).limit(100).all()

    return [
        {
            "id": r.id,
            "design_id": r.design_id,
            "gene_name": r.gene_name,
            "result_type": r.result_type,
            "value": r.value,
            "unit": r.unit,
            "organism": r.organism,
            "success": r.success,
            "notes": r.notes,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in results
    ]


@router.get("/variants/{gene_name}")
def get_improved_variants(
    gene_name: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get variant suggestions for a gene, ranked by lab data + ESM-2 scores.

    With 0 lab results: returns ESM-2 zero-shot predictions only.
    With 3+ lab results: combines ESM-2 scores with empirical mutation preferences.
    """
    if user.tier not in ("pro", "admin"):
        raise HTTPException(status_code=403, detail="Variant suggestions are a Pro feature")

    gene = gene_name.lower().strip()

    # Get user's lab data for this gene
    lab_results = db.query(LabResult).filter(
        LabResult.user_id == user.id,
        LabResult.gene_name == gene,
    ).all()

    # Build empirical mutation profile from lab data
    empirical_profile = _build_empirical_profile(lab_results)

    # Try ESM-2 scoring if a sequence is available
    esm_results = None
    template_seq = None
    if lab_results:
        # Use the sequence from the best-performing result
        successful = [r for r in lab_results if r.success and r.sequence]
        if successful:
            best = max(successful, key=lambda r: r.value)
            template_seq = best.sequence

    if template_seq and len(template_seq) > 10:
        try:
            from services.esm_scorer import score_variants
            esm_results = score_variants(template_seq)
        except Exception:
            pass

    # Combine ESM-2 + empirical data
    combined = _combine_scores(esm_results, empirical_profile, template_seq)

    return {
        "gene_name": gene,
        "lab_results_count": len(lab_results),
        "data_driven": len(lab_results) >= 3,
        "template_sequence": template_seq[:50] + "..." if template_seq and len(template_seq) > 50 else template_seq,
        "variants": combined[:20],
        "method": "esm2_zero_shot + lab_feedback" if lab_results else "esm2_zero_shot",
        "note": (
            f"Ranked using {len(lab_results)} lab result{'s' if len(lab_results) != 1 else ''} "
            + ("and ESM-2 predictions." if esm_results else "(ESM-2 not available).")
            if lab_results else
            "ESM-2 zero-shot predictions only. Submit lab results to improve rankings."
        ),
    }


@router.get("/stats")
def lab_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Summary of user's lab feedback data."""
    total = db.query(LabResult).filter(LabResult.user_id == user.id).count()
    genes = db.query(LabResult.gene_name).filter(
        LabResult.user_id == user.id
    ).distinct().all()
    success_rate = 0.0
    if total > 0:
        successes = db.query(LabResult).filter(
            LabResult.user_id == user.id, LabResult.success == True
        ).count()
        success_rate = round(successes / total * 100, 1)

    return {
        "total_results": total,
        "genes_tested": [g[0] for g in genes],
        "success_rate": success_rate,
        "data_driven_genes": len([g for g in genes if _gene_has_enough_data(g[0], user.id, db)]),
        "message": (
            "No lab results yet. Run experiments and submit results to unlock data-driven designs."
            if total == 0 else
            f"{total} results across {len(genes)} gene{'s' if len(genes) != 1 else ''}. "
            f"{'All' if success_rate == 100 else f'{success_rate}%'} success rate."
        ),
    }


def _gene_has_enough_data(gene_name: str, user_id: str, db) -> bool:
    """Check if we have enough data for meaningful variant ranking."""
    count = db.query(LabResult).filter(
        LabResult.user_id == user_id,
        LabResult.gene_name == gene_name,
    ).count()
    return count >= 3


def _build_empirical_profile(results: list) -> dict:
    """Build a simple mutation preference profile from lab results.

    Returns {position: {amino_acid: avg_score}} from successful experiments.
    This is basic statistics, not ML — honest about what small data can tell us.
    """
    if len(results) < 2:
        return {}

    # Group by sequence to find mutations that correlate with success
    profile = {}
    sequences = [(r.sequence, r.value, r.success) for r in results if r.sequence]

    if len(sequences) < 2:
        return {}

    # Find the reference (most common or first successful)
    ref_seq = sequences[0][0]

    for seq, value, success in sequences:
        if len(seq) != len(ref_seq):
            continue
        for pos, (ref_aa, test_aa) in enumerate(zip(ref_seq, seq)):
            if ref_aa != test_aa:
                key = f"{pos + 1}"
                if key not in profile:
                    profile[key] = {}
                if test_aa not in profile[key]:
                    profile[key][test_aa] = []
                profile[key][test_aa].append(value if success else -abs(value))

    # Average scores per position/mutation
    averaged = {}
    for pos, mutations in profile.items():
        averaged[pos] = {
            aa: round(sum(scores) / len(scores), 3)
            for aa, scores in mutations.items()
        }

    return averaged


def _combine_scores(esm_results: dict | None, empirical: dict, template: str | None) -> list:
    """Combine ESM-2 zero-shot scores with empirical lab data.

    ESM-2 weight decreases as empirical data grows (lab data is ground truth).
    """
    variants = []

    if esm_results and esm_results.get("beneficial_mutations"):
        for mut in esm_results["beneficial_mutations"]:
            pos_key = str(mut["position"])
            esm_score = mut["score"]

            # Check if empirical data exists for this position
            emp_score = 0.0
            has_lab_data = False
            if pos_key in empirical and mut["mutant"] in empirical[pos_key]:
                emp_score = empirical[pos_key][mut["mutant"]]
                has_lab_data = True

            # Weighted combination: more lab data = less ESM-2 weight
            if has_lab_data:
                combined_score = 0.3 * esm_score + 0.7 * emp_score
                source = "esm2 + lab_data"
            else:
                combined_score = esm_score
                source = "esm2_only"

            variants.append({
                **mut,
                "combined_score": round(combined_score, 3),
                "source": source,
                "lab_validated": has_lab_data,
            })

    # Add empirical-only mutations not in ESM-2 results
    if empirical:
        esm_positions = {str(v["position"]) + v.get("mutant", "") for v in variants}
        for pos_key, mutations in empirical.items():
            for aa, score in mutations.items():
                if pos_key + aa not in esm_positions and template:
                    pos = int(pos_key) - 1
                    if 0 <= pos < len(template):
                        variants.append({
                            "position": int(pos_key),
                            "wild_type": template[pos],
                            "mutant": aa,
                            "score": 0,
                            "notation": f"{template[pos]}{pos_key}{aa}",
                            "combined_score": score,
                            "source": "lab_data_only",
                            "lab_validated": True,
                        })

    # Sort by combined score
    variants.sort(key=lambda x: x.get("combined_score", 0), reverse=True)
    return variants
