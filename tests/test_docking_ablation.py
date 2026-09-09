"""
Unit tests for EC-2-2-02: CYP3A4 Structural Pocket Docking & ONNX Feasibility.
"""

import json
from pathlib import Path
import numpy as np
import pytest
import onnx
import onnxruntime as ort

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_JSON = BASE_DIR / "data" / "packaged" / "docking_ablation_results.json"
REPORT_MD = BASE_DIR / "docs" / "STRETCH_EXPERIMENTS_REPORT.md"
ONNX_MODEL = BASE_DIR / "data" / "processed" / "pdbqt" / "chemprop_predictor.onnx"


@pytest.fixture(scope="module")
def ablation_data():
    assert OUT_JSON.exists(), f"Missing {OUT_JSON}"
    with open(OUT_JSON) as f:
        return json.load(f)


def test_docking_metadata_and_receptors(ablation_data):
    meta = ablation_data["metadata"]
    assert meta["task_id"] == "EC-2-2-02"
    assert meta["num_compounds_docked"] == 10
    assert set(meta["receptors_evaluated"]) == {"2V0M", "1TQN"}
    assert "2V0M" in ablation_data["receptors"]
    assert "1TQN" in ablation_data["receptors"]


def test_docking_energies_and_heme_distances(ablation_data):
    compounds = ablation_data["docking_evaluations"]
    assert len(compounds) == 10

    for comp in compounds:
        assert "name" in comp
        assert "docking_results" in comp
        res_2v0m = comp["docking_results"]["2V0M"]
        res_1tqn = comp["docking_results"]["1TQN"]

        # Affinities must be favorable negative values (< -5.0 kcal/mol)
        assert res_2v0m["vina_affinity_kcal_mol"] < -5.0
        assert res_1tqn["vina_affinity_kcal_mol"] < -5.0

        # In 2V0M, all 10 MBIs should enter the active-site steric proximity sphere (<= 5.0 A)
        assert res_2v0m["min_dist_to_heme_fe_angstrom"] <= 5.0
        assert res_2v0m["in_active_site_steric_proximity_le_5A"] is True
        assert res_2v0m["in_heme_reaction_sphere_le_5A"] is True

    # Assert typed contact distances for literature MBIs
    tienilic = next(c for c in compounds if c["name"] == "Tienilic acid")
    assert abs(tienilic["docking_results"]["2V0M"]["min_dist_to_heme_fe_angstrom"] - 2.19) <= 0.05
    assert abs(tienilic["docking_results"]["2V0M"]["reactive_sulfur_dist_angstrom"] - 6.90) <= 0.05

    raloxifene = next(c for c in compounds if c["name"] == "Raloxifene")
    assert abs(raloxifene["docking_results"]["2V0M"]["min_dist_to_heme_fe_angstrom"] - 2.23) <= 0.05
    assert abs(raloxifene["docking_results"]["2V0M"]["reactive_sulfur_dist_angstrom"] - 8.02) <= 0.05


def test_onnx_export_and_runtime_inference(ablation_data):
    """Dense-Head Smoke Test: validates Chemprop FFN predictor head ONNX serialization parity on 300D embedding vectors."""
    onnx_res = ablation_data["onnx_export_feasibility"]
    assert onnx_res["status"] == "PASS"
    assert onnx_res["parity_verified"] is True
    assert onnx_res["numerical_parity_max_abs_diff"] < 1e-5

    assert ONNX_MODEL.exists()
    model = onnx.load(str(ONNX_MODEL))
    onnx.checker.check_model(model)

    session = ort.InferenceSession(str(ONNX_MODEL))
    # Deterministic test inputs matching 300D Chemprop latent embedding dimensions
    dummy_input = np.ones((2, 300), dtype=np.float32) * 0.5
    out = session.run(None, {"graph_embedding": dummy_input})[0]
    assert out.shape == (2, 1)
    assert (0.0 <= out).all() and (out <= 1.0).all()


def test_report_exists_and_contains_summary():
    assert REPORT_MD.exists()
    text = REPORT_MD.read_text()
    assert "# CYP3A4 Structural Pocket Docking & Chemprop ONNX Export Study" in text
    assert "2V0M" in text
    assert "1TQN" in text
    assert "Raloxifene" in text
    assert "Lapatinib" in text


def test_pdbqt_source_to_artifact_reproducibility(ablation_data):
    """Comprehensively verify raw PDBQT parsing reproducibility for all 10 compounds against packaged docking results."""
    def parse_pdbqt(path: Path, fe_coord: np.ndarray):
        affinity = None
        heavy_atoms = []
        in_m1 = False
        for line in path.read_text().splitlines():
            if "REMARK VINA RESULT:" in line and affinity is None:
                affinity = float(line.split()[3])
            elif line.startswith("MODEL 1"):
                in_m1 = True
            elif line.startswith("ENDMDL"):
                break
            elif in_m1 and line.startswith(("ATOM", "HETATM")):
                name = line[12:16].strip()
                atype = line[77:].strip()
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                if not (name.startswith("H") or atype in ("H", "HD", "HS")):
                    heavy_atoms.append((name, atype, [x, y, z]))
        coords = np.array([a[2] for a in heavy_atoms])
        dists = np.linalg.norm(coords - fe_coord, axis=1)
        min_dist = round(float(np.min(dists)), 2)
        s_indices = [i for i, a in enumerate(heavy_atoms) if a[0].startswith("S") or a[1] == "S"]
        min_s = round(float(np.min(dists[s_indices])), 2) if s_indices else None
        return affinity, min_dist, min_s

    receptors = ablation_data["receptors"]
    for comp in ablation_data["docking_evaluations"]:
        name = comp["name"]
        slug = name.lower().replace(" ", "_")
        for rec_id in ("2V0M", "1TQN"):
            p = BASE_DIR / "data" / "processed" / "pdbqt" / f"docked_{rec_id}_{slug}.pdbqt"
            assert p.exists(), f"Missing raw PDBQT file {p}"
            fe_coord = np.array(receptors[rec_id]["fe_coord"])
            aff, min_dist, min_s = parse_pdbqt(p, fe_coord)
            exp = comp["docking_results"][rec_id]
            assert min_dist == exp["min_dist_to_heme_fe_angstrom"], f"{name} {rec_id} distance mismatch: {min_dist} vs {exp['min_dist_to_heme_fe_angstrom']}"
            assert aff == exp["vina_affinity_kcal_mol"], f"{name} {rec_id} affinity mismatch: {aff} vs {exp['vina_affinity_kcal_mol']}"
            if exp.get("reactive_sulfur_dist_angstrom") is not None:
                assert min_s == exp["reactive_sulfur_dist_angstrom"], f"{name} {rec_id} sulfur distance mismatch: {min_s} vs {exp['reactive_sulfur_dist_angstrom']}"


