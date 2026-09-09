# IN-DEPTH CODE, SCIENCE & COMPETITION AUDIT PROMPT FOR GPT-5.6-LUNA

You are an adversarial Senior Principal Software Engineer and Computational Chemist conducting an exhaustive, in-depth audit of this entire OpenADMET Cytochrome P450 Bioactivation & Conformal Risk Control project.

Do NOT give a polite or surface-level summary. We need a rigorous, fine-grained, adversarial review that uncovers every potential flaw, scientific gap, UI edge case, or deployment risk before competition submission.

## MANDATORY INVESTIGATION STEPS (Use your tools to read and verify these files before writing your report):
1. **Planning & Requirements:**
   - Read `MASTER_PLAN.md` and `TODO.md` to understand all project phases, execution cards, and scientific commitments.
2. **Core Interactive Application:**
   - Read `app.py` in its entirety. Inspect the reactive Marimo DAG, all 5 narrative Acts, cell dependencies, error handling, layout structuring, and LaTeX formulas.
3. **Custom AnyWidget & Molecular Layout Engine:**
   - Read `widgets/bioactivation_tracer.js`, `widgets/bioactivation_tracer.py`, `widgets/bioactivation_tracer.css`, and `widgets/layout_engine.py`.
   - Inspect SVG coordinate transformations, AFM ESM exports, traitlet sync, reactive halo rendering, and responsive header layouts.
4. **Data Packaging, Embedded Assets & Zero-Network Resilience:**
   - Read `models/embedded_assets.py`, `scripts/package_assets.py`, and inspect `data/fixtures/literature_mbi_reference_set.json`.
   - Check fallback sample decompression, SHA256 verification, and offline operation.
5. **Scientific Descriptors & Benchmarks:**
   - Inspect `models/quantum_features.py` (or AIMNet2-NSE features), `models/vina_docking.py` (or docking ablation fixtures), `models/mmp_engine.py`, and `models/txconformal.py` (or conformal selection results).
   - Check the mathematical and statistical validity: Are the claims backed by real calculations? Is there any leakage?
6. **Integration & DevTools Verification Suites:**
   - Inspect `tests/test_phase3_seam.py`, `tests/test_devtools_audit.py`, `tests/test_literature_mbi.py`, and `docs/DEVTOOLS_AUDIT_REPORT.json`.
   - Run `pytest` or inspect test passes.

---

## REQUIRED REVIEW SECTIONS IN YOUR REPORT:

### 1. Executive Verdict & Readiness Score
- Overall readiness score (0-100%) for the Marimo / OpenADMET competition.
- Major strengths vs. critical vulnerabilities.

### 2. Scientific & Methodological Rigor (Adversarial Critique)
- **Scaffold Split & The "Bathtub Effect":** Is Bemis-Murcko cluster-stratified splitting sound? Is data leakage genuinely zero?
- **Quantum Physics Grounding:** Are AIMNet2-NSE ΔSCF descriptors (IP, EA, chemical hardness η, electrophilicity ω, Fukui radical indices f_k^0) correctly computed and scientifically sound?
- **3D Active-Site Enzymology:** Are the AutoDock Vina v1.2.7 active-site docking poses in CYP3A4 2V0M vs 1TQN chemically credible?
- **Medicinal Chemistry Steering (MMPs):** Are the 46 matched molecular pairs genuine activity cliffs?
- **Statistical Provable Safety (TxConformal):** Does the weighted step-up selection procedure actually control FDR under covariate shift? Are the assumptions realistic?

### 3. Application Code Quality & Architecture
- **Single-File `app.py`:** DAG cycle-safety, variable scoping, PEP 723 metadata, execution flow.
- **AnyWidget Custom Component:** AFM export standards, DOM event listeners, memory leaks, SVG scaling/clipping, contrast.
- **Zero-Network Fallback:** Does the app work if the primary parquet is absent or network is disabled?

### 4. UI/UX, Typography & Accessibility Audit
- Visual hierarchy, markdown and LaTeX math formatting.
- Interactive controls (dropdowns, sliders, buttons) behavior and edge cases.
- Mobile / viewport responsiveness.

### 5. Detailed Findings & Edge Cases (File & Line Specific)
- Enumerate every specific finding with:
  - **Severity:** [CRITICAL / HIGH / MEDIUM / LOW / ENHANCEMENT]
  - **Location:** File path and line number(s)
  - **Problem:** Exact issue, why it matters, how it could fail
  - **Recommended Fix:** Concrete code snippet or architectural resolution

### 6. Final Prioritized Action Checklist
- Ranked list of fixes to implement before final submission.
