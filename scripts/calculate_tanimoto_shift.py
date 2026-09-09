#!/usr/bin/env python3
"""
EC-1-3-02: Compute Nearest-Neighbor Tanimoto Distribution Across Splits.

Quantifies chemical distributional shift across splits:
  1. Computes Morgan fingerprints (radius 2, 2,048 bits) for all 6,145 compounds.
  2. For each 5-fold CV test fold, computes the nearest-neighbor Tanimoto similarity
     to the training set using RDKit's fast BulkTanimotoSimilarity.
  3. Computes the same for 60/20/20 holdouts (Test vs Train, Calibration vs Train).
  4. Generates a comparison against a naive random 5-fold split to demonstrate the
     degree of out-of-domain shift imposed by scaffold grouping.
  5. Computes parametric and non-parametric summary statistics (mean, std, min,
     p10, p25, median, p75, p90, max, fraction >= 0.6, fraction < 0.4).
  6. Exports to `data/curated/tanimoto_shift_summary.json`.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs
from rdkit.Chem import rdFingerprintGenerator

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_CURATED = BASE_DIR / "data" / "curated"
SPLITS_PARQUET = DATA_CURATED / "cyp_splits.parquet"
OUT_JSON = DATA_CURATED / "tanimoto_shift_summary.json"


def summarize_distribution(values: list[float] | np.ndarray) -> dict[str, float]:
    arr = np.array(values, dtype=float)
    return {
        "count": int(len(arr)),
        "mean": float(round(float(np.mean(arr)), 4)),
        "std": float(round(float(np.std(arr)), 4)),
        "min": float(round(float(np.min(arr)), 4)),
        "p10": float(round(float(np.percentile(arr, 10)), 4)),
        "p25": float(round(float(np.percentile(arr, 25)), 4)),
        "median": float(round(float(np.median(arr)), 4)),
        "p75": float(round(float(np.percentile(arr, 75)), 4)),
        "p90": float(round(float(np.percentile(arr, 90)), 4)),
        "max": float(round(float(np.max(arr)), 4)),
        "fraction_high_similarity_ge_0_6": float(round(float(np.mean(arr >= 0.6)), 4)),
        "fraction_novel_chemotypes_lt_0_4": float(round(float(np.mean(arr < 0.4)), 4)),
    }


def compute_tanimoto_shifts() -> dict:
    print(f"Loading partitioned dataset from {SPLITS_PARQUET}...")
    df = pd.read_parquet(SPLITS_PARQUET)
    assert len(df) == 6145

    print("Generating 2,048-bit Morgan Fingerprints (radius=2)...")
    t0 = time.time()
    mfp_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = [mfp_gen.GetFingerprint(Chem.MolFromSmiles(smi)) for smi in df["assay_smiles"]]
    print(f"Computed {len(fps)} fingerprints in {time.time() - t0:.2f}s.")

    results = {
        "metadata": {
            "num_compounds": len(df),
            "fingerprint": "Morgan",
            "radius": 2,
            "n_bits": 2048,
            "created_at": "2026-09-03",
        },
        "cv_folds_scaffold": {},
        "holdout_scaffold": {},
        "random_baseline_comparison": {},
    }

    # 1. 5-Fold Cluster-Stratified Murcko Scaffold CV
    print("\nEvaluating 5-Fold Cluster-Stratified Murcko Scaffold Splits:")
    all_fold_nn_sims = []
    for f in range(5):
        test_indices = np.where(df["cv_fold_5"] == f)[0]
        train_indices = np.where(df["cv_fold_5"] != f)[0]

        test_fps = [fps[i] for i in test_indices]
        train_fps = [fps[i] for i in train_indices]

        nn_sims = []
        for fp in test_fps:
            sims = DataStructs.BulkTanimotoSimilarity(fp, train_fps)
            nn_sims.append(max(sims))

        all_fold_nn_sims.extend(nn_sims)
        summary = summarize_distribution(nn_sims)
        results["cv_folds_scaffold"][f"fold_{f}"] = summary
        print(f"  Fold {f}: Mean={summary['mean']:.3f} | Median={summary['median']:.3f} | P90={summary['p90']:.3f} | Novel(<0.4)={summary['fraction_novel_chemotypes_lt_0_4']*100:.1f}%")

    results["cv_folds_scaffold"]["overall_cv_mean"] = summarize_distribution(all_fold_nn_sims)

    # 2. 60/20/20 Holdout Partition
    print("\nEvaluating 60/20/20 Holdout Partitions:")
    train_idx = np.where(df["holdout_split"] == "TRAIN")[0]
    calib_idx = np.where(df["holdout_split"] == "CALIBRATION")[0]
    test_idx = np.where(df["holdout_split"] == "TEST")[0]

    train_fps = [fps[i] for i in train_idx]
    calib_fps = [fps[i] for i in calib_idx]
    test_fps = [fps[i] for i in test_idx]

    # Test vs Train
    test_nn = [max(DataStructs.BulkTanimotoSimilarity(fp, train_fps)) for fp in test_fps]
    results["holdout_scaffold"]["test_vs_train"] = summarize_distribution(test_nn)

    # Calibration vs Train
    calib_nn = [max(DataStructs.BulkTanimotoSimilarity(fp, train_fps)) for fp in calib_fps]
    results["holdout_scaffold"]["calibration_vs_train"] = summarize_distribution(calib_nn)

    print(f"  Test vs Train:        Mean={results['holdout_scaffold']['test_vs_train']['mean']:.3f} | Median={results['holdout_scaffold']['test_vs_train']['median']:.3f} | P90={results['holdout_scaffold']['test_vs_train']['p90']:.3f}")
    print(f"  Calibration vs Train: Mean={results['holdout_scaffold']['calibration_vs_train']['mean']:.3f} | Median={results['holdout_scaffold']['calibration_vs_train']['median']:.3f} | P90={results['holdout_scaffold']['calibration_vs_train']['p90']:.3f}")

    # 3. Naive Random 5-Fold Comparison (for scientific benchmarking)
    print("\nEvaluating Naive Random 5-Fold Comparison:")
    np.random.seed(42)
    random_folds = np.random.randint(0, 5, size=len(df))
    random_all_nn = []
    for f in range(5):
        test_i = np.where(random_folds == f)[0]
        train_i = np.where(random_folds != f)[0]
        test_f = [fps[i] for i in test_i]
        train_f = [fps[i] for i in train_i]

        r_sims = [max(DataStructs.BulkTanimotoSimilarity(fp, train_f)) for fp in test_f]
        random_all_nn.extend(r_sims)

    results["random_baseline_comparison"] = summarize_distribution(random_all_nn)
    print(f"  Random 5-Fold Overall: Mean={results['random_baseline_comparison']['mean']:.3f} | Median={results['random_baseline_comparison']['median']:.3f} | P90={results['random_baseline_comparison']['p90']:.3f} | Novel(<0.4)={results['random_baseline_comparison']['fraction_novel_chemotypes_lt_0_4']*100:.1f}%")
    print(f"  Distributional Shift Effect: Scaffold split decreases median NN similarity by {results['random_baseline_comparison']['median'] - results['cv_folds_scaffold']['overall_cv_mean']['median']:.3f} Tanimoto units!")

    # Save JSON summary
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSuccessfully exported Tanimoto shift summary to {OUT_JSON} ({OUT_JSON.stat().st_size:,} bytes).")
    return results


if __name__ == "__main__":
    compute_tanimoto_shifts()
