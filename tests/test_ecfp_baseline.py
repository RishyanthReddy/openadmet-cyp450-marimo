"""
Unit tests for EC-2-1-01: ECFP4 baseline modeling benchmark on Random vs Grouped splits.
"""

import json
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_JSON = BASE_DIR / "data" / "packaged" / "ecfp_baseline_results.json"


@pytest.fixture(scope="module")
def baseline_data():
    assert RESULTS_JSON.exists(), f"Missing {RESULTS_JSON}"
    with open(RESULTS_JSON) as f:
        return json.load(f)


def test_metadata_integrity(baseline_data):
    meta = baseline_data["metadata"]
    assert meta["target"] == "CYP3A4_is_TDI"
    assert meta["n_samples"] == 3584
    assert meta["n_positives"] == 764
    assert "ECFP4" in meta["feature_type"]


def test_models_presence_and_metrics(baseline_data):
    models = baseline_data["models"]
    assert "logistic_regression" in models
    assert "lightgbm" in models

    for m_name in ["logistic_regression", "lightgbm"]:
        m = models[m_name]
        assert "random_5fold" in m
        assert "grouped_5fold" in m
        assert "delta_random_minus_grouped" in m

        # Check Random CV metrics
        rand_oof = m["random_5fold"]["overall_oof"]
        assert 0.70 <= rand_oof["roc_auc"] <= 0.85
        assert 0.35 <= rand_oof["pr_auc"] <= 0.55
        assert 0.20 <= rand_oof["mcc"] <= 0.45

        # Check Grouped Scaffold CV metrics
        grp_oof = m["grouped_5fold"]["overall_oof"]
        assert 0.68 <= grp_oof["roc_auc"] <= 0.80
        assert 0.30 <= grp_oof["pr_auc"] <= 0.50
        assert 0.18 <= grp_oof["mcc"] <= 0.40

        # Check Bootstrap 95% CIs
        for oof in [rand_oof, grp_oof]:
            ci = oof["bootstrap_ci_95"]
            assert "roc_auc" in ci
            assert "pr_auc" in ci
            assert "mcc" in ci
            assert ci["roc_auc"]["ci_lower"] < ci["roc_auc"]["ci_upper"]
            assert ci["pr_auc"]["ci_lower"] < ci["pr_auc"]["ci_upper"]


def test_empirical_scientific_hypothesis_shift(baseline_data):
    models = baseline_data["models"]
    for m_name in ["logistic_regression", "lightgbm"]:
        delta = models[m_name]["delta_random_minus_grouped"]
        # Random splitting inflates apparent PR-AUC and MCC
        assert delta["pr_auc_delta"] > 0, f"{m_name} PR-AUC delta is non-positive: {delta['pr_auc_delta']}"
        assert delta["mcc_delta"] > 0, f"{m_name} MCC delta is non-positive: {delta['mcc_delta']}"
        assert delta["random_inflates_performance"] is True
