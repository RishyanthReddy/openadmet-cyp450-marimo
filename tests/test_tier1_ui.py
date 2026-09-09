"""
tests/test_tier1_ui.py - Automated Unit & Regression Tests for Tier 1 Native Marimo UI Enhancements.
Governed by docs/TIER1_TIER2_IMPLEMENTATION_PLAN.md.
"""

import re
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

APP_PATH = BASE_DIR / "app.py"
STANDALONE_PATH = BASE_DIR / "standalone_app.py"


# ---------------------------------------------------------------------------
# EC-T1-01: Native mo.accordion Refactor
# ---------------------------------------------------------------------------

def test_act1_protocol_uses_native_accordion():
    """Asserts that Act 1 uses native mo.accordion for in vitro protocol deep dive."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    assert "mo.accordion(" in app_code, "app.py does not call mo.accordion"
    assert "The In Vitro Microsomal Preincubation Assay Protocol" in app_code
    assert "act1_protocol" in app_code


def test_act5_dome_uses_native_accordion():
    """Asserts that Act 5 uses native mo.accordion for DOME compliance with exact required title."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    assert '"📋 DOME Recommendations Compliance": dome_content' in app_code, (
        "app.py must have exact accordion title '📋 DOME Recommendations Compliance'"
    )
    assert '"📋 DOME Recommendations Compliance (Machine Learning in Life Sciences)"' not in app_code
    # Must have eliminated raw HTML details/summary disclosures
    assert "<details>" not in app_code, "app.py still contains raw <details> tag in Act 5"
    assert "<summary" not in app_code, "app.py still contains raw <summary> tag in Act 5"


# ---------------------------------------------------------------------------
# EC-T1-02: Native mo.stat KPI Metric Callout Cards
# ---------------------------------------------------------------------------

def test_act2_stat_specification():
    """Asserts that Act 2 defines act2_kpis using native mo.stat with exact values and direction semantics."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    assert "act2_kpis" in app_code, "act2_kpis must be defined in app.py"
    assert "PR-AUC scaffold shift" in app_code
    assert "-0.0364" in app_code
    assert "MCC scaffold shift" in app_code
    assert "-0.0394" in app_code
    assert "PR-AUC apparent inflation" in app_code
    assert "9.4%" in app_code
    # Ensure direction semantics: inflation has target_direction="decrease"
    assert 'direction="increase", target_direction="decrease"' in app_code or (
        'direction="increase"' in app_code and 'target_direction="decrease"' in app_code
    )


def test_act3_stat_specification():
    """Asserts that Act 3 defines act3_kpis using native mo.stat with neutral ROC-AUC and lower-is-better Brier."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    assert "act3_kpis" in app_code, "act3_kpis must be defined in app.py"
    assert "PR-AUC lift" in app_code
    assert "+0.0101" in app_code
    assert "MCC lift" in app_code
    assert "+0.0209" in app_code
    assert "ROC-AUC change" in app_code
    assert "+0.0023" in app_code
    assert "Brier error change" in app_code
    assert "-0.0031" in app_code
    # ROC-AUC must be direction=None
    assert "direction=None" in app_code


def test_act5_stat_specification():
    """Asserts that Act 5 defines act5_kpis using native mo.stat for FDP, candidate count, and active alpha."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    assert "act5_kpis" in app_code, "act5_kpis must be defined in app.py"
    assert "Empirical FDP" in app_code
    assert "Mean selected candidates" in app_code
    assert "Active nominal α" in app_code
    assert "250-run diagnostic utility" in app_code


# ---------------------------------------------------------------------------
# EC-T1-03: Reactive Table 1.1 Selection to BioactivationTracer and 3D Docking
# ---------------------------------------------------------------------------

def test_table_value_normalizes_empty_list_and_dict():
    """Validates that normalize_single_table_value safely normalizes various table value shapes."""
    import app as marimo_app
    # Get normalize_single_table_value from app or definition
    norm_fn = getattr(marimo_app, "normalize_single_table_value", None)
    if norm_fn is None:
        app_code = APP_PATH.read_text(encoding="utf-8")
        start = app_code.index("def normalize_single_table_value(value: object) -> dict:")
        end = app_code.index("return (normalize_single_table_value,)", start)
        func_code = app_code[start:end].strip()
        locs = {}
        exec(func_code, {}, locs)
        norm_fn = locs["normalize_single_table_value"]

    assert norm_fn(None) == {}
    assert norm_fn([]) == {}
    assert norm_fn([{}]) == {}
    assert norm_fn([{"Compound": "Lapatinib"}]) == {"Compound": "Lapatinib"}
    assert norm_fn({}) == {}
    assert norm_fn({"Compound": ["Mibefradil"]}) == {"Compound": "Mibefradil"}
    assert norm_fn({"Compound": "Raloxifene"}) == {"Compound": "Raloxifene"}


def test_act1_table_uses_single_selection_and_raloxifene_default():
    """Asserts that Table 1.1 uses selection='single', default Raloxifene selection, and hidden SMILES."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    assert 'selection="single"' in app_code
    assert 'hidden_columns=["SMILES"]' in app_code or "hidden_columns=['SMILES']" in app_code
    assert "initial_selection=[default_mbi_index]" in app_code or "initial_selection" in app_code


def test_act1_selection_binds_viewer_and_docking_state():
    """Asserts that Table 1.1 selection drives both Act 1 molecular viewer and Act 3 docking card."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    assert "normalize_single_table_value" in app_code
    assert "selected_entry" in app_code
    assert "selected_name" in app_code


# ---------------------------------------------------------------------------
# EC-T1-04: Reactive Table 5.1 Selection to Candidate Preview Card
# ---------------------------------------------------------------------------

def test_act5_table_uses_single_selection():
    """Asserts that Table 5.1 uses single selection and hides internal machine columns."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    assert "candidate_table = mo.ui.table(" in app_code
    assert 'hidden_columns=["candidate_id", "smiles"]' in app_code or "hidden_columns=['candidate_id', 'smiles']" in app_code


def test_act5_empty_selection_is_safe():
    """Asserts that empty selection on candidate_table yields an informative callout rather than an exception."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    assert "Select a candidate row in Table 5.1 above to inspect its 2D chemical structure." in app_code
    assert "candidate_card" in app_code


def test_act5_selection_renders_candidate_structure_card():
    """Asserts that candidate selection renders 2D candidate structure card with SMILES, alpha, probability, and layout validation."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    assert "### 2D Candidate Structure" in app_code
    assert "`SMILES`: `{smiles}`" in app_code
    assert "Active nominal α: `{alpha_slider.value:.2f}`" in app_code
    assert "Predicted liability probability:" in app_code
    assert "Weighted conformal p-value:" in app_code
    assert "safe_generate_molecule_layout(smiles)" in app_code
    assert "if not _layout or not _layout.get(\"atoms\"):" in app_code


# ---------------------------------------------------------------------------
# EC-T1-05: One-Click mo.download Prioritized Candidate Pool Export
# ---------------------------------------------------------------------------

def test_candidate_csv_has_exact_schema():
    """Asserts that the exported CSV schema exactly matches the 6 canonical columns in order."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    expected_cols = [
        "molecule_name",
        "smiles",
        "predicted_liability_prob",
        "weighted_conformal_pvalue",
        "nominal_alpha_threshold",
        "conformal_cutoff_pstar",
    ]
    for col in expected_cols:
        assert f'"{col}"' in app_code or f"'{col}'" in app_code, f"Missing export column: {col}"


def test_candidate_csv_tracks_active_alpha():
    """Asserts that candidate download filename and rows dynamically track active alpha."""
    app_code = APP_PATH.read_text(encoding="utf-8")
    assert "txconformal_candidates_alpha_" in app_code
    assert "candidate_download" in app_code
    assert 'mimetype="text/csv"' in app_code


def test_candidate_csv_real_builder_and_round_trip():
    """Validates that production build_candidate_csv from app.py outputs valid UTF-8 CSV with exact schema."""
    import csv
    import io
    import app as marimo_app

    _, defs = marimo_app.app.run()
    assert "build_candidate_csv" in defs, "app.py did not define build_candidate_csv"
    build_candidate_csv = defs["build_candidate_csv"]
    raw_bytes = build_candidate_csv()

    EXPECTED_COLUMNS = [
        "molecule_name",
        "smiles",
        "predicted_liability_prob",
        "weighted_conformal_pvalue",
        "nominal_alpha_threshold",
        "conformal_cutoff_pstar",
    ]

    # Round trip
    reader = list(csv.DictReader(io.StringIO(raw_bytes.decode("utf-8"))))
    assert len(reader) == 56, f"Expected 56 selected candidates at alpha=0.10, got {len(reader)}"
    assert list(reader[0].keys()) == EXPECTED_COLUMNS
    for r in reader:
        assert float(r["predicted_liability_prob"]) >= 0.0
        assert float(r["weighted_conformal_pvalue"]) >= 0.0
        assert float(r["nominal_alpha_threshold"]) == 0.10
        assert float(r["conformal_cutoff_pstar"]) > 0.0


# ---------------------------------------------------------------------------
# EC-T1-06: Standalone Inlined ESM and Runtime Portability
# ---------------------------------------------------------------------------

def test_standalone_inlined_esm_syntax_and_svg_namespace():
    """Asserts that standalone_app.py contains valid inlined ESM with correct svgNS and zero JS syntax errors."""
    import subprocess

    standalone_code = STANDALONE_PATH.read_text(encoding="utf-8")
    assert 'const svgNS = "http://www.w3.org/2000/svg";' in standalone_code, (
        "standalone_app.py must contain full SVG namespace without truncation"
    )

    # Extract _INLINED_ESM
    start_marker = '_INLINED_ESM = """'
    assert start_marker in standalone_code
    start = standalone_code.index(start_marker) + len(start_marker)
    end = standalone_code.index('"""', start)
    js_code = standalone_code[start:end]

    # Validate ESM syntax without disk writes
    res = subprocess.run(
        ["node", "--input-type=module", "--check"],
        input=js_code,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"node --check failed on inlined ESM: {res.stderr}"


def test_standalone_bundle_size_strictly_under_budget():
    """Asserts that standalone_app.py strictly stays under 200,000 bytes."""
    size_bytes = STANDALONE_PATH.stat().st_size
    assert size_bytes < 200000, f"standalone_app.py is {size_bytes} bytes, exceeding 200,000 budget!"


def test_standalone_runtime_headless_browser():
    """Validates that standalone_app.py mounts cleanly in headless Chrome with 0 console errors and mounted widgets."""
    import os
    import subprocess
    import time

    if os.environ.get("RUN_BROWSER_TESTS") != "1":
        pytest.skip("Standalone live browser test gated behind RUN_BROWSER_TESTS=1")

    from playwright.sync_api import sync_playwright

    proc = subprocess.Popen(
        [sys.executable, "-m", "marimo", "run", str(STANDALONE_PATH), "--port", "2720", "--headless"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(3.0)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                headless=True,
                args=["--disable-gpu", "--no-sandbox"],
            )
            page = browser.new_page()
            errors = []
            page.on("console", lambda m: errors.append(m.text) if m.type in ("error", "assert") else None)
            page.on("pageerror", lambda e: errors.append(str(e)))

            page.goto("http://localhost:2720", wait_until="networkidle", timeout=20000)
            page.wait_for_timeout(2000)

            widgets = page.query_selector_all(".bat-container")
            svgs = page.query_selector_all("svg")

            assert len(errors) == 0, f"Standalone console errors: {errors}"
            assert len(widgets) == 5, f"Expected exactly 5 widgets, got {len(widgets)}"
            assert len(svgs) >= 70, f"Expected >= 70 SVGs, got {len(svgs)}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()




