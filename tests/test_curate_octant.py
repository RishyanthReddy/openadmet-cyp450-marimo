"""
Unit tests for EC-1-2-01: Octant auxiliary dataset curation and QC overlay.
"""

from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_CURATED = BASE_DIR / "data" / "curated"

REACT_PATH = DATA_CURATED / "octant_reactivity_curated.parquet"
WILL_PATH = DATA_CURATED / "octant_willitfly_curated.parquet"
OVERLAY_PATH = DATA_CURATED / "octant_openadmet_qc_overlay.parquet"


def test_octant_curated_files_exist():
    assert REACT_PATH.exists(), f"Missing {REACT_PATH}"
    assert WILL_PATH.exists(), f"Missing {WILL_PATH}"
    assert OVERLAY_PATH.exists(), f"Missing {OVERLAY_PATH}"


def test_reactivity_schema_and_enzymes():
    df = pd.read_parquet(REACT_PATH)
    assert len(df) == 2446
    assert df["ocnt_batch"].nunique() == 1223
    assert set(df["enzyme"].unique()) == {"CYP3A4", "CYP2J2"}
    assert df["pct_remaining"].notna().all()
    assert df["inchikey"].notna().all()


def test_willitfly_schema_and_areas():
    df = pd.read_parquet(WILL_PATH)
    assert len(df) == 11353
    assert "ammonium_fluoride_area" in df.columns
    assert "ammonium_formate_area" in df.columns
    assert df["inchikey"].notna().all()
    assert (df["ammonium_fluoride_area"] >= 0).all()


def test_qc_overlay_alignment_and_counts():
    df = pd.read_parquet(OVERLAY_PATH)
    assert len(df) == 6145

    # Check verified overlap counts
    has_will = df["ammonium_fluoride_area"].notna().sum()
    has_inhib_rec = df["octant_inhib_activity"].notna().sum()
    has_inhib_pic50 = df["octant_direct_pic50"].notna().sum()
    has_react_3a4 = df["octant_cyp3a4_pct_remaining"].notna().sum()

    assert has_will == 4396
    assert has_inhib_rec == 1250
    assert has_inhib_pic50 == 1075
    assert has_react_3a4 == 1150

    # Verify ionization QC tiers
    assert set(df["ionization_qc_tier"].unique()).issubset({
        "HIGH_IONIZATION", "MODERATE_IONIZATION", "LOW_IONIZATION", "NO_DATA"
    })
    assert (df["ionization_qc_tier"] != "NO_DATA").sum() == 4396


def test_target_leakage_prohibition():
    df = pd.read_parquet(OVERLAY_PATH)
    # The overlay must never contain ground truth TDI labels
    assert "CYP3A4_is_TDI" not in df.columns
    assert "cyp3a4_is_tdi" not in df.columns
    assert "cyp2d6_is_tdi" not in df.columns
