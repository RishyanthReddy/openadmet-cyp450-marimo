"""Regression checks for evidence provenance and the repaired selection artifacts."""
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from widgets.layout_engine import generate_molecule_layout
from models.txconformal_selector import conformal_fdr_select

ROOT = Path(__file__).resolve().parents[1]


def test_molecule_summary_cannot_masquerade_as_atom_quantum_values():
    layout = generate_molecule_layout('c1ccoc1', quantum_features={'fukui_radical_max': 0.99})
    assert all(a['fukui_radical'] == 0 for a in layout['atoms'])
    assert any(a['reactivity_score'] > 0 for a in layout['atoms'])
    assert all(a['score_type'] == 'Structural-alert heuristic' for a in layout['atoms'])
    assert all('not a quantum calculation' in a['score_source'] for a in layout['atoms'])
    supplied = generate_molecule_layout('c1ccoc1', atom_fukui_map={0: 0.0, 1: 0.1234})
    assert supplied['atoms'][0]['reactivity_score'] == 0
    assert supplied['atoms'][0]['score_type'] == 'Supplied radical Fukui index'
    assert supplied['atoms'][1]['fukui_radical'] == 0.1234
    assert supplied['atoms'][2]['score_type'] == 'Structural-alert heuristic'


@pytest.mark.parametrize('mapping', [{7: 1.0}, {-1: 0.0}, {0: float('nan')}, {0: float('inf')}])
def test_invalid_atom_mapping_rejected(mapping):
    with pytest.raises(ValueError, match='atom-level'):
        generate_molecule_layout('CCO', atom_fukui_map=mapping)


def test_stereoisomers_keep_distinct_identity_and_depiction():
    left = generate_molecule_layout('N[C@H](C)C(=O)O')
    right = generate_molecule_layout('N[C@@H](C)C(=O)O')
    assert left['inchikey'] != right['inchikey']
    assert {a['cip_label'] for a in left['atoms'] if a['cip_label']} != {a['cip_label'] for a in right['atoms'] if a['cip_label']}
    assert any(b['direction'] in ('BEGINWEDGE', 'BEGINDASH') for b in left['bonds'])
    assert any(b['direction'] in ('BEGINWEDGE', 'BEGINDASH') for b in right['bonds'])


@pytest.mark.parametrize('values, alpha', [([np.nan], .1), ([1.1], .1), ([-.1], .1), ([[.1]], .1), ([.1], np.inf), ([.1], -.1)])
def test_bh_rejects_malformed_inputs(values, alpha):
    with pytest.raises(ValueError):
        conformal_fdr_select(values, alpha)


def test_holdout_provenance_and_packaging_agree_exactly():
    payload = json.loads((ROOT/'data/packaged/txconformal_selection_results.json').read_text())
    meta = payload['metadata']
    for filename, digest in meta['input_sha256'].items():
        assert hashlib.sha256((ROOT/filename).read_bytes()).hexdigest() == digest
    holdout_path = ROOT/'data/packaged/txconformal_holdout.parquet'
    assert hashlib.sha256(holdout_path.read_bytes()).hexdigest() == meta['holdout_sha256']
    split = pd.read_parquet(ROOT/'data/curated/cyp_splits.parquet')
    holdout = pd.read_parquet(holdout_path).set_index('assay_inchikey')
    master = pd.read_parquet(ROOT/'data/packaged/cyp_tdi_curated.parquet').set_index('assay_inchikey')
    target = split[split['cyp3a4_is_tdi'].notna()]
    assert len(holdout) == 703
    assert set(holdout.index) == set(target.loc[target.holdout_split == 'TEST', 'assay_inchikey'])
    for key in ('grouping_parent_inchikey', 'murcko_scaffold_smiles'):
        groups = [set(target.loc[target.holdout_split == part, key].dropna()) - {''} for part in ('TRAIN', 'CALIBRATION', 'TEST')]
        assert all(not groups[a] & groups[b] for a, b in ((0,1), (0,2), (1,2)))
    # Full precision values must survive packaging rather than use incompatible OOF scores.
    np.testing.assert_array_equal(master.loc[holdout.index, 'txconformal_pvalue_cyp3a4'], holdout['weighted_pvalue'])
    sample = payload['test_candidates_sample']
    by_name = holdout.reset_index().set_index('molecule_name')
    assert len(sample) == 100
    for row in sample:
        assert row['weighted_pvalue'] == by_name.loc[row['molecule_name'], 'weighted_pvalue']
        assert row['predicted_liability_prob'] == by_name.loc[row['molecule_name'], 'predicted_liability_prob']
    result = conformal_fdr_select([row['weighted_pvalue'] for row in sample], .1)
    assert {i for i, row in enumerate(sample) if row['selected_at_alpha_0_10']} == set(result['selected_indices'])
