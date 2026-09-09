import subprocess
import sys
import time
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

APP_PATH = BASE_DIR / "app.py"


def test_app_file_exists_and_non_empty():
    assert APP_PATH.exists(), f"Missing {APP_PATH}"
    assert APP_PATH.stat().st_size > 1000, f"app.py too small: {APP_PATH.stat().st_size} bytes"


def test_marimo_check_app():
    """Validates that app.py has no cyclical dependencies or syntax errors."""
    res = subprocess.run(
        [sys.executable, "-m", "marimo", "check", str(APP_PATH)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"marimo check failed:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"


def test_act1_content_and_reference_mbis():
    content = APP_PATH.read_text(encoding="utf-8")

    # Verify provenance pill
    assert "Data Source:" in content
    assert "Parquet SHA-256 Verified" in content

    # Verify key Act 1 scientific concepts
    assert "Act 1: What TDI Is — and What It Is Not" in content
    assert "Preincubation Shift Assay Reality" in content
    assert "Irreversible MBI Mechanism" in content
    assert "Suicide Inactivation" in content

    # Verify key literature compounds and docking distances from empirical data
    from models.embedded_assets import (
        load_literature_mbi_reference_set,
        load_docking_ablation_results,
    )
    mbi_data = load_literature_mbi_reference_set()
    names = [e["name"] for e in mbi_data["entries"]]
    for expected in ["Raloxifene", "Tienilic acid", "Furafylline", "Bergamottin", "Lapatinib"]:
        assert expected in names, f"Missing {expected} in literature reference set"

    dock_data = load_docking_ablation_results()
    dock_dict = {c["name"]: c["docking_results"]["2V0M"]["min_dist_to_heme_fe_angstrom"] for c in dock_data["docking_evaluations"]}
    assert round(dock_dict["Raloxifene"], 2) == 2.23
    assert round(dock_dict["Tienilic acid"], 2) == 2.19

    # Verify NCBI Entrez verification and PubMed linkage
    assert "NCBI Entrez Verified" in content
    assert "NCBI Verified Title" in content
    assert "NCBI Journal" in content
    assert "https://pubmed.ncbi.nlm.nih.gov/" in content


def test_app_import_and_execution_speed():
    """Verify app.py module can be imported and executed without errors."""
    t0 = time.perf_counter()
    import app as marimo_app
    load_dt = time.perf_counter() - t0

    print(f"\napp.py import latency: {load_dt:.3f}s")
    assert hasattr(marimo_app, "app")
    assert marimo_app.app is not None
    assert load_dt < 1.0, f"app.py import took {load_dt:.2f}s (> 1.0s SLA)"
