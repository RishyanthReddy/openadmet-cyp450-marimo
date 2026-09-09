"""
tests/test_cyp2d6_ui.py - Automated Unit & Regression Tests for CYP2D6 Dual-Isoform Docking UI in Act 3.
Governed by docs/TIER1_TIER2_IMPLEMENTATION_PLAN.md and docs/CYP2D6_DOCKING_REPORT.md.
"""

import subprocess
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

APP_PATH = BASE_DIR / "app.py"


def test_marimo_check_app():
    """Asserts that app.py marimo DAG is free of cycles or missing references."""
    res = subprocess.run(
        [sys.executable, "-m", "marimo", "check", str(APP_PATH)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"marimo check failed:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"


def test_cyp2d6_ui_controls_and_section_defined():
    """Asserts that CYP2D6 controls and display card are defined and reactively bound in app.py."""
    code = APP_PATH.read_text(encoding="utf-8")

    # Verify control dropdowns
    assert "cyp2d6_compound_dropdown = mo.ui.dropdown(" in code
    assert "cyp2d6_isoform_dropdown = mo.ui.dropdown(" in code
    assert "All Conformations (Side-by-Side)" in code

    # Verify reactive consumption of dropdown value
    assert "cyp2d6_isoform_dropdown.value" in code

    # Verify section definition
    assert "act3_cyp2d6_section = mo.vstack([" in code
    assert "load_cyp2d6_docking_results" in code


def test_cyp2d6_ui_content_and_rigor():
    """Asserts that CYP2D6 section contains essential biophysical and telemetry assertions."""
    code = APP_PATH.read_text(encoding="utf-8")

    # Canonical CYP2D6 references & crystallographic targets
    assert "3TBG" in code
    assert "4WNW" in code
    assert "Asp301" in code
    assert "Paroxetine" in code

    # Beam Cloud RTX 4090 badge & Task ID
    assert "Beam Cloud" in code
    assert "RTX 4090" in code or "AutoDock Vina v1.2.7 on Beam Cloud" in code
    assert "dc1112ce-e7dc-4abe-943b-790ccae2e9b5" in code

    # Scientific honesty & honest geometry (not overclaiming salt bridge)
    assert "Active-Site Proximity" in code
    assert "(Electrostatic Salt Bridge)" not in code
    assert "empirical scoring functions" in code
    assert "k_{inact}/K_I" in code or "kinact" in code or "catalytic strike zone" in code


def test_cyp2d6_section_mounted_in_main_view():
    """Asserts that act3_cyp2d6_section is wired into main_view."""
    code = APP_PATH.read_text(encoding="utf-8")

    # In cell signature
    assert "act3_cyp2d6_section" in code

    # In main_view vstack
    main_view_def = code[code.find("main_view = mo.vstack(["):code.find("return (main_view,)")]
    assert "act3_docking_section," in main_view_def
    assert "act3_cyp2d6_section," in main_view_def
    # Make sure act3_cyp2d6_section appears directly after act3_docking_section
    docking_idx = main_view_def.find("act3_docking_section")
    cyp2d6_idx = main_view_def.find("act3_cyp2d6_section")
    assert docking_idx != -1 and cyp2d6_idx != -1
    assert docking_idx < cyp2d6_idx < main_view_def.find("act3_table_section")


def test_cyp2d6_ui_empty_evaluations_fallback_renders_no_numeric_sentinels():
    """Regression test (Luna Max Round 20): asserts that empty docking evaluation branch renders
    explicit 'No Evaluation Available' and completely eliminates numeric sentinels (0.0 kcal/mol, 99.9 A).
    """
    code = APP_PATH.read_text(encoding="utf-8")

    # Assert source code has eliminated numeric sentinels in fallback branch
    assert 'vina_affinity_kcal_mol": 0.0' not in code
    assert 'min_dist_to_heme_fe_angstrom": 99.9' not in code

    # Verify fallback formatting in app.py
    assert '_vina_3tbg_html = \'<span style="color: #94a3b8; font-weight: 600;">No Evaluation Available</span>\'' in code
    assert '_fe_dist_3tbg_html = \'<span style="color: #94a3b8; font-weight: 600;">No Evaluation Available</span>\'' in code
    assert "⚪ No Structural Evaluation Available" in code
    assert "No docking evaluation record is available for the current selection." in code

    # Same check for standalone_app.py
    standalone_code = (BASE_DIR / "standalone_app.py").read_text(encoding="utf-8")
    assert 'vina_affinity_kcal_mol": 0.0' not in standalone_code
    assert 'min_dist_to_heme_fe_angstrom": 99.9' not in standalone_code
    assert "⚪ No Structural Evaluation Available" in standalone_code


def test_cyp2d6_ui_empty_evaluations_live_cell_simulation():
    """Dynamically compiles and executes the registered Marimo Act 3 CYP2D6 cell AST from
    both app.py and standalone_app.py with empty evaluations (cyp2d6_evals=[]), asserting
    that the rendered HTML section completely eliminates numeric sentinels.
    """
    import ast
    import marimo as mo

    class DummyDropdown:
        value = None

    for target_file in [APP_PATH, BASE_DIR / "standalone_app.py"]:
        tree = ast.parse(target_file.read_text(encoding="utf-8"))
        target_func_node = None
        for n in ast.walk(tree):
            if isinstance(n, ast.FunctionDef) and set([
                "cyp2d6_compound_dropdown",
                "cyp2d6_dock_data",
                "cyp2d6_evals",
                "cyp2d6_isoform_dropdown",
                "mo",
            ]).issubset(set(a.arg for a in n.args.args)):
                target_func_node = n
                break

        assert target_func_node is not None, f"Could not locate CYP2D6 cell in {target_file.name}"
        target_func_node.decorator_list = []
        target_func_node.name = "eval_cyp2d6_cell"
        mod = ast.Module(body=[target_func_node], type_ignores=[])
        ast.fix_missing_locations(mod)

        code_obj = compile(mod, filename=f"<{target_file.name}_ast>", mode="exec")
        ns = {}
        exec(code_obj, ns)
        cell_func = ns["eval_cyp2d6_cell"]

        res = cell_func(
            cyp2d6_compound_dropdown=DummyDropdown(),
            cyp2d6_dock_data={},
            cyp2d6_evals=[],
            cyp2d6_isoform_dropdown=DummyDropdown(),
            mo=mo,
        )

        section = res[0]
        rendered_text = section.text
        import re
        clean_text = " ".join(re.sub(r"<[^>]+>", " ", rendered_text).split())

        # Strict absence of fake numeric sentinels
        assert "0.00 kcal/mol" not in clean_text, f"Found 0.00 kcal/mol in {target_file.name}"
        assert "0.0 kcal/mol" not in clean_text, f"Found 0.0 kcal/mol in {target_file.name}"
        assert "99.90 Å" not in clean_text, f"Found 99.90 Å in {target_file.name}"
        assert "99.9" not in clean_text, f"Found 99.9 in {target_file.name}"
        assert "Canonical CYP2D6 Mechanism" not in clean_text, f"Canonical narrative leaked in {target_file.name}"

        # Strict presence of explicit fail-closed labels
        assert "No Evaluation Available" in clean_text, f"Missing fail-closed label in {target_file.name}"
        assert "⚪ No Structural Evaluation Available" in clean_text, f"Missing badge in {target_file.name}"


