# Evidence ledger for the submission candidate

## Evidence boundaries

| Display | Source and population | Interpretation and limit |
|---|---|---|
| Molecular alerts and default halos | RDKit SMARTS in widgets/layout_engine.py; illustrative motif weights | A structural hypothesis; not experimental reactivity, a quantum atom calculation, or a safety probability. Caller-supplied atom values require an identity/atom mapping that is absent from default views. |
| Literature example | literature_mbi_reference_set.json and cached PubMed metadata | Literature evidence is isoform-specific. Cross-docking into another isoform does not transfer the demonstrated mechanism. |
| TDI endpoints | cyp_splits.parquet; endpoint-specific measured masks | Challenge labels include threshold/inference rules. An assay endpoint is distinct from proving irreversible inactivation. |
| Random vs scaffold scores | ecfp_baseline_results.json and dmpnn_baseline_results.json | Out-of-fold endpoint metrics; reported molecule-level bootstrap intervals are not a paired significance test. A smaller difference does not imply better absolute performance. |
| Chemical distance | tanimoto_shift_summary.json | Packaged mean/fraction summaries; random CV and scaffold holdout populations differ. Original decorative histogram bins lacked artifact support and were removed. |
| Descriptor augmentation | augmented_results.json, 3,584 CYP3A4 rows | PR-AUC 0.4652→0.4753; MCC 0.3298→0.3507; ROC-AUC 0.7868→0.7891; Brier 0.1573→0.1542. Observed changes only. Full cache lacks model/conformer provenance; do not claim every row is NSE. |
| Docking | docking_ablation_results.json, cyp2d6_docking_results.json | Vina CPU scoring and whole-ligand minimum iron distances. RTX 4090 worker provisioning does not mean GPU docking; the nearest atom may be unrelated to the reaction site. The UI is a result panel, not an interactive 3D pose viewer. |
| Molecular pairs/errors | mmp_transformations.json, oof_error_cases.json | Observed label differences/model errors; narratives are proposed explanations, not causal attribution. |
| Candidate p-values | txconformal_holdout.parquet and selection JSON | TRAIN 2,194 / CALIBRATION 687 / TEST 703, parent and nonempty-scaffold disjoint. Predictive labels use TRAIN only; density discriminator sees unlabeled CAL/TEST features, clipping weights to [0.1,10]. |
| Display and CSV | first 100 TEST rows in source order | Ordered convenience sample, not claimed representative. BH reruns on these 100 p-values at the active alpha. Stored flags, plot colors and export use this pool's selection. |
| Historical FDP | 250 pools of size 200 sampled with replacement from the 703 TEST rows | At alpha .10 mean FDP .0267, MC interval [.0230,.0304], mean selection size 30. Repeated resampling of one holdout is an empirical diagnostic, not independent prospective validation. |

The packager previously combined OOF scores with separate calibration data. It now consumes the dedicated TRAIN-only selector's full-precision holdout artifact, validates identities and hashes, and keeps error-inspection OOF scores separate. Ordinary BH with estimated weights is **TxConformal-inspired**, not a verified reproduction of every guarantee in the paper.

## Artifact hashes

| Artifact | SHA-256 |
|---|---|
| `data/curated/cyp_splits.parquet` | `ad7f84322a1e12b2d2cfc109b49e91f556336f831e1136b5ccc64147837ed6cd` |
| `data/curated/aimnet2_cyp3a4_features.parquet` | `51009632d9a881b0cdce0cf862ea304c265d13205efb017996e14983bbec20ee` |
| `data/packaged/txconformal_holdout.parquet` | `f27a6a28fe1a755bf5fdc0a897d1fb0d738bb1eec4f616b6cf176ffc54b0d86f` |
| `data/packaged/txconformal_selection_results.json` | `e930baae9da03e4cd99d97875a51a418a68e66dad0f5e9e5205449c5c49f6cf8` |
| `data/packaged/cyp_tdi_curated.parquet` | `6faaf1d741b33223916bfaf85cf8db6c29e332b7aef098916640eac63f19e2f2` |
| `data/packaged/augmented_results.json` | `593fa2baa7f835094dd2360b0c0dce2e7e52a3008cdca3bf0d0b68383f12bfc3` |
| `data/packaged/ecfp_baseline_results.json` | `cbbe0dbfecc2ab88245937956d88e5227f0adc6412a1074b9f58199623804102` |
| `data/packaged/dmpnn_baseline_results.json` | `847bca5c5f8fd783c7ba2f8da7e3af2508d78919d7739953ed5d4e8542e375fd` |

## Primary references

- [OpenADMET CYP Challenge tutorial](https://github.com/OpenADMET/CYP-Challenge-Tutorial).
- [AIMNet2 model guide](https://isayevlab.github.io/aimnetcentral/models/guide/) and [AIMNet2-NSE article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12851018/).
- [TxConformal preprint](https://doi.org/10.64898/2026.04.27.721076) and [author implementation](https://github.com/ying531/TxConformal).

No additional Beam computation was run for this candidate. The $25 approved ceiling remains unused. Actual atom-level quantum overlays and a stronger mechanistic validation experiment are deferred; neither is necessary for the corrected demonstration.
