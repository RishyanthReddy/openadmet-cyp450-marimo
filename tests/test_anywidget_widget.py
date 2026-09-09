"""
Unit tests for EC-3-1-03: BioactivationTracer AnyWidget Python Wrapper & Traitlet Integration.
"""

import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import marimo as mo
from widgets.bioactivation_tracer import BioactivationTracer, get_inlined_widget_definition
from scripts.bundle_app import verify_bundle_components


def test_widget_instantiation_defaults():
    widget = BioactivationTracer()
    assert widget.layout == {}
    assert widget.overlay_mode == "warheads"
    assert widget.selected_atom_idx is None
    assert widget.selected_atom_metadata == {}
    assert len(widget._esm) > 500
    assert len(widget._css) > 500


def test_widget_from_smiles_factory():
    smiles = "CC1=C(C(=O)N(C1=O)C)N2C=NC(=C2)C"  # Furafylline
    widget = BioactivationTracer.from_smiles(smiles)

    assert widget.layout != {}
    assert widget.layout["smiles"] == smiles
    assert len(widget.layout["canonical_smiles"]) > 0
    assert widget.layout["num_atoms"] == 15
    assert widget.layout["num_bonds"] == 16
    assert widget.layout["has_bioactivation_alert"] is True
    assert widget.selected_atom_idx is None


def test_widget_traitlet_mutation_and_events():
    widget = BioactivationTracer.from_smiles("c1ccccc1")  # Benzene
    assert widget.layout["num_atoms"] == 6

    # Test selection mutation (simulating frontend click event)
    mock_metadata = {
        "atom_index": 2,
        "atom_symbol": "C",
        "formal_charge": 0,
        "is_aromatic": True,
        "in_warhead": False,
        "atom_score": 0.0,
        "score_type": "Baseline Element",
        "score_source": "Topological Graph",
        "normalization": "Unit range [0, 1]",
        "is_experimental": False,
    }

    widget.selected_atom_idx = 2
    widget.selected_atom_metadata = mock_metadata
    assert widget.selected_atom_idx == 2
    assert widget.selected_atom_metadata["atom_index"] == 2

    # Test update_smiles resets selection
    widget.update_smiles("CCO")
    assert widget.layout["num_atoms"] == 3
    assert widget.selected_atom_idx is None
    assert widget.selected_atom_metadata == {}


def test_marimo_ui_anywidget_mounting():
    widget = BioactivationTracer.from_smiles("c1ccccc1")
    ui_element = mo.ui.anywidget(widget)
    assert ui_element is not None
    # Verify value attribute delegates cleanly
    assert hasattr(ui_element, "value")


def test_inlined_widget_code_and_bundle_components():
    inlined_code = get_inlined_widget_definition()
    assert "class BioactivationTracer(anywidget.AnyWidget):" in inlined_code
    assert "_esm = " in inlined_code
    assert "_css = " in inlined_code

    bundle_status = verify_bundle_components()
    assert bundle_status["bundle_ready"] is True
    assert bundle_status["fallback_df_rows"] == 100
    assert bundle_status["mmp_transformations_count"] == 34
