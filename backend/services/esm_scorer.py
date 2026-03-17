"""
ESM-2 protein variant scoring — zero-shot mutation effect prediction.

Uses Meta's ESM-2 protein language model to predict which single-residue
mutations in a protein are likely beneficial, neutral, or deleterious.

Approach: Wild-type marginal scoring (single forward pass). For each position
in the protein, computes the model's predicted probability for every amino acid.
Mutations where P(mutant) > P(wild-type) are flagged as potentially beneficial.

This is a COMPUTATIONAL PREDICTION, not experimental validation. ESM-2 scores
correlate with experimental deep mutational scanning data (Spearman rho ~0.4-0.5)
but are not a substitute for wet-lab testing.

Model options:
  - esm2_t12_35M_UR50D: 35M params, ~140 MB, fast on CPU (1-5s per protein)
  - esm2_t33_650M_UR50D: 650M params, ~2.6 GB, better quality (5-30s on CPU)

The model is lazily loaded on first use and cached as a singleton. If PyTorch
is not installed or the model can't load, scoring is skipped gracefully.
"""

from config import settings

# Standard amino acids
AMINO_ACIDS = "ACDEFGHIKLMNPQRSTVWY"

# Max protein length to score (guard against memory spikes)
MAX_PROTEIN_LENGTH = 1000

# Minimum number of beneficial mutations to report
TOP_N_MUTATIONS = 10

# Model cache (singleton, loaded lazily)
_model = None
_tokenizer = None
_model_ready = False
_model_error = None


def _get_model():
    """Lazily load the ESM-2 model. Returns (model, tokenizer) or (None, None)."""
    global _model, _tokenizer, _model_ready, _model_error

    if _model_ready:
        return _model, _tokenizer

    if _model_error:
        return None, None  # Already failed, don't retry

    try:
        import torch
        from transformers import AutoTokenizer, EsmForMaskedLM

        model_name = getattr(settings, "ESM_MODEL", "facebook/esm2_t12_35M_UR50D")
        print(f"[ESM] Loading {model_name}...")

        _tokenizer = AutoTokenizer.from_pretrained(model_name)
        _model = EsmForMaskedLM.from_pretrained(model_name)
        _model.eval()
        _model_ready = True

        param_count = sum(p.numel() for p in _model.parameters()) / 1e6
        print(f"[ESM] Model loaded: {param_count:.0f}M parameters")
        return _model, _tokenizer

    except ImportError:
        _model_error = "PyTorch or transformers not installed"
        print(f"[ESM] Skipping: {_model_error}")
        return None, None
    except Exception as e:
        _model_error = str(e)
        print(f"[ESM] Failed to load model: {_model_error}")
        return None, None


def score_variants(protein_sequence: str) -> dict | None:
    """Score all single-residue mutations in a protein using ESM-2.

    Returns a dict with:
      - beneficial_mutations: list of predicted beneficial mutations (top N)
      - total_scored: number of positions scored
      - model_used: which ESM-2 model was used
      - method: "wild_type_marginal"

    Returns None if ESM-2 is not available or sequence is invalid.
    """
    if not protein_sequence:
        return None

    # Clean sequence
    seq = protein_sequence.upper().replace("*", "").replace("X", "").strip()
    if not seq:
        return None

    # Length guard
    if len(seq) > MAX_PROTEIN_LENGTH:
        print(f"[ESM] Skipping: protein too long ({len(seq)} aa > {MAX_PROTEIN_LENGTH} max)")
        return {
            "beneficial_mutations": [],
            "total_scored": 0,
            "model_used": "skipped",
            "method": "sequence_too_long",
            "note": f"Protein exceeds {MAX_PROTEIN_LENGTH} aa limit for variant scoring.",
        }

    # Validate sequence contains only standard amino acids
    non_standard = set(seq) - set(AMINO_ACIDS)
    if non_standard:
        # Remove non-standard residues for scoring
        seq = "".join(c for c in seq if c in AMINO_ACIDS)
        if len(seq) < 10:
            return None

    model, tokenizer = _get_model()
    if model is None or tokenizer is None:
        return None

    try:
        import torch

        # Tokenize
        inputs = tokenizer(seq, return_tensors="pt")

        # Single forward pass — wild-type marginal scoring
        with torch.no_grad():
            logits = model(**inputs).logits
            log_probs = torch.log_softmax(logits, dim=-1)

        # Build amino acid token ID mapping
        aa_to_id = {}
        for aa in AMINO_ACIDS:
            token_id = tokenizer.convert_tokens_to_ids(aa)
            if token_id != tokenizer.unk_token_id:
                aa_to_id[aa] = token_id

        if not aa_to_id:
            print("[ESM] Could not map amino acids to token IDs")
            return None

        # Score all mutations
        beneficial = []
        neutral = []
        deleterious_count = 0

        for pos_idx, wt_aa in enumerate(seq):
            if wt_aa not in aa_to_id:
                continue

            token_pos = pos_idx + 1  # offset for BOS token
            wt_score = log_probs[0, token_pos, aa_to_id[wt_aa]].item()

            for mut_aa in AMINO_ACIDS:
                if mut_aa == wt_aa or mut_aa not in aa_to_id:
                    continue

                mut_score = log_probs[0, token_pos, aa_to_id[mut_aa]].item()
                delta = mut_score - wt_score

                if delta > 0:
                    beneficial.append({
                        "position": pos_idx + 1,
                        "wild_type": wt_aa,
                        "mutant": mut_aa,
                        "score": round(delta, 3),
                        "notation": f"{wt_aa}{pos_idx + 1}{mut_aa}",
                    })
                elif delta > -1.0:
                    neutral.append(1)
                else:
                    deleterious_count += 1

        # Sort by score descending
        beneficial.sort(key=lambda x: x["score"], reverse=True)

        model_name = getattr(settings, "ESM_MODEL", "facebook/esm2_t12_35M_UR50D")

        return {
            "beneficial_mutations": beneficial[:TOP_N_MUTATIONS],
            "total_beneficial": len(beneficial),
            "total_neutral": len(neutral),
            "total_deleterious": deleterious_count,
            "total_scored": len(seq),
            "model_used": model_name.split("/")[-1],
            "method": "wild_type_marginal",
            "note": (
                "ESM-2 zero-shot predictions. Positive scores indicate the mutant "
                "amino acid is more probable than wild-type at that position, suggesting "
                "the mutation may be tolerated or beneficial. These are computational "
                "predictions (Spearman rho ~0.4-0.5 with experimental data) — "
                "wet-lab validation is required."
            ),
        }

    except Exception as e:
        print(f"[ESM] Scoring failed: {e}")
        return None
