# Comprehensive Final Adversarial Audit Report

### 1. Executive Summary & Calibrated Score

- **Progression:** 36 → 56 → 78 → 86 → 88 → Final: **89 / 100**
- **Submission Readiness Verdict:** **REVISION NEEDED (<90)**

The main remediation is real and materially improves the project. However, two submission-grade claims remain unverified or overstated:

1. The full suite collected 139 tests but produced **131 passed, 8 skipped**, not 139 passed.
2. Live Chrome execution failed with `TargetClosedError`; the checked-in DevTools report is therefore offline evidence, not independently reproduced live evidence.

Git metadata is absent, so commit-level diff provenance could not be reviewed.

Key dimension scores:

- **Scientific & Chemical Truth:** 23/25 pts — 92/100
- **Data Provenance & MMP Integrity:** 14/15 pts — 93/100
- **Statistical & Conformal Rigor:** 17/20 pts — 85/100
- **Architecture, Portability & Bundling:** 19/20 pts — 95/100
- **AnyWidget Frontend, UI & Accessibility:** 9/10 pts — 90/100
- **Test Coverage & DevTools Audit:** 7/10 pts — 70/100

**Total: 89/100**

### 2. Detailed Evaluation by Remediation Dimension

#### 2.1 Scientific & Chemical Truth — 23/25

**Prior status at 86/88:** stale hydrogen-inclusive docking logic, incorrect contact claims, overreaching ferryl-oxo language, and undocked compounds in the report.

**Verified remediation:**

- UI wording is corrected in [app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:104), [app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:178), and [app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:251).
- Tienilic acid and Raloxifene values are correct.
- The parser now separates hydrogens from heavy atoms in [docking_ablation.py](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:226).
- The report qualifies Fe distance as an active-site steric proxy in [STRETCH_EXPERIMENTS_REPORT.md](/Users/rishyanthreddy/Desktop/Marimo/docs/STRETCH_EXPERIMENTS_REPORT.md:25).
- Table 2.1 contains the ten docked compounds and the corrected Tienilic/Raloxifene contacts.
- The ONNX experiment is accurately labeled as a dense-head smoke test.

I independently parsed all ten raw 2V0M PDBQT files. Heavy-atom distances, sulfur distances, and Vina affinities match the packaged artifact to stored precision, including Tienilic acid 2.19/6.90 Å and Raloxifene 2.23/8.02 Å.

**Residual risk:**

- `test_pdbqt_source_to_artifact_reproducibility()` parses raw PDBQT files but compares only two hardcoded distances; it does not load or compare `docking_ablation_results.json` ([test_docking_ablation.py](/Users/rishyanthreddy/Desktop/Marimo/tests/test_docking_ablation.py:91)).
- The report generator still uses manual name branches for “Carbonyl O” and “Phenolic O” ([docking_ablation.py](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:485)).
- Legacy `reaction_sphere` field names and stale “strike zone”/“catalytic reaction sphere” terminology remain in supporting files.

#### 2.2 Data Provenance & MMP Integrity — 14/15

**Prior status at 86/88:** missing heavy-atom enforcement, hardcoded OOF cases, and incomplete provenance display.

**Verified remediation:**

- `delta_heavy <= 6` is enforced in [generate_mmps.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_mmps.py:97).
- Act 4 dynamically loads OOF records from [app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:949).
- All four OOF cases contain the required provenance fields in [oof_error_cases.json](/Users/rishyanthreddy/Desktop/Marimo/data/packaged/oof_error_cases.json:1).
- The generator reproduces all 34 MMPs. I independently compared the complete normalized generated/package dictionaries, excluding only the generated `mmp_id`; there were zero differences.

**Residual risk:**

- MMP records lack actual source-row identifiers; assay metadata is inserted as constant labels in [generate_mmps.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_mmps.py:78).
- OOF `source_row_id` values are structured identifiers but are not linked to a separate raw prediction-run artifact.
- The UI still provides fallback provenance values if metadata is absent.

#### 2.3 Statistical & Conformal Rigor — 17/20

**Prior status at 86/88:** FDR overclaiming, alpha-range mismatch, and insufficient limitations language.

**Verified remediation:**

- Slider and narrative agree on α ∈ [0.05, 0.20] ([app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1068)).
- The badge now says “Observed Screening FDP Diagnostic” ([app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1125)).
- The limitations note correctly states exchangeability and density-ratio assumptions ([app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1184)).
- Dynamic BH selection is implemented in [txconformal_selector.py](/Users/rishyanthreddy/Desktop/Marimo/models/txconformal_selector.py:54).
- Monte Carlo summaries contain diagnostic flags and notes in [txconformal_selection_results.json](/Users/rishyanthreddy/Desktop/Marimo/data/packaged/txconformal_selection_results.json:99).

**Residual risk:**

- `fdr_controlled` remains a potentially misleading field name for an empirical FDP diagnostic.
- The packaged full-test evaluation lacks `empirical_fdp_diagnostic_passed` and the explicit diagnostic note, even though the source generator now emits them ([txconformal_selector.py](/Users/rishyanthreddy/Desktop/Marimo/models/txconformal_selector.py:252)).
- The 250 Monte Carlo runs repeatedly resample the same 703 test labels and p-values; they are retrospective resampling diagnostics, not independent prospective screens.
- Intermediate slider values display the nearest precomputed alpha benchmark rather than a newly recomputed FDP estimate.

#### 2.4 Architecture, Portability & Bundling — 19/20

**Prior status at 86/88:** duplicated bundle logic and weaker path portability.

**Verified remediation:**

- Layout and conformal code are dynamically extracted in [bundle_app.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/bundle_app.py:47).
- OOF loading is inlined and returned from the standalone first cell ([bundle_app.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/bundle_app.py:286)).
- Parquet SHA-256 matches exactly:

  `2f56102a498419fdd0937e3a0940dcf392345c513993f35e1143fd11c679f6e4`

- `app.py` and `standalone_app.py` both import successfully.
- Both Marimo checks exit 0 with empty output.
- `standalone_app.py` contains no project-local `models` or `widgets` imports.

**Residual risk:**

- Dependencies are lower-bounded rather than pinned.
- Generated-file drift remains possible.
- No Git metadata is available.
- Some development scripts still contain machine-specific absolute paths, although the application bundle itself is path-decoupled.

#### 2.5 AnyWidget Frontend, UI & Accessibility — 9/10

**Prior status at 86/88:** gradient collisions, clipped tooltips, missing ARIA linkage, and incomplete selection/lifecycle handling.

**Verified remediation:**

- Instance-scoped gradient IDs are implemented in [bioactivation_tracer.js](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:176).
- Atom nodes use scoped `aria-describedby` ([bioactivation_tracer.js](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:371)).
- Selected atoms receive a dashed visual ring ([bioactivation_tracer.js](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:375)).
- Traitlet listeners and cleanup are present ([bioactivation_tracer.js](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:452)).
- `.bat-container` uses `overflow: visible` ([bioactivation_tracer.css](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.css:52)).

**Residual risk:**

- Tooltip content uses `innerHTML` with metadata values ([bioactivation_tracer.js](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:94)).
- The invalid-layout path can replace the tooltip DOM while retaining its old reference.
- The Node test remains a simulated DOM contract test, not a real browser lifecycle test.

#### 2.6 Test Coverage & DevTools Audit — 7/10

**Verified execution:**

- `marimo check app.py`: exit 0, empty output.
- `marimo check standalone_app.py`: exit 0, empty output.
- `app` and `standalone_app` imports: successful.
- `pytest tests/ -v`: **139 collected, 131 passed, 8 skipped, exit 0**.
- The eight skips are live-browser tests skipped after Chrome launch failed with `TargetClosedError`.
- The checked-in report is internally valid: `PASS`, zero console errors, zero network failures, 80 SVGs, and 4 AnyWidget instances ([DEVTOOLS_AUDIT_REPORT.json](/Users/rishyanthreddy/Desktop/Marimo/docs/DEVTOOLS_AUDIT_REPORT.json:1)).

**Important qualification:**

The live browser assertions are outside the launch `try/except`, so post-launch assertion failures would fail correctly. However, launch failure still produces skipped tests, meaning the suite can exit successfully without live browser verification.

The artifact records **342** network requests, not the claimed 340.

### 3. Verification of Zero False Claims & Zero Mocks

A literal repo-wide zero-mock/zero-simulation sign-off is not supportable.

Positive findings:

- Primary packaged datasets and docking artifacts are real repository artifacts.
- Literature entries have citations and PubMed identifiers.
- MMP transformations derive from RDKit/OpenADMET data.
- OOF cases are dynamically loaded and provenance-rich.
- Submission-facing UI no longer uses the old “Clinically Validated” or “Empirical FDR Controlled” badges.

Residual violations:

- [test_anywidget_contract.py](/Users/rishyanthreddy/Desktop/Marimo/tests/test_anywidget_contract.py:82) explicitly defines `HeadlessDOMNode` and a simulated traitlet proxy.
- The ONNX smoke test uses synthetic 300-dimensional vectors.
- The conformal study intentionally performs Monte Carlo resampling.
- [models/embedded_assets.py](/Users/rishyanthreddy/Desktop/Marimo/models/embedded_assets.py:10) and [scripts/package_assets.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/package_assets.py:342) retain “strike zone” terminology.
- [TODO.md](/Users/rishyanthreddy/Desktop/Marimo/TODO.md:750) retains “catalytic reaction sphere” language and [TODO.md](/Users/rishyanthreddy/Desktop/Marimo/TODO.md:937) retains unqualified empirical FDR language.

These are mostly test, planning, or historical artifacts rather than active UI claims, but they prevent a literal repository-wide zero-claims assertion.

### 4. Code Quality & Architectural Health

The Marimo DAG is healthy: both files pass static checks with no stderr, and both import cleanly.

The standalone bundle is genuinely self-contained, dynamically sourced, SHA-validated, and free of local project imports. AnyWidget normal-path cleanup and DOM scoping are well implemented.

The remaining weaknesses are evidence-integrity issues:

- The docking reproducibility test is weaker than its name implies.
- The packaged conformal artifact is slightly behind the current generator schema.
- Browser health is not live-verified in this environment.
- Simulated frontend and synthetic ONNX tests must remain explicitly scoped as smoke tests.

An Antigravity second-pass review was attempted, but the MCP call was cancelled and direct CLI execution was blocked by sandbox restrictions on CLI log writes and localhost binding. No delegated conclusions were used in this score.

### 5. Final Recommendation & Sign-Off

**Final recommendation: REVISION NEEDED — 89/100.**

The project is a strong near-submission candidate, but I would withhold 90+ sign-off until:

1. The docking test compares all parsed raw fields directly against the packaged artifact.
2. The packaged conformal full-test records are regenerated with the new diagnostic fields.
3. Live Chrome tests fail rather than skip on launch failure, followed by a fresh permitted live audit.
4. Stale “reaction sphere,” “strike zone,” and unqualified FDR terminology are removed or clearly marked historical.
5. MMP source-row provenance is made genuinely row-level rather than constant metadata.

