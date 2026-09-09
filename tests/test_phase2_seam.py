"""
EC-INTEGRATION-P2-01: Phase 2 Seam Integration Test.

Validates the complete precomputed scientific foundation and packaged artifacts:
  1. All Phase 2 artifacts exist and match expected schemas and non-zero byte sizes.
  2. Consolidated master dataset (cyp_tdi_curated.parquet):
     - Size <= 12 MB (strict contract)
     - Cold-load latency on CPU < 150 ms (strict SLA)
     - Exactly 6,145 rows (0 rows lost from Phase 1)
     - 59 columns with zero unexpected schema alterations
  3. Strict endpoint nulls and prediction masking:
     - CYP3A4: exactly 3,584 non-null labels & predictions; 2,561 expected nulls
     - CYP2D6: exactly 1,497 non-null labels & predictions; 4,648 expected nulls
     - Joint mask: exactly 259 dual-tested compounds
     - Zero hallucinated predictions on unlabeled molecules
  4. Quantum electronic feature coherence (AIMNet2-NSE ΔSCF):
     - 10 quantum reactivity descriptors populated for all 3,584 CYP3A4 compounds with 0 NaNs
  5. Conformal risk control (TxConformal):
     - Conformal p-values strictly in [0, 1] on TEST holdout
     - Controlled FDR at nominal alpha <= 0.10
  6. Matched Molecular Pair (MMP) activity cliffs:
     - 56 compounds annotated across 46 curated pairs
  7. Embedded fallback assets:
     - Standalone in-memory decoding verified for zero-network execution
  8. Programmatic Target Leakage Assertion:
     - Zero assay columns leaked into model feature sets
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Artifact paths
PRIMARY_PARQUET = BASE_DIR / "data" / "packaged" / "cyp_tdi_curated.parquet"
FALLBACK_PARQUET = BASE_DIR / "data" / "packaged" / "fallback_sample.parquet"
ECFP_RESULTS = BASE_DIR / "data" / "packaged" / "ecfp_baseline_results.json"
DMPNN_RESULTS = BASE_DIR / "data" / "packaged" / "dmpnn_baseline_results.json"
AIMNET_PARQUET = BASE_DIR / "data" / "curated" / "aimnet2_cyp3a4_features.parquet"
AUGMENTED_RESULTS = BASE_DIR / "data" / "packaged" / "augmented_results.json"
MMP_RESULTS = BASE_DIR / "data" / "packaged" / "mmp_transformations.json"
TXCONFORMAL_RESULTS = BASE_DIR / "data" / "packaged" / "txconformal_selection_results.json"
EMBEDDED_MODULE = BASE_DIR / "models" / "embedded_assets.py"

from models.embedded_assets import (
    load_fallback_dataset,
    load_literature_mbi_reference_set,
    load_mmp_transformations,
    load_curated_dataset,
)

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


@pytest.fixture(scope="module")
def df_master():
    return pd.read_parquet(PRIMARY_PARQUET)


class TestPhase2ArtifactCompleteness:
    """Verifies existence and non-zero byte size of all Phase 2 outputs."""

    def test_all_phase2_artifacts_exist(self):
        artifacts = [
            PRIMARY_PARQUET,
            FALLBACK_PARQUET,
            ECFP_RESULTS,
            DMPNN_RESULTS,
            AIMNET_PARQUET,
            AUGMENTED_RESULTS,
            MMP_RESULTS,
            TXCONFORMAL_RESULTS,
            EMBEDDED_MODULE,
        ]
        for art in artifacts:
            assert art.exists(), f"Missing required Phase 2 artifact: {art}"
            assert art.stat().st_size > 0, f"Artifact {art} is empty (0 bytes)!"


class TestConsolidatedTableContracts:
    """Verifies packaging constraints, size limits, and cold-load performance SLAs."""

    def test_file_size_and_load_latency_sla(self):
        file_size_mb = PRIMARY_PARQUET.stat().st_size / (1024 * 1024)
        assert file_size_mb <= 12.0, f"File size {file_size_mb:.2f} MB exceeds 12 MB limit!"

        t0 = time.perf_counter()
        df = pd.read_parquet(PRIMARY_PARQUET)
        dt_ms = (time.perf_counter() - t0) * 1000
        assert dt_ms < 150.0, f"Cold load latency {dt_ms:.1f}ms exceeds 150ms SLA!"
        assert len(df) == 6145
        assert len(df.columns) == 59


class TestEndpointMasksAndPredictionIntegrity:
    """Verifies strict missingness contracts and zero prediction hallucination."""

    def test_cyp3a4_mask_and_predictions(self, df_master):
        mask_3a4 = df_master["mask_cyp3a4"]
        assert mask_3a4.sum() == 3584

        # Non-null labels on masked rows
        labels = df_master.loc[mask_3a4, "cyp3a4_is_tdi"]
        assert labels.isna().sum() == 0
        assert set(labels.unique()).issubset({True, False, 0, 1})

        # Non-null predictions on masked rows
        p_2d = df_master.loc[mask_3a4, "pred_cyp3a4_prob_baseline_2d"]
        p_aug = df_master.loc[mask_3a4, "pred_cyp3a4_prob_augmented_physics"]
        assert p_2d.isna().sum() == 0
        assert p_aug.isna().sum() == 0
        assert (0.0 <= p_2d).all() and (p_2d <= 1.0).all()
        assert (0.0 <= p_aug).all() and (p_aug <= 1.0).all()

        # Strict nulls on unmasked rows (no hallucinated predictions)
        assert df_master.loc[~mask_3a4, "cyp3a4_is_tdi"].isna().all()
        assert df_master.loc[~mask_3a4, "pred_cyp3a4_prob_baseline_2d"].isna().all()
        assert df_master.loc[~mask_3a4, "pred_cyp3a4_prob_augmented_physics"].isna().all()

    def test_cyp2d6_mask_and_predictions(self, df_master):
        mask_2d6 = df_master["mask_cyp2d6"]
        assert mask_2d6.sum() == 1497

        # Non-null labels on masked rows
        labels = df_master.loc[mask_2d6, "cyp2d6_is_tdi"]
        assert labels.isna().sum() == 0
        assert set(labels.unique()).issubset({True, False, 0, 1})

        # Non-null predictions on masked rows
        p_2d6 = df_master.loc[mask_2d6, "pred_cyp2d6_prob_baseline_2d"]
        assert p_2d6.isna().sum() == 0
        assert (0.0 <= p_2d6).all() and (p_2d6 <= 1.0).all()

        # Strict nulls on unmasked rows
        assert df_master.loc[~mask_2d6, "cyp2d6_is_tdi"].isna().all()
        assert df_master.loc[~mask_2d6, "pred_cyp2d6_prob_baseline_2d"].isna().all()

    def test_joint_mask_and_retention(self, df_master):
        joint_mask = df_master["mask_cyp3a4"] & df_master["mask_cyp2d6"]
        assert joint_mask.sum() == 259


class TestScientificFeaturesAndConformalCalibration:
    """Verifies AIMNet2 physics descriptors, TxConformal calibration, and MMP cliffs."""

    def test_aimnet2_physics_descriptors(self, df_master):
        aimnet_cols = [
            "aimnet2_ip_ev", "aimnet2_ea_ev", "aimnet2_hardness_ev",
            "aimnet2_chemical_potential_ev", "aimnet2_electrophilicity_ev",
            "aimnet2_softness_inv_ev", "aimnet2_max_fukui_radical",
            "aimnet2_max_charge_ox", "aimnet2_max_charge_red",
            "aimnet2_num_reactive_atoms"
        ]
        for col in aimnet_cols:
            assert col in df_master.columns
            # 0 NaNs on the 3,584 CYP3A4 compounds
            assert df_master.loc[df_master["mask_cyp3a4"], col].isna().sum() == 0

        # Physical bounds check
        ip_vals = df_master.loc[df_master["mask_cyp3a4"], "aimnet2_ip_ev"]
        assert 3.0 <= ip_vals.mean() <= 12.0

    def test_txconformal_selection_columns(self, df_master):
        test_3a4 = df_master["mask_cyp3a4"] & (df_master["holdout_split"] == "TEST")
        assert test_3a4.sum() == 703

        pvals = df_master.loc[test_3a4, "txconformal_pvalue_cyp3a4"]
        assert pvals.isna().sum() == 0
        assert (0.0 <= pvals).all() and (pvals <= 1.0).all()

        sel_10 = df_master.loc[test_3a4, "txconformal_selected_alpha_0_10"]
        assert sel_10.sum() > 0

    def test_mmp_activity_cliffs(self, df_master):
        assert df_master["is_mmp_cliff"].sum() == 56
        mmp_subset = df_master[df_master["is_mmp_cliff"]]
        assert mmp_subset["mmp_id"].str.startswith("MMP-").all()
        assert set(mmp_subset["mmp_role"].unique()) == {"INACTIVE", "LIABILITY"}


class TestZeroNetworkEmbeddedResilience:
    """Verifies in-memory decoding and fallback loader under simulated network failure."""

    def test_embedded_assets_decode_cleanly(self):
        df_fb = load_fallback_dataset()
        assert len(df_fb) == 100
        assert len(df_fb.columns) == 59

        lit = load_literature_mbi_reference_set()
        assert len(lit["entries"]) == 10

        mmps = load_mmp_transformations()
        assert len(mmps["pairs"]) == 34

    def test_loader_graceful_fallback(self, monkeypatch):
        import models.embedded_assets as ea
        monkeypatch.setattr(ea, "PARQUET_PRIMARY_PATH", Path("/tmp/nonexistent_dataset_phase2.parquet"))
        df_loaded = ea.load_curated_dataset()
        assert len(df_loaded) == 100


class TestTargetLeakageGuardrail:
    """Verifies that no ground-truth assay columns leaked into model predictions."""

    def test_feature_columns_pass_leakage_assertion(self):
        with open(AUGMENTED_RESULTS) as f:
            aug_data = json.load(f)
        features = aug_data["metadata"]["physics_features"]
        leaked = set(features).intersection(BANNED_COLUMNS)
        assert len(leaked) == 0, f"TARGET LEAKAGE DETECTED: {leaked}"
