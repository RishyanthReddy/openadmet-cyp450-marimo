# 100-MOLECULE BASELINE VERTICAL SLICE REPORT
## Milestone Acceptance Report: Full End-to-End Working Pipeline

> **Document Status:** Milestone Acceptance Report  
> **Paired Task:** `EC-0-4-01` (Phase 0 Feasibility Spike & September 10 Milestone)  
> **Timestamp:** 2026-09-03 03:44:24 UTC  
> **Evaluator:** Antigravity / Senior Software Engineer Protocol

---

## 1. Executive Summary & Milestone Verdict

- **Milestone Verdict:** **PASS (GO)**
- **Objective:** Deliver a complete, functional vertical slice of the entire pipeline across 100 curated molecules (Data Ingestion $\to$ ECFP4 Baseline Featurization $\to$ Cross-Validated Modeling $\to$ Custom `BioactivationTracer` Anywidget $\to$ Interactive Marimo Notebook) ahead of the September 10, 2026 milestone.
- **Local In-Memory Boot Latency:** **0.443 seconds** (SLA $< 3.0\text{s}$).
- **molab.marimo.io Cloud Gateway Latency:** **1.26 seconds** (SLA $< 10.0\text{s}$).
- **Static Standalone HTML Export:** **323 KB** (`/tmp/vertical_slice.html`).
- **Target Leakage Enforcement:** 100% verified (2,048 pure structure bits; zero assay leakage).

---

## 2. Dataset Curation & Stratification

From the primary OpenADMET benchmark (`cyp-challenge-TRAIN_TDI.csv`, 6,145 rows), a 100-molecule stratified slice was extracted:
- **Total Molecules:** 100
- **CYP3A4 TDI Confirmed Liabilities (Positive):** 25 compounds (25.0%)
- **CYP3A4 Safe Non-TDI Compounds (Negative):** 75 compounds (75.0%)
- **Class Ratio:** 1:3 positive-to-negative ratio, matching the real-world baseline class imbalance.
- **Echo-MS Mass Spec Overlap:** Cross-referenced with Octant `willitfly.tsv` to embed real quantitative ammonium fluoride ionization peak areas for analytical QC context.

---

## 3. ECFP4 Baseline Modeling & Target Leakage Validation

### A. Zero Target-Leakage Assertion
The feature extraction pipeline was programmatically verified against the target-leakage guardrail contract:
```python
# Programmatic assertion verified before model fitting:
assert_zero_target_leakage(feature_cols)  # PASSED on all 2,048 Morgan bits
```
* Under no circumstances were `pIC50_direct_inhibition`, `pIC50_TDI_condition`, `Emax`, confidence intervals, or standard deviations provided as features.

### B. 5-Fold Stratified Cross-Validation Results
To provide realistic baseline risk probabilities for each of the 100 molecules, a balanced Logistic Regression classifier ($C=0.5$, class-weight balanced) was trained across 5 folds:
- **ROC-AUC:** **0.647**
- **MCC (Matthews Correlation Coefficient):** **0.063**
- **Brier Score (Calibration Metric):** **0.200**

These out-of-fold calibrated probabilities are exported directly into the notebook for interactive exploration.

---

## 4. `BioactivationTracer` Anywidget Vector Engine

The custom anywidget mounts directly in Marimo and renders client-side chemical vector graphics using vanilla SVG and Traitlets:
1. **Automated 2D Layout:** Coordinates are pre-computed using RDKit `rdDepictor.Compute2DCoords` and dynamically scaled to the SVG viewport.
2. **Skeletal Bond Geometry:** Accurately renders single bonds and offset double bonds (`order: 2`).
3. **Multi-Color Atom Halos:**
   - **High Susceptibility Halos (Amber / Red):** Radial gradient halos centered on atoms with elevated partial charge / polar vulnerability.
   - **Moderate Polar Halos (Cyan):** Subtler halos marking secondary electronic soft spots.
   - **Heteroatom Badges:** Styled badges for N, O, S, F, Cl, Br, and P with distinct CPK-inspired colors.

---

## 5. Live Staging & Cloud Verification URLs

| Component | Target / Location | Verified Status |
| :--- | :--- | :--- |
| **Local Spike Notebook** | [`spikes/spike_02_vertical_slice.py`](../spikes/spike_02_vertical_slice.py) | Verified with `marimo check` (0 errors, 0 warnings) |
| **Payload Datasets** | `data/processed/slice_100_payload.json` (686 KB), `slice_100.csv` (9.4 KB) | Generated & checksummed |
| **Public GitHub Gist** | [Gist `58e1720ccf2c3455519a083cd94c58b0`](https://gist.github.com/RishyanthReddy/58e1720ccf2c3455519a083cd94c58b0) | Publicly accessible (HTTP 200) |
| **Live molab Cloud Staging**| [`https://molab.marimo.io/?url=https://gist.githubusercontent.com/...`](https://molab.marimo.io/?url=https://gist.githubusercontent.com/RishyanthReddy/58e1720ccf2c3455519a083cd94c58b0/raw/spike_02_vertical_slice.py) | **HTTP 200 OK in 1.26s** |
| **Self-Containment** | Embedded 59.5 KB gzipped Base64 fallback | Works 100% offline or on fresh containers |

---

## 6. Verification Gate Status for `EC-0-4-01`

- [x] 100-molecule stratified slice curated from primary OpenADMET data.
- [x] ECFP4 2,048-bit fingerprints generated; target leakage assertion passed.
- [x] 5-fold cross-validated baseline fitted and probabilities exported.
- [x] `BioactivationTracer` custom anywidget vector engine implemented and reactive.
- [x] Standalone Marimo notebook built with embedded 59.5 KB fallback.
- [x] Local boot latency verified (0.443s vs $< 3.0\text{s}$ SLA).
- [x] Live cloud verification on `molab.marimo.io` verified (1.26s vs $< 10.0\text{s}$ SLA).
