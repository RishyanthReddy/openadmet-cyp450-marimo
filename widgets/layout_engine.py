#!/usr/bin/env python3
"""
EC-3-1-01: Python-Side RDKit 2D Layout Generator for BioactivationTracer Anywidget.

Converts molecular SMILES into clean, normalized JSON dictionaries containing:
  - 2D atom coordinates (SVG-inverted, scaled, with padding)
  - Bond topology (connectivity, bond orders, stereo tags)
  - Atom property vectors (formal charges, element colors, aromaticity)
  - Mechanism-based inactivation warhead detection (Furan, Thiophene, MDP, etc.)
  - Quantum reactivity halo annotations (Fukui indices, oxidation charge response)
"""

from __future__ import annotations

import math
from typing import Any
import numpy as np
from rdkit import Chem
from rdkit.Chem import rdDepictor

# Standard CPK/Biochemical element palette for SVG rendering
ELEMENT_COLORS = {
    "C": "#94a3b8",   # Slate carbon
    "N": "#3b82f6",   # Blue nitrogen
    "O": "#ef4444",   # Red oxygen
    "S": "#eab308",   # Yellow sulfur
    "F": "#10b981",   # Emerald fluorine
    "Cl": "#22c55e",  # Green chlorine
    "Br": "#a855f7",  # Purple bromine
    "I": "#7c3aed",   # Violet iodine
    "P": "#f97316",   # Orange phosphorus
    "Fe": "#ea580c",  # Rust orange iron
}

# Curated structural alerts for Cytochrome P450 mechanism-based bioactivation
WARHEAD_SMARTS = {
    "Furan": ("o1cccc1", "#f97316", "Furan ring oxidizes to reactive enedione / epoxide"),
    "Thiophene": ("s1cccc1", "#eab308", "Thiophene ring undergoes S-oxidation to reactive thiophene sulfoxide"),
    "1,3-Benzodioxole": ("c1ccc2c(c1)OCO2", "#ec4899", "Methylenedioxyphenyl forms covalent carbene complex with Heme Fe"),
    "Alkyne": ("C#C", "#8b5cf6", "Terminal/internal alkyne alkylates heme porphyrin nitrogen"),
    "Tertiary amine": ("[NX3]([#6])([#6])[#6]", "#06b6d4", "Undergoes alpha-carbon oxidation to reactive iminium intermediate"),
    "Aniline": ("c[NX3;H2,H1]", "#3b82f6", "Aromatic amine oxidizes to reactive nitroso / quinone imine"),
    "Quinone / Hydroquinone": ("O=C1C=CC(=O)C=C1", "#dc2626", "Michael acceptor susceptible to covalent cysteine addition"),
    "Hydrazine": ("[NX3][NX3]", "#6366f1", "Hydrazine motif generates reactive diazene radicals"),
}

_COMPILED_WARHEADS = {
    name: (Chem.MolFromSmarts(smarts), color, desc)
    for name, (smarts, color, desc) in WARHEAD_SMARTS.items()
}


def generate_molecule_layout(
    smiles: str,
    quantum_features: dict[str, Any] | None = None,
    scale: float = 35.0,
    padding: float = 30.0,
    atom_fukui_map: dict[int, float] | None = None,
) -> dict[str, Any]:
    """
    Computes 2D topological layout, bounding box, and bioactivation annotations for a SMILES string.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES string provided: {smiles}")

    mol = Chem.RemoveHs(mol)
    canonical_smiles = Chem.MolToSmiles(mol)
    inchikey = Chem.MolToInchiKey(mol)

    # Compute 2D coordinates
    rdDepictor.Compute2DCoords(mol)
    rdDepictor.NormalizeDepiction(mol)
    conf = mol.GetConformer()

    num_atoms = mol.GetNumAtoms()
    xs_raw = np.zeros(num_atoms, dtype=float)
    ys_raw = np.zeros(num_atoms, dtype=float)

    for i in range(num_atoms):
        pos = conf.GetAtomPosition(i)
        xs_raw[i] = pos.x
        # Invert y for standard SVG screen coordinates (y-down)
        ys_raw[i] = -pos.y

    # Normalize coordinates so min is at 0, then scale and pad
    min_x, max_x = float(xs_raw.min()), float(xs_raw.max())
    min_y, max_y = float(ys_raw.min()), float(ys_raw.max())

    span_x = max(max_x - min_x, 0.1)
    span_y = max(max_y - min_y, 0.1)

    # Scale to canvas pixels
    scaled_xs = (xs_raw - min_x) * scale + padding
    scaled_ys = (ys_raw - min_y) * scale + padding

    canvas_width = span_x * scale + 2 * padding
    canvas_height = span_y * scale + 2 * padding

    # 1. Detect Warhead Substructures
    warhead_matches = []
    atom_warhead_map = {}  # atom_idx -> (name, color, desc)

    for name, (sub_mol, color, desc) in _COMPILED_WARHEADS.items():
        if sub_mol is None:
            continue
        matches = mol.GetSubstructMatches(sub_mol)
        for match in matches:
            atom_indices = list(match)
            warhead_matches.append({
                "family": name,
                "color": color,
                "description": desc,
                "atom_indices": atom_indices,
            })
            for idx in atom_indices:
                if idx not in atom_warhead_map:
                    atom_warhead_map[idx] = (name, color, desc)

    # 2. Extract Atoms
    atoms_data = []
    for i in range(num_atoms):
        atom = mol.GetAtomWithIdx(i)
        symbol = atom.GetSymbol()
        charge = atom.GetFormalCharge()
        aromatic = atom.GetIsAromatic()

        # Check warhead
        in_warhead = i in atom_warhead_map
        warhead_family = atom_warhead_map[i][0] if in_warhead else None
        halo_color = atom_warhead_map[i][1] if in_warhead else None

        # Quantum Fukui radical index (if provided)
        fukui_val = 0.0
        if atom_fukui_map and i in atom_fukui_map:
            fukui_val = float(atom_fukui_map[i])
        elif quantum_features and "aimnet2_max_fukui_radical" in quantum_features and in_warhead:
            fukui_val = float(quantum_features["aimnet2_max_fukui_radical"])

        # Default halo intensity based on warhead or radical index
        halo_intensity = 0.85 if in_warhead else (fukui_val if fukui_val > 0 else 0.0)

        atoms_data.append({
            "index": i,
            "symbol": symbol,
            "x": round(float(scaled_xs[i]), 2),
            "y": round(float(scaled_ys[i]), 2),
            "charge": charge,
            "is_aromatic": aromatic,
            "element_color": ELEMENT_COLORS.get(symbol, "#64748b"),
            "in_warhead": in_warhead,
            "warhead_family": warhead_family,
            "halo_color": halo_color,
            "halo_intensity": round(halo_intensity, 2),
            "fukui_radical": round(fukui_val, 4),
        })

    # 3. Extract Bonds
    bonds_data = []
    for b in mol.GetBonds():
        b_idx = b.GetIdx()
        begin = b.GetBeginAtomIdx()
        end = b.GetEndAtomIdx()
        b_type = b.GetBondType()

        if b_type == Chem.rdchem.BondType.SINGLE:
            order = 1.0
        elif b_type == Chem.rdchem.BondType.DOUBLE:
            order = 2.0
        elif b_type == Chem.rdchem.BondType.TRIPLE:
            order = 3.0
        elif b_type == Chem.rdchem.BondType.AROMATIC:
            order = 1.5
        else:
            order = 1.0

        stereo_type = str(b.GetStereo()).replace("BondStereo.", "")
        in_warhead = (begin in atom_warhead_map) and (end in atom_warhead_map)

        bonds_data.append({
            "index": b_idx,
            "begin_atom": begin,
            "end_atom": end,
            "order": order,
            "is_aromatic": b.GetIsAromatic(),
            "stereo": stereo_type,
            "in_warhead": in_warhead,
        })

    layout_payload = {
        "smiles": smiles,
        "canonical_smiles": canonical_smiles,
        "inchikey": inchikey,
        "num_atoms": num_atoms,
        "num_bonds": len(bonds_data),
        "viewBox": {
            "min_x": 0.0,
            "min_y": 0.0,
            "width": round(canvas_width, 2),
            "height": round(canvas_height, 2),
        },
        "atoms": atoms_data,
        "bonds": bonds_data,
        "warhead_alerts": warhead_matches,
        "has_bioactivation_alert": len(warhead_matches) > 0,
        "rendering_metadata": {
            "scale": scale,
            "padding": padding,
            "generator": "rdkit-rdDepictor-Compute2DCoords",
            "version": "1.0.0",
        },
    }

    assert_layout_validity(layout_payload)
    return layout_payload


def assert_layout_validity(layout: dict[str, Any], min_atom_dist_ratio: float = 0.35) -> None:
    """
    Validates mathematical and topological integrity of a generated layout:
      - All coordinates are finite floats (no NaNs or infinities).
      - All bond endpoints point to existing atom indices.
      - Atoms are not overlapping (distance > min_atom_dist_ratio * scale).
    """
    scale = layout["rendering_metadata"]["scale"]
    min_dist_threshold = scale * min_atom_dist_ratio
    atoms = layout["atoms"]
    num_atoms = len(atoms)

    coords = []
    for a in atoms:
        x, y = a["x"], a["y"]
        assert not (math.isnan(x) or math.isnan(y)), f"NaN coordinate detected in atom {a['index']}"
        assert not (math.isinf(x) or math.isinf(y)), f"Infinite coordinate detected in atom {a['index']}"
        coords.append([x, y])

    # Check pairwise atom distances for overlapping
    coords = np.array(coords)
    for i in range(num_atoms):
        for j in range(i + 1, num_atoms):
            dist = np.linalg.norm(coords[i] - coords[j])
            assert dist >= min_dist_threshold, (
                f"Atoms {i} and {j} overlap! Distance {dist:.2f}px is below threshold {min_dist_threshold:.2f}px"
            )

    # Check bond integrity
    for b in layout["bonds"]:
        begin = b["begin_atom"]
        end = b["end_atom"]
        assert 0 <= begin < num_atoms, f"Bond {b['index']} begin atom {begin} out of bounds"
        assert 0 <= end < num_atoms, f"Bond {b['index']} end atom {end} out of bounds"


def batch_generate_layouts(smiles_list: list[str]) -> list[dict[str, Any]]:
    """Batch generator for multiple molecules."""
    return [generate_molecule_layout(s) for s in smiles_list]


def safe_generate_molecule_layout(
    smiles: str,
    quantum_features: dict[str, Any] | None = None,
    scale: float = 35.0,
    padding: float = 30.0,
    atom_fukui_map: dict[int, float] | None = None,
) -> dict[str, Any]:
    """Defensive wrapper that returns a structured fallback layout instead of raising exceptions."""
    if not smiles or not isinstance(smiles, str) or not smiles.strip():
        return {
            "is_valid": False,
            "error": "Empty or non-string SMILES provided.",
            "canonical_smiles": "",
            "inchikey": "",
            "num_atoms": 0,
            "num_bonds": 0,
            "atoms": [],
            "bonds": [],
            "warhead_regions": [],
            "warhead_alerts": [],
            "has_bioactivation_alert": False,
            "viewBox": {"min_x": 0, "min_y": 0, "width": 300, "height": 200},
            "canvas_width": 300,
            "canvas_height": 200,
        }
    try:
        res = generate_molecule_layout(
            smiles=smiles,
            quantum_features=quantum_features,
            scale=scale,
            padding=padding,
            atom_fukui_map=atom_fukui_map,
        )
        res["is_valid"] = True
        res["error"] = None
        return res
    except Exception as err:
        return {
            "is_valid": False,
            "error": str(err),
            "canonical_smiles": str(smiles),
            "inchikey": "",
            "num_atoms": 0,
            "num_bonds": 0,
            "atoms": [],
            "bonds": [],
            "warhead_regions": [],
            "warhead_alerts": [],
            "has_bioactivation_alert": False,
            "viewBox": {"min_x": 0, "min_y": 0, "width": 300, "height": 200},
            "canvas_width": 300,
            "canvas_height": 200,
        }


if __name__ == "__main__":
    test_smiles = "CC1=C(C(=O)N(C1=O)C)N2C=NC(=C2)C"  # Furafylline
    res = generate_molecule_layout(test_smiles)
    print(f"Generated layout for {test_smiles}:")
    print(f"  Canvas: {res['viewBox']['width']} x {res['viewBox']['height']}")
    print(f"  Atoms: {res['num_atoms']}, Bonds: {res['num_bonds']}")
    print(f"  Warhead alerts: {[a['family'] for a in res['warhead_alerts']]}")
