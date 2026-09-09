Audit complete: **56/100 — REVISION NEEDED**.

The workspace is read-only, so I could not save the report to `docs/GPT56_LUNA_POST_REMEDIATION_AUDIT.md`; the write was rejected. The complete report follows.

# Comprehensive Post-Remediation Adversarial Audit Report

### 1. Executive Summary & Calibrated Score

- **Previous Score:** 36 / 100
- **Post-Remediation Score:** **56 / 100**
- **Submission Readiness Verdict:** **REVISION NEEDED**

The remediation materially improved the visible application and core asset packaging path, but the highest-risk issues remain. Act 5 does not call a reusable conformal selector and applies Benjamini–Hochberg to only a 50-candidate sample. The conformal selector’s Monte Carlo procedure reuses labeled test outcomes and does not establish the claimed guarantee. The checked-in MMP generator still emits obsolete empirical-verification labels and cannot reproduce the packaged artifact. Verification commands also do not complete cleanly.

| Dimension | Score |
|---|---:|
| Scientific & Chemical Truth | 15 / 25 |
| Data Provenance & MMP Integrity | 7 / 15 |
| Statistical & Conformal Rigor | 8 / 20 |
| Architecture, Portability & Bundling | 14 / 20 |
| AnyWidget Frontend, UI & Accessibility | 8 / 10 |
| Test Coverage & DevTools Audit | 4 / 10 |
| **Total** | **56 / 100** |

The workspace contains no Git metadata, so repository diff provenance could not be independently reviewed.

### 2. Detailed Evaluation by Remediation Phase

#### Phase 1 — Chemistry and Structural Enzymology Truth

**Original defect.** The baseline audit found that a 1.61 Å hydrogen distance was incorrectly presented as a sulfur contact, PDB resolutions were inverted, and CYP3A4 structural probing was insufficiently separated from broader CYP isoform biology.

**Implemented and verified.** `app.py` now reports Raloxifene’s top pose as:

- nearest heavy atom: phenolic oxygen at 2.24 Å;
- benzothiophene sulfur: 8.03 Å.

Direct parsing of `docked_2V0M_raloxifene.pdbqt`, MODEL 1, reproduced these values. The raw PDB headers confirm 2V0M at 2.80 Å and 1TQN at 2.05 Å. Act 3 frames CYP3A4 2V0M as a prototypical steric model and contextualizes CYP1A2, 2A6, 2C9, 2C19, 2D6, and 3A4.

**Residual risk.** The UI states that the 2.24 Å oxygen lies within the ferryl-oxo catalytic sphere, although the calculation is only a distance-to-heme-iron proxy and does not establish ferryl-oxo chemistry, protonation, Compound I formation, or covalent mechanism. The interface does not identify the selected pose as MODEL 1, despite nine poses having materially different distances. `docs/STRETCH_EXPERIMENTS_REPORT.md` still contains an unqualified 1.61 Å entry. The literature fixture and UI still use “clinically validated” and “validated literature MBIs” for records with mixed evidence levels.

**Assessment.** The specific sulfur error and resolution inversion are fixed in the main app, but mechanistic wording and stale artifacts prevent a full pass.

#### Phase 2 — MMP Data Integrity and Provenance

**Original defect.** The baseline found 46 purported empirical HLM cliffs, duplicates, unsupported experimental claims, and weakly specified transformation generation.

**Implemented and verified.** `data/packaged/mmp_transformations.json` contains 34 unique pairs: 25 CYP3A4 and 9 CYP2D6. All pairs use `OPENADMET_LABEL_SHIFT` provenance. Direct RDKit checks found:

- 34 unique pair IDs/names;
- all 56 molecule names present in the packaged dataset;
- no conserved-core matching failures;
- heavy-atom deltas within six.

Act 4 now describes the records as OpenADMET label shifts rather than empirical HLM validation.

**Residual risk.** `scripts/generate_mmps.py` is not reproducible with the packaged artifact. It still emits `VERIFIED_EMPIRICAL`, `INACTIVE_TO_LIABILITY`, old 35/15 quotas, and the old creation date. It does not explicitly enforce every advertised exocyclic-bond, delta, maximal-core, and de-duplication rule.

The packaged MMP JSON lacks assay IDs, source references, replicate counts, uncertainty, and explicit row-level provenance. There is also a semantic inconsistency: `mol_inactive`/`mol_active` encode false/true while `measured_label_flip` says `OPENADMET_ACTIVE_TO_INACTIVE`.

Act 4’s “OOF” showcase is hardcoded to four narratives rather than being linked to fold IDs, model artifacts, predictions, and source records. Some text still claims “in vitro HLM testing confirmed” and “experimentally active/safe.”

**Assessment.** The packaged artifact improved substantially, but the generator and provenance contract remain inadequate.

#### Phase 3 — Statistical Conformal Rigor and Algorithmic Wiring

**Original defect.** The baseline found “FDR Guaranteed” claims, an app path that did not execute the selector, static results, and an invalid Monte Carlo guarantee.

**Implemented and verified.** Act 5 contains a real dynamic BH computation: p-values are sorted, thresholds `(k/m) × alpha` are evaluated, and the largest passing k is selected. The local badge now says “Empirical FDR Controlled (Nominal α ≤ target).” `models/txconformal_selector.py` contains a correct ordinary BH helper.

**Residual risk.** No `conformal_fdr_select()` function exists, and Act 5 does not import or call the selector. Instead, Act 5 performs its own BH calculation on `test_candidates_sample`, containing only 50 records, while packaged metadata reports 703 test records. At alpha 0.10, the sample selects 33 candidates while the full artifact summary selects 106.

The selector:

- fits a domain discriminator using calibration and test descriptors;
- clips density-ratio weights to `[0.1, 10]` without a validity argument;
- evaluates labeled test outcomes;
- bootstraps the same test p-values and labels;
- reports a normal-approximation interval around realized FDP.

This does not establish expected or finite-sample FDR control. Candidate payloads expose `is_tdi_ground_truth`, incompatible with a genuinely blinded display path. Static alpha-bin summaries remain wired into the UI.

Unsupported language remains, including:

- “Provable Safety”;
- “guaranteeing finite-sample FDR control”;
- “E[FDR]≤alpha”;
- “Finite-sample FDR controlled via TxConformal”;
- “FDR ≤ 2.7%.”

**Assessment.** The local BH calculation is real, but the central conformal wiring and claim discipline remain submission-blocking defects.

#### Phase 4 — Portability, Path Decoupling, and Bundling

**Original defect.** The baseline found absolute workstation paths, incomplete bundling, and weak fallback/integrity behavior.

**Implemented and verified.** Production loaders now use relative `Path(__file__).resolve()` paths. The 6,145-row Parquet is SHA-256 verified against:

`d11dec87562080471d33c0e4d2a93b6f85e369d8d3dbc4286830f8fda8038e7d`

Direct loading reports `PRIMARY_PARQUET_VERIFIED`. The app displays green full-dataset or yellow embedded-sandbox status. The bundler embeds JS, CSS, fallback data, literature data, and MMP data. `standalone_app.py` imports without project model/widget imports, and its embedded MMP count matches the packaged artifact.

**Residual risk.** The bundler validates layout-engine bytes but the standalone file contains a manually duplicated layout implementation, creating source-drift risk. `load_curated_dataset(max_retries=3)` accepts a retry parameter but does not actually retry. Other assets lack equivalent hash verification. Dependencies remain unpinned, and clean-directory/network-disabled standalone execution was not demonstrated. Absolute paths remain in browser scripts, tests, logs, and planning artifacts.

**Assessment.** Portability is materially improved, but the bundle is not fully hermetic or generated from a single source of truth.

#### Phase 5 — AnyWidget Frontend and Accessibility

**Original defect.** The widget lacked cleanup, keyboard semantics, focus styles, and responsive overflow handling.

**Implemented and verified.** `widgets/bioactivation_tracer.js` adds:

- `tabindex="0"`;
- `role="button"`;
- `aria-label`;
- Enter/Space key handlers.

CSS includes `:focus-visible` styles. `render()` returns cleanup that removes traitlet listeners and clears the DOM root.

**Residual risk.** `.bat-container` still uses `overflow: hidden`; child SVG overflow cannot prevent parent clipping. Long no-wrap labels may overflow narrow layouts. Fixed SVG gradient IDs can collide across multiple widget instances. Tooltip/badge markup uses `innerHTML`, lacks complete `aria-describedby` relationships, and selected-atom state is not fully observed/rendered. The lifecycle test is not a browser integration test.

**Assessment.** Strong improvement with minor remaining UI and accessibility risks.

#### Phase 6 — Verification Suites and DevTools Audit

**Implemented and verified.** `docs/DEVTOOLS_AUDIT_REPORT.json` reports:

- Chrome 152;
- 341 network requests;
- zero unhandled console errors;
- 80 SVG elements;
- four AnyWidget instances;
- five dropdowns;
- two sliders;
- 125 buttons;
- all five Acts verified;
- 1.525 s page load;
- 15.89 ms reactive-render p95.

Direct imports of `app.py` and `standalone_app.py` succeeded, as did direct Node import of the widget.

**Failed verification.** `pytest tests/ -v` failed before collection because no usable temporary directory was available. `marimo check app.py standalone_app.py` exited 0 but emitted two unhandled task exceptions from `ReusableDefinitionOrderRule.check`, caused by the same temporary-directory failure. It cannot be treated as clean DAG evidence.

Several Act tests check only return codes and ignore stderr. The DevTools JSON is a lossy summary and omits HTTP failures, accessibility results, offline testing, mobile checks, and proof of actual state transitions. Browser scripts contain hardcoded Chrome and `.gemini` paths. Some tests use mocked DOM/model objects and simulated rendering; a docking test uses random input to exercise an FFN head.

**Assessment.** The DevTools report is useful historical evidence, but current verification is not clean and does not support a zero-mock/zero-simulation claim.

### 3. Verification of Zero False Claims and Zero Mocks

A zero-false-claims conclusion is not supportable.

Positive findings:

- The primary dataset is real, packaged, and hash-verified.
- The packaged MMP artifact is labeled as an OpenADMET label-shift resource.
- Docking values for the top Raloxifene pose agree with direct PDBQT geometry.
- The production code uses real RDKit, LightGBM, logistic-regression, docking, and AIMNet/ΔSCF paths.

Blocking findings:

- Unsupported “provable,” “guaranteed,” clinical-validation, HLM, and experimental-OOF language remains.
- The checked-in MMP generator still emits obsolete empirical labels.
- The conformal artifact exposes ground-truth test labels.
- Static narratives are not consistently linked to source rows or model artifacts.
- Tests contain mocks and random probes. These may be legitimate unit-test techniques, but they do not prove real end-to-end execution.

Public wording should be limited to: “Empirical evaluation on the packaged OpenADMET split under the stated protocol,” with explicit assumptions and limitations.

### 4. Code Quality and Architectural Health

Relative production paths and the primary SHA-256 gate are good improvements. The standalone source is importable and embeds the principal visible assets.

The Marimo DAG was not cleanly verified because `marimo check` emitted unhandled exceptions despite exit code 0. The absence of Git metadata also limits reproducibility review.

Standalone portability is improved but not fully hermetic: layout code is duplicated, dependencies are unpinned, optional external probes remain, and the retry parameter is ineffective.

AnyWidget lifecycle hygiene is substantially improved because listeners are removed and the DOM is cleared. Remaining fixed-ID, clipping, `innerHTML`, and semantic-state issues should still be corrected.

### 5. Remaining Observations, Minor Recommendations, and Roadmap

Before submission:

1. Implement one tested `conformal_fdr_select()` function and call it from Act 5 over the complete candidate set.
2. Remove labels from user-facing candidate payloads.
3. Separate empirical FDP reporting from formal guarantees and remove unsupported guarantee language.
4. Replace `generate_mmps.py` with a deterministic generator matching the 34-pair artifact.
5. Add source, assay, replicate, uncertainty, and row-level provenance fields.
6. Remove or qualify stale HLM, clinical-validation, 1.61 Å, and FDR language across app, standalone app, docs, TODO, and planning files.
7. Make pytest, browser, and Marimo checks fail on stderr and capture complete evidence.
8. Generate the standalone layout from one canonical source and implement real retries/per-asset hashes.
9. Fix widget clipping, instance-safe SVG IDs, tooltip semantics, and selected-state rendering.
10. Add tests for selector equivalence, MMP reproducibility, structural correspondence, label hiding, and clean standalone execution.

### 6. Final Recommendation and Sign-Off

**Recommendation: REVISION NEEDED.**

The score rises from 36 to 56 because the chemistry typo, PDB resolutions, dataset hash gate, packaged MMP count/label, production path portability, standalone asset embedding, and AnyWidget cleanup/accessibility work are genuine improvements.

The project should not yet be signed off. Conformal safety claims, MMP reproducibility/provenance, stale unsupported statements, and nonclean verification results remain material scientific and engineering risks. A submission-grade re-audit should follow only after these issues are corrected and the full test, Marimo, browser, and clean standalone checks complete without hidden task exceptions.