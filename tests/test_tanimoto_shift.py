"""
Unit tests for EC-1-3-02: Nearest-neighbor Tanimoto distributional shift.
"""

import json
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
SUMMARY_JSON = BASE_DIR / "data" / "curated" / "tanimoto_shift_summary.json"


@pytest.fixture(scope="module")
def summary_data():
    assert SUMMARY_JSON.exists(), f"Missing {SUMMARY_JSON}"
    with open(SUMMARY_JSON) as f:
        return json.load(f)


def test_metadata_integrity(summary_data):
    meta = summary_data["metadata"]
    assert meta["num_compounds"] == 6145
    assert meta["fingerprint"] == "Morgan"
    assert meta["radius"] == 2
    assert meta["n_bits"] == 2048


def test_cv_folds_tanimoto_bounds(summary_data):
    cv = summary_data["cv_folds_scaffold"]
    for f in range(5):
        key = f"fold_{f}"
        assert key in cv
        stats = cv[key]
        assert 0.40 <= stats["mean"] <= 0.55
        assert 0.38 <= stats["median"] <= 0.52
        assert stats["p90"] <= 0.70
        assert stats["fraction_novel_chemotypes_lt_0_4"] >= 0.25


def test_holdout_partitions_metrics(summary_data):
    holdout = summary_data["holdout_scaffold"]
    assert "test_vs_train" in holdout
    assert "calibration_vs_train" in holdout

    test_stats = holdout["test_vs_train"]
    assert 0.38 <= test_stats["mean"] <= 0.50
    assert 0.35 <= test_stats["median"] <= 0.48
    assert test_stats["p90"] <= 0.65


def test_random_comparison_shift(summary_data):
    rnd = summary_data["random_baseline_comparison"]
    scaff_mean = summary_data["cv_folds_scaffold"]["overall_cv_mean"]
    # Random split has higher P90 similarity due to shared scaffolds across folds
    assert rnd["p90"] > scaff_mean["p90"]
