import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "ProtoForge"
    VERSION = "0.2.0"
    TAGLINE = (
        "We help scientists, climate innovators, bio-hackers, and everyday "
        "problem-solvers design custom microbes, enzymes, and genetic circuits "
        "in plain English — without a PhD, wet lab, or million-dollar budget."
    )

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./protoforge.db")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # NCBI Entrez (required for real sequence fetching)
    NCBI_EMAIL = os.getenv("NCBI_EMAIL", "protoforge@example.com")
    NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")  # optional, increases rate limit

    # Evo 2 — NVIDIA hosted API (free tier at build.nvidia.com)
    EVO2_NVIDIA_API_KEY = os.getenv("EVO2_NVIDIA_API_KEY", "")
    EVO2_NVIDIA_URL = "https://health.api.nvidia.com/v1/biology/arc-institute/evo2-40b/generate"
    # Fallback: local HuggingFace 7B
    EVO2_HF_MODEL = "arcinstitute/evo2_7b"
    EVO2_USE_LOCAL = os.getenv("EVO2_USE_LOCAL", "false").lower() == "true"

    # COBRApy genome-scale models (downloaded on first use)
    FBA_MODELS_DIR = os.getenv("FBA_MODELS_DIR", "./fba_models")

    # Auth
    JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRY_HOURS = 72

    # Rate limiting (free tier)
    FREE_TIER_MONTHLY_DESIGNS = 5

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    # Lab disclaimer on every output
    DISCLAIMER = (
        "EDUCATIONAL/EXPERIMENTAL ONLY — NOT LAB-READY WITHOUT EXPERT REVIEW. "
        "Designs are computational predictions. Any laboratory implementation "
        "must comply with institutional biosafety committees (IBC), NIH Guidelines "
        "for Recombinant or Synthetic Nucleic Acid Molecules, and all applicable "
        "regulations. Do not synthesize or release engineered organisms without "
        "proper authorization and containment."
    )


settings = Settings()
