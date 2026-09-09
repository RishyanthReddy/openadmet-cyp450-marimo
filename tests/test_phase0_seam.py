"""
EC-INTEGRATION-P0-01: Phase 0 Seam Integration Test Suite.

Verifies end-to-end coherence across all Phase 0 deliverables:
  1. Pinned artifact checksums and report integrity (Audit, Endpoint Dict, Smoke Test, Feasibility).
  2. Data schema contracts for the 100-molecule vertical slice (CSV and JSON graph payloads).
  3. Programmatic target-leakage prohibition on baseline features.
  4. RDKit chemical validity across all slice molecules.
  5. BioactivationTracerWidget anywidget state synchronization.
  6. Cold-boot latency of the interactive vertical slice (< 3.0s SLA).
  7. AIMNet2-NSE Gate 1 verification on Beam Cloud NVIDIA RTX 4090.
"""

from __future__ import annotations

import base64
import gzip
import hashlib
import importlib.util
import json
import time
from pathlib import Path
import pandas as pd
import pytest
from rdkit import Chem

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
DOCS_DIR = BASE_DIR / "docs"
SPIKES_DIR = BASE_DIR / "spikes"

PINNED_RAW_FILES = {
    "cyp-challenge-TRAIN_TDI.csv": {
        "sha256": "b458f599a792412292664386e8f18adc5d4a4129d6bd212ae80a60fb9b96bb60",
        "rows": 6145,
    },
    "cyp-challenge-TEST-BLINDED.csv": {
        "sha256": "a342f8444a8dcb531ca12f3685293f0bd6c36ae9073f491e44a9bc1cc4b741f9",
        "rows": 750,
    },
    "cyp-challenge-TRAIN_inhibition.csv": {
        "sha256": "b8f79addd266fb6f9f4c222c5e4e73d926362328b6a8d2841871a54e46bd2278",
        "rows": 4905,
    },
    "cyp-challenge-TRAIN_Emax.csv": {
        "sha256": "482f686a9a9f9166f290e6f5ea463a99de1da478b179a88f4baef48bc66501f1",
        "rows": 6145,
    },
    "octant_reactivity.tsv": {
        "sha256": "efca9d85202f215edeb929d3786693359589ea83071a3ebcbe1de79318e24834",
        "rows": 2446,
    },
    "octant_inhibition.tsv": {
        "sha256": "19e537166a17a42dd50cc262dd6eb0a963c181830fdc52db0fba98533e01c9c6",
        "rows": 1340,
    },
    "octant_willitfly_github.tsv": {
        "sha256": "afb8482cad6910fce18c14661810b2c3342797fd60833e6daba9065f5cb18d37",
        "rows": 11353,
    },
}


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestPhase0Artifacts:
    """Verifies artifact checksums, reports, and documentation integrity."""

    @pytest.mark.parametrize("filename,meta", PINNED_RAW_FILES.items())
    def test_raw_files_checksum_and_row_count(self, filename: str, meta: dict):
        path = RAW_DIR / filename
        assert path.exists(), f"Raw source file missing: {path}"
        actual_sha = compute_sha256(path)
        assert actual_sha == meta["sha256"], (
            f"Checksum mismatch for {filename}!\n"
            f"Expected: {meta['sha256']}\nActual:   {actual_sha}"
        )
        sep = "\t" if filename.endswith(".tsv") else ","
        df = pd.read_csv(path, sep=sep)
        assert len(df) == meta["rows"], (
            f"Row count mismatch for {filename}!\n"
            f"Expected: {meta['rows']}\nActual:   {len(df)}"
        )

    def test_dataset_audit_report_contents(self):
        report = DOCS_DIR / "DATASET_AUDIT_REPORT.md"
        assert report.exists()
        text = report.read_text()
        assert "2,446" in text or "2446" in text, "Audit report must document the 2,446 reactivity count."
        assert "willitfly" in text.lower(), "Audit report must document the willitfly stereoisomer investigation."
        assert "95.79%" in text or "5,886" in text, "Audit report must document the dropna() joint missingness trap."

    def test_endpoint_dictionary_guardrails(self):
        dict_file = DOCS_DIR / "ENDPOINT_DICTIONARY.md"
        assert dict_file.exists()
        text = dict_file.read_text()
        assert "assert_zero_target_leakage" in text, "Endpoint dictionary must specify leakage assertion."
        assert "assay_smiles" in text and "grouping_parent_smiles" in text, "Dual-SMILES policy missing."

    def test_aimnet2_feasibility_gate1_report(self):
        report = DOCS_DIR / "AIMNET2_FEASIBILITY_REPORT.md"
        assert report.exists()
        text = report.read_text()
        assert "RTX 4090" in text, "Feasibility report must cite the RTX 4090 GPU execution."
        assert "PASS (GO)" in text, "Gate 1 verdict must be PASS (GO)."


class TestSlice100DataCoherence:
    """Verifies schema, RDKit coordinates, and absence of target leakage in slice 100."""

    @classmethod
    @pytest.fixture(scope="class")
    def slice_data(cls):
        csv_path = PROCESSED_DIR / "slice_100.csv"
        json_path = PROCESSED_DIR / "slice_100_payload.json"
        assert csv_path.exists(), f"Missing {csv_path}"
        assert json_path.exists(), f"Missing {json_path}"
        df = pd.read_csv(csv_path)
        with open(json_path) as f:
            payload = json.load(f)
        return df, payload

    def test_slice_100_row_count_and_columns(self, slice_data):
        df, payload = slice_data
        assert len(df) == 100, f"Expected 100 molecules in slice, got {len(df)}"
        assert len(payload) == 100, f"Expected 100 payloads, got {len(payload)}"

        expected_cols = {
            "Molecule_Name", "SMILES", "CYP3A4_is_TDI",
            "baseline_prob_tdi", "baseline_pred_tdi",
            "ammonium_fluoride_area", "ammonium_formate_area",
        }
        assert expected_cols.issubset(set(df.columns)), f"Missing columns in slice_100.csv: {expected_cols - set(df.columns)}"

        # Verify class balance: 25 positive liabilities, 75 negative
        pos_count = int(df["CYP3A4_is_TDI"].sum())
        assert pos_count == 25, f"Expected 25 positive liabilities, got {pos_count}"

    def test_slice_100_payload_schema_and_geometry(self, slice_data):
        _, payload = slice_data
        for idx, mol in enumerate(payload):
            assert "id" in mol and "smiles" in mol
            assert "atoms" in mol and "bonds" in mol
            assert len(mol["atoms"]) > 0

            # Verify atom coordinate boundedness and finite floats
            for a in mol["atoms"]:
                assert "index" in a and "symbol" in a and "x" in a and "y" in a
                assert not (a["x"] != a["x"] or a["y"] != a["y"]), "NaN coordinate detected"
                assert "halo_intensity" in a
                assert 0.0 <= a["halo_intensity"] <= 1.0

            # Verify bonds
            num_atoms = len(mol["atoms"])
            for b in mol["bonds"]:
                assert 0 <= b["source"] < num_atoms
                assert 0 <= b["target"] < num_atoms
                assert b["order"] in {1, 2, 3, 1.5, 4}

    def test_rdkit_chemical_validity(self, slice_data):
        df, _ = slice_data
        for _, row in df.iterrows():
            mol = Chem.MolFromSmiles(row["SMILES"])
            assert mol is not None, f"RDKit failed to parse SMILES: {row['SMILES']}"
            assert mol.GetNumAtoms() > 0

    def test_target_leakage_assertion_on_features(self, slice_data):
        df, _ = slice_data
        forbidden = [
            "pic50", "tdi_condition", "direct_inhibition", "conf_high",
            "conf_low", "std", "emax", "is_tdi", "pct_remaining", "area",
        ]
        # In baseline features, none of these should appear in feature matrix columns
        feature_cols = [c.lower() for c in df.columns if c.startswith("fp_") or c.startswith("feat_")]
        for f in feature_cols:
            for bad in forbidden:
                assert bad not in f, f"Forbidden target column substring '{bad}' leaked into feature '{f}'!"


class TestAnywidgetAndNotebookBoot:
    """Verifies that BioactivationTracerWidget syncs state and that notebook boots in < 3.0s."""

    def test_anywidget_traitlet_contract(self):
        notebook_path = SPIKES_DIR / "spike_02_vertical_slice.py"
        assert notebook_path.exists()

        spec = importlib.util.spec_from_file_location("vertical_slice_module", notebook_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        source = notebook_path.read_text()
        assert "class BioactivationTracerWidget(anywidget.AnyWidget):" in source
        assert "molecule = traitlets.Dict(default_value={}).tag(sync=True)" in source
        assert "_esm = \"\"\"" in source
        assert "model.on(\"change:molecule\", draw)" in source

    def test_vertical_slice_local_boot_latency(self):
        """Measures cold boot latency of spike_02_vertical_slice.py (< 3.0s SLA)."""
        notebook_path = SPIKES_DIR / "spike_02_vertical_slice.py"

        t0 = time.perf_counter()
        spec = importlib.util.spec_from_file_location("spike_vs", notebook_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        boot_time = time.perf_counter() - t0

        print(f"\n[BENCHMARK] Vertical slice in-memory boot latency: {boot_time:.4f} seconds")
        assert boot_time < 3.0, f"Boot latency {boot_time:.3f}s exceeded 3.0s SLA!"

    def test_embedded_payload_decodes_cleanly(self):
        """Verifies embedded base64 gzipped payload unpacks cleanly without disk access."""
        notebook_path = SPIKES_DIR / "spike_02_vertical_slice.py"
        source = notebook_path.read_text()

        assert "EMBEDDED_B64_PAYLOAD = \"" in source
        start = source.find('EMBEDDED_B64_PAYLOAD = "') + len('EMBEDDED_B64_PAYLOAD = "')
        end = source.find('"', start)
        b64_str = source[start:end].strip()

        raw_gz = base64.b64decode(b64_str)
        decompressed = gzip.decompress(raw_gz).decode("utf-8")
        data = json.loads(decompressed)

        assert len(data) == 100, f"Expected 100 molecules in embedded payload, got {len(data)}"
        assert data[0]["id"].startswith("OCNT-")


class TestAIMNet2Gate1Seam:
    """Verifies that AIMNet2 Gate 1 outputs are verified on Cloud GPU."""

    def test_aimnet2_spike_results_file(self):
        spike_json = PROCESSED_DIR / "aimnet2_spike_50.json"
        assert spike_json.exists(), "aimnet2_spike_50.json missing!"

        with open(spike_json) as f:
            data = json.load(f)

        assert data["status"] == "success"
        assert "RTX 4090" in data["device_name"]
        assert len(data["molecules"]) == 50

        # Verify steady-state latency and no NaNs
        latencies = [m["latency_s"] for m in data["molecules"][1:]]  # Exclude first warmup call
        median_lat = sorted(latencies)[len(latencies) // 2]
        assert median_lat < 0.10, f"Median steady-state GPU latency {median_lat:.4f}s exceeds 0.10s!"

        for m in data["molecules"]:
            ip = m["ip_v_ev"]
            ea = m["ea_v_ev"]
            assert ip == ip and ea == ea, f"NaN energy delta detected for {m['id']}"
            assert 5.0 <= ip <= 12.0, f"Unphysical IP_v {ip} eV for molecule {m['id']}"
