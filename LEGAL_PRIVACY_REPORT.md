# ProtoForge Legal & Privacy Report

**Prepared:** March 14, 2026
**Platform:** ProtoForge -- AI-Powered Bioengineering Design Platform
**Stage:** Pre-launch (March 2026)
**Business Model:** Freemium SaaS ($29/mo Pro tier), solo founder

> **Caveat:** This report is a research document, not legal advice. It identifies issues, maps the regulatory landscape, and makes recommendations. Several sections explicitly call out where a qualified attorney should be consulted. The author is not a lawyer.

---

## Table of Contents

1. [Privacy Policy Requirements](#1-privacy-policy-requirements)
2. [Terms of Service](#2-terms-of-service)
3. [GDPR Compliance](#3-gdpr-compliance)
4. [EU AI Act Implications](#4-eu-ai-act-implications)
5. [Biosecurity / Dual-Use Legal Exposure](#5-biosecurity--dual-use-legal-exposure)
6. [IGSC Gene Synthesis Screening](#6-igsc-gene-synthesis-screening)
7. [Open Source License Audit](#7-open-source-license-audit)
8. [Recommendations & Launch Checklist](#8-recommendations--launch-checklist)
9. [Sources](#9-sources)

---

## 1. Privacy Policy Requirements

### 1.1 Data ProtoForge Collects

Based on the codebase (SQLAlchemy models, auth system, design pipeline), ProtoForge collects and processes the following categories of personal and user-generated data:

| Data Category | Source | Storage | Sensitivity |
|---|---|---|---|
| **Account data** | Signup form | SQLite (User table) | Email, hashed password, name |
| **Design prompts** | User input (plain English descriptions) | SQLite (Design table) | May reveal research intent, IP |
| **Generated designs** | Pipeline output | SQLite (Design table) | Gene circuits, DNA sequences, assembly plans |
| **Chat/refinement history** | Refine endpoint | SQLite (ChatMessage table) | Iterative design conversations |
| **Audit logs** | Every generate/refine action | SQLite (AuditLog table) | User ID, action, safety flags |
| **Safety scores** | safety_scorer.py output | Stored with design | Dual-use flags, risk assessments |
| **Usage metadata** | Rate limiting (5 free/month) | Derived from design count | Usage patterns |

### 1.2 Third-Party Data Processing Disclosures

**Anthropic Claude API:**
- Every design request sends the user's plain-English prompt to Anthropic's Claude API (claude-sonnet-4).
- Under Anthropic's current API terms (as of September 2025): API data is **never used for model training**, and API logs are stored for **only 7 days** before automatic deletion.
- Anthropic offers a Data Processing Agreement (DPA) with Standard Contractual Clauses (SCCs) that is automatically incorporated into their Commercial Terms of Service.
- **Required disclosure:** The privacy policy must explicitly state that user prompts are sent to Anthropic for processing, specify the purpose (gene circuit design), note Anthropic's retention period, and link to Anthropic's privacy policy.

**NCBI Entrez API:**
- ProtoForge queries NCBI's public databases to fetch real gene sequences.
- NCBI is a US government public database. Queries contain gene names and accession numbers, not personal data.
- **Privacy concern level: Low.** The queries themselves do not contain personal information. However, NCBI's usage policy requires an email address (configured as `protoforge@paperst.co` in the .env), which is the platform's operational email, not user data.
- **Recommended disclosure:** Mention that the platform queries public biological databases (NCBI/GenBank) to retrieve gene sequence data, and that no user personal information is transmitted to these databases.

**No other third-party processors identified** in the current codebase (no analytics, no payment processor yet, no error tracking service).

### 1.3 Applicable Privacy Laws

**Definite applicability:**

- **GDPR (EU/EEA):** ProtoForge targets iGEM teams (66+ countries). EU users are virtually guaranteed. GDPR applies to any entity processing data of EU residents, regardless of where the company is based. No revenue or size threshold.
- **CCPA/CPRA (California):** Applies if ProtoForge has California users AND meets revenue thresholds ($25M annual revenue, 100,000+ consumers, or 50%+ revenue from selling personal data). At launch, ProtoForge likely falls below these thresholds. However, best practice is to comply proactively because (a) thresholds can be crossed quickly, and (b) a CCPA-compliant policy also satisfies most other state laws.

**Likely applicable (depending on user geography):**

- **Virginia CDPA, Colorado CPA, Connecticut CTDPA, Texas TDPSA, Oregon OCPA** and 10+ other US state privacy laws enacted 2023-2025. Many have lower thresholds than CCPA.
- **UK GDPR** (post-Brexit equivalent): Same obligations as EU GDPR for UK users.
- **PIPEDA (Canada):** Applies if Canadian users are present.
- **LGPD (Brazil):** Similar to GDPR, applies to processing data of Brazilian residents.

**Practical recommendation:** Draft a single global privacy policy that meets GDPR standards (the strictest), which will satisfy nearly all other frameworks. This is standard industry practice for SaaS startups.

### 1.4 Privacy Policy Must Include

At minimum, the privacy policy needs to cover:

1. Identity and contact details of the data controller (ProtoForge / founder)
2. Categories of personal data collected (account data, design data, usage data)
3. Purposes and legal basis for processing (contract performance, legitimate interest)
4. Third-party data processors (Anthropic Claude API -- with specifics about prompt transmission)
5. Data retention periods (how long designs, accounts, and audit logs are kept)
6. International data transfers (data sent to Anthropic's US servers if serving EU users)
7. User rights (access, rectification, deletion, portability, objection)
8. Cookie usage (if any -- current codebase uses JWT tokens, not cookies, but the frontend may set cookies)
9. Contact information for privacy requests
10. Right to lodge a complaint with a supervisory authority (GDPR requirement)

---

## 2. Terms of Service

### 2.1 Liability for Generated Designs

This is the single most critical legal document for ProtoForge. The platform generates gene circuits, DNA sequences, and assembly plans that a user could theoretically attempt to build in a lab. The ToS must create a clear legal barrier between the platform's computational output and any downstream physical implementation.

**Required provisions:**

- **"Not Lab-Ready" Disclaimer:** The existing disclaimer in `config.py` and `safety_scorer.py` ("EDUCATIONAL/EXPERIMENTAL ONLY -- NOT LAB-READY WITHOUT EXPERT REVIEW") is a good start, but it needs to be elevated to the ToS as a binding contractual term, not just a UI notification.
- **No Warranty on Biological Accuracy:** Explicitly disclaim that generated sequences, predicted yields, FBA results, codon optimization outputs, and assembly plans are computational predictions only. No representation that they will function as described in vivo.
- **No Professional Advice:** State that ProtoForge does not provide professional biological engineering, biosafety, or regulatory advice. Outputs should not be treated as substitutes for expert consultation.
- **Limitation of Liability:** Cap liability at the amount paid by the user (e.g., $29/month for Pro users, $0 for free-tier). Disclaim consequential, incidental, and indirect damages.
- **Indemnification:** Users agree to indemnify ProtoForge against claims arising from their use of generated designs.

### 2.2 User Responsibility for Downstream Use

The ToS must make clear:

- Users are solely responsible for any laboratory implementation of designs.
- Users must comply with all applicable biosafety regulations (NIH Guidelines, institutional biosafety committees, local/national laws) before synthesizing, cloning, or expressing any generated construct.
- Users must obtain all necessary institutional approvals (IBC review, IRB if applicable, export controls) before acting on any design output.
- ProtoForge bears no responsibility for designs that are modified by the user after generation.

### 2.3 IP Ownership of Generated Designs

This is a legally unsettled area. Key considerations:

- **US Copyright Office position (current as of 2025):** Purely AI-generated works without sufficient human authorship are not copyrightable. However, if a user provides detailed, creative prompts and makes substantial editorial choices, the resulting work may have copyrightable elements attributable to the human author.
- **Anthropic's API terms:** Anthropic assigns output ownership to the API customer (ProtoForge), and ProtoForge can then assign those rights to users.
- **Recommended ToS approach:**
  - Grant users ownership of their generated designs (this is the market standard -- OpenAI, Anthropic, and most AI platforms do this).
  - Disclaim any guarantee that designs are copyrightable or patentable.
  - Reserve a limited license for ProtoForge to use anonymized/aggregated design data for service improvement (with appropriate privacy safeguards).
  - Clarify that gene sequences retrieved from NCBI are public domain data and cannot be claimed as proprietary by any user.

### 2.4 Acceptable Use Policy (AUP)

This is especially important for a bioengineering platform. The AUP must prohibit:

- Designing organisms intended as biological weapons or bioterrorism agents
- Designing select agents or toxins listed on the HHS/USDA Select Agent and Toxin List
- Designing organisms for deliberate environmental release without regulatory approval
- Attempting to circumvent safety scoring or dual-use detection
- Using the platform to facilitate violations of the Biological Weapons Convention (BWC)
- Using the platform to design controlled substances or precursors
- Sharing designs publicly that contain high-risk elements flagged by the safety scorer

**Enforcement mechanism:** The ToS should reserve ProtoForge's right to suspend accounts, refuse to generate designs that trigger safety flags, and report suspected misuse to appropriate authorities. The existing safety scoring system (`safety_scorer.py`) provides a technical foundation for this, but it needs a contractual counterpart in the ToS.

### 2.5 Account Termination and Data Handling

- Right to terminate accounts that violate AUP
- What happens to stored designs upon termination (deletion timeline)
- What happens to designs upon account deletion at user request

---

## 3. GDPR Compliance

### 3.1 Legal Basis for Processing

ProtoForge needs a valid legal basis under GDPR Article 6 for each processing activity:

| Processing Activity | Recommended Legal Basis |
|---|---|
| Account creation (email, name, password) | Contract performance (Art. 6(1)(b)) |
| Design generation and storage | Contract performance |
| Sending prompts to Anthropic Claude API | Contract performance + legitimate interest |
| Safety scoring and audit logging | Legitimate interest (Art. 6(1)(f)) -- platform safety |
| NCBI queries (no personal data) | N/A -- no personal data processed |
| Rate limiting | Legitimate interest |
| Email communications (if any) | Consent (Art. 6(1)(a)) for marketing; contract for transactional |

### 3.2 Right to Deletion (Article 17)

ProtoForge must implement:

- **Account deletion endpoint:** Delete the User record, all associated Design records, ChatMessage records, and AuditLog records.
- **Timeline:** GDPR does not specify an exact deadline, but "without undue delay" is interpreted as within 30 days.
- **Complications:** Audit logs contain user IDs and safety flags. Consider whether anonymization (replacing user ID with a hash) is sufficient to satisfy deletion requests while retaining safety audit trails. This is a legitimate interest balancing test -- consult a lawyer on this specific point.
- **Third-party deletion:** Anthropic deletes API logs after 7 days automatically, so no action needed for prompts older than 7 days. For recent prompts, Anthropic's DPA should cover deletion obligations.

### 3.3 Data Portability (Article 20)

Users have the right to receive their personal data in a structured, commonly used, machine-readable format. For ProtoForge, this means:

- Export all user designs (JSON or FASTA format -- the platform already generates FASTA downloads)
- Export account information
- Export chat/refinement history

**Implementation note:** The existing FASTA download feature in `ResultsPanel.tsx` partially covers this, but a comprehensive "download my data" feature is needed for full compliance.

### 3.4 Data Processing Agreements (DPAs)

**Anthropic:** A DPA with Standard Contractual Clauses is automatically incorporated into Anthropic's Commercial Terms of Service. When ProtoForge accepted the API terms, this DPA was accepted. Verify this is in place by checking the Anthropic dashboard or contacting their privacy team.

**NCBI:** NCBI is a US government agency operating public databases. No DPA is needed for querying public databases, as the queries do not involve personal data (gene names, accession numbers). NCBI's terms of use apply, but these are usage/rate-limit terms, not privacy terms.

**Hosting/Infrastructure:** If ProtoForge deploys to Render, Vercel, or AWS, DPAs will be needed with those providers. Most major cloud providers offer standard DPAs.

### 3.5 Cookie Consent

The current codebase uses JWT tokens stored (likely) in localStorage or as HTTP-only cookies. If JWT tokens are stored as cookies:

- A cookie consent banner is required under the ePrivacy Directive (which works alongside GDPR).
- Strictly necessary cookies (authentication) may be exempt from consent requirements, but a cookie notice is still needed.
- If analytics, tracking, or advertising cookies are added later, explicit opt-in consent is required before setting them.

**Current state:** No analytics or tracking cookies identified in the codebase. If the JWT is stored in localStorage rather than a cookie, the cookie consent requirement is minimal (just a notice about the auth mechanism).

### 3.6 Data Protection Officer (DPO)

**A DPO is likely NOT required** for ProtoForge at launch. Under GDPR Article 37, a DPO is mandatory only when:

1. The organization is a public authority (no)
2. Core activities require large-scale, regular and systematic monitoring of individuals (no -- ProtoForge monitors designs for safety, not individuals)
3. Core activities involve large-scale processing of special category data or criminal conviction data (no)

ProtoForge's core activity is generating bioengineering designs, not monitoring individuals or processing sensitive personal data at scale. The safety scoring system monitors content, not people.

**However:** If the platform grows significantly and begins processing data in ways that involve systematic monitoring of user behavior (e.g., behavioral analytics, usage pattern tracking for safety purposes), this assessment should be revisited.

### 3.7 International Data Transfers

User data from EU users is transferred to the US when:
- Prompts are sent to Anthropic's US-based Claude API
- The backend server is hosted in the US (likely, given current deployment plans)

**Mechanism:** Anthropic's DPA includes Standard Contractual Clauses (SCCs), which is the standard mechanism for EU-to-US data transfers post-Schrems II. For hosting, ensure the hosting provider also offers SCCs or is certified under the EU-US Data Privacy Framework.

---

## 4. EU AI Act Implications

### 4.1 Risk Classification

The EU AI Act classifies AI systems into four risk tiers: unacceptable, high-risk, limited risk, and minimal risk.

**ProtoForge's likely classification: Limited risk (with transparency obligations), NOT high-risk.**

The high-risk AI systems are enumerated in Annex III of the AI Act, covering eight specific domains:
1. Biometrics
2. Critical infrastructure (water, gas, electricity, transport)
3. Education and vocational training
4. Employment and worker management
5. Access to essential services (credit, insurance, public benefits)
6. Law enforcement
7. Migration and border control
8. Administration of justice

A bioengineering design tool does not fall into any of these categories. It is not a safety component of critical infrastructure, it does not make decisions about individuals' access to services, and it does not perform biometric identification.

**However, there are two caveats:**

1. The Commission is required to publish guidelines specifying high-risk classification by February 2026, and a comprehensive list of practical examples of high-risk and non-high-risk use cases is expected. As of March 2026, these guidelines may have been published -- check the AI Act Service Desk for updates.

2. Article 6(2) allows the Commission to update Annex III. Future amendments could potentially add AI systems used in biological design, especially if biosecurity concerns escalate. This is speculative but worth monitoring.

### 4.2 Transparency Obligations

Even if not classified as high-risk, ProtoForge has transparency obligations under Article 50 (applicable from August 2, 2026):

- **AI-generated content disclosure:** Users must be informed that the gene circuits and designs are generated by an AI system (Claude). The existing disclaimers partially cover this, but a more explicit "This design was generated by an AI system (Anthropic Claude)" notice may be needed.
- **Deployer obligations:** If ProtoForge is considered a "deployer" of an AI system (which it is, as it integrates Claude's API), it must inform users that they are interacting with an AI system.

### 4.3 Scientific Research Exemption

Article 2(6) of the EU AI Act exempts AI systems "specifically developed and put into service for the sole purpose of scientific research and development."

**This exemption does NOT apply to ProtoForge** because:
- ProtoForge is a commercial product (freemium model, $29/mo Pro tier), not a research tool developed solely for scientific R&D.
- The exemption applies to AI that is "put into service" but NOT "placed on the market." A commercial SaaS product is placed on the market.
- The exemption is interpreted narrowly: "sole purpose" means exclusively for research, not a commercial tool that researchers happen to use.

### 4.4 Documentation Requirements

As a limited-risk AI system, ProtoForge's documentation obligations are lighter than for high-risk systems but still include:

- Basic technical documentation of how the AI system works
- Record of the AI model used (Claude sonnet-4) and its version
- Transparency notices to users
- No conformity assessment or CE marking required (those are high-risk obligations)

### 4.5 Timeline

- **February 2, 2025:** Prohibitions on unacceptable-risk AI took effect (ProtoForge is not affected).
- **August 2, 2025:** GPAI model obligations took effect (applies to Anthropic as the model provider, not to ProtoForge as the deployer).
- **August 2, 2026:** Obligations for Annex III high-risk systems and transparency rules (Article 50) take effect. ProtoForge needs transparency compliance by this date.

---

## 5. Biosecurity / Dual-Use Legal Exposure

### 5.1 Platform Liability for Dangerous Designs

This is the highest-stakes legal question for ProtoForge. If a user generates a design for a dangerous organism, is the platform liable?

**Current US law -- multiple theories of liability:**

**a) Section 230 of the Communications Decency Act:**
- Section 230 traditionally shields platforms from liability for user-generated content.
- **Critical issue:** Section 230 protects platforms from being "treated as the publisher or speaker of any information provided by another information content provider." But ProtoForge is not merely hosting user content -- it is generating content via AI in response to user prompts.
- Recent legal analysis (2025-2026) strongly suggests that **AI-generated outputs are unlikely to receive full Section 230 protection**, because the platform is "responsible, in whole or in part, for the creation or development" of the content. Transformer-based systems generate new, organic outputs, which looks less like neutral intermediation and more like authored speech.
- **No court has yet ruled definitively** on Section 230 coverage for AI-generated biological designs. The Garcia v. Character Technologies case (2024) is instructive: AI defendants did not even raise Section 230, likely because AI companies materially contribute to the content.
- Legislative proposals to sunset Section 230 by 2026 add further uncertainty.

**b) Products liability:**
- If a generated design causes harm, ProtoForge could face products liability claims. The design output could be treated as a "product" (information product / computational tool output).
- The "not lab-ready" disclaimer and safety scoring provide some defense, but disclaimers alone do not eliminate products liability if the plaintiff can show the tool was defectively designed or lacked adequate warnings.

**c) Negligence:**
- A negligence claim could argue that ProtoForge had a duty of care to prevent generation of dangerous designs, breached that duty through inadequate screening, and that the breach caused harm.
- The existing `safety_scorer.py` demonstrates awareness of the risk and an attempt to mitigate it, which cuts both ways: it shows responsibility, but it also establishes that ProtoForge knew about the risk (relevant to a negligence analysis).

**d) Aiding and abetting / conspiracy:**
- If a user explicitly requests a bioweapon design and ProtoForge's system generates it, there is theoretical exposure under federal criminal law (18 U.S.C. Section 175 -- Biological Weapons Anti-Terrorism Act) if the platform knew or had reason to know the design would be used for prohibited purposes.
- The Acceptable Use Policy and safety scoring system are critical defenses here. They demonstrate that the platform prohibits such use and takes steps to prevent it.

### 5.2 US Executive Order 14110 (October 2023) -- AI Biosecurity Provisions

Section 4.4(b) of Executive Order 14110 directed the federal government to reduce risks of misuse of synthetic nucleic acids. Key developments:

- The OSTP Framework for Nucleic Acid Synthesis Screening (April 2024) established screening requirements for **synthesis providers** -- entities that physically manufacture DNA. The Framework targets providers and manufacturers, not computational design tools.
- **May 5, 2025:** President Trump's Executive Order "Improving the Safety and Security of Biological Research" paused and directed revision of the 2024 Framework. The 90-day deadline (August 3, 2025) for revised guidance expired **without new guidance being issued**, leaving the regulatory landscape uncertain.
- The Trump EO called for expanding the Framework to non-federally funded entities and adding enforcement mechanisms, but the specifics remain unresolved as of March 2026.

**Implication for ProtoForge:** The current screening frameworks target physical synthesis vendors, not computational design tools. ProtoForge is not required to comply with the OSTP Framework. However:
- The regulatory trend is toward broader coverage.
- Voluntary screening demonstrates good faith and reduces liability exposure.
- If ProtoForge designs are exported and sent to a synthesis vendor, that vendor will perform their own screening.

### 5.3 Dual-Use Research of Concern (DURC) Policies

- US DURC policy (updated May 2024) is limited to life sciences research on a specific list of select agents and applies primarily to federally funded research.
- ProtoForge is a commercial tool, not a federally funded research project. DURC policies do not directly apply.
- However, the platform's safety scorer addresses DURC-relevant genes (anthrax, botulinum, ricin, Ebola, smallpox components), which demonstrates awareness and voluntary compliance with the spirit of DURC oversight.
- Policy experts have called for broadening DURC scope to include AI-driven synthetic biology tools. This is an evolving area.

### 5.4 Biological Weapons Convention (BWC)

The BWC prohibits the development, production, and stockpiling of biological weapons. While the BWC applies to state actors, domestic implementing legislation (in the US, the Biological Weapons Anti-Terrorism Act, 18 U.S.C. Section 175) criminalizes individual actions. ProtoForge's AUP should explicitly reference compliance with the BWC and prohibit use of the platform for designing agents prohibited under the Convention.

---

## 6. IGSC Gene Synthesis Screening

### 6.1 IGSC Harmonized Screening Protocol v3.0

The International Gene Synthesis Consortium's Harmonized Screening Protocol (updated September 2024) requires:

- Sequence screening of orders 200+ base pairs against the Regulated Pathogen Database (RPD)
- Six-frame translation to detect codon-optimized evasion attempts
- Customer screening (identity verification, institutional affiliation)
- 8-year retention of sequences and customer data

### 6.2 Do IGSC Standards Apply to Computational Design Tools?

**No, IGSC standards currently apply only to physical synthesis vendors** -- companies that manufacture and ship DNA. The IGSC is a consortium of gene synthesis companies (Twist Bioscience, IDT, GenScript, etc.), and their protocols govern the synthesis order workflow, not computational design.

ProtoForge does not synthesize DNA. It generates computational designs that a user would then need to order from a synthesis vendor. At the point of ordering, the synthesis vendor performs IGSC-compliant screening.

**However, this distinction is becoming less clear:**

- In October 2025, Microsoft researchers demonstrated that AI protein design tools could redesign known toxins to evade BLAST-based screening. IGSC and major vendors deployed patches catching approximately 97% of AI-designed evasion attempts, but gaps remain.
- The biosecurity community is increasingly discussing whether computational design tools should perform upstream screening to prevent users from even generating designs that would be flagged by synthesis vendors.
- SecureDNA, a nonprofit, offers free screening for sequences 30+ nucleotides, with a REST API that could be integrated into ProtoForge's pipeline.

### 6.3 Assessment of ProtoForge's Existing Safety Scorer

The current `safety_scorer.py` (at `/home/cypherthread/protoforge/backend/services/safety_scorer.py`) performs:

**What it does:**
- Regex-based pattern matching against 4 known pathogenic sequence motifs (botulinum toxin, anthrax pagA, ricin RTA, smallpox crmB)
- Gene name matching against 11 dual-use gene names (anthrax, ricin, botulinum, Ebola, smallpox components)
- Antibiotic resistance marker detection (13 markers)
- Environmental release language flagging
- Sequence length and GC content analysis
- Assigns a numerical safety score (0.0-1.0) with risk categories

**What it lacks (compared to IGSC-level screening):**
- No BLAST-based homology screening against a comprehensive pathogen database
- Only 4 regex patterns vs. the IGSC Regulated Pathogen Database (hundreds of entries)
- No protein-level functional screening (important for detecting codon-optimized evasion)
- No customer screening or identity verification
- No six-frame translation analysis
- The comment in the code itself acknowledges this: "simplified for MVP -- production would use a comprehensive database like the IGSC screening guidelines"

**Is it legally sufficient?**
- For legal compliance: Yes, because no law currently requires computational design tools to perform synthesis-level screening.
- For liability mitigation: It is a meaningful step that demonstrates good faith, but it could be significantly strengthened.
- For ethical responsibility: It falls short of what the biosecurity community would consider robust screening.

### 6.4 Recommendations for Screening Enhancement

1. **Integrate SecureDNA** (free, nonprofit, REST API): Screen all generated sequences against their comprehensive hazard database before returning results to users. This is the single highest-impact improvement for biosecurity posture.
2. **Expand the pathogen pattern database:** The current 4 regex patterns are inadequate. At minimum, cover all CDC/USDA Select Agents and Toxins.
3. **Add protein-level screening:** The pipeline already performs codon optimization, so the protein sequences are available. Screen at the protein level, not just DNA.
4. **Log and review flagged designs:** The audit logging system exists but should trigger alerts for high-risk flags, not just passive logging.
5. **Consider refusing to return designs** that score below a safety threshold (currently the system returns designs with warnings, even if they score 0.0).

---

## 7. Open Source License Audit

### 7.1 Dependency License Analysis

| Package | License | Commercial SaaS Use | Risk |
|---|---|---|---|
| **COBRApy** | GPL-2.0+ / LGPL-2.0+ (dual license) | See analysis below | MEDIUM |
| **BioPython** | Biopython License / BSD-3-Clause (dual) | Permitted | LOW |
| **dna_features_viewer** | MIT | Permitted | NONE |
| **FastAPI** | MIT | Permitted | NONE |
| **SQLAlchemy** | MIT | Permitted | NONE |
| **matplotlib** | PSF-based (permissive) | Permitted | NONE |
| **Pillow** | HPND (permissive) | Permitted | NONE |
| **anthropic** (Python SDK) | MIT | Permitted | NONE |
| **uvicorn** | BSD-3-Clause | Permitted | NONE |
| **httpx** | BSD-3-Clause | Permitted | NONE |
| **pydantic** | MIT | Permitted | NONE |
| **PyJWT** | MIT | Permitted | NONE |
| **bcrypt** | Apache-2.0 | Permitted | NONE |

### 7.2 COBRApy -- The Key Concern

COBRApy is dual-licensed under GPL-2.0-or-later and LGPL-2.0-or-later. Users may choose which license applies.

**Under LGPL-2.0+:**
- You can use the library in a proprietary application without open-sourcing your application, provided you dynamically link to the library (standard Python import behavior qualifies).
- If you modify COBRApy itself, you must release those modifications under LGPL.
- You must allow users to re-link against modified versions of the LGPL library (relevant for compiled software, less so for Python).

**Under GPL-2.0+:**
- If you choose GPL, derivative works must also be GPL-licensed.
- **The SaaS loophole:** Under GPL (v2 or v3), the copyleft obligation is triggered by "distribution." Running GPL software on a server and providing it as a service (SaaS) is NOT distribution. Therefore, ProtoForge can use GPL-licensed COBRApy server-side without open-sourcing its own code.
- This is a well-established legal interpretation. The AGPL (Affero GPL) was specifically created to close this loophole, but COBRApy is NOT AGPL-licensed.

**Bottom line:** ProtoForge can safely use COBRApy in a commercial SaaS under either the LGPL (preferred -- use it as a library without modification) or the GPL (SaaS loophole applies). Choose the LGPL path for maximum legal clarity. Do not modify the COBRApy source code unless you are prepared to release those modifications.

### 7.3 BioPython

BioPython is dual-licensed under the Biopython License Agreement and the BSD-3-Clause License. Both are permissive licenses that explicitly permit commercial use, modification, and distribution. No concerns for SaaS use.

### 7.4 dna_features_viewer

Licensed under MIT by the Edinburgh Genome Foundry. The MIT license is maximally permissive -- commercial use, modification, and distribution are all permitted with only an attribution requirement (include the license notice). No concerns.

### 7.5 Genome-Scale Models (iJO1366, iJN1463)

The FBA engine downloads BiGG genome-scale models. These models are published scientific works, typically released under Creative Commons licenses (CC-BY or CC0). Verify the specific license for each model used. Generally, academic metabolic models are freely available for commercial use with attribution.

### 7.6 Summary

**No copyleft (GPL/AGPL) dependencies that would force open-sourcing of ProtoForge's code** under a SaaS model. The only GPL-licensed dependency (COBRApy) is either usable under LGPL (permissive path) or under the GPL SaaS loophole. No AGPL dependencies were identified.

**Action item:** Add a LICENSE-THIRD-PARTY.md or equivalent notice file acknowledging all open-source dependencies and their licenses. This is good practice and satisfies the attribution requirements of MIT, BSD, and Biopython licenses.

---

## 8. Recommendations & Launch Checklist

### 8.1 Required Legal Documents (Priority Order)

| Priority | Document | Self-Draftable? | Estimated Cost (Lawyer) | Notes |
|---|---|---|---|---|
| **P0 -- BLOCKER** | Terms of Service | Partially | $1,500-$3,000 | AUP and liability sections need lawyer review for a bioengineering platform |
| **P0 -- BLOCKER** | Privacy Policy | Partially | $500-$1,500 | Template-based draft is feasible; lawyer review recommended for GDPR compliance |
| **P0 -- BLOCKER** | Acceptable Use Policy | Can self-draft | Included in ToS | Critical for biosecurity; list prohibited uses explicitly |
| **P1 -- PRE-LAUNCH** | Cookie/Consent Notice | Can self-draft | $0-$300 | Minimal if no tracking cookies |
| **P1 -- PRE-LAUNCH** | GDPR Data Subject Rights Process | Can self-draft | $0 | Internal process document for handling deletion/access requests |
| **P2 -- POST-LAUNCH** | DPA with Hosting Provider | Standard form | $0 | Most providers offer standard DPAs at no cost |
| **P2 -- POST-LAUNCH** | Third-Party License Notices | Can self-draft | $0 | Attribution file for open-source dependencies |
| **P3 -- LATER** | EU AI Act Transparency Documentation | Can self-draft | $0-$500 | Needed by August 2026 |

### 8.2 Can the Founder Self-Draft?

**Partially.** Here is a candid assessment:

- **Privacy Policy:** A founder can produce a reasonable first draft using established templates (Termly, iubenda, PrivacyPolicies.com) and customize for ProtoForge's specific data flows. GDPR-specific provisions (legal basis, international transfers, DPA references) benefit from lawyer review. Cost of a lawyer review of a self-drafted policy: ~$500-$800.

- **Terms of Service:** The general structure can be templated, but the biosecurity-specific provisions (acceptable use policy, liability for generated biological designs, dual-use disclaimers) are novel enough that a lawyer experienced in biotech or AI should review them. A biotech/AI-specialized lawyer reviewing a self-drafted ToS: ~$1,000-$2,000.

- **Acceptable Use Policy:** Can be self-drafted by referencing the CDC/USDA Select Agent List, the Biological Weapons Convention, and existing synthetic biology platform terms (e.g., Benchling's ToS, Twist Bioscience's ordering terms).

**Estimated total legal setup cost: $2,000-$5,000** for a lawyer-reviewed ToS + Privacy Policy package. This is within range for a solo founder. A SaaS-specialized legal package from platforms like Clerky, Stripe Atlas legal add-ons, or ContractsCounsel could reduce costs to the $1,000-$2,500 range, though biotech-specific provisions may not be covered by standard packages.

### 8.3 Immediate Red Flags That Could Block Launch

**RED FLAG 1: No Terms of Service exist.**
Without a ToS that includes an acceptable use policy, liability limitations, and warranty disclaimers, ProtoForge has essentially no legal protection against misuse claims. This is a hard launch blocker.

**RED FLAG 2: Safety scorer is minimal.**
The 4-regex, 11-gene-name safety system is better than nothing but far below industry expectations. If a user generates a design for a dangerous organism and the safety scorer fails to flag it, ProtoForge's defense ("we had safety measures") would be undermined. Integrating SecureDNA (free API) before launch would significantly strengthen both the safety posture and the legal defense.

**RED FLAG 3: No account deletion capability.**
GDPR requires the ability to delete user data on request. The current codebase has no deletion endpoint. This needs to be implemented before serving EU users.

**RED FLAG 4: No payment processing privacy terms.**
If launching with a $29/mo Pro tier, a payment processor (Stripe, etc.) will be added. The privacy policy needs to account for payment data processing, and Stripe's DPA needs to be in place.

**RED FLAG 5: Audit logs may conflict with deletion rights.**
The audit log stores user IDs alongside safety flags. If a user requests deletion, can their audit log entries be anonymized rather than deleted? This needs a documented legal basis (legitimate interest in maintaining safety records) and should be disclosed in the privacy policy.

### 8.4 Pre-Launch Action Items (Ordered)

1. Draft Terms of Service with Acceptable Use Policy (biosecurity-focused)
2. Draft Privacy Policy (GDPR-compliant, disclose Anthropic API data processing)
3. Implement account deletion endpoint (GDPR right to erasure)
4. Integrate SecureDNA screening API into the design pipeline
5. Expand safety_scorer.py pathogen database beyond 4 regex patterns
6. Add "data export" feature for GDPR data portability
7. Add explicit AI transparency notice ("This design was generated by an AI system")
8. Create third-party license attribution file
9. Have a biotech-experienced lawyer review the ToS and Privacy Policy
10. Set up payment processing with appropriate DPA and privacy disclosures

### 8.5 Post-Launch Monitoring

- Monitor EU AI Act implementing guidance (Commission guidelines on high-risk classification were due by February 2026)
- Monitor the status of revised US nucleic acid synthesis screening framework (Trump EO directed revision but no new guidance issued as of March 2026)
- Monitor state privacy law changes (new laws taking effect in 2026 in multiple states)
- Monitor any legislative changes to Section 230 affecting AI-generated content
- Track IGSC protocol updates, especially any expansion to computational tools
- Watch for any legal cases involving AI-generated biological designs (none exist yet, but the first will set important precedent)

---

## 9. Sources

### EU AI Act
- [EU AI Act 2026 Updates: Compliance Requirements and Business Risks](https://www.legalnodes.com/article/eu-ai-act-2026-updates-compliance-requirements-and-business-risks)
- [AI Act | Shaping Europe's Digital Future](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
- [EU AI Act Timeline: Key Compliance Dates](https://www.dataguard.com/eu-ai-act/timeline)
- [Timeline for Implementation of the EU AI Act](https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act)
- [High-Risk AI - EU AI Act Guide (Orrick)](https://ai-law-center.orrick.com/eu-ai-act/high-risk-ai/)
- [352 Days to Compliance: EU AI Act High-Risk Deadlines](https://www.modulos.ai/blog/eu-ai-act-high-risk-compliance-deadline-2026/)
- [The EU AI Act: 6 Steps to Take Before 2 August 2026](https://www.orrick.com/en/Insights/2025/11/The-EU-AI-Act-6-Steps-to-Take-Before-2-August-2026)
- [Annex III: High-Risk AI Systems](https://artificialintelligenceact.eu/annex/3/)
- [Article 6: Classification Rules for High-Risk AI Systems](https://artificialintelligenceact.eu/article/6/)
- [Article 2: Scope (Scientific Research Exemption)](https://artificialintelligenceact.eu/article/2/)
- [Challenges in Applying the EU AI Act Research Exemptions](https://www.nature.com/articles/s41746-025-02263-0)

### IGSC & Gene Synthesis Screening
- [IGSC Harmonized Screening Protocol v3.0](https://genesynthesisconsortium.org/wp-content/uploads/IGSC-Harmonized-Screening-Protocol-v3.0-1.pdf)
- [International Gene Synthesis Consortium](https://genesynthesisconsortium.org/)
- [International Screening Standards - IBBIS](https://ibbis.bio/our-work/international-screening-standards/)
- [Gene Synthesis Screening Information Hub (Johns Hopkins)](https://genesynthesisscreening.centerforhealthsecurity.org/)
- [IBBIS Whitepaper: Implementing Emerging Customer Screening Standards](https://ibbis.bio/wp-content/uploads/2025/11/IBBIS_Whitepaper_2025_Implementing-Emerging-Customer-Screening-Standards-for-Nucleic-Acid-Synthesis.pdf)
- [SecureDNA: Free DNA Synthesis Screening Platform](https://securedna.org/)

### US Executive Orders & Biosecurity Policy
- [Breaking Down the Biden AI EO: Screening DNA Synthesis and Biorisk (CSET Georgetown)](https://cset.georgetown.edu/article/breaking-down-the-biden-ai-eo-screening-dna-synthesis-and-biorisk/)
- [OSTP Framework for Nucleic Acid Synthesis Screening (2024)](https://bidenwhitehouse.archives.gov/wp-content/uploads/2024/10/OSTP-Nucleic-Acid_Synthesis_Screening_Framework-Sep2024-Final.pdf)
- [Trump EO: Improving Safety and Security of Biological Research (May 2025)](https://www.whitehouse.gov/presidential-actions/2025/05/improving-the-safety-and-security-of-biological-research/)
- [Convergence of AI and Synthetic Biology: The Looming Deluge (Nature)](https://www.nature.com/articles/s44385-025-00021-1)
- [Dual Use Concerns of Generative AI and LLMs](https://www.tandfonline.com/doi/full/10.1080/23299460.2024.2304381)

### Section 230 & AI Liability
- [Section 230 Immunity and Generative AI (CRS / Congress.gov)](https://www.congress.gov/crs-product/LSB11097)
- [Section 230 and AI-Driven Platforms (The Regulatory Review)](https://www.theregreview.org/2026/01/17/seminar-section-230-and-ai-driven-platforms/)
- [Section 230 Immunity for AI Chatbot Lawsuits 2026 (Moody's)](https://www.moodys.com/web/en/us/insights/insurance/230-immunity-for-AI-chatbot-lawsuits.html)
- [Fortune: Section 230 May Not Protect AI Chatbots](https://fortune.com/2025/10/03/ai-chatbot-section-230-meta-social-media-legal-shield-no-protection/)
- [Generative AI Meets Section 230 (UChicago Business Law Review)](https://businesslawreview.uchicago.edu/print-archive/generative-ai-meets-section-230-future-liability-and-its-implications-startup)

### Privacy & GDPR
- [Anthropic DPA (Data Processing Addendum)](https://privacy.claude.com/en/articles/7996862-how-do-i-view-and-sign-your-data-processing-addendum-dpa)
- [Anthropic Privacy Policy](https://platform.claude.com/docs/en/legal-center/privacy)
- [Updates to Anthropic Consumer Terms and Privacy Policy](https://www.anthropic.com/news/updates-to-our-consumer-terms)
- [SaaS Privacy Compliance Requirements 2025 Guide](https://secureprivacy.ai/blog/saas-privacy-compliance-requirements-2025-guide)
- [Privacy Laws for Startups: GDPR, CCPA & State Compliance](https://promise.legal/startup-legal-guide/compliance/privacy-laws)
- [DPO Requirements (European Commission)](https://commission.europa.eu/law/law-topic/data-protection/rules-business-and-organisations/obligations/data-protection-officers/does-my-companyorganisation-need-have-data-protection-officer-dpo_en)

### IP Ownership
- [Generative AI and Copyright Law (CRS / Congress.gov)](https://www.congress.gov/crs-product/LSB10922)
- [AI Created It -- But Do You Own It? (Darrow Everett)](https://darroweverett.com/ai-and-the-law-who-owns-output-legal-analysis/)
- [Who Owns AI Content? Platform Rights Compared (2026)](https://www.terms.law/2025/04/09/navigating-ai-platform-policies-who-owns-ai-generated-content/)

### Open Source Licenses
- [COBRApy License (GitHub)](https://github.com/opencobra/cobrapy)
- [BioPython License (GitHub)](https://github.com/biopython/biopython/blob/master/LICENSE.rst)
- [DNA Features Viewer (Edinburgh Genome Foundry)](https://github.com/Edinburgh-Genome-Foundry/DnaFeaturesViewer)
- [Understanding the SaaS Loophole in GPL (Revenera)](https://www.revenera.com/blog/software-composition-analysis/understanding-the-saas-loophole-in-gpl/)
- [The SaaS Loophole in GPL Open Source Licenses (Mend)](https://www.mend.io/blog/the-saas-loophole-in-gpl-open-source-licenses/)

### Legal Costs
- [Privacy Policy Cost (ContractsCounsel)](https://www.contractscounsel.com/b/privacy-policy-cost)
- [Terms of Service and Privacy Policy Cost (ContractsCounsel)](https://www.contractscounsel.com/b/terms-of-service-and-privacy-policy-cost)

---

*This report was prepared on March 14, 2026, based on web research and codebase analysis. Laws, regulations, and enforcement guidance are evolving rapidly in this space. This document should be treated as a research starting point, not as legal advice. Consult a qualified attorney specializing in biotech/AI law before finalizing legal documents.*
