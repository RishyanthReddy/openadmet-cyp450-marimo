"""
Unit tests for EC-2-1-02: Chemprop v2 D-MPNN baseline modeling on Random vs Grouped splits.
"""

import json
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_JSON = BASE_DIR / "data" / "packaged" / "dmpnn_baseline_results.json"


@pytest.fixture(scope="module")
def dmpnn_data():
    assert RESULTS_JSON.exists(), f"Missing {RESULTS_JSON}"
    with open(RESULTS_JSON) as f:
        return json.load(f)


def test_metadata_integrity(dmpnn_data):
    meta = dmpnn_data["metadata"]
    assert meta["target"] == "CYP3A4_is_TDI"
    assert meta["n_samples"] == 3584
    assert meta["n_positives"] == 764
    assert "Chemprop v2 D-MPNN" in meta["model_architecture"]
    assert meta["epochs"] == 20
    assert meta["batch_size"] == 64


def test_dmpnn_metrics_and_folds(dmpnn_data):
    dmpnn = dmpnn_data["dmpnn"]
    assert "random_5fold" in dmpnn
    assert "grouped_5fold" in dmpnn
    assert "delta_random_minus_grouped" in dmpnn

    # Check Random 5-fold OOF
    rand_oof = dmpnn["random_5fold"]["overall_oof"]
    assert 0.65 <= rand_oof["roc_auc"] <= 0.78
    assert 0.28 <= rand_oof["pr_auc"] <= 0.45
    assert len(dmpnn["random_5fold"]["per_fold"]) == 5

    # Check Grouped 5-fold OOF
    grp_oof = dmpnn["grouped_5fold"]["overall_oof"]
    assert 0.65 <= grp_oof["roc_auc"] <= 0.78
    assert 0.28 <= grp_oof["pr_auc"] <= 0.45
    assert len(dmpnn["grouped_5fold"]["per_fold"]) == 5

    # Check Bootstrap 95% CIs
    for oof in [rand_oof, grp_oof]:
        ci = oof["bootstrap_ci_95"]
        assert "roc_auc" in ci
        assert "pr_auc" in ci
        assert "mcc" in ci
        assert ci["roc_auc"]["ci_lower"] < ci["roc_auc"]["ci_upper"]
        assert ci["pr_auc"]["ci_lower"] < ci["pr_auc"]["ci_upper"]


def test_generalization_gap_delta(dmpnn_data):
    delta = dmpnn_data["dmpnn"]["delta_random_minus_grouped"]
    # D-MPNN graph representation shows consistent generalization without scaffold memorization
    assert abs(delta["roc_auc_delta"]) < 0.05
    assert abs(delta["pr_auc_delta"]) < 0.05
