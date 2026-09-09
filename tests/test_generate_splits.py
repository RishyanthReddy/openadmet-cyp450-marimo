"""
Unit tests for EC-1-3-01: Leak-proof multi-level splitting engine.
"""

from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
SPLITS_PARQUET = BASE_DIR / "data" / "curated" / "cyp_splits.parquet"


@pytest.fixture(scope="module")
def df_splits():
    assert SPLITS_PARQUET.exists(), f"Missing {SPLITS_PARQUET}"
    return pd.read_parquet(SPLITS_PARQUET)


def test_row_count_and_columns(df_splits):
    assert len(df_splits) == 6145
    assert "cv_fold_5" in df_splits.columns
    assert "holdout_split" in df_splits.columns
    assert set(df_splits["cv_fold_5"].unique()) == {0, 1, 2, 3, 4}
    assert set(df_splits["holdout_split"].unique()) == {"TRAIN", "CALIBRATION", "TEST"}


def test_cv_fold_size_balance(df_splits):
    counts = df_splits["cv_fold_5"].value_counts()
    for f in range(5):
        size = counts[f]
        # Target is ~1,229; assert strictly within 1,180 - 1,290 (within ~4%)
        assert 1180 <= size <= 1290, f"Fold {f} size {size} is out of balanced bounds!"


def test_zero_parent_leakage_across_all_folds(df_splits):
    for f1 in range(5):
        for f2 in range(f1 + 1, 5):
            parents_f1 = set(df_splits[df_splits["cv_fold_5"] == f1]["grouping_parent_inchikey"])
            parents_f2 = set(df_splits[df_splits["cv_fold_5"] == f2]["grouping_parent_inchikey"])
            shared = parents_f1.intersection(parents_f2)
            assert len(shared) == 0, f"Found {len(shared)} shared parent InChIKeys between Fold {f1} and Fold {f2}!"


def test_zero_scaffold_leakage_across_all_folds(df_splits):
    for f1 in range(5):
        for f2 in range(f1 + 1, 5):
            sub1 = df_splits[df_splits["cv_fold_5"] == f1]
            sub2 = df_splits[df_splits["cv_fold_5"] == f2]
            scaffs_f1 = set(sub1[sub1["murcko_scaffold_smiles"] != ""]["murcko_scaffold_smiles"])
            scaffs_f2 = set(sub2[sub2["murcko_scaffold_smiles"] != ""]["murcko_scaffold_smiles"])
            shared = scaffs_f1.intersection(scaffs_f2)
            assert len(shared) == 0, f"Found {len(shared)} shared scaffolds between Fold {f1} and Fold {f2}!"


def test_target_stratification(df_splits):
    for f in range(5):
        sub = df_splits[df_splits["cv_fold_5"] == f]
        pos_3a4 = (sub["cyp3a4_is_tdi"] == True).sum()
        tot_3a4 = sub["mask_cyp3a4"].sum()
        rate_3a4 = pos_3a4 / tot_3a4 * 100
        # Target rate is 21.32%; assert within 19% - 24%
        assert 19.0 <= rate_3a4 <= 24.0, f"Fold {f} CYP3A4 positive rate {rate_3a4:.2f}% out of stratified range!"


def test_holdout_split_integrity(df_splits):
    train = df_splits[df_splits["holdout_split"] == "TRAIN"]
    calib = df_splits[df_splits["holdout_split"] == "CALIBRATION"]
    test = df_splits[df_splits["holdout_split"] == "TEST"]

    assert len(train) + len(calib) + len(test) == 6145
    assert len(set(train["grouping_parent_inchikey"]).intersection(set(test["grouping_parent_inchikey"]))) == 0
    assert len(set(train["grouping_parent_inchikey"]).intersection(set(calib["grouping_parent_inchikey"]))) == 0
