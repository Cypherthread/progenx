import json
import time
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Any

from database import get_db
from models import User, Design, ChatMessage, AuditLog
from auth import get_current_user, check_rate_limit
from services.llm_orchestrator import generate_design, refine_design
from services.safety_scorer import score_safety
from config import settings

router = APIRouter()


class DesignRequest(BaseModel):
    prompt: str
    environment: str = "ocean"
    safety_level: float = 0.7
    complexity: float = 0.5


class RefineRequest(BaseModel):
    message: str


class DesignResponse(BaseModel):
    id: str
    status: str
    design_name: str
    host_organism: str
    organism_summary: str
    gene_circuit: Any  # JSON object
    gene_sequences: Any  # JSON: NCBI results per gene
    codon_optimized: Any  # JSON: optimized sequences
    dna_sequence: str
    fasta_content: str
    plasmid_map_data: Any  # JSON with png_base64 + features
    fba_results: Any  # JSON: COBRApy output
    assembly_plan: Any  # JSON: ori, marker, kill switch
    safety_score: float
    safety_flags: list[str]
    dual_use_assessment: str
    simulated_yield: str
    estimated_cost: str
    target_product: str
    generation_time_sec: float
    model_used: str
    is_public: bool
    disclaimer: str
    is_conceptual: bool = False
    conceptual_banner: str = ""
    non_registry_genes: list[str] = []
    conceptual_genes: list[str] = []


@router.post("/generate", response_model=DesignResponse)
def create_design(
    req: DesignRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    check_rate_limit(user, db)

    design = Design(
        user_id=user.id,
        prompt=req.prompt,
        environment=req.environment,
        safety_level=req.safety_level,
        complexity=req.complexity,
        status="generating",
    )
    db.add(design)
    db.commit()
    db.refresh(design)

    start = time.time()
    try:
        result = generate_design(
            prompt=req.prompt,
            environment=req.environment,
            safety_level=req.safety_level,
            complexity=req.complexity,
            user_tier=user.tier,
        )

        safety = score_safety(
            result.get("dna_sequence", ""),
            result.get("organism_summary", ""),
            json.dumps(result.get("gene_circuit", {})),
        )

        design.design_name = result.get("design_name", "Untitled")
        design.host_organism = result.get("host_organism", "")
        design.organism_summary = result.get("organism_summary", "")
        design.gene_circuit = json.dumps(result.get("gene_circuit", {}))
        design.gene_sequences = json.dumps(result.get("gene_sequences", {}), default=str)
        design.codon_optimized = json.dumps(result.get("codon_optimized", {}), default=str)
        design.dna_sequence = result.get("dna_sequence", "")
        design.fasta_content = result.get("fasta_content", "")
        design.plasmid_map_data = json.dumps(result.get("plasmid_map", {}), default=str)
        design.fba_results = json.dumps(result.get("fba_results", {}), default=str)
        design.assembly_plan = json.dumps(result.get("assembly_plan", {}), default=str)
        design.safety_score = safety["score"]
        design.safety_flags = json.dumps(safety["flags"])
        design.dual_use_assessment = safety["dual_use_assessment"]
        design.simulated_yield = result.get("simulated_yield", "N/A")
        design.estimated_cost = result.get("estimated_cost", "N/A")
        design.target_product = result.get("target_product", "")
        design.model_used = result.get("model_used", "claude")
        design.status = "complete"
        design.generation_time_sec = round(time.time() - start, 2)

        user.designs_this_month += 1

        audit = AuditLog(
            user_id=user.id,
            action="generate_design",
            details=json.dumps({"prompt": req.prompt, "design_id": design.id}),
            safety_flags=json.dumps(safety["flags"]),
        )
        db.add(audit)

        msg = ChatMessage(
            design_id=design.id,
            role="assistant",
            content=f"Design generated: {design.design_name}\n\n{design.organism_summary[:500]}",
        )
        db.add(msg)
        db.commit()
        db.refresh(design)

    except Exception as e:
        design.status = "error"
        db.commit()
        error_msg = str(e)
        # Provide user-friendly error messages for common failures
        if "No LLM available" in error_msg or "Connection refused" in error_msg:
            detail = (
                "Design engine is temporarily unavailable. "
                "The AI model may be starting up — please try again in 30 seconds."
            )
        elif "Could not parse LLM response" in error_msg:
            detail = (
                "The AI returned an unexpected response. "
                "This sometimes happens — please try again or simplify your prompt."
            )
        elif "rate" in error_msg.lower() or "429" in error_msg:
            detail = "Rate limit reached. Please wait a moment and try again."
        else:
            detail = f"Design generation failed: {error_msg[:200]}"
        raise HTTPException(status_code=500, detail=detail)

    return _design_response(design)


@router.post("/{design_id}/refine", response_model=DesignResponse)
def refine(
    design_id: str,
    req: RefineRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    design = db.query(Design).filter(Design.id == design_id, Design.user_id == user.id).first()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")

    user_msg = ChatMessage(design_id=design.id, role="user", content=req.message)
    db.add(user_msg)

    history = db.query(ChatMessage).filter(ChatMessage.design_id == design.id).order_by(ChatMessage.created_at).all()
    messages = [{"role": m.role, "content": m.content} for m in history]

    start = time.time()
    result = refine_design(
        original_design={
            "design_name": design.design_name,
            "host_organism": design.host_organism,
            "organism_summary": design.organism_summary,
            "gene_circuit": design.gene_circuit,
            "dna_sequence": design.dna_sequence,
            "environment": design.environment,
        },
        refinement_request=req.message,
        conversation_history=messages,
        user_tier=user.tier,
    )

    safety = score_safety(result.get("dna_sequence", ""), result.get("organism_summary", ""), json.dumps(result.get("gene_circuit", {})))

    design.organism_summary = result.get("organism_summary", design.organism_summary)
    design.gene_circuit = json.dumps(result.get("gene_circuit", {}))
    design.gene_sequences = json.dumps(result.get("gene_sequences", {}), default=str)
    design.codon_optimized = json.dumps(result.get("codon_optimized", {}), default=str)
    design.dna_sequence = result.get("dna_sequence", design.dna_sequence)
    design.fasta_content = result.get("fasta_content", design.fasta_content)
    design.plasmid_map_data = json.dumps(result.get("plasmid_map", {}), default=str)
    design.fba_results = json.dumps(result.get("fba_results", {}), default=str)
    design.assembly_plan = json.dumps(result.get("assembly_plan", {}), default=str)
    design.safety_score = safety["score"]
    design.safety_flags = json.dumps(safety["flags"])
    design.dual_use_assessment = safety["dual_use_assessment"]
    design.simulated_yield = result.get("simulated_yield", design.simulated_yield)
    design.generation_time_sec = round(time.time() - start, 2)

    assistant_msg = ChatMessage(
        design_id=design.id,
        role="assistant",
        content=result.get("refinement_summary", "Design updated."),
    )
    db.add(assistant_msg)

    audit = AuditLog(
        user_id=user.id,
        action="refine_design",
        details=json.dumps({"design_id": design.id, "refinement": req.message}),
        safety_flags=json.dumps(safety["flags"]),
    )
    db.add(audit)
    db.commit()
    db.refresh(design)

    return _design_response(design)


@router.get("/history")
def list_designs(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    designs = (
        db.query(Design).filter(Design.user_id == user.id)
        .order_by(Design.created_at.desc()).limit(50).all()
    )
    return [_design_response(d) for d in designs]


@router.get("/{design_id}", response_model=DesignResponse)
def get_design(design_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    design = db.query(Design).filter(Design.id == design_id, Design.user_id == user.id).first()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    return _design_response(design)


@router.get("/{design_id}/chat")
def get_chat(design_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    design = db.query(Design).filter(Design.id == design_id, Design.user_id == user.id).first()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    messages = db.query(ChatMessage).filter(ChatMessage.design_id == design.id).order_by(ChatMessage.created_at).all()
    return [{"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()} for m in messages]


@router.post("/{design_id}/share")
def toggle_share(design_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    design = db.query(Design).filter(Design.id == design_id, Design.user_id == user.id).first()
    if not design:
        raise HTTPException(status_code=404, detail="Design not found")
    design.is_public = not design.is_public
    db.commit()
    return {"is_public": design.is_public}


def _parse_json_field(value: str, default=None):
    if default is None:
        default = {}
    if not value:
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


def _design_response(design: Design) -> DesignResponse:
    gene_seqs = _parse_json_field(design.gene_sequences)

    # Derive conceptual flags from stored gene_sequences data
    non_registry = []
    conceptual = []
    for name, data in gene_seqs.items():
        if isinstance(data, dict):
            if data.get("source") != "ncbi_registry":
                non_registry.append(name)
            if data.get("conceptual_only"):
                conceptual.append(name)

    is_conceptual = bool(non_registry)
    conceptual_banner = ""
    if is_conceptual:
        conceptual_banner = settings.CONCEPTUAL_ONLY_BANNER
        if conceptual:
            conceptual_banner += (
                f" Genes with no verified biological parts: "
                f"{', '.join(conceptual)}."
            )

    return DesignResponse(
        id=design.id,
        status=design.status,
        design_name=design.design_name,
        host_organism=design.host_organism or "",
        organism_summary=design.organism_summary,
        gene_circuit=_parse_json_field(design.gene_circuit),
        gene_sequences=gene_seqs,
        codon_optimized=_parse_json_field(design.codon_optimized),
        dna_sequence=design.dna_sequence,
        fasta_content=design.fasta_content,
        plasmid_map_data=_parse_json_field(design.plasmid_map_data),
        fba_results=_parse_json_field(design.fba_results),
        assembly_plan=_parse_json_field(design.assembly_plan),
        safety_score=design.safety_score,
        safety_flags=_parse_json_field(design.safety_flags, []),
        dual_use_assessment=design.dual_use_assessment,
        simulated_yield=design.simulated_yield,
        estimated_cost=design.estimated_cost,
        target_product=design.target_product or "",
        generation_time_sec=design.generation_time_sec,
        model_used=design.model_used,
        is_public=design.is_public,
        disclaimer=settings.DISCLAIMER,
        is_conceptual=is_conceptual,
        conceptual_banner=conceptual_banner,
        non_registry_genes=non_registry,
        conceptual_genes=conceptual,
    )
