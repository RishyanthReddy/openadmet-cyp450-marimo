# OpenADMET: When Can We Trust a CYP Prediction?

An interactive marimo notebook about CYP3A4/CYP2D6 time-dependent inhibition: explore molecular alerts, audit model evaluation, examine electronic-descriptor and docking evidence, and select a candidate shortlist.

The submission candidate is **standalone_app.py**. Publication and the final hosted molab check are pending; older links and audit reports describe previous versions.

## Run the submission candidate

Python 3.11+ and [uv](https://docs.astral.sh/uv/) are required for the locked workflow:

```bash
uv run --script standalone_app.py
```

This resolves the adjacent `standalone_app.py.lock` and launches marimo with pinned notebook dependencies. Initial installation needs internet. Subsequent notebook interactions use embedded assets and require no runtime GPU or Beam credentials. The notebook also works when copied without the repository: it labels its embedded 100-molecule dataset fallback. The candidate-selection demonstration contains a separate 100-row TEST sample; benchmark summaries describe their original larger populations.

For development and tests:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m marimo run app.py
.venv/bin/python -m pytest -q
RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q
```

Live browser tests require Chrome (or the relevant browser-path environment variable). Training/reproduction scripts may additionally require their chemistry/ML tools; they are not needed to run the standalone notebook. The existing Beam workflows are optional and credentials belong in the ignored `.env` file.

## Five-minute path

1. Predict what a structural alert implies, then reveal the explanation.
2. Select a literature molecule; inspect alerts and their evidence. Try custom SMILES.
3. Change the model and evaluation metric. Compare random and scaffold results with uncertainty.
4. Examine the modest descriptor changes, docking geometry, a molecular pair, and a model error.
5. Change nominal alpha, click a candidate in the plot/table, and download the exact selected CSV.

## Scientific scope

- Default halos are illustrative motif weights, **not atom-level quantum calculations**. No matched alert does not establish safety.
- TDI assay labels, literature mechanisms, predictions, and docking geometry are different evidence types.
- Descriptor augmentation changes PR-AUC by +0.0101 and MCC by +0.0209 in the packaged experiment. Statistical significance and a mechanistic benefit have not been demonstrated; the full AIMNet2 cache lacks a model/conformer manifest.
- Vina uses a CPU backend; an RTX 4090 being provisioned on Beam does not imply GPU-accelerated docking. Minimum whole-ligand distance to iron does not identify a reaction site.
- Candidate predictions use TRAIN-only fitting, separate CALIBRATION labels, and TEST candidates. Estimated density weights plus ordinary BH are a simplified TxConformal-inspired demonstration. Historical 2.67% mean FDP is an empirical diagnostic, not a guarantee for an individual candidate or the displayed shortlist.

[Evidence ledger](docs/SUBMISSION_EVIDENCE_LEDGER.md), [current verification](docs/SUBMISSION_VERIFICATION.md), [submission fields](docs/JOTFORM_SUBMISSION_PACKAGE.md), and [video script](docs/VIDEO_285_SECOND_SCRIPT.md) describe this candidate. Historical documents remain for provenance and must not be used as verification of this version.

Rishyanth Reddy developed this exploration with AI assistance for code, review, and presentation. Third-party data and tools retain their own terms; a repository license has not yet been added.
