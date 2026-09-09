"""
Unit tests for EC-3-2-02: Master Marimo App Act 2 (The Bathtub Audit & Split Comparison).
"""

import subprocess
import sys
import time
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

APP_PATH = BASE_DIR / "app.py"


def test_marimo_check_app():
    """Validates that app.py DAG is clean and free of circularities."""
    res = subprocess.run(
        [sys.executable, "-m", "marimo", "check", str(APP_PATH)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"marimo check failed:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"


def test_act2_narrative_and_scientific_leakage_audit():
    content = APP_PATH.read_text(encoding="utf-8")

    # Verify key Act 2 narrative concepts
    assert "Act 2: The Bathtub Audit" in content
    assert "Bemis-Murcko molecular core scaffold" in content
    assert "Bathtub Effect" in content
    assert "strict zero-leakage" in content

    # Verify quantitative empirical deltas and CIs
    assert "+0.0364" in content
    assert "+0.0394" in content
    assert "0.4217" in content
    assert "0.3853" in content
    assert "Chemprop v2 D-MPNN" in content

    # Verify Tanimoto distribution values
    assert "0.4862" in content
    assert "0.4428" in content
    assert "40.7%" in content


def test_app_import_and_act2_objects():
    t0 = time.perf_counter()
    import app as marimo_app
    load_dt = time.perf_counter() - t0

    print(f"\napp.py import latency with Act 1 & 2: {load_dt:.3f}s")
    assert hasattr(marimo_app, "app")
    assert marimo_app.app is not None
    assert load_dt < 1.0, f"Import took {load_dt:.2f}s (> 1.0s SLA)"
