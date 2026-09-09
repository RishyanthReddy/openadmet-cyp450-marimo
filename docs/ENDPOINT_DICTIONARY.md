# ENDPOINT DICTIONARY & TARGET LEAKAGE GUARDRAIL CONTRACT
## Deconstructing CYP Time-Dependent Inhibition (CYP-TDI)

> **Document Status:** Active Engineering Contract  
> **Paired Task:** `EC-0-1-02` (Phase 0 Feasibility Spike)  
> **Source Commit / Hash:** Frozen via `spikes/spike_01_dataset_audit.py` on 2026-09-03  
> **Governing Plans:** [`MASTER_PLAN.md`](../MASTER_PLAN.md) §5.2 & [`TODO.md`](../TODO.md)

---

## 1. Pinned Source Artifacts & Provenance

Every dataset used in this project is pinned to an authoritative upstream URL, immutable SHA-256 checksum, and verified row count.

| Artifact File | Authoritative Source Repository | Exact SHA-256 Hash (64-char) | Verified Rows | Role in Project |
| :--- | :--- | :--- | :---: | :--- |
| `cyp-challenge-TRAIN_TDI.csv` | `openadmet/cyp-challenge-train-test` (Hugging Face) | `b458f599a792412292664386e8f18adc5d4a4129d6bd212ae80a60fb9b96bb60` | 6,145 | **Primary Ground Truth Benchmark** |
| `cyp-challenge-TEST-BLINDED.csv` | `openadmet/cyp-challenge-train-test` (Hugging Face) | `a342f8444a8dcb531ca12f3685293f0bd6c36ae9073f491e44a9bc1cc4b741f9` | 750 | **Quarantined Blinded Test Set** (Zero Training/Calibration Influence) |
| `cyp-challenge-TRAIN_inhibition.csv` | `openadmet/cyp-challenge-train-test` (Hugging Face) | `b8f79addd266fb6f9f4c222c5e4e73d926362328b6a8d2841871a54e46bd2278` | 4,905 | Contextual Reference (Single-point IC50 data) |
| `cyp-challenge-TRAIN_Emax.csv` | `openadmet/cyp-challenge-train-test` (Hugging Face) | `482f686a9a9f9166f290e6f5ea463a99de1da478b179a88f4baef48bc66501f1` | 6,145 | Contextual Reference (Dose-response curve plateau) |
| `reactivity.tsv` | `openadmet/Octant_CYP_inhibition_reactivity_blog_release` (HF) | `efca9d85202f215edeb929d3786693359589ea83071a3ebcbe1de79318e24834` | 2,446 | **Auxiliary Context:** Echo-MS substrate depletion (`pct_remaining`) |
| `inhibition.tsv` | `openadmet/Octant_CYP_inhibition_reactivity_blog_release` (HF) | `19e537166a17a42dd50cc262dd6eb0a963c181830fdc52db0fba98533e01c9c6` | 1,340 | **Auxiliary Context:** High-throughput direct pIC50 curves |
| `willitfly.tsv` | `OpenADMET/Octant_CYP_blog_post/data/willitfly.tsv` (GitHub) | `afb8482cad6910fce18c14661810b2c3342797fd60833e6daba9065f5cb18d37` | 11,353 | **QC Context:** Quantitative electrospray ionization peak areas |

*(Note: The Hugging Face dataset card description for `reactivity.tsv` informally cited 2,442 rows; our SHA-256 audited count confirms exactly 2,446 compound-enzyme rows matching GitHub's `reactivity_processed.tsv` with 2,447 lines including header).*

---

## 2. Comprehensive Endpoint Dictionary

This table defines the unambiguous semantic identity, physical units, experimental technology, and project role for each endpoint:

| Internal Identifier | Raw Source Column | Origin File | Experimental Technology & Protocol | Units | Role in Project | Missingness & Mask Policy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `cyp3a4_is_tdi` | `CYP3A4_is_TDI` | `cyp-challenge-TRAIN_TDI.csv` | Recombinant CYP3A4 + NADPH preincubation (30 min vs 0 min); binary preincubation shift ($\ge 1.5$ to $2.0$-fold $\text{IC}_{50}$ ratio). | Binary (`bool`: `True`/`False`) | **Primary Target Endpoint** | 3,584 labeled (764 True, 2,820 False); 2,561 null (41.68%). Filter via `mask_cyp3a4`. |
| `cyp2d6_is_tdi` | `CYP2D6_is_TDI` | `cyp-challenge-TRAIN_TDI.csv` | Recombinant CYP2D6 + NADPH preincubation (30 min vs 0 min); binary preincubation shift ($\ge 1.5$ to $2.0$-fold $\text{IC}_{50}$ ratio). | Binary (`bool`: `True`/`False`) | **Replication Target Endpoint** | 1,497 labeled (324 True, 1,173 False); 4,648 null (75.64%). Filter via `mask_cyp2d6`. |
| `cyp3a4_pic50_direct` | `CYP3A4_pIC50_direct_inhibition` | `cyp-challenge-TRAIN_TDI.csv` | Standard direct inhibition without preincubation (0 min preincubation); $-\log_{10}(\text{IC}_{50}\text{ [M]})$. | Molar $-\log_{10}$ (`float64`) | **Plotting / Analysis ONLY** | 2,335 measured (62.00% null). **STRICT LEAKAGE GUARD: NEVER A FEATURE.** |
| `cyp2d6_pic50_direct` | `CYP2D6_pIC50_direct_inhibition` | `cyp-challenge-TRAIN_TDI.csv` | Standard direct inhibition without preincubation (0 min preincubation); $-\log_{10}(\text{IC}_{50}\text{ [M]})$. | Molar $-\log_{10}$ (`float64`) | **Plotting / Analysis ONLY** | 1,493 measured (75.70% null). **STRICT LEAKAGE GUARD: NEVER A FEATURE.** |
| `cyp3a4_pic50_tdi_cond`| `CYP3A4_pIC50_TDI_condition` | `cyp-challenge-TRAIN_TDI.csv` | Preincubated inhibition (30 min preincubation with NADPH); $-\log_{10}(\text{IC}_{50}\text{ [M]})$. | Molar $-\log_{10}$ (`float64`) | **Plotting / Analysis ONLY** | 3,583 measured (41.69% null). **STRICT LEAKAGE GUARD: NEVER A FEATURE.** |
| `cyp2d6_pic50_tdi_cond`| `CYP2D6_pIC50_TDI_condition` | `cyp-challenge-TRAIN_TDI.csv` | Preincubated inhibition (30 min preincubation with NADPH); $-\log_{10}(\text{IC}_{50}\text{ [M]})$. | Molar $-\log_{10}$ (`float64`) | **Plotting / Analysis ONLY** | 1,497 measured (75.64% null). **STRICT LEAKAGE GUARD: NEVER A FEATURE.** |
| `substrate_depletion` | `pct_remaining` | `reactivity.tsv` (HF) | Acoustic droplet ejection Echo-MS measurement of test substrate loss after 60-min microsomal incubation. | Percentage ($0 - 150\%+$) | **Auxiliary Context ONLY** | 2,446 compound-enzyme rows (1,223 compounds). Documented as reaction phenotyping. |
| `ammonium_fluoride_area` | `ammonium_fluoride_area` | `willitfly.tsv` (GitHub) | High-throughput electrospray ionization (ESI) MS peak area in ammonium fluoride buffer modifier. | Arbitrary MS Area Units (`float64`) | **Analytical QC Context ONLY** | 11,353 rows (mean: 71,759.05). Indicates buffer-specific ionization quality. |
| `ammonium_formate_area` | `ammonium_formate_area` | `willitfly.tsv` (GitHub) | High-throughput electrospray ionization (ESI) MS peak area in ammonium formate buffer modifier. | Arbitrary MS Area Units (`float64`) | **Analytical QC Context ONLY** | 11,353 rows (mean: 33,100.83). Indicates buffer-specific ionization quality. |

---

## 3. Strict Target-Leakage Guardrail Contract

### The Rule
> **Target Leakage Prohibition:** Under NO circumstances may any predictive model receive `pIC50_direct_inhibition`, `pIC50_TDI_condition`, `Emax`, confidence bounds (`conf_high`, `conf_low`), standard deviations (`std`), or any other assay-derived columns as input features.

### Why This is Critical
In the OpenADMET dataset, `CYP3A4_is_TDI` is calculated by the assay provider directly from the shift between `CYP3A4_pIC50_TDI_condition` and `CYP3A4_pIC50_direct_inhibition`.  
If a predictive model were provided `pIC50_direct` or `pIC50_TDI_condition` as features, it would trivially learn the arithmetic difference between the two columns, achieving a fraudulent $>99\%$ ROC-AUC. 

### Automated Architectural Enforcement
All feature extraction and dataset preparation pipelines must pass the following programmatic assertion before model training:

```python
FORBIDDEN_FEATURE_SUBSTRINGS = [
    "pic50", "tdi_condition", "direct_inhibition", 
    "conf_high", "conf_low", "std", "emax", 
    "is_tdi", "pct_remaining", "area"
]

def assert_zero_target_leakage(feature_columns: list[str]) -> None:
    """Enforce strict separation between structure inputs and experimental assay outputs."""
    for col in feature_columns:
        col_lower = col.lower()
        for forbidden in FORBIDDEN_FEATURE_SUBSTRINGS:
            assert forbidden not in col_lower, (
                f"FATAL TARGET LEAKAGE DETECTED: Feature column '{col}' matches "
                f"forbidden pattern '{forbidden}'. Structure-only models must never "
                f"receive assay-derived values as input features."
            )
```

---

## 4. Dual-SMILES Policy & Standardization Contract

To balance experimental fidelity with rigorous chemical leakage prevention, every compound is represented by two parallel SMILES fields:

1. **`assay_smiles` (Preserved Untouched Source Structure):**
   * **Definition:** The exact, unmodified SMILES string provided in the raw OpenADMET assay file.
   * **Usage:** Used as the definitive ground-truth chemical structure for 2D molecular graph featurization (Chemprop D-MPNN), 3D conformer generation (AIMNet2-NSE), and visualization in the `BioactivationTracer` anywidget.
   * **Integrity:** Never desalted, never neutralized, never stripped of counterions or stereochemistry flags.
2. **`grouping_parent_smiles` (Standardized Parent Structure):**
   * **Definition:** The parent molecule derived via MolVS / RDKit standardization:
     - Stripped of inorganic salts and solvent counterions (`Standardizer.disconnect_metals`, `SaltRemover`).
     - Neutralized to uncharged state where chemically valid (`Standardizer.neutralize_charges`).
     - Largest organic fragment retained.
   * **Usage:** Used **strictly and exclusively** for:
     - Detecting identical duplicate parents across assay rows.
     - Partitioning train, validation, and test splits (Grouped 5-Fold CV and Repeated Grouped Holdouts).
     - Clustered Bemis-Murcko framework calculation.
   * **Rule:** `grouping_parent_smiles` is never fed into the 3D quantum engine, ensuring conformers reflect the actual assayed species.

---

## 5. Missingness & Masking Contract

The dataset audit revealed the following joint missingness structure across the 6,145 compounds:

```
Total Compounds: 6,145
  ├─ Jointly Labeled (both CYP3A4 & CYP2D6):       259 ( 4.21%)
  ├─ Only CYP3A4 Labeled:                        3,325 (54.11%)
  ├─ Only CYP2D6 Labeled:                        1,238 (20.15%)
  └─ Neither Labeled (Unmeasured/Direct only):   1,323 (21.53%)
```

### The Dual-Masking Rule
* **Prohibition:** Code must **never** call `df.dropna(subset=['CYP3A4_is_TDI', 'CYP2D6_is_TDI'])`. Doing so would discard 5,886 rows (**95.79% of the dataset**) and ruin statistical power.
* **Contract:** Every dataframe loaded into memory carries two explicit boolean mask columns:
  * `mask_cyp3a4 = ~df['cyp3a4_is_tdi'].isna()` (Yields 3,584 valid training/evaluation rows).
  * `mask_cyp2d6 = ~df['cyp2d6_is_tdi'].isna()` (Yields 1,497 valid training/evaluation rows).
* **Modeling Strategy:** Models predicting CYP3A4 calculate loss and validation metrics strictly on `mask_cyp3a4 == True`. Multi-task models apply loss masking per head.

---

## 6. Blinded Test Set Isolation Contract

* **File:** `cyp-challenge-TEST-BLINDED.csv` (750 compounds, SHA-256: `a342f8444a...`)
* **Strict Quarantine:** The 750 blinded molecules are permanently isolated from all model development:
  1. Never merged into training, validation, or cross-validation folds.
  2. Never used to fit standardizers, scalers, or dimensionality reduction models.
  3. Never used to tune hyperparameters, calibration curves, or decision thresholds.
* **Conformal Selection Evaluation Protocol:** All `TxConformal` empirical False Discovery Proportion (FDP) simulations, power evaluations, and candidate-pool selections are conducted on **repeated held-out candidate pools sampled strictly from the 6,145 training compounds**. The 750 blinded molecules are reserved exclusively for an optional final demonstration in Act 5.

---

## 7. Chemical Nuance Dictionary

To ensure flawless scientific communication in the Marimo application, the following chemical terminology distinctions are strictly enforced:

| Term / Concept | Scientifically Correct Definition | Forbidden / Misleading Usage | Rationale |
| :--- | :--- | :--- | :--- |
| **Time-Dependent Inhibition (TDI)** | An assay-observed increase in enzyme inhibition potency following a 30-minute preincubation with NADPH. | *"Mechanism-based inactivation (MBI)"* or *"Covalent adduct formation"* | TDI is an empirical assay observation. While MBI is a major cause, slow-binding tight reversible inhibition, metabolite-intermediate complexes, or assay artifacts can also cause TDI shifts (EMA DDI Guidelines). |
| **TDI-Positive Liabilities** | Compounds exhibiting assay-confirmed preincubation potency shifts. | *"Reactive liabilities"* or *"Metabolic warheads"* | Labeling all TDI compounds as "reactive" is chemically inaccurate; bioactivation explains a specific subset of TDI, not all. |
| **Echo-MS Ionization Peak Areas** | Quantitative mass spectrometry signal response in specific buffer modifiers (ammonium fluoride or ammonium formate). | *"Proof that a compound universally flies"* | Ionization in electrospray mass spectrometry is buffer-dependent, matrix-dependent, and source-dependent. High peak area indicates favorable ionization under the tested assay conditions. |
| **Bioactivation-Aware Features** | Calculated vertical ionization potentials ($IP_v$), electron affinities ($EA_v$), and atomic charge responses from `aimnet2-nse` representing electronic susceptibility to radical oxidation. | *"Proven metabolic soft spots"* or *"Direct radical spin densities"* | AIMNet2 computes vertical energy deltas and charge responses; it does not simulate full CYP heme-coordinated reaction pathways. |

---

## 8. Verification & Acceptance Gate

- [x] All 7 source artifacts pinned with exact 64-character SHA-256 hashes and row counts.
- [x] All 9 endpoints mapped with units, experimental protocols, and missingness masks.
- [x] Target leakage prohibition codified with automated code assertion template.
- [x] Dual-SMILES policy defined (`assay_smiles` vs `grouping_parent_smiles`).
- [x] Dual-masking policy codified, mathematically preventing 95.79% data loss.
- [x] Blinded test set isolation protocol codified.
- [x] Chemical nuance definitions codified to guarantee educational rigor in the Marimo notebook.
