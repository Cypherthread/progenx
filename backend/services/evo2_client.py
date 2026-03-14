"""
Evo 2 integration for DNA sequence generation.

Two modes:
1. NVIDIA hosted API (free tier at build.nvidia.com) — default, fast
2. Local HuggingFace model (7B) — offline, requires GPU

Evo 2 is a genomic foundation model from the Arc Institute that generates
biologically plausible DNA sequences given a prompt/seed sequence.
"""

import httpx
from config import settings

# Optional local model import
_local_model = None
_local_tokenizer = None


def generate_sequence_nvidia(
    seed_sequence: str,
    num_tokens: int = 256,
    temperature: float = 0.7,
    top_k: int = 4,
) -> str:
    """Generate DNA sequence via NVIDIA hosted Evo 2 40B API."""
    if not settings.EVO2_NVIDIA_API_KEY:
        raise RuntimeError(
            "EVO2_NVIDIA_API_KEY not set. Get a free key at https://build.nvidia.com/arc/evo2-40b"
        )

    headers = {
        "Authorization": f"Bearer {settings.EVO2_NVIDIA_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "sequence": seed_sequence,
        "num_tokens": num_tokens,
        "temperature": temperature,
        "top_k": top_k,
    }

    with httpx.Client(timeout=120.0) as client:
        resp = client.post(settings.EVO2_NVIDIA_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    return data.get("sequence", seed_sequence)


def generate_sequence_local(
    seed_sequence: str,
    num_tokens: int = 256,
    temperature: float = 0.7,
) -> str:
    """Generate DNA sequence via local Evo 2 7B model (HuggingFace)."""
    global _local_model, _local_tokenizer

    if _local_model is None:
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
        except ImportError:
            raise RuntimeError(
                "Install transformers + torch for local Evo 2: pip install transformers torch"
            )

        _local_tokenizer = AutoTokenizer.from_pretrained(
            settings.EVO2_HF_MODEL, trust_remote_code=True
        )
        _local_model = AutoModelForCausalLM.from_pretrained(
            settings.EVO2_HF_MODEL,
            trust_remote_code=True,
            torch_dtype=torch.float16,
            device_map="auto",
        )

    import torch

    inputs = _local_tokenizer(seed_sequence, return_tensors="pt").to(_local_model.device)

    with torch.no_grad():
        outputs = _local_model.generate(
            **inputs,
            max_new_tokens=num_tokens,
            temperature=temperature,
            do_sample=True,
            top_k=4,
        )

    generated = _local_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated


def generate_sequence(
    seed_sequence: str,
    num_tokens: int = 256,
    temperature: float = 0.7,
) -> str:
    """Generate DNA sequence using configured Evo 2 backend."""
    if settings.EVO2_USE_LOCAL:
        return generate_sequence_local(seed_sequence, num_tokens, temperature)
    else:
        return generate_sequence_nvidia(seed_sequence, num_tokens, temperature)


def validate_dna_sequence(sequence: str) -> dict:
    """Basic validation that a sequence is valid DNA."""
    clean = sequence.upper().replace("\n", "").replace(" ", "")
    valid_chars = set("ATCGN")
    invalid = set(clean) - valid_chars
    gc_count = clean.count("G") + clean.count("C")
    gc_content = gc_count / len(clean) if clean else 0

    return {
        "is_valid": len(invalid) == 0 and len(clean) > 0,
        "length": len(clean),
        "gc_content": round(gc_content, 3),
        "invalid_chars": list(invalid),
        "sequence": clean,
    }
