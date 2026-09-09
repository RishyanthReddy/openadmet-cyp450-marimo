"""
EC-4-3-01: Defensive Fuzzing & Graceful Fallbacks.
Tests invalid SMILES strings, organometallics, macrocycles, and boundary chemotypes.
Asserts that layout generators and widget constructors return graceful fallbacks
without raising unhandled exceptions or tracebacks.
"""

import pytest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from widgets.layout_engine import (
    generate_molecule_layout,
    safe_generate_molecule_layout,
)
from widgets.bioactivation_tracer import BioactivationTracer


MALFORMED_SMILES = [
    "NOT_A_SMILES",
    "C1=CC=CC=",
    "",
    "   ",
    "C(((",
    "12345",
    ">>><<<",
    "C#C#C#C#C#C#C",
]

CHALLENGING_CHEMOTYPES = [
    # 32-membered macrocycle
    ("32-macrocycle", "C1" + "C" * 30 + "C1"),
    # Organometallic cisplatin
    ("cisplatin", "[Pt+2](Cl)(Cl)(N)(N)"),
    # Inorganic salt
    ("salt", "[Na+].[Cl-]"),
    # Stable isotope
    ("isotope", "[13CH4]"),
    # Huge linear alkyl chain
    ("long-chain", "C" * 120),
]


@pytest.mark.parametrize("bad_smiles", MALFORMED_SMILES)
def test_safe_layout_engine_fuzzing_malformed_inputs(bad_smiles):
    """Verify that safe_generate_molecule_layout returns a clean fallback dictionary without raising."""
    res = safe_generate_molecule_layout(bad_smiles)

    assert isinstance(res, dict)
    assert res["is_valid"] is False
    assert res["error"] is not None and len(res["error"]) > 0
    assert res["num_atoms"] == 0
    assert res["num_bonds"] == 0
    assert "viewBox" in res
    assert res["viewBox"]["width"] > 0
    assert res["viewBox"]["height"] > 0


@pytest.mark.parametrize("name, smiles", CHALLENGING_CHEMOTYPES)
def test_safe_layout_engine_challenging_chemotypes(name, smiles):
    """Verify that challenging chemotypes (macrocycles, organometallics, salts) parse cleanly."""
    res = safe_generate_molecule_layout(smiles)

    assert isinstance(res, dict)
    # Even if RDKit cannot compute 2D coords for certain inorganics, it must handle gracefully
    if res["is_valid"]:
        assert res["num_atoms"] > 0
        assert "atoms" in res
        assert "bonds" in res
    else:
        assert res["error"] is not None


@pytest.mark.parametrize("bad_smiles", MALFORMED_SMILES)
def test_bioactivation_tracer_safe_from_smiles(bad_smiles):
    """Verify that BioactivationTracer.safe_from_smiles constructs valid widget instances."""
    widget = BioactivationTracer.safe_from_smiles(bad_smiles)

    assert isinstance(widget, BioactivationTracer)
    assert widget.layout["is_valid"] is False
    assert widget.layout["error"] is not None
    assert widget.selected_atom_idx is None


def test_standard_layout_engine_strict_raises():
    """Verify that standard generate_molecule_layout strictly raises ValueError on invalid input."""
    with pytest.raises(ValueError, match="Invalid SMILES"):
        generate_molecule_layout("TOTALLY_INVALID")
