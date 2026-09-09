"""
Unit tests for EC-2-2-03: Matched Molecular Pair (MMP) transformations extraction.
"""

import json
import sys
from pathlib import Path
from rdkit import Chem
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
MMP_JSON = BASE_DIR / "data" / "packaged" / "mmp_transformations.json"


@pytest.fixture(scope="module")
def mmp_data():
    assert MMP_JSON.exists(), f"Missing {MMP_JSON}"
    with open(MMP_JSON) as f:
        return json.load(f)


def test_metadata_integrity(mmp_data):
    meta = mmp_data["metadata"]
    assert meta["total_unique_pairs"] == 34
    assert "CYP3A4" in meta["counts_by_isoform"]
    assert "CYP2D6" in meta["counts_by_isoform"]
    assert meta["counts_by_isoform"]["CYP3A4"] == 25
    assert meta["counts_by_isoform"]["CYP2D6"] == 9
    assert meta["curation_status"] == "OPENADMET_LABEL_SHIFT"


def test_pairs_chemical_validity_and_activity_flips(mmp_data):
    pairs = mmp_data["pairs"]
    assert len(pairs) == mmp_data["metadata"]["total_unique_pairs"]

    # Verify uniqueness of compound pairs
    unique_keys = set()
    for pair in pairs:
        assert pair["mmp_id"].startswith("MMP-")
        assert pair["isoform"] in ["CYP3A4", "CYP2D6"]
        assert pair["curation_status"] == "OPENADMET_LABEL_SHIFT"

        # Check molecules
        inact = pair["mol_inactive"]
        act = pair["mol_active"]
        pair_key = (inact["molecule_name"], act["molecule_name"])
        assert pair_key not in unique_keys, f"Duplicate pair detected: {pair_key}"
        unique_keys.add(pair_key)

        assert inact["is_tdi"] is False
        assert act["is_tdi"] is True
        assert len(inact["parent_inchikey"]) == 27
        assert len(act["parent_inchikey"]) == 27

        # Chemical validity
        mol_inact = Chem.MolFromSmiles(inact["smiles"])
        mol_act = Chem.MolFromSmiles(act["smiles"])
        assert mol_inact is not None
        assert mol_act is not None

        # Core validity
        core_mol = Chem.MolFromSmiles(pair["core_smarts"])
        assert core_mol is not None
        assert core_mol.GetNumHeavyAtoms() >= 10
        assert core_mol.GetRingInfo().NumRings() >= 1

        # Provenance tags & row-level assay metadata
        assert inact["holdout_split"] in ["TRAIN", "CALIBRATION", "TEST"]
        assert act["holdout_split"] in ["TRAIN", "CALIBRATION", "TEST"]
        assert 0 <= inact["cv_fold_5"] <= 4
        assert 0 <= act["cv_fold_5"] <= 4
        assert inact["source_row_id"].startswith("OCTANT_SPLITS_ROW_")
        assert act["source_row_id"].startswith("OCTANT_SPLITS_ROW_")
        assert inact["assay_id"] in ["OCTANT_CYP3A4_HLM_IC50_SHIFT", "OCTANT_CYP2D6_HLM_IC50_SHIFT"]
        assert act["assay_id"] in ["OCTANT_CYP3A4_HLM_IC50_SHIFT", "OCTANT_CYP2D6_HLM_IC50_SHIFT"]
        assert inact["source_dataset"] == "cyp-challenge-TRAIN_TDI.csv"
        assert act["source_dataset"] == "cyp-challenge-TRAIN_TDI.csv"
        assert inact["direct_pic50"] is not None and inact["tdi_pic50"] is not None
        assert act["direct_pic50"] is not None and act["tdi_pic50"] is not None


def test_transformation_syntax(mmp_data):
    for pair in mmp_data["pairs"]:
        trans = pair["transformation"]
        assert " >> " in trans
        sub_act, sub_in = trans.split(" >> ")
        assert sub_act == pair["substituent_active"]
        assert sub_in == pair["substituent_inactive"]
        assert pair["measured_label_flip"] == "OPENADMET_ACTIVE_TO_INACTIVE"


def test_mmp_generator_reproducibility(mmp_data):
    """Verifies that running the extraction pipeline deterministically reproduces all 34 packaged pairs."""
    from scripts.generate_mmps import extract_isoform_mmps
    import pandas as pd

    splits_parquet = BASE_DIR / "data" / "curated" / "cyp_splits.parquet"
    df = pd.read_parquet(splits_parquet)

    df_3a4 = df[df["mask_cyp3a4"]].copy().reset_index(drop=True)
    p_3a4 = extract_isoform_mmps(df_3a4, "cyp3a4_is_tdi", "CYP3A4", max_pairs=25)

    df_2d6 = df[df["mask_cyp2d6"]].copy().reset_index(drop=True)
    p_2d6 = extract_isoform_mmps(df_2d6, "cyp2d6_is_tdi", "CYP2D6", max_pairs=9)

    generated = p_3a4 + p_2d6
    assert len(generated) == 34
    packaged_pairs = mmp_data["pairs"]
    assert len(packaged_pairs) == 34

    for i in range(34):
        gen = generated[i]
        pack = packaged_pairs[i]
        assert gen["isoform"] == pack["isoform"]
        assert gen["core_smarts"] == pack["core_smarts"]
        assert gen["transformation"] == pack["transformation"]
        assert gen["mol_inactive"]["molecule_name"] == pack["mol_inactive"]["molecule_name"]
        assert gen["mol_active"]["molecule_name"] == pack["mol_active"]["molecule_name"]
        h_act = Chem.MolFromSmiles(gen["mol_active"]["smiles"]).GetNumHeavyAtoms()
        h_inact = Chem.MolFromSmiles(gen["mol_inactive"]["smiles"]).GetNumHeavyAtoms()
        assert abs(h_act - h_inact) <= 6

