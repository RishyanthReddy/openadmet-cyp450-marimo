"""
Unit tests for EC-1-1-01: OpenADMET primary dataset curation.
"""

from pathlib import Path
import pandas as pd
import pytest
from rdkit import Chem

BASE_DIR = Path(__file__).resolve().parent.parent
PARQUET_PATH = BASE_DIR / "data" / "curated" / "openadmet_primary.parquet"
CSV_PATH = BASE_DIR / "data" / "curated" / "openadmet_primary.csv"


@pytest.fixture(scope="module")
def df_curated():
    assert PARQUET_PATH.exists(), f"Curated Parquet file missing at {PARQUET_PATH}"
    df = pd.read_parquet(PARQUET_PATH)
    return df


def test_row_count_and_columns(df_curated):
    assert len(df_curated) == 6145
    required_cols = {
        "molecule_name", "assay_smiles", "assay_inchikey",
        "grouping_parent_smiles", "grouping_parent_inchikey",
        "murcko_scaffold_smiles",
        "cyp3a4_is_tdi", "mask_cyp3a4",
        "cyp2d6_is_tdi", "mask_cyp2d6",
        "mask_joint_both",
        "mw", "logp", "tpsa", "hbd", "hba", "rotbonds", "heavy_atom_count",
    }
    assert required_cols.issubset(set(df_curated.columns))


def test_dual_smiles_integrity(df_curated):
    for _, row in df_curated.head(100).iterrows():
        # Verify assay smiles parses
        m_assay = Chem.MolFromSmiles(row["assay_smiles"])
        assert m_assay is not None
        assert Chem.MolToInchiKey(m_assay) == row["assay_inchikey"]

        # Verify parent smiles parses
        m_parent = Chem.MolFromSmiles(row["grouping_parent_smiles"])
        assert m_parent is not None
        assert Chem.MolToInchiKey(m_parent) == row["grouping_parent_inchikey"]


def test_endpoint_mask_distributions(df_curated):
    # CYP3A4
    mask_3a4 = df_curated["mask_cyp3a4"]
    assert mask_3a4.sum() == 3584
    pos_3a4 = df_curated.loc[mask_3a4, "cyp3a4_is_tdi"].sum()
    assert pos_3a4 == 764
    assert df_curated.loc[~mask_3a4, "cyp3a4_is_tdi"].isna().all()

    # CYP2D6
    mask_2d6 = df_curated["mask_cyp2d6"]
    assert mask_2d6.sum() == 1497
    pos_2d6 = df_curated.loc[mask_2d6, "cyp2d6_is_tdi"].sum()
    assert pos_2d6 == 324
    assert df_curated.loc[~mask_2d6, "cyp2d6_is_tdi"].isna().all()

    # Joint
    assert df_curated["mask_joint_both"].sum() == 259


def test_physicochemical_bounds(df_curated):
    assert (df_curated["mw"] > 0).all()
    assert (df_curated["heavy_atom_count"] > 0).all()
    assert (df_curated["tpsa"] >= 0).all()
