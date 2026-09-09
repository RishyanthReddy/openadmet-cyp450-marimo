# ROUND 11 ADVERSARIAL AUDIT PROMPT FOR GPT-5.6-LUNA (MAX REASONING)

You are the Lead Adversarial Reviewer, Principal Computational Chemist, and Senior Judge for the **Bring Cheminformatics to Life — molab Notebook Competition #3 (OpenADMET × marimo)**.

### Mandate
In Round 10 (`docs/GPT56_LUNA_AUDIT_ROUND10_FINAL.md`), you gave an unconditional **98/100 Submission-Grade Sign-Off**. Following your Strategic Advisory (`docs/LUNA_COMPETITION_STRATEGY_ADVISORY.md`) and Technical Implementation Plan (`docs/TIER1_TIER2_IMPLEMENTATION_PLAN.md`), the engineering team has executed the complete **Tier 1: High-Impact Native Marimo UI Polish** (`EC-T1-01` through `EC-T1-06`).

The user's explicit instructions:
1. Conduct an exhaustive post-implementation audit with Luna Max through Codex CLI.
2. Read all project implementation files and verify code, reactivity, tests, and runtime artifacts directly.
3. Do not proceed to Tier 2 until a calibrated, flawless audit and sign-off are achieved.

---

## FILES TO INSPECT ON DISK
Please use your file-reading tools to inspect and verify the actual files on disk:
1. `docs/TIER1_TIER2_IMPLEMENTATION_PLAN.md` — The authoritative specification for Cards `EC-T1-01` through `EC-T1-06`.
2. `app.py` — The primary modular Marimo application notebook.
3. `standalone_app.py` — The bundled single-file distribution (199,487 bytes).
4. `tests/test_tier1_ui.py` — The 14 dedicated automated unit & regression tests.
5. `scripts/bundle_app.py` — The bundler script with asset inlining and minification.
6. `docs/DEVTOOLS_AUDIT_REPORT.json` — The live Playwright headless DevTools audit report.

---

## KEY VERIFICATION GATES FOR TIER 1

### Gate 1: `EC-T1-01` (Native `mo.accordion` Refactor)
- **Act 1:** Check `act1_protocol` (`🔬 Deep Dive: The In Vitro Microsomal Preincubation Assay Protocol`) implemented as a native `mo.accordion`.
- **Act 5:** Check DOME compliance checklist refactored to native `mo.accordion`.
- **Zero HTML Disclosures:** Confirm raw `<details>` and `<summary>` HTML tags have been completely eliminated from `app.py` and `standalone_app.py`.

### Gate 2: `EC-T1-02` (Native `mo.stat` KPI Metric Callout Cards)
- **Act 2:** `act2_kpis` displaying:
  - Scaffold shift: `-0.0364` (PR-AUC, decrease / decrease)
  - MCC shift: `-0.0394` (MCC, decrease / decrease)
  - Inflation: `9.4%` (increase / target_direction="decrease")
- **Act 3:** `act3_kpis` displaying:
  - PR-AUC lift: `+0.0101` (PR-AUC, increase / increase)
  - MCC lift: `+0.0209` (MCC, increase / increase)
  - ROC-AUC: `+0.0023` (neutral, `direction=None`)
  - Brier error reduction: `-0.0031` (decrease / target_direction="decrease")
- **Act 5:** `act5_kpis` displaying:
  - Empirical FDP: `2.67%` (decrease / target_direction="decrease")
  - Mean candidates: `30.0` (increase / target_direction="increase")
  - Active nominal $\alpha$: `0.10` (`direction=None`)

### Gate 3: `EC-T1-03` (Bi-directional `mo.ui.table` Selection in Act 1)
- Table 1.1 configured with `selection="single"`, `initial_selection=[default_mbi_index]` (Raloxifene default), and internal `SMILES` hidden.
- Defensive normalization helper `normalize_single_table_value` handling `None`, empty lists `[]`, empty dicts `{}`, dicts-of-columns, and DataFrame records.
- Bi-directional reactive wiring: selected drug name directly drives Act 1 `BioactivationTracer` (`selected_name`) and Act 3 macromolecular 3D docking viewer.

### Gate 4: `EC-T1-04` (Bi-directional `mo.ui.table` Selection in Act 5)
- Table 5.1 configured with `selection="single"` with hidden internal machine columns (`candidate_id`, `smiles`).
- Downstream `candidate_card` rendering 2D structure, predicted liability, conformal p-value, and status.
- Safe empty-selection fallback when no row is clicked.

### Gate 5: `EC-T1-05` (One-Click `mo.download` CSV Candidate Export in Act 5)
- `candidate_download = mo.download(...)` exporting canonical 6 columns:
  `["molecule_name", "smiles", "predicted_liability_prob", "weighted_conformal_pvalue", "nominal_alpha_threshold", "conformal_cutoff_pstar"]`.
- Dynamically bound to active nominal $\alpha$ slider threshold.
- UTF-8 round-trip verified.

### Gate 6: `EC-T1-06` (Tier 1 Rebundling & Seam Integration Gate)
- Size Budget: `standalone_app.py` is **199,487 bytes** (strictly within the decimal `< 200,000` byte budget).
- Marimo DAG integrity: `marimo check app.py` and `marimo check standalone_app.py` both exit 0 with zero syntax, duplicate definition, or cyclic dependency errors.
- Python compilation: `.venv/bin/python -W error -m py_compile app.py standalone_app.py` exits 0 with zero warnings.
- Automated tests: 200 passed tests (14 in `test_tier1_ui.py`, 8 in `test_devtools_audit.py`, 178 unit/integration tests).
- Headless DevTools audit: 0 unhandled console errors, 0 network failures, 84 SVGs, 4 anywidget instances, 8.92ms p95 reactive render latency, status `PASS`.

---

## OUTPUT REQUIREMENTS
Author your audit report with:
1. **Executive Summary & Calibrated Score (out of 100)**: Reflecting Tier 1 completion on top of the Round 10 98/100 baseline.
2. **Card-by-Card Forensic Evaluation**: Detailed assessment of `EC-T1-01` through `EC-T1-06`.
3. **Marimo Reactivity & Scoping Audit**: Confirm that cell returns, private variables, closures, and DAG flows are strictly invariant and free of silent failure modes.
4. **Standalone Bundle & Wasm Portability Review**: Confirm `standalone_app.py` (199,487 bytes) satisfies single-file zero-network offline deployment.
5. **Clear Verdict & Authorization**: Explicit statement on whether Tier 1 is fully passed and whether the team is cleared to commence **Tier 2 (Beam Cloud RTX 4090 Dual-Isoform CYP2D6 Docking)**.
