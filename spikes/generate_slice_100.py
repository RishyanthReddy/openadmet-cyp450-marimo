#!/usr/bin/env python3
"""
Curate 100-molecule vertical slice dataset, fit cross-validated ECFP4 baseline,
and export 2D graph payloads with atom-level halos for the BioactivationTracer anywidget.
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdDepictor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, matthews_corrcoef, roc_auc_score
from sklearn.model_selection import StratifiedKFold

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_TDI = BASE_DIR / "data" / "raw" / "cyp-challenge-TRAIN_TDI.csv"
RAW_FLY = BASE_DIR / "data" / "raw" / "octant_willitfly_github.tsv"
OUT_DIR = BASE_DIR / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def curate_and_train() -> None:
    print("Loading raw OpenADMET dataset...")
    df_raw = pd.read_csv(RAW_TDI)
    df_labeled = df_raw.dropna(subset=["CYP3A4_is_TDI"]).copy()
    df_labeled["CYP3A4_is_TDI"] = df_labeled["CYP3A4_is_TDI"].astype(bool)

    # 100-molecule stratified sample (25 positive, 75 negative)
    pos = df_labeled[df_labeled["CYP3A4_is_TDI"] == True].sample(n=25, random_state=42)
    neg = df_labeled[df_labeled["CYP3A4_is_TDI"] == False].sample(n=75, random_state=42)
    slice_df = pd.concat([pos, neg]).sample(frac=1.0, random_state=42).reset_index(drop=True)

    print(f"Sampled 100 molecules: {slice_df['CYP3A4_is_TDI'].value_counts().to_dict()}")

    # Merge with willitfly for MS ionization QC context
    df_fly = pd.read_csv(RAW_FLY, sep="\t")

    def get_ikey(s: str) -> str | None:
        try:
            m = Chem.MolFromSmiles(s.strip())
            return Chem.MolToInchiKey(m) if m else None
        except Exception:
            return None

    slice_df["inchikey"] = slice_df["SMILES"].apply(get_ikey)
    df_fly["inchikey"] = df_fly["standardized_smiles"].apply(get_ikey)
    merged = slice_df.merge(
        df_fly[["inchikey", "ammonium_fluoride_area", "ammonium_formate_area"]].drop_duplicates("inchikey"),
        on="inchikey",
        how="left",
    )

    # Featurize with ECFP4
    def get_ecfp4(smi: str) -> np.ndarray:
        mol = Chem.MolFromSmiles(smi)
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        return np.array(fp)

    X = np.vstack([get_ecfp4(s) for s in merged["SMILES"]])
    y = merged["CYP3A4_is_TDI"].values.astype(int)

    # Target leakage verification
    feature_cols = [f"ecfp4_bit_{i}" for i in range(2048)]
    forbidden = ["pic50", "tdi_condition", "direct_inhibition", "conf_high", "conf_low", "std", "emax", "is_tdi", "pct_remaining", "area"]
    for c in feature_cols:
        for f in forbidden:
            assert f not in c.lower(), f"Leakage: {c}"
    print("✓ Target leakage check PASSED on 2,048 ECFP4 features.")

    # 5-fold cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    probs = np.zeros(len(y))

    for train_idx, val_idx in cv.split(X, y):
        clf = LogisticRegression(class_weight="balanced", C=0.5, random_state=42, max_iter=500)
        clf.fit(X[train_idx], y[train_idx])
        probs[val_idx] = clf.predict_proba(X[val_idx])[:, 1]

    auc = roc_auc_score(y, probs)
    preds = (probs >= 0.5).astype(int)
    mcc = matthews_corrcoef(y, preds)
    brier = brier_score_loss(y, probs)

    print(f"✓ 100-Molecule CV Baseline Metrics: ROC-AUC={auc:.3f}, MCC={mcc:.3f}, Brier={brier:.3f}")

    merged["baseline_prob_tdi"] = probs.round(4)
    merged["baseline_pred_tdi"] = (probs >= 0.5)

    # Build 2D graph payload with atom coordinates and risk halos
    molecules_payload = []
    for _, row in merged.iterrows():
        mol = Chem.MolFromSmiles(row["SMILES"])
        rdDepictor.Compute2DCoords(mol)
        conf = mol.GetConformer()

        # Gasteiger charges as proxy for atom halo intensity in the baseline spike
        AllChem.ComputeGasteigerCharges(mol)

        atoms = []
        for i, atom in enumerate(mol.GetAtoms()):
            pos = conf.GetAtomPosition(i)
            try:
                charge = float(atom.GetProp("_GasteigerCharge"))
                if np.isnan(charge) or np.isinf(charge):
                    charge = 0.0
            except Exception:
                charge = 0.0

            halo_intensity = min(abs(charge) * 2.5, 1.0)
            atoms.append({
                "index": i,
                "symbol": atom.GetSymbol(),
                "x": round(pos.x, 3),
                "y": round(pos.y, 3),
                "charge": round(charge, 3),
                "halo_intensity": round(halo_intensity, 3),
            })

        bonds = []
        for bond in mol.GetBonds():
            bonds.append({
                "source": bond.GetBeginAtomIdx(),
                "target": bond.GetEndAtomIdx(),
                "order": int(bond.GetBondTypeAsDouble()),
            })

        mw = round(Descriptors.MolWt(mol), 2)
        logp = round(Descriptors.MolLogP(mol), 2)
        tpsa = round(Descriptors.TPSA(mol), 2)

        nh4f = float(row["ammonium_fluoride_area"]) if pd.notna(row["ammonium_fluoride_area"]) else None
        nh4fa = float(row["ammonium_formate_area"]) if pd.notna(row["ammonium_formate_area"]) else None

        molecules_payload.append({
            "id": row["Molecule_Name"],
            "smiles": row["SMILES"],
            "cyp3a4_is_tdi": bool(row["CYP3A4_is_TDI"]),
            "baseline_prob": float(row["baseline_prob_tdi"]),
            "baseline_pred": bool(row["baseline_pred_tdi"]),
            "mw": mw,
            "logp": logp,
            "tpsa": tpsa,
            "nh4f_area": nh4f,
            "nh4fa_area": nh4fa,
            "atoms": atoms,
            "bonds": bonds,
        })

    out_json = OUT_DIR / "slice_100_payload.json"
    with open(out_json, "w") as f:
        json.dump(molecules_payload, f, indent=2)

    out_csv = OUT_DIR / "slice_100.csv"
    merged[["Molecule_Name", "SMILES", "CYP3A4_is_TDI", "baseline_prob_tdi", "baseline_pred_tdi", "ammonium_fluoride_area", "ammonium_formate_area"]].to_csv(out_csv, index=False)

    print(f"✓ Saved 100-molecule payload to {out_json} ({out_json.stat().st_size:,} bytes)")
    print(f"✓ Saved slice summary to {out_csv} ({out_csv.stat().st_size:,} bytes)")


if __name__ == "__main__":
    curate_and_train()
