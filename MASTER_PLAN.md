# MASTER PLAN: Deconstructing CYP Time-Dependent Inhibition
## When Do 2D Models Fail on New Scaffolds, and Do Bioactivation-Aware Features Help?

> **Target:** Bring Cheminformatics to Life — molab Notebook Competition #3 (OpenADMET × marimo)  
> **Judges:** Pat Walters (Chief Scientist, OpenADMET) + marimo core founding team  
> **Repository:** `/Users/rishyanthreddy/Desktop/Marimo`  
> **Operating Mode:** Two-File System (`MASTER_PLAN.md` + `TODO.md`)  
> **Branch Strategy:** Trunk-based with short-lived feature branches (`feat/<phase>-<topic>`)

---

## 0) Project Identity

- **Project Name:** `deconstructing-cyp-tdi` (Repo/Path: `/Users/rishyanthreddy/Desktop/Marimo`)
- **Submission Title:** *"Deconstructing CYP Time-Dependent Inhibition: When Do 2D Models Fail on New Scaffolds, and Do Bioactivation-Aware Features Help?"*
- **Target URL:** `https://molab.marimo.io` (Hosted self-contained Marimo notebook, CPU-only runtime, pinned `marimo==0.24.0`)
- **Status:** `in progress (Phase 0 Feasibility Spikes)`
- **Lead Methodology:** Empirical Benchmark & Forensic Audit + 100-Molecule Baseline Vertical Slice + Optional Physics-Grounded Ablations + `TxConformal` Candidate Selection + Bespoke Vector Anywidget (`BioactivationTracer`).

---

## 1) Goal

- **Primary Research Question (Falsifiable & Neutral):**  
  *When do conventional 2D machine learning models fail to predict Cytochrome P450 Time-Dependent Inhibition (CYP-TDI) on chemically novel scaffolds, and does augmenting representations with bioactivation-aware electronic or geometric features measurably improve generalization?*  
  *(Note: We test whether random splitting inflates apparent generalization relative to chemically grouped splitting, without assuming the direction or magnitude beforehand. A null or negative result—showing where bioactivation-aware features fail to improve upon 2D baselines—is explicitly accepted as a valid, high-impact scientific finding).*
- **Primary Product Goal:**  
  Deliver a genuinely self-contained, crash-proof Marimo notebook on `molab.marimo.io` that educates medicinal chemists on TDI assay interpretation, visualizes assay discrepancies and matched molecular pairs via a custom `BioactivationTracer` anywidget, and demonstrates covariate-shift-aware candidate prioritization using `TxConformal`.
- **Secondary Goals:**
  1. Build on the **6,145-compound OpenADMET CYP challenge dataset** as primary ground truth, focusing primarily on **CYP3A4** (with CYP2D6 as replication analysis), keeping Octant high-throughput data clearly demarcated as auxiliary reaction phenotyping context.
  2. Document Octant subsets with exact provenance: `inhibition` (1,340 compound-level rows), `inhibition_detailed` (16,931 well-level rows), `reactivity` (2,446 compound-enzyme rows), `reactivity_detailed` (19,344 well-level rows), and `will_it_fly` (11,353 rows). The combined ~51,400 figure represents the sum across all dataset configurations.
  3. Implement strict chemical leakage controls: dual SMILES representations (`assay_smiles` preserved for modeling; `grouping_parent_smiles` for duplicate grouping and scaffold partitioning), acyclic handling, Bemis-Murcko framework clustering, and Morgan fingerprint nearest-neighbor Tanimoto reporting.
  4. Execute strict **target-leakage guardrails**: structure-only models never receive direct pIC50, TDI-condition pIC50, Emax, or confidence bounds as features.
  5. De-risk feasibility through Phase 0 spikes (dataset audit, endpoint dictionary, minimal molab smoke test, and a 100-molecule baseline-only vertical slice) before any large-scale modeling.
  6. Ensure full alignment with *Nature Methods* DOME (Data, Optimization, Model, Evaluation) reporting guidelines.
  7. Achieve realistic runtime SLAs on `molab.marimo.io`: local cold boot $< 3\text{s}$, molab container boot $< 10\text{s}$, local JS feedback $< 100\text{ms}$, end-to-end reactive DAG p95 $< 500\text{ms}$, CPU-only execution, zero application-generated console errors, and a video walkthrough strictly under 5 minutes.

---

## 2) Context & Problem Statement

- **Current State:**  
  Conventional ADMET models treat molecules as static 2D topological graphs (Morgan fingerprints, GNNs, SMILES language models). We evaluate whether random splitting inflates apparent generalization metrics relative to chemically grouped splitting, testing the hypothesis that congeneric series overlap inflates benchmark performance.
- **The Core Scientific Reality (TDI vs. MBI):**  
  **TDI is an assay-observed increase in enzyme inhibition following preincubation.** Mechanism-based inactivation (MBI) via reactive bioactivation (e.g. Compound I $\text{Fe}^{\text{IV}}=\text{O}^{+\bullet}$ oxidation generating covalent adducts to heme or apoprotein) is one major cause of TDI, but **TDI labels alone do not establish an irreversible covalent mechanism** (quasi-irreversible metabolite-intermediate complexes, slow-binding tight reversible inhibitors, or assay artifacts can also produce TDI shifts; see EMA DDI Guidelines).  
  *Therefore, bioactivation-aware features may help explain a specific subset of TDI, but cannot be assumed to govern all TDI phenomena.*
- **The Modeling Dilemma:**  
  Structure-activity relationships for TDI can be discontinuous. Two compounds with identical 2D topological cores can have divergent TDI profiles due to subtle electronic stabilization of radical intermediates or steric orientation relative to the heme.
- **Why It Matters Now:**  
  TDI is a major cause of clinical drug-drug interactions and adverse events. OpenADMET released the first standardized community benchmark to evaluate predictive models.
- **Who Is Impacted:**  
  Medicinal chemists prioritizing chemical series, preclinical pharmacologists, and safety assessors.

---

## 3) Constraints & Boundaries

- **Tech Stack & Deployment Constraints:**
  - *Judge / Online Runtime:* Must run **100% CPU-only** in the sandboxed environment of `molab.marimo.io`. No runtime GPU dependency.
  - *Pinned Environment:* Pinned to `marimo==0.24.0`, Python 3.11+, standard PEP 723 inline dependency declarations (`# /// script ... # ///`). Zero binary compilation at runtime.
  - *Genuinely Self-Contained Single File Contract:* `app.py` contains inlined JS and CSS as raw multi-line strings for `BioactivationTracer` AND embeds all fallback assets (100-molecule fallback dataset, literature MBI reference set, and matched molecular pair transformations catalog) directly as gzip-compressed, base64-encoded JSON strings.
  - *Single-File Offline Acceptance Test:* Copy only `app.py` into an empty directory on a machine with Python dependencies pre-installed but networking disabled, launch via `marimo run app.py`, and confirm that the notebook boots in $< 3\text{s}$ and that every act renders cleanly in "offline sample mode" with a visible status banner (testing asset independence).
  - *Network Resilience:* Remote Parquet fetching incorporates timeout handling (15s), SHA-256 checksum verification, and 3-attempt exponential backoff, gracefully falling back to embedded assets upon network timeout or disconnect.
  - *Asset Footprint:* Total downloadable asset bundle (Parquet data + precomputed features) $\le 15\text{ MB}$, streaming from public CDN/GitHub releases with local in-memory caching.
  - *Frontend:* `anywidget>=0.9.13`, Python-side RDKit 2D depiction coordinates converted to JSON, client-side vanilla SVG rendering.
  - *Offline Compute:* Heavy computations (AIMNet2, docking) run offline; results are precomputed and frozen.
- **Target Leakage Guardrail (CRITICAL):**  
  **Structure-only predictive models must not receive direct pIC50, TDI-condition pIC50, Emax, confidence intervals, or any other assay-derived columns as input features.** Assay-derived columns are strictly reserved for ground-truth label derivation, error analysis, and visualization.
- **Dual SMILES Standardization Strategy:**
  - `assay_smiles`: Untouched source structure used for exact traceability and structure-based modeling.
  - `grouping_parent_smiles`: Standardized parent structure (desalted, neutralized) strictly used for duplicate grouping, clustering, and scaffold leakage prevention.
  - Failed sanitizations are quarantined with an audit log; no silent structure replacements.
- **Performance & Latency SLAs:**
  - Local cold boot time: $< 3$ seconds.
  - Molab cloud container boot time: Target $< 10$ seconds.
  - Local JavaScript click feedback: $< 100$ milliseconds.
  - End-to-end reactive DAG update (p95): $< 500$ milliseconds.
  - Console hygiene: Zero application-generated console errors or unhandled promise rejections; documented third-party warnings.
- **Explicit Non-Goals & Scope Boundaries:**
  1. We do *not* claim to have "solved" TDI prediction.
  2. We do *not* treat TDI as synonymous with covalent mechanism-based inactivation.
  3. We do *not* force bioactivation features to beat 2D baselines; null results are reported objectively.
  4. We do *not* require live arbitrary GNN inference in the browser (live editing is restricted to precomputed matched molecular pairs or clearly flagged 2D heuristic surrogates with applicability-domain warnings).
- **Phase 0 Decision Gates:**
  - *Gate 1 (AIMNet2-NSE Feasibility Spike):* Evaluated using `aimnet2-nse` with fixed nuclear geometry for open-shell states:
    $$IP_v = E(N-1) - E(N)$$
    $$EA_v = E(N) - E(N+1)$$
    Must pass charge-conservation, finite-energy, element-coverage, failure-rate ($<2\%$), conformer-sensitivity, and reproducibility checks on 50 test molecules, with qualitative validation against a cited IP/EA reference set. If failed, drop whole-dataset quantum featurization and rely on 2D physical-organic proxies.
  - *Gate 2 (Docking Feasibility Spike):* Docking is explicitly moved to a post-MVP stretch ablation (CYP3A4 2V0M/1TQN); not in the critical path.
  - *Gate 3 (ONNX Feasibility Spike):* Chemprop ONNX export is moved to a post-MVP stretch experiment; the primary Marimo app uses precomputed predictions.
  - *Gate 4 (molab Smoke Test):* Must boot minimal Marimo + Anywidget notebook on `molab.marimo.io` within 10 seconds.

---

## 4) Success Metrics (Measurable)

- [ ] **Metric 1 (Falsifiable Scientific Benchmark):** Objective comparison of 2D baselines (ECFP4, Chemprop D-MPNN) vs. bioactivation-augmented models across both Random 5-Fold CV and Grouped Scaffold splits (Grouped 5-Fold CV / Repeated Grouped Holdouts), reporting MCC, PR-AUC, Brier score, and calibration curves with chemical-group-level bootstrap 95% confidence intervals.
- [ ] **Metric 2 (Competition Rubric Target):** Target $\ge 92 / 100$ aggregate score evaluated against the official 6 criteria:
  - *Creativity & Impact (20%):* Deep forensic audit of TDI assay interpretation and failure modes.
  - *Customization (20%):* `BioactivationTracer` custom anywidget extending `marimo-chem-utils`.
  - *Interactivity & Workflow (20%):* Fluid Marimo reactive DAG without circular dependencies.
  - *Design & Presentation (20%):* DOME-aligned reporting, transparent AI disclosure, video under 5 min.
  - *Chemical Validity (10%):* Dual SMILES preservation, non-leaking grouped splits, authentic CYP chemistry.
  - *Code Quality & Clarity (10%):* Genuinely self-contained single-file `app.py` with embedded fallback assets, PEP 723 metadata, pinned `marimo==0.24.0`, 0 errors on molab.
- [ ] **Metric 3 (Leakage Control Integrity):** Zero shared grouping parents or Murcko frameworks between train and test partitions; report nearest-neighbor Tanimoto distribution across splits.
- [ ] **Metric 4 (100-Molecule Baseline Vertical Slice):** End-to-end working vertical slice (Data $\to$ Baseline $\to$ Widget $\to$ Marimo) completed by **September 10, 2026**.
- [ ] **Metric 5 (molab Zero-Disqualification SLA):** Clean CPU run, local boot $< 3\text{s}$, molab cold boot $< 10\text{s}$, p95 reactive DAG $< 500\text{ms}$, 0 unhandled application errors.

---

## 5) Architecture Snapshot

### 5.1 System Components

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        DECONSTRUCTING CYP-TDI: SYSTEM ARCHITECTURE                     │
└────────────────────────────────────────────────────────────────────────────────────────┘

[ TIER 0: PHASE 0 FEASIBILITY SPIKES ]
  ├─ Spike 0.1: Dataset Audit & Endpoint Dictionary (OpenADMET 6.1K vs Octant subsets)
  ├─ Spike 0.2: AIMNet2-NSE ΔSCF Energy & Atomic Charge-Response Benchmark (Gate 1)
  ├─ Spike 0.3: Minimal Anywidget Deployment to molab.marimo.io (Gate 4)
  └─ Spike 0.4: Baseline-Only 100-Molecule Vertical Slice (Milestone: Sept 10)
                               │
                               ▼
[ TIER 1: DATA FOUNDATION (Phase 1) ]
  ├─ Part 1.1: Primary OpenADMET Dataset (6,145 DRC compounds; CYP3A4 primary, 2D6 replication)
  ├─ Part 1.2: Auxiliary Octant Substrate Depletion (ammonium-fluoride & formate peak areas)
  ├─ Part 1.3: Leak-Free Splitting Engine (Grouped 5-Fold CV + Repeated Grouped Holdouts)
  └─ Part 1.4: Literature MBI Reference Set (literature_mbi_reference_set.json; evidence levels)
                               │
                               ▼
[ TIER 2: MODEL EVIDENCE & BENCHMARKING (Phase 2) ]
  ├─ Part 2.1: 2D Baselines (ECFP4 + Logistic/LightGBM, Chemprop v2 D-MPNN) across splits
  ├─ Part 2.2: Physics-Grounded Ablation (Conditional on Gate 1) & Post-MVP Stretch
  │             └─ MMP Extraction & Curation (`mmp_transformations.json`)
  ├─ Part 2.3: TxConformal Engine (Jin et al. 2026; candidate-pool prioritization under covariate shift)
  └─ Part 2.4: Precomputed Dataset Packaging (`cyp_tdi_curated.parquet` + embedded base64 fallback)
                               │
                               ▼
[ TIER 3: MARIMO REACTIVE APPLICATION (`app.py`) ]
  ├─ Act 1: What TDI Is — and What It Is Not (Preincubation shift, MBI vs non-covalent causes)
  ├─ Act 2: How Apparent Performance Changes After Chemical Leakage Control (Bathtub audit)
  ├─ Act 3: Do Bioactivation-Aware Features Add Information? (Falsifiable evidence & null discussions)
  ├─ Act 4: BioactivationTracer (Matched molecular pairs, out-of-fold errors, provenance halos)
  └─ Act 5: TxConformal Candidate Selection (Lower-TDI shortlist, limitations, DOME-aligned reporting)
```

### 5.2 Exact Endpoint Dictionary & Source Column Mappings

| Internal Field Name | Source Raw Column / File | Assay Nature | Role in Project | Missingness Policy |
| :--- | :--- | :--- | :--- | :--- |
| `cyp3a4_is_tdi` | `CYP3A4_is_TDI` | Binary preincubation shift | **Primary Target** | Filter to non-null for 3A4 modeling |
| `cyp2d6_is_tdi` | `CYP2D6_is_TDI` | Binary preincubation shift | **Replication Target** | Filter to non-null for 2D6 modeling |
| `cyp3a4_pic50_direct`| `CYP3A4_pIC50_direct_inhibition`| Direct-condition pIC50 | Analysis/Plotting ONLY | **Target Leakage: NEVER A FEATURE** |
| `cyp2d6_pic50_direct`| `CYP2D6_pIC50_direct_inhibition`| Direct-condition pIC50 | Analysis/Plotting ONLY | **Target Leakage: NEVER A FEATURE** |
| `cyp3a4_pic50_tdi_cond`| `CYP3A4_pIC50_TDI_condition`| Preincubated pIC50 | Analysis/Plotting ONLY | **Target Leakage: NEVER A FEATURE** |
| `cyp2d6_pic50_tdi_cond`| `CYP2D6_pIC50_TDI_condition`| Preincubated pIC50 | Analysis/Plotting ONLY | **Target Leakage: NEVER A FEATURE** |
| `substrate_depletion`| HF `reactivity:pct_remaining` | Echo-MS substrate loss | Auxiliary Context ONLY | Documented as reaction phenotyping (2,446 rows) |
| `ammonium_fluoride_area`| `willitfly.tsv:ammonium_fluoride_area`| Ionization peak area | QC Context ONLY | Quantitative ammonium fluoride signal (11,353 rows) |
| `ammonium_formate_area` | `willitfly.tsv:ammonium_formate_area` | Ionization peak area | QC Context ONLY | Quantitative ammonium formate signal (11,353 rows) |

*(Note: In accordance with data audit findings, rows with missing labels in one isoform are retained for the other isoform; models use endpoint-specific masking rather than dropping partially labeled compounds).*

### 5.3 TxConformal Candidate Prioritization Definition

Cited directly as:
> **Jin, Y., Huang, K., Diamant, N., et al. (2026).** *TxConformal: Controlling False Discoveries in AI-Driven Therapeutic Discovery*. bioRxiv. [doi:10.64898/2026.04.27.721076](https://doi.org/10.64898/2026.04.27.721076) (GitHub: `ying531/TxConformal`).

- **Candidate Selection Tool:** Used strictly as an interactive candidate-pool prioritization experiment under covariate shift, not as a generic per-molecule confidence interval engine.
- **Discovery Definition:** A compound selected as *non-TDI* (lower TDI liability) for the chosen isoform.
- **False Discovery Definition:** A selected compound whose true label is *TDI-positive*.
- **Statistical Evaluation Protocol:** Report mean empirical False Discovery Proportion (FDP), Monte Carlo uncertainty, selection set size, and statistical power across repeated held-out candidate-pool simulations; compare mean FDR with target threshold $\alpha$ without assuming or forcing a successful result. Document all covariate-shift weighting assumptions transparently.

### 5.4 Exact Atom Halo Contract in `BioactivationTracer`

To guarantee full chemical interpretability without misleading claims, every atom halo rendered by the custom anywidget is accompanied by an explicit metadata contract:
- `atom_score` (Float): Normalized scalar value driving halo radius and opacity.
- `score_type` (Enum): `calculated_electronic_proxy` | `model_attribution` | `literature_curated_site`.
- `score_source` (String): e.g., `AIMNet2-NSE_charge_response`, `Chemprop_integrated_gradients`, or `Literature_MBI_reference`.
- `normalization` (String): e.g., `min_max_per_mol` or `unit_sum`.
- `is_experimental` (Boolean): `True` only if experimentally verified in peer-reviewed literature; `False` for model predictions.
*(Rule: If AIMNet2 fails Gate 1, hide the electronic proxy layer or replace it with a clearly labeled model attribution layer; never display a generic "reactivity halo" without explicit provenance. All displayed model errors come strictly from out-of-fold or held-out test predictions).*

---

## 6) Phase Plan

### Phase 0: Scientific & Technical Feasibility Spikes (Immediate Priority)
- `0.1` Dataset Audit & Endpoint Dictionary (`docs/ENDPOINT_DICTIONARY.md`).
- `0.2` AIMNet2-NSE $\Delta\text{SCF}$ Feasibility Spike on 50 molecules (Gate 1).
- `0.3` Minimal molab.marimo.io Smoke Test on CPU (Gate 4).
- `0.4` 100-Molecule Baseline-Only Vertical Slice (Data $\to$ Baseline $\to$ Anywidget $\to$ Marimo) by **September 10, 2026**.

### Phase 1: Reproducible Data Foundation
- `1.1` Primary OpenADMET dataset curation (dual SMILES: `assay_smiles` vs `grouping_parent_smiles`).
- `1.2` Auxiliary Octant substrate depletion curation (`willitfly.tsv` ammonium fluoride/formate areas).
- `1.3` Leak-free splitting engine (Grouped 5-Fold CV + Repeated Grouped Holdouts; Murcko + Tanimoto).
- `1.4` Literature MBI Reference Set (`literature_mbi_reference_set.json`) with documented evidence levels.

### Phase 2: Empirical Benchmark & Evidence
- `2.1` 2D Baselines training (ECFP4 + Logistic/LightGBM, Chemprop D-MPNN) across splits.
- `2.2` Bioactivation feature ablation (conditional on Gate 1), post-MVP stretch, and Matched Molecular Pair (MMP) extraction (`mmp_transformations.json`).
- `2.3` `TxConformal` candidate-pool selection calibration with empirical FDP/FDR evaluation.
- `2.4` Packaging precomputed predictions into `cyp_tdi_curated.parquet` ($\le 12\text{ MB}$) with embedded base64 fallback assets.

### Phase 3: Marimo 5-Act Narrative & Custom Widget
- `3.1` `BioactivationTracer` anywidget (Python RDKit 2D JSON layout + client-side vanilla SVG).
- `3.2` Master `app.py` assembly (strictly 5 Acts; pinned `marimo==0.24.0`; inlined JS/CSS single-file).

### Phase 4: Reliability, molab QA & Submission
- `4.1` Chrome DevTools MCP automated console and DOM audit.
- `4.2` Live cloud verification on `molab.marimo.io`.
- `4.3` Defensive input fuzzing and graceful callouts.
- `4.4` Presentation walkthrough video ($< 5\text{ minutes}$) and submission by **October 1, 2026**.

---

## 10) Verification Matrix

| Category | Check | Method / Tool | Frequency | Target / Pass Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **Leakage Control** | Target leakage guardrail | Static code check / assert | Phase 1 & 2 | 0 assay columns in feature matrix |
| **Scaffold Isolation**| Grouped split leakage | RDKit Murcko & InChIKey | Phase 1 | 0 train/test overlap; Tanimoto shift reported |
| **Data Integrity** | Packaged data nulls | Parquet schema check | Phase 2 | Expected nulls match masks; no unexpected NaNs/infs |
| **Scientific Rigor** | Objective benchmark reporting | Group-level bootstrap 95% CIs | Phase 2 | Full reporting of MCC, PR-AUC, Brier; accept null |
| **Conformal Selection**| TxConformal candidate pool | Empirical FDP simulation | Phase 2 | Report mean FDP, MC uncertainty, size & power |
| **Frontend Hygiene** | Console & DOM audit | Chrome DevTools MCP | Phase 4 | 0 application errors, p95 DAG $< 500\text{ms}$ |
| **Cloud Runtime** | molab cloud deployment | HTTP probe / molab | Phase 4 | Local $<3\text{s}$, molab $< 10\text{s}$; assets $< 15\text{ MB}$; CPU |
| **Video Duration** | Presentation timebox | Video metadata check | Phase 4 | Strictly $< 5\text{ minutes}$ (JotForm rule) |

---

## 13) Decisions & Technical Debt Log

- **ADR-01: TDI Observation vs MBI Mechanism:** TDI is treated as an assay-observed preincubation shift; mechanism-based bioactivation is evaluated as an explanatory hypothesis for a subset of TDI, not an equivalence.
- **ADR-02: Target Leakage Prevention:** All assay-derived columns (`pIC50_direct`, `pIC50_TDI_condition`, `Emax`) are strictly barred from model feature inputs.
- **ADR-03: Dual-SMILES Policy:** Source structures are preserved untouched in `assay_smiles`; standardization is performed on `grouping_parent_smiles` for duplicate grouping and scaffold partitioning.
- **ADR-04: Genuinely Self-Contained Single File Deployment:** `app.py` has the anywidget JS/CSS inlined as raw strings and embeds the 100-compound fallback dataset, literature MBI reference set, and MMP catalog directly as inlined gzip-compressed base64 JSON strings, ensuring 100% autonomous cloud execution.
- **ADR-05: Network Resilience & Offline Fallback Test:** Remote Parquet fetching incorporates timeout, retry, and checksum validation, gracefully falling back to embedded assets; to be verified by running `app.py` in an empty directory with networking disabled.

---

## 14) Senior Engineering Principles & Cumulative Integration Doctrine

1. **Strict Task-by-Task Execution Discipline:**
   - Work proceeds strictly **one execution card at a time** (`EC-...`).
   - No rapid-completion bias, no rushing, no batching, and no skipping ahead.
   - Every task transitions deliberately: declared $\to$ marked `WIP` $\to$ implemented $\to$ verified via live automated command $\to$ logged $\to$ marked `DONE`.
2. **100% Real Only (Zero Mocks, Zero Simulations, Zero Placeholders):**
   - Strictly **no mock data, no synthetic dummy molecules, no simulated training curves, and no stubbed metrics**.
   - Every calculation runs against real chemical graphs from OpenADMET and Octant, real RDKit/MolVS routines, real model training, and real out-of-fold predictions.
3. **True Pipeline Integration Testing (Real Seams):**
   - Integration testing is explicitly distinguished from isolated unit testing.
   - Each Phase Seam test (`EC-INTEGRATION-P...`) exercises the **continuous end-to-end data pipeline**: the actual artifact output of Component $A$ is piped directly into Component $B$.
   - Verifies schema integrity, data types, null masks, coordinate geometries, and physical units across real module boundaries.
4. **Cumulative Regression Harness:**
   - Integration testing is **cumulative across all phases**.
   - Completing Phase 1 requires passing `tests/test_phase0_seam.py` and `tests/test_phase1_seam.py`.
   - Completing Phase 2 runs Phase 0 + Phase 1 + Phase 2.
   - Phase 4 runs the complete full-stack dry-run: Raw Ingestion $\to$ Splitting $\to$ Modeling $\to$ Packaging $\to$ Marimo DAG $\to$ Headless DevTools DOM.
   - Guarantees upstream modifications never silently corrupt downstream consumers.
5. **Cheminformatics & Machine Learning Guardrails:**
   - **Dual-SMILES Policy:** Untouched `assay_smiles` preserved for modeling; standardized `grouping_parent_smiles` used strictly for grouping and scaffold partitioning.
   - **Target-Leakage Ban:** Direct pIC50, TDI-condition pIC50, and Emax are barred from predictive features under automated assertions.
   - **Out-of-Fold Integrity:** Displayed model errors and calibration curves use strictly out-of-fold cross-validation or held-out test predictions—never in-sample training errors.
   - **Falsifiable Science:** We evaluate whether random splitting inflates apparent generalization and test physics features neutrally, accepting null or negative results as valuable scientific conclusions.

---

## 19) Two-File Operating Pattern

1. This `MASTER_PLAN.md` governs strategy, boundaries, decisions, and engineering doctrines.
2. `TODO.md` tracks active Execution Cards (`EC-...`), timeboxes, and change logs.
3. Work starts immediately with **Phase 0 Feasibility Spikes** to validate the 100-molecule vertical slice.

