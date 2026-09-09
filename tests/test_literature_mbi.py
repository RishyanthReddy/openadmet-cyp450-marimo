"""
Unit tests for EC-1-4-01: Literature Mechanism-Based Inhibitor (MBI) reference set.
"""

import json
from pathlib import Path
import pytest
from rdkit import Chem

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "data" / "fixtures" / "literature_mbi_reference_set.json"


@pytest.fixture(scope="module")
def mbi_data():
    assert JSON_PATH.exists(), f"Missing {JSON_PATH}"
    with open(JSON_PATH) as f:
        return json.load(f)


def test_metadata_integrity(mbi_data):
    assert "metadata" in mbi_data
    assert mbi_data["metadata"]["num_entries"] == 10
    assert len(mbi_data["entries"]) == 10


def test_schema_and_required_fields(mbi_data):
    required_fields = {
        "id", "name", "target_cyp", "smiles", "inchikey",
        "evidence_level", "inactivation_mechanism",
        "reactive_warhead_motif", "literature_citation",
        "pubmed_id", "openadmet_presence", "notes"
    }
    for entry in mbi_data["entries"]:
        assert required_fields.issubset(set(entry.keys()))
        assert len(entry["literature_citation"]) > 10
        assert len(entry["reactive_warhead_motif"]) > 3
        assert entry["pubmed_id"].isdigit() and len(entry["pubmed_id"]) >= 7


def test_chemical_validity_and_inchikeys(mbi_data):
    for entry in mbi_data["entries"]:
        mol = Chem.MolFromSmiles(entry["smiles"])
        assert mol is not None, f"Failed to parse SMILES for {entry['name']}"
        calc_inchikey = Chem.MolToInchiKey(mol)
        assert calc_inchikey == entry["inchikey"], f"InChIKey mismatch for {entry['name']}"


def test_specific_isoforms_and_openadmet_presence(mbi_data):
    entries_by_name = {e["name"]: e for e in mbi_data["entries"]}

    # Furafylline is CYP1A2 reference control
    assert entries_by_name["Furafylline"]["target_cyp"] == "CYP1A2"

    # Paroxetine is CYP2D6 MBI
    assert entries_by_name["Paroxetine"]["target_cyp"] == "CYP2D6"

    # Mibefradil and Diltiazem are CYP3A4 MBIs
    assert entries_by_name["Mibefradil"]["target_cyp"] == "CYP3A4"
    assert entries_by_name["Diltiazem"]["target_cyp"] == "CYP3A4"

    # Clopidogrel and Raloxifene are in OpenADMET
    assert entries_by_name["Clopidogrel"]["openadmet_presence"] is True
    assert entries_by_name["Raloxifene"]["openadmet_presence"] is True

    # Total in OpenADMET is exactly 2
    in_openadmet = sum(1 for e in mbi_data["entries"] if e["openadmet_presence"])
    assert in_openadmet == 2
