#!/usr/bin/env python3
"""
EC-1-1-01: Standardize OpenADMET Primary TDI Dataset.

Curates the 6,145 compounds from cyp-challenge-TRAIN_TDI.csv:
  1. Preserves untouched original `assay_smiles` (for modeling and 2D/3D coordinate generation).
  2. Generates `grouping_parent_smiles` via RDKit standard desalting and neutralization (for scaffold splitting).
  3. Computes canonical InChIKey for both assay and parent structures.
  4. Generates Bemis-Murcko scaffolds for downstream cluster-stratified splitting.
  5. Computes physicochemical properties (MW, LogP, TPSA, HBD, HBA, RotBonds, CSP3).
  6. Creates explicit boolean masks:
       - `mask_cyp3a4`: Exactly 3,584 labeled (764 True, 2,820 False)
       - `mask_cyp2d6`: Exactly 1,497 labeled (324 True, 1,173 False)
       - `mask_joint_both`: Exactly 259 labeled for both isoforms
  7. Preserves auxiliary assay context columns while enforcing the target-leakage guardrail contract.
  8. Saves standardized dataset to `data/curated/openadmet_primary.parquet` and `.csv`.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski
from rdkit.Chem.MolStandardize import rdMolStandardize
from rdkit.Chem.Scaffolds import MurckoScaffold

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_INPUT = BASE_DIR / "data" / "raw" / "cyp-challenge-TRAIN_TDI.csv"
OUT_PARQUET = BASE_DIR / "data" / "curated" / "openadmet_primary.parquet"
OUT_CSV = BASE_DIR / "data" / "curated" / "openadmet_primary.csv"


def curate_dataset() -> pd.DataFrame:
    print(f"Loading raw OpenADMET data from {RAW_INPUT}...")
    df_raw = pd.read_csv(RAW_INPUT)
    assert len(df_raw) == 6145, f"Expected 6,145 rows, found {len(df_raw)}"

    # Initialize RDKit standardizers
    lfc = rdMolStandardize.LargestFragmentChooser()
    uncharger = rdMolStandardize.Uncharger()

    records = []
    quarantined = []

    print("Standardizing molecules (dual-SMILES policy, scaffolds, descriptors)...")
    for idx, row in df_raw.iterrows():
        mol_name = row["Molecule_Name"]
        assay_smi = row["SMILES"]

        mol = Chem.MolFromSmiles(assay_smi)
        if mol is None:
            quarantined.append({"row_index": idx, "molecule_name": mol_name, "smiles": assay_smi, "reason": "RDKit parse failure"})
            continue

        assay_inchikey = Chem.MolToInchiKey(mol)

        # Parent standardization: strip salts, uncharge
        try:
            parent_mol = lfc.choose(mol)
            parent_mol = uncharger.uncharge(parent_mol)
            parent_smi = Chem.MolToSmiles(parent_mol, canonical=True)
            parent_inchikey = Chem.MolToInchiKey(parent_mol)
        except Exception as e:
            parent_smi = assay_smi
            parent_inchikey = assay_inchikey
            parent_mol = mol

        # Bemis-Murcko scaffold
        try:
            scaffold_smi = MurckoScaffold.MurckoScaffoldSmiles(mol=parent_mol)
        except Exception:
            scaffold_smi = ""

        # Descriptors
        mw = round(Descriptors.MolWt(mol), 3)
        logp = round(Descriptors.MolLogP(mol), 3)
        tpsa = round(Descriptors.TPSA(mol), 3)
        hbd = int(Lipinski.NumHDonors(mol))
        hba = int(Lipinski.NumHAcceptors(mol))
        rotbonds = int(Lipinski.NumRotatableBonds(mol))
        heavy_atoms = int(mol.GetNumHeavyAtoms())
        f_csp3 = round(Descriptors.FractionCSP3(mol), 3)
        ring_count = int(Lipinski.RingCount(mol))

        # Endpoints and Masks
        cyp3a4_raw = row["CYP3A4_is_TDI"]
        cyp2d6_raw = row["CYP2D6_is_TDI"]

        has_3a4 = pd.notna(cyp3a4_raw)
        has_2d6 = pd.notna(cyp2d6_raw)

        cyp3a4_label = bool(cyp3a4_raw) if has_3a4 else None
        cyp2d6_label = bool(cyp2d6_raw) if has_2d6 else None

        records.append({
            "molecule_name": mol_name,
            "assay_smiles": assay_smi,
            "assay_inchikey": assay_inchikey,
            "grouping_parent_smiles": parent_smi,
            "grouping_parent_inchikey": parent_inchikey,
            "murcko_scaffold_smiles": scaffold_smi,
            # Primary Endpoints & Masks
            "cyp3a4_is_tdi": cyp3a4_label,
            "mask_cyp3a4": has_3a4,
            "cyp2d6_is_tdi": cyp2d6_label,
            "mask_cyp2d6": has_2d6,
            "mask_joint_both": (has_3a4 and has_2d6),
            # Physicochemical Descriptors
            "mw": mw,
            "logp": logp,
            "tpsa": tpsa,
            "hbd": hbd,
            "hba": hba,
            "rotbonds": rotbonds,
            "heavy_atom_count": heavy_atoms,
            "fraction_csp3": f_csp3,
            "ring_count": ring_count,
            # Auxiliary Non-Target Columns (Strictly quarantined from model feature sets)
            "cyp3a4_pic50_direct_inhibition": row.get("CYP3A4_pIC50_direct_inhibition"),
            "cyp3a4_pic50_tdi_condition": row.get("CYP3A4_pIC50_TDI_condition"),
            "cyp2d6_pic50_direct_inhibition": row.get("CYP2D6_pIC50_direct_inhibition"),
            "cyp2d6_pic50_tdi_condition": row.get("CYP2D6_pIC50_TDI_condition"),
        })

    print(f"Standardized {len(records)} molecules. Quarantined failures: {len(quarantined)}.")
    assert len(quarantined) == 0, f"Unexpected quarantine failures: {quarantined}"
    assert len(records) == 6145, f"Expected 6,145 output rows, got {len(records)}"

    df_curated = pd.DataFrame(records)

    # Verification Assertions
    mask_3a4 = df_curated["mask_cyp3a4"]
    mask_2d6 = df_curated["mask_cyp2d6"]
    mask_joint = df_curated["mask_joint_both"]

    assert mask_3a4.sum() == 3584, f"Expected 3,584 CYP3A4 labels, got {mask_3a4.sum()}"
    pos_3a4 = df_curated.loc[mask_3a4, "cyp3a4_is_tdi"].sum()
    assert pos_3a4 == 764, f"Expected 764 positive CYP3A4 TDI labels, got {pos_3a4}"

    assert mask_2d6.sum() == 1497, f"Expected 1,497 CYP2D6 labels, got {mask_2d6.sum()}"
    pos_2d6 = df_curated.loc[mask_2d6, "cyp2d6_is_tdi"].sum()
    assert pos_2d6 == 324, f"Expected 324 positive CYP2D6 TDI labels, got {pos_2d6}"

    assert mask_joint.sum() == 259, f"Expected exactly 259 jointly labeled compounds, got {mask_joint.sum()}"

    # Export to Parquet and CSV
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    df_curated.to_parquet(OUT_PARQUET, index=False)
    df_curated.to_csv(OUT_CSV, index=False)

    print(f"\nSuccessfully saved curated dataset:")
    print(f"  Parquet: {OUT_PARQUET} ({OUT_PARQUET.stat().st_size:,} bytes)")
    print(f"  CSV:     {OUT_CSV} ({OUT_CSV.stat().st_size:,} bytes)")
    print(f"\nEndpoint Distribution Summary:")
    print(f"  CYP3A4 Labeled:    {mask_3a4.sum()} (Positives: {pos_3a4} / {pos_3a4/mask_3a4.sum()*100:.2f}%)")
    print(f"  CYP2D6 Labeled:    {mask_2d6.sum()} (Positives: {pos_2d6} / {pos_2d6/mask_2d6.sum()*100:.2f}%)")
    print(f"  Jointly Labeled:   {mask_joint.sum()} ({mask_joint.sum()/len(df_curated)*100:.2f}%)")
    print(f"  Unique Parents:    {df_curated['grouping_parent_inchikey'].nunique()}")
    print(f"  Unique Scaffolds:  {df_curated['murcko_scaffold_smiles'].nunique()}")

    return df_curated


if __name__ == "__main__":
    curate_dataset()
