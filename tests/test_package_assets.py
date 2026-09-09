"""
Unit tests for EC-2-4-01: Packaged curated dataset and embedded zero-network fallback assets.
"""

import sys
import time
from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from models.embedded_assets import (
    load_fallback_dataset,
    load_literature_mbi_reference_set,
    load_mmp_transformations,
    load_oof_error_cases,
    load_ncbi_pubmed_cache,
    load_curated_dataset,
    PARQUET_PRIMARY_PATH,
    PARQUET_EXPECTED_SHA256,
)

PRIMARY_PARQUET = BASE_DIR / "data" / "packaged" / "cyp_tdi_curated.parquet"
FALLBACK_PARQUET = BASE_DIR / "data" / "packaged" / "fallback_sample.parquet"


def test_primary_parquet_size_and_cold_load_latency():
    assert PRIMARY_PARQUET.exists(), f"Missing {PRIMARY_PARQUET}"
    file_size_mb = PRIMARY_PARQUET.stat().st_size / (1024 * 1024)
    assert file_size_mb <= 12.0, f"File size {file_size_mb:.2f} MB exceeds 12 MB limit!"

    t0 = time.perf_counter()
    df = pd.read_parquet(PRIMARY_PARQUET)
    latency_ms = (time.perf_counter() - t0) * 1000
    assert latency_ms < 150.0, f"Cold load latency {latency_ms:.1f}ms exceeds 150ms SLA!"
    assert len(df) == 6145


def test_schema_integrity_and_endpoint_nulls():
    df = pd.read_parquet(PRIMARY_PARQUET)

    # All expected columns present
    required_cols = [
        "molecule_name", "assay_smiles", "assay_inchikey",
        "mask_cyp3a4", "mask_cyp2d6", "cyp3a4_is_tdi", "cyp2d6_is_tdi",
        "pred_cyp3a4_prob_baseline_2d", "pred_cyp3a4_prob_augmented_physics",
        "pred_cyp2d6_prob_baseline_2d", "txconformal_pvalue_cyp3a4",
        "txconformal_selected_alpha_0_10", "is_mmp_cliff", "mmp_id",
        "mw", "logp", "tpsa"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column {col}"

    # Verify 3A4 labeled predictions
    assert df["mask_cyp3a4"].sum() == 3584
    assert df.loc[df["mask_cyp3a4"], "pred_cyp3a4_prob_baseline_2d"].isna().sum() == 0
    assert df.loc[df["mask_cyp3a4"], "pred_cyp3a4_prob_augmented_physics"].isna().sum() == 0
    # No hallucinated predictions outside mask
    assert df.loc[~df["mask_cyp3a4"], "pred_cyp3a4_prob_baseline_2d"].isna().all()

    # Verify 2D6 labeled predictions
    assert df["mask_cyp2d6"].sum() == 1497
    assert df.loc[df["mask_cyp2d6"], "pred_cyp2d6_prob_baseline_2d"].isna().sum() == 0
    assert df.loc[~df["mask_cyp2d6"], "pred_cyp2d6_prob_baseline_2d"].isna().all()


def test_txconformal_and_mmp_columns():
    df = pd.read_parquet(PRIMARY_PARQUET)

    # TxConformal evaluated on TEST holdout for 3A4
    test_3a4_mask = df["mask_cyp3a4"] & (df["holdout_split"] == "TEST")
    assert test_3a4_mask.sum() == 703
    assert df.loc[test_3a4_mask, "txconformal_pvalue_cyp3a4"].isna().sum() == 0
    assert df["txconformal_selected_alpha_0_10"].sum() > 0

    # MMP annotations
    assert df["is_mmp_cliff"].sum() == 56
    mmp_rows = df[df["is_mmp_cliff"]]
    assert mmp_rows["mmp_id"].str.startswith("MMP-").all()
    assert set(mmp_rows["mmp_role"].unique()) == {"INACTIVE", "LIABILITY"}


def test_fallback_sample_parquet():
    assert FALLBACK_PARQUET.exists(), f"Missing {FALLBACK_PARQUET}"
    df_fb = pd.read_parquet(FALLBACK_PARQUET)
    assert len(df_fb) == 100
    assert df_fb["mask_cyp3a4"].sum() >= 40
    assert df_fb["mask_cyp2d6"].sum() >= 25
    assert df_fb["is_mmp_cliff"].sum() >= 10


def test_embedded_assets_loaders_and_resilience(monkeypatch):
    # In-memory decoding tests
    df_fb = load_fallback_dataset()
    assert len(df_fb) == 100

    lit = load_literature_mbi_reference_set()
    assert len(lit["entries"]) == 10

    mmps = load_mmp_transformations()
    assert len(mmps["pairs"]) == 34

    oof = load_oof_error_cases()
    assert len(oof["cases"]) == 4

    ncbi_c = load_ncbi_pubmed_cache()
    assert len(ncbi_c) >= 10

    # Test primary loader
    df_main = load_curated_dataset()
    assert len(df_main) == 6145

    # Test fallback resilience under simulated missing file
    import models.embedded_assets as ea
    monkeypatch.setattr(ea, "PARQUET_PRIMARY_PATH", Path("/tmp/nonexistent_dataset_12345.parquet"))
    df_fallback_loaded = ea.load_curated_dataset()
    assert len(df_fallback_loaded) == 100
