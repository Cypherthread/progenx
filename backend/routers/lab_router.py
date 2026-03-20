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
import math
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from database import get_db
from models import User, Design, LabResult, AuditLog
from auth import get_current_user

router = APIRouter()

VALID_RESULT_TYPES = {"activity", "expression", "stability", "growth", "binding", "solubility", "yield"}
VALID_ASSAY_METHODS = {"plate_reader", "hplc", "gel", "fluorescence", "mass_spec", "growth_curve", "western_blot", "other", ""}


class LabResultRequest(BaseModel):
    design_id: str
    gene_name: str = Field(..., max_length=100)
    sequence: str = Field(default="", max_length=10000)
    sequence_type: str = Field(default="protein", max_length=10)
    mutations: str = Field(default="", max_length=500)
    organism: str = Field(default="", max_length=200)
    result_type: str = Field(default="activity", max_length=50)
    assay_method: str = Field(default="", max_length=50)
    value: float = Field(default=0.0, ge=-1e6, le=1e6)
    unit: str = Field(default="", max_length=50)
    is_control: bool = False
    experiment_id: str = Field(default="", max_length=100)
    replicate_number: int = Field(default=1, ge=1, le=20)
    conditions: dict = {}
    notes: str = Field(default="", max_length=2000)
    success: bool = True

    @field_validator("result_type")
    @classmethod
    def validate_result_type(cls, v):
        v = v.lower().strip()
        if v not in VALID_RESULT_TYPES:
            raise ValueError(f"result_type must be one of: {', '.join(sorted(VALID_RESULT_TYPES))}")
        return v

    @field_validator("sequence_type")
    @classmethod
    def validate_sequence_type(cls, v):
        if v not in ("protein", "dna"):
            raise ValueError("sequence_type must be 'protein' or 'dna'")
        return v

    @field_validator("mutations")
    @classmethod
    def validate_mutations(cls, v):
        if not v or v.lower() == "wild_type":
            return v
        pattern = r'^[A-Z]\d+[A-Z](/[A-Z]\d+[A-Z])*$'
        if not re.match(pattern, v.upper()):
            raise ValueError("Mutations must be in notation like 'A237G' or 'S238F/W159H' or 'wild_type'")
        return v.upper()


@router.post("/results")
def submit_lab_result(
    req: LabResultRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Submit experimental results for a design's gene. Pro tier only."""
    if user.tier not in ("pro", "admin"):
        raise HTTPException(status_code=403, detail="Lab feedback is a Pro feature")

    # Rate limit: max 50 submissions per hour
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent = db.query(LabResult).filter(
        LabResult.user_id == user.id,
        LabResult.created_at >= one_hour_ago,
    ).count()
    if recent >= 50:
        raise HTTPException(status_code=429, detail="Rate limit: max 50 lab results per hour")

    # Verify design exists and belongs to user
    design = db.query(Design).filter(
        Design.id == req.design_id, Design.user_id == user.id
    ).first()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    gene = req.gene_name.lower().strip()

    # Validate gene exists in the design
    if design.gene_circuit:
        try:
            circuit = json.loads(design.gene_circuit) if isinstance(design.gene_circuit, str) else design.gene_circuit
            design_genes = {g.get("name", "").lower().strip() for g in circuit.get("genes", [])}
            if design_genes and gene not in design_genes:
                raise HTTPException(
                    status_code=400,
                    detail=f"Gene '{gene}' not in this design. Available: {', '.join(sorted(design_genes))}"
                )
        except (json.JSONDecodeError, AttributeError):
            pass

    result = LabResult(
        user_id=user.id,
        design_id=req.design_id,
        gene_name=gene,
        sequence=req.sequence.upper().strip(),
        sequence_type=req.sequence_type,
        mutations=req.mutations,
        organism=req.organism,
        result_type=req.result_type,
        assay_method=req.assay_method,
        value=req.value,
        unit=req.unit,
        is_control=req.is_control,
        experiment_id=req.experiment_id,
        replicate_number=req.replicate_number,
        conditions=json.dumps(req.conditions),
        notes=req.notes,
        success=req.success,
    )
    db.add(result)

    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="lab_result_submit",
        details=json.dumps({"design_id": req.design_id, "gene": gene, "type": req.result_type}),
    )
    db.add(audit)
    db.commit()

    total = db.query(LabResult).filter(LabResult.user_id == user.id).count()

    return {
        "id": result.id,
        "message": f"Lab result saved. {total} total result{'s' if total != 1 else ''} — "
                   + ("future variant suggestions will use this data." if total >= 3
                      else f"submit {3 - total} more to unlock data-driven variant ranking."),
    }


@router.delete("/results/{result_id}")
def delete_lab_result(
    result_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a lab result. Only the owner can delete."""
    result = db.query(LabResult).filter(
        LabResult.id == result_id, LabResult.user_id == user.id
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Lab result not found")
    db.delete(result)
    db.commit()
    return {"message": "Lab result deleted"}


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
            "mutations": r.mutations or "",
            "result_type": r.result_type,
            "value": r.value,
            "unit": r.unit,
            "organism": r.organism,
            "is_control": r.is_control,
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
    """Get variant suggestions ranked by lab data + ESM-2 scores."""
    if user.tier not in ("pro", "admin"):
        raise HTTPException(status_code=403, detail="Variant suggestions are a Pro feature")

    gene = gene_name.lower().strip()
    lab_results = db.query(LabResult).filter(
        LabResult.user_id == user.id,
        LabResult.gene_name == gene,
    ).all()

    empirical_profile = _build_empirical_profile(lab_results)

    # Try ESM-2 scoring if a sequence is available
    esm_results = None
    template_seq = None
    if lab_results:
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

    combined = _combine_scores(esm_results, empirical_profile, template_seq)

    n = len(lab_results)
    return {
        "gene_name": gene,
        "lab_results_count": n,
        "data_driven": n >= 3,
        "template_sequence": template_seq[:50] + "..." if template_seq and len(template_seq) > 50 else template_seq,
        "variants": combined[:20],
        "method": "esm2_zero_shot + lab_feedback" if lab_results else "esm2_zero_shot",
        "note": (
            f"Ranked using {n} lab result{'s' if n != 1 else ''}. "
            + (f"Confidence: {'high' if n >= 10 else 'medium' if n >= 5 else 'low — treat as directional hints'}. "
               if n >= 3 else "Need more data for reliable ranking. ")
            + ("ESM-2 predictions included." if esm_results else "ESM-2 not available.")
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
        "message": (
            "No lab results yet. Run experiments and submit results to unlock data-driven designs."
            if total == 0 else
            f"{total} results across {len(genes)} gene{'s' if len(genes) != 1 else ''}. "
            f"{success_rate}% success rate."
        ),
    }


def _build_empirical_profile(results: list) -> dict:
    """Build mutation preference profile from lab results.

    Groups by result_type+unit to avoid mixing measurement scales.
    Returns {position: {amino_acid: {"mean": float, "n": int, "confidence": str}}}
    """
    if len(results) < 2:
        return {}

    sequences = [
        (r.sequence, r.value, r.success, r.result_type, r.unit)
        for r in results if r.sequence
    ]
    if len(sequences) < 2:
        return {}

    # Reference: prefer control sequence, then most common
    control_seqs = [r.sequence for r in results if r.sequence and getattr(r, 'is_control', False)]
    if control_seqs:
        ref_seq = Counter(control_seqs).most_common(1)[0][0]
    else:
        seq_counts = Counter(s[0] for s in sequences)
        ref_seq = seq_counts.most_common(1)[0][0]

    # Group by result_type + unit to avoid mixing scales
    grouped = defaultdict(list)
    for seq, value, success, rtype, unit in sequences:
        grouped[(rtype, unit)].append((seq, value, success))

    profile = {}
    for (rtype, unit), entries in grouped.items():
        if len(entries) < 2:
            continue
        for seq, value, success in entries:
            if len(seq) != len(ref_seq):
                continue
            if not success:
                continue
            for pos, (ref_aa, test_aa) in enumerate(zip(ref_seq, seq)):
                if ref_aa != test_aa:
                    key = f"{pos + 1}"
                    if key not in profile:
                        profile[key] = {}
                    if test_aa not in profile[key]:
                        profile[key][test_aa] = []
                    profile[key][test_aa].append(value)

    # Compute mean + count + confidence
    averaged = {}
    for pos, mutations in profile.items():
        averaged[pos] = {}
        for aa, scores in mutations.items():
            n = len(scores)
            mean = sum(scores) / n
            std = math.sqrt(sum((s - mean) ** 2 for s in scores) / n) if n > 1 else float('inf')
            averaged[pos][aa] = {
                "mean": round(mean, 3),
                "n": n,
                "std": round(std, 3),
                "confidence": "low" if n < 3 else ("medium" if n < 10 else "high"),
            }

    return averaged


def _combine_scores(esm_results: dict | None, empirical: dict, template: str | None) -> list:
    """Combine ESM-2 scores with lab data using rank normalization."""
    variants = []

    if esm_results and esm_results.get("beneficial_mutations"):
        # Normalize ESM scores to [0, 1]
        esm_scores = [m["score"] for m in esm_results["beneficial_mutations"]]
        esm_min = min(esm_scores) if esm_scores else 0
        esm_range = (max(esm_scores) - esm_min) if len(esm_scores) > 1 else 1.0

        # Normalize empirical means to [0, 1]
        all_emp_means = []
        for pos_muts in empirical.values():
            for aa, data in pos_muts.items():
                all_emp_means.append(data["mean"] if isinstance(data, dict) else data)
        emp_min = min(all_emp_means) if all_emp_means else 0
        emp_range = (max(all_emp_means) - emp_min) if len(all_emp_means) > 1 else 1.0

        for mut in esm_results["beneficial_mutations"]:
            pos_key = str(mut["position"])
            esm_norm = (mut["score"] - esm_min) / esm_range if esm_range else 0.5

            has_lab_data = False
            emp_norm = 0.0
            lab_meta = None
            if pos_key in empirical and mut["mutant"] in empirical[pos_key]:
                emp_data = empirical[pos_key][mut["mutant"]]
                emp_val = emp_data["mean"] if isinstance(emp_data, dict) else emp_data
                emp_norm = (emp_val - emp_min) / emp_range if emp_range else 0.5
                lab_meta = emp_data if isinstance(emp_data, dict) else None
                has_lab_data = True

            combined = 0.3 * esm_norm + 0.7 * emp_norm if has_lab_data else esm_norm

            entry = {
                **mut,
                "combined_score": round(combined, 3),
                "source": "esm2 + lab_data" if has_lab_data else "esm2_only",
                "lab_validated": has_lab_data,
            }
            if lab_meta:
                entry["lab_confidence"] = lab_meta.get("confidence", "unknown")
                entry["lab_n"] = lab_meta.get("n", 0)
            variants.append(entry)

    # Add empirical-only mutations
    if empirical:
        esm_positions = {str(v["position"]) + v.get("mutant", "") for v in variants}
        for pos_key, mutations in empirical.items():
            for aa, data in mutations.items():
                if pos_key + aa not in esm_positions and template:
                    pos = int(pos_key) - 1
                    if 0 <= pos < len(template):
                        entry = {
                            "position": int(pos_key),
                            "wild_type": template[pos],
                            "mutant": aa,
                            "score": 0,
                            "notation": f"{template[pos]}{pos_key}{aa}",
                            "combined_score": data["mean"] if isinstance(data, dict) else data,
                            "source": "lab_data_only",
                            "lab_validated": True,
                        }
                        if isinstance(data, dict):
                            entry["lab_confidence"] = data.get("confidence", "unknown")
                            entry["lab_n"] = data.get("n", 0)
                        variants.append(entry)

    variants.sort(key=lambda x: x.get("combined_score", 0), reverse=True)
    return variants
