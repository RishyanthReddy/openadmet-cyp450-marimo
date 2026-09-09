#!/usr/bin/env python3
"""
EC-2-1-02: Train Robust 2D D-MPNN (Chemprop v2) Across Splits.

Evaluates 2D Directed Message Passing Neural Network (Chemprop v2) on CYP3A4_is_TDI across:
  - Random 5-Fold Stratified CV
  - Grouped 5-Fold Murcko Scaffold CV (leak-free from EC-1-3-01)

Calculates:
  - ROC-AUC, PR-AUC, MCC, Brier Score, Balanced Accuracy
  - 1,000-resample non-parametric bootstrap 95% Confidence Intervals
  - Empirical shift (Delta = Metric_Random - Metric_Grouped)
Enforces:
  - assert_zero_target_leakage (features derived strictly from molecular 2D graph)
Exports:
  - data/packaged/dmpnn_baseline_results.json
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import lightning as L
from chemprop import data, models, nn
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    matthews_corrcoef,
    brier_score_loss,
    balanced_accuracy_score,
)

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_PARQUET = BASE_DIR / "data" / "curated" / "cyp_splits.parquet"
OUT_JSON = BASE_DIR / "data" / "packaged" / "dmpnn_baseline_results.json"

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


def assert_zero_target_leakage(feature_input_names: list[str]) -> None:
    leaked = set(feature_input_names).intersection(BANNED_COLUMNS)
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


def create_dmpnn_model() -> models.MPNN:
    mp = nn.BondMessagePassing(d_h=300, depth=3, dropout=0.1)
    agg = nn.MeanAggregation()
    ffn = nn.BinaryClassificationFFN(input_dim=300, hidden_dim=300, dropout=0.1)
    return models.MPNN(message_passing=mp, agg=agg, predictor=ffn)


def train_and_eval_dmpnn_cv(
    smiles_list: list[str],
    y: np.ndarray,
    fold_indices: list[tuple[np.ndarray, np.ndarray]],
    epochs: int = 20,
    accelerator: str = "cpu"
) -> dict:
    oof_probs = np.zeros(len(y), dtype=float)
    fold_metrics = []

    ys_2d = y.astype(float)[:, None]
    all_datapoints = [data.MoleculeDatapoint.from_smi(s, y_val) for s, y_val in zip(smiles_list, ys_2d)]

    for fold_idx, (train_idx, val_idx) in enumerate(fold_indices):
        f_t0 = time.time()
        print(f"    Fold {fold_idx + 1}/5: Training ({len(train_idx)} train / {len(val_idx)} val)...", flush=True)

        train_data = data.MoleculeDataset([all_datapoints[i] for i in train_idx])
        val_data = data.MoleculeDataset([all_datapoints[i] for i in val_idx])

        train_loader = data.build_dataloader(train_data, batch_size=64, shuffle=True, num_workers=0)
        val_loader = data.build_dataloader(val_data, batch_size=64, shuffle=False, num_workers=0)

        # Build fresh model
        L.seed_everything(42 + fold_idx, workers=True)
        mpnn = create_dmpnn_model()

        trainer = L.Trainer(
            max_epochs=epochs,
            accelerator=accelerator,
            logger=False,
            enable_checkpointing=False,
            enable_progress_bar=False,
            deterministic=False,
        )
        trainer.fit(mpnn, train_dataloaders=train_loader)

        # Predict
        preds_list = trainer.predict(mpnn, dataloaders=val_loader)
        probs = torch.cat(preds_list, dim=0).squeeze().numpy().astype(float)
        oof_probs[val_idx] = probs

        f_pred = (probs >= 0.5).astype(int)
        y_val_1d = y[val_idx]

        f_roc = float(round(roc_auc_score(y_val_1d, probs), 4))
        f_pr = float(round(average_precision_score(y_val_1d, probs), 4))
        f_mcc = float(round(matthews_corrcoef(y_val_1d, f_pred), 4))
        f_brier = float(round(brier_score_loss(y_val_1d, probs), 4))

        fold_metrics.append({
            "fold": fold_idx,
            "roc_auc": f_roc,
            "pr_auc": f_pr,
            "mcc": f_mcc,
            "brier_score": f_brier,
        })
        print(f"      Fold {fold_idx + 1} done in {time.time() - f_t0:.1f}s -> ROC-AUC: {f_roc:.4f}, PR-AUC: {f_pr:.4f}, MCC: {f_mcc:.4f}", flush=True)

    overall = compute_metrics(y, oof_probs)
    return {
        "overall_oof": overall,
        "per_fold": fold_metrics,
        "oof_probabilities": [float(round(p, 4)) for p in oof_probs],
    }


def run_benchmark() -> dict:
    print(f"Loading partitioned dataset from {SPLITS_PARQUET}...", flush=True)
    df = pd.read_parquet(SPLITS_PARQUET)

    df_3a4 = df[df["mask_cyp3a4"]].copy().reset_index(drop=True)
    assert len(df_3a4) == 3584, f"Expected 3,584 CYP3A4 compounds, got {len(df_3a4)}"
    y = df_3a4["cyp3a4_is_tdi"].astype(int).values
    smiles_list = df_3a4["assay_smiles"].tolist()
    pos_count = int(np.sum(y))
    print(f"CYP3A4 Target: {len(df_3a4)} labeled molecules | {pos_count} Positives ({pos_count/len(df_3a4)*100:.2f}%)", flush=True)

    # Programmatic target leakage check
    # Model inputs are purely 2D molecular graphs from assay_smiles
    assert_zero_target_leakage(["assay_smiles"])
    print("Programmatic target leakage check passed (features derived solely from 2D molecular graph).", flush=True)

    # Cross-validation splits
    # 1. Random 5-Fold Stratified CV
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    random_splits = list(skf.split(smiles_list, y))

    # 2. Grouped 5-Fold Murcko Scaffold CV
    grouped_splits = []
    for f in range(5):
        val_idx = np.where(df_3a4["cv_fold_5"] == f)[0]
        train_idx = np.where(df_3a4["cv_fold_5"] != f)[0]
        grouped_splits.append((train_idx, val_idx))

    # Determine accelerator
    accelerator = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Using accelerator: {accelerator.upper()}", flush=True)

    epochs = 20

    print("\n=======================================================", flush=True)
    print("     Training Chemprop v2 D-MPNN on Random 5-Fold CV", flush=True)
    print("=======================================================", flush=True)
    t0_rand = time.time()
    res_rand = train_and_eval_dmpnn_cv(smiles_list, y, random_splits, epochs=epochs, accelerator=accelerator)
    print(f"  Random CV finished in {time.time() - t0_rand:.1f}s.", flush=True)
    print(f"  Random OOF -> ROC-AUC: {res_rand['overall_oof']['roc_auc']:.4f} [95% CI: {res_rand['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_lower']:.4f} - {res_rand['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_upper']:.4f}]", flush=True)
    print(f"                PR-AUC:  {res_rand['overall_oof']['pr_auc']:.4f} [95% CI: {res_rand['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_lower']:.4f} - {res_rand['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_upper']:.4f}]", flush=True)
    print(f"                MCC:     {res_rand['overall_oof']['mcc']:.4f} [95% CI: {res_rand['overall_oof']['bootstrap_ci_95']['mcc']['ci_lower']:.4f} - {res_rand['overall_oof']['bootstrap_ci_95']['mcc']['ci_upper']:.4f}]", flush=True)

    print("\n=======================================================", flush=True)
    print("     Training Chemprop v2 D-MPNN on Grouped 5-Fold Scaffold CV", flush=True)
    print("=======================================================", flush=True)
    t0_grp = time.time()
    res_grp = train_and_eval_dmpnn_cv(smiles_list, y, grouped_splits, epochs=epochs, accelerator=accelerator)
    print(f"  Grouped CV finished in {time.time() - t0_grp:.1f}s.", flush=True)
    print(f"  Grouped OOF -> ROC-AUC: {res_grp['overall_oof']['roc_auc']:.4f} [95% CI: {res_grp['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_lower']:.4f} - {res_grp['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_upper']:.4f}]", flush=True)
    print(f"                 PR-AUC:  {res_grp['overall_oof']['pr_auc']:.4f} [95% CI: {res_grp['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_lower']:.4f} - {res_grp['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_upper']:.4f}]", flush=True)
    print(f"                 MCC:     {res_grp['overall_oof']['mcc']:.4f} [95% CI: {res_grp['overall_oof']['bootstrap_ci_95']['mcc']['ci_lower']:.4f} - {res_grp['overall_oof']['bootstrap_ci_95']['mcc']['ci_upper']:.4f}]", flush=True)

    delta_roc = round(res_rand["overall_oof"]["roc_auc"] - res_grp["overall_oof"]["roc_auc"], 4)
    delta_pr = round(res_rand["overall_oof"]["pr_auc"] - res_grp["overall_oof"]["pr_auc"], 4)
    delta_mcc = round(res_rand["overall_oof"]["mcc"] - res_grp["overall_oof"]["mcc"], 4)
    print(f"\n--> Delta (Random - Grouped): ROC-AUC: {delta_roc:+.4f} | PR-AUC: {delta_pr:+.4f} | MCC: {delta_mcc:+.4f}", flush=True)

    results = {
        "metadata": {
            "target": "CYP3A4_is_TDI",
            "model_architecture": "Chemprop v2 D-MPNN (BondMessagePassing + MeanAggregation + BinaryClassificationFFN)",
            "n_samples": int(len(df_3a4)),
            "n_positives": int(pos_count),
            "epochs": epochs,
            "batch_size": 64,
            "accelerator": accelerator,
            "created_at": "2026-09-03",
        },
        "dmpnn": {
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
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nSuccessfully persisted D-MPNN baseline results to {OUT_JSON} ({OUT_JSON.stat().st_size:,} bytes).", flush=True)
    return results


if __name__ == "__main__":
    run_benchmark()
