# Progenx Competitive Intelligence
## Cradle, Asimov, TeselaGen — March 2026

---

## The Bottom Line

None of these three are direct competitors. They all serve experienced biotech professionals with existing wet labs and enterprise budgets. Progenx serves the underserved: biohackers, students, iGEM teams, climate founders who need the first 80% of ideation without a PhD or a million-dollar budget.

| Dimension | Cradle | Asimov | TeselaGen | Progenx |
|-----------|--------|--------|-----------|------------|
| **Input** | Protein sequence + lab data | Manual part selection | Structured + NL libraries | Plain English |
| **Output** | Optimized protein variants | Cell lines, vectors | Libraries, protocols, worklists | Gene circuits, sequences, FBA, maps |
| **User** | Pharma R&D ($50K+/yr) | Pharma R&D ($209M raised) | Labs with automation ($150/mo+) | Anyone (free) |
| **Chassis** | N/A (protein-level) | Mammalian (CHO, HEK) | Various (lab-dependent) | Prokaryotic (E. coli, P. putida, S. elongatus) |
| **FBA** | No | No | No | Yes (COBRApy) |
| **Safety scoring** | No | Biosecurity screening | No | Yes (pathogen, dual-use, resistance) |
| **Kill switch** | No | No | No | Yes (ccdA/ccdB, mazE/mazF) |
| **Plain English** | No | No | Partial (library designer) | Yes (core feature) |
| **Free tier** | No | iGEM only | Yes (Community) | Yes (5 designs/mo) |

---

## What to Steal (Actionable, prioritized)

### High Priority (do before or at launch)

1. **"If you can describe it, you can design it"** — adapt Cradle's brilliant positioning ("if you can measure it, you can optimize it") to Progenx's plain-English strength.

2. **iGEM partnership** — Asimov gives free Kernel access to iGEM teams. We should formalize a similar partnership. Same target users, massive credibility signal, pipeline to future enterprise customers.

3. **Quantified outcome claims** — Cradle says "1.2x to 12x speedup" and "up to 90% cost reduction." We need specific numbers: "60-second design time," "19 verified genes," "$0 per design on free tier." Already started on the landing page stats bar.

4. **Vendor pricing integration** — TeselaGen's BioShop shows real-time DNA synthesis pricing from Twist/IDT. We currently just link to vendors. Adding actual $/bp quotes would be a strong differentiator.

### Medium Priority (post-launch, first 3 months)

5. **Interactive plasmid editor** — TeselaGen open-sourced their React vector editor (`@teselagen/ove`, MIT license, GitHub). We could integrate this instead of our static SVG maps. Users could click features, edit, and export.

6. **Primer design in assembly plans** — TeselaGen generates complete primer sequences with Tm calculations. Our assembly plans say "use Golden Gate" but don't generate primers. Adding this would make our output more lab-actionable.

7. **Python SDK** — TeselaGen has `pip install tesela`. A `pip install protoforge` SDK with `protoforge.design("plastic eating bacteria")` would be powerful for developer adoption and integration.

8. **ML-trained codon optimization** — Both Cradle and Asimov use learned models, not just frequency tables. Our per-chassis codon tables are functional but not state-of-the-art. Could train on publicly available expression data.

9. **Lab feedback loop** — Cradle's core value is the iterative data flywheel (design -> test -> upload results -> better designs). We could add a "Upload Lab Results" feature that refines future designs, even if the ML is simple at first.

### Low Priority (6+ months)

10. **Combinatorial library design** — TeselaGen generates 96-384 variant libraries from a single prompt. We generate single circuits. Library design would be powerful for iGEM teams and researchers.

11. **Content/media arm** — Asimov publishes Asimov Press (science media). A Progenx blog or newsletter about synbio design could build thought leadership cheaply.

12. **Lab automation integration** — TeselaGen exports worklists for Tecan/Hamilton/Echo. Not relevant until our users have automation hardware, but worth planning for enterprise tier.

---

## What NOT to Copy

1. **Enterprise-only pricing** — All three are enterprise-first. Our free tier IS the moat. Don't abandon it.

2. **Manual part selection UI** — Asimov and TeselaGen require users to manually pick parts. Our LLM-first approach is the differentiator. Don't add complexity that makes us more like them.

3. **Mammalian cell focus** — Asimov is 100% CHO/HEK. We're prokaryotic. Don't chase the therapeutic market — it requires clinical-grade validation we can't provide.

4. **"Not chatbots" positioning** — TeselaGen explicitly positions against LLMs ("these agents execute real algorithms, not chatbots"). We ARE LLM-powered and should own it, because our LLM approach is what makes plain-English design possible.

5. **Overly complex onboarding** — All three require sales calls, SSO setup, or organization-level access. Keep our signup flow to email + password + start designing.

---

## Competitive Moat Assessment

Progenx's defensible advantages:
1. **Only plain-English-to-complete-design tool** — nobody else does this
2. **Only free self-service synbio design platform** — TeselaGen has a free tier but it's for library design, not full circuits
3. **Only platform with FBA metabolic modeling in the design pipeline** — none of the three do genome-scale FBA
4. **Only platform with automated kill switch + safety scoring** — genuine biosafety differentiator
5. **Data moat potential** — every design trains future models (not yet implemented but architecturally possible)

Vulnerabilities:
1. **Parts are not experimentally validated** — Cradle and Asimov test in real labs. Our parts come from NCBI accessions.
2. **Single-founder risk** — all three competitors have funded teams of 26-130+ people
3. **No lab integration** — Cradle partners with Ginkgo for one-click lab testing. We have no lab path.
4. **Codon optimization is basic** — frequency tables vs. learned ML models

---

*Research conducted March 15, 2026. Sources: company websites, press releases, documentation, API docs, GitHub repos, funding databases, interview articles. Flagged uncertainties noted in full reports.*
