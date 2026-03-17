#!/usr/bin/env python3
"""
===============================================================================
ProtoForge x MiroFish Business Swarm Simulator
===============================================================================

WHAT THIS DOES:
  Sets up MiroFish (an LLM-powered multi-agent social simulation engine),
  generates a ProtoForge seed file, launches the Docker environment, and
  provides a ready-to-paste prediction prompt for the MiroFish web UI.

  MiroFish simulates thousands of AI agents interacting on simulated social
  platforms (Twitter-like / Reddit-like) to predict opinion trajectories
  and emergent outcomes. It is NOT a traditional financial model — it
  produces qualitative foresight via agent consensus, not spreadsheet math.

  You will use the web UI to upload the seed file, paste the prediction
  prompt, and run the simulation. The script automates everything up to
  that point.

PREREQUISITES:
  - Docker + Docker Compose installed and running
  - Python 3.10+
  - Git
  - Ollama installed locally (FREE — no API keys needed)
    OR an OpenAI-compatible API key (paid)
  - A Zep Cloud API key (free tier: https://app.getzep.com/)

QUICK START (FREE — Ollama mode, no cloud LLM costs):

  1. Install Ollama:       https://ollama.com/download
  2. Start Ollama:         $ ollama serve
  3. Pull a model:         $ ollama pull llama3.1:8b
  4. Get a Zep key:        https://app.getzep.com/ (free tier)
  5. Run this script:      $ python protoforge_mirofish_simulator.py --ollama
  6. Open the UI:          http://localhost:3000
  7. Upload seed file, paste prompt, run simulation.

ALTERNATIVE (Cloud LLM — higher quality, costs money):

  1. Get your API keys:
     - LLM: https://platform.openai.com/api-keys
     - Zep: https://app.getzep.com/
  2. Run: $ python protoforge_mirofish_simulator.py --cloud
  3. Paste your keys when prompted.

FLAGS:
  --ollama    Use local Ollama (default, free, no cloud LLM key needed)
  --cloud     Use cloud LLM (OpenAI/Qwen — prompts for API key)
  --update    Regenerate seed file only (for weekly reruns)
  --model X   Override Ollama model (default: llama3.1:8b)

EXAMPLES:
  $ python protoforge_mirofish_simulator.py                    # Ollama default
  $ python protoforge_mirofish_simulator.py --ollama           # Explicit Ollama
  $ python protoforge_mirofish_simulator.py --model qwen2:7b   # Use Qwen locally
  $ python protoforge_mirofish_simulator.py --cloud            # Use OpenAI
  $ python protoforge_mirofish_simulator.py --update           # Weekly rerun

HOW TO STOP:
  $ cd mirofish && docker compose down
  $ ollama stop  (optional — Ollama uses minimal resources when idle)

COST:
  Ollama mode:  $0 (runs entirely on your machine)
  Cloud mode:   ~$2-25 per simulation run depending on agent count

===============================================================================
"""

import os
import sys
import subprocess
import shutil
import textwrap
import webbrowser
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

# ── Configuration ────────────────────────────────────────────────────

MIROFISH_REPO = "https://github.com/666ghj/MiroFish.git"
MIROFISH_DIR = Path(__file__).parent / "mirofish"
SEED_FILE = MIROFISH_DIR / "seed_protoforge.txt"
PROMPT_FILE = Path(__file__).parent / "prediction_prompt.txt"
REPORT_TEMPLATE = Path(__file__).parent / "report_template.md"
MIROFISH_UI_URL = "http://localhost:3000"
MIROFISH_API_URL = "http://localhost:5001"

# Default Ollama settings
DEFAULT_OLLAMA_MODEL = "llama3.1:8b"
# From inside Docker, Ollama on the host is reachable at:
#   Linux:   http://host.docker.internal:11434  (with --add-host in compose)
#            or http://172.17.0.1:11434          (docker bridge IP)
#   macOS:   http://host.docker.internal:11434   (native Docker Desktop support)
#   WSL2:    http://host.docker.internal:11434   (Docker Desktop for Windows)
OLLAMA_DOCKER_URL = "http://host.docker.internal:11434/v1"
OLLAMA_LOCAL_URL = "http://localhost:11434/v1"

# Update these weekly with real traction numbers before rerunning
TRACTION_DATA = {
    "date": "2026-03-14",
    "registered_users": 0,
    "monthly_active_users": 0,
    "designs_generated": 0,
    "pro_subscribers": 0,
    "mrr_usd": 0,
    "product_hunt_upvotes": 0,
    "igem_teams_contacted": 0,
    "wait_list": 0,
    "github_stars": 0,
    "twitter_followers": 0,
    "notable_events": "MVP complete. Launching on Product Hunt this week.",
}


# ── CLI Argument Parsing ─────────────────────────────────────────────

def parse_args() -> dict:
    """Parse command-line arguments into a config dict."""
    args = sys.argv[1:]
    config = {
        "mode": "ollama",       # default to free Ollama mode
        "model": DEFAULT_OLLAMA_MODEL,
        "update_only": False,
    }

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--ollama":
            config["mode"] = "ollama"
        elif arg == "--cloud":
            config["mode"] = "cloud"
        elif arg == "--update":
            config["update_only"] = True
        elif arg == "--model" and i + 1 < len(args):
            i += 1
            config["model"] = args[i]
            config["mode"] = "ollama"  # --model implies Ollama
        elif arg.startswith("--model="):
            config["model"] = arg.split("=", 1)[1]
            config["mode"] = "ollama"
        else:
            print(f"  Unknown flag: {arg}")
            print(f"  Usage: python {Path(__file__).name} [--ollama|--cloud] [--model X] [--update]")
            sys.exit(1)
        i += 1

    return config


# ── Seed File Content ────────────────────────────────────────────────

def build_seed_content() -> str:
    """Generate the ProtoForge seed document for MiroFish ingestion."""
    t = TRACTION_DATA
    return textwrap.dedent(f"""\
    =========================================================================
    PROTOFORGE — AI-POWERED BIOENGINEERING DESIGN PLATFORM
    Seed Material for MiroFish Swarm Prediction Engine
    Generated: {t['date']}
    =========================================================================

    SECTION 1: PRODUCT OVERVIEW
    -------------------------------------------------------------------------
    ProtoForge is a web application that lets users describe custom microbes,
    enzymes, and genetic circuits in plain English and receive back:
      - Real gene circuits with verified gene names and regulatory elements
      - DNA sequences fetched from NCBI GenBank (not AI-generated)
      - Codon-optimized coding sequences for the target chassis organism
      - Flux Balance Analysis (FBA) via COBRApy with genome-scale models
        (iJO1366 for E. coli, iJN1463 for P. putida)
      - Circular plasmid/construct maps with real base-pair positions
      - Safety scores with dual-use screening and biosafety flags
      - Assembly plans (Golden Gate / Gibson) with ori, marker, kill switch
      - FASTA downloads ready for gene synthesis vendors (Twist, IDT)
      - NVIDIA Evo 2 protein generation as fallback for novel sequences

    Target metaphor: "Canva for synthetic biology."

    The platform includes biology hardening layers:
      - Hardcoded gene registry with verified NCBI accessions for 20+ genes
      - Organism-filtered NCBI searches to avoid gene-name collisions
      - LLM-based function validation (rejects wrong-protein NCBI hits)
      - Unsupported biology detection (flags functions with no known parts)
      - Conceptual-only banners for unverified designs

    SECTION 2: MARKET CONTEXT
    -------------------------------------------------------------------------
    Synthetic biology market size:
      - 2024: $19-25 billion globally
      - 2031 projected: $56+ billion (CAGR ~14-18%)
      - Key drivers: climate tech, biomanufacturing, food/agriculture,
        pharmaceuticals, materials science

    Target user segments:
      1. iGEM teams: 10,000+ participants/year across 400+ teams globally.
         Most lack computational design tools. Season runs March-October.
      2. Benchling users: 200,000+ researchers on the leading biotech R&D
         platform. ProtoForge fills the "ideation before Benchling" gap.
      3. Biohackers / community bio labs: ~100+ community labs worldwide
         (Genspace, BioCurious, etc.). Price-sensitive, value free tools.
      4. Climate founders: Early-stage startups working on bio-based
         solutions (plastic degradation, carbon capture, nitrogen fixation).
      5. University courses: Synthetic biology courses at 500+ universities.
         Professors need teaching tools for computational design.

    Competitive landscape:
      - Benchling ($6.1B valuation, 2021): Lab notebook + molecular bio
        tools. Enterprise-focused. No AI design-from-prompt feature.
      - Ginkgo Bioworks ($1.5B revenue target): Foundry model, not
        self-serve software. Recently acquired Zymergen.
      - Asimov (Google Ventures-backed): Genetic circuit CAD. Enterprise.
      - SnapGene / Geneious: Desktop sequence editors. No AI generation.
      - No direct competitor offers prompt-to-design with real sequences.

    SECTION 3: BUSINESS MODEL
    -------------------------------------------------------------------------
    Pricing (as of March 2026):
      - Free tier: 5 designs per month, full pipeline, no exports
      - Pro tier: $29/month — unlimited designs, FASTA export, API access,
        priority queue, saved design history
      - Enterprise (planned): Custom pricing, SSO, team workspaces,
        private gene registries, on-prem deployment
      - API tier (planned): Per-design pricing for integrations

    Unit economics (projected):
      - Cost per design: ~$0.15-0.40 (Claude API + NCBI + compute)
      - Free tier cost ceiling: 5 designs x $0.40 = $2.00/user/month
      - Pro margin: $29 - (est. 20 designs x $0.30) = ~$23/month margin
      - Target LTV/CAC ratio: 5:1+

    SECTION 4: CURRENT STATUS (March 2026)
    -------------------------------------------------------------------------
    Team: Solo founder (full-stack engineer + foresight strategist)
    Stage: Pre-launch MVP complete
    Tech stack: React 19 + FastAPI + SQLite + Claude API + BioPython +
                COBRApy + dna_features_viewer + NVIDIA Evo 2
    Launch plan: Product Hunt this week, then iGEM community outreach
    Funding: Bootstrapped (no external funding yet)

    Current traction:
      - Registered users: {t['registered_users']}
      - Monthly active users: {t['monthly_active_users']}
      - Designs generated: {t['designs_generated']}
      - Pro subscribers: {t['pro_subscribers']}
      - MRR: ${t['mrr_usd']}
      - Product Hunt upvotes: {t['product_hunt_upvotes']}
      - iGEM teams contacted: {t['igem_teams_contacted']}
      - Wait list signups: {t['wait_list']}
      - GitHub stars: {t['github_stars']}
      - Twitter/X followers: {t['twitter_followers']}
      - Notable: {t['notable_events']}

    SECTION 5: FORESIGHT ALIGNMENT
    -------------------------------------------------------------------------
    Global Trends 2040 (US NIC, 2021) scenario relevance:

    1. RENAISSANCE OF DEMOCRACIES
       - Open science policies favor open-source bio tools
       - Increased public R&D funding for climate biotech
       - iGEM and DIYbio communities thrive with government support
       - ProtoForge positioned as democratic access to synbio design
       - Probability estimate: 15-20%

    2. WORLD ADRIFT
       - Fragmented regulation creates compliance complexity
       - International collaboration on biosafety standards weakens
       - Users need jurisdiction-aware safety scoring
       - ProtoForge could add regulatory compliance layers
       - Probability estimate: 20-25%

    3. COMPETITIVE COEXISTENCE
       - US-China tech competition drives bioeconomy investment
       - Dual-use screening becomes critical differentiator
       - Government contracts possible for biosecurity tools
       - Export controls may limit some gene synthesis pathways
       - Probability estimate: 25-30%

    4. SEPARATE SILOS
       - Regional biotech ecosystems develop independently
       - Need for region-specific gene registries and regulations
       - Reduced global collaboration, more local solutions
       - ProtoForge may need regional instances
       - Probability estimate: 10-15%

    5. TRAGEDY AND MOBILIZATION
       - Climate crisis or pandemic drives massive biotech investment
       - Urgent demand for rapid organism design tools
       - Government fast-tracks bio-manufacturing capabilities
       - ProtoForge usage could spike for climate/health applications
       - Probability estimate: 15-20%

    Additional foresight frameworks:
      - Coates (1996) genetics revolution: democratization of genetic
        tools follows same trajectory as computing democratization
      - Mad Scientist Initiative: hybrid human-AI tools for biodefense
        align with ProtoForge's AI-assisted design approach
      - IARPA/IC foresight: prediction markets and swarm intelligence
        (this simulation) as tools for strategic planning

    SECTION 6: RISK FACTORS
    -------------------------------------------------------------------------
    Technical risks:
      - NCBI API rate limits could throttle free tier at scale
      - Claude API costs scale linearly with usage
      - Gene name ambiguity in NCBI search (partially mitigated)
      - FBA models limited to E. coli and P. putida currently

    Business risks:
      - Solo founder bus factor
      - Benchling or Ginkgo could build similar feature in 3-6 months
      - Free tier costs could exceed revenue at scale
      - Academic users rarely convert to paid tiers

    Regulatory risks:
      - AI-generated biological designs face emerging regulation
      - EU AI Act may classify synbio design tools as high-risk
      - US Executive Order on AI (2023) biosecurity provisions
      - Gene synthesis screening (IGSC) applies to downstream vendors
      - Dual-use research of concern (DURC) policies evolving

    Market risks:
      - Synbio market growth could slow if key applications underperform
      - Funding winter could reduce biotech startup formation
      - Public backlash against synthetic biology (GMO-adjacent fears)

    SECTION 7: EXIT / ACQUISITION SCENARIOS
    -------------------------------------------------------------------------
    Potential acquirers (if ProtoForge reaches significant traction):
      - Benchling: Fill their ideation/design gap ($5-20M acqui-hire range)
      - Ginkgo Bioworks: Software layer for their foundry ($10-50M)
      - Twist Bioscience: Upstream design tool for synthesis ($5-30M)
      - Thermo Fisher / Danaher: Extend digital biology portfolio ($20-80M)
      - Illumina: Complement sequencing with design tools ($10-50M)
      - Big Tech (Google DeepMind, Microsoft): AI-bio convergence ($50-150M)

    Valuation drivers:
      - User base and engagement metrics
      - Proprietary gene registry and validation layers
      - AI pipeline (prompt-to-design-to-synthesis)
      - Regulatory compliance features (dual-use screening)
      - Revenue and growth rate

    =========================================================================
    END OF SEED MATERIAL
    =========================================================================
    """)


# ── Prediction Prompt ────────────────────────────────────────────────

PREDICTION_PROMPT = textwrap.dedent("""\
Simulate ProtoForge's growth over the next 24 months (March 2026 - March 2028).

ProtoForge is an AI-powered bioengineering design platform that turns plain-English
prompts into real gene circuits, DNA sequences, plasmid maps, and safety scores.
It targets biohackers, iGEM teams, climate founders, and Benchling users. It is
currently a solo-founder MVP launching this week.

Use the attached seed file for full context on the product, market, pricing,
competition, and foresight alignment.

Run this simulation under all five Global Trends 2040 scenarios:
  1. Renaissance of Democracies
  2. World Adrift
  3. Competitive Coexistence
  4. Separate Silos
  5. Tragedy and Mobilization

For EACH scenario, predict:
  - Monthly user growth curve (Month 1-24)
  - Monthly revenue projection (free vs. Pro conversion rates)
  - Churn risks and retention drivers
  - Regulatory risks specific to that scenario
  - Probability of acquisition offer and likely valuation range ($5M-$150M)
  - Recommended strategic pivots
  - Key signposts that indicate this scenario is materializing

Also provide:
  - Probability weight for each scenario (must sum to 100%)
  - Cross-scenario consensus: what is true in ALL scenarios?
  - Biggest single risk across all scenarios
  - Highest-upside opportunity across all scenarios
  - One-sentence recommendation for the founder right now

Format the output as a structured report with clear section headers.
""")


# ── Report Template ──────────────────────────────────────────────────

REPORT_TEMPLATE_CONTENT = textwrap.dedent("""\
# ProtoForge Business Simulation Report
## MiroFish Swarm Prediction — {date}

**Simulation parameters:**
- Agent count: ___
- Simulation rounds: ___
- LLM backend: {llm_backend}
- Seed file: seed_protoforge.txt
- Run duration: ___ minutes

---

## Scenario Probability Weights

| Scenario | Probability | Confidence |
|----------|------------|------------|
| Renaissance of Democracies | __% | Low / Med / High |
| World Adrift | __% | Low / Med / High |
| Competitive Coexistence | __% | Low / Med / High |
| Separate Silos | __% | Low / Med / High |
| Tragedy and Mobilization | __% | Low / Med / High |

---

## Scenario 1: Renaissance of Democracies

**24-Month User Growth:**
- Month 1: ___
- Month 6: ___
- Month 12: ___
- Month 24: ___

**Revenue Projection:**
- Month 6 MRR: $___
- Month 12 MRR: $___
- Month 24 MRR: $___
- Free-to-Pro conversion rate: ___%

**Key Risks:**
1. ___
2. ___

**Acquisition Probability:** __% | Valuation Range: $___M - $___M

**Recommended Pivots:**
1. ___
2. ___

**Signposts to Watch:**
- ___

---

## Scenario 2: World Adrift

_(Same structure as above -- fill from MiroFish report)_

---

## Scenario 3: Competitive Coexistence

_(Same structure)_

---

## Scenario 4: Separate Silos

_(Same structure)_

---

## Scenario 5: Tragedy and Mobilization

_(Same structure)_

---

## Cross-Scenario Consensus

**True in ALL scenarios:**
1. ___
2. ___
3. ___

**Biggest single risk:** ___

**Highest-upside opportunity:** ___

---

## Exit Valuation Ranges

| Scenario | 12-Month | 24-Month | Likely Acquirer |
|----------|----------|----------|-----------------|
| Renaissance | $___M | $___M | ___ |
| World Adrift | $___M | $___M | ___ |
| Competitive | $___M | $___M | ___ |
| Separate Silos | $___M | $___M | ___ |
| Tragedy | $___M | $___M | ___ |

---

## Agent Interview Highlights

**Most bullish agent said:**
> "___"

**Most bearish agent said:**
> "___"

**Most surprising insight:**
> "___"

---

## Actionable Next Steps (This Week)

1. ___
2. ___
3. ___
4. ___
5. ___

---

## Founder's One-Sentence Directive

> ___

---

*Generated by MiroFish swarm simulation on {date}.*
*LLM backend: {llm_backend}*
*Simulation is qualitative foresight, not financial advice.*
*To rerun weekly: edit TRACTION_DATA in protoforge_mirofish_simulator.py,*
*then run: python protoforge_mirofish_simulator.py --update*
""")


# ── Utility Functions ────────────────────────────────────────────────

def run_cmd(cmd: list[str], cwd: str | None = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command with live output."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True,
    )
    if result.stdout.strip():
        for line in result.stdout.strip().split("\n")[-5:]:
            print(f"    {line}")
    if result.returncode != 0 and check:
        print(f"\n  ERROR (exit {result.returncode}):")
        for line in result.stderr.strip().split("\n")[-10:]:
            print(f"    {line}")
    return result


def check_prerequisites() -> list[str]:
    """Check that required tools are installed."""
    missing = []
    for tool in ["git", "docker"]:
        if not shutil.which(tool):
            missing.append(tool)

    # Check docker compose (v2 plugin style)
    result = subprocess.run(
        ["docker", "compose", "version"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        if not shutil.which("docker-compose"):
            missing.append("docker compose")

    return missing


def check_ollama_running() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags")
        resp = urllib.request.urlopen(req, timeout=3)
        return resp.status == 200
    except Exception:
        return False


def check_ollama_model(model: str) -> bool:
    """Check if a specific model is pulled in Ollama."""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:11434/api/tags")
        resp = urllib.request.urlopen(req, timeout=3)
        data = json.loads(resp.read().decode())
        model_base = model.split(":")[0]
        for m in data.get("models", []):
            if m.get("name", "").startswith(model_base):
                return True
        return False
    except Exception:
        return False


def prompt_for_key(name: str, description: str, url: str) -> str:
    """Interactively prompt user for an API key."""
    print(f"\n  {name}")
    print(f"  {description}")
    print(f"  Get one at: {url}")
    value = input(f"  Paste your {name} (or press Enter to skip): ").strip()
    return value


# ── Main Pipeline ────────────────────────────────────────────────────

def step_0_ollama_setup(config: dict):
    """Verify Ollama is running and the model is available."""
    model = config["model"]

    print("\n" + "=" * 70)
    print("STEP 0: Ollama Setup (FREE local LLM)")
    print("=" * 70)
    print(f"\n  Model: {model}")
    print(f"  Ollama URL (host):   http://localhost:11434")
    print(f"  Ollama URL (Docker): {OLLAMA_DOCKER_URL}")

    # Check if Ollama is installed
    if not shutil.which("ollama"):
        print("\n  Ollama is not installed.")
        print("  Install it from: https://ollama.com/download")
        print()
        print("  Quick install (Linux):")
        print("    $ curl -fsSL https://ollama.com/install.sh | sh")
        print()
        print("  Quick install (macOS):")
        print("    $ brew install ollama")
        print()
        print("  After installing, run:")
        print("    $ ollama serve")
        print(f"    $ ollama pull {model}")
        print(f"    $ python {Path(__file__).name} --ollama")
        print()
        proceed = input("  Continue anyway (Ollama may be running remotely)? (y/N): ").strip().lower()
        if proceed != "y":
            sys.exit(1)
        return

    # Check if Ollama is running
    if not check_ollama_running():
        print("\n  Ollama is installed but not running.")
        print("  Start it in another terminal:")
        print("    $ ollama serve")
        print()

        # Try to start it
        start = input("  Attempt to start Ollama now? (Y/n): ").strip().lower()
        if start != "n":
            print("  Starting Ollama in background...")
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Wait for it to come up
            for i in range(10):
                time.sleep(1)
                if check_ollama_running():
                    print("  Ollama is running.")
                    break
            else:
                print("  Could not confirm Ollama started. Continuing anyway...")
                print("  If it fails, run 'ollama serve' manually first.")
    else:
        print("\n  Ollama is running.")

    # Check if the model is pulled
    if check_ollama_running() and not check_ollama_model(model):
        print(f"\n  Model '{model}' not found locally.")
        pull = input(f"  Pull '{model}' now? This downloads 4-8 GB. (Y/n): ").strip().lower()
        if pull != "n":
            print(f"  Pulling {model}... (this may take several minutes)")
            result = run_cmd(["ollama", "pull", model], check=False)
            if result.returncode != 0:
                print(f"  Pull failed. Try manually: $ ollama pull {model}")
            else:
                print(f"  Model {model} ready.")
    elif check_ollama_running():
        print(f"  Model '{model}' is available.")


def step_1_clone_repo():
    """Clone MiroFish if not already present."""
    print("\n" + "=" * 70)
    print("STEP 1: Clone MiroFish Repository")
    print("=" * 70)

    if MIROFISH_DIR.exists() and (MIROFISH_DIR / "docker-compose.yml").exists():
        print(f"  MiroFish already cloned at {MIROFISH_DIR}")
        print("  Pulling latest changes...")
        run_cmd(["git", "pull"], cwd=str(MIROFISH_DIR), check=False)
        return

    if MIROFISH_DIR.exists():
        print(f"  Removing incomplete MiroFish directory...")
        shutil.rmtree(MIROFISH_DIR)

    print(f"  Cloning {MIROFISH_REPO}...")
    result = run_cmd(["git", "clone", MIROFISH_REPO, str(MIROFISH_DIR)])
    if result.returncode != 0:
        print("\n  FATAL: Could not clone MiroFish. Check your internet connection.")
        sys.exit(1)

    print("  Clone complete.")


def step_2_configure_env(config: dict):
    """Create .env file with API keys — Ollama or cloud."""
    is_ollama = config["mode"] == "ollama"
    model = config["model"]

    print("\n" + "=" * 70)
    print("STEP 2: Configure Environment")
    print("=" * 70)

    if is_ollama:
        print("  Mode: Ollama (local, free)")
        print(f"  Model: {model}")
    else:
        print("  Mode: Cloud LLM (OpenAI-compatible, paid)")

    env_file = MIROFISH_DIR / ".env"
    env_example = MIROFISH_DIR / ".env.example"

    # Read existing env
    existing_env = {}
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                existing_env[key.strip()] = value.strip()

    # Determine LLM settings
    if is_ollama:
        llm_key = "ollama"
        llm_base_url = OLLAMA_DOCKER_URL
        llm_model = model
    else:
        llm_key = existing_env.get("LLM_API_KEY", "")
        llm_base_url = existing_env.get("LLM_BASE_URL", "https://api.openai.com/v1")
        llm_model = existing_env.get("LLM_MODEL_NAME", "gpt-4o")

        has_llm = bool(llm_key and llm_key != "ollama")
        if not has_llm:
            llm_key = prompt_for_key(
                "LLM_API_KEY",
                "OpenAI-compatible API key (OpenAI, Alibaba Qwen, etc.)",
                "https://platform.openai.com/api-keys",
            )

    # Zep key (needed in both modes)
    zep_key = existing_env.get("ZEP_API_KEY", "")
    has_zep = bool(zep_key.strip())
    if not has_zep:
        zep_key = prompt_for_key(
            "ZEP_API_KEY",
            "Zep Cloud API key (free tier — needed for agent memory/knowledge graph)",
            "https://app.getzep.com/",
        )

    # Check if keys already match what we want
    if env_file.exists():
        existing_mode = "ollama" if existing_env.get("LLM_API_KEY") == "ollama" else "cloud"
        if existing_mode == config["mode"] and has_zep:
            print("  .env already configured for this mode.")
            reconfig = input("  Reconfigure? (y/N): ").strip().lower()
            if reconfig != "y":
                return

    # Build .env content
    if env_example.exists():
        env_content = env_example.read_text()
        lines = []
        for line in env_content.splitlines():
            stripped = line.strip()
            if stripped.startswith("LLM_API_KEY"):
                lines.append(f"LLM_API_KEY={llm_key}")
            elif stripped.startswith("LLM_BASE_URL"):
                lines.append(f"LLM_BASE_URL={llm_base_url}")
            elif stripped.startswith("LLM_MODEL_NAME"):
                lines.append(f"LLM_MODEL_NAME={llm_model}")
            elif stripped.startswith("ZEP_API_KEY") and zep_key:
                lines.append(f"ZEP_API_KEY={zep_key}")
            else:
                lines.append(line)
        env_content = "\n".join(lines) + "\n"
    else:
        if is_ollama:
            env_content = textwrap.dedent(f"""\
            # MiroFish Environment Configuration
            # Generated by protoforge_mirofish_simulator.py on {datetime.now().isoformat()}
            # Mode: OLLAMA (free, local LLM — no cloud API costs)

            # ── LLM Configuration (Ollama) ──
            # Ollama serves an OpenAI-compatible API on port 11434.
            # From inside Docker, the host is reachable at host.docker.internal.
            LLM_API_KEY=ollama
            LLM_BASE_URL={OLLAMA_DOCKER_URL}
            LLM_MODEL_NAME={model}

            # ── Cloud LLM (commented out — uncomment to switch from Ollama) ──
            # LLM_API_KEY=sk-your-openai-key-here
            # LLM_BASE_URL=https://api.openai.com/v1
            # LLM_MODEL_NAME=gpt-4o

            # Optional: secondary "boost" LLM for acceleration
            # LLM_BOOST_API_KEY=
            # LLM_BOOST_BASE_URL=
            # LLM_BOOST_MODEL_NAME=

            # ── Zep Cloud (Agent Memory) ──
            # Required for knowledge graph and agent memory
            # Free tier: https://app.getzep.com/
            ZEP_API_KEY={zep_key}

            # ── Server Config ──
            FLASK_ENV=production
            """)
        else:
            env_content = textwrap.dedent(f"""\
            # MiroFish Environment Configuration
            # Generated by protoforge_mirofish_simulator.py on {datetime.now().isoformat()}
            # Mode: CLOUD (OpenAI-compatible API)

            # ── LLM Configuration (Cloud) ──
            LLM_API_KEY={llm_key}
            LLM_BASE_URL={llm_base_url}
            LLM_MODEL_NAME={llm_model}

            # ── Ollama (commented out — use --ollama flag to switch) ──
            # LLM_API_KEY=ollama
            # LLM_BASE_URL={OLLAMA_DOCKER_URL}
            # LLM_MODEL_NAME={DEFAULT_OLLAMA_MODEL}

            # Optional: secondary "boost" LLM for acceleration
            # LLM_BOOST_API_KEY=
            # LLM_BOOST_BASE_URL=
            # LLM_BOOST_MODEL_NAME=

            # ── Zep Cloud (Agent Memory) ──
            # Required for knowledge graph and agent memory
            # Free tier: https://app.getzep.com/
            ZEP_API_KEY={zep_key}

            # ── Server Config ──
            FLASK_ENV=production
            """)

    env_file.write_text(env_content)
    print(f"\n  .env written to {env_file}")

    if not zep_key:
        print("\n  WARNING: ZEP_API_KEY is missing.")
        print("  Get a free key at: https://app.getzep.com/")
        print(f"  Then edit: {env_file}")


def step_3_generate_seed():
    """Generate the ProtoForge seed file."""
    print("\n" + "=" * 70)
    print("STEP 3: Generate ProtoForge Seed File")
    print("=" * 70)

    SEED_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = build_seed_content()
    SEED_FILE.write_text(content)
    print(f"  Seed file written to {SEED_FILE}")
    print(f"  Size: {len(content):,} characters")
    print(f"  Traction date: {TRACTION_DATA['date']}")


def step_4_start_docker(config: dict):
    """Start MiroFish via Docker Compose."""
    is_ollama = config["mode"] == "ollama"

    print("\n" + "=" * 70)
    print("STEP 4: Start MiroFish (Docker)")
    print("=" * 70)

    if is_ollama:
        print("  LLM backend: Ollama (local)")
        print(f"  Make sure 'ollama serve' is running in another terminal.")
        print()

    # Check if already running
    result = subprocess.run(
        ["docker", "compose", "ps", "--format", "json"],
        cwd=str(MIROFISH_DIR), capture_output=True, text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        print("  MiroFish containers detected. Restarting...")
        run_cmd(["docker", "compose", "down"], cwd=str(MIROFISH_DIR), check=False)

    print("  Starting MiroFish containers...")
    print("  (This may take several minutes on first run — downloading images)")
    print()

    result = run_cmd(
        ["docker", "compose", "up", "-d"],
        cwd=str(MIROFISH_DIR),
        check=False,
    )

    if result.returncode != 0:
        print("\n  Docker Compose failed. Common fixes:")
        print("    1. Is Docker running?  $ docker info")
        print("    2. Port conflict?      $ lsof -i :3000 -i :5001")
        print("    3. Try manually:       $ cd mirofish && docker compose up -d")
        if is_ollama:
            print("    4. Is Ollama running?  $ ollama serve")
            print("    5. Ollama networking:  Make sure host.docker.internal resolves")
            print("       On Linux, you may need: --add-host=host.docker.internal:host-gateway")
            print("       in docker-compose.yml under the backend service.")
        print("\n  You can also run MiroFish without Docker:")
        print("    $ cd mirofish && cp .env.example .env  # edit keys")
        print("    $ npm run setup:all")
        print("    $ npm run dev")
        return False

    print("\n  Waiting for services to become healthy...")
    for attempt in range(30):
        try:
            import urllib.request
            req = urllib.request.Request(MIROFISH_UI_URL)
            urllib.request.urlopen(req, timeout=3)
            print(f"  MiroFish UI is live at {MIROFISH_UI_URL}")
            return True
        except Exception:
            time.sleep(2)
            if attempt % 5 == 4:
                print(f"    Still waiting... ({attempt + 1}/30)")

    print(f"\n  MiroFish may still be starting up.")
    print(f"  Check manually: {MIROFISH_UI_URL}")
    print(f"  View logs: $ cd mirofish && docker compose logs -f")
    return True


def step_5_save_prompt_and_open():
    """Save the prediction prompt and open the web UI."""
    print("\n" + "=" * 70)
    print("STEP 5: Prediction Prompt + Web UI")
    print("=" * 70)

    PROMPT_FILE.write_text(PREDICTION_PROMPT)
    print(f"  Prediction prompt saved to {PROMPT_FILE}")

    print("\n" + "-" * 70)
    print("PASTE THIS PROMPT INTO THE MIROFISH WEB UI:")
    print("-" * 70)
    print(PREDICTION_PROMPT)
    print("-" * 70)

    print(f"\n  Seed file to upload: {SEED_FILE}")
    print(f"  Prompt file (backup): {PROMPT_FILE}")

    print(f"\n  Opening {MIROFISH_UI_URL} in your browser...")
    try:
        webbrowser.open(MIROFISH_UI_URL)
    except Exception:
        print(f"  Could not open browser. Navigate to: {MIROFISH_UI_URL}")


def step_6_save_report_template(config: dict):
    """Save the report template."""
    print("\n" + "=" * 70)
    print("STEP 6: Report Template")
    print("=" * 70)

    if config["mode"] == "ollama":
        llm_backend = f"Ollama ({config['model']}) -- local, free"
    else:
        llm_backend = "Cloud LLM (OpenAI-compatible)"

    content = REPORT_TEMPLATE_CONTENT.replace(
        "{date}", datetime.now().strftime("%Y-%m-%d")
    ).replace(
        "{llm_backend}", llm_backend
    )
    REPORT_TEMPLATE.write_text(content)
    print(f"  Report template saved to {REPORT_TEMPLATE}")
    print("  Fill this in with MiroFish results after simulation completes.")


def step_7_api_example(config: dict):
    """Print optional API automation example."""
    print("\n" + "=" * 70)
    print("STEP 7: API Automation (Optional / Experimental)")
    print("=" * 70)

    print(textwrap.dedent(f"""\
    MiroFish is primarily a web UI application. However, its Flask backend
    exposes REST endpoints that may allow programmatic access. This is
    experimental -- the API is not officially documented and may change.

    Example (Python requests -- run AFTER MiroFish is started):

    ```python
    import requests

    MIROFISH_API = "{MIROFISH_API_URL}"

    # Check if the API is accessible
    try:
        r = requests.get(f"{{MIROFISH_API}}/", timeout=5)
        print(f"API status: {{r.status_code}}")
    except requests.ConnectionError:
        print("MiroFish API not accessible. Is Docker running?")

    # Known endpoints (inspect mirofish/backend/app/api/ for full list):
    #   GET  /api/graph          -- Knowledge graph operations
    #   POST /api/simulation     -- Simulation control
    #   GET  /api/report         -- Report generation
    #
    # Upload seed material (may require multipart form):
    # r = requests.post(
    #     f"{{MIROFISH_API}}/api/graph/upload",
    #     files={{"file": open("mirofish/seed_protoforge.txt", "rb")}},
    # )
    #
    # The exact endpoints depend on MiroFish version.
    # Check: $ cd mirofish && grep -r "@app.route" backend/
    ```

    For fully automated weekly reruns, the recommended workflow is:
      1. Update TRACTION_DATA in this script with current numbers
      2. Run: $ python {Path(__file__).name} --update
      3. Upload the new seed file in the MiroFish UI
      4. Re-paste the prediction prompt and run
    """))


def print_final_summary(config: dict):
    """Print the final summary with all file locations."""
    is_ollama = config["mode"] == "ollama"
    model = config["model"]

    print("\n" + "=" * 70)
    print("SETUP COMPLETE")
    print("=" * 70)

    if is_ollama:
        print(f"""
  +----------------------------------------------------------+
  |  RUNNING IN FREE OLLAMA MODE -- ZERO COST, FULLY LOCAL   |
  |  Model: {model:<49s}|
  |  No cloud LLM charges. Only Zep free tier needed.        |
  +----------------------------------------------------------+
        """)
    else:
        print(f"""
  +----------------------------------------------------------+
  |  RUNNING IN CLOUD MODE                                   |
  |  API calls will incur costs from your LLM provider.      |
  +----------------------------------------------------------+
        """)

    print(f"""  Files created:
    Seed file:         {SEED_FILE}
    Prediction prompt: {PROMPT_FILE}
    Report template:   {REPORT_TEMPLATE}
    MiroFish config:   {MIROFISH_DIR / '.env'}

  MiroFish UI:       {MIROFISH_UI_URL}

  What to do now:
    1. Open {MIROFISH_UI_URL}
    2. Create a new prediction
    3. Upload {SEED_FILE}
    4. Paste the prediction prompt from {PROMPT_FILE}
    5. Set agents: 100-500 (start small to test)
    6. Set rounds: 5-10
    7. Run and wait (30-60+ minutes for large simulations)
    8. Export report and fill in {REPORT_TEMPLATE}""")

    if is_ollama:
        print(f"""
  Ollama tips:
    - Keep 'ollama serve' running in another terminal
    - Larger models = better quality but slower:
        $ ollama pull llama3.1:70b    (needs 40+ GB RAM)
        $ ollama pull qwen2:7b        (good alternative to llama3.1:8b)
    - Monitor GPU usage: $ nvidia-smi (if using GPU)
    - Ollama uses ~4-8 GB RAM for 8B models

  Cost estimate: $0 (all local)""")
    else:
        print("""
  Cost estimate:
    100 agents x 5 rounds  = $2-5 in API calls
    500 agents x 10 rounds = $10-25 in API calls
    1000 agents x 20 rounds = $30-80 in API calls""")

    print(f"""
  To rerun weekly:
    1. Edit TRACTION_DATA in {Path(__file__).name}
    2. Run: $ python {Path(__file__).name} --update

  To switch modes:
    Ollama:  $ python {Path(__file__).name} --ollama
    Cloud:   $ python {Path(__file__).name} --cloud

  To stop MiroFish:
    $ cd mirofish && docker compose down
    """)


# ── Entry Point ──────────────────────────────────────────────────────

def main():
    config = parse_args()

    is_ollama = config["mode"] == "ollama"
    model = config["model"]

    if is_ollama:
        print("""
    +==================================================================+
    |  ProtoForge x MiroFish Business Swarm Simulator                  |
    |  Multi-agent foresight simulation for biotech business model     |
    |                                                                  |
    |  RUNNING IN FREE OLLAMA MODE -- ZERO COST, FULLY LOCAL           |
    +==================================================================+
        """)
    else:
        print("""
    +==================================================================+
    |  ProtoForge x MiroFish Business Swarm Simulator                  |
    |  Multi-agent foresight simulation for biotech business model     |
    |                                                                  |
    |  RUNNING IN CLOUD MODE (OpenAI-compatible API)                   |
    +==================================================================+
        """)

    # Handle --update flag (regenerate seed + prompt only)
    if config["update_only"]:
        print("  UPDATE MODE: Regenerating seed file and prompt only.\n")
        step_3_generate_seed()
        PROMPT_FILE.write_text(PREDICTION_PROMPT)
        print(f"\n  Updated seed file: {SEED_FILE}")
        print(f"  Upload the new seed file in MiroFish UI and re-run.")
        print(f"  (Make sure you edited TRACTION_DATA in this script first.)")
        return

    # Check prerequisites
    missing = check_prerequisites()
    if missing:
        print(f"  Missing prerequisites: {', '.join(missing)}")
        print()
        print("  Install them:")
        if "git" in missing:
            print("    Git:    https://git-scm.com/downloads")
        if "docker" in missing or "docker compose" in missing:
            print("    Docker: https://docs.docker.com/get-docker/")
        if is_ollama:
            print("    Ollama: https://ollama.com/download")
        print()

        proceed = input("  Continue without Docker (generate files only)? (y/N): ").strip().lower()
        if proceed != "y":
            sys.exit(1)
        step_3_generate_seed()
        step_6_save_report_template(config)
        PROMPT_FILE.write_text(PREDICTION_PROMPT)
        print(f"\n  Files generated. Set up Docker and MiroFish manually:")
        print(f"    $ git clone {MIROFISH_REPO} mirofish")
        print(f"    $ cd mirofish && cp .env.example .env  # add your keys")
        if is_ollama:
            print(f"    $ ollama serve                         # start Ollama")
            print(f"    $ ollama pull {model}              # pull model")
        print(f"    $ docker compose up -d")
        print(f"    $ open {MIROFISH_UI_URL}")
        return

    # Full pipeline
    if is_ollama:
        step_0_ollama_setup(config)
    step_1_clone_repo()
    step_2_configure_env(config)
    step_3_generate_seed()
    step_4_start_docker(config)
    step_5_save_prompt_and_open()
    step_6_save_report_template(config)
    step_7_api_example(config)
    print_final_summary(config)


if __name__ == "__main__":
    main()
