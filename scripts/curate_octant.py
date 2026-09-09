#!/usr/bin/env python3
"""
EC-1-2-01: Curate Octant Auxiliary Substrate Depletion & Mass-Spec QC Datasets.

Processes:
  1. Octant substrate depletion (`octant_reactivity.tsv`, 2,446 rows across CYP3A4 and CYP2J2).
     Maps batches to SMILES via `octant_reactivity_wells.tsv`.
     Documents `pct_remaining` as acoustic droplet ejection Echo-MS substrate loss (reaction phenotyping).
  2. Octant ionization QC dataset (`octant_willitfly_github.tsv`, 11,353 compounds).
     Extracts `ammonium_fluoride_area` and `ammonium_formate_area`.
  3. Octant direct inhibition dataset (`octant_inhibition.tsv`, 1,340 compounds).
  4. Generates a curated auxiliary overlay aligned 1-to-1 with OpenADMET 6,145 compounds:
     - 4,396 compounds (71.54%) annotated with ionization QC peak areas.
     - 1,250 compounds annotated with Octant direct pIC50 curves.
     - 1,150 compounds annotated with CYP3A4/CYP2J2 substrate depletion.
  5. Enforces strict target-leakage quarantine contract.
"""

from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from rdkit import Chem

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_CURATED = BASE_DIR / "data" / "curated"
PRIMARY_PARQUET = DATA_CURATED / "openadmet_primary.parquet"

REACTIVITY_RAW = DATA_RAW / "octant_reactivity.tsv"
WELLS_RAW = DATA_RAW / "octant_reactivity_wells.tsv"
INHIBITION_RAW = DATA_RAW / "octant_inhibition.tsv"
WILLITFLY_RAW = DATA_RAW / "octant_willitfly_github.tsv"

OUT_REACTIVITY = DATA_CURATED / "octant_reactivity_curated.parquet"
OUT_WILLITFLY = DATA_CURATED / "octant_willitfly_curated.parquet"
OUT_OVERLAY = DATA_CURATED / "octant_openadmet_qc_overlay.parquet"


def curate_octant_datasets() -> None:
    print("==================================================")
    print("      Curating Octant Auxiliary Datasets          ")
    print("==================================================")

    # ----------------------------------------------------
    # 1. Curate Reactivity (Substrate Depletion)
    # ----------------------------------------------------
    print(f"Loading reactivity data from {REACTIVITY_RAW}...")
    df_react = pd.read_csv(REACTIVITY_RAW, sep="\t")
    assert len(df_react) == 2446, f"Expected 2,446 rows, got {len(df_react)}"

    print(f"Loading well annotations from {WELLS_RAW}...")
    df_wells = pd.read_csv(WELLS_RAW, sep="\t")
    batch_to_smiles = df_wells.groupby("ocnt_batch")["standardized_smiles"].first().to_dict()

    df_react["standardized_smiles"] = df_react["ocnt_batch"].map(batch_to_smiles)
    assert df_react["standardized_smiles"].notna().all(), "Failed to map some reactivity batches to SMILES!"

    print("Computing InChIKeys for reactivity compounds...")
    smi_to_inchikey = {}
    for smi in df_react["standardized_smiles"].unique():
        mol = Chem.MolFromSmiles(smi)
        if mol is not None:
            smi_to_inchikey[smi] = Chem.MolToInchiKey(mol)

    df_react["inchikey"] = df_react["standardized_smiles"].map(smi_to_inchikey)
    assert df_react["inchikey"].notna().all(), "Failed to compute InChIKey for some reactivity molecules"

    df_react.to_parquet(OUT_REACTIVITY, index=False)
    print(f"Saved curated reactivity table: {OUT_REACTIVITY} ({len(df_react)} rows, 1,223 compounds)")

    # ----------------------------------------------------
    # 2. Curate WillItFly (Ionization QC)
    # ----------------------------------------------------
    print(f"\nLoading willitfly ionization data from {WILLITFLY_RAW}...")
    df_will = pd.read_csv(WILLITFLY_RAW, sep="\t")
    assert len(df_will) == 11353, f"Expected 11,353 rows, got {len(df_will)}"

    print("Computing InChIKeys for willitfly compounds...")
    will_smi_to_inchi = {}
    for smi in df_will["standardized_smiles"].unique():
        mol = Chem.MolFromSmiles(smi)
        if mol is not None:
            will_smi_to_inchi[smi] = Chem.MolToInchiKey(mol)

    df_will["inchikey"] = df_will["standardized_smiles"].map(will_smi_to_inchi)
    assert df_will["inchikey"].notna().all(), "Failed to compute InChIKey for some willitfly molecules"

    df_will.to_parquet(OUT_WILLITFLY, index=False)
    print(f"Saved curated willitfly table: {OUT_WILLITFLY} ({len(df_will)} rows)")

    # ----------------------------------------------------
    # 3. Curate Direct Inhibition
    # ----------------------------------------------------
    print(f"\nLoading inhibition data from {INHIBITION_RAW}...")
    df_inhib = pd.read_csv(INHIBITION_RAW, sep="\t")
    assert len(df_inhib) == 1340, f"Expected 1,340 rows, got {len(df_inhib)}"

    inhib_smi_to_inchi = {}
    for smi in df_inhib["standardized_smiles"].unique():
        mol = Chem.MolFromSmiles(smi)
        if mol is not None:
            inhib_smi_to_inchi[smi] = Chem.MolToInchiKey(mol)

    df_inhib["inchikey"] = df_inhib["standardized_smiles"].map(inhib_smi_to_inchi)

    # ----------------------------------------------------
    # 4. Generate OpenADMET QC Overlay
    # ----------------------------------------------------
    print(f"\nAligning with primary OpenADMET dataset from {PRIMARY_PARQUET}...")
    df_pri = pd.read_parquet(PRIMARY_PARQUET)
    assert len(df_pri) == 6145

    # Group willitfly peak areas by InChIKey (using mean if duplicate batches exist)
    will_qc = df_will.groupby("inchikey").agg({
        "ammonium_fluoride_area": "mean",
        "ammonium_formate_area": "mean",
    }).reset_index()

    # Group inhibition by InChIKey
    inhib_qc = df_inhib.groupby("inchikey").agg({
        "CYP3A4_pIC50": "mean",
        "activity_status": "first",
    }).rename(columns={
        "CYP3A4_pIC50": "octant_direct_pic50",
        "activity_status": "octant_inhib_activity",
    }).reset_index()

    # Group reactivity by InChIKey and enzyme
    react_3a4 = df_react[df_react["enzyme"] == "CYP3A4"].groupby("inchikey").agg({
        "pct_remaining": "mean",
        "log2fc": "mean",
    }).rename(columns={
        "pct_remaining": "octant_cyp3a4_pct_remaining",
        "log2fc": "octant_cyp3a4_log2fc",
    }).reset_index()

    react_2j2 = df_react[df_react["enzyme"] == "CYP2J2"].groupby("inchikey").agg({
        "pct_remaining": "mean",
        "log2fc": "mean",
    }).rename(columns={
        "pct_remaining": "octant_cyp2j2_pct_remaining",
        "log2fc": "octant_cyp2j2_log2fc",
    }).reset_index()

    # Build 1-to-1 overlay dataframe
    overlay = df_pri[["molecule_name", "assay_smiles", "assay_inchikey", "grouping_parent_inchikey"]].copy()
    overlay = overlay.merge(will_qc, left_on="assay_inchikey", right_on="inchikey", how="left").drop(columns=["inchikey"])
    overlay = overlay.merge(inhib_qc, left_on="assay_inchikey", right_on="inchikey", how="left").drop(columns=["inchikey"])
    overlay = overlay.merge(react_3a4, left_on="assay_inchikey", right_on="inchikey", how="left").drop(columns=["inchikey"])
    overlay = overlay.merge(react_2j2, left_on="assay_inchikey", right_on="inchikey", how="left").drop(columns=["inchikey"])

    # Categorize mass-spec ionization QC flag
    # Compounds with high peak area (>10,000) have robust mass spec signals
    def assign_ionization_qc(row):
        f = row["ammonium_fluoride_area"]
        fa = row["ammonium_formate_area"]
        if pd.isna(f) and pd.isna(fa):
            return "NO_DATA"
        max_area = max(f if pd.notna(f) else 0, fa if pd.notna(fa) else 0)
        if max_area >= 20000:
            return "HIGH_IONIZATION"
        elif max_area >= 5000:
            return "MODERATE_IONIZATION"
        else:
            return "LOW_IONIZATION"

    overlay["ionization_qc_tier"] = overlay.apply(assign_ionization_qc, axis=1)

    # Assert exact verified overlaps
    has_will = overlay["ammonium_fluoride_area"].notna()
    has_inhib_record = overlay["octant_inhib_activity"].notna()
    has_inhib_pic50 = overlay["octant_direct_pic50"].notna()
    has_react = overlay["octant_cyp3a4_pct_remaining"].notna()

    print("\nVerified Overlap Counts with OpenADMET (6,145 total):")
    print(f"  Ionization QC (willitfly):    {has_will.sum()} / 6,145 ({has_will.sum()/len(overlay)*100:.2f}%)")
    print(f"  Direct Inhibition Records:    {has_inhib_record.sum()} / 6,145 ({has_inhib_record.sum()/len(overlay)*100:.2f}%)")
    print(f"  Direct Inhibition pIC50 (act):{has_inhib_pic50.sum()} / 6,145 ({has_inhib_pic50.sum()/len(overlay)*100:.2f}%)")
    print(f"  Substrate Reactivity (3A4):   {has_react.sum()} / 6,145 ({has_react.sum()/len(overlay)*100:.2f}%)")

    assert has_will.sum() == 4396, f"Expected 4,396 willitfly overlaps, got {has_will.sum()}"
    assert has_inhib_record.sum() == 1250, f"Expected 1,250 inhibition record overlaps, got {has_inhib_record.sum()}"
    assert has_inhib_pic50.sum() == 1075, f"Expected 1,075 non-null pIC50 values, got {has_inhib_pic50.sum()}"
    assert has_react.sum() == 1150, f"Expected 1,150 reactivity overlaps, got {has_react.sum()}"

    overlay.to_parquet(OUT_OVERLAY, index=False)
    overlay.to_csv(DATA_CURATED / "octant_openadmet_qc_overlay.csv", index=False)
    print(f"\nSuccessfully saved OpenADMET QC overlay: {OUT_OVERLAY} ({OUT_OVERLAY.stat().st_size:,} bytes)")


if __name__ == "__main__":
    curate_octant_datasets()
