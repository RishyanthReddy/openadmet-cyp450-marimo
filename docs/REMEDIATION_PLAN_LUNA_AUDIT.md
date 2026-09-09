# Sequential Remediation & Elevation Plan: OpenADMET Cytochrome P450 Platform
**Target:** Elevate Adversarial Audit Score from **36/100** to **90+/100 (Publication & Submission Grade)**  
**Auditor Reference:** `docs/GPT56_LUNA_COMPREHENSIVE_REVIEW.md` (`gpt-5.6-luna` max-reasoning audit)

---

## Architecture of the Plan

The remediation is organized into **6 sequential, non-overlapping phases**. Each phase directly tackles a core vulnerability cluster flagged by Luna, verified with automated tests and visual checks before proceeding to the next.

```
Phase 1: Chemistry & Docking Truth (Raloxifene Heavy Atoms, PDB Resolutions, Multi-Isoform Framing)
   ↓
Phase 2: MMP Integrity & Data Provenance (De-duplication, OpenADMET Label Shifts, Removal of False HLM Claims)
   ↓
Phase 3: Statistical Conformal Rigor (Real Weighted Step-Up Wiring in Act 5, "FDR Controlled" Precision)
   ↓
Phase 4: Portability, Path Decoupling & True Standalone Bundling (Relative Paths, Checksums, Status Banner)
   ↓
Phase 5: AnyWidget Lifecycle & Accessibility (JS Event Cleanup, Keyboard Focus, Contrast & Mobile Viewports)
   ↓
Phase 6: End-to-End Verification, Clean Staging & Luna Re-Audit (Pytest, DevTools Audit, Target 90+ Score)
```

---

## Phase 1: Chemistry & Structural Enzymology Truth (P0 / P1)
> **Goal:** Eliminate all fact-check vulnerabilities in docking and structural chemistry.

- [ ] **Task 1.1: Correct Raloxifene Docking Distance in Act 1 & Act 3**
  - *Location:* `app.py` (lines 153, 731), `docs/`, `spikes/docking_ablation.py`
  - *Current Flaw:* Claims "raloxifene sulfur is 1.61 Å from heme Fe". The 1.61 Å contact is to a hydrogen; the benzothiophene sulfur is actually 4.91 Å, and the nearest heavy atom (carbonyl oxygen) is 2.15–2.24 Å.
  - *Fix:* Explicitly report both the nearest heavy-atom distance (`2.15 Å, Carbonyl Oxygen contact within catalytic sphere`) and the reactive sulfur distance (`4.91 Å, Benzothiophene core`). Remove the false "sulfur is 1.61 Å" claim.
- [ ] **Task 1.2: Invert PDB Resolution Typo in Act 5 Limitations**
  - *Location:* `app.py` (line 1199)
  - *Current Flaw:* Inverted resolutions: stated 2V0M was 2.05 Å and 1TQN was 2.80 Å.
  - *Fix:* Correct to: **PDB 2V0M is 2.80 Å** (CYP3A4 with ketoconazole) and **PDB 1TQN is 2.05 Å** (ligand-free CYP3A4).
- [ ] **Task 1.3: Isoform Target Framing Clarification**
  - *Location:* `app.py` (Act 1 and Act 3 headers/intro)
  - *Current Flaw:* The 10 literature reference drugs target different CYPs (CYP1A2, 2A6, 2C9, 2C19, 2D6, 3A4), but docking in Act 3 is exclusively against CYP3A4 (PDB 2V0M).
  - *Fix:* Add explicit framing text: *“CYP3A4 (2V0M) is used as the prototypical steric reference probe to evaluate active-site catalytic volume; isoform-specific targets (e.g. Furafylline on 1A2, Paroxetine on 2D6) are noted for cross-isoform selectivity.”*

---

## Phase 2: MMP Data Integrity & Accurate Provenance (P0 / P1)
> **Goal:** Align matched molecular pair claims with actual dataset origin; eliminate unsubstantiated wet-lab claims.

- [ ] **Task 2.1: Re-label 46 MMPs from "Empirical HLM Cliffs" to "OpenADMET Label Shifts"**
  - *Location:* `data/packaged/mmp_transformations.json`, `app.py` (line 799), `scripts/generate_mmps.py`
  - *Current Flaw:* Claims *"Directly validated 1→0 activity shift in human liver microsomes"* and tags pairs as `VERIFIED_EMPIRICAL`.
  - *Fix:* Update taxonomy to: `EVIDENCE_LEVEL: ALGORITHMIC_LABEL_SHIFT_OPENADMET` and description: *"Algorithmic matched molecular pair exhibiting active-to-inactive (1→0) label shift on the identical Murcko core in OpenADMET assay data."*
- [ ] **Task 2.2: De-duplicate and Condense MMP Pair Transformations**
  - *Location:* `data/packaged/mmp_transformations.json`, `tests/test_mmps.py`
  - *Current Flaw:* 46 records contain only 34 unique compound pairs (12 are duplicate fragmentation cuts).
  - *Fix:* Group pairs by unique `(mol_a_id, mol_b_id)` compound pairs, preserving distinct functional group transformations with unambiguous IDs.

---

## Phase 3: Statistical Conformal Rigor & Reactive Algorithmic Wiring (P0)
> **Goal:** Connect Act 5 UI directly to the real weighted Benjamini-Hochberg step-up selector.

- [ ] **Task 3.1: Replace Naive `p <= alpha` with True Weighted BH Step-Up Selector in Act 5**
  - *Location:* `app.py` (lines 1050–1090)
  - *Current Flaw:* The reactive slider filters `_p_val <= _target_alpha` (unadjusted hypothesis testing) while claiming "FDR Guaranteed".
  - *Fix:* Call `models/txconformal_selector.py::conformal_fdr_select()` inside the reactive cell, dynamically computing the Benjamini-Hochberg critical index $k^* = \max \{ i : p_{(i)} \le \frac{i}{m} \alpha \}$ weighted by the covariate shift density ratio $w(x)$.
- [ ] **Task 3.2: Re-label UI Badges and Narrative Claims**
  - *Location:* `app.py` (lines 1018, 1085)
  - *Current Flaw:* Overclaims "FDR Guaranteed" without citing exact finite-sample exchangeability assumptions.
  - *Fix:* Change to: *"Empirically Controlled FDR under Covariate Shift via Weighted Conformal Selection"* with clear footnotes citing the density-ratio bounds and finite-sample exchangeability criteria.

---

## Phase 4: Portability, Path Decoupling & True Standalone Bundling (P0 / H1)
> **Goal:** Guarantee zero-path dependency and true standalone execution anywhere.

- [ ] **Task 4.1: Eliminate Absolute File Paths**
  - *Location:* `app.py`, `models/embedded_assets.py`, `scripts/package_assets.py`
  - *Current Flaw:* Hardcoded `/Users/rishyanthreddy/Desktop/Marimo/...` absolute paths break on any other machine or cloud sandbox.
  - *Fix:* Use `Path(__file__).resolve().parent` for relative resolution with dynamic fallback.
- [ ] **Task 4.2: Visible Asset Status Banner (No Silent Zeros)**
  - *Location:* `app.py` (Header / Act 1)
  - *Current Flaw:* Missing files silently become `{}` and render `0.00` metrics.
  - *Fix:* Add an explicit status pill in the header:
    - 🟢 `Data Source: Full Curated Dataset (6,145 compounds, Parquet SHA-256 Verified)`
    - 🟡 `Data Source: Embedded Offline Sandbox (100-molecule Fallback Mode)`
- [ ] **Task 4.3: Real Standalone Single-File Inliner in `scripts/bundle_app.py`**
  - *Location:* `scripts/bundle_app.py`
  - *Current Flaw:* `bundle_app.py` was a validator, not an inliner.
  - *Fix:* Implement code generator that outputs a self-contained `standalone_app.py` with inlined JS/CSS and base64 gzip fallback parquet, capable of running in an empty temporary directory with zero local dependencies.

---

## Phase 5: AnyWidget Frontend Hardening & Accessibility (P1 / P2)
> **Goal:** Fix DOM event leaks, keyboard accessibility, and contrast.

- [ ] **Task 5.1: Return Cleanup Function in AnyWidget `render()`**
  - *Location:* `widgets/bioactivation_tracer.js`
  - *Current Flaw:* Event listeners attached to model changes and DOM buttons are never cleaned up on unmount.
  - *Fix:* Return a proper cleanup callback `return () => { model.off(...); ... };` conforming to the AnyWidget ESM spec.
- [ ] **Task 5.2: Keyboard Accessibility & ARIA Support**
  - *Location:* `widgets/bioactivation_tracer.js`, `widgets/bioactivation_tracer.css`
  - *Fix:* Add `tabindex="0"`, `role="button"`, `aria-label`, and visible focus rings (`:focus-visible`) on interactive atom nodes and mode toggle buttons.
- [ ] **Task 5.3: Container Overflow and Responsive Padding**
  - *Location:* `widgets/bioactivation_tracer.css`
  - *Fix:* Adjust `.bat-container` and SVG viewBox scaling so atom halos and tooltips never get clipped on narrow screens.

---

## Phase 6: End-to-End Verification & Luna Re-Audit (P2)
> **Goal:** Prove that the elevated codebase passes all verification suites and re-audit with Luna.

- [ ] **Task 6.1: Run Full Pytest Suite (24+ suites)**
  - Re-verify with zero non-zero exit codes.
- [ ] **Task 6.2: Live Google Chrome DevTools Headless Audit**
  - Regenerate `docs/DEVTOOLS_AUDIT_REPORT.json` from the running server: 0 console errors, 0 network errors.
- [ ] **Task 6.3: Standalone Offline Sandbox Verification**
  - Copy `standalone_app.py` to `/tmp/marimo_sandbox_test/` and run `marimo run` with network disabled to confirm 100% offline self-containment.
- [ ] **Task 6.4: Re-Audit with `gpt-5.6-luna` (Max Reasoning)**
  - Re-run the adversarial review prompt to measure score elevation from **36/100** to **90+/100**.
