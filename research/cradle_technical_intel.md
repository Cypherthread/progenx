# Cradle Technical Intelligence — Reverse Engineering Report
## March 15, 2026

### Key Finding
Cradle's competitive advantage is NOT a single breakthrough model. It's the integration of:
1. Foundation model embeddings (ESM-2 or similar)
2. Adaptive exploration algorithms (AdaLead — open-sourced at github.com/samsinai/FLEXS)
3. Experimental data feedback loops

ProtoForge can replicate 1 and 2 with open-source tools today.

### Founder Research Origins
- Sam Sinai (co-founder) published:
  - FLEXS: github.com/samsinai/FLEXS (170 stars) — fitness landscape exploration benchmark
  - AdaLead: adaptive greedy search for sequence design (Sinai et al. 2020)
  - EVOVAE: VAE for protein sequences (arxiv.org/abs/1712.03346, NIPS MLCB 2017)

### Implementation Priority for ProtoForge

**Phase 1 (1-2 weeks):**
- ESM-2 zero-shot variant scoring (pip install fair-esm)
- ESMFold structure prediction via public API

**Phase 2 (2-4 weeks):**
- ProtGPT2 de novo generation for novel enzymes
- AdaLead from FLEXS for in-silico directed evolution

**Phase 3 (1-2 months):**
- BioNeMo CodonFM for learned codon optimization
- ProteinMPNN for structure-guided sequence design
- Active learning loop for user experimental data

### Open-Source Tools to Integrate
| Tool | What | License | Repo |
|------|------|---------|------|
| ESM-2 | Protein language model (650M params) | MIT | github.com/facebookresearch/esm |
| ProteinMPNN | Sequence design from structure | MIT | github.com/dauparas/ProteinMPNN |
| ESMFold | Structure prediction (no MSA) | MIT | Part of ESM package |
| ProtGPT2 | De novo protein generation | Apache 2.0 | huggingface.co/nferruz/ProtGPT2 |
| FLEXS | Fitness landscape exploration | MIT | github.com/samsinai/FLEXS |
| RFdiffusion | De novo structure design | BSD | github.com/RosettaCommons/RFdiffusion |
| BioNeMo | NVIDIA bio framework + CodonFM | Apache 2.0 | github.com/NVIDIA/bionemo-framework |
| ESM3 | Multimodal protein AI (1.4B open) | Various | github.com/EvolutionaryScale/esm |

### Datasets to Index
- UniRef50/90: ~50M protein sequences
- PDB: ~220K structures
- FLIP: Fitness landscape benchmarks
- ProteinGym: ~300 DMS assays
- BRENDA: Enzyme kinetics (Km, kcat)
- iGEM Parts Registry: Characterized genetic parts
