"""
tests/test_cyp2d6_docking.py - Automated Unit & Regression Tests for CYP2D6 Structural Docking.
Governed by docs/TIER1_TIER2_IMPLEMENTATION_PLAN.md (EC-T2-01).
"""

import json
import math
import subprocess
from pathlib import Path
import pytest
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = BASE_DIR / "data" / "raw" / "pdb" / "cyp2d6_manifest.json"
ARTIFACT_PATH = BASE_DIR / "data" / "packaged" / "cyp2d6_docking_results.json"
REPORT_PATH = BASE_DIR / "docs" / "CYP2D6_DOCKING_REPORT.md"
POSES_DIR = BASE_DIR / "data" / "processed" / "pdbqt" / "cyp2d6" / "poses"


def test_cyp2d6_artifact_schema_and_cardinality():
    """Asserts that cyp2d6_docking_results.json matches cyp2d6_docking.v1 schema with 10 compounds x 2 receptors."""
    assert ARTIFACT_PATH.exists(), f"CYP2D6 docking artifact missing at {ARTIFACT_PATH}"
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))

    assert data.get("schema_version") == "cyp2d6_docking.v1"
    meta = data.get("metadata", {})
    assert meta.get("task_id") == "EC-T2-01"
    assert meta.get("expected_compounds") == 10
    assert meta.get("expected_runs") == 20
    assert meta.get("completed_runs") == 20
    assert meta.get("vina_version") == "1.2.7"
    assert meta.get("seed") == 42
    assert meta.get("exhaustiveness") == 8
    exec_meta = meta.get("execution", {})
    assert exec_meta.get("provider") == "Beam"
    assert exec_meta.get("beam_task_id") == "dc1112ce-e7dc-4abe-943b-790ccae2e9b5"
    assert exec_meta.get("beam_environment") == "serverless_rtx4090"
    assert "sha256:" in exec_meta.get("image_digest", "")
    assert "RTX" in exec_meta.get("gpu_device", "") and "4090" in exec_meta.get("gpu_device", "")
    assert "RTX4090" in exec_meta.get("vina_compute_backend", "") or "RTX 4090" in exec_meta.get("vina_compute_backend", "")
    assert "https://app.beam.cloud" in exec_meta.get("provider_task_url", "")
    assert "function-dc1112ce" in exec_meta.get("container_id", "")
    assert exec_meta.get("provider_task_record_path") == "data/packaged/beam_cyp2d6_execution_record.json"

    # Verify provider execution record file integrity and API-authenticated linkage
    rec_path = BASE_DIR / exec_meta["provider_task_record_path"]
    assert rec_path.exists(), f"Missing provider execution record at {rec_path}"
    import hashlib
    assert hashlib.sha256(rec_path.read_bytes()).hexdigest() == exec_meta.get("provider_task_record_sha256")
    rec_data = json.loads(rec_path.read_text(encoding="utf-8"))
    assert rec_data.get("task_id") == "dc1112ce-e7dc-4abe-943b-790ccae2e9b5"
    assert rec_data.get("status") == "COMPLETE"
    assert rec_data.get("verified_by_provider_api") is True

    evaluations = data.get("docking_evaluations", [])
    assert len(evaluations) == 10
    for ev in evaluations:
        assert "name" in ev
        assert "smiles" in ev
        assert "target_cyp" in ev
        assert ev.get("warhead"), f"Missing warhead for {ev['name']}"
        assert "docking_results" in ev
        assert set(ev["docking_results"].keys()) == {"3TBG", "4WNW"}


def test_receptor_manifest_has_sha256_and_fe_centered_grid():
    """Asserts that cyp2d6_manifest.json contains valid byte-level SHA-256 and Fe-centered grid definitions."""
    assert MANIFEST_PATH.exists(), f"Receptor manifest missing at {MANIFEST_PATH}"
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert manifest.get("schema_version") == "cyp2d6_manifest.v1"
    receptors = manifest.get("receptors", {})
    assert set(receptors.keys()) == {"3TBG", "4WNW"}

    for pdb_id in ("3TBG", "4WNW"):
        rec = receptors[pdb_id]
        assert len(rec.get("source_pdb_sha256", "")) == 64
        assert len(rec.get("prepared_pdbqt_sha256", "")) == 64
        assert rec.get("chain") == "A"
        assert rec.get("retained_heteroatoms") == ["HEM"]
        assert rec.get("removed_waters") is True
        fe = rec.get("heme_fe_coord_angstrom", [])
        grid = rec.get("grid_center_angstrom", [])
        assert len(fe) == 3 and len(grid) == 3
        assert fe == grid, f"Grid center {grid} must match HEM Fe {fe} for {pdb_id}"
        assert rec.get("grid_size_angstrom") == [22.0, 22.0, 22.0]
        assert len(rec.get("asp301_od1_coord_angstrom", [])) == 3
        assert len(rec.get("asp301_od2_coord_angstrom", [])) == 3


def test_all_twenty_runs_have_explicit_status():
    """Asserts that all 20 docking evaluations have explicit 'ok' status and finite numeric metrics."""
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    evaluations = data.get("docking_evaluations", [])

    for ev in evaluations:
        name = ev["name"]
        for pdb_id in ("3TBG", "4WNW"):
            result = ev["docking_results"][pdb_id]
            assert result.get("status") in {"ok", "failed"}, f"Missing explicit status for {name} on {pdb_id}"
            if result["status"] == "ok":
                aff = result.get("vina_affinity_kcal_mol")
                fe_dist = result.get("min_dist_to_heme_fe_angstrom")
                assert aff is not None and math.isfinite(float(aff)), f"Invalid affinity for {name} on {pdb_id}"
                assert fe_dist is not None and math.isfinite(float(fe_dist)), f"Invalid Fe distance for {name} on {pdb_id}"
                assert isinstance(result.get("active_site_steric_proximity_le_5A"), bool)
                assert len(result.get("pose_1_pdbqt_sha256", "")) == 64
                assert result.get("nearest_heavy_atom") is not None
                assert result.get("docking_latency_sec") is not None
            else:
                assert result.get("error", {}).get("message")


def test_paroxetine_asp301_observation_is_not_overclaimed():
    """Asserts that Paroxetine's Asp301 observation is measured geometrically and honestly framed."""
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    evaluations = data.get("docking_evaluations", [])
    paroxetine = next((e for e in evaluations if e["name"] == "Paroxetine"), None)
    assert paroxetine is not None, "Paroxetine not found in docking evaluations"
    assert paroxetine.get("target_cyp") == "CYP2D6"

    for pdb_id, exp_dist in (("3TBG", 6.71), ("4WNW", 6.31)):
        res = paroxetine["docking_results"][pdb_id]
        asp_obs = res.get("asp301_contact")
        assert asp_obs is not None, f"Missing Asp301 observation for Paroxetine on {pdb_id}"
        assert asp_obs.get("residue") == "ASP301"
        assert asp_obs.get("contact_type") == "proximity_only"
        dist = asp_obs.get("distance_angstrom")
        assert dist == pytest.approx(exp_dist, abs=0.01)

    # Verify report does not overclaim Kd or covalent binding and includes Beam Task ID
    report_text = REPORT_PATH.read_text(encoding="utf-8")
    assert "dc1112ce-e7dc-4abe-943b-790ccae2e9b5" in report_text
    assert "not measured $K_d$ or covalent inactivation parameters" in report_text or "not measured" in report_text
    assert "Paroxetine" in report_text
    assert "Asp301" in report_text


def test_raw_pdbqt_pose_reproducibility():
    """Independently parses Model 1 from raw PDBQT poses to verify artifact reproducibility."""
    data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    evaluations = data.get("docking_evaluations", [])

    for ev in evaluations:
        safe_name = ev["name"].lower().replace(" ", "_").replace("-", "_")
        for pdb_id in ("3TBG", "4WNW"):
            pose_path = POSES_DIR / f"docked_{pdb_id}_{safe_name}.pdbqt"
            assert pose_path.exists(), f"Raw pose PDBQT missing: {pose_path}"

            # Parse Model 1 independently
            lines = pose_path.read_text(encoding="utf-8").splitlines()
            vina_aff = None
            heavy_coords = []
            in_mode_1 = False

            for line in lines:
                if "REMARK VINA RESULT:" in line and vina_aff is None:
                    vina_aff = float(line.split()[3])
                elif line.startswith("MODEL 1"):
                    in_mode_1 = True
                elif line.startswith("ENDMDL"):
                    break
                elif in_mode_1 and line.startswith(("ATOM", "HETATM")):
                    aname = line[12:16].strip()
                    atype = line[77:].strip()
                    if aname.startswith("H") or atype in ("H", "HD", "HS"):
                        continue
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    heavy_coords.append([x, y, z])

            res_expected = ev["docking_results"][pdb_id]
            assert vina_aff == pytest.approx(res_expected["vina_affinity_kcal_mol"], abs=0.01)

            fe_coord = np.array(manifest["receptors"][pdb_id]["heme_fe_coord_angstrom"])
            dists = np.linalg.norm(np.array(heavy_coords) - fe_coord, axis=1)
            min_dist = float(np.min(dists))
            assert min_dist == pytest.approx(res_expected["min_dist_to_heme_fe_angstrom"], abs=0.05)


def test_beam_provider_payload_cryptographic_binding():
    """Validates that raw Beam provider payload cryptographically binds to the packaged JSON artifact."""
    import cloudpickle
    import hashlib

    raw_payload_path = BASE_DIR / "data" / "packaged" / "beam_task_dc1112ce_raw_result.pkl"
    assert raw_payload_path.exists(), f"Missing raw provider payload at {raw_payload_path}"

    raw_bytes = raw_payload_path.read_bytes()
    raw_sha = hashlib.sha256(raw_bytes).hexdigest()

    rec_path = BASE_DIR / "data" / "packaged" / "beam_cyp2d6_execution_record.json"
    rec_data = json.loads(rec_path.read_text(encoding="utf-8"))
    assert raw_sha == rec_data.get("result_payload_sha256")
    assert raw_sha == "7abd0177817f1dd7ac4ffe0b1f62362835873481550229d35d15766123494109"

    raw_obj = cloudpickle.loads(raw_bytes)
    assert raw_obj.get("status") == "success"
    assert raw_obj["telemetry"]["provider"] == "Beam"
    assert "RTX 4090" in raw_obj["telemetry"]["gpu_device"]
    assert raw_obj["telemetry"]["cuda_available"] is True

    docking_data = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
    evals = docking_data.get("docking_evaluations", [])
    assert len(evals) == 10

    for ev in evals:
        cname = ev["name"]
        assert cname in raw_obj["results"]
        for pdb_id in ("3TBG", "4WNW"):
            json_res = ev["docking_results"][pdb_id]
            provider_res = raw_obj["results"][cname][pdb_id]
            assert json_res["vina_affinity_kcal_mol"] == pytest.approx(provider_res["vina_affinity_kcal_mol"], abs=1e-4)
            assert json_res["min_dist_to_heme_fe_angstrom"] == pytest.approx(provider_res["min_dist_to_heme_fe_angstrom"], abs=1e-4)
            assert json_res["nearest_heavy_atom"] == provider_res["nearest_heavy_atom"]
            assert json_res["pose_1_pdbqt_sha256"] == provider_res["pose_1_pdbqt_sha256"]

