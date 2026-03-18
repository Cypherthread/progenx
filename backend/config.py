import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = "Progenx"
    VERSION = "0.2.0"
    TAGLINE = (
        "We help scientists, climate innovators, bio-hackers, and everyday "
        "problem-solvers design custom microbes, enzymes, and genetic circuits "
        "in plain English — without a PhD, wet lab, or million-dollar budget."
    )

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./progenx.db")
    CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # NCBI Entrez (required for real sequence fetching)
    NCBI_EMAIL = os.getenv("NCBI_EMAIL", "progenx@example.com")
    NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")  # optional, increases rate limit

    # Free-tier LLM (Groq in cloud, Ollama local — OpenAI-compatible API)
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")  # "ollama" for local, real key for Groq/cloud

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

    # Stripe (Pro tier payments)
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID", "")  # $29/mo recurring price
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # ESM-2 protein variant scoring (optional — needs PyTorch + transformers)
    # Smaller model (35M) is fast on CPU. Larger (650M) is more accurate but slower.
    ESM_MODEL = os.getenv("ESM_MODEL", "facebook/esm2_t12_35M_UR50D")

    # Airtable CRM (optional, syncs users + designs for email campaigns)
    AIRTABLE_API_TOKEN = os.getenv("AIRTABLE_API_TOKEN", "")
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
    AIRTABLE_USERS_TABLE = os.getenv("AIRTABLE_USERS_TABLE", "Users")
    AIRTABLE_DESIGNS_TABLE = os.getenv("AIRTABLE_DESIGNS_TABLE", "Designs")

    # SecureDNA hazard screening (optional — run synthclient locally)
    # Register at: https://securedna.org/cert-request/
    # Docker: docker run -p 8080:80 ghcr.io/securedna/synthclient
    SECUREDNA_URL = os.getenv("SECUREDNA_URL", "")  # e.g. http://localhost:8080

    # Lab disclaimer on every output
    DISCLAIMER = (
        "EDUCATIONAL/EXPERIMENTAL ONLY — NOT LAB-READY WITHOUT EXPERT REVIEW. "
        "Designs are computational predictions. Any laboratory implementation "
        "must comply with institutional biosafety committees (IBC), NIH Guidelines "
        "for Recombinant or Synthetic Nucleic Acid Molecules, and all applicable "
        "regulations. Do not synthesize or release engineered organisms without "
        "proper authorization and containment."
    )

    # Shown when design uses genes outside the verified registry
    CONCEPTUAL_ONLY_BANNER = (
        "WARNING — CONCEPTUAL DESIGN: This design uses genes not in our verified "
        "registry. Biology may not support the requested function. NCBI search "
        "results may not match the intended biological function. Lab validation "
        "required before any experimental work."
    )


settings = Settings()
