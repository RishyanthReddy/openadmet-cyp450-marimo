#!/usr/bin/env python3
"""
Sample 50 diverse drug-like molecules from OpenADMET with 3D ETKDGv3 coordinates
to benchmark AIMNet2-NSE on Beam Cloud GPU.
"""

from __future__ import annotations

import json
from pathlib import Path
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_TDI = BASE_DIR / "data" / "raw" / "cyp-challenge-TRAIN_TDI.csv"
OUT_DIR = BASE_DIR / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_50_molecules_3d() -> list[dict]:
    df = pd.read_csv(RAW_TDI).dropna(subset=["CYP3A4_is_TDI"])
    df["CYP3A4_is_TDI"] = df["CYP3A4_is_TDI"].astype(bool)

    pos = df[df["CYP3A4_is_TDI"] == True].sample(n=25, random_state=42)
    neg = df[df["CYP3A4_is_TDI"] == False].sample(n=25, random_state=42)
    sample_df = pd.concat([pos, neg]).sample(frac=1.0, random_state=42).reset_index(drop=True)

    prepared = []
    failed_embed = 0

    params = AllChem.ETKDGv3()
    params.randomSeed = 42

    for _, row in sample_df.iterrows():
        smi = row["SMILES"]
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        mol = Chem.AddHs(mol)
        res = AllChem.EmbedMolecule(mol, params)
        if res != 0:
            # Fallback with random coordinates
            res = AllChem.EmbedMolecule(mol, useRandomCoords=True, randomSeed=42)
        if res != 0:
            failed_embed += 1
            continue

        conf = mol.GetConformer()
        atomic_numbers = [atom.GetAtomicNum() for atom in mol.GetAtoms()]
        coords = [[round(pos.x, 4), round(pos.y, 4), round(pos.z, 4)] for pos in (conf.GetAtomPosition(i) for i in range(mol.GetNumAtoms()))]

        prepared.append({
            "id": row["Molecule_Name"],
            "smiles": smi,
            "cyp3a4_is_tdi": bool(row["CYP3A4_is_TDI"]),
            "num_atoms": len(atomic_numbers),
            "atomic_numbers": atomic_numbers,
            "coords": coords,
        })

    print(f"Generated 3D conformers for {len(prepared)} molecules (failed: {failed_embed}).")
    out_file = OUT_DIR / "aimnet2_input_50.json"
    with open(out_file, "w") as f:
        json.dump(prepared, f, indent=2)
    print(f"Saved input payload to {out_file} ({out_file.stat().st_size:,} bytes).")
    return prepared


if __name__ == "__main__":
    generate_50_molecules_3d()
