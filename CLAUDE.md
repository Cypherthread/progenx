# CLAUDE.md — ProtoForge

## What This Is

**ProtoForge** — an AI-powered bioengineering design platform that lets users describe custom microbes, enzymes, and genetic circuits in plain English and get back real gene circuits, DNA sequences, plasmid maps, safety scores, FBA yield predictions, assembly plans, and vendor links. Think "Canva for synthetic biology."

Target users: biohackers, students, iGEM teams, early-stage climate founders, researchers who need the first 80% of ideation without a PhD or million-dollar budget.

## Stack

### Backend (`backend/`)
- **Python 3.12 + FastAPI** — REST API
- **SQLAlchemy + SQLite** — ORM + database (`protoforge.db`, auto-created on startup)
- **Anthropic Claude API** (claude-sonnet-4) — structured gene circuit design via LLM
- **BioPython + NCBI Entrez** — real CDS sequence fetching from GenBank
- **COBRApy** — flux balance analysis with genome-scale models (iJO1366 for E. coli, iJN1463 for P. putida)
- **dna_features_viewer** — circular plasmid map rendering (matplotlib backend)
- **JWT auth** (PyJWT + bcrypt) — user accounts, rate limiting (5 free designs/month)

### Frontend (`frontend/`)
- **React 19 + Vite 8 + TypeScript** — SPA
- **Tailwind CSS** — styling
- **Zustand** — state management (useDesign, useAuth stores)

### Deployment (`deploy/`)
- `docker-compose.yml`, `vercel.json`, `render.yaml` — deployment configs (not yet deployed)

## Key Commands

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend
npm run dev          # dev server on :5173
npx vite build       # production build → dist/

# Test user (after server starts)
curl -X POST http://localhost:8000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@protoforge.dev","password":"testpass123","name":"Test"}'
```

No test suite yet. Validation is manual via API calls.

## Architecture

### Design Pipeline (`services/llm_orchestrator.py`)
The core value — a 6-step pipeline that runs on every `/api/designs/generate` call:

1. **Claude designs the gene circuit** — structured JSON with real gene names, chassis, promoters, terminators, regulatory elements
2. **NCBI Entrez fetches real sequences** — hardcoded registry for 20+ common synbio genes (PETase, MHETase, PHA pathway, nif cluster, etc.), falls back to NCBI search
3. **Codon optimizer** — reverse-translates protein → DNA using per-chassis codon usage tables (E. coli, P. putida, S. elongatus)
4. **COBRApy FBA** — genome-scale metabolic models predict growth rates, metabolic burden, theoretical yields
5. **Assembly planner** — selects ori (pMB1/pBBR1/RSF1010), marker (kan/gent/spec), assembly method (Golden Gate/Gibson), kill switch (ccdA/ccdB, mazE/mazF)
6. **Plasmid visualizer** — circular construct map via dna_features_viewer with real bp positions

### Backend Services (`backend/services/`)
- `llm_orchestrator.py` — main pipeline coordinator
- `ncbi_client.py` — NCBI Entrez + hardcoded gene registry (CRITICAL: has alias system to avoid gene symbol collisions like cutA)
- `codon_optimizer.py` — per-chassis codon frequency tables
- `fba_engine.py` — COBRApy wrapper, downloads BiGG models on first use to `./fba_models/`
- `assembly_planner.py` — ori/marker/method/kill switch selection logic
- `plasmid_visualizer.py` — dna_features_viewer circular maps, SVG fallback
- `safety_scorer.py` — pathogen pattern matching, dual-use gene detection, resistance marker flagging
- `bio_engine.py` — sequence analysis utilities
- `evo2_client.py` — NVIDIA Evo2 API (fallback for novel sequences, rarely used)

### Backend Core
- `main.py` — FastAPI app, CORS, router mounting
- `models.py` — SQLAlchemy models (User, Design, ChatMessage, AuditLog)
- `auth.py` — JWT creation/verification, rate limiting
- `database.py` — SQLite session management
- `config.py` — settings from .env (API keys, disclaimer text, model paths)
- `routers/designs_router.py` — generate, refine, history, share endpoints
- `routers/auth_router.py` — signup, login, me
- `routers/challenges_router.py` — daily/random climate challenges

### Frontend Key Files
- `src/lib/api.ts` — API client + TypeScript interfaces for all response types
- `src/components/ResultsPanel.tsx` — main results display (NCBI provenance, codon opt, FBA, assembly, plasmid map, safety, FASTA download)
- `src/components/GeneCircuit.tsx` — visual gene circuit diagram
- `src/components/Sliders.tsx` — environment/safety/complexity controls
- `src/components/ShareButton.tsx` — public sharing toggle
- `src/pages/Studio.tsx` — main design page with error boundary
- `src/hooks/useDesign.ts` — Zustand design store
- `src/hooks/useAuth.ts` — Zustand auth store

## NCBI Gene Registry

The hardcoded registry in `ncbi_client.py` is critical for accuracy. Key decisions:

- **Protein accessions preferred** over nucleotide — proteins get codon-optimized for chassis anyway, avoids partial-CDS and whole-genome fetch bugs
- **UniProt IDs for PHA pathway** (P14611, P14697, P23608) — old GenBank J04987 accessions had swapped annotations
- **Alias system** — `cutA` redirects to `cutinase` (P00590, F. solani) to avoid bacterial divalent-cation tolerance protein collision
- **Post-fetch length validation** — rejects sequences outside 50-150% of expected_aa range, falls through to NCBI search
- **Generic size guard** — NCBI search skips any hit >1500 aa (polyproteins, wrong hits)

Current registry covers: petase, mhetase, phaA/B/C, rbcL/S, ccmK/M, nifH/D/K, alkB, opdA, cutinase, cah, ccdA/B, gfp

## Environment & Secrets

```bash
# backend/.env (chmod 600, git-ignored)
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET=...
CORS_ORIGINS=http://localhost:5173
DATABASE_URL=sqlite:///./protoforge.db
EVO2_NVIDIA_API_KEY=nvapi-...     # optional
NCBI_EMAIL=protoforge@paperst.co  # required for Entrez
NCBI_API_KEY=                      # optional, increases rate limit
```

## Critical Rules

- **Every output includes disclaimer**: "EDUCATIONAL/EXPERIMENTAL ONLY — NOT LAB-READY WITHOUT EXPERT REVIEW" (enforced in `config.py`, rendered top+bottom in ResultsPanel)
- **Safety scoring is mandatory** — runs on every design before returning to user
- **Real genes only** — Claude prompt explicitly forbids inventing gene names
- **No fake sequences** — all DNA comes from NCBI fetch + codon optimization, never generated/padded
- **Audit logging** — every generate/refine action logged with user ID and safety flags

## Known Limitations / Future Work

- FBA uses iJO1366 (E. coli) for all chassis — need iJN1463 download for P. putida
- COBRApy model download happens on first FBA call (~30s)
- NCBI search fallback can return wrong proteins (gene name ambiguity) — registry is the fix
- No Benchling/SnapGene export yet (APIs exist)
- No Evo2 de novo sequence generation (stub exists)
- No user accession override UI
- No test suite — validation is manual API calls
- Not deployed yet — local dev only
