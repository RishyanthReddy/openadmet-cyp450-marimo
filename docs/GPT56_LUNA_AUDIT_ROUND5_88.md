# Comprehensive Final Adversarial Audit Report

### 1. Executive Summary & Calibrated Score

- **Progression:** Baseline (36/100) → Interim (56/100) → Post-Hardening (78/100) → Final Score: **88 / 100**
- **Submission Readiness Verdict:** **REVISION NEEDED (<90)**

The claimed wording, artifact, bundling, provenance-field, and AnyWidget fixes are present. However, two material submission risks remain:

1. The rerunnable docking source still measures all atoms while labeling the result as a heavy-atom distance.
2. Browser tests silently convert live-browser launch failures and assertion failures into cached-report passes.

The prior file [`GPT56_LUNA_FINAL_AUDIT_REPORT.md`](/Users/rishyanthreddy/Desktop/Marimo/docs/GPT56_LUNA_FINAL_AUDIT_REPORT.md:1) actually records **86/100**, rather than 78/100; I used it as the historical prior-audit baseline. No Git metadata is present, so no commit-level diff could be independently reviewed.

Key dimension scores:

- **Scientific & Chemical Truth:** **21/25** (84/100)
- **Data Provenance & MMP Integrity:** **14/15** (93/100)
- **Statistical & Conformal Rigor:** **17/20** (85/100)
- **Architecture, Portability & Bundling:** **19/20** (95/100)
- **AnyWidget Frontend, UI & Accessibility:** **9/10** (90/100)
- **Test Coverage & DevTools Audit:** **8/10** (80/100)

**Total: 88/100**

### 2. Detailed Evaluation by Remediation Dimension

#### 2.1 Scientific & Chemical Truth — 21/25

**Prior status at 78/86:** The previous audits identified blanket clinical-validation wording, ferryl-oxo overclaiming, incorrect sulfur/hydrogen contact interpretation, stale docking records, and undocked compounds in the report.

**Verified remediation:**

- The required Table 1.1 wording is present in [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:251).
- The heading now reads “Curated Reference Set of Documented Literature MBIs” [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:255).
- Tienilic acid reports carbonyl oxygen at 2.20 Å and sulfur at 6.89 Å [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:179).
- The packaged docking artifact contains Tienilic sulfur at 6.89 Å and Raloxifene sulfur at 8.03 Å [`docking_ablation_results.json`](/Users/rishyanthreddy/Desktop/Marimo/data/packaged/docking_ablation_results.json:203).
- The report explicitly qualifies Fe distance as an active-site steric proximity proxy rather than direct Compound I chemistry [`STRETCH_EXPERIMENTS_REPORT.md`](/Users/rishyanthreddy/Desktop/Marimo/docs/STRETCH_EXPERIMENTS_REPORT.md:25).
- The docking table contains the ten current compounds and excludes Mifepristone, Ritonavir, and Troleandomycin. Tienilic and Raloxifene contain the corrected contacts [`STRETCH_EXPERIMENTS_REPORT.md`](/Users/rishyanthreddy/Desktop/Marimo/docs/STRETCH_EXPERIMENTS_REPORT.md:34).
- The ONNX experiment is accurately labeled as a dense-head smoke test on 300-dimensional embeddings [`STRETCH_EXPERIMENTS_REPORT.md`](/Users/rishyanthreddy/Desktop/Marimo/docs/STRETCH_EXPERIMENTS_REPORT.md:53).

**Residual risk:**

The rerunnable source remains scientifically inconsistent with the packaged artifact. In [`spikes/docking_ablation.py`](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:218), every `ATOM`/`HETATM` record is included in the distance calculation; hydrogens are not filtered. The existing PDBQT files independently produce:

- Raloxifene: all-atom minimum **1.612 Å**, heavy-atom minimum **2.244 Å**
- Tienilic acid: all-atom minimum **1.957 Å**, heavy-atom minimum **2.199 Å**

The source then manually inserts corrected heavy-atom fields only for those two compounds [`docking_ablation.py`](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:245). A rerun can therefore regress the packaged `min_dist_to_heme_fe_angstrom` values. The current docking test checks the packaged JSON, not source-to-artifact reproducibility.

The application also retains stronger-than-necessary phrases such as “Inside Catalytic Sphere” and “strike zone” [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:745). The proxy disclaimer helps, but the interface still risks implying catalytic mechanism or covalent inactivation from a single Fe-distance metric.

#### 2.2 Data Provenance & MMP Integrity — 14/15

**Prior status at 78/86:** Heavy-atom delta enforcement, hardcoded OOF cases, and incomplete row-level assay provenance were the principal concerns.

**Verified remediation:**

- The MMP pairing loop enforces `delta_heavy <= 6` [`generate_mmps.py`](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_mmps.py:97).
- RDKit `rdMMPA.FragmentMol` uses its standard non-ring MMP fragmentation pattern.
- The reproducibility test regenerates and compares all 34 packaged pairs [`test_mmps.py`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_mmps.py:90).
- The packaged catalog contains exactly 34 pairs: 25 CYP3A4 and 9 CYP2D6.
- Act 4 displays assay ID, source dataset, measurement type, uncertainty, and replicate summary [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:916).
- OOF cases are dynamically loaded [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:949).
- All four OOF records contain the requested molecule, source-row, model-version, assay, fold, label, prediction, dataset, and rationale fields [`oof_error_cases.json`](/Users/rishyanthreddy/Desktop/Marimo/data/packaged/oof_error_cases.json:17).

**Residual risk:**

The OOF JSON is now field-complete, but the identifiers are not independently linked to a raw prediction table or model-run artifact. The `source_row_id` values have a constructed format such as `OCTANT_ROW_OCNT-..._CV_FOLD_0`. Dynamic loading improves architecture, but does not itself establish empirical traceability.

MMP provenance is also coarse: the generator assigns constant assay metadata and does not preserve an emitted source-row identifier, although it retains an internal row index during extraction [`generate_mmps.py`](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_mmps.py:65).

#### 2.3 Statistical & Conformal Rigor — 17/20

**Prior status at 78/86:** The prior implementation overstated FDR control, had alpha-range inconsistencies, and lacked sufficient limitations language.

**Verified remediation:**

- The narrative and slider both use α ∈ [0.05, 0.20], default 0.10 [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1053).
- The badge now says “Observed Screening FDP Diagnostic” [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1134).
- The limitations explicitly mention exchangeability, density-ratio assumptions, and out-of-distribution shrinkage [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1193).
- A real BH step-up selector is implemented [`txconformal_selector.py`](/Users/rishyanthreddy/Desktop/Marimo/models/txconformal_selector.py:54).
- Packaged results include both `empirical_fdp_controlled` and `fdr_controlled`, plus an explicit diagnostic note [`txconformal_selection_results.json`](/Users/rishyanthreddy/Desktop/Marimo/data/packaged/txconformal_selection_results.json:111).

**Residual risk:**

- `fdr_controlled` remains a potentially misleading field name for a realized empirical FDP diagnostic.
- The 250 runs repeatedly resample the same held-out test labels and p-values [`txconformal_selector.py`](/Users/rishyanthreddy/Desktop/Marimo/models/txconformal_selector.py:274). This is a useful retrospective resampling diagnostic, not 250 independent prospective screens and not a finite-sample guarantee.
- Act 5 applies BH dynamically to `test_candidates_sample`, which contains 100 candidates, while the statistical artifact reports a 703-compound test set [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1083).
- The displayed FDP metric is selected from alpha buckets rather than recalculated continuously for every slider value [`app.py`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1093). At α = 0.08, for example, the card can show the α = 0.10 diagnostic while the shortlist is computed at 0.08.

#### 2.4 Architecture, Portability & Bundling — 19/20

**Prior status at 78/86:** The bundle duplicated implementation logic and had weaker path portability.

**Verified remediation:**

- Layout-engine extraction is dynamic [`bundle_app.py`](/Users/rishyanthreddy/Desktop/Marimo/scripts/bundle_app.py:47).
- Conformal-selector extraction is dynamic.
- `load_oof_error_cases()` is inlined into the first standalone cell.
- The expected SHA-256 matches `models.embedded_assets.PARQUET_EXPECTED_SHA256` and the intended packaged file `data/packaged/cyp_tdi_curated.parquet`.
- `standalone_app.py` contains no project-local `models` or `widgets` imports.
- `standalone_app.py` imports successfully.
- Both Marimo checks passed with exit code 0 and no output.

**Residual risk:**

- Standalone dependencies are lower-bounded but unpinned, so the bundle is portable but not fully reproducible across future environments.
- The workspace has no Git metadata, preventing independent commit/diff provenance verification.
- Generated-file drift remains possible if source code changes without regenerating `standalone_app.py`.

#### 2.5 AnyWidget Frontend, UI & Accessibility — 9/10

**Prior status at 78/86:** Gradient-ID collisions, clipped tooltips, missing ARIA linkage, incomplete selection state, and listener cleanup were identified.

**Verified remediation:**

- Gradient IDs are scoped with a per-instance identifier [`bioactivation_tracer.js`](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:176).
- Atom nodes use scoped `aria-describedby` links [`bioactivation_tracer.js`](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:371).
- Selected atoms render a dashed selection ring [`bioactivation_tracer.js`](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:381).
- Reactive `selected_atom_idx` listeners and cleanup are present [`bioactivation_tracer.js`](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:453).
- `.bat-container` uses `overflow: visible` [`bioactivation_tracer.css`](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.css:52).

**Residual risk:**

- Tooltip and badge content is assembled through `innerHTML` using metadata values [`bioactivation_tracer.js`](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:94). Current values are locally generated, but escaping or `textContent` would be safer.
- The invalid-layout path replaces the tooltip DOM while retaining its old reference, potentially breaking later ARIA links.
- The widget test is a fake DOM/model simulation rather than a real browser test.

#### 2.6 Test Coverage & DevTools Audit — 8/10

**Verified execution:**

- `./.venv/bin/marimo check app.py`: exit 0, empty stdout/stderr.
- `./.venv/bin/marimo check standalone_app.py`: exit 0, empty stdout/stderr.
- `./.venv/bin/python -m pytest tests/ -v`: **136 passed, 0 failed**.
- The checked-in report is internally consistent: status `PASS`, 340 requests, zero console errors, zero network failures, 80 SVGs, and 4 AnyWidget instances [`DEVTOOLS_AUDIT_REPORT.json`](/Users/rishyanthreddy/Desktop/Marimo/docs/DEVTOOLS_AUDIT_REPORT.json:1).

**Critical qualification:**

A direct Playwright launch of the installed Chrome binary failed in this sandbox with `TargetClosedError`. The two browser test suites catch broad `Exception` blocks and substitute the checked-in report. In [`test_devtools_audit.py`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_devtools_audit.py:203), the fallback returns synthetic values including HTTP 200, all five Acts present, and default control counts. The seam test has the same broad fallback [`test_phase3_seam.py`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_phase3_seam.py:179).

Therefore, the 136-test pass is real, but it does not prove that a live browser run passed in this audit. It proves that the source checks pass and that the cached report satisfies the fallback assertions.

### 3. Verification of Zero False Claims & Zero Mocks

A literal zero-mock/zero-simulation sign-off is **not supportable**.

Positive findings:

- The active app and standalone bundle no longer contain the old “Clinically Validated,” “Empirical FDR Controlled,” or “guarantees valid coverage” wording.
- Core datasets, OpenADMET splits, RDKit MMP extraction, packaged model outputs, and docking artifacts are real repository artifacts.
- The MMP generator reproduces all 34 packaged pair identities.
- Literature InChIKeys and schema checks pass.

Negative findings:

- [`test_anywidget_contract.py`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_anywidget_contract.py:70) explicitly defines `HeadlessDOMNode` and `HeadlessWidgetModelTraitletProxy`, then reports “Simulated DOM render passed.”
- The ONNX experiment intentionally uses `torch.randn` embedding vectors, which is acceptable for an explicitly labeled smoke test but is still synthetic benchmark input.
- Browser fallbacks can report a successful audit without a live browser execution.
- OOF cases are packaged JSON records, not independently regenerated during this audit from a prediction table.
- `TODO.md` still contains unqualified historical phrases such as “catalytic reaction sphere” and “empirical FDR control” [`TODO.md`](/Users/rishyanthreddy/Desktop/Marimo/TODO.md:501). Historical audit and planning documents also retain obsolete terminology. These are not active UI logic, but they prevent a clean repository-wide zero-claims assertion.

### 4. Code Quality & Architectural Health

The Marimo DAG is healthy: both application files pass `marimo check`, syntax compilation passes, and standalone import succeeds.

The standalone bundle is genuinely path-decoupled and contains embedded fallback assets. Dynamic source extraction and SHA validation are well designed. AnyWidget lifecycle cleanup is implemented correctly for normal render paths.

The main architectural weaknesses are evidence integrity rather than DAG correctness:

- Docking source and packaged results are not fully reproducible because of the unfiltered hydrogen-distance calculation.
- Browser verification is not fail-closed.
- The headless DOM test validates only a narrow mocked contract.
- Dependency versions are not pinned.
- No Git metadata is available for change provenance.

### 5. Final Recommendation & Sign-Off

**Final sign-off: withheld.** The repository is close, but the evidence does not justify a 90+ submission-grade score.

Before publication or competition submission:

1. Filter hydrogens in the docking parser, derive all contact fields from parsed poses, regenerate the package/report, and add a source-to-artifact regression test.
2. Make browser tests fail closed on launch, navigation, or DOM assertion errors. Treat cached DevTools JSON as an explicitly labeled offline check, not a transparent substitute.
3. Run a fresh permitted live-browser audit and record execution mode, timestamp, browser version, and failure provenance.
4. Label the 100-row Act 5 view as a display sample or apply the method to the full 703-compound test universe.
5. Rename or clearly scope `fdr_controlled`, align alpha diagnostics with the actual slider value, and clean stale repository-wide terminology.

Current calibrated status: **88/100 — strong near-submission candidate, but revision is required for defensible submission-grade sign-off.**