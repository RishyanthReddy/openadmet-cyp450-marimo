# DATASET AUDIT REPORT: OpenADMET & Octant Benchmarks
> **Generated at:** 2026-09-03 03:28:06 UTC
> **Task:** `EC-0-1-01` (Phase 0 Feasibility Spike)
> **Evaluator:** Antigravity / Senior Software Engineer Protocol

---

## 1. Executive Summary & Core Counts

| Dataset File | Role | Total Rows | Valid SMILES | Unique Can. SMILES | Unique InChIKeys | SHA-256 (first 10) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `cyp-challenge-TRAIN_TDI.csv` | Primary OpenADMET Train TDI | 6,145 | 6,145 | 6,145 | 6,145 | `b458f599a7...` |
| `cyp-challenge-TEST-BLINDED.csv` | OpenADMET Blinded Test | 750 | 750 | 750 | 750 | `a342f8444a...` |
| `octant_willitfly_github.tsv` | Octant willitfly (GitHub Raw) | 11,353 | 11,353 | 11,353 | 11,352 | `afb8482cad...` |
| `octant_reactivity.tsv` | Octant Reactivity (HF) | 2,446 | 2,446 | 1,223 | 1,223 | `efca9d8520...` |
| `octant_inhibition.tsv` | Octant Inhibition (HF) | 1,340 | 1,340 | 1,340 | 1,340 | `19e537166a...` |
| `octant_will_it_fly_hf.tsv` | Octant Will It Fly (HF) | 11,353 | 11,353 | 11,353 | 11,352 | `afb8482cad...` |

*Note: Octant well-level detailed files contain:*
- `inhibition_wells.tsv`: 16,931 rows (well-level replicates)
- `reactivity_wells.tsv`: 19,344 rows (well-level replicates)

---

## 2. OpenADMET Primary TDI Dataset Schema & Missingness

**Source File:** `cyp-challenge-TRAIN_TDI.csv` (6,145 rows)

| Column Name | Data Type | Null Count | Null % | Sample Values |
| :--- | :--- | :--- | :--- | :--- |
| `Molecule_Name` | `str` | 0 | 0.00% | OCNT-0000422, OCNT-0001882 |
| `SMILES` | `str` | 0 | 0.00% | CC1=C(O)C(C=O)=C(CO)C=N1, CC(C)(OC1=CC=C(Cl)C=C1)C(=O)O |
| `CYP2D6_is_TDI` | `object` | 4,648 | 75.64% | True, False |
| `CYP3A4_is_TDI` | `object` | 2,561 | 41.68% | False, False |
| `CYP1A2_pIC50_TDI_condition` | `float64` | 4,732 | 77.01% | 5.739094973, 5.025380082 |
| `CYP2C9_pIC50_TDI_condition` | `float64` | 4,860 | 79.09% | 2.026651913, 3.589719642 |
| `CYP2D6_pIC50_TDI_condition` | `float64` | 4,648 | 75.64% | 5.315580657, 4.647690993 |
| `CYP3A4_pIC50_TDI_condition` | `float64` | 2,562 | 41.69% | 2.004111803, 2.21348669 |
| `CYP1A2_pIC50_TDI_condition_conf_high` | `float64` | 4,732 | 77.01% | 5.86376175, 5.19299075 |
| `CYP2C9_pIC50_TDI_condition_conf_high` | `float64` | 4,860 | 79.09% | 3.1963435, 4.11831075 |
| `CYP2D6_pIC50_TDI_condition_conf_high` | `float64` | 4,648 | 75.64% | 5.4114455, 4.820231 |
| `CYP3A4_pIC50_TDI_condition_conf_high` | `float64` | 2,562 | 41.69% | 3.3099295, 3.5919875 |
| `CYP1A2_pIC50_TDI_condition_conf_low` | `float64` | 4,732 | 77.01% | 5.59861775, 4.86454325 |
| `CYP2C9_pIC50_TDI_condition_conf_low` | `float64` | 4,860 | 79.09% | 1.0599255, 2.38441425 |
| `CYP2D6_pIC50_TDI_condition_conf_low` | `float64` | 4,648 | 75.64% | 5.18083775, 4.52902975 |
| `CYP3A4_pIC50_TDI_condition_conf_low` | `float64` | 2,562 | 41.69% | 1.04638825, 1.06221575 |
| `CYP1A2_pIC50_TDI_condition_std` | `float64` | 4,732 | 77.01% | 0.06771313986, 0.0859224736 |
| `CYP2C9_pIC50_TDI_condition_std` | `float64` | 4,860 | 79.09% | 0.6291989748, 0.4431331534 |
| `CYP2D6_pIC50_TDI_condition_std` | `float64` | 4,648 | 75.64% | 0.05564188229, 0.07236323997 |
| `CYP3A4_pIC50_TDI_condition_std` | `float64` | 2,562 | 41.69% | 0.6519833739, 0.7209569597 |
| `CYP1A2_pIC50_direct_inhibition` | `float64` | 4,733 | 77.02% | 5.783014945, 5.053625558 |
| `CYP2C9_pIC50_direct_inhibition` | `float64` | 4,860 | 79.09% | 2.169687087, 2.834837307 |
| `CYP2D6_pIC50_direct_inhibition` | `float64` | 4,652 | 75.70% | 4.615706783, 4.45672162 |
| `CYP3A4_pIC50_direct_inhibition` | `float64` | 3,810 | 62.00% | 2.101240007, 2.577795577 |
| `CYP1A2_pIC50_direct_inhibition_conf_high` | `float64` | 4,733 | 77.02% | 5.880482, 5.14111975 |
| `CYP2C9_pIC50_direct_inhibition_conf_high` | `float64` | 4,860 | 79.09% | 3.2269215, 3.84599325 |
| `CYP2D6_pIC50_direct_inhibition_conf_high` | `float64` | 4,652 | 75.70% | 4.795599, 4.5979305 |
| `CYP3A4_pIC50_direct_inhibition_conf_high` | `float64` | 3,810 | 62.00% | 3.4523925, 3.71784025 |
| `CYP1A2_pIC50_direct_inhibition_conf_low` | `float64` | 4,733 | 77.02% | 5.68250125, 4.9507345 |
| `CYP2C9_pIC50_direct_inhibition_conf_low` | `float64` | 4,860 | 79.09% | 1.0699735, 1.18445625 |
| `CYP2D6_pIC50_direct_inhibition_conf_low` | `float64` | 4,652 | 75.70% | 4.4761265, 4.3383195 |
| `CYP3A4_pIC50_direct_inhibition_conf_low` | `float64` | 3,810 | 62.00% | 1.0483375, 1.140199 |
| `CYP1A2_pIC50_direct_inhibition_std` | `float64` | 4,733 | 77.02% | 0.04955124269, 0.04860521579 |
| `CYP2C9_pIC50_direct_inhibition_std` | `float64` | 4,860 | 79.09% | 0.6401651452, 0.7172113069 |
| `CYP2D6_pIC50_direct_inhibition_std` | `float64` | 4,652 | 75.70% | 0.08106933771, 0.06593245385 |
| `CYP3A4_pIC50_direct_inhibition_std` | `float64` | 3,810 | 62.00% | 0.6962576872, 0.7201463348 |

### Primary Target Label Distribution & Joint Missingness:

- **CYP3A4_is_TDI (Primary Target):**
  - Tested & Labeled: 3,584 compounds (764 True, 2,820 False; ~21.32% positive rate)
  - Missing/Unmeasured: 2,561 compounds (41.68% null)
- **CYP2D6_is_TDI (Replication Target):**
  - Tested & Labeled: 1,497 compounds (324 True, 1,173 False; ~21.64% positive rate)
  - Missing/Unmeasured: 4,648 compounds (75.64% null)

#### Joint Labeling Breakdown across the 6,145 Compounds:
- **Jointly Labeled (both CYP3A4 & CYP2D6):** **259 compounds (4.21%)**
- **Only CYP3A4 Labeled:** **3,325 compounds (54.11%)**
- **Only CYP2D6 Labeled:** **1,238 compounds (20.15%)**
- **Neither Labeled (Unlabeled/Direct only):** **1,323 compounds (21.53%)**

> [!CAUTION]
> **The Masking Mandate:** If a naive modeler ran `df.dropna(subset=['CYP3A4_is_TDI', 'CYP2D6_is_TDI'])`, they would retain only 259 compounds and **discard 5,886 compounds (95.79% of the dataset!)**.
> Our pipeline strictly enforces **isoform-specific boolean masks**, evaluating CYP3A4 on all 3,584 labeled compounds and CYP2D6 on all 1,497 labeled compounds.

---

## 3. Octant Reaction Phenotyping & Ionization Data

### A. Resolution of the 2,446 vs 2,442 Reactivity Count:
- **Pinned Artifact:** Hugging Face `openadmet/Octant_CYP_inhibition_reactivity_blog_release:reactivity.tsv`
- **SHA-256:** `efca9d8520d20d437651a700080fb05537553b497b791448b456897caee6df4b`
- **Verified Row Count:** Exactly **2,446 rows** (matching GitHub's `reactivity_processed.tsv` with 2,447 lines including header).
- *Finding:* The "2,442" figure was a minor prose discrepancy in the Hugging Face README dataset card text; the authoritative raw data file contains exactly 2,446 compound-enzyme measurements across 1,223 unique compounds.

### B. Resolution of the willitfly Duplicate InChIKey (11,353 rows vs 11,352 unique InChIKeys):
- **Affected Rows:**
  - Row 1086: `OCNT-2328658-BW-001` (SMILES: `CC1=CC(C=CC2=CC=C3C=C(N(C)C)C=CC3=[N+]2C)=C(C)N1C1=CC=CC=C1`, unspecified double bond stereochemistry)
  - Row 5569: `OCNT-2328450-CU-001` (SMILES: `CC1=CC(/C=C/C2=CC=C3C=C(N(C)C)C=CC3=[N+]2C)=C(C)N1C1=CC=CC=C1`, explicit *trans*/E double bond stereochemistry)
- **Root Cause:** Both rows represent separate physical synthesis batches with distinct measured ionization peak areas (Row 1086: NH4F=192,369.0, NH4FA=255,111.5; Row 5569: NH4F=118,090.0, NH4FA=93,021.5). Standard InChI generation maps unspecified double-bond geometry to the same connectivity/stereo layer (`QMHSXPLYMTVAMK-UHFFFAOYSA-N`).
- **Policy:** Both rows are preserved as authentic experimental measurements; neither is discarded.

### C. `willitfly.tsv` (GitHub Raw) Ionization Peak Areas:
- Total rows: 11,353
- Exact Column Names: `['ocnt_batch', 'ammonium_fluoride_area', 'ammonium_formate_area', 'standardized_smiles']`
- `ammonium_fluoride_area` (dtype: `float64`): mean = 71,759.05 (buffer-specific Echo-MS ionization QC signal in ammonium fluoride)
- `ammonium_formate_area` (dtype: `float64`): mean = 33,100.83 (buffer-specific Echo-MS ionization QC signal in ammonium formate)

> [!NOTE]
> Ionization peak areas represent **buffer-specific Echo-MS quality control measurements**, reflecting electrospray ionization response under specific mobile phase modifiers, not universal ionization behavior.

---

## 4. Chemical Overlap & Leakage Check

- **OpenADMET Unique InChIKeys:** 6,145
- **Octant Inhibition Unique InChIKeys:** 1,340
- **Octant willitfly Unique InChIKeys:** 11,352
- **Overlap Methodology:**
  - Calculated using **stereochemistry-exact full InChIKeys** generated by RDKit (`inchi.MolToInchiKey`).
  - All mappings are 1-to-1 deterministic with zero ambiguous multi-mappings.
- **Overlap Results:**
  - **Shared with Octant Inhibition:** **1,250 compounds** (20.34% of OpenADMET)
  - **Shared with Octant willitfly:** **4,396 compounds** (71.54% of OpenADMET)
  - *(Using the 14-character connectivity block skeleton, overlap with willitfly is 4,404 compounds).*

---

## 5. Blinded Test Set Isolation Protocol

- **Dataset File:** `cyp-challenge-TEST-BLINDED.csv` (750 rows, SHA-256: `a342f8444a...`)
- **Strict Quarantine:** The 750 blinded compounds are **permanently isolated**. They are strictly barred from:
  - Feature engineering or representation learning
  - Model training and hyperparameter optimization
  - Conformal calibration or threshold tuning
- **TxConformal Evaluation Protocol:** Conformal candidate-pool prioritization and FDR/FDP empirical simulations are conducted strictly on **repeated held-out candidate pools drawn from the 6,145 training compounds**. The blinded test set is reserved exclusively for a post-training unlabeled inference showcase in Act 5 if needed.

---

## 6. Verification Gate Status for `EC-0-1-01`

- [x] Raw OpenADMET files ingested and checksummed.
- [x] Raw Octant files ingested, pinned to SHA-256, and 2,446 count resolved.
- [x] willitfly duplicate InChIKey investigated (stereoisomer batches, both preserved).
- [x] Joint label counts quantified (259 both, avoiding 95.79% dropna data loss).
- [x] Deterministic full InChIKey overlap calculated (1,250 and 4,396 compounds).
- [x] Blinded test set permanently quarantined from training/calibration.
- [x] Target-leakage guardrail rules confirmed for `docs/ENDPOINT_DICTIONARY.md`.

