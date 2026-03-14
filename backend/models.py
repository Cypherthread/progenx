from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import uuid


def gen_id():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_id)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, default="")
    tier = Column(String, default="free")
    designs_this_month = Column(Integer, default=0)
    month_reset = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    designs = relationship("Design", back_populates="user")


class Design(Base):
    __tablename__ = "designs"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    organism_type = Column(String, default="")
    environment = Column(String, default="ocean")
    safety_level = Column(Float, default=0.7)
    complexity = Column(Float, default=0.5)

    # Generated outputs
    design_name = Column(String, default="")
    host_organism = Column(String, default="")
    organism_summary = Column(Text, default="")
    gene_circuit = Column(Text, default="")       # JSON
    gene_sequences = Column(Text, default="{}")    # JSON: NCBI results per gene
    codon_optimized = Column(Text, default="{}")   # JSON: optimized sequences
    dna_sequence = Column(Text, default="")
    fasta_content = Column(Text, default="")
    plasmid_map_data = Column(Text, default="{}")  # JSON: features + base64 image
    fba_results = Column(Text, default="{}")       # JSON: COBRApy output
    assembly_plan = Column(Text, default="{}")     # JSON: ori, marker, kill switch, method
    safety_score = Column(Float, default=0.0)
    safety_flags = Column(Text, default="[]")
    dual_use_assessment = Column(Text, default="")
    simulated_yield = Column(String, default="")
    estimated_cost = Column(String, default="")
    target_product = Column(String, default="")

    # Metadata
    generation_time_sec = Column(Float, default=0.0)
    model_used = Column(String, default="")
    status = Column(String, default="pending")
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="designs")
    messages = relationship("ChatMessage", back_populates="design")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=gen_id)
    design_id = Column(String, ForeignKey("designs.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    design = relationship("Design", back_populates="messages")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text, default="")
    safety_flags = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
