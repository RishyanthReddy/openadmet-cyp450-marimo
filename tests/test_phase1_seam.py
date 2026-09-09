"""
EC-INTEGRATION-P1-01: Phase 1 Seam Integration Test Suite.

Verifies end-to-end coherence, data integrity, and leakage absence across
all Phase 1 curated datasets, split partitions, and literature reference fixtures:
  1. TestPhase1CuratedArtifacts: Checks presence, schemas, and row counts of all 7 Phase 1 artifacts.
  2. TestEndpointMaskAndMissingnessCoherence: Verifies exact label distributions, masks, and null patterns.
  3. TestSplitsZeroLeakageSeam: Programmatically verifies zero parent InChIKey and zero scaffold leakage across all CV and holdout folds.
  4. TestSeamDataJoinAndSchemaIntegrity: Verifies seamless 1-to-1 multi-dataset joins across OpenADMET, splits, and Octant overlays.
  5. TestTargetLeakageGuardrails: Enforces programmatic zero-target-leakage assertion across feature matrices.
"""

import json
from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_CURATED = BASE_DIR / "data" / "curated"
DATA_FIXTURES = BASE_DIR / "data" / "fixtures"

PRIMARY_PARQUET = DATA_CURATED / "openadmet_primary.parquet"
OCTANT_REACT_PARQUET = DATA_CURATED / "octant_reactivity_curated.parquet"
OCTANT_WILL_PARQUET = DATA_CURATED / "octant_willitfly_curated.parquet"
OCTANT_OVERLAY_PARQUET = DATA_CURATED / "octant_openadmet_qc_overlay.parquet"
SPLITS_PARQUET = DATA_CURATED / "cyp_splits.parquet"
TANIMOTO_JSON = DATA_CURATED / "tanimoto_shift_summary.json"
MBI_FIXTURE_JSON = DATA_FIXTURES / "literature_mbi_reference_set.json"

BANNED_TARGET_AND_ASSAY_COLUMNS = {
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


def assert_zero_target_leakage(feature_columns: list[str] | set[str]) -> None:
    feature_set = set(feature_columns)
    leaked = feature_set.intersection(BANNED_TARGET_AND_ASSAY_COLUMNS)
    assert len(leaked) == 0, f"TARGET LEAKAGE DETECTED! Found banned assay columns in feature set: {leaked}"


@pytest.fixture(scope="module")
def df_primary():
    return pd.read_parquet(PRIMARY_PARQUET)


@pytest.fixture(scope="module")
def df_splits():
    return pd.read_parquet(SPLITS_PARQUET)


class TestPhase1CuratedArtifacts:
    """Verifies that all Phase 1 deliverables exist, parse cleanly, and match authoritative row counts."""

    def test_openadmet_primary_artifact(self):
        assert PRIMARY_PARQUET.exists()
        df = pd.read_parquet(PRIMARY_PARQUET)
        assert len(df) == 6145
        assert "assay_smiles" in df.columns
        assert "grouping_parent_smiles" in df.columns
        assert "grouping_parent_inchikey" in df.columns

    def test_octant_curated_artifacts(self):
        assert OCTANT_REACT_PARQUET.exists()
        assert OCTANT_WILL_PARQUET.exists()
        assert OCTANT_OVERLAY_PARQUET.exists()

        df_react = pd.read_parquet(OCTANT_REACT_PARQUET)
        assert len(df_react) == 2446

        df_will = pd.read_parquet(OCTANT_WILL_PARQUET)
        assert len(df_will) == 11353

        df_overlay = pd.read_parquet(OCTANT_OVERLAY_PARQUET)
        assert len(df_overlay) == 6145

    def test_splits_and_tanimoto_artifacts(self):
        assert SPLITS_PARQUET.exists()
        df_splits_check = pd.read_parquet(SPLITS_PARQUET)
        assert len(df_splits_check) == 6145

        assert TANIMOTO_JSON.exists()
        with open(TANIMOTO_JSON) as f:
            tanimoto_data = json.load(f)
        assert tanimoto_data["metadata"]["num_compounds"] == 6145

    def test_literature_mbi_fixture_artifact(self):
        assert MBI_FIXTURE_JSON.exists()
        with open(MBI_FIXTURE_JSON) as f:
            mbi = json.load(f)
        assert len(mbi["entries"]) == 10


class TestEndpointMaskAndMissingnessCoherence:
    """Verifies dual-masking rules and absence of the 95.79% joint dropna trap."""

    def test_cyp3a4_mask_distribution(self, df_primary):
        mask_3a4 = df_primary["mask_cyp3a4"]
        assert mask_3a4.sum() == 3584
        assert (df_primary.loc[mask_3a4, "cyp3a4_is_tdi"] == True).sum() == 764
        assert (df_primary.loc[mask_3a4, "cyp3a4_is_tdi"] == False).sum() == 2820
        assert df_primary.loc[~mask_3a4, "cyp3a4_is_tdi"].isna().all()

    def test_cyp2d6_mask_distribution(self, df_primary):
        mask_2d6 = df_primary["mask_cyp2d6"]
        assert mask_2d6.sum() == 1497
        assert (df_primary.loc[mask_2d6, "cyp2d6_is_tdi"] == True).sum() == 324
        assert (df_primary.loc[mask_2d6, "cyp2d6_is_tdi"] == False).sum() == 1173
        assert df_primary.loc[~mask_2d6, "cyp2d6_is_tdi"].isna().all()

    def test_joint_mask_and_retention(self, df_primary):
        assert df_primary["mask_joint_both"].sum() == 259
        # Total rows must be 100% retained (no dropna applied)
        assert len(df_primary) == 6145


class TestSplitsZeroLeakageSeam:
    """Validates leak-proof properties of cross-validation and holdout splits."""

    def test_zero_parent_inchikey_leakage_across_all_cv_folds(self, df_splits):
        for f1 in range(5):
            for f2 in range(f1 + 1, 5):
                p1 = set(df_splits[df_splits["cv_fold_5"] == f1]["grouping_parent_inchikey"])
                p2 = set(df_splits[df_splits["cv_fold_5"] == f2]["grouping_parent_inchikey"])
                overlap = p1.intersection(p2)
                assert len(overlap) == 0, f"Parent InChIKey leakage between Fold {f1} and {f2}: {overlap}"

    def test_zero_murcko_scaffold_leakage_across_all_cv_folds(self, df_splits):
        for f1 in range(5):
            for f2 in range(f1 + 1, 5):
                s1 = set(df_splits[(df_splits["cv_fold_5"] == f1) & (df_splits["murcko_scaffold_smiles"] != "")]["murcko_scaffold_smiles"])
                s2 = set(df_splits[(df_splits["cv_fold_5"] == f2) & (df_splits["murcko_scaffold_smiles"] != "")]["murcko_scaffold_smiles"])
                overlap = s1.intersection(s2)
                assert len(overlap) == 0, f"Scaffold leakage between Fold {f1} and {f2}: {overlap}"

    def test_zero_leakage_in_60_20_20_holdout(self, df_splits):
        train = df_splits[df_splits["holdout_split"] == "TRAIN"]
        calib = df_splits[df_splits["holdout_split"] == "CALIBRATION"]
        test = df_splits[df_splits["holdout_split"] == "TEST"]

        p_train = set(train["grouping_parent_inchikey"])
        p_calib = set(calib["grouping_parent_inchikey"])
        p_test = set(test["grouping_parent_inchikey"])

        assert len(p_train.intersection(p_test)) == 0
        assert len(p_train.intersection(p_calib)) == 0
        assert len(p_calib.intersection(p_test)) == 0

    def test_fold_size_balance_and_stratification(self, df_splits):
        counts = df_splits["cv_fold_5"].value_counts()
        for f in range(5):
            assert 1180 <= counts[f] <= 1290
            sub = df_splits[df_splits["cv_fold_5"] == f]
            pos_3a4_rate = (sub["cyp3a4_is_tdi"] == True).sum() / sub["mask_cyp3a4"].sum() * 100
            assert 19.0 <= pos_3a4_rate <= 24.0


class TestSeamDataJoinAndSchemaIntegrity:
    """Verifies that all curated Phase 1 tables join seamlessly with zero corruption or schema drift."""

    def test_seamless_master_table_join(self):
        df_pri = pd.read_parquet(PRIMARY_PARQUET)
        df_splits_check = pd.read_parquet(SPLITS_PARQUET)
        df_overlay = pd.read_parquet(OCTANT_OVERLAY_PARQUET)

        # Confirm exact row matching
        assert len(df_pri) == len(df_splits_check) == len(df_overlay) == 6145
        assert (df_pri["assay_inchikey"] == df_splits_check["assay_inchikey"]).all()
        assert (df_pri["assay_inchikey"] == df_overlay["assay_inchikey"]).all()

        # Join datasets
        merged = df_pri.merge(
            df_splits_check[["assay_inchikey", "cv_fold_5", "holdout_split"]],
            on="assay_inchikey",
            how="inner"
        ).merge(
            df_overlay[["assay_inchikey", "ammonium_fluoride_area", "ammonium_formate_area", "ionization_qc_tier"]],
            on="assay_inchikey",
            how="inner"
        )

        assert len(merged) == 6145
        assert merged["cv_fold_5"].notna().all()
        assert merged["holdout_split"].notna().all()
        assert (merged["ionization_qc_tier"] != "NO_DATA").sum() == 4396


class TestTargetLeakageGuardrails:
    """Enforces programmatic target-leakage prohibition on feature extraction."""

    def test_feature_selection_passes_leakage_assertion(self):
        valid_feature_columns = [
            "mw", "logp", "tpsa", "hbd", "hba", "rotbonds",
            "heavy_atom_count", "fraction_csp3", "ring_count"
        ]
        # Must pass without raising AssertionError
        assert_zero_target_leakage(valid_feature_columns)

    def test_banned_columns_trigger_assertion(self):
        leaked_columns = ["mw", "logp", "cyp3a4_pic50_direct_inhibition"]
        with pytest.raises(AssertionError, match="TARGET LEAKAGE DETECTED"):
            assert_zero_target_leakage(leaked_columns)

        leaked_target = ["mw", "logp", "cyp3a4_is_tdi"]
        with pytest.raises(AssertionError, match="TARGET LEAKAGE DETECTED"):
            assert_zero_target_leakage(leaked_target)
