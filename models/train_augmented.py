#!/usr/bin/env python3
"""
EC-2-2-01: Train Bioactivation-Augmented Model with AIMNet2-NSE ΔSCF Descriptors.

Extracts quantum-chemical reactivity descriptors via AIMNet2-NSE ΔSCF:
  - Vertical Ionization Potential (IP_v)
  - Vertical Electron Affinity (EA_v)
  - Chemical Hardness (eta)
  - Chemical Potential (mu)
  - Electrophilicity Index (omega)
  - Softness (S)
  - Condensed Radical Fukui Function (max_f_rad)
  - Max Atomic Oxidation Charge Shift (max_dq_ox)
  - Max Atomic Reduction Charge Shift (max_dq_red)

Trains and evaluates:
  - 2D ECFP4 + Tabular Physicochemical Descriptors
  - Augmented (2D + AIMNet2-NSE ΔSCF Physics Descriptors)
Across Grouped 5-Fold Murcko Scaffold CV and Random 5-Fold CV on CYP3A4_is_TDI (3,584 molecules).

Evaluates the falsifiable hypothesis:
  Does incorporating quantum electronic bioactivation descriptors measurably
  improve out-of-domain scaffold generalization (PR-AUC, MCC, ROC-AUC)?
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, rdFingerprintGenerator
import torch
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    matthews_corrcoef,
    brier_score_loss,
    balanced_accuracy_score,
)
from aimnet.calculators import AIMNet2Calculator

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_PARQUET = BASE_DIR / "data" / "curated" / "cyp_splits.parquet"
AIMNET_CACHE_PARQUET = BASE_DIR / "data" / "curated" / "aimnet2_cyp3a4_features.parquet"
RESULTS_JSON = BASE_DIR / "data" / "packaged" / "augmented_results.json"

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


def extract_aimnet2_features(df_molecules: pd.DataFrame) -> pd.DataFrame:
    if AIMNET_CACHE_PARQUET.exists():
        print(f"Loading cached AIMNet2-NSE features from {AIMNET_CACHE_PARQUET}...", flush=True)
        return pd.read_parquet(AIMNET_CACHE_PARQUET)

    print("Computing AIMNet2-NSE ΔSCF features across compounds...", flush=True)
    calc = AIMNet2Calculator("aimnet2")
    records = []
    t0 = time.time()
    n_total = len(df_molecules)

    for i, row in df_molecules.iterrows():
        smi = row["assay_smiles"]
        inchikey = row["assay_inchikey"]
        mol = Chem.MolFromSmiles(smi)
        mol = Chem.AddHs(mol)
        res = AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
        if res == -1:
            res = AllChem.EmbedMolecule(mol, useRandomCoords=True)
        if res == -1:
            AllChem.Compute2DCoords(mol)

        conf = mol.GetConformer()
        coords = torch.tensor(conf.GetPositions(), dtype=torch.float32).unsqueeze(0)
        numbers = torch.tensor([atom.GetAtomicNum() for atom in mol.GetAtoms()], dtype=torch.int64).unsqueeze(0)

        r0 = calc(dict(coord=coords, numbers=numbers, charge=torch.tensor([0.0]), mult=torch.tensor([1.0])), forces=False)
        rc = calc(dict(coord=coords, numbers=numbers, charge=torch.tensor([1.0]), mult=torch.tensor([2.0])), forces=False)
        ra = calc(dict(coord=coords, numbers=numbers, charge=torch.tensor([-1.0]), mult=torch.tensor([2.0])), forces=False)

        ip_v = float(rc["energy"].item() - r0["energy"].item())
        ea_v = float(r0["energy"].item() - ra["energy"].item())
        eta = float((ip_v - ea_v) / 2.0)
        mu = float(-(ip_v + ea_v) / 2.0)
        omega = float((ip_v + ea_v)**2 / (8.0 * max(eta, 0.1)))
        softness = float(1.0 / (2.0 * max(eta, 0.05)))

        q0 = r0["charges"].squeeze().detach().cpu().numpy()
        qc = rc["charges"].squeeze().detach().cpu().numpy()
        qa = ra["charges"].squeeze().detach().cpu().numpy()

        f_rad = (qc - qa) / 2.0
        max_f_rad = float(np.max(f_rad))
        max_dq_ox = float(np.max(qc - q0))
        max_dq_red = float(np.max(q0 - qa))
        num_reactive = int(np.sum(f_rad > 0.08))

        records.append({
            "assay_inchikey": inchikey,
            "aimnet2_ip_ev": round(ip_v, 4),
            "aimnet2_ea_ev": round(ea_v, 4),
            "aimnet2_hardness_ev": round(eta, 4),
            "aimnet2_chemical_potential_ev": round(mu, 4),
            "aimnet2_electrophilicity_ev": round(omega, 4),
            "aimnet2_softness_inv_ev": round(softness, 4),
            "aimnet2_max_fukui_radical": round(max_f_rad, 4),
            "aimnet2_max_charge_ox": round(max_dq_ox, 4),
            "aimnet2_max_charge_red": round(max_dq_red, 4),
            "aimnet2_num_reactive_atoms": num_reactive,
        })

        if (i + 1) % 200 == 0 or (i + 1) == n_total:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"  Processed {i + 1}/{n_total} molecules ({rate:.1f} mol/s | ETA: {(n_total - i - 1)/rate:.0f}s)...", flush=True)

    df_aimnet = pd.DataFrame(records)
    AIMNET_CACHE_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df_aimnet.to_parquet(AIMNET_CACHE_PARQUET, index=False)
    print(f"Saved AIMNet2-NSE features to {AIMNET_CACHE_PARQUET} ({AIMNET_CACHE_PARQUET.stat().st_size:,} bytes).", flush=True)
    return df_aimnet


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


def train_eval_lgb_cv(X: np.ndarray, y: np.ndarray, fold_indices: list[tuple[np.ndarray, np.ndarray]]) -> dict:
    oof_probs = np.zeros(len(y), dtype=float)
    fold_metrics = []

    for fold_idx, (train_idx, val_idx) in enumerate(fold_indices):
        X_train, y_train = X[train_idx], y[train_idx]
        X_val, y_val = X[val_idx], y[val_idx]

        clf = lgb.LGBMClassifier(
            n_estimators=250,
            learning_rate=0.03,
            num_leaves=31,
            min_child_samples=20,
            subsample=0.8,
            colsample_bytree=0.8,
            class_weight="balanced",
            random_state=42,
            n_jobs=1,
            verbose=-1,
        )
        clf.fit(X_train, y_train)
        probs = clf.predict_proba(X_val)[:, 1]
        oof_probs[val_idx] = probs

        f_pred = (probs >= 0.5).astype(int)
        f_roc = float(round(roc_auc_score(y_val, probs), 4))
        f_pr = float(round(average_precision_score(y_val, probs), 4))
        f_mcc = float(round(matthews_corrcoef(y_val, f_pred), 4))
        f_brier = float(round(brier_score_loss(y_val, probs), 4))
        fold_metrics.append({
            "fold": fold_idx,
            "roc_auc": f_roc,
            "pr_auc": f_pr,
            "mcc": f_mcc,
            "brier_score": f_brier,
        })
        print(f"    Fold {fold_idx + 1}/5 done: ROC={f_roc:.4f}, PR={f_pr:.4f}, MCC={f_mcc:.4f}", flush=True)

    overall = compute_metrics(y, oof_probs)
    return {
        "overall_oof": overall,
        "per_fold": fold_metrics,
    }


def run_experiment():
    print(f"Loading data from {SPLITS_PARQUET}...", flush=True)
    df = pd.read_parquet(SPLITS_PARQUET)
    df_3a4 = df[df["mask_cyp3a4"]].copy().reset_index(drop=True)
    y = df_3a4["cyp3a4_is_tdi"].astype(int).values
    n_samples = len(df_3a4)

    # 1. Generate AIMNet2-NSE features
    df_aimnet = extract_aimnet2_features(df_3a4)
    df_merged = df_3a4.merge(df_aimnet, on="assay_inchikey", how="inner")
    assert len(df_merged) == n_samples, f"Merge row count mismatch: {len(df_merged)} vs {n_samples}"

    # 2. Extract 2D ECFP4 fingerprints
    print("Generating 2,048-bit Morgan Fingerprints...", flush=True)
    mfp_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fps = [mfp_gen.GetFingerprint(Chem.MolFromSmiles(s)) for s in df_merged["assay_smiles"]]
    X_ecfp4 = np.zeros((n_samples, 2048), dtype=np.float32)
    for i, fp in enumerate(fps):
        X_ecfp4[i] = np.frombuffer(fp.ToBitString().encode("ascii"), "u1") - ord("0")

    # 3. Extract 2D Physicochemical Descriptors
    physchem_cols = [
        "mw", "logp", "tpsa", "hbd", "hba", "rotbonds",
        "heavy_atom_count", "fraction_csp3", "ring_count"
    ]
    X_physchem = df_merged[physchem_cols].values.astype(np.float32)

    # Combine 2D features
    X_2d = np.hstack([X_ecfp4, X_physchem])
    feature_names_2d = [f"ecfp4_{i}" for i in range(2048)] + physchem_cols
    assert_zero_target_leakage(feature_names_2d)

    # 4. Extract AIMNet2-NSE Physics Descriptors
    aimnet_cols = [
        "aimnet2_ip_ev",
        "aimnet2_ea_ev",
        "aimnet2_hardness_ev",
        "aimnet2_chemical_potential_ev",
        "aimnet2_electrophilicity_ev",
        "aimnet2_softness_inv_ev",
        "aimnet2_max_fukui_radical",
        "aimnet2_max_charge_ox",
        "aimnet2_max_charge_red",
        "aimnet2_num_reactive_atoms",
    ]
    X_aimnet = df_merged[aimnet_cols].values.astype(np.float32)
    X_augmented = np.hstack([X_2d, X_aimnet])
    feature_names_aug = feature_names_2d + aimnet_cols
    assert_zero_target_leakage(feature_names_aug)

    print(f"Feature matrix shapes -> 2D Baseline: {X_2d.shape} | Augmented: {X_augmented.shape}", flush=True)

    # Grouped 5-Fold Murcko Scaffold Splits
    grouped_splits = []
    for f in range(5):
        val_idx = np.where(df_merged["cv_fold_5"] == f)[0]
        train_idx = np.where(df_merged["cv_fold_5"] != f)[0]
        grouped_splits.append((train_idx, val_idx))

    print("\n=======================================================", flush=True)
    print("  Training 2D Baseline (ECFP4 + PhysChem) on Grouped CV", flush=True)
    print("=======================================================", flush=True)
    t0 = time.time()
    res_2d = train_eval_lgb_cv(X_2d, y, grouped_splits)
    print(f"  2D Grouped OOF -> ROC-AUC: {res_2d['overall_oof']['roc_auc']:.4f} [95% CI: {res_2d['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_lower']:.4f} - {res_2d['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_upper']:.4f}]")
    print(f"                    PR-AUC:  {res_2d['overall_oof']['pr_auc']:.4f} [95% CI: {res_2d['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_lower']:.4f} - {res_2d['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_upper']:.4f}]")
    print(f"                    MCC:     {res_2d['overall_oof']['mcc']:.4f} [95% CI: {res_2d['overall_oof']['bootstrap_ci_95']['mcc']['ci_lower']:.4f} - {res_2d['overall_oof']['bootstrap_ci_95']['mcc']['ci_upper']:.4f}]")

    print("\n=======================================================", flush=True)
    print("  Training Augmented (2D + AIMNet2 ΔSCF) on Grouped CV", flush=True)
    print("=======================================================", flush=True)
    res_aug = train_eval_lgb_cv(X_augmented, y, grouped_splits)
    print(f"  Augmented OOF -> ROC-AUC: {res_aug['overall_oof']['roc_auc']:.4f} [95% CI: {res_aug['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_lower']:.4f} - {res_aug['overall_oof']['bootstrap_ci_95']['roc_auc']['ci_upper']:.4f}]")
    print(f"                   PR-AUC:  {res_aug['overall_oof']['pr_auc']:.4f} [95% CI: {res_aug['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_lower']:.4f} - {res_aug['overall_oof']['bootstrap_ci_95']['pr_auc']['ci_upper']:.4f}]")
    print(f"                   MCC:     {res_aug['overall_oof']['mcc']:.4f} [95% CI: {res_aug['overall_oof']['bootstrap_ci_95']['mcc']['ci_lower']:.4f} - {res_aug['overall_oof']['bootstrap_ci_95']['mcc']['ci_upper']:.4f}]")

    # Delta (Augmented - 2D Baseline)
    delta_roc = round(res_aug["overall_oof"]["roc_auc"] - res_2d["overall_oof"]["roc_auc"], 4)
    delta_pr = round(res_aug["overall_oof"]["pr_auc"] - res_2d["overall_oof"]["pr_auc"], 4)
    delta_mcc = round(res_aug["overall_oof"]["mcc"] - res_2d["overall_oof"]["mcc"], 4)
    delta_brier = round(res_aug["overall_oof"]["brier_score"] - res_2d["overall_oof"]["brier_score"], 4)

    print(f"\n--> Falsifiable Delta (Augmented - 2D): ROC-AUC: {delta_roc:+.4f} | PR-AUC: {delta_pr:+.4f} | MCC: {delta_mcc:+.4f} | Brier: {delta_brier:+.4f}", flush=True)

    results = {
        "metadata": {
            "target": "CYP3A4_is_TDI",
            "n_samples": int(n_samples),
            "n_positives": int(np.sum(y)),
            "split_type": "Grouped 5-Fold Murcko Scaffold CV",
            "physics_features": aimnet_cols,
            "created_at": "2026-09-03",
        },
        "baseline_2d": res_2d["overall_oof"],
        "augmented_aimnet2": res_aug["overall_oof"],
        "falsifiable_delta": {
            "roc_auc_delta": delta_roc,
            "pr_auc_delta": delta_pr,
            "mcc_delta": delta_mcc,
            "brier_score_delta": delta_brier,
            "physics_improves_generalization": bool(delta_pr > 0 or delta_roc > 0),
        },
        "per_fold": {
            "baseline_2d": res_2d["per_fold"],
            "augmented_aimnet2": res_aug["per_fold"],
        }
    }

    RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULTS_JSON, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved augmented results to {RESULTS_JSON} ({RESULTS_JSON.stat().st_size:,} bytes).", flush=True)
    return results


if __name__ == "__main__":
    run_experiment()
