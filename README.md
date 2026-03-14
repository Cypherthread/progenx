# ProtoForge

**Bioengineer Anything in Plain English**

We help scientists, climate innovators, bio-hackers, and everyday problem-solvers design custom microbes, enzymes, and genetic circuits in plain English so they can tackle plastic-eating oceans, carbon-capturing bacteria, personalized medicine, or drought-proof crops — without a PhD, wet lab, or million-dollar budget.

## Features

- **Single prompt box** — describe what you want: "Design a microbe that eats ocean microplastics"
- **Evo 2 genomic AI** — Arc Institute's 40B parameter model generates biologically plausible DNA
- **Claude AI orchestration** — structured design with real genes, promoters, regulatory elements
- **Interactive plasmid maps** — Plotly-powered circular maps with hover details
- **Safety scoring** — mandatory dual-use flagging, pathogen screening, biosafety assessment
- **Chat refinement** — "Make it 30% more efficient" or "Add kanamycin resistance"
- **FASTA export** — download sequences, copy to clipboard, order from Twist/IDT
- **Daily climate challenges** — 20 curated prompts from ocean plastic to drought-proof crops
- **Viral share button** — "I just designed a plastic-eating bug in 47 seconds"
- **Per-user memory** — ChromaDB vector embeddings remember your past designs

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 + Vite + Tailwind CSS + Zustand |
| Backend | FastAPI (Python 3.12) |
| LLM | Anthropic Claude API + LangChain |
| Genomics | Evo 2 (NVIDIA API / HuggingFace 7B) |
| Biology | BioPython + RDKit |
| Database | SQLite + ChromaDB (vector embeddings) |
| Visualization | Plotly.js (interactive plasmid maps) |
| Auth | JWT (built-in) |
| External APIs | NCBI BLAST, iGEM Parts Registry, UniProt, AlphaFold DB |

## Quick Start (Local)

### Prerequisites

- Python 3.12+
- Node.js 20+
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

### 1. Get a free Evo 2 API key

Go to [build.nvidia.com/arc/evo2-40b](https://build.nvidia.com/arc-institute/evo2-40b) and click "Get API Key". The free tier gives you 1,000 requests/month.

**Or run the 7B model locally** (requires ~16GB VRAM):
```bash
pip install transformers torch
# Set EVO2_USE_LOCAL=true in your .env
```

### 2. Backend setup

```bash
cd protoforge/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY and EVO2_NVIDIA_API_KEY

# Start the API server
uvicorn main:app --reload --port 8000
```

API docs at http://localhost:8000/docs

### 3. Frontend setup

```bash
cd protoforge/frontend

npm install
npm run dev
```

Open http://localhost:5173 — the Vite dev server proxies `/api` to the backend.

### 4. Use it

1. Sign up at http://localhost:5173
2. Go to Design Studio
3. Type: "Design a microbe that eats ocean microplastics and turns them into biodegradable plastic"
4. Adjust sliders (environment, safety, complexity)
5. Hit Generate
6. Explore the plasmid map, download FASTA, refine through chat

## Docker

```bash
cd protoforge
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

docker compose up --build
```

Frontend: http://localhost:5173 | Backend: http://localhost:8000

## Deploy (Free Tier)

### Frontend → Vercel

1. Push to GitHub
2. Import repo in [vercel.com](https://vercel.com)
3. Set root directory to `frontend`
4. Framework: Vite
5. Add environment variable: `VITE_API_URL=https://your-render-backend.onrender.com`
6. Deploy

### Backend → Render

1. Create new Web Service at [render.com](https://render.com)
2. Connect GitHub repo
3. Root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `ANTHROPIC_API_KEY`
   - `EVO2_NVIDIA_API_KEY`
   - `JWT_SECRET` (generate a random string)
   - `CORS_ORIGINS` = your Vercel URL
7. Add a 1GB disk mounted at `/app` for SQLite persistence

### Update Vercel rewrites

In `deploy/vercel.json`, replace `your-render-backend.onrender.com` with your actual Render URL.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/signup` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Current user profile |
| POST | `/api/designs/generate` | Generate a new design |
| POST | `/api/designs/{id}/refine` | Refine existing design |
| GET | `/api/designs/history` | List user's designs |
| GET | `/api/designs/{id}` | Get specific design |
| GET | `/api/designs/{id}/chat` | Get chat history |
| POST | `/api/designs/{id}/share` | Toggle public sharing |
| GET | `/api/challenges/daily` | Today's climate challenge |
| GET | `/api/challenges/all` | All challenge prompts |

## Safety & Regulatory Notes

ProtoForge includes mandatory safety features:

- **Dual-use screening**: Every design is checked against known pathogenic sequence patterns, select agent gene lists, and antibiotic resistance markers
- **Safety score**: 0-100% score with detailed flags and assessment
- **Audit log**: All design requests are logged with safety flags
- **Disclaimers**: All outputs include regulatory compliance notices
- **Vendor screening**: DNA synthesis vendors (Twist, IDT) perform additional IGSC-compliant screening before synthesis

**This tool is for educational and research purposes.** Any laboratory implementation must comply with:
- Institutional Biosafety Committees (IBC)
- NIH Guidelines for Research Involving Recombinant or Synthetic Nucleic Acid Molecules
- All applicable local, national, and international biosafety regulations
- Cartagena Protocol on Biosafety (for transboundary movement)

## License

MIT License for the open-source core. See [LICENSE](LICENSE) for details.

Proprietary components (Pro/Team only):
- Production safety screening layer (full IGSC database)
- Evo 2 fine-tuned model weights
- Curated training datasets
