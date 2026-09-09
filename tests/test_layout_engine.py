"""
Unit tests for EC-3-1-01: Python-side RDKit 2D Layout Generator for Anywidget.
"""

import json
import sys
import time
from pathlib import Path
import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from widgets.layout_engine import (
    generate_molecule_layout,
    assert_layout_validity,
    batch_generate_layouts,
)

PRIMARY_PARQUET = BASE_DIR / "data" / "packaged" / "cyp_tdi_curated.parquet"
MBI_FIXTURE = BASE_DIR / "data" / "fixtures" / "literature_mbi_reference_set.json"


def test_single_molecule_layout_structure():
    smiles = "CC1=C(C(=O)N(C1=O)C)N2C=NC(=C2)C"  # Furafylline
    layout = generate_molecule_layout(smiles)

    assert "viewBox" in layout
    assert layout["viewBox"]["width"] > 0
    assert layout["viewBox"]["height"] > 0
    assert layout["num_atoms"] == 15
    assert layout["num_bonds"] == 16
    assert len(layout["atoms"]) == 15
    assert len(layout["bonds"]) == 16

    # Test JSON serializability
    dumped = json.dumps(layout)
    assert len(dumped) > 100
    loaded = json.loads(dumped)
    assert loaded["canonical_smiles"] == layout["canonical_smiles"]


def test_warhead_detection_on_literature_mbis():
    with open(MBI_FIXTURE) as f:
        data = json.load(f)

    for entry in data["entries"]:
        smi = entry["smiles"]
        name = entry["name"]
        layout = generate_molecule_layout(smi)

        assert layout["has_bioactivation_alert"] is True, f"Failed to detect warhead alert in {name}"
        assert len(layout["warhead_alerts"]) > 0

        # Check that warhead atoms have appropriate halos
        warhead_atoms = [a for a in layout["atoms"] if a["in_warhead"]]
        assert len(warhead_atoms) > 0
        for wa in warhead_atoms:
            assert wa["halo_color"] is not None
            assert wa["halo_intensity"] > 0.0


def test_100_arbitrary_drug_molecules_layout_validity():
    df = pd.read_parquet(PRIMARY_PARQUET)
    sample_smiles = df["assay_smiles"].sample(n=100, random_state=42).tolist()

    t0 = time.perf_counter()
    layouts = batch_generate_layouts(sample_smiles)
    total_dt = time.perf_counter() - t0

    mean_latency_ms = (total_dt / len(sample_smiles)) * 1000
    print(f"\n100 molecules layout latency: {total_dt:.3f}s ({mean_latency_ms:.2f} ms/mol)")

    assert len(layouts) == 100
    assert mean_latency_ms < 5.0, f"Mean latency {mean_latency_ms:.2f}ms exceeds 5ms SLA!"

    for i, layout in enumerate(layouts):
        assert_layout_validity(layout)
        assert layout["num_atoms"] > 0
        assert layout["viewBox"]["width"] > 50.0
        assert layout["viewBox"]["height"] > 50.0


def test_invalid_smiles_handling():
    with pytest.raises(ValueError, match="Invalid SMILES"):
        generate_molecule_layout("NOT_A_VALID_CHEMICAL_SMILES_123")
