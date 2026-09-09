"""
Unit tests for EC-2-3-01: TxConformal candidate selection engine.
"""

import json
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
RESULTS_JSON = BASE_DIR / "data" / "packaged" / "txconformal_selection_results.json"


@pytest.fixture(scope="module")
def tx_data():
    assert RESULTS_JSON.exists(), f"Missing {RESULTS_JSON}"
    with open(RESULTS_JSON) as f:
        return json.load(f)


def test_metadata_integrity(tx_data):
    meta = tx_data["metadata"]
    assert "TxConformal" in meta["method"]
    assert "Jin, Y., Huang, K., Diamant, N., et al. (2026)" in meta["citation"]
    assert meta["n_calibration"] == 687
    assert meta["n_test"] == 703
    assert meta["monte_carlo_trials"] == 250
    assert meta["screening_pool_size"] == 200


def test_fdr_control_across_alphas(tx_data):
    mc = tx_data["monte_carlo_robustness_summary"]
    for alpha_key in ["alpha_0.05", "alpha_0.10", "alpha_0.15", "alpha_0.20"]:
        assert alpha_key in mc
        entry = mc[alpha_key]
        target_alpha = entry["target_alpha"]
        mean_fdp = entry["mean_fdp"]
        mc_se = entry["mc_se"]
        mc_ci = entry["mc_ci_95"]

        # Assert empirical FDR is controlled below target alpha
        assert mean_fdp <= target_alpha, f"FDR violation for {alpha_key}: {mean_fdp} > {target_alpha}"
        assert entry["fdr_controlled"] is True
        assert entry["empirical_fdp_controlled"] is True
        assert mc_se > 0.0
        assert mc_ci[0] < mc_ci[1]


def test_candidate_sample_validity(tx_data):
    sample = tx_data["test_candidates_sample"]
    assert len(sample) >= 30
    for cand in sample:
        assert cand["molecule_name"].startswith("OCNT-")
        assert 0.0 <= cand["predicted_liability_prob"] <= 1.0
        assert 0.0 <= cand["weighted_pvalue"] <= 1.0
        assert 0.0 <= cand["unweighted_pvalue"] <= 1.0
        # Assert label hiding: candidate prioritization display MUST NOT leak ground truth labels
        assert "is_tdi_ground_truth" not in cand, "Candidate display payload must not leak ground truth labels"
        assert isinstance(cand["selected_at_alpha_0_10"], bool)


def test_conformal_fdr_select_equivalence(tx_data):
    from models.txconformal_selector import conformal_fdr_select, apply_benjamini_hochberg
    sample = tx_data["test_candidates_sample"]
    p_vals = [c["weighted_pvalue"] for c in sample]

    res_10 = conformal_fdr_select(p_vals, 0.10)
    assert res_10["target_alpha"] == 0.10
    assert res_10["total_hypotheses"] == len(p_vals)
    assert res_10["selected_count"] == len(res_10["selected_indices"])

    # Monotonicity test: alpha 0.20 must select >= alpha 0.05
    res_05 = conformal_fdr_select(p_vals, 0.05)
    res_20 = conformal_fdr_select(p_vals, 0.20)
    assert res_20["selected_count"] >= res_05["selected_count"]

    # Equivalence with apply_benjamini_hochberg
    legacy_sel = apply_benjamini_hochberg(p_vals, 0.10)
    assert sorted(res_10["selected_indices"]) == sorted(legacy_sel.tolist())

