# Progenx: Paper St Marketing Kernel Audit
## Governing Meaning Applied to a Biotech SaaS
### March 17, 2026

---

## Kernel 1: TRUTH LOCK (SSOT)

### Single Source of Truth Sentence

**Progenx helps scientists, biohackers, iGEM teams, and climate founders design real gene circuits, DNA sequences, and metabolic simulations in plain English, in under a minute, without a PhD, wet lab, or enterprise budget.**

### SSOT Components

| Component | Locked Value |
|-----------|-------------|
| **Buyer** | Scientists, biohackers, iGEM teams (10k+/year), climate founders, university labs |
| **Loss** | Without Progenx: weeks of manual NCBI searches, hand-drawn circuit sketches, guesswork assembly plans, or $50K+/year enterprise tools (Benchling, Ginkgo, Asimov) |
| **Mechanism** | Plain English prompt > AI designs gene circuit > NCBI fetches real sequences > codon optimization > COBRApy FBA simulation > assembly planning with primers > plasmid map > safety scoring. 6 automated stages. |
| **Outcome** | Complete, verifiable bioengineering design in under 60 seconds. Real NCBI accessions, not AI-generated biology. |
| **Constraints** | Computational predictions only (not lab-validated). 3 supported chassis (E. coli, P. putida, S. elongatus). 26 verified genes in curated registry. Designs are educational/experimental, not lab-ready without expert review. |

### Gate 1 Status: LOCKED

Any copy, feature description, or marketing claim that changes the Buyer, Loss, Mechanism, Outcome, or Constraints above is invalid and triggers a rewind.

---

## Kernel 2: CLAIMS INVENTORY + PROOF LEDGER

### Approved Claims (evidence exists, verifiable)

| Claim | Evidence | Strength | Location |
|-------|----------|----------|----------|
| "26 verified gene accessions" | `len(GENE_REGISTRY)` in ncbi_client.py | Strong (code) | Landing stats |
| "Real NCBI sequences" | NCBI Entrez API calls in ncbi_client.py | Strong (live API) | Hero copy |
| "3 chassis with genome-scale models" | `SUPPORTED_CHASSIS` in fba_engine.py | Strong (code) | Landing stats |
| "56 regression tests passing" | `python tests/test_accuracy.py` | Strong (runnable) | Landing stats |
| "6 pipeline stages" | Steps in llm_orchestrator.py | Strong (code) | Landing stats |
| "$0 free tier" | Ollama local, no API cost | Strong (architecture) | Pricing |
| "Under 60 seconds" | Typical Ollama response time | Medium (varies by hardware) | Hero copy |
| "$0.01/design Pro tier" | Token math from Claude pricing | Medium (estimate) | Internal |
| "97% gross margin" | $29 - $0.01/design x 100 | Medium (projection) | Internal |
| "5 designs/month free" | `FREE_TIER_MONTHLY_DESIGNS = 5` in config.py | Strong (code) | Pricing |
| "Primer design with Tm calculation" | SantaLucia model in primer_designer.py | Strong (code) | Assembly output |
| "GenBank export" | genbank_exporter.py | Strong (code) | Export bar |
| "Safety scoring with dual-use screening" | safety_scorer.py | Strong (code) | Every design |

### Conditional Claims (true with caveats)

| Claim | Condition | Required Caveat |
|-------|-----------|-----------------|
| "Design in plain English" | Works for well-characterized pathways | Free tier constrained to 26 registry genes and 3 chassis |
| "Metabolic simulation" | Only for E. coli and P. putida | "FBA predictions are theoretical upper bounds. Actual yields depend on wet-lab conditions." |
| "ESM-2 variant predictions" | Pro tier only, requires PyTorch | "Computational predictions (Spearman rho ~0.4-0.5 with experimental data)" |
| "SecureDNA screening" | Not yet deployed | DO NOT CLAIM until synthclient is running |
| "No hallucinated biology" | Registry genes are verified; NCBI search results may not match intended function | "Designs using genes outside our verified registry are labeled as conceptual" |

### NOT ALLOWED Claims (no evidence, or misleading)

| Claim | Why Not Allowed |
|-------|-----------------|
| "Lab-ready designs" | Computational predictions only. Explicitly prohibited. |
| "X users signed up" | Must be live from database, even if 0 |
| "X designs generated" | Must be live from database, even if 0 |
| "First consumer Evo 2 interface" | Evo 2 is not fully integrated into the pipeline yet |
| "400+ threats screened" | SecureDNA not deployed yet |
| Any specific acquisition valuation | Speculative, from Grok analysis, not verified |
| "Endorsed by iGEM" | No formal partnership exists |
| "Used by X universities" | No users yet |

---

## Kernel 3: RISK MODEL

### Downstream Misread Risks

| Line | Risk | Mitigation |
|------|------|------------|
| "Design Microbes in Plain English" | User thinks output is lab-ready | Disclaimer banner on every design. "Computational predictions. Lab validation required." |
| "Real NCBI sequences" | User thinks sequences are experimentally validated for their specific application | Confidence badges (high/medium/low). Function override when LLM misuses a gene. |
| "Metabolic simulation" | User takes FBA yield numbers as guaranteed | "UPPER BOUND" label. Limitations section. "Actual yields are typically 10-50% of theoretical." |
| "Safety Score: 100%" | User thinks design is safe to release | Score measures known patterns only. "Standard biosafety practices apply." Not a regulatory clearance. |
| "Free" | User thinks there are no limitations | "3 supported chassis. 26 verified genes. 5 designs/month." Clearly stated. |

### Overclaim Risks

| Area | Risk | Status |
|------|------|--------|
| Evo 2 integration | Code exists but not wired into pipeline | Removed from feature claims. Listed in CLAUDE.md as "not yet implemented." |
| SecureDNA | Integration code exists but synthclient not running | Removed "400+ threats" from landing page stats. |
| Acquisition valuations | $5M-$150M range from Grok analysis | Labeled as "speculative, from Grok strategic analysis" in seed file. Not on public site. |
| User growth projections | "1,000-3,000 in month 1-3" | Labeled as "founder estimates, not validated" in seed file. Not on public site. |

---

## Kernel 4: MESSAGE ARCHITECTURE

### Decision Path (homepage)

1. **Attention** (hero): "Design Microbes in Plain English" + glowing DNA helix
2. **Problem** (sub-hero): "Stop spending weeks on NCBI searches, manual circuit sketches, and guesswork assembly plans"
3. **Mechanism** (How It Works): 3 steps. Describe > AI + Real Biology > Download & Build
4. **Proof** (Pipeline): 6 verified stages with descriptions
5. **Demo** (Video placeholder): "See It in Action" section
6. **Social proof** (Stats): Live counters (real, even if 0) + verified code metrics
7. **CTA** (bottom): "The bioeconomy needs better tools. Start Designing Free."
8. **Contact**: Direct email + form

### Objection Map

| Objection | Where Addressed |
|-----------|-----------------|
| "Is the biology real?" | "Real NCBI sequences" + confidence badges + registry verification |
| "Is it accurate?" | 56 regression tests + function validation + self-consistency checking |
| "Is it safe?" | Safety scoring on every design + disclaimer on every output |
| "What if it's wrong?" | Conceptual-only banners + FBA limitations section + "lab validation required" |
| "How much does it cost?" | Pricing page with clear tiers. Free tier is genuinely $0. |
| "Is it a toy?" | Assembly plans with real primers + GenBank export + 8 export formats |
| "Who uses this?" | "Built for" bar: iGEM Teams, Climate Founders, Biohackers, University Labs |

---

## Kernel 5: PERSUASION PLUGINS (Applied)

### Plugin A: STORY (StoryBrand-style)
- **One-liner**: "Progenx turns plain English into real gene circuits, so scientists and biohackers can design custom microbes without a PhD or million-dollar budget."
- **Hero**: The scientist/student/founder (not Progenx)
- **Problem**: Manual NCBI searches, guesswork assembly, enterprise tool pricing
- **Guide**: Progenx (the tool)
- **Plan**: Describe > AI designs > Download & build
- **Call to action**: "Start Designing Free"
- **Success**: Complete design in under a minute
- **Failure**: Weeks of manual work, or paying $50K+/year

### Plugin B: INFLUENCE (Cialdini)
- **Authority**: "Real NCBI sequences" + "COBRApy genome-scale models" + "SantaLucia Tm calculation" (named, published methods)
- **Social proof**: Live stats (honest, even if 0). "Built for iGEM Teams" (10,000+ participants/year is a real, verifiable number)
- **Scarcity**: 5 free designs/month (real constraint, not manufactured)
- **Commitment**: Free tier gets users invested before upgrade decision

### Plugin C: ACTION (Fogg)
- **Motivation**: "Stop spending weeks on manual work"
- **Ability**: Plain English input, no jargon needed, free
- **Prompt**: CTA buttons above fold + bottom CTA

### Plugin D: BEHAVIORAL FRAMING
- **Loss framing**: "Stop spending weeks on NCBI searches, manual circuit sketches, and guesswork assembly plans"
- **Contrast**: Free tier vs $50K+/year enterprise tools (Benchling, Ginkgo, Asimov)
- **Reference point**: "Under a minute" (vs weeks)

### Gate 5 (Drift Check): PRESERVED
No plugin introduced a new outcome, mechanism, or claim not in the SSOT.

---

## Kernel 6: CHANNEL BLOCKS

### Homepage Modules (Built)
- Hero with DNA helix background + particles
- "Built for" audience bar
- 3-step "How It Works"
- "See It in Action" video placeholder
- 6-feature pipeline grid
- Example prompts (clickable)
- Live stats (real from DB)
- Final CTA
- Contact section
- Dark footer with legal links

### Export Formats (Built)
- FASTA, GenBank, Plasmid SVG, Primers CSV, Assembly Plan (MD), Full Report (MD), JSON, Copy DNA

### Pages (Built)
- Landing (/), Studio (/studio), History (/history), Pricing (/pricing)

### Pages Needed
- Terms of Service (/terms)
- Privacy Policy (/privacy)
- About (/about)
- Documentation/Learn (/learn)

---

## Kernel 7: SYSTEMS + INSTRUMENTATION

### Capture > Route > Follow-up > Measurement

| Step | Status |
|------|--------|
| **Capture** | Signup (email/password), contact form (mailto) |
| **Route** | JWT auth, tier-based routing (free/pro/admin) |
| **Follow-up** | Not implemented (no email system, no Mailchimp/Resend) |
| **Measurement** | /api/stats (user count, design count). No analytics (GA, Plausible, etc.) |

### Missing
- Email capture on landing page (for non-signup visitors)
- Analytics (need Plausible or similar, privacy-respecting)
- Email follow-up sequences (Resend or similar)
- CRM/pipeline tracking

---

## Kernel 8: OPERATING LOOP

### Proof Captured So Far
- 5 real designs generated (LithioSorb, InflammaGuard, OceanClean, ClearSkin x2)
- 5-test accuracy audit: 3 A's, 2 B's (documented)
- 56 regression tests passing
- 14-point system consistency check passing
- CISO security audit: 0 critical, 0 high issues
- Competitive intel: Cradle, Asimov, TeselaGen reverse-engineered
- Legal/privacy report: 580 lines

### Claims to Update When Available
- User count (live from DB, currently 0)
- Design count (live from DB, currently 0)
- Customer testimonials (none yet)
- Lab validation results (none yet)
- iGEM team usage (none yet)

---

## Anti-Goals Enforcement Log

| Date | Trigger | Action Taken |
|------|---------|-------------|
| Mar 15 | Fake live ticker ("147 designs today") | HALT. Replaced with real DB stats (0). |
| Mar 15 | "400+ threats screened via SecureDNA" | HALT. Removed. SecureDNA not deployed. |
| Mar 16 | "All organism types" on free tier | HALT. Changed to "3 supported chassis." Free tier is constrained. |
| Mar 16 | Em dashes throughout copy | SIMPLIFY. Removed all em dashes (AI writing tell). |
| Mar 16 | UI sounds (click, welcome tone) | HALT. Removed. "Goofy and unprofessional." |
| Mar 16 | Admin API endpoint with secret | HALT. Removed endpoint. Replaced with CLI-only script (no attack surface). |
| Mar 17 | Auth modal closes on backdrop click | HALT. Changed to X button only (prevents data loss). |

---

## Summary

Progenx passes all 8 Paper St kernels with the following status:

| Kernel | Status |
|--------|--------|
| K1 Truth Lock | LOCKED |
| K2 Claims Inventory | 13 approved, 5 conditional, 7 denied |
| K3 Risk Model | All high-risk claims have boundaries |
| K4 Message Architecture | Canonical structure approved |
| K5 Persuasion Plugins | Applied, no drift |
| K6 Channel Blocks | Homepage + Studio + History + Pricing built |
| K7 Systems | Partially connected (no email, no analytics) |
| K8 Operating Loop | Proof being captured, claims updated as earned |

**Every number on the site is either live from the database or verifiable in the source code. No manufactured certainty. No aspirational metrics.**

---

*Generated by applying Paper St OS kernels to Progenx. This document should be updated as new proof is earned and claims are verified.*
