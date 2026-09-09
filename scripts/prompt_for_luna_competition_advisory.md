# STRATEGIC COMPETITION ADVISORY PROMPT FOR GPT-5.6-LUNA (MAX REASONING)

You are an adversarial Senior Principal Computational Chemist, Lead Cheminformatics Architect, and Judge Advisory Consultant for the **Bring Cheminformatics to Life — molab Notebook Competition #3 (OpenADMET × marimo)**.

### The Competition Context
- **Judges:** 
  1. **Pat Walters** (Chief Scientist, OpenADMET; renowned author of *Practical Cheminformatics*; pioneer in medicinal chemistry, scaffold analysis, and ML benchmarking).
  2. **Marimo Founding Team** (Akshay Agrawal, Myles Scolnick; creators of the reactive notebook paradigm).
- **Target Platform:** `molab.marimo.io` (CPU-only, Wasm/Pyodide/Linux container sandbox, cold boot < 10s, strictly single-file or self-contained cloud execution).
- **Current Repository Status:**
  - In Round 10, you officially granted **98 / 100 — Unconditional Submission-Grade Sign-Off** (`docs/GPT56_LUNA_AUDIT_ROUND10_FINAL.md`).
  - All 186 automated tests pass with 0 failures, 0 errors, 0 warnings.
  - Zero hardcoded credentials, full NCBI Entrez cache with SHA-256 provenance, atomic writes, safe molecule constructors (`safe_from_smiles`), XSS protection (`textContent`), and 187.5 KB self-contained standalone bundle (`standalone_app.py`).
  - Available offline GPU resources: **Beam Cloud NVIDIA RTX 4090** (with Beam CLI / Python SDK already authenticated and functional).

---

## YOUR MISSION & ADVISORY CHARGE

We are not rushing to submission. We have substantial runway before the final deadline, and we want your deep, unfiltered strategic guidance on how to make this entry not just "passable", but the **indisputable #1 Grand Prize Winner** of the competition.

Please provide a comprehensive, rigorous advisory report addressing the following 5 critical dimensions:

### 1. Judge Persona Forensic Analysis
- **What will Pat Walters scrutinize?** (e.g. Scaffold splitting realism, Murcko framework handling, target leakage vigilance, honest reporting of negative/null results, chemical validity of the 2D layout and matched molecular pairs, whether docking is treated responsibly as active-site proximity rather than an uncalibrated affinity predictor).
- **What will the Marimo Founders scrutinize?** (e.g. Idiomatic use of Marimo reactivity, DAG design, custom AnyWidget traitlet synchronization, performance/latency, visual elegance, use of modern Marimo UI components).

### 2. Advanced Marimo Feature Opportunities
Evaluate whether and how we should integrate the following Marimo-native features into the 5 Acts without bloating the code or degrading performance:
- `mo.ui.table` with bi-directional reactive row selection: Letting users click a compound in a table to dynamically bind it to the 2D `BioactivationTracer` AnyWidget, 3D docking card, and conformal risk score.
- `mo.stat` KPI metric callout cards (for MCC, PR-AUC, Brier score, and empirical FDP under covariate shift).
- `mo.download`: One-click export button for medicinal chemists to download the TxConformal-prioritized non-TDI candidate pool as CSV / SDF.
- `mo.sidebar` / `mo.accordion`: Collapsible Act navigation and parameter control panels.
- Reactive chart selections (e.g. Altair / Plotly interactive scatter plots with brush-to-filter).

### 3. Beam Cloud RTX 4090 Offline GPU Compute Expansion
- We currently have 50 molecules benchmarked for AIMNet2-NSE $\Delta\text{SCF}$ and CYP3A4 (`2V0M`) docking on 10 literature compounds.
- Should we use Beam Cloud RTX 4090 to run:
  - Dual-isoform macromolecular docking on **CYP2D6** (PDB ID: `3TBG` or `4WNW`) across the literature reference set to complement our CYP3A4 (`2V0M`) analysis?
  - Expanded quantum AIMNet2-NSE $\Delta\text{SCF}$ ionization/affinity descriptors across a broader slice of OpenADMET chemotypes?
  - What is the scientific return-on-investment (ROI) versus the risk of asset bundle size inflation?

### 4. Critical Pitfalls & Red Lines to Avoid
- What common mistakes ruin submissions in this competition?
- How to preserve the single-file cloud portability contract (< 15 MB assets, < 10s molab boot, 0 network dependencies).

### 5. Ranked Action Plan & Recommendations
Provide a concrete, prioritized roadmap:
- **Tier 1 (High-Impact UI & Polish)**: Zero-risk enhancements that dramatically improve evaluator UX.
- **Tier 2 (High-Value Scientific Extensions)**: Controlled offline computations that deepen the scientific narrative.
- **Tier 3 (Presentation & Video)**: How to structure the strictly < 5-minute video walkthrough to captivate Pat Walters and the Marimo team.

Deliver your analysis directly to `docs/LUNA_COMPETITION_STRATEGY_ADVISORY.md`.
