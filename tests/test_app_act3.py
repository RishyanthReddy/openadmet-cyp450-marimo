"""
Unit tests for EC-3-2-03: Master Marimo App Act 3 (Quantum Reactivity & 3D Enzymology).
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


def test_act3_quantum_and_enzymology_narrative():
    content = APP_PATH.read_text(encoding="utf-8")

    # Verify key Act 3 biophysical concepts
    assert "Act 3: Physics-Grounded Quantum Reactivity & Active-Site Enzymology" in content
    assert "Compound I" in content
    assert "Vertical Ionization Potential" in content
    assert "Radical Fukui Index" in content
    assert "Chemical Hardness" in content

    # Verify quantitative empirical benchmark figures
    assert "0.4652" in content
    assert "0.4753" in content
    assert "+0.0101" in content or "0.0101" in content
    assert "0.1573" in content
    assert "0.1542" in content

    # Verify transparent scientific null discussion on ROC-AUC
    assert "ROC-AUC across 3,584 compounds remains essentially unchanged" in content

    # Verify 3D crystallographic docking validation
    assert "AutoDock Vina v1.2.7" in content
    assert "2V0M" in content
    assert "1TQN" in content
    assert "2.23 Å" in content


def test_app_import_and_act3_objects():
    t0 = time.perf_counter()
    import app as marimo_app
    load_dt = time.perf_counter() - t0

    print(f"\napp.py import latency with Acts 1, 2 & 3: {load_dt:.3f}s")
    assert hasattr(marimo_app, "app")
    assert marimo_app.app is not None
    assert load_dt < 1.0, f"Import took {load_dt:.2f}s (> 1.0s SLA)"
