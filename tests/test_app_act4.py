"""
Unit tests for EC-3-2-04: Master Marimo App Act 4 (Medicinal Chemistry Steering & MMPs).
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


def test_act4_mmp_and_oof_narrative():
    content = APP_PATH.read_text(encoding="utf-8")

    # Verify key Act 4 narrative concepts
    assert "Act 4: Medicinal Chemistry Steering" in content
    assert "Matched Molecular Pairs (MMPs)" in content
    assert "34 unique matched molecular pairs" in content
    assert "Out-of-Fold Model Error Diagnosis" in content
    assert "False Negative (Dangerous Escape)" in content
    assert "False Positive (False Alarm)" in content
    assert "Resorcinol" in content


def test_app_import_and_act4_objects():
    t0 = time.perf_counter()
    import app as marimo_app
    load_dt = time.perf_counter() - t0

    print(f"\napp.py import latency with Acts 1 to 4: {load_dt:.3f}s")
    assert hasattr(marimo_app, "app")
    assert marimo_app.app is not None
    assert load_dt < 1.0, f"Import took {load_dt:.2f}s (> 1.0s SLA)"
