# Comprehensive Final Adversarial Audit Report

### 1. Executive Summary & Calibrated Score

- **Progression:** Baseline (36/100) → Interim (56/100) → Post-Hardening (78/100) → Final Score: **86 / 100**
- **Submission Readiness Verdict:** **REVISION NEEDED (<90)**

The requested remediation is genuinely present across the primary application, packaged artifacts, bundle generator, standalone app, and widget implementation. However, submission-grade sign-off is blocked by stale rerunnable docking source, synthetic/mock validation paths, missing explicit network-failure evidence, and a non-clean 136-test run.

- **Scientific & Chemical Truth:** 21/25
- **Data Provenance & MMP Integrity:** 14/15
- **Statistical & Conformal Rigor:** 17/20
- **Architecture, Portability & Bundling:** 19/20
- **AnyWidget Frontend, UI & Accessibility:** 9/10
- **Test Coverage & DevTools Audit:** 6/10

Process note: Antigravity health check passed, but its delegated review was blocked by sandbox restrictions on CLI log/crash writes and localhost binding. The findings below are based on direct repository inspection and executed checks.

### 2. Detailed Evaluation by Remediation Dimension

#### 2.1 Scientific & Chemical Truth — 21/25

**Status at 78/100:** Clinical-validation wording, ferryl-oxo overclaims, stale contact distances, and undocked compounds remained.

**Verified remediation:**

- Table 1.1 now uses the required documented-literature wording in [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:249).
- Tienilic acid now reports MODEL 1 carbonyl oxygen at 2.20 Å and sulfur at 6.89 Å in [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:179).
- The cross-isoform note now states “10 curated documented literature MBIs” in [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:775).
- The packaged Tienilic artifact contains `reactive_sulfur_dist_angstrom: 6.89` under the 2V0M result [`docking_ablation_results.json`](/Users/rishyanthreddy/Desktop/Marimo/data/packaged/docking_ablation_results.json:201).
- The stretch report explicitly describes Fe distance as an active-site steric proximity proxy, not direct ferryl-oxo observation [`STRETCH_EXPERIMENTS_REPORT.md`](/Users/rishyanthreddy/Desktop/Marimo/docs/STRETCH_EXPERIMENTS_REPORT.md:25).
- Table 2.1 contains only docked compounds and reports the corrected Tienilic/Raloxifene contacts [`STRETCH_EXPERIMENTS_REPORT.md`](/Users/rishyanthreddy/Desktop/Marimo/docs/STRETCH_EXPERIMENTS_REPORT.md:34).
- The ONNX experiment is accurately labeled as a dense-head smoke test on 300-dimensional embedding vectors [`STRETCH_EXPERIMENTS_REPORT.md`](/Users/rishyanthreddy/Desktop/Marimo/docs/STRETCH_EXPERIMENTS_REPORT.md:53).

**Residual risk:**

- The UI heading still says “Validated Literature MBIs” [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:255), despite mixed evidence levels including in-vitro/reference entries.
- The rerunnable source generator remains stale: it still emits unqualified ferryl-oxo/reaction-sphere claims, names Mifepristone/Ritonavir/Troleandomycin, and uses `torch.randn` dense-head inputs [`spikes/docking_ablation.py`](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:246). It also does not generate the typed sulfur-contact fields now present in the packaged artifact. Re-running it could regress the corrected report and JSON.

#### 2.2 Data Provenance & MMP Integrity — 14/15

**Status at 78/100:** The heavy-atom constraint was documented but not enforced; OOF cases were hardcoded; provenance was incomplete in the UI.

**Verified remediation:**

- The generator now enforces `delta_heavy <= 6` in the pairing loop [`generate_mmps.py`](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_mmps.py:97).
- The reproducibility test passed and compares all 34 regenerated pair identities [`test_mmps.py`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_mmps.py:90).
- The packaged artifact contains 34 pairs: 25 CYP3A4 and 9 CYP2D6.
- All pairs contain assay ID, source dataset, measurement type, uncertainty, and replicate summary.
- Act 4 surfaces row-level assay provenance [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:916).
- OOF cases are dynamically loaded rather than hardcoded [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:948), and all four packaged cases contain the required fields [`oof_error_cases.json`](/Users/rishyanthreddy/Desktop/Marimo/data/packaged/oof_error_cases.json:1).

**Residual risk:** OOF provenance still lacks an explicit model version/source-row identifier, and the MMP UI uses fallback defaults if row metadata is missing.

#### 2.3 Statistical & Conformal Rigor — 17/20

**Status at 78/100:** The UI overstated empirical FDR control, the alpha narrative conflicted with the slider, and limitations overclaimed guarantees.

**Verified remediation:**

- Target range and slider are aligned at α ∈ [0.05, 0.20] [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1053).
- The badge now says “Observed Screening FDP Diagnostic” [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1134).
- The limitations note now states exchangeability and density-ratio assumptions and explains OOD shrinkage [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1193).
- The canonical BH selector is implemented in [`txconformal_selector.py`](/Users/rishyanthreddy/Desktop/Marimo/models/txconformal_selector.py:54).
- Packaged results contain both `empirical_fdp_controlled` and `fdr_controlled`, with explicit empirical diagnostic notes [`txconformal_selector.py`](/Users/rishyanthreddy/Desktop/Marimo/models/txconformal_selector.py:310).
- The 100-candidate display sample contains no ground-truth labels.

**Residual risk:**

- `fdr_controlled` remains a potentially misleading field name even when paired with empirical diagnostics.
- The 250-run evaluation repeatedly resamples the same held-out test labels and p-values [`txconformal_selector.py`](/Users/rishyanthreddy/Desktop/Marimo/models/txconformal_selector.py:266); it is an empirical resampling diagnostic, not a finite-sample guarantee.
- Act 5 displays alpha-bucketed Monte Carlo summaries rather than recalculating the metric continuously for every slider value [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1093).

#### 2.4 Architecture, Portability & Bundling — 19/20

**Status at 78/100:** The bundle duplicated implementation logic and lacked reliable dynamic extraction.

**Verified remediation:**

- Layout and conformal implementations are dynamically extracted [`bundle_app.py`](/Users/rishyanthreddy/Desktop/Marimo/scripts/bundle_app.py:47).
- `load_oof_error_cases()` is inlined and returned from the first standalone cell [`bundle_app.py`](/Users/rishyanthreddy/Desktop/Marimo/scripts/bundle_app.py:286).
- Parquet SHA-256 parity was verified.
- Bundle generation completed successfully with 100 fallback rows, 10 literature MBIs, and 34 MMPs.
- `standalone_app.py` imports cleanly and contains no project-local `models` or `widgets` imports.
- Both Marimo checks completed with exit code 0 and no emitted output.

**Residual risk:** The project has no Git metadata in this environment, so commit-level provenance and diff review could not be independently established. The standalone file also depends on its declared Python packages, although it is correctly single-file and path-decoupled.

#### 2.5 AnyWidget Frontend, UI & Accessibility — 9/10

**Status at 78/100:** Gradient IDs collided across instances, overflow clipped tooltips, ARIA linkage and selected-state rendering were incomplete.

**Verified remediation:**

- Gradient IDs are instance-scoped [`bioactivation_tracer.js`](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:176).
- Atom nodes link to the scoped tooltip via `aria-describedby` [`bioactivation_tracer.js`](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:371).
- Selected atoms receive a dashed visual ring [`bioactivation_tracer.js`](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:375).
- Traitlet listeners and cleanup are implemented [`bioactivation_tracer.js`](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:452).
- `.bat-container` uses `overflow: visible` [`bioactivation_tracer.css`](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.css:46).

**Residual risk:** Tooltip content is assembled with `innerHTML`; currently trusted local metadata is safe, but future user-controlled metadata would require sanitization.

#### 2.6 Test Coverage & DevTools Audit — 6/10

**Verified runtime results:**

- `marimo check app.py`: exit 0, no output.
- `marimo check standalone_app.py`: exit 0, no output.
- Direct `standalone_app` import: exit 0.
- `pytest tests/ -v`: 136 collected, **128 passed, 1 failed, 7 errors**.
- The eight non-passing tests fail during Chrome/Playwright startup with `TargetClosedError`, SIGABRT, and EPERM process termination. They do not provide a successful live-browser verification in this environment.

The checked-in DevTools artifact reports `PASS`, 340 network requests, and zero unhandled console errors [`DEVTOOLS_AUDIT_REPORT.json`](/Users/rishyanthreddy/Desktop/Marimo/docs/DEVTOOLS_AUDIT_REPORT.json:1). However, it does not persist a `network_failures` field. The report writer computes network failures but drops them before writing the official JSON [`test_devtools_audit.py`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_devtools_audit.py:162).

### 3. Verification of Zero False Claims & Zero Mocks

The literal repo-wide requirement is **not satisfied**.

Positive findings:

- No current “Clinically Validated,” “Empirical FDR Controlled,” or guarantee language remains in the submission-facing app or regenerated standalone bundle.
- The current stretch report is appropriately qualified.
- MMPs use OpenADMET provenance and observed label shifts.
- OOF cases are packaged and dynamically loaded.
- Conformal candidate displays hide ground-truth labels.

Residual violations:

- [`spikes/docking_ablation.py`](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:427) still contains old ferryl-oxo/reaction-sphere claims and references compounds removed from the corrected report.
- The ONNX generator and test use random synthetic embedding tensors [`spikes/docking_ablation.py`](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:253), [`test_docking_ablation.py`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_docking_ablation.py:64). The final report labels this honestly as a smoke test, but it is not real molecular graph inference.
- The AnyWidget test suite explicitly uses `MockElement`, `MockModel`, and simulated DOM rendering [`test_anywidget_contract.py`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_anywidget_contract.py:70).
- The conformal evaluation explicitly performs Monte Carlo resampling [`txconformal_selector.py`](/Users/rishyanthreddy/Desktop/Marimo/models/txconformal_selector.py:266).
- `TODO.md` and historical audit documents retain stale “provable” or “strict FDR” language, including [`TODO.md`](/Users/rishyanthreddy/Desktop/Marimo/TODO.md:792). These are historical/planning artifacts rather than current UI claims, but they should be removed or clearly marked before submission.

### 4. Code Quality & Architectural Health

- Marimo DAG integrity is verified for both application files.
- Standalone bundling is dynamically sourced and path-decoupled.
- Parquet hash validation and fallback loading are functional.
- AnyWidget lifecycle cleanup, event unsubscription, DOM scoping, and accessibility attributes are implemented.
- The main weakness is source-of-truth drift: the corrected packaged docking artifact is not reproducibly generated by the current docking spike source.
- Browser-level lifecycle behavior remains unverified in this environment despite passing simulated DOM tests.

### 5. Final Recommendation & Sign-Off

**Final recommendation: REVISION NEEDED — 86/100.**

The primary application is substantially improved and close to submission quality, but I cannot provide a 90+ sign-off until:

- `spikes/docking_ablation.py` is updated to generate the corrected scientific report and typed contact fields.
- Synthetic ONNX and mock-DOM paths are explicitly scoped as smoke tests or replaced with real graph-level validation.
- Stale TODO/source claims are removed or marked historical.
- A permitted environment produces a clean 136/136 test run and fresh browser audit.
- `network_failures: []` is persisted in the DevTools artifact alongside the PASS status.