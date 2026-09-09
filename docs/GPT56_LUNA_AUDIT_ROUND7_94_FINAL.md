# Comprehensive Final Adversarial Audit Report

### 1. Executive Summary & Calibrated Score

- **Progression:** 36 → 56 → 78 → 86 → 88 → 89 → Final Score: **94 / 100**
- **Submission Readiness Verdict:** **SUBMISSION GRADE (90+)**

All five Round 6 acceptance gates are functionally satisfied. The remaining deductions are limited to test-strength gaps, legacy terminology/schema names, simulated AnyWidget coverage, and absent Git metadata.

Key dimension scores:

- **Scientific & Chemical Truth:** 24/25 pts
- **Data Provenance & MMP Integrity:** 15/15 pts
- **Statistical & Conformal Rigor:** 18/20 pts
- **Architecture, Portability & Bundling:** 19/20 pts
- **AnyWidget Frontend, UI & Accessibility:** 9/10 pts
- **Test Coverage & DevTools Audit:** 9/10 pts

**Total: 94/100**

### 2. Detailed Evaluation of the 5 Round 6 Remediation Items

#### 1. Docking reproducibility and dynamic reporting — PASS

[`tests/test_docking_ablation.py:92`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_docking_ablation.py:92) loads the packaged artifact, loops through all 10 compounds and both `2V0M`/`1TQN` receptors, and directly parses raw PDBQT affinities, heavy-atom distances, and sulfur distances.

Verified command:

```text
pytest tests/test_docking_ablation.py -v
5 passed in 0.11s
```

[`spikes/docking_ablation.py:476`](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:476) derives table labels from `nearest_heavy_atom` and `reactive_sulfur_dist_angstrom`; no compound-name conditional branches remain. The regenerated report contains all 10 compounds and dynamic contact labels.

My independent parser additionally checked 180 derived fields across 20 raw poses, including mean distances, nearest atom labels, hydrogen distances, sulfur distances, and boolean proximity fields: **0 mismatches**.

Caveat: the unit test itself asserts only the core affinity/heavy-distance/sulfur fields, not every derived JSON field. The artifact is correct, but the test could be made genuinely exhaustive.

#### 2. Packaged conformal diagnostic fields — PASS

[`models/txconformal_selector.py:230`](/Users/rishyanthreddy/Desktop/Marimo/models/txconformal_selector.py:230) now emits `empirical_fdp_diagnostic_passed` and `diagnostic_note` for every full-test evaluation.

The packaged JSON contains:

- 4 alpha levels
- 2 methods per alpha
- 8 diagnostic records
- 8/8 diagnostic flags `true`
- 8/8 notes referencing the 703-compound holdout

```text
pytest tests/test_txconformal.py -v
4 passed in 0.69s
```

The UI correctly uses “Observed Screening FDP Diagnostic” rather than claiming unconditional statistical guarantees at [`app.py:1127`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1127).

Residual issue: legacy `fdr_controlled` field names remain in the model and packaged artifact, although the user-facing interpretation is now appropriately qualified.

#### 3. Fail-closed live browser tests — PASS

No `pytest.skip` remains in either browser test module. Chrome launch occurs outside the assertion-handling blocks at [`tests/test_phase3_seam.py:138`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_phase3_seam.py:138) and [`tests/test_devtools_audit.py:70`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_devtools_audit.py:70), so launch failures propagate as test failures.

Verified command:

```text
pytest tests/test_phase3_seam.py tests/test_devtools_audit.py -v
17 passed in 13.03s
```

The live audit produced:

- 340 network requests
- 0 console errors
- 0 network failures
- 80 SVGs
- 4 AnyWidget instances
- `audit_status: PASS`

Evidence: [`docs/DEVTOOLS_AUDIT_REPORT.json`](/Users/rishyanthreddy/Desktop/Marimo/docs/DEVTOOLS_AUDIT_REPORT.json:1).

#### 4. Supporting terminology cleanup — PASS for active runtime, qualified repository-wide

The requested active-code cleanup is present:

- [`models/embedded_assets.py:10`](/Users/rishyanthreddy/Desktop/Marimo/models/embedded_assets.py:10) uses “active-site steric proximity”.
- [`scripts/package_assets.py`](/Users/rishyanthreddy/Desktop/Marimo/scripts/package_assets.py) contains no “strike zone”.
- The new `in_active_site_steric_proximity_le_5A` field is present in the docking artifact.
- The historical alias is explicitly marked at [`spikes/docking_ablation.py:274`](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:274).

However, a literal repository-wide search still finds “strike zone” in historical audit reports and the remediation prompt. `TODO.md` also retains older FDR terminology in planning/history sections. These are not active submission UI claims, but they prevent a literal zero-stale-terminology assertion.

#### 5. Row-level MMP provenance — PASS

[`scripts/generate_mmps.py:63`](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_mmps.py:63) extracts direct and TDI pIC50 values from the source parquet and propagates them per molecule at [`scripts/generate_mmps.py:130`](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_mmps.py:130).

The artifact contains:

- 34 MMP pairs
- 68 molecule-level provenance records
- Unique `source_row_id` values
- `assay_id`
- `direct_pic50`
- `tdi_pic50`
- `pic50_shift`

The Act 4 card displays both rows and shifts at [`app.py:916`](/Users/rishyanthreddy/Desktop/Marimo/app.py:916).

```text
pytest tests/test_mmps.py -v
4 passed in 7.10s
```

Independent source reconciliation checked all 68 records against `cyp_splits.parquet`: **0 mismatches**. Embedded assets and standalone assets also match the packaged MMP JSON exactly.

### 3. Verification of Zero False Claims & Real Empirical Evidence

The submission-facing evidence is real and reproducible:

- Raw PDBQT files were parsed directly.
- Docking artifacts match raw coordinates and affinities.
- MMP measurements map to source parquet rows.
- Conformal diagnostics use the actual 703-compound holdout.
- Browser metrics were reproduced in live native Chrome.
- No production data path relies on fabricated mock records.

Important qualifications remain:

- The ONNX experiment is explicitly a dense-head smoke test using synthetic 300-dimensional inputs.
- The AnyWidget contract test uses a simulated DOM, although live Chrome coverage now supplements it.
- Monte Carlo results are retrospective resampling diagnostics, not independent prospective trials.
- Legacy `fdr_controlled` names remain in statistical artifacts.
- Historical reports retain obsolete terminology.

Therefore, the correct conclusion is: **no material false submission claim was found in the active application or packaged evidence**, but a literal repository-wide zero-simulation/zero-legacy-terminology claim would be overstated.

### 4. Code Quality & Architectural Health

Both DAG checks pass cleanly:

```text
marimo check app.py
exit 0, empty stderr

marimo check standalone_app.py
exit 0, empty stderr
```

Full verification:

```text
pytest tests/ -q
139 passed in 24.05s
```

The standalone bundle is 178,331 bytes (~174.2 KiB), contains no local `models` or `widgets` imports, and its embedded docking, conformal, and MMP assets exactly match packaged artifacts.

AnyWidget improvements are substantial:

- Instance-scoped gradient IDs
- ARIA tooltip linkage
- Keyboard-focus support
- Selected-atom visual state
- Traitlet listener cleanup
- Live rendering of four widget instances

Residual frontend risks are minor: tooltip content uses `innerHTML`, and the invalid-layout branch can replace the tooltip DOM while retaining its old reference.

The workspace contains no Git metadata, so commit-level diff provenance could not be audited.

### 5. Final Recommendation & Official Sign-Off

**FINAL RECOMMENDATION: SUBMISSION GRADE — 94/100**

**Official sign-off:** The repository is submission-ready for the OpenADMET / Marimo Competitive Challenge. All five Round 6 blockers have been resolved with live, reproducible evidence.

Recommended non-blocking polish before archival:

1. Extend the docking unit test to assert every derived artifact field.
2. Rename or clearly namespace legacy `fdr_controlled` fields as empirical FDP diagnostics.
3. Separate historical audit terminology from active repository terminology.

These items do not block submission.