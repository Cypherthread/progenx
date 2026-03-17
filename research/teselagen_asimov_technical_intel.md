# TeselaGen & Asimov Technical Intelligence — Reverse Engineering Report
## March 15, 2026

---

## TeselaGen: What We Can Use

### Open-Source (MIT Licensed, Directly Integrable)

1. **@teselagen/ove** — React vector editor for interactive plasmid editing
   - CircularView, LinearView, DigestTool, PCRTool, AlignmentTool
   - Far richer than our static SVG renderer
   - github.com/TeselaGen/tg-oss

2. **@teselagen/bio-parsers** — Parse/export 7 biological formats
   - FASTA, GenBank, SBOL XML, SnapGene, Geneious XML, JBEI XML, AB1
   - We only output FASTA currently. This adds GenBank/SBOL export.

3. **@teselagen/sequence-utils** (135 source files) — DNA manipulation algorithms:
   - **Tm calculation**: Nearest-neighbor with Breslauer/Sugimoto/SantaLucia tables
   - **Virtual restriction digest**: cut site finding, fragment calculation, Type IIS support
   - **ORF detection**: findOrfsInPlasmid, getOrfsFromSequence
   - **Overlap detection**: useful for Gibson Assembly validation
   - **Reverse translation**: protein to degenerate DNA
   - **Molecular weight calculation**: from amino acid sequence

### TeselaGen API Architecture (Design Patterns to Copy)

- **Bin-based combinatorial design**: Constructs = ordered bins (promoter, RBS, CDS, terminator), each bin holds multiple interchangeable parts. Simple matrix structure.
- **RBS Calculator integration**: Direct integration with Salis Lab RBS Calculator v2.1 (ReverseRBS, LibraryCalculator modes)
- **Async codon optimization jobs**: Algorithm is parameterized, suggesting multiple algorithms available
- **EVOLVE module**: Predictive (descriptor->target ML) + Evolutive (multi-objective Pareto) + Generative (novel sequences)

---

## Asimov/Cello: What We Can Use

### Cello v2 Pipeline (9 modules, open-source Java)

The core algorithm is **simulated annealing for genetic part assignment**:
- Temperature: log cooling from 100 to 0.001 over 600 steps + 100 greedy steps
- Scoring: min(ON activity) / max(OFF activity) across truth table — biological signal-to-noise ratio
- Constraints: toxicity threshold (growth > 0.75), roadblock detection (transcriptional interference)
- Parts modeled with **Hill equation**: output = ymin + (ymax-ymin) / (1 + (x/K)^n)

### UCF (User Constraint File) Format
- JSON format defining gate libraries with Hill equation parameters
- Input sensors, output devices, parts, device rules, circuit rules
- Sample UCFs included in Cello repo for E. coli

### CIDARLAB Open-Source Tools (github.com/CIDARLAB, 187 repos)
- **Cello v1** (861 stars) + **Cello v2** — genetic circuit compilers
- **Knox** (14 stars) — combinatorial design using GOLDBAR framework + Neo4j
- **dnaplotlib** — Python DNA visualization
- **Eugene** — constraint-based genetic design language

### Key Voigt Lab Publications
- Nielsen et al., Science 2016 — original Cello: 60 circuits designed, 45 worked first try
- Cello 2.0, Nature Protocols 2022 — updated pipeline
- Weinberg et al., Nat Biotech 2017 — large-scale genetic part characterization

---

## Priority Implementation List (Combined)

### Immediate (add real accuracy value)
1. **Tm calculation** — port SantaLucia nearest-neighbor from sequence-utils to Python. Add to assembly planner for primer design.
2. **GenBank export** — replicate bio-parsers JSON schema for GenBank output alongside FASTA.
3. **Virtual restriction digest** — validate Golden Gate/Gibson assembly plans by checking for internal cut sites.

### Near-term (major feature additions)
4. **Open Vector Editor** — integrate @teselagen/ove into React frontend for interactive plasmid editing.
5. **Hill equation gate modeling** — implement Cello's response function scoring for gene circuit performance prediction.
6. **RBS Calculator integration** — predict translation initiation rates for designed RBS sequences.

### Strategic (competitive differentiation)
7. **Simulated annealing part optimization** — adapt Cello's SA algorithm for our assembly optimization.
8. **Combinatorial bin-based design** — TeselaGen's matrix approach for multi-variant library design.
9. **Multi-objective Pareto optimization** — rank design variants across multiple objectives simultaneously.
