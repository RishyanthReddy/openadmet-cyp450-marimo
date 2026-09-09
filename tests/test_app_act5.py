"""
Unit tests for EC-3-2-05: Master Marimo App Act 5 (TxConformal Selection & DOME Checklist).
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


def test_act5_txconformal_and_dome_narrative():
    content = APP_PATH.read_text(encoding="utf-8")

    # Verify key Act 5 narrative concepts
    assert "Act 5: TxConformal Candidate Prioritization" in content
    assert "TxConformal" in content
    assert "False Discovery Rate (FDR) control" in content
    assert "DOME Recommendations Compliance" in content
    assert "Honest Scientific Limitations" in content
    assert "Binary TDI vs. Kinetic" in content
    assert "In Vitro Microsomes vs. Whole-Body In Vivo Clearance" in content

    # Verify primary data citations
    assert "OpenADMET Challenge" in content
    assert "Octant Bio" in content
    assert "AIMNet2-NSE" in content
    assert "2V0M" in content
    assert "AutoDock Vina v1.2.7" in content


def test_app_import_and_complete_5acts():
    t0 = time.perf_counter()
    import app as marimo_app
    load_dt = time.perf_counter() - t0

    print(f"\napp.py complete 5-act import latency: {load_dt:.3f}s")
    assert hasattr(marimo_app, "app")
    assert marimo_app.app is not None
    assert load_dt < 1.0, f"Import took {load_dt:.2f}s (> 1.0s SLA)"
