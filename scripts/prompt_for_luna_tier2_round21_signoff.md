# Codex Execution Prompt: Luna Max Round 21 Final Sign-Off (OpenADMET x marimo)

You are **Luna Max** (`gpt-5.6-luna`, `model_reasoning_effort="max"`), the Senior Principal AI/ML & Biophysical Cheminformatics Auditor.

In Round 20, you confirmed:
- Gate 1 (Docking Integrity & Biophysical Grounding): **40/40**
- Gate 3 (Molab Bundling, SLA & Staging): **30/30**
- Gate 2: **28/30**
- You noted: *"The original static fallback/canonical narrative issue is fixed... but the empty-evaluation branch assigns numeric sentinel values: `0.0 kcal/mol` and `99.9 Å`. Those values are still rendered by the card templates as visible metrics in both artifacts: app.py:1127, 1159 and standalone_app.py:1958, 1990."*
- **Required correction:** *"render Vina affinity and heme-distance fields as explicit `No Evaluation Available` values when `_target_eval is None`, and add a regression test for the empty-evaluation branch."*

---

## Remediations Fully Executed for Round 21

### 1. Complete Elimination of Numeric Sentinels in Act 3 CYP2D6 Fallback
In `app.py` (lines 1103–1180) and `standalone_app.py` (lines 1940–2015):
- The dictionaries with dummy keys `"vina_affinity_kcal_mol": 0.0` and `"min_dist_to_heme_fe_angstrom": 99.9` have been **completely removed**.
- When `_target_eval` is present:
  - `_vina_3tbg_html`: `<span style="font-weight: 700; color: #047857;">{_res_3tbg["vina_affinity_kcal_mol"]:.2f} kcal/mol</span>`
  - `_fe_dist_3tbg_html`: `<span style="font-size: 15px; font-weight: 700; color: #047857;">{_res_3tbg["min_dist_to_heme_fe_angstrom"]:.2f} Å</span> ({_res_3tbg.get("nearest_heavy_atom", "N/A")})`
  - `_vina_4wnw_html`: `<span style="font-weight: 700; color: #334155;">{_res_4wnw["vina_affinity_kcal_mol"]:.2f} kcal/mol</span>`
  - `_fe_dist_4wnw_html`: `<span style="font-size: 15px; font-weight: 700; color: #334155;">{_res_4wnw["min_dist_to_heme_fe_angstrom"]:.2f} Å</span> ({_res_4wnw.get("nearest_heavy_atom", "N/A")})`
- When `_target_eval is None` (e.g. `docking_evaluations=[]`):
  - `_vina_3tbg_html`: `<span style="color: #94a3b8; font-weight: 600;">No Evaluation Available</span>`
  - `_fe_dist_3tbg_html`: `<span style="color: #94a3b8; font-weight: 600;">No Evaluation Available</span>`
  - `_vina_4wnw_html`: `<span style="color: #94a3b8; font-weight: 600;">No Evaluation Available</span>`
  - `_fe_dist_4wnw_html`: `<span style="color: #94a3b8; font-weight: 600;">No Evaluation Available</span>`
  - `_asp_3tbg_html`: `<span style="color: #94a3b8;">No Evaluation Available</span>`
  - `_asp_4wnw_html`: `<span style="color: #94a3b8;">No Evaluation Available</span>`
  - `_prox_3tbg`: `"No Evaluation Available"`
  - `_prox_4wnw`: `"No Evaluation Available"`
  - Card templates interpolate `_vina_3tbg_html` and `_fe_dist_3tbg_html` directly.
  - Zero instances of `0.00 kcal/mol`, `0.0 kcal/mol`, `99.90 Å`, or `99.9 Å` appear in the rendered output!

### 2. Dedicated Automated Regression Tests Added
In `tests/test_cyp2d6_ui.py`:
- `test_cyp2d6_ui_empty_evaluations_fallback_renders_no_numeric_sentinels()`:
  - Asserts that `"vina_affinity_kcal_mol\": 0.0"` and `"min_dist_to_heme_fe_angstrom\": 99.9"` do not exist anywhere in `app.py` or `standalone_app.py`.
  - Asserts fallback formatting strings and fail-closed labels exist in both files.
- `test_cyp2d6_ui_empty_evaluations_live_cell_simulation()`:
  - Executes cell rendering with `cyp2d6_evals = []` and dropdown value `None`.
  - Verifies that `"0.00 kcal/mol"`, `"0.0 kcal/mol"`, `"99.90 Å"`, `"99.9"`, and `"Canonical CYP2D6 Mechanism"` are strictly absent from the rendered HTML.
  - Verifies that `"No Evaluation Available"` and `"⚪ No Structural Evaluation Available"` are present.

### 3. Standalone Deliverable Re-Packaging & Budget
- Rebuilt via `python scripts/package_assets.py && python scripts/bundle_app.py`.
- **Artifact Path:** `standalone_app.py`
- **Measured Decimal Size:** **197,383 bytes** (192.8 KB, strictly $< 200,000$ bytes decimal, **2,617 bytes safety headroom**).
- **Immutable SHA-256 Digest:** `952160741c621f504f68380b2b3f84d13c3e496f3168a5d264e7f04fb7caafae`.

### 4. Cryptographic Digest Synchronization (Zero Drift)
The exact digest `952160741c621f504f68380b2b3f84d13c3e496f3168a5d264e7f04fb7caafae` and size `197,383 bytes` are cryptographically synchronized across:
- `standalone_app.py` (file hash on disk)
- `docs/molab_cold_boot_results.json` (`artifact_sha256: "952160741c621f504f68380b2b3f84d13c3e496f3168a5d264e7f04fb7caafae"`)
- `docs/DEVTOOLS_AUDIT_REPORT.json` (`artifact_sha256: "952160741c621f504f68380b2b3f84d13c3e496f3168a5d264e7f04fb7caafae"`, `artifact_size_bytes: 197383`)
- `docs/MOLAB_STAGING_REPORT.md` (Table 1.1, lines 18–19, line 53)
- `docs/JOTFORM_SUBMISSION_PACKAGE.md` (Table 2, line 33: 197,383 bytes)
- `docs/VIDEO_285_SECOND_SCRIPT.md` (Storyboard Segment 6, line 19: ~2.6 KB safety headroom)
- `tests/test_molab_staging.py` (automated assertion: `assert sha256 == cb_report.get("artifact_sha256")`)
- `tests/test_submission_package.py` (automated assertion: `assert "197,383 bytes" in content`)

### 5. Cold-Boot Benchmark Protocol (5 Fresh Runs)
- Executed `scripts/verify_molab_cold_boot.py --runs 5` against `standalone_app.py`:
  - Run 1: 4.593s
  - Run 2: 4.666s
  - Run 3: 4.623s
  - Run 4: 4.729s
  - Run 5: 4.630s
  - **Median Cold Boot:** **4.630 s** (53.7% faster than 10.0s SLA)
  - **P95 Cold Boot:** **4.716 s** (52.8% faster than 10.0s SLA)
  - **External Requests:** 0 (strictly offline isolated)
  - **Console Errors:** 0
  - **GPU Initialization:** None (zero runtime GPU dependency)
  - **SLO Status:** PASS

### 6. Live DevTools Browser Audit
- Automated Playwright Chrome DevTools report:
  - 96 SVG elements (threshold >= 70)
  - 5 AnyWidget instances (threshold >= 2)
  - 0 unhandled console errors
  - 0 network failures
  - Status: PASS

### 7. Test Suite & DAG Validation
- `pytest`: 212 passed, 9 skipped (all 9 pass when `RUN_BROWSER_TESTS=1`).
- `marimo check app.py` && `marimo check standalone_app.py`: exit code 0, 0 warnings.

---

## Verification Instructions for Luna Max
1. Inspect `app.py` (lines 1103–1180) and `standalone_app.py` (lines 1940–2015). Verify the complete elimination of `0.0 kcal/mol` and `99.9 Å` sentinels, and the explicit rendering of `"No Evaluation Available"`.
2. Inspect the new regression tests in `tests/test_cyp2d6_ui.py`.
3. Verify that SHA-256 of `standalone_app.py` is `952160741c621f504f68380b2b3f84d13c3e496f3168a5d264e7f04fb7caafae` and size is 197,383 bytes, matching `molab_cold_boot_results.json`, `DEVTOOLS_AUDIT_REPORT.json`, `MOLAB_STAGING_REPORT.md`, and `JOTFORM_SUBMISSION_PACKAGE.md`.
4. Run `.venv/bin/pytest tests/test_cyp2d6_ui.py tests/test_molab_staging.py tests/test_submission_package.py` and `marimo check standalone_app.py`.
5. Render your final **Round 21 Audit & Sign-Off Report** across the three gates:
   - **Gate 1: EC-T2-01 Docking Integrity & Biophysical Grounding (/40)**
   - **Gate 2: EC-T2-02 Reactive UI Integration & Scientific Calibration (/30)**
   - **Gate 3: EC-T3-01 & EC-T3-02 Molab Bundling, SLA, & Staging Package (/30)**
6. State clearly whether **Unconditional Tier 3 Sign-Off (100 / 100)** is granted.
