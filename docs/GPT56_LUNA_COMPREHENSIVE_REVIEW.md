# Adversarial audit verdict

## 1. Executive verdict

**Readiness score: 36/100**

This is a strong interactive prototype and narrative demo, but it is not yet competition-ready as a scientifically defensible submission. The largest issue is the gap between the project’s integrity claims and the implementation:

- The declared single-file, zero-network contract is not implemented.
- The packaged TxConformal results are not cleanly separated from test data.
- The UI claims an incorrect docking interaction: the reported 1.61 Å contact is to a hydrogen, not raloxifene sulfur.
- The 46 “verified empirical activity cliffs” are generated binary label flips, not demonstrated quantitative HLM activity cliffs.
- The active UI does not execute the claimed weighted conformal procedure.
- The audit suite itself does not produce a clean reproducible pass.

The project is approximately demo-ready in the current repository, but not claim-ready for scientific review.

### Major strengths

- Five-act narrative structure is coherent and visually compelling.
- Current parquet contains 6,145 records and its SHA256 matches the declared expected hash.
- Current parent/scaffold split has no observed parent overlap.
- The widget architecture has a functioning AnyWidget traitlet surface and valid ESM export.
- The code has meaningful testing around RDKit parsing, schemas, asset counts, and basic widget contracts.
- The project explicitly documents limitations such as “MBI is not TDI,” which is scientifically appropriate.

### Critical vulnerabilities

1. **The “self-contained single-file notebook” is false.**
2. **Conformal FDR claims are overstated and inconsistently implemented.**
3. **The docking narrative is chemically incorrect.**
4. **MMP provenance and activity-cliff claims are unsupported.**
5. **AIMNet2-NSE provenance and validation are incomplete.**
6. **Static and hardcoded values are presented as live experimental/model outputs.**
7. **The current verification result is not clean:**

```text
123 passed, 4 failed, 7 errors, 2 warnings
```

The failures are partly caused by the restricted execution environment (`EPERM` temporary-directory and `__pycache__` failures), but they still prevent an unqualified claim that the project passes its verification suite.

The repository has no `.git` directory, so a historical/current diff could not be independently inspected.

---

## 2. Scientific and methodological rigor

### 2.1 Scaffold split and the “bathtub effect”

The split is directionally correct but not sufficient to support “zero leakage” or robust generalization claims.

What is sound:

- The current dataset has 6,145 rows.
- `grouping_parent_inchikey` is unique in the current parquet.
- Current Murcko scaffold and parent overlap checks pass.
- The split is more defensible than a random row split.

Problems:

1. **Acyclic compounds are grouped by molecule name, not a chemically stable parent key.**

   `[generate_splits.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_splits.py:37)`

   The fallback key is effectively `ACYCLIC_{molecule_name}`. Equivalent acyclic structures with different names could be separated across folds.

2. **The fold-balancing objective only optimizes CYP3A4 positives and fold size.**

   `[generate_splits.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_splits.py:81)`

   The CYP2D6 balancing variables are not actually part of the optimization objective. This contradicts the stated multi-target balance requirement.

3. **Only one primary seed appears to be used for the main split.**

   Seeds 43 and 44 are generated but there is no convincing repeated-seed stability analysis.

4. **No nearest-neighbor leakage audit is shown.**

   Scaffold disjointness does not imply chemical dissimilarity. A test molecule can still be highly similar to a training molecule through alternative scaffold representations, shared substituent series, or fragmented analogs.

5. **The leakage guardrail is exact-name based.**

   `[scripts/package_assets.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/package_assets.py:46)`

   `BANNED_COLUMNS` catches known exact names but not derived variants such as `conf_high`, `predicted_*`, `target_proxy`, `is_mmp_cliff`, or future target-derived columns.

6. **Bootstrap confidence intervals are row-level, not chemical-group-level.**

   `[models/train_augmented.py](/Users/rishyanthreddy/Desktop/Marimo/models/train_augmented.py:145)`

   A row bootstrap over correlated analogs materially understates uncertainty.

**Verdict:** The split is acceptable as a first scaffold split, but the claim of leakage-free generalization is not established. A proper audit needs parent-key grouping for acyclic compounds, repeated seeds, maximum train/test similarity, group-level bootstrap, and a complete target-derived-column audit.

---

### 2.2 AIMNet2-NSE and quantum descriptors

The mathematical intent is reasonable, but the implementation does not meet the project’s own AIMNet2-NSE validation gate.

The code appears to compute:

- `IP = E(cation) - E(neutral)`
- `EA = E(neutral) - E(anion)`
- `η = (IP - EA) / 2`
- `μ = -(IP + EA) / 2`
- `ω = μ² / (2η)`

Those formulas can be valid for consistent vertical ΔSCF energies. The problems are implementation and validation.

#### Model identity is not reproducible

The production feature path uses:

```python
AIMNet2Calculator("aimnet2")
```

`[models/train_augmented.py](/Users/rishyanthreddy/Desktop/Marimo/models/train_augmented.py:78)`

The feasibility spike uses a different identifier corresponding to `isayevlab/aimnet2-nse`. The code therefore does not prove that the packaged descriptors came from the claimed AIMNet2-NSE model. The distinction matters because AIMNet2-NSE explicitly handles spin-resolved electronic properties and requires charge/multiplicity-aware calculations. See the [AIMNet2-NSE paper](https://onlinelibrary.wiley.com/doi/full/10.1002/ange.202516763).

#### Insufficient physical validation

The implementation lacks the declared checks for:

- charge conservation,
- finite energy,
- element coverage,
- conformer sensitivity,
- reproducibility across runs,
- comparison against reference IP/EA values,
- consistency of open-shell multiplicities.

The feasibility report mainly demonstrates speed, NaN absence, and an IP range. It does not establish scientific correctness.

#### Geometry and state problems

- ETKDG coordinates are generated, but no robust geometry optimization is guaranteed.
- Random-coordinate or 2D fallbacks are possible.
- Cation and anion multiplicities are assigned using a simplistic rule.
- No check confirms that the assigned multiplicity matches the molecule’s electron count or chemically relevant state.
- Vertical ionization energies are being computed on a single conformer, with no conformer uncertainty estimate.

#### Fukui index is not safely defined

The code uses:

```python
f_rad = (q_cation - q_anion) / 2
```

`[models/train_augmented.py](/Users/rishyanthreddy/Desktop/Marimo/models/train_augmented.py:113)`

If `q` represents atomic partial charge rather than electron population, this may have the opposite sign from the usual density-based condensed radical Fukui convention. The sign convention is undocumented and never validated against a known example.

More seriously, the layout engine applies one global maximum Fukui value to every warhead atom when atom-specific values are absent:

`[layout_engine.py](/Users/rishyanthreddy/Desktop/Marimo/widgets/layout_engine.py:133)`

That cannot support atom-localized mechanistic claims.

#### Ad hoc normalization

Clipping, minimum hardness, thresholding, and maximum aggregation are used without calibration to physical uncertainty. The resulting values are presentation-friendly, but they are not demonstrably comparable across molecules.

**Verdict:** The quantum descriptors are plausible exploratory proxies, not yet scientifically validated AIMNet2-NSE ΔSCF descriptors.

---

### 2.3 CYP3A4 docking

The docking section is the most visibly incorrect scientific component.

The app claims that raloxifene sulfur is 1.61 Å from heme iron:

`[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:731)`

Inspection of the actual pose shows:

- nearest atom to Fe: hydrogen, approximately 1.61 Å;
- nearest sulfur: approximately 4.91 Å;
- nearest oxygen: approximately 2.15–2.24 Å.

Therefore the statement that “the raloxifene sulfur is 1.61 Å from heme” is false.

The docking implementation also has major methodological deficiencies:

- receptor charges are assigned as zero;
- protonation and hydrogen placement are not chemically validated;
- the heme/iron representation is not validated;
- the minimum distance includes all ligand atoms, including hydrogens;
- no reactive atom is selected;
- no Compound I or ferryl oxygen geometry is modeled;
- no pose replicate stability or redocking RMSD is reported;
- no known-ligand validation is performed;
- the distance cutoff is arbitrary;
- Vina affinity is treated as mechanistic evidence for MBI liability.

`[spikes/docking_ablation.py](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:218)`

The literature fixture is also target-mismatched. It contains compounds associated with CYP3A4, CYP2D6, CYP2A6, CYP2C9, CYP2C19, and CYP1A2, yet the UI presents the collection as a CYP3A4 docking narrative. `[literature_mbi_reference_set.json](/Users/rishyanthreddy/Desktop/Marimo/data/fixtures/literature_mbi_reference_set.json:2)`

The structural context is important: the RCSB entry for [2V0M](https://www1.rcsb.org/structure/2V0M) is a CYP3A4–ketoconazole structure at 2.80 Å, while [1TQN](https://www.rcsb.org/structure/1TQN) is at 2.05 Å. The app reverses these resolutions in its limitations text.

**Verdict:** The docking result cannot currently support a claim of chemically credible bioactivation accessibility. The 1.61 Å sulfur claim must be removed immediately.

---

### 2.4 Matched molecular pairs

The 46 MMP records are not demonstrated activity cliffs.

The generator:

- fragments molecules with `maxCuts=1`;
- chooses the larger disconnected fragment as “core”;
- does not explicitly enforce an exocyclic cut;
- does not explicitly enforce a six-heavy-atom delta;
- selects any binary label flip;
- has no potency difference threshold;
- has no assay replication requirement;
- has no uncertainty or source-level assay provenance.

`[generate_mmps.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_mmps.py:43)`  
`[generate_mmps.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_mmps.py:79)`

The output has 46 records but only 34 unique molecule-pair identities. Twelve records are duplicate transformations of the same underlying compound pair. The records are labeled `VERIFIED_EMPIRICAL`, but the generator does not perform empirical verification.

The app’s claim:

> “Directly validated 1→0 activity shift in human liver microsomes”

`[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:799)`

is not supported by the generation code or metadata. The records appear to be binary OpenADMET target-label flips, not direct replicated HLM MBI measurements.

There is also no binding-affinity evidence supporting the UI claim that a “safe analog” maintains the binding core or drug-like behavior.

**Verdict:** These can be called “label-flip matched pairs” or “hypothesis-generating transformations.” They cannot currently be called verified empirical activity cliffs.

---

### 2.5 TxConformal and FDR control

The project’s strongest statistical claim is currently not defensible.

The app says:

- “FDR Guaranteed”
- weighted step-up selection
- finite-sample FDR control.

`[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1085)`

But the app’s actual reactive logic simply filters candidates using:

```python
_p_val <= _target_alpha
```

`[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1078)`

That is not a weighted step-up procedure.

The implementation is inconsistent:

- `models/txconformal_selector.py` implements weighted p-values followed by ordinary BH.
- `scripts/package_assets.py` duplicates a different implementation.
- The app bins alpha into four static result records instead of recomputing selection.
- The UI reports precomputed expected values rather than the result of the active selection.

The packaged implementation also has serious separation leakage. Its OOF predictions are generated from folds spanning the full dataset, so models evaluating one test fold can be trained on other test-fold labels.

`[scripts/package_assets.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/package_assets.py:109)`  
`[scripts/package_assets.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/package_assets.py:135)`

Even the cleaner selector implementation does not prove FDR control:

- it reports one realized FDP, not the expectation `E[FDP]`;
- it clips estimated density-ratio weights to `[0.1, 10]` without proving the resulting procedure remains valid;
- domain-discriminator calibration is not independent of all other modeling decisions;
- its Monte Carlo procedure resamples the same labeled test set with replacement;
- its normal-approximation interval is not a rigorous finite-sample FDP confidence bound.

The selector itself documents ordinary BH, not a proven general weighted step-up theorem. The [TxConformal preprint](https://www.biorxiv.org/content/10.64898/2026.04.27.721076v1) and [reference implementation](https://github.com/ying531/TxConformal) support the general idea of balancing and conformal selection, but do not validate this project’s specific implementation.

**Verdict:** The project may demonstrate an exploratory conformal-ranking workflow. It must not claim “FDR guaranteed” until the exact procedure, assumptions, train/calibration/test separation, and finite-sample bound are independently established.

---

## 3. Application architecture and code quality

### Marimo DAG

No obvious direct reactive cycle was found in `app.py`, and the five-act cell structure is broadly understandable. However:

- the app is 1,261 lines and mixes computation, presentation, data loading, provenance, and static claims;
- many displayed values are not outputs of reactive computations;
- missing assets silently become empty dictionaries;
- invalid molecule input raises through the layout engine;
- no unified error-state model exists;
- runtime status is not surfaced to the user.

The architecture is therefore DAG-shaped but not evidence-shaped: a reactive control can update one number while the surrounding scientific interpretation remains hardcoded.

### PEP 723 and reproducibility

`app.py` declares loose dependencies such as `marimo>=0.11.0`, while the project plan requires a pinned Marimo version. `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1)`

The app also reports `__generated_with="0.11.0"` even though the plan specifies a different target version.

This is a reproducibility risk for:

- widget behavior,
- Marimo cell semantics,
- Markdown/LaTeX rendering,
- AnyWidget lifecycle,
- browser audit results.

### Packaging

The bundler does not actually create a standalone application. It checks that components exist and returns `"bundle_ready": True`.

`[scripts/bundle_app.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/bundle_app.py:52)`  
`[scripts/bundle_app.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/bundle_app.py:90)`

The app imports external Python modules and external packaged JSON/parquet files. Copying only `app.py` to an empty directory fails.

### Fallback behavior

`load_curated_dataset(max_retries=3)`:

- uses an absolute local path;
- does not perform SHA256 verification;
- does not retry;
- does not perform network fallback;
- does not use `max_retries`.

`[models/embedded_assets.py](/Users/rishyanthreddy/Desktop/Marimo/models/embedded_assets.py:24)`  
`[models/embedded_assets.py](/Users/rishyanthreddy/Desktop/Marimo/models/embedded_assets.py:54)`

The fallback only applies to that loader. Act 2, Act 3, and Act 5 independently load external files and silently substitute `{}` when files are missing. The app can therefore display zeros or empty selections without telling the user that the scientific asset is unavailable.

---

## 4. UI, typography, and accessibility

### Visual hierarchy

The five-act progression is effective. The primary UI problem is not visual polish; it is semantic trust. Static numbers and prose are styled like live calculations.

Examples:

- hardcoded benchmark deltas;
- hardcoded Tanimoto distributions;
- hardcoded docking summary values;
- hardcoded conformal bins;
- static OOF case explanations presented as “real out-of-fold” results.

The UI needs visible provenance labels such as:

- computed live,
- loaded from packaged artifact,
- illustrative,
- unavailable,
- externally sourced.

### Controls and edge cases

- Empty or corrupt literature data can cause `mbi_dropdown.value` access errors.
- Missing docking data falls back to one raloxifene record, which can make a partial dataset look complete.
- Missing benchmark files produce zero metrics without a warning.
- The conformal slider only selects among four precomputed bins; it does not recompute the procedure.
- The OOF inspector does not resolve records from stored OOF prediction data.
- Invalid SMILES can raise out of the reactive cell and break rendering.

### AnyWidget

The ESM export is present and the traitlet fields exist, but lifecycle and accessibility are incomplete.

Problems:

- no cleanup function is returned from `render`;
- model listeners remain attached after widget destruction;
- fixed SVG gradient IDs can collide across multiple widget instances;
- atom nodes are not keyboard-focusable;
- no `aria-label`, `role`, or `aria-pressed` state exists for atom selection;
- selected atom state is not visually represented;
- Python-side selection changes are not clearly reflected in the SVG;
- `innerHTML` is used for tooltip and badge content;
- the tooltip is hover-only and unsuitable for touch devices.

### Responsive behavior

The header contains non-wrapping elements:

`[bioactivation_tracer.css](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.css:78)`

The container clips overflow while the SVG allows overflow:

`[bioactivation_tracer.css](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.css:46)`  
`[bioactivation_tracer.css](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.css:147)`

This is likely to clip large halos, labels, and tooltips on narrow viewports.

There are also no visible `:focus-visible` styles, and several color combinations are questionable for WCAG contrast, especially small muted text and green/red semantic overlays.

---

## 5. Detailed findings

### Critical

#### C1 — Standalone-file contract is not implemented

**Location:** `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:39)`, `[bundle_app.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/bundle_app.py:52)`

**Problem:** `app.py` imports `models` and `widgets` from the filesystem and reads packaged assets externally. The bundler only validates components; it does not inline or write a standalone file.

**Fix:** Build an actual bundling step that embeds Python fallback data, widget JavaScript, CSS, and all required metadata. Add a CI test that copies only the generated file into a clean temporary directory and runs it.

#### C2 — SHA256 and retry promises are not implemented

**Location:** `[embedded_assets.py](/Users/rishyanthreddy/Desktop/Marimo/models/embedded_assets.py:24)`, `[embedded_assets.py](/Users/rishyanthreddy/Desktop/Marimo/models/embedded_assets.py:54)`

**Problem:** The expected hash exists, but the loader never hashes the file. `max_retries` is unused. The loader has no remote URL, timeout, or backoff.

**Fix:**

```python
digest = hashlib.sha256(path.read_bytes()).hexdigest()
if digest != PARQUET_EXPECTED_SHA256:
    raise ValueError("Curated parquet checksum mismatch")
```

Implement retries around an explicit remote source, then fall back only after checksum validation fails.

#### C3 — TxConformal UI claims a guarantee it does not execute

**Location:** `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1078)`, `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1085)`

**Problem:** The active selection is `p <= alpha`, while the UI labels it “FDR Guaranteed.”

**Fix:** Call one canonical tested selector from the reactive cell, expose weights/p-values/selected hypotheses, and remove “guaranteed” until a formal bound is demonstrated.

#### C4 — Packaged conformal predictions leak test-fold labels

**Location:** `[package_assets.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/package_assets.py:109)`, `[package_assets.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/package_assets.py:135)`

**Problem:** Fold models are trained over all folds, so predictions for one test fold can be influenced by labels from other test folds.

**Fix:** Train the predictive model on TRAIN only, calibrate on CALIBRATION only, and evaluate TEST exactly once. No test labels may enter model, threshold, weight, feature selection, or hyperparameter decisions.

#### C5 — Raloxifene sulfur distance is false

**Location:** `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:731)`

**Problem:** The 1.61 Å minimum is to hydrogen, not sulfur. Sulfur is approximately 4.91 Å from Fe.

**Fix:** Compute and display the nearest heavy atom and reactive atom explicitly. Remove all mechanistic conclusions based on Fe-to-any-atom distance.

#### C6 — MMPs are mislabeled as verified empirical activity cliffs

**Location:** `[generate_mmps.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_mmps.py:79)`, `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:799)`

**Problem:** The generator finds binary label flips without quantitative effect size, replicated assay evidence, or source-level HLM provenance.

**Fix:** Rename them to “binary label-flip MMP hypotheses,” or replace them with source-linked quantitative HLM measurements and explicit assay uncertainty.

#### C7 — AIMNet2-NSE provenance is ambiguous

**Location:** `[train_augmented.py](/Users/rishyanthreddy/Desktop/Marimo/models/train_augmented.py:78)`

**Problem:** The production path and feasibility path use different calculator identifiers. The report does not establish that the packaged descriptors came from AIMNet2-NSE.

**Fix:** Pin the exact model identifier and version, record it in every descriptor artifact, and add a test that verifies model identity.

---

### High

#### H1 — Absolute paths break portability

**Location:** `[embedded_assets.py](/Users/rishyanthreddy/Desktop/Marimo/models/embedded_assets.py:24)`, `[package_assets.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/package_assets.py:35)`

**Problem:** `/Users/rishyanthreddy/Desktop/Marimo/...` is embedded in runtime code and packaging code.

**Fix:** Resolve paths relative to `Path(__file__)`, or eliminate runtime filesystem dependencies through true bundling.

#### H2 — Missing scientific assets silently display zeros

**Location:** `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:237)`, `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:530)`, `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1050)`

**Problem:** Missing files become `{}` and the app continues rendering apparently valid cards.

**Fix:** Introduce an explicit `AssetStatus` object with `available`, `source`, `sha256`, and `error`. Render a visible unavailable state instead of zero metrics.

#### H3 — Static narratives do not follow control values

**Location:** `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:364)`, `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:615)`

**Problem:** Text such as “+0.0364 PR-AUC” and “directly sharpen precision” remains fixed when the selected metric or data source changes.

**Fix:** Generate narrative text from the selected metric and verified artifact values, with confidence intervals.

#### H4 — Split implementation does not enforce the stated protocol

**Location:** `[generate_splits.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_splits.py:37)`, `[generate_splits.py](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_splits.py:81)`

**Problem:** Acyclic grouping and CYP2D6 balancing are incomplete.

**Fix:** Group by canonical parent structure/InChIKey, optimize all target distributions, and report repeated-seed statistics.

#### H5 — OOF inspector is not connected to OOF artifacts

**Location:** `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:903)`

**Problem:** Four hardcoded examples are presented as real OOF predictions without record IDs, artifact lookup, fold identity, or checksum.

**Fix:** Load examples from a versioned OOF table and display molecule ID, fold, model version, calibration partition, and source hash.

#### H6 — Widget event listeners leak

**Location:** `[bioactivation_tracer.js](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:359)`

**Problem:** Listeners are attached but no cleanup callback is returned.

**Fix:** Return a cleanup function that removes every listener and cancels pending rendering work.

#### H7 — Widget metadata violates the declared contract

**Location:** `[bioactivation_tracer.js](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:261)`

**Problem:** `score_type` values do not match the documented enum, and `score_source` is hardcoded regardless of actual provenance.

**Fix:** Validate metadata in Python and serialize only allowed enums with real source identifiers.

#### H8 — Layout errors are not isolated

**Location:** `[layout_engine.py](/Users/rishyanthreddy/Desktop/Marimo/widgets/layout_engine.py:65)`, `[layout_engine.py](/Users/rishyanthreddy/Desktop/Marimo/widgets/layout_engine.py:218)`

**Problem:** Invalid SMILES, empty molecules, unusual chemistry, or malformed Fukui indices can raise and break rendering. Batch generation has no per-molecule isolation.

**Fix:** Return a typed error layout for individual molecules and continue rendering the rest of the application.

#### H9 — Docking receptor preparation is not chemically validated

**Location:** `[docking_ablation.py](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:113)`

**Problem:** Zero receptor charges, simplified heme treatment, and no known-pose validation make the docking score and geometry unreliable.

**Fix:** Validate protonation, charges, heme parameters, metal coordination, redocking RMSD, pose clustering, and reactive-atom orientation.

#### H10 — “Chemprop v2” export is only a random dense head

**Location:** `spikes/docking_ablation.py` export section

**Problem:** The ONNX artifact exports a `BinaryClassificationFFN`-style head over dummy embeddings, not a complete Chemprop D-MPNN message-passing model.

**Fix:** Export the complete graph model or label the artifact accurately as a classifier-head smoke test.

#### H11 — DevTools evidence is stale and incomplete

**Location:** `[DEVTOOLS_AUDIT_REPORT.json](/Users/rishyanthreddy/Desktop/Marimo/docs/DEVTOOLS_AUDIT_REPORT.json:1)`, `[test_devtools_audit.py](/Users/rishyanthreddy/Desktop/Marimo/tests/test_devtools_audit.py:98)`

**Problem:** The report claims zero console errors and 341 requests, but the current audit was not reproduced. The test checks response status but not request failures, mobile layout, accessibility, or offline behavior.

**Fix:** Regenerate the report from the exact submission artifact and test request failures, console errors, mobile widths, offline mode, and actual control state changes.

---

### Medium

#### M1 — Static docking and benchmark summaries can contradict selected records

**Location:** `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:748)`

**Problem:** Summary tables are hardcoded separately from dropdown data.

**Fix:** Derive every summary row from the same validated data object used by the selector.

#### M2 — Four-bin alpha logic is not continuous

**Location:** `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1057)`

**Problem:** Slider values are mapped to a few static bins, creating the appearance of continuous conformal control.

**Fix:** Recompute selection for every slider value or make the control a discrete selector with explicit labels.

#### M3 — AnyWidget lacks keyboard accessibility

**Location:** `[bioactivation_tracer.js](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:263)`

**Problem:** Atoms respond to mouse hover/click only.

**Fix:** Add `tabindex="0"`, semantic roles, keyboard activation, focus styling, and accessible labels.

#### M4 — SVG and tooltip clipping on small screens

**Location:** `[bioactivation_tracer.css](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.css:46)`

**Problem:** Container clipping conflicts with oversized halos and tooltip positioning.

**Fix:** Add responsive breakpoints, allow controlled overflow, and reposition tooltips within viewport bounds.

#### M5 — Contrast and dark-mode variables are inconsistent

**Location:** `[bioactivation_tracer.css](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.css:24)`, `[bioactivation_tracer.css](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.css:205)`

**Problem:** CSS variables are scoped inconsistently, and `mix-blend-mode:multiply` can reduce contrast.

**Fix:** Test rendered colors under light/dark themes with automated WCAG contrast checks.

#### M6 — External PubMed link violates offline narrative

**Location:** `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:167)`

**Problem:** The link fails without network and has no local citation fallback.

**Fix:** Include citation metadata locally and mark external links as optional.

#### M7 — Empty dropdowns are not handled robustly

**Location:** `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:142)`

**Problem:** Empty or malformed fixture data can make `.value` invalid or raise.

**Fix:** Provide an explicit “No records available” state and validate the selected key before dereferencing.

#### M8 — Scientific citations and resolution text are inconsistent

**Location:** `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1018)`, `[app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1199)`

**Problem:** The TxConformal venue/citation is inconsistent with the project’s own source, and 2V0M/1TQN resolutions are reversed.

**Fix:** Use DOI/URL-backed citations generated from structured metadata.

#### M9 — MMP uniqueness and curation tests are inadequate

**Location:** `[tests/test_mmps.py](/Users/rishyanthreddy/Desktop/Marimo/tests/test_mmps.py:1)`

**Problem:** Tests check parsing and counts but not unique pair identity, exocyclic cuts, delta limits, same-core identity, or assay provenance.

**Fix:** Add invariant tests for all stated MMP criteria and require unique molecule-pair keys.

---

### Low / enhancement

#### L1 — `innerHTML` creates future injection risk

**Location:** `[bioactivation_tracer.js](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:85)`

**Problem:** Current strings are mostly internal, but future molecule names or citations could become unsafe HTML.

**Fix:** Use `textContent` for untrusted values and construct DOM nodes explicitly.

#### L2 — Widget tests use an unrealistically weak fake DOM

**Location:** `[test_anywidget_contract.py](/Users/rishyanthreddy/Desktop/Marimo/tests/test_anywidget_contract.py:70)`

**Problem:** `querySelector` returns `null`, so the tests do not exercise actual SVG generation, event wiring, focus, or cleanup.

**Fix:** Add browser-level tests with real DOM behavior.

#### L3 — Performance claims are not independently reproduced

**Location:** `[MASTER_PLAN.md](/Users/rishyanthreddy/Desktop/Marimo/MASTER_PLAN.md:30)`

**Problem:** The stated latency SLAs and stale DevTools report are not verified against a clean submission artifact.

**Fix:** Benchmark cold start, first render, reactive update, and four simultaneous widgets on the exact competition environment.

---

## 6. Prioritized action checklist

### P0 — Must fix before submission

1. Remove or correct the false 1.61 Å sulfur claim.
2. Stop calling the MMPs “verified empirical activity cliffs” unless source-linked quantitative assay evidence is added.
3. Rebuild the conformal pipeline with strict TRAIN/CALIBRATION/TEST separation.
4. Make the app call the actual conformal selector instead of filtering `p <= alpha`.
5. Remove “FDR Guaranteed” until a valid theorem and empirical protocol support it.
6. Implement real single-file bundling and test execution from a clean directory.
7. Replace absolute paths and add checksum validation.
8. Make missing assets visible rather than silently rendering zeros.
9. Pin the exact Python, Marimo, AnyWidget, RDKit, AIMNet, and Vina versions.
10. Correct the AIMNet2-NSE model identity and complete the declared physics validation gate.

### P1 — Required for scientific credibility

11. Rebuild docking validation around reactive heavy atoms, validated heme parameters, pose clustering, and known-ligand redocking.
12. Separate CYP3A4 fixtures from compounds whose literature target is another CYP isoform.
13. Rework MMP extraction to enforce true matched cores, unique pairs, explicit transformation limits, and quantitative assay criteria.
14. Add repeated-seed scaffold splits, maximum similarity audits, and group-level bootstrap intervals.
15. Replace hardcoded UI claims with values derived from versioned artifacts.
16. Connect the OOF inspector to real stored OOF predictions.
17. Add artifact provenance: source, fold, model version, checksum, and computation status.

### P2 — Required for product quality

18. Add AnyWidget cleanup, keyboard support, focus states, accessible labels, and visible selection state.
19. Fix mobile header wrapping, SVG overflow, tooltip positioning, dark-mode variables, and contrast.
20. Add browser tests for offline mode, mobile widths, request failures, console errors, and actual control state changes.
21. Re-run the full test suite outside the restricted temporary-directory environment.
22. Regenerate `DEVTOOLS_AUDIT_REPORT.json` from the final artifact.
23. Correct citations, DOI/URL metadata, and PDB resolution statements.

Until the P0 list is complete, the project should be presented as an exploratory prototype rather than a validated bioactivation-risk and statistically controlled selection system.