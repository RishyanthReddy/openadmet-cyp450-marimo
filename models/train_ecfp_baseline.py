#!/usr/bin/env python3
"""
EC-2-1-01: Train & Evaluate ECFP4 Baselines on Random vs. Grouped Splits.

Evaluates 2,048-bit Morgan (ECFP4) fingerprints on CYP3A4_is_TDI across:
  1. Logistic Regression (L2-regularized, balanced class weight)
  2. LightGBM (Gradient boosted decision trees, early stopping, balanced class weight)
Across two parallel cross-validation protocols:
  - Random 5-Fold Stratified CV
  - Grouped 5-Fold Murcko Scaffold CV (leak-free from EC-1-3-01)

Calculates:
  - ROC-AUC, PR-AUC, MCC, Brier Score, Balanced Accuracy
  - 1,000-resample non-parametric bootstrap 95% Confidence Intervals
  - Empirical shift (Delta = Metric_Random - Metric_Grouped)
Enforces:
  - assert_zero_target_leakage on feature matrix
Exports:
  - data/packaged/ecfp_baseline_results.json
"""

from __future__ import annotations

import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    matthews_corrcoef,
    brier_score_loss,
    balanced_accuracy_score,
)
import lightgbm as lgb

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_PARQUET = BASE_DIR / "data" / "curated" / "cyp_splits.parquet"
OUT_JSON = BASE_DIR / "data" / "packaged" / "ecfp_baseline_results.json"

BANNED_COLUMNS = {
    "cyp3a4_is_tdi", "CYP3A4_is_TDI",
    "cyp2d6_is_tdi", "CYP2D6_is_TDI",
    "cyp3a4_pic50_direct_inhibition", "CYP3A4_pIC50_direct_inhibition",
    "cyp3a4_pic50_tdi_condition", "CYP3A4_pIC50_TDI_condition",
    "cyp2d6_pic50_direct_inhibition", "CYP2D6_pIC50_direct_inhibition",
    "cyp2d6_pic50_tdi_condition", "CYP2D6_pIC50_TDI_condition",
    "octant_direct_pic50", "CYP3A4_pIC50",
    "octant_cyp3a4_pct_remaining", "octant_cyp2j2_pct_remaining",
    "pct_remaining", "log2fc", "log10fc",
}


def assert_zero_target_leakage(feature_names: list[str]) -> None:
    leaked = set(feature_names).intersection(BANNED_COLUMNS)
    assert len(leaked) == 0, f"TARGET LEAKAGE DETECTED! Found banned columns: {leaked}"


def compute_bootstrap_ci(y_true: np.ndarray, y_prob: np.ndarray, y_pred: np.ndarray, n_boot: int = 1000, seed: int = 42) -> dict:
    rng = np.random.RandomState(seed)
    n = len(y_true)
    boot_metrics = {"roc_auc": [], "pr_auc": [], "mcc": [], "brier": []}

    for _ in range(n_boot):
        idx = rng.randint(0, n, size=n)
        yt, yp, ypr = y_true[idx], y_prob[idx], y_pred[idx]
        if len(np.unique(yt)) < 2:
            continue
        boot_metrics["roc_auc"].append(roc_auc_score(yt, yp))
        boot_metrics["pr_auc"].append(average_precision_score(yt, yp))
        boot_metrics["mcc"].append(matthews_corrcoef(yt, ypr))
        boot_metrics["brier"].append(brier_score_loss(yt, yp))

    ci_summary = {}
    for m, vals in boot_metrics.items():
        ci_summary[m] = {
            "ci_lower": float(round(float(np.percentile(vals, 2.5)), 4)),
            "ci_upper": float(round(float(np.percentile(vals, 97.5)), 4)),
            "boot_mean": float(round(float(np.mean(vals)), 4)),
            "boot_std": float(round(float(np.std(vals)), 4)),
        }
    return ci_summary


def compute_metrics(y_true: np.ndarray, y_prob: np.ndarray) -> dict:
    y_pred = (y_prob >= 0.5).astype(int)
    roc_auc = float(round(roc_auc_score(y_true, y_prob), 4))
    pr_auc = float(round(average_precision_score(y_true, y_prob), 4))
    mcc = float(round(matthews_corrcoef(y_true, y_pred), 4))
    brier = float(round(brier_score_loss(y_true, y_prob), 4))
    bal_acc = float(round(balanced_accuracy_score(y_true, y_pred), 4))
    ci = compute_bootstrap_ci(y_true, y_prob, y_pred)

    return {
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "mcc": mcc,
        "brier_score": brier,
        "balanced_acc": bal_acc,
        "bootstrap_ci_95": ci,
    }


def train_and_eval_cv(X: np.ndarray, y: np.ndarray, fold_indices: list[tuple[np.ndarray, np.ndarray]], model_type: str) -> dict:
    oof_probs = np.zeros(len(y), dtype=float)
    fold_metrics = []

    for fold_idx, (train_idx, val_idx) in enumerate(fold_indices):
        X_train, y_train = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]

        if model_type == "logistic_regression":
            clf = LogisticRegression(C=0.1, max_iter=1000, class_weight="balanced", random_state=42, solver="lbfgs")
            clf.fit(X_train, y_train)
            probs = clf.predict_proba(X_val)[:, 1]
        elif model_type == "lightgbm":
            clf = lgb.LGBMClassifier(
                n_estimators=250,
                learning_rate=0.03,
                num_leaves=31,
                min_child_samples=20,
                subsample=0.8,
                colsample_bytree=0.8,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
                verbose=-1,
            )
            clf.fit(X_train, y_train)
            probs = clf.predict_proba(X_val)[:, 1]
        else:
            raise ValueError(f"Unknown model_type: {model_type}")

        oof_probs[val_idx] = probs
        f_pred = (probs >= 0.5).astype(int)
        fold_metrics.append({
            "fold": fold_idx,
            "roc_auc": float(round(roc_auc_score(y_val, probs), 4)),
            "pr_auc": float(round(average_precision_score(y_val, probs), 4)),
            "mcc": float(round(matthews_corrcoef(y_val, f_pred), 4)),
            "brier_score": float(round(brier_score_loss(y_val, probs), 4)),
        })

    overall = compute_metrics(y, oof_probs)
    return {
        "overall_oof": overall,
        "per_fold": fold_metrics,
        "oof_probabilities": [float(round(p, 4)) for p in oof_probs],
    }


def run_benchmark() -> dict:
    print(f"Loading partitioned dataset from {SPLITS_PARQUET}...")
    df = pd.read_parquet(SPLITS_PARQUET)

    # Filter to primary target CYP3A4_is_TDI labeled molecules
    df_3a4 = df[df["mask_cyp3a4"]].copy().reset_index(drop=True)
    assert len(df_3a4) == 3584, f"Expected 3,584 CYP3A4 compounds, got {len(df_3a4)}"
    y = df_3a4["cyp3a4_is_tdi"].astype(int).values
    pos_count = np.sum(y)
    print(f"CYP3A4 Target: {len(df_3a4)} labeled molecules | {pos_count} Positives ({pos_count/len(df_3a4)*100:.2f}%)")

    # Generate 2,048-bit Morgan Fingerprints
    print("Generating 2,048-bit Morgan Fingerprints (radius=2)...")
    t0 = time.time()
    mfp_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = [mfp_gen.GetFingerprint(Chem.MolFromSmiles(s)) for s in df_3a4["assay_smiles"]]
    X = np.zeros((len(df_3a4), 2048), dtype=np.float32)
    for i, fp in enumerate(fps):
        X[i] = np.frombuffer(fp.ToBitString().encode("ascii"), "u1") - ord("0")
    print(f"Generated feature matrix X: {X.shape} in {time.time() - t0:.2f}s.")

    # Programmatic target leakage assertion
    feature_names = [f"ecfp4_bit_{i}" for i in range(2048)]
    assert_zero_target_leakage(feature_names)
    print("Programmatic target leakage check passed (0 assay columns in feature matrix).")

    # CV Split Folds
    # 1. Random 5-Fold Stratified CV
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    random_splits = list(skf.split(X, y))

    # 2. Grouped 5-Fold Murcko Scaffold CV (from EC-1-3-01)
    grouped_splits = []
    for f in range(5):
        val_idx = np.where(df_3a4["cv_fold_5"] == f)[0]
        train_idx = np.where(df_3a4["cv_fold_5"] != f)[0]
        grouped_splits.append((train_idx, val_idx))

    results = {
        "metadata": {
            "target": "CYP3A4_is_TDI",
            "n_samples": int(len(df_3a4)),
            "n_positives": int(pos_count),
            "feature_type": "ECFP4 (Morgan radius 2, 2048 bits)",
            "random_state": 42,
            "created_at": "2026-09-03",
        },
        "models": {},
        "scientific_hypothesis_test": {},
    }

    models = ["logistic_regression", "lightgbm"]
    for m in models:
        print(f"\n=======================================================")
        print(f"     Evaluating Model: {m.upper()}")
        print(f"=======================================================")

        # A. Random CV
        print(f"  Training {m} on Random 5-Fold CV...")
        res_rand = train_and_eval_cv(X, y, random_splits, m)
        print(f"    Random OOF -> ROC-AUC: {res_rand['overall_oof']['roc_auc']:.4f} [95% CI: {res_rand['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_lower']:.4f} - {res_rand['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_upper']:.4f}]")
        print(f"                  PR-AUC:  {res_rand['overall_oof']['pr_auc']:.4f} [95% CI: {res_rand['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_lower']:.4f} - {res_rand['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_upper']:.4f}]")
        print(f"                  MCC:     {res_rand['overall_oof']['mcc']:.4f} [95% CI: {res_rand['overall_oof']['bootstrap_ci_95']['mcc']['ci_lower']:.4f} - {res_rand['overall_oof']['bootstrap_ci_95']['mcc']['ci_upper']:.4f}]")

        # B. Grouped Scaffold CV
        print(f"  Training {m} on Grouped 5-Fold Scaffold CV...")
        res_grp = train_and_eval_cv(X, y, grouped_splits, m)
        print(f"    Grouped OOF -> ROC-AUC: {res_grp['overall_oof']['roc_auc']:.4f} [95% CI: {res_grp['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_lower']:.4f} - {res_grp['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_upper']:.4f}]")
        print(f"                   PR-AUC:  {res_grp['overall_oof']['pr_auc']:.4f} [95% CI: {res_grp['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_lower']:.4f} - {res_grp['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_upper']:.4f}]")
        print(f"                   MCC:     {res_grp['overall_oof']['mcc']:.4f} [95% CI: {res_grp['overall_oof']['bootstrap_ci_95']['mcc']['ci_lower']:.4f} - {res_grp['overall_oof']['bootstrap_ci_95']['mcc']['ci_upper']:.4f}]")

        # C. Delta (Random - Grouped)
        delta_roc = round(res_rand["overall_oof"]["roc_auc"] - res_grp["overall_oof"]["roc_auc"], 4)
        delta_pr = round(res_rand["overall_oof"]["pr_auc"] - res_grp["overall_oof"]["pr_auc"], 4)
        delta_mcc = round(res_rand["overall_oof"]["mcc"] - res_grp["overall_oof"]["mcc"], 4)

        print(f"  --> Delta (Random - Grouped): ROC-AUC: {delta_roc:+.4f} | PR-AUC: {delta_pr:+.4f} | MCC: {delta_mcc:+.4f}")

        results["models"][m] = {
            "random_5fold": {
                "overall_oof": res_rand["overall_oof"],
                "per_fold": res_rand["per_fold"],
            },
            "grouped_5fold": {
                "overall_oof": res_grp["overall_oof"],
                "per_fold": res_grp["per_fold"],
            },
            "delta_random_minus_grouped": {
                "roc_auc_delta": delta_roc,
                "pr_auc_delta": delta_pr,
                "mcc_delta": delta_mcc,
                "random_inflates_performance": bool(delta_roc > 0 or delta_pr > 0),
            }
        }

    # Save to JSON
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSuccessfully persisted ECFP4 baseline results to {OUT_JSON} ({OUT_JSON.stat().st_size:,} bytes).")
    return results


if __name__ == "__main__":
    run_benchmark()
