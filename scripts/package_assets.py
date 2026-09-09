#!/usr/bin/env python3
"""
EC-2-4-01: Package Precomputed Dataset, Predictions, and MMP Pairs into Parquet & Base64.

Consolidates:
  1. OpenADMET primary dataset & splits (6,145 compounds)
  2. Octant QC overlay (quantitative peak areas, depletion, substrate inhibition)
  3. AIMNet2-NSE ΔSCF quantum electronic features (10 descriptors, 0 NaNs)
  4. 2D Baseline & Physics-Augmented model predictions (out-of-fold probabilities)
  5. TxConformal candidate selection flags & weighted p-values (Jin et al. 2026)
  6. Matched Molecular Pair (MMP) activity cliff annotations (46 pairs)

Outputs:
  - data/packaged/cyp_tdi_curated.parquet (Snappy compressed, <= 12 MB, loads < 150ms)
  - data/packaged/fallback_sample.parquet (100 compounds for zero-network execution)
  - models/embedded_assets.py (Base64+gzip strings and robust loaders with 3 retries)
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import rdFingerprintGenerator
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import lightgbm as lgb

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_PARQUET = BASE_DIR / "data" / "curated" / "cyp_splits.parquet"
QC_PARQUET = BASE_DIR / "data" / "curated" / "octant_openadmet_qc_overlay.parquet"
AIMNET_PARQUET = BASE_DIR / "data" / "curated" / "aimnet2_cyp3a4_features.parquet"
MMP_JSON = BASE_DIR / "data" / "packaged" / "mmp_transformations.json"
LIT_JSON = BASE_DIR / "data" / "fixtures" / "literature_mbi_reference_set.json"
NCBI_JSON = BASE_DIR / "data" / "packaged" / "ncbi_pubmed_cache.json"
CYP2D6_JSON = BASE_DIR / "data" / "packaged" / "cyp2d6_docking_results.json"

OUT_PARQUET = BASE_DIR / "data" / "packaged" / "cyp_tdi_curated.parquet"
FALLBACK_PARQUET = BASE_DIR / "data" / "packaged" / "fallback_sample.parquet"
EMBEDDED_PY = BASE_DIR / "models" / "embedded_assets.py"

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


def generate_predictions_and_pvalues(df_master: pd.DataFrame) -> pd.DataFrame:
    print("Generating model predictions and TxConformal p-values...", flush=True)

    # Initialize prediction columns with NaNs (will be populated on labeled subsets)
    df_master["pred_cyp3a4_prob_baseline_2d"] = np.nan
    df_master["pred_cyp3a4_prob_augmented_physics"] = np.nan
    df_master["pred_cyp2d6_prob_baseline_2d"] = np.nan
    df_master["txconformal_pvalue_cyp3a4"] = np.nan
    df_master["txconformal_selected_alpha_0_10"] = False
    df_master["txconformal_selected_alpha_0_20"] = False

    physchem_cols = [
        "mw", "logp", "tpsa", "hbd", "hba", "rotbonds",
        "heavy_atom_count", "fraction_csp3", "ring_count"
    ]
    aimnet_cols = [
        "aimnet2_ip_ev", "aimnet2_ea_ev", "aimnet2_hardness_ev",
        "aimnet2_chemical_potential_ev", "aimnet2_electrophilicity_ev",
        "aimnet2_softness_inv_ev", "aimnet2_max_fukui_radical",
        "aimnet2_max_charge_ox", "aimnet2_max_charge_red",
        "aimnet2_num_reactive_atoms"
    ]

    mfp_gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)

    # 1. CYP3A4 Predictions (3,584 compounds)
    mask_3a4 = df_master["mask_cyp3a4"].values
    idx_3a4 = np.where(mask_3a4)[0]
    df_3a4 = df_master.iloc[idx_3a4].copy()

    fps_3a4 = [mfp_gen.GetFingerprint(Chem.MolFromSmiles(s)) for s in df_3a4["assay_smiles"]]
    X_fp_3a4 = np.zeros((len(df_3a4), 2048), dtype=np.float32)
    for i, fp in enumerate(fps_3a4):
        X_fp_3a4[i] = np.frombuffer(fp.ToBitString().encode("ascii"), "u1") - ord("0")

    X_phys_3a4 = df_3a4[physchem_cols].values.astype(np.float32)
    X_aim_3a4 = df_3a4[aimnet_cols].values.astype(np.float32)

    X_2d_3a4 = np.hstack([X_fp_3a4, X_phys_3a4])
    X_aug_3a4 = np.hstack([X_2d_3a4, X_aim_3a4])
    y_3a4 = df_3a4["cyp3a4_is_tdi"].astype(int).values

    assert_zero_target_leakage([f"ecfp4_{i}" for i in range(2048)] + physchem_cols)
    assert_zero_target_leakage([f"ecfp4_{i}" for i in range(2048)] + physchem_cols + aimnet_cols)

    oof_2d_3a4 = np.zeros(len(df_3a4), dtype=float)
    oof_aug_3a4 = np.zeros(len(df_3a4), dtype=float)

    for fold in range(5):
        train_sub = np.where(df_3a4["cv_fold_5"] != fold)[0]
        val_sub = np.where(df_3a4["cv_fold_5"] == fold)[0]

        # 2D Model
        clf_2d = lgb.LGBMClassifier(
            n_estimators=200, learning_rate=0.03, num_leaves=31,
            class_weight="balanced", random_state=42 + fold, n_jobs=1, verbose=-1
        )
        clf_2d.fit(X_2d_3a4[train_sub], y_3a4[train_sub])
        oof_2d_3a4[val_sub] = clf_2d.predict_proba(X_2d_3a4[val_sub])[:, 1]

        # Augmented Physics Model
        clf_aug = lgb.LGBMClassifier(
            n_estimators=200, learning_rate=0.03, num_leaves=31,
            class_weight="balanced", random_state=42 + fold, n_jobs=1, verbose=-1
        )
        clf_aug.fit(X_aug_3a4[train_sub], y_3a4[train_sub])
        oof_aug_3a4[val_sub] = clf_aug.predict_proba(X_aug_3a4[val_sub])[:, 1]

    df_master.loc[idx_3a4, "pred_cyp3a4_prob_baseline_2d"] = np.round(oof_2d_3a4, 4)
    df_master.loc[idx_3a4, "pred_cyp3a4_prob_augmented_physics"] = np.round(oof_aug_3a4, 4)

    # 2. TxConformal p-values on CYP3A4
    train_holdout = np.where(df_3a4["holdout_split"] == "TRAIN")[0]
    cal_holdout = np.where(df_3a4["holdout_split"] == "CALIBRATION")[0]
    test_holdout = np.where(df_3a4["holdout_split"] == "TEST")[0]

    # Domain discriminator on CALIBRATION vs TEST
    desc_all = physchem_cols + aimnet_cols
    scaler = StandardScaler()
    X_domain = scaler.fit_transform(df_3a4.iloc[np.concatenate([cal_holdout, test_holdout])][desc_all].values)
    y_domain = np.array([0] * len(cal_holdout) + [1] * len(test_holdout))
    disc = LogisticRegression(C=0.1, max_iter=500, random_state=42)
    disc.fit(X_domain, y_domain)
    d_probs = disc.predict_proba(X_domain)[:, 1]

    n_cal, n_test = len(cal_holdout), len(test_holdout)
    odds = d_probs / (1.0 - np.clip(d_probs, 1e-4, 1.0 - 1e-4))
    w_all = odds * (n_cal / n_test)
    w_all = np.clip(w_all, 0.1, 10.0)

    w_cal = w_all[:n_cal]
    w_test = w_all[n_cal:]

    cal_null_mask = (y_3a4[cal_holdout] == 1)
    s_cal_null = 1.0 - oof_aug_3a4[cal_holdout][cal_null_mask]
    w_cal_null = w_cal[cal_null_mask]

    s_test = 1.0 - oof_aug_3a4[test_holdout]
    sum_w_cal = np.sum(w_cal_null)

    pvals_test = np.zeros(len(test_holdout), dtype=float)
    for i in range(len(test_holdout)):
        num = np.sum(w_cal_null[s_cal_null >= s_test[i]]) + w_test[i]
        pvals_test[i] = num / (sum_w_cal + w_test[i])

    # Benjamini-Hochberg selections
    def bh_select(pvals, alpha):
        m = len(pvals)
        s_idx = np.argsort(pvals)
        sp = pvals[s_idx]
        thresh = (np.arange(1, m + 1) / m) * alpha
        below = np.where(sp <= thresh)[0]
        if len(below) == 0:
            return set()
        return set(s_idx[:below[-1] + 1])

    sel_10 = bh_select(pvals_test, 0.10)
    sel_20 = bh_select(pvals_test, 0.20)

    test_global_indices = idx_3a4[test_holdout]
    df_master.loc[test_global_indices, "txconformal_pvalue_cyp3a4"] = np.round(pvals_test, 4)
    df_master.loc[test_global_indices, "txconformal_selected_alpha_0_10"] = [i in sel_10 for i in range(len(test_holdout))]
    df_master.loc[test_global_indices, "txconformal_selected_alpha_0_20"] = [i in sel_20 for i in range(len(test_holdout))]

    # 3. CYP2D6 Predictions (1,497 compounds)
    mask_2d6 = df_master["mask_cyp2d6"].values
    idx_2d6 = np.where(mask_2d6)[0]
    df_2d6 = df_master.iloc[idx_2d6].copy()

    fps_2d6 = [mfp_gen.GetFingerprint(Chem.MolFromSmiles(s)) for s in df_2d6["assay_smiles"]]
    X_fp_2d6 = np.zeros((len(df_2d6), 2048), dtype=np.float32)
    for i, fp in enumerate(fps_2d6):
        X_fp_2d6[i] = np.frombuffer(fp.ToBitString().encode("ascii"), "u1") - ord("0")

    X_phys_2d6 = df_2d6[physchem_cols].values.astype(np.float32)
    X_2d_2d6 = np.hstack([X_fp_2d6, X_phys_2d6])
    y_2d6 = df_2d6["cyp2d6_is_tdi"].astype(int).values

    oof_2d_2d6 = np.zeros(len(df_2d6), dtype=float)
    for fold in range(5):
        train_sub = np.where(df_2d6["cv_fold_5"] != fold)[0]
        val_sub = np.where(df_2d6["cv_fold_5"] == fold)[0]
        clf_2d6 = lgb.LGBMClassifier(
            n_estimators=150, learning_rate=0.03, num_leaves=31,
            class_weight="balanced", random_state=42 + fold, n_jobs=1, verbose=-1
        )
        clf_2d6.fit(X_2d_2d6[train_sub], y_2d6[train_sub])
        oof_2d_2d6[val_sub] = clf_2d6.predict_proba(X_2d_2d6[val_sub])[:, 1]

    df_master.loc[idx_2d6, "pred_cyp2d6_prob_baseline_2d"] = np.round(oof_2d_2d6, 4)

    print("Predictions and TxConformal values successfully populated.", flush=True)
    return df_master


def attach_mmp_annotations(df_master: pd.DataFrame) -> pd.DataFrame:
    print(f"Attaching MMP activity cliff tags from {MMP_JSON}...", flush=True)
    with open(MMP_JSON) as f:
        mmp_payload = json.load(f)

    df_master["is_mmp_cliff"] = False
    df_master["mmp_id"] = None
    df_master["mmp_role"] = None
    df_master["mmp_transformation"] = None

    # Map by molecule_name
    mmp_map = {}
    for p in mmp_payload["pairs"]:
        m_id = p["mmp_id"]
        trans = p["transformation"]

        # Inactive partner
        inact_name = p["mol_inactive"]["molecule_name"]
        mmp_map[inact_name] = {
            "mmp_id": m_id,
            "mmp_role": "INACTIVE",
            "mmp_transformation": trans,
        }
        # Active partner
        act_name = p["mol_active"]["molecule_name"]
        mmp_map[act_name] = {
            "mmp_id": m_id,
            "mmp_role": "LIABILITY",
            "mmp_transformation": trans,
        }

    matched_count = 0
    for idx, row in df_master.iterrows():
        name = row["molecule_name"]
        if name in mmp_map:
            df_master.at[idx, "is_mmp_cliff"] = True
            df_master.at[idx, "mmp_id"] = mmp_map[name]["mmp_id"]
            df_master.at[idx, "mmp_role"] = mmp_map[name]["mmp_role"]
            df_master.at[idx, "mmp_transformation"] = mmp_map[name]["mmp_transformation"]
            matched_count += 1

    print(f"Annotated {matched_count} compounds belonging to curated MMP pairs.", flush=True)
    return df_master


def build_fallback_sample(df_master: pd.DataFrame) -> pd.DataFrame:
    print("Selecting 100-molecule stratified fallback sample...", flush=True)
    # Stratified:
    # 50 CYP3A4 compounds (40 non-TDI, 10 TDI)
    # 30 CYP2D6 compounds (24 non-TDI, 6 TDI)
    cyp3a4_neg = df_master[df_master["mask_cyp3a4"] & (df_master["cyp3a4_is_tdi"] == False) & (df_master["is_mmp_cliff"] == False)].sample(n=40, random_state=42)
    cyp3a4_pos = df_master[df_master["mask_cyp3a4"] & (df_master["cyp3a4_is_tdi"] == True) & (df_master["is_mmp_cliff"] == False)].sample(n=10, random_state=42)

    cyp2d6_neg = df_master[df_master["mask_cyp2d6"] & (df_master["cyp2d6_is_tdi"] == False) & (df_master["is_mmp_cliff"] == False)].sample(n=24, random_state=42)
    cyp2d6_pos = df_master[df_master["mask_cyp2d6"] & (df_master["cyp2d6_is_tdi"] == True) & (df_master["is_mmp_cliff"] == False)].sample(n=6, random_state=42)

    mmp_sample = df_master[df_master["is_mmp_cliff"] == True].sample(n=20, random_state=42)

    df_fallback = pd.concat([cyp3a4_neg, cyp3a4_pos, cyp2d6_neg, cyp2d6_pos, mmp_sample]).drop_duplicates(subset=["assay_inchikey"]).reset_index(drop=True)
    if len(df_fallback) < 100:
        extra = df_master[~df_master["assay_inchikey"].isin(df_fallback["assay_inchikey"])].sample(n=100 - len(df_fallback), random_state=42)
        df_fallback = pd.concat([df_fallback, extra]).reset_index(drop=True)
    df_fallback = df_fallback.iloc[:100].copy()
    for col in df_fallback.select_dtypes(include="float64").columns:
        df_fallback[col] = df_fallback[col].astype("float32")

    FALLBACK_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df_fallback.to_parquet(FALLBACK_PARQUET, index=False, compression=None)
    print(f"Saved fallback sample ({len(df_fallback)} rows) to {FALLBACK_PARQUET} ({FALLBACK_PARQUET.stat().st_size:,} bytes).", flush=True)
    return df_fallback


def generate_embedded_assets_module():
    print(f"Encoding fallback assets into {EMBEDDED_PY}...", flush=True)

    def _compress_json(path: Path) -> str:
        raw = path.read_text(encoding="utf-8")
        min_json = json.dumps(json.loads(raw), separators=(",", ":")).encode("utf-8")
        return base64.b64encode(gzip.compress(min_json, compresslevel=9)).decode("ascii")

    # 1. Fallback sample parquet -> gzip -> base64
    fallback_bytes = FALLBACK_PARQUET.read_bytes()
    fallback_gz = gzip.compress(fallback_bytes, compresslevel=9)
    fallback_b64 = base64.b64encode(fallback_gz).decode("ascii")

    # 2. Literature MBI reference set -> gzip -> base64
    lit_b64 = _compress_json(LIT_JSON)

    # 3. MMP transformations catalog -> gzip -> base64
    mmp_b64 = _compress_json(MMP_JSON)

    # 4. Packaged Benchmark JSONs -> gzip -> base64
    ecfp_b64 = _compress_json(BASE_DIR / "data" / "packaged" / "ecfp_baseline_results.json")
    dmpnn_b64 = _compress_json(BASE_DIR / "data" / "packaged" / "dmpnn_baseline_results.json")
    tani_b64 = _compress_json(BASE_DIR / "data" / "curated" / "tanimoto_shift_summary.json")
    aug_b64 = _compress_json(BASE_DIR / "data" / "packaged" / "augmented_results.json")
    dock_b64 = _compress_json(BASE_DIR / "data" / "packaged" / "docking_ablation_results.json")
    tx_b64 = _compress_json(BASE_DIR / "data" / "packaged" / "txconformal_selection_results.json")
    oof_b64 = _compress_json(BASE_DIR / "data" / "packaged" / "oof_error_cases.json")
    ncbi_b64 = _compress_json(NCBI_JSON)
    cyp2d6_b64 = _compress_json(CYP2D6_JSON)

    # 5. Compute primary curated parquet SHA-256 checksum
    parquet_bytes = OUT_PARQUET.read_bytes()
    parquet_sha256 = hashlib.sha256(parquet_bytes).hexdigest()

    code = f'''# Generated by scripts/package_assets.py - DO NOT EDIT MANUALLY
"""
Embedded Assets & Zero-Network Fallback Module for OpenADMET CYP TDI App.

Contains embedded gzip-compressed base64 fallbacks for:
  - 100-molecule stratified reference sample
  - Literature MBI reference inactivators
  - Matched Molecular Pair (MMP) activity cliff catalog
  - ECFP4, Chemprop D-MPNN, and Physics-Augmented benchmark results
  - Macromolecular docking active-site steric proximity & TxConformal candidate selections
  - NCBI Entrez PubMed verification cache
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import os
import sys
import time
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PARQUET_PRIMARY_PATH = BASE_DIR / "data" / "packaged" / "cyp_tdi_curated.parquet"
PARQUET_EXPECTED_SHA256 = "{parquet_sha256}"

DATASET_PROVENANCE_STATUS = "UNINITIALIZED"

# Embedded Assets (GZIP + Base64)
_FALLBACK_SAMPLE_GZIP_B64 = """{fallback_b64}"""
_LITERATURE_MBI_GZIP_B64 = """{lit_b64}"""
_MMP_TRANSFORMATIONS_GZIP_B64 = """{mmp_b64}"""
_ECFP_BASELINE_GZIP_B64 = """{ecfp_b64}"""
_DMPNN_BASELINE_GZIP_B64 = """{dmpnn_b64}"""
_TANIMOTO_SHIFT_GZIP_B64 = """{tani_b64}"""
_AUGMENTED_RESULTS_GZIP_B64 = """{aug_b64}"""
_DOCKING_ABLATION_GZIP_B64 = """{dock_b64}"""
_TXCONFORMAL_SELECTION_GZIP_B64 = """{tx_b64}"""
_OOF_ERROR_CASES_GZIP_B64 = """{oof_b64}"""
_NCBI_PUBMED_CACHE_GZIP_B64 = """{ncbi_b64}"""
_CYP2D6_DOCKING_GZIP_B64 = """{cyp2d6_b64}"""


def load_fallback_dataset() -> pd.DataFrame:
    """Decodes and loads the 100-molecule standalone fallback sample in-memory."""
    raw_gz = base64.b64decode(_FALLBACK_SAMPLE_GZIP_B64)
    raw_parquet = gzip.decompress(raw_gz)
    return pd.read_parquet(io.BytesIO(raw_parquet))


def load_literature_mbi_reference_set() -> dict:
    """Decodes and returns the curated literature MBI reference set."""
    raw_gz = base64.b64decode(_LITERATURE_MBI_GZIP_B64)
    raw_json = gzip.decompress(raw_gz).decode("utf-8")
    return json.loads(raw_json)


def load_mmp_transformations() -> dict:
    """Decodes and returns the curated Matched Molecular Pair transformations."""
    raw_gz = base64.b64decode(_MMP_TRANSFORMATIONS_GZIP_B64)
    raw_json = gzip.decompress(raw_gz).decode("utf-8")
    return json.loads(raw_json)


def load_ecfp_baseline_results() -> dict:
    p = BASE_DIR / "data" / "packaged" / "ecfp_baseline_results.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return json.loads(gzip.decompress(base64.b64decode(_ECFP_BASELINE_GZIP_B64)).decode("utf-8"))


def load_dmpnn_baseline_results() -> dict:
    p = BASE_DIR / "data" / "packaged" / "dmpnn_baseline_results.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return json.loads(gzip.decompress(base64.b64decode(_DMPNN_BASELINE_GZIP_B64)).decode("utf-8"))


def load_tanimoto_shift_summary() -> dict:
    p = BASE_DIR / "data" / "curated" / "tanimoto_shift_summary.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return json.loads(gzip.decompress(base64.b64decode(_TANIMOTO_SHIFT_GZIP_B64)).decode("utf-8"))


def load_augmented_results() -> dict:
    p = BASE_DIR / "data" / "packaged" / "augmented_results.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return json.loads(gzip.decompress(base64.b64decode(_AUGMENTED_RESULTS_GZIP_B64)).decode("utf-8"))


def load_docking_ablation_results() -> dict:
    p = BASE_DIR / "data" / "packaged" / "docking_ablation_results.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return json.loads(gzip.decompress(base64.b64decode(_DOCKING_ABLATION_GZIP_B64)).decode("utf-8"))


def load_txconformal_selection_results() -> dict:
    p = BASE_DIR / "data" / "packaged" / "txconformal_selection_results.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return json.loads(gzip.decompress(base64.b64decode(_TXCONFORMAL_SELECTION_GZIP_B64)).decode("utf-8"))


def load_oof_error_cases() -> dict:
    p = BASE_DIR / "data" / "packaged" / "oof_error_cases.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return json.loads(gzip.decompress(base64.b64decode(_OOF_ERROR_CASES_GZIP_B64)).decode("utf-8"))


def load_ncbi_pubmed_cache() -> dict:
    p = BASE_DIR / "data" / "packaged" / "ncbi_pubmed_cache.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return json.loads(gzip.decompress(base64.b64decode(_NCBI_PUBMED_CACHE_GZIP_B64)).decode("utf-8"))


def load_cyp2d6_docking_results() -> dict:
    p = BASE_DIR / "data" / "packaged" / "cyp2d6_docking_results.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return json.loads(gzip.decompress(base64.b64decode(_CYP2D6_DOCKING_GZIP_B64)).decode("utf-8"))


def get_dataset_provenance_status() -> str:
    """Returns the active provenance status of the loaded dataset."""
    global DATASET_PROVENANCE_STATUS
    return DATASET_PROVENANCE_STATUS


def load_curated_dataset(max_retries: int = 3) -> pd.DataFrame:
    """
    Loads primary packaged dataset with fallback resilience:
      1. Tries loading local PARQUET_PRIMARY_PATH (resolved relative to module) with up to max_retries attempts.
      2. Validates SHA-256 checksum against PARQUET_EXPECTED_SHA256.
      3. Falls back gracefully to the embedded 100-molecule dataset if file is absent, checksum mismatches, or all attempts fail.
    """
    global DATASET_PROVENANCE_STATUS
    if PARQUET_PRIMARY_PATH.exists():
        for attempt in range(1, max(1, max_retries) + 1):
            try:
                raw_bytes = PARQUET_PRIMARY_PATH.read_bytes()
                computed_sha = hashlib.sha256(raw_bytes).hexdigest()
                if computed_sha == PARQUET_EXPECTED_SHA256:
                    df = pd.read_parquet(io.BytesIO(raw_bytes))
                    DATASET_PROVENANCE_STATUS = "PRIMARY_PARQUET_VERIFIED"
                    return df
                else:
                    print(f"[Warning] SHA256 mismatch ({{computed_sha[:12]}}... != {{PARQUET_EXPECTED_SHA256[:12]}}...). Falling back to embedded sample.", file=sys.stderr)
                    break
            except Exception as err:
                print(f"[Warning] Attempt {{attempt}}/{{max_retries}} failed loading {{PARQUET_PRIMARY_PATH}}: {{err}}.", file=sys.stderr)
                if attempt < max_retries:
                    time.sleep(0.05 * attempt)
                else:
                    print(f"[Warning] All {{max_retries}} attempts failed. Falling back to embedded sample.", file=sys.stderr)

    DATASET_PROVENANCE_STATUS = "EMBEDDED_OFFLINE_FALLBACK"
    return load_fallback_dataset()
'''

    EMBEDDED_PY.parent.mkdir(parents=True, exist_ok=True)
    EMBEDDED_PY.write_text(code)
    print(f"Generated {EMBEDDED_PY} ({EMBEDDED_PY.stat().st_size:,} bytes).", flush=True)


def package_all_assets():
    t0 = time.time()
    print("==================================================", flush=True)
    print("      Consolidating Curated Assets into Parquet   ", flush=True)
    print("==================================================", flush=True)

    # 1. Load primary tables
    print(f"Loading {SPLITS_PARQUET}...", flush=True)
    df_splits = pd.read_parquet(SPLITS_PARQUET)
    print(f"Loading {QC_PARQUET}...", flush=True)
    df_qc = pd.read_parquet(QC_PARQUET)
    print(f"Loading {AIMNET_PARQUET}...", flush=True)
    df_aimnet = pd.read_parquet(AIMNET_PARQUET)

    # Merge tables cleanly without duplicate column suffixes
    common_qc = [c for c in df_qc.columns if c in df_splits.columns and c != "assay_inchikey"]
    df_qc_clean = df_qc.drop(columns=common_qc)
    df_master = df_splits.merge(df_qc_clean, on="assay_inchikey", how="left")

    common_aim = [c for c in df_aimnet.columns if c in df_master.columns and c != "assay_inchikey"]
    df_aimnet_clean = df_aimnet.drop(columns=common_aim)
    df_master = df_master.merge(df_aimnet_clean, on="assay_inchikey", how="left")
    assert len(df_master) == 6145, f"Expected 6,145 rows, got {len(df_master)}"

    # 2. Generate predictions and conformal p-values
    df_master = generate_predictions_and_pvalues(df_master)

    # 3. Attach MMP annotations
    df_master = attach_mmp_annotations(df_master)

    # 4. Save primary parquet
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df_master.to_parquet(OUT_PARQUET, index=False, compression="snappy")
    file_size_mb = OUT_PARQUET.stat().st_size / (1024 * 1024)
    print(f"\nSaved consolidated table to {OUT_PARQUET} ({file_size_mb:.2f} MB).", flush=True)
    assert file_size_mb <= 12.0, f"File size {file_size_mb:.2f} MB exceeds 12 MB limit!"

    # 5. Measure cold-load latency on CPU
    t_load = time.time()
    df_test = pd.read_parquet(OUT_PARQUET)
    dt_ms = (time.time() - t_load) * 1000
    print(f"Cold-load benchmark: {len(df_test)} rows loaded in {dt_ms:.1f} ms.", flush=True)
    assert dt_ms < 150.0, f"Load time {dt_ms:.1f}ms exceeds 150ms SLA!"

    # 6. Build fallback sample
    build_fallback_sample(df_master)

    # 7. Generate embedded assets module
    generate_embedded_assets_module()

    total_time = time.time() - t0
    print(f"\nAsset packaging successfully completed in {total_time:.1f}s.")


if __name__ == "__main__":
    if "--embedded-only" in sys.argv:
        generate_embedded_assets_module()
    else:
        package_all_assets()
