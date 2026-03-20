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
    stripe_customer_id = Column(String, default="")
    stripe_subscription_id = Column(String, default="")
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
    bump_count = Column(Integer, default=0)
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


class ApiKey(Base):
    """API keys for programmatic access (Pro tier)."""
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String, nullable=False)  # bcrypt hash of the key
    name = Column(String, default="Default")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=None)
    is_active = Column(Boolean, default=True)


class Bump(Base):
    """One bump per user per design. Bumps = community endorsement."""
    __tablename__ = "bumps"

    id = Column(String, primary_key=True, default=gen_id)
    design_id = Column(String, ForeignKey("designs.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DesignComment(Base):
    """Community comments on public designs."""
    __tablename__ = "design_comments"

    id = Column(String, primary_key=True, default=gen_id)
    design_id = Column(String, ForeignKey("designs.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DesignVersion(Base):
    """Stores snapshots of a design before each refinement (Pro tier)."""
    __tablename__ = "design_versions"

    id = Column(String, primary_key=True, default=gen_id)
    design_id = Column(String, ForeignKey("designs.id"), nullable=False)
    version_number = Column(Integer, default=1)
    design_name = Column(String, default="")
    organism_summary = Column(Text, default="")
    gene_circuit = Column(Text, default="")
    gene_sequences = Column(Text, default="{}")
    dna_sequence = Column(Text, default="")
    fba_results = Column(Text, default="{}")
    assembly_plan = Column(Text, default="{}")
    safety_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(String, primary_key=True, default=gen_id)
    session_id = Column(String, nullable=False, index=True)
    user_id = Column(String, default="")  # empty for anonymous
    event_type = Column(String, nullable=False)  # page_view, click, scroll_depth, funnel_step, time_on_page, drop_off
    page = Column(String, default="")
    element = Column(String, default="")  # button id, section name, tab name
    value = Column(String, default="")  # scroll percentage, time in seconds, etc.
    metadata_ = Column("metadata", Text, default="{}")  # JSON for extra context (column named "metadata" in DB)
    created_at = Column(DateTime, default=datetime.utcnow)


class LabResult(Base):
    """User-submitted experimental results for a gene/design.
    Enables data-driven variant ranking over time."""
    __tablename__ = "lab_results"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    design_id = Column(String, ForeignKey("designs.id"), nullable=False)
    gene_name = Column(String, nullable=False)          # e.g. "petase"
    sequence = Column(Text, default="")                  # AA or DNA sequence tested
    sequence_type = Column(String, default="protein")    # "protein" or "dna"
    mutations = Column(String, default="")               # e.g. "S238F/W159H" or "wild_type"
    organism = Column(String, default="")                # chassis used
    result_type = Column(String, default="activity")     # activity, expression, stability, growth
    assay_method = Column(String, default="")            # plate_reader, hplc, gel, etc.
    value = Column(Float, default=0.0)                   # measured value
    unit = Column(String, default="")                    # e.g. "U/mg", "mg/L", "°C"
    is_control = Column(Boolean, default=False)          # True = wild-type/negative control
    experiment_id = Column(String, default="")           # groups replicates
    replicate_number = Column(Integer, default=1)        # 1, 2, 3 for triplicates
    conditions = Column(Text, default="{}")              # JSON: temp, pH, media, etc.
    notes = Column(Text, default="")                     # free text
    success = Column(Boolean, default=True)              # did it work at all?
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=gen_id)
    user_id = Column(String, nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text, default="")
    safety_flags = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
