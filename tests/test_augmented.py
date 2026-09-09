"""
Unit tests for EC-2-2-01: Physics-grounded feature ablation and augmented modeling.
"""

import json
from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
AIMNET_PARQUET = BASE_DIR / "data" / "curated" / "aimnet2_cyp3a4_features.parquet"
RESULTS_JSON = BASE_DIR / "data" / "packaged" / "augmented_results.json"


def test_aimnet2_features_parquet():
    assert AIMNET_PARQUET.exists(), f"Missing {AIMNET_PARQUET}"
    df = pd.read_parquet(AIMNET_PARQUET)
    assert len(df) == 3584
    assert "assay_inchikey" in df.columns
    assert "aimnet2_ip_ev" in df.columns
    assert "aimnet2_ea_ev" in df.columns
    assert "aimnet2_hardness_ev" in df.columns
    assert "aimnet2_electrophilicity_ev" in df.columns
    assert "aimnet2_max_fukui_radical" in df.columns
    assert "aimnet2_max_charge_ox" in df.columns

    # 0 NaNs across all rows
    assert df.isna().sum().sum() == 0

    # Physical validity bounds
    assert 3.0 <= df["aimnet2_ip_ev"].mean() <= 12.0
    assert 0.0 <= df["aimnet2_max_fukui_radical"].min()


def test_augmented_results_structure():
    assert RESULTS_JSON.exists(), f"Missing {RESULTS_JSON}"
    with open(RESULTS_JSON) as f:
        data = json.load(f)

    meta = data["metadata"]
    assert meta["target"] == "CYP3A4_is_TDI"
    assert meta["n_samples"] == 3584
    assert len(meta["physics_features"]) == 10

    assert "baseline_2d" in data
    assert "augmented_aimnet2" in data
    assert "falsifiable_delta" in data


def test_falsifiable_physics_lift():
    with open(RESULTS_JSON) as f:
        data = json.load(f)

    delta = data["falsifiable_delta"]
    assert delta["physics_improves_generalization"] is True
    # Augmented model improves PR-AUC and MCC over 2D baseline
    assert delta["pr_auc_delta"] > 0, f"PR-AUC delta non-positive: {delta['pr_auc_delta']}"
    assert delta["mcc_delta"] > 0, f"MCC delta non-positive: {delta['mcc_delta']}"
    assert delta["brier_score_delta"] < 0, f"Brier score did not improve: {delta['brier_score_delta']}"
