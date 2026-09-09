# Tier 1–Tier 2 Implementation Plan

## Bring Cheminformatics to Life — OpenADMET × marimo

**Workspace root:** `/Users/rishyanthreddy/Desktop/Marimo`  
**Runtime contract:** `marimo==0.24.0` in the current `.venv`; Molab execution is CPU-only, offline, and must not import Beam, CUDA, or a live network dependency.  
**Document status:** This is an execution specification. It describes expected changes and gates; it does not claim that any Tier 1, Tier 2, or Tier 3 card has already been implemented.

## 0. Release guardrails and execution order

Round 10’s signed-off baseline is the protected reference point:

- **98 / 100 unconditional submission-grade sign-off.**
- **186 / 186 browser assertions passed**, with zero failures or warnings.
- Standard suite: **178 passed, 8 skipped**, exit code 0.
- `marimo check` passed for both `app.py` and `standalone_app.py`.
- Strict `py_compile` passed with warnings treated as errors.
- The current generated standalone file is **192,050 bytes**, which is 187.55 KiB and below the new Tier 1 decimal budget of 200,000 bytes.

These numbers are baseline evidence from `docs/GPT56_LUNA_AUDIT_ROUND10_FINAL.md`; they are not future results. The working directory currently has no `.git` metadata, so the implementer must create an external copy or checksum manifest of the baseline before changing implementation files. Do not represent that copy as a Git tag.

### Non-negotiable invariants

1. `app.py` is the source notebook. `standalone_app.py` is generated only by `scripts/bundle_app.py`; it must never be hand-edited.
2. No PDB, PDBQT, Beam SDK, CUDA library, model weight, or external URL may be required when Molab imports or runs the standalone notebook.
3. All future scientific artifacts must be deterministic, schema-validated, provenance-bearing, and generated offline at runtime from packaged summaries only.
4. AutoDock Vina scores are docking scoring-function outputs. The UI may describe them as active-site steric-proximity proxies; it must not call them experimental binding free energies, (K_d), or proof of covalent inactivation.
5. Conformal results are empirical screening diagnostics under stated assumptions. Do not claim unconditional FDR control or perfect coverage under extreme chemical shift.
6. A failed gate stops the tier. Do not weaken a threshold to preserve a positive narrative.
7. The existing 186 browser assertions and zero-warning status are regression gates. A new test may increase the count, but a lower count, warning, console error, or network regression is a failure.

### Dependency graph

The request text refers to a 12-card plan, but the explicitly named list contains 11 cards: six Tier 1 cards, three Tier 2 cards, and two Tier 3 cards. This document formalizes every named card and does not invent an unrequested twelfth implementation card; the final dependency checklist is the cross-tier release gate.

```text
EC-T1-01 ─┐
EC-T1-02 ─┼─> EC-T1-03 ─┐
          │             ├─> EC-T1-05 ─┐
          └─> EC-T1-04 ─┘             │
                                      └─> EC-T1-06 ─> Tier 1 exit

Tier 1 exit ─> EC-T2-01 ─> EC-T2-02 ─> EC-T2-03 ─> Tier 2 exit

Tier 2 exit ─> EC-T3-01 ─> EC-T3-02 ─> submission package
```

All commands below are run from the workspace root. Unless a command explicitly says otherwise, use the repository interpreter (`.venv/bin/python`) so the pinned `marimo==0.24.0` API is the one being verified.

---

## EC-T1-01: Native `mo.accordion` Refactor for Assay Protocol and DOME Checklist

### 1. Card ID & Title

`EC-T1-01: Native mo.accordion Refactor for In Vitro Assay Protocol (Act 1) and DOME Checklist (Act 5)`

### 2. Phase / Tier

Tier 1 — native Marimo UI polish; no scientific data or model change.

### 3. Objective & Scientific / UX Rationale

Use the native Marimo disclosure primitive to keep the five-act narrative readable while preserving deep assay and reporting detail for an auditor. The Act 1 protocol is important scientific context but should not dominate the first viewport. The Act 5 DOME checklist is required evidence, but its full table should be available on demand rather than rendered as a large block in the default flow.

The refactor must preserve the distinction between an observed preincubation TDI shift and an irreversible MBI mechanism. It must also preserve the existing DOME wording, citations, and honest limitations. This is a container refactor, not permission to rewrite the science.

### 4. Target Files to Touch or Create

- `app.py` — split the Act 1 introductory prose into a concise visible section plus a native protocol accordion; replace the Act 5 raw disclosure block.
- `standalone_app.py` — generated output only, after the source passes the card test; never edit manually.
- `tests/test_tier1_ui.py` — create the shared Tier 1 UI contract test module if it does not exist; add accordion-specific assertions.
- `scripts/bundle_app.py` — do not change for this card unless the source-to-standalone extraction boundary is proven to require a narrowly scoped adjustment.

### 5. Exact Code & API Specifications

Use the `marimo==0.24.0` API exactly as follows. `items` is a dictionary from the visible item title to either Markdown text or a rendered Marimo object; `multiple=False` keeps the default narrative focused on one open panel.

```python
@app.cell
def __(mo):
    act1_protocol_content = mo.md(
        r"""
        **Assay setup.** Incubate the test compound with human liver microsomes
        (HLM) for 30 minutes in matched wells with and without NADPH. Add the
        CYP probe substrate after preincubation: midazolam for CYP3A4 or
        dextromethorphan for CYP2D6.

        **Interpretation.** A preincubation IC50 shift of approximately 1.5–2.0x
        (ΔpIC50 ≥ 0.3) is a TDI observation. It is not, by itself, proof of a
        covalent MBI mechanism. Slow reversible binding, metabolic-intermediate
        complexation, and true irreversible inactivation remain mechanistically
        distinct explanations.
        """
    )
    act1_protocol = mo.accordion(
        {
            "🔬 Deep Dive: The In Vitro Microsomal Preincubation Assay Protocol":
                act1_protocol_content,
        },
        multiple=False,
    )
    return (act1_protocol,)
```

Place `act1_protocol` immediately after the short Act 1 narrative and before the selectors/reference table. The visible Act 1 narrative must still state HLM, the 30-minute incubation, NADPH, and the probe-substrate examples so the collapsed state is not scientifically opaque.

Replace the raw `<details>` / `<summary>` block in the Act 5 limitations cell with a Markdown-backed native accordion. Do not nest a raw `<details>` element inside the new component.

```python
@app.cell
def __(mo):
    dome_content = mo.md(
        """
        | DOME axis | Implementation in the OpenADMET platform |
        | --- | --- |
        | **Data (D)** | 6,145 compounds; dual-SMILES policy; isoform-specific missingness masks; zero target leakage checks; Murcko scaffold and parent-InChIKey separation. |
        | **Optimization (O)** | Tree-based baselines and Chemprop D-MPNN with documented cross-validation and early stopping. |
        | **Model (M)** | ECFP4, graph representations, AIMNet2-NSE ΔSCF descriptors, and AutoDock Vina active-site proximity analysis. |
        | **Evaluation (E)** | Grouped Murcko 5-fold CV, 60/20/20 holdout, bootstrap intervals, and empirical covariate-shift FDP diagnostics. |
        """
    )
    act5_dome_accordion = mo.accordion(
        {
            "📋 DOME Recommendations Compliance": dome_content,
        },
        multiple=False,
    )
    return (act5_dome_accordion,)
```

Compose the existing honest limitations, the accordion, and the citations as a `mo.vstack`. Preserve the scientific limitations before the accordion and the primary data-source citations after it. The implementation may use `mo.md` with a Markdown table; it must not rely on undocumented HTML styling or a nested disclosure element.

### 6. Automated Verification Command

```bash
.venv/bin/python -m pytest -q \
  tests/test_tier1_ui.py::test_act1_protocol_uses_native_accordion \
  tests/test_tier1_ui.py::test_act5_dome_uses_native_accordion \
  tests/test_app_act1.py::test_marimo_check_app \
  tests/test_app_act5.py::test_marimo_check_app
```

The new tests must inspect the source and assert the exact item titles, `mo.accordion(` calls, and absence of `<details>` / `<summary>` in the Act 5 implementation path. If the existing test function names differ, use the actual node IDs printed by `pytest --collect-only`; do not silently broaden the command to the entire suite.

### 7. Predeclared Acceptance Gate (Done When)

- Act 1 contains exactly one native accordion item titled `🔬 Deep Dive: The In Vitro Microsomal Preincubation Assay Protocol`.
- Its content explicitly states 30-minute HLM preincubation, ± NADPH, CYP3A4/midazolam, and CYP2D6/dextromethorphan.
- Act 5 contains exactly one native accordion item titled `📋 DOME Recommendations Compliance` and retains all four DOME axes and the existing citations.
- No raw `<details>` or `<summary>` remains in the Act 5 source path.
- `marimo check app.py` exits 0 with no stderr warnings after the card is implemented.
- Opening and closing both accordions in a browser does not move the Act 1 table, Act 5 table, or adjacent AnyWidget into an overlapping or horizontally clipped layout.

### 8. Rollback Trigger

Revert the accordion source change to the baseline disclosure implementation if `marimo check` fails, the native component renders Markdown as literal broken markup, any existing Act 1/Act 5 browser assertion fails, a warning or console error appears, or the open state clips a table/AnyWidget at the tested desktop and narrow viewport widths.

---

## EC-T1-02: Native `mo.stat` KPI Metric Callout Cards

### 1. Card ID & Title

`EC-T1-02: Native mo.stat KPI Metric Callout Cards across Acts 2, 3, and 5`

### 2. Phase / Tier

Tier 1 — native Marimo UI polish; values are read from existing packaged artifacts.

### 3. Objective & Scientific / UX Rationale

Replace the verbose HTML KPI spans embedded in comparison cards with accessible, compact `mo.stat` callouts. The direction arrow is meaningful only when its semantics are explicit: higher PR-AUC/MCC is desirable, lower Brier/FDP is desirable, and a neutral ROC-AUC result must not be presented as a breakthrough.

The values below are the contract at the current default controls. If a user changes an Act 2 or Act 3 metric selector, the same cards may update dynamically, but the formatter and direction logic must remain consistent with the artifact values. Act 5’s FDP is a nearest-precomputed-α diagnostic, while its candidate count is computed from the active display sample; do not conflate the two.

### 4. Target Files to Touch or Create

- `app.py` — add native stats in the Act 2 comparison cell, Act 3 comparison cell, and Act 5 conformal selection cell.
- `standalone_app.py` — generated only by a later rebundling card.
- `tests/test_tier1_ui.py` — add static KPI specification and direction-semantics tests.
- `data/packaged/ecfp_baseline_results.json`, `data/packaged/augmented_results.json`, and `data/packaged/txconformal_selection_results.json` — read only; do not edit to make a KPI pass.

### 5. Exact Code & API Specifications

The pinned signature is:

```python
mo.stat(
    value: str | float,
    label: str | None = None,
    caption: str | None = None,
    direction: "increase" | "decrease" | None = None,
    bordered: bool = False,
    target_direction: "increase" | "decrease" | None = "increase",
)
```

Use `bordered=True` for each KPI so cards remain visually distinct in the horizontal group. The following specifications are exact at the current default controls.

#### Act 2 — LightGBM ECFP4 scaffold-shift KPIs

```python
act2_kpis = mo.hstack(
    [
        mo.stat(
            value="-0.0364",
            label="PR-AUC scaffold shift",
            caption="0.4217 random → 0.3853 scaffold; higher is better",
            direction="decrease",
            target_direction="increase",
            bordered=True,
        ),
        mo.stat(
            value="-0.0394",
            label="MCC scaffold shift",
            caption="0.3006 random → 0.2612 scaffold; higher is better",
            direction="decrease",
            target_direction="increase",
            bordered=True,
        ),
        mo.stat(
            value="9.4%",
            label="PR-AUC apparent inflation",
            caption="Random-split optimism relative to the 0.3853 scaffold value",
            direction="increase",
            target_direction="decrease",
            bordered=True,
        ),
    ],
    gap=12,
)
```

The 9.4% value is an optimism/inflation diagnostic, so an increasing value is visually undesirable (`direction="increase"`, `target_direction="decrease"`). Do not label it as a model improvement.

#### Act 3 — 2D baseline versus AIMNet2-NSE

```python
act3_kpis = mo.hstack(
    [
        mo.stat(
            value="+0.0101",
            label="PR-AUC lift",
            caption="0.4652 baseline → 0.4753 AIMNet2-NSE; grouped scaffold CV",
            direction="increase",
            target_direction="increase",
            bordered=True,
        ),
        mo.stat(
            value="+0.0209",
            label="MCC lift",
            caption="0.3298 baseline → 0.3507 AIMNet2-NSE; grouped scaffold CV",
            direction="increase",
            target_direction="increase",
            bordered=True,
        ),
        mo.stat(
            value="+0.0023",
            label="ROC-AUC change",
            caption="0.7868 baseline → 0.7891 AIMNet2-NSE; neutral within uncertainty",
            direction=None,
            target_direction="increase",
            bordered=True,
        ),
        mo.stat(
            value="-0.0031",
            label="Brier error change",
            caption="0.1573 baseline → 0.1542 AIMNet2-NSE; lower is better",
            direction="decrease",
            target_direction="decrease",
            bordered=True,
        ),
    ],
    gap=12,
)
```

The ROC-AUC card deliberately uses `direction=None`; the caption must carry the neutral interpretation. For a dynamic metric selector, use the following rule rather than hard-coding a positive arrow:

```python
delta = augmented_value - baseline_value
direction = None if metric_key == "roc_auc" and abs(delta) <= 0.005 else (
    "increase" if delta > 0 else "decrease"
)
target_direction = "decrease" if metric_key == "brier_score" else "increase"
```

#### Act 5 — active-α conformal diagnostics

At the default slider value `alpha_slider.value == 0.10`, render:

```python
act5_kpis = mo.hstack(
    [
        mo.stat(
            value=f"{_benchmark_mean_fdp:.2%}",  # 2.67% at alpha=0.10
            label="Empirical FDP",
            caption=f"α={_nearest_alpha:.2f} · 250 Monte Carlo runs · N=703; lower is better",
            direction="decrease",
            target_direction="decrease",
            bordered=True,
        ),
        mo.stat(
            value=f"{_stats.get('mean_selection_size', 30.0):.1f}",  # 30.0 at alpha=0.10
            label="Mean selected candidates",
            caption="250-run diagnostic utility; not a quality guarantee",
            direction="increase",
            target_direction="increase",
            bordered=True,
        ),
        mo.stat(
            value=f"{_target_alpha:.2f}",  # 0.10 at the default slider position
            label="Active nominal α",
            caption="Slider range 0.05–0.20; Table 5.1 and export recompute from this state",
            direction=None,
            target_direction="increase",
            bordered=True,
        ),
    ],
    gap=12,
)
```

The Act 5 code must select the nearest stored benchmark alpha exactly as the current narrative does, and must label the displayed FDP as a benchmark diagnostic when the slider is between stored alpha values. The active alpha and current `selected_count` are reactive values; a 30.0 mean selection size is not a promise that every alpha or every display sample returns 30 candidates.

### 6. Automated Verification Command

```bash
.venv/bin/python -m pytest -q \
  tests/test_tier1_ui.py::test_act2_stat_specification \
  tests/test_tier1_ui.py::test_act3_stat_specification \
  tests/test_tier1_ui.py::test_act5_stat_specification \
  tests/test_app_act2.py::test_marimo_check_app \
  tests/test_app_act3.py::test_marimo_check_app \
  tests/test_app_act5.py::test_marimo_check_app
```

### 7. Predeclared Acceptance Gate (Done When)

- All Act 2, Act 3, and Act 5 KPI cards are native `mo.stat` objects, not HTML lookalikes.
- At the default state, every value, label, caption, `direction`, and `target_direction` matches the exact specifications above.
- Act 3 ROC-AUC is visibly neutral (`direction=None`) and Act 3 Brier/FDP are visibly interpreted as lower-is-better.
- Moving the Act 5 alpha slider updates the active-alpha caption and candidate count without stale values from the previous cell execution.
- No card makes a stronger scientific claim than its caption and no confidence interval is silently dropped from the surrounding narrative.
- The card group remains readable at the existing desktop and narrow viewport test sizes.

### 8. Rollback Trigger

Revert the KPI replacement if any artifact-backed value changes, if a neutral result receives a positive direction arrow, if a lower-is-better metric is presented as higher-is-better, if a slider update leaves stale alpha text, or if the native stats introduce a Marimo warning, layout overflow, or browser-console error.

---

## EC-T1-03: Reactive Table 1.1 Selection to `BioactivationTracer` and 3D Docking

### 1. Card ID & Title

`EC-T1-03: Bi-directional Reactive mo.ui.table Row Selection in Act 1`

### 2. Phase / Tier

Tier 1 — Act 1 cross-cell state binding.

### 3. Objective & Scientific / UX Rationale

Make Table 1.1 the direct browsing surface for the ten documented literature MBIs. A row click must update the 2D `BioactivationTracer` and the Act 3 docking card from the same selected record, eliminating the current disconnect between a static table and separate dropdowns.

“Bi-directional” in this plan means that a user interaction becomes Marimo reactive state and that the state is consumed by both the molecular and docking views. `mo.ui.table.value` is read-only application state; never mutate it or depend on a private widget field. The Act 1 dropdown may remain as a compatibility/fallback selector, but the selected row must be the primary source when present.

### 4. Target Files to Touch or Create

- `app.py` — add stable lookup columns to Table 1.1, set single-row selection, expose the selected record, and make the viewer and Act 3 docking cell depend on it.
- `standalone_app.py` — generated after Tier 1 rebundling.
- `tests/test_tier1_ui.py` — add table-selection normalization, default, and downstream-binding tests.
- `tests/test_app_act1.py` and `tests/test_app_act3.py` — extend only if an existing source-contract assertion is the right home.

### 5. Exact Code & API Specifications

Define one defensive normalization helper in a small dependency cell and reuse it for both Table 1.1 and Table 5.1. It must accept the list-of-dicts behavior observed with the pinned runtime (`[]` before selection), a selected row dictionary, and a dict-of-columns/table-shaped value.

```python
def normalize_single_table_value(value: object) -> dict:
    """Return one row dict or {} for every supported empty selection shape."""
    if value is None:
        return {}

    if isinstance(value, (list, tuple)):
        if not value:
            return {}
        first = value[0]
        return dict(first) if isinstance(first, dict) else {}

    if isinstance(value, dict):
        if not value:
            return {}
        # Some table backends expose one selected row as a dict of columns.
        if all(isinstance(column_value, (list, tuple)) for column_value in value.values()):
            return {
                key: column_value[0]
                for key, column_value in value.items()
                if column_value
            }
        return dict(value)

    # Defensive support for a one-row DataFrame-like return without importing
    # a backend-specific dataframe class into the notebook.
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        try:
            records = to_dict(orient="records")
        except TypeError:
            records = to_dict()
        if isinstance(records, list) and records and isinstance(records[0], dict):
            return dict(records[0])

    return {}
```

Construct rows with stable machine-facing keys. Human-friendly labels may be changed only if the lookup keys remain unchanged.

```python
table_rows = [
    {
        "Compound": entry["name"],
        "SMILES": entry["smiles"],
        "Target CYP": entry["target_cyp"],
        "Reactive Warhead": entry.get("reactive_warhead_motif", entry.get("warhead", "N/A")),
        "PubMed ID": f"PMID: {entry.get('pubmed_id', entry.get('pmid', 'N/A'))}",
        "Evidence Level": entry.get("evidence_level", "Literature MBI"),
        "NCBI Verified": "✅ Entrez Verified" if entry.get("ncbi_verified") else "Pending",
    }
    for entry in mbi_entries
]
default_mbi_index = next(
    (index for index, row in enumerate(table_rows) if row["Compound"] == "Raloxifene"),
    0,
)
mbi_summary_table = mo.ui.table(
    data=table_rows,
    selection="single",
    initial_selection=[default_mbi_index],
    hidden_columns=["SMILES"],
    label="Table 1.1: Curated Reference Set of 10 Documented Literature Cytochrome P450 Mechanism-Based Inactivators",
)
```

The SMILES column is hidden only for presentation; it remains part of the selected record. The visible table must retain the target isoform, warhead, PubMed, evidence, and verification information.

Bind the table to downstream cells through the cell signature, not by performing imperative updates:

```python
@app.cell
def __(mbi_entries, mbi_summary_table, mbi_dropdown, normalize_single_table_value):
    selected_row = normalize_single_table_value(mbi_summary_table.value)
    selected_name = (
        selected_row.get("Compound")
        or mbi_dropdown.value
        or "Raloxifene"
    )
    selected_entry = next(
        (entry for entry in mbi_entries if entry.get("name") == selected_name),
        mbi_entries[0] if mbi_entries else {},
    )
    return selected_entry, selected_name, selected_row


@app.cell
def __(BioactivationTracer, selected_entry, mo, safe_generate_molecule_layout):
    selected_smiles = selected_entry.get("smiles", "")
    layout = safe_generate_molecule_layout(selected_smiles)
    widget = BioactivationTracer.safe_from_smiles(
        smiles=selected_smiles,
        overlay_mode="warheads",
    )
    act1_selected_widget = mo.ui.anywidget(widget)
    return act1_selected_widget, layout


@app.cell
def __(selected_name, dock_data, mo):
    # Table 1.1 is the Act 3 docking-card input. Keep all existing
    # active-site-proximity language; this only changes the selected compound.
    target_eval = next(
        (record for record in dock_data.get("docking_evaluations", [])
         if record.get("name") == selected_name),
        None,
    )
    if target_eval is None:
        docking_card = mo.callout(
            f"No cached CYP3A4 docking record is available for {selected_name}.",
            kind="warn",
        )
    else:
        result_2v0m = target_eval.get("docking_results", {}).get("2V0M", {})
        docking_card = mo.md(
            f"### CYP3A4 active-site docking: {selected_name}\n"
            f"Vina score: {result_2v0m.get('vina_affinity_kcal_mol', 'N/A')} kcal/mol "
            "(active-site proximity proxy, not Kd)  \n"
            f"Minimum HEM Fe distance: {result_2v0m.get('min_dist_to_heme_fe_angstrom', 'N/A')} Å"
        )
    return (docking_card,)
```

The existing Act 3 card can retain its full HTML/Markdown layout; the important DAG contract is that the viewer cell and docking-card cell list `selected_entry`/`selected_name` in their arguments. An empty `table.value` must resolve to Raloxifene (or the first fixture entry if the fixture is empty) without `IndexError`, `KeyError`, `TypeError`, or `NoneType` dereferences.

Remove the old Act 3-only compound control if it would create a second, contradictory source of truth. If it is retained for backward compatibility, document it as a fallback and add a browser assertion that a Table 1.1 click wins for the next render.

### 6. Automated Verification Command

```bash
.venv/bin/python -m pytest -q \
  tests/test_tier1_ui.py::test_table_value_normalizes_empty_list_and_dict \
  tests/test_tier1_ui.py::test_act1_table_uses_single_selection_and_raloxifene_default \
  tests/test_tier1_ui.py::test_act1_selection_binds_viewer_and_docking_state \
  tests/test_app_act1.py::test_marimo_check_app \
  tests/test_app_act3.py::test_marimo_check_app
```

### 7. Predeclared Acceptance Gate (Done When)

- Table 1.1 calls `mo.ui.table(..., selection="single", ...)` and has a deterministic Raloxifene initial selection.
- The selected record contains stable compound name, SMILES, target CYP, warhead, and evidence keys.
- Empty list, empty dict, `None`, and a dict-of-columns selection are all handled without an exception.
- Clicking at least two fixture rows updates the `BioactivationTracer` SMILES and the Act 3 docking card’s compound name from the same state.
- The fallback path renders the default compound when nothing is selected and never displays a blank/invalid molecule because of a transient empty value.
- The test harness records no new console error and the source cell compute path is below 10 ms for a normal ten-row selection on the pinned runtime.

### 8. Rollback Trigger

Revert the selection wiring to display-only if any empty selection produces an exception, if Table 1.1 and the docking card show different compounds after a click, if the default row is nondeterministic, if the AnyWidget receives a malformed SMILES, or if `marimo export html`/the browser audit loses selection state or emits a new warning.

---

## EC-T1-04: Reactive Table 5.1 Selection to the 2D Candidate Card

### 1. Card ID & Title

`EC-T1-04: Bi-directional Reactive mo.ui.table Row Selection in Act 5`

### 2. Phase / Tier

Tier 1 — Act 5 candidate inspection and decision-support UX.

### 3. Objective & Scientific / UX Rationale

Allow a medicinal chemist to click a prioritized candidate and immediately inspect its 2D structure, SMILES, predicted liability probability, conformal p-value, nominal alpha, and selection status. This turns Table 5.1 from a static report into a reactive inspection surface while keeping the exact weighted BH computation as the source of truth.

The table row selection is for preview only. It must not change which candidates pass weighted BH or silently convert an excluded candidate into a selected one. The export pool in EC-T1-05 is derived from the algorithmic selected-index set, not from the one-row preview selection.

### 4. Target Files to Touch or Create

- `app.py` — split the current Act 5 candidate table cell so the table object and raw rows are returned, then add a downstream 2D candidate card cell.
- `standalone_app.py` — generated by EC-T1-06; no manual edits.
- `tests/test_tier1_ui.py` — add candidate-table and empty-state tests.
- `widgets/bioactivation_tracer.py` and `widgets/layout_engine.py` — read only unless an existing safe rendering contract is insufficient; do not weaken `safe_from_smiles`.

### 5. Exact Code & API Specifications

Preserve raw numeric values in hidden or machine-facing columns. Do not make the downstream card parse formatted strings such as `"✅ Selected (p ≤ 0.0123)"`.

```python
candidate_rows = []
for index, candidate in enumerate(_candidates):
    p_value = float(candidate.get("weighted_pvalue", 1.0))
    probability = float(candidate.get("predicted_liability_prob", 0.5))
    selected = index in _selected_indices
    candidate_rows.append(
        {
            "candidate_id": candidate.get("molecule_name", f"candidate-{index:03d}"),
            "molecule_name": candidate.get("molecule_name", "Unknown"),
            "smiles": candidate.get("smiles", ""),
            "predicted_liability_prob": probability,
            "weighted_conformal_pvalue": p_value,
            "selection_status": (
                f"✅ Selected (p ≤ {_critical_cutoff:.4f})"
                if selected else "Excluded (p > BH cutoff)"
            ),
        }
    )

candidate_table = mo.ui.table(
    data=candidate_rows,
    selection="single",
    initial_selection=[0] if candidate_rows else [],
    hidden_columns=["candidate_id", "smiles"],
    label=(
        f"Table 5.1: TxConformal Prioritized Candidate Shortlist — "
        f"N={len(candidate_rows)} display candidates; nominal α={_target_alpha:.2f}"
    ),
)
```

The row keys must be available to the selection value even when hidden. Render the downstream card with the same defensive helper used in EC-T1-03:

```python
@app.cell
def __(BioactivationTracer, candidate_table, mo, safe_generate_molecule_layout):
    selected_candidate = normalize_single_table_value(candidate_table.value)
    if not selected_candidate:
        candidate_card = mo.callout(
            "Select a candidate row to inspect its 2D structure.",
            kind="info",
        )
    else:
        smiles = str(selected_candidate.get("smiles", ""))
        layout = safe_generate_molecule_layout(smiles)
        widget = BioactivationTracer.safe_from_smiles(
            smiles=smiles,
            overlay_mode="warheads",
        )
        candidate_card = mo.vstack(
            [
                mo.md(
                    "### 2D Candidate Structure\n"
                    f"**{selected_candidate.get('molecule_name', 'Unknown')}**  \n"
                    f"Predicted liability probability: "
                    f"{float(selected_candidate.get('predicted_liability_prob', 0.0)):.4f}  \n"
                    f"Weighted conformal p-value: "
                    f"{float(selected_candidate.get('weighted_conformal_pvalue', 1.0)):.4f}  \n"
                    f"Status: {selected_candidate.get('selection_status', 'Unknown')}"
                ),
                mo.ui.anywidget(widget),
            ]
        )
    return (candidate_card,)
```

If `safe_generate_molecule_layout` reports invalid input, show its safe fallback callout and retain the row’s textual data. Never call strict `BioactivationTracer.from_smiles` on user or artifact data.

### 6. Automated Verification Command

```bash
.venv/bin/python -m pytest -q \
  tests/test_tier1_ui.py::test_act5_table_uses_single_selection \
  tests/test_tier1_ui.py::test_act5_empty_selection_is_safe \
  tests/test_tier1_ui.py::test_act5_selection_renders_candidate_structure_card \
  tests/test_app_act5.py::test_marimo_check_app
```

### 7. Predeclared Acceptance Gate (Done When)

- Table 5.1 uses `selection="single"` and keeps stable raw `smiles`, probability, p-value, and status fields.
- A non-empty row click renders the corresponding candidate structure and the exact row-level scores.
- Empty list, empty dict, `None`, and an empty candidate universe render a safe callout or deterministic no-op rather than throwing.
- Slider recomputation does not leave a preview card showing a candidate that is absent from the new table.
- Preview selection has no effect on the algorithmic `_selected_indices` or download pool.
- No strict SMILES constructor is introduced in either source or generated paths.

### 8. Rollback Trigger

Revert the preview card if any candidate row renders the wrong SMILES or scores, if an empty selection causes a traceback, if changing alpha leaves stale candidate data, if preview selection mutates BH selection, or if the structure widget introduces any warning, XSS path, or browser-console error.

---

## EC-T1-05: One-Click Prioritized Candidate CSV Export

### 1. Card ID & Title

`EC-T1-05: One-Click mo.download Prioritized Candidate Pool Export in Act 5`

### 2. Phase / Tier

Tier 1 — reactive candidate export.

### 3. Objective & Scientific / UX Rationale

Give a chemist a portable, auditable CSV of the exact current weighted-BH selected pool. The download must be generated lazily from the current alpha and current candidate computation, so a slider change cannot leave the browser offering an old file with a new label.

The CSV is a decision-support export, not an experimental assay order. Its columns must preserve the values needed to reproduce the displayed selection and must carry the active nominal alpha and critical cutoff on every row.

### 4. Target Files to Touch or Create

- `app.py` — add the CSV builder and `mo.download` beneath Table 5.1 / the candidate preview.
- `standalone_app.py` — generated only by EC-T1-06.
- `tests/test_tier1_ui.py` — add CSV schema, UTF-8, active-alpha, and selected-pool tests.
- `tests/test_app_act5.py` — extend only for a source contract if useful.

### 5. Exact Code & API Specifications

Use exactly these six columns and this order:

```python
EXPORT_COLUMNS = [
    "molecule_name",
    "smiles",
    "predicted_liability_prob",
    "weighted_conformal_pvalue",
    "nominal_alpha_threshold",
    "conformal_cutoff_pstar",
]
```

Build rows from the algorithmic selected index set, not from the table preview selection. The following code is the required shape; the surrounding cell must return the download component so the active alpha is in its closure.

```python
import csv
import io


def selected_export_rows():
    rows = []
    for index, candidate in enumerate(_candidates):
        if index not in _selected_indices:
            continue
        rows.append(
            {
                "molecule_name": candidate.get("molecule_name", f"candidate-{index:03d}"),
                "smiles": candidate.get("smiles", ""),
                "predicted_liability_prob": float(
                    candidate.get("predicted_liability_prob", 0.5)
                ),
                "weighted_conformal_pvalue": float(
                    candidate.get("weighted_pvalue", 1.0)
                ),
                "nominal_alpha_threshold": float(_target_alpha),
                "conformal_cutoff_pstar": float(_critical_cutoff),
            }
        )
    return rows


def build_candidate_csv():
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=EXPORT_COLUMNS,
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    writer.writerows(selected_export_rows())
    return stream.getvalue().encode("utf-8")


def candidate_csv_filename():
    return f"txconformal_candidates_alpha_{float(_target_alpha):.2f}.csv"


candidate_download = mo.download(
    data=build_candidate_csv,
    filename=candidate_csv_filename,
    mimetype="text/csv",
    disabled=not bool(_selected_indices),
    label="Download Prioritized Non-TDI Leads (CSV)",
)
```

`data=build_candidate_csv` and `filename=candidate_csv_filename` are callables evaluated at click time. The cell must be invalidated when `alpha_slider.value`, `_candidates`, `_selected_indices`, or `_critical_cutoff` changes. Use standard UTF-8 without a BOM and LF row endings. An empty selected set should either disable the control, as above, or produce a valid header-only CSV; it must never produce stale rows from the previous alpha.

Place the component immediately below Table 5.1 and the optional 2D preview. Do not add an SDF dependency in this card; SDF is a separate future feature and would increase the portability surface.

### 6. Automated Verification Command

```bash
.venv/bin/python -m pytest -q \
  tests/test_tier1_ui.py::test_candidate_csv_has_exact_schema \
  tests/test_tier1_ui.py::test_candidate_csv_tracks_active_alpha \
  tests/test_tier1_ui.py::test_candidate_csv_is_utf8_and_round_trips \
  tests/test_app_act5.py::test_marimo_check_app
```

### 7. Predeclared Acceptance Gate (Done When)

- The Act 5 cell contains native `mo.download` with `mimetype="text/csv"`, lazy data, and lazy filename callables.
- The CSV header is exactly the six `EXPORT_COLUMNS` values in the declared order.
- At alpha 0.10, every exported row is in `_selected_indices`, has the current 0.10 threshold, and has the current critical cutoff.
- Moving alpha to 0.05 and 0.15 changes both the selected rows and filename; no row from the previous state remains unless it is selected in the new state.
- UTF-8 decoding and `csv.DictReader` round-trip without malformed rows or extra columns.
- The button is disabled or header-only when the selection is empty and never raises on a missing/empty artifact.

### 8. Rollback Trigger

Revert to a static/precomputed export if a click produces invalid CSV, the header differs from the six-column contract, the filename or row values do not track alpha, browser download generation stalls, or the browser test detects stale data after a slider change.

---

## EC-T1-06: Tier 1 Rebundling and Seam Integration Gate

### 1. Card ID & Title

`EC-T1-06: Tier 1 Automated Rebundling & Seam Integration Gate`

### 2. Phase / Tier

Tier 1 exit gate — source-to-standalone generation, tests, size, warnings, and browser seams.

### 3. Objective & Scientific / UX Rationale

Prove that the native UI additions are portable in the actual single-file artifact and have not compromised the signed-off app. This card is a gate, not a place to repair failing science or relax counts. A Tier 1 implementation is not complete until the generated file, static checks, normal suite, and browser audit agree.

### 4. Target Files to Touch or Create

- `scripts/bundle_app.py` — execute as the canonical source-to-standalone generator; modify only if a deterministic source extraction issue is demonstrated.
- `standalone_app.py` — regenerated output.
- `tests/test_tier1_ui.py`, `tests/test_phase4_seam.py`, `tests/test_devtools_audit.py` — add or update only the assertions needed to make the gates falsifiable.
- `docs/TIER1_TIER2_IMPLEMENTATION_PLAN.md` — record measured gate outputs in the implementation PR/change log, not by replacing the predeclared thresholds here.

### 5. Exact Code & API Specifications

Run the generator from the workspace root and measure the exact byte count of the generated file, not a rounded `du` value:

```bash
.venv/bin/python scripts/bundle_app.py
.venv/bin/python -c 'from pathlib import Path; p=Path("standalone_app.py"); n=p.stat().st_size; print(f"standalone_app.py: {n} bytes ({n/1024:.2f} KiB)"); assert n < 200_000, n'
```

The Tier 1 size limit is **200,000 bytes (decimal KB)**. Also print the KiB value for humans; do not substitute 200 KiB (204,800 bytes) for the gate.

Required source and generated checks:

```bash
.venv/bin/python -m marimo check app.py
.venv/bin/python -m marimo check standalone_app.py
.venv/bin/python -W error -m py_compile app.py standalone_app.py
```

The normal and browser suites must be run separately so skipped browser tests cannot hide a failure:

```bash
.venv/bin/python -m pytest -q
RUN_BROWSER_TESTS=1 PYTHONWARNINGS=error .venv/bin/python -m pytest -q -v
```

The browser command must retain the existing live-browser gate in `tests/test_devtools_audit.py`; do not mark it skipped to satisfy this card. Capture the final `passed`, `failed`, `skipped`, and warnings summary. The browser result must be at least 186 passed assertions; the standard suite must not regress from 178 passed and 8 skipped unless a documented new test increases the pass count.

Add a source-level no-runtime-dependency check that imports the standalone module in a controlled test and proves that the new UI path contains no `beam`, CUDA initialization, external HTTP client, or unguarded remote URL. Existing cached NCBI behavior is out of scope for this card but must remain unchanged.

### 6. Automated Verification Command

```bash
RUN_BROWSER_TESTS=1 PYTHONWARNINGS=error .venv/bin/python -m pytest -q -v
```

The card is not green unless this command exits 0, reports at least 186 passed browser assertions, and reports zero warnings. Run the normal suite, `marimo check`, compile, and the exact byte assertion above as companion commands.

### 7. Predeclared Acceptance Gate (Done When)

- `scripts/bundle_app.py` regenerates `standalone_app.py` without a manual patch.
- `standalone_app.py` is smaller than **200,000 bytes decimal**.
- The browser suite has **at least 186 passed assertions**, zero failures/errors, zero console warnings, zero unhandled console errors, and no new external network dependency.
- The normal suite exits 0 with no regression from the baseline 178 passed / 8 skipped profile.
- Both `marimo check` invocations and strict `py_compile` exit 0 with empty warning output.
- The generated file contains the accordion, stats, table selection, candidate preview, and download source paths exactly once where the bundler expects them.

### 8. Rollback Trigger

Restore the known-good source/bundle snapshot immediately if the generated file is at or above 200,000 bytes, browser passes fall below 186, any test fails, any warning or console error appears, `marimo check` or strict compile fails, or the standalone path attempts a network/GPU operation. Do not proceed to Tier 2 with a failed Tier 1 gate.

---

## EC-T2-01: Beam Cloud CYP2D6 Structural Docking Pipeline

### 1. Card ID & Title

`EC-T2-01: Beam Cloud CYP2D6 Structural Docking Pipeline for 3TBG and 4WNW`

### 2. Phase / Tier

Tier 2 — controlled offline scientific extension; gated Beam compute with local reproducibility.

### 3. Objective & Scientific / UX Rationale

Add a dual-conformation CYP2D6 structural comparison to complement the existing CYP3A4 2V0M/1TQN analysis. CYP2D6 is the relevant isoform for the Paroxetine reference compound and has a narrower, negatively charged pocket in which Asp301 is a useful contact-validation residue.

This is a precomputed structural-proximity experiment, not a new runtime model. Docking all ten reference MBIs against both CYP2D6 structures is an exploratory panel; only Paroxetine is isoform-matched in the fixture. Every result must retain the original `target_cyp`, and a docking score must never be presented as a measured (K_d) or a mechanistic proof.

### 4. Target Files to Touch or Create

- `spikes/docking_cyp2d6.py` — create a deterministic local preparation/parser and artifact writer; keep the existing CYP3A4 spike untouched.
- `spikes/beam_cyp2d6_docking.py` — create the Beam entrypoint, or combine it with the spike only if the local/remote boundary remains testable.
- `data/raw/pdb/3TBG.pdb` and `data/raw/pdb/4WNW.pdb` — frozen input files or a separately documented acquisition directory.
- `data/raw/pdb/cyp2d6_manifest.json` — URLs, retrieval time, PDB SHA-256, header resolution, and selected chain.
- `data/processed/pdbqt/cyp2d6/` — cleaned receptor PDBQT, ligand PDBQT, pose-1 PDBQT, and logs; never embed this directory in Molab.
- `data/packaged/cyp2d6_docking_results.json` — expected packaged summary artifact, created only after all gates pass.
- `docs/CYP2D6_DOCKING_REPORT.md` — generated scientific report with explicit failures and provenance.
- `tests/test_cyp2d6_docking.py` — deterministic schema, geometry, and raw-PDBQT reproducibility tests.

### 5. Exact Code & API Specifications

#### Input freezing and receptor preparation

1. Freeze the ten canonical entries from `data/fixtures/literature_mbi_reference_set.json`; compute a canonical JSON SHA-256 over sorted entries and store it in artifact metadata. Do not fetch SMILES from PubChem or another live service.
2. Acquire `https://files.rcsb.org/download/3TBG.pdb` and `https://files.rcsb.org/download/4WNW.pdb` once during the controlled preparation step. Record each byte-level SHA-256 in `cyp2d6_manifest.json`. Beam receives these frozen files through its input payload/volume; it must not depend on a network fetch during the job.
3. Inspect the PDB header and fail closed if the expected chain or HEM residue is absent. Start with chain `A`, but record the validated chain in the manifest rather than assuming it silently.
4. Keep `ATOM` records from the selected chain and `HETATM` records for the selected-chain `HEM` cofactor only. Exclude waters, crystallization ligands, salts, and other heteroatoms unless a method review explicitly adds them. Keep the complete HEM ring and catalytic Fe atom; do not reduce HEM to Fe alone.
5. Resolve alternate locations deterministically: retain blank or `A` altloc, choose the highest-occupancy record when multiple candidates remain, and record discarded altloc identifiers. Remove hydrogens before receptor PDBQT generation unless the chosen preparation tool explicitly adds them; do not use a mixed protonation policy.
6. Protonate protein residues at pH 7.4 using the declared preparation tool in the Beam image, record the tool/version, and preserve HEM/Fe parameters. If the tool cannot prepare a residue or HEM consistently, mark the receptor `failed` and stop integration rather than silently assigning zero charges.

The local preparation function must expose the Fe coordinate and grid contract:

```python
import math

GRID_SIZE_ANGSTROM = (22.0, 22.0, 22.0)
VINA_VERSION = "1.2.7"
VINA_SEED = 42
VINA_EXHAUSTIVENESS = 8


def grid_for_heme_fe(fe_coord: tuple[float, float, float]) -> dict:
    if len(fe_coord) != 3 or not all(math.isfinite(float(x)) for x in fe_coord):
        raise ValueError("Invalid catalytic HEM Fe coordinate")
    return {
        "center_angstrom": [round(float(x), 3) for x in fe_coord],
        "size_angstrom": list(GRID_SIZE_ANGSTROM),
    }
```

The grid is centered on each receptor’s own HEM Fe; it is not a single coordinate copied from CYP3A4. The default box is exactly 22.0 × 22.0 × 22.0 Å. A different size is allowed only if an inspected active-site geometry report documents the reason, the measured alternative, and a new predeclared test threshold.

#### Deterministic ligand preparation

Use the current fixture SMILES, RDKit ETKDGv3 with `randomSeed=42`, explicit hydrogens, and MMFF94 minimization. Fail a ligand with a machine-readable error if embedding or force-field optimization fails; never substitute a guessed conformer.

```python
mol = Chem.MolFromSmiles(smiles)
if mol is None:
    raise ValueError(f"Invalid fixture SMILES for {compound_name}")
mol = Chem.AddHs(mol)
etkdg = AllChem.ETKDGv3()
etkdg.randomSeed = 42
if AllChem.EmbedMolecule(mol, etkdg) != 0:
    raise RuntimeError(f"ETKDGv3 failed for {compound_name}")
if AllChem.MMFFOptimizeMolecule(mol, maxIters=500) != 0:
    raise RuntimeError(f"MMFF94 failed for {compound_name}")
ligand_setup = MoleculePreparation().prepare(mol)[0]
pdbqt_text, is_ok, error = PDBQTWriterLegacy.write_string(ligand_setup)
if not is_ok:
    raise RuntimeError(f"Meeko failed for {compound_name}: {error}")
```

Record RDKit and Meeko versions, protonation/charge policy, ligand PDBQT SHA-256, and the conformer seed in each run’s provenance.

#### AutoDock Vina execution on Beam RTX 4090

Use a fixed executable version and explicit arguments. The command for each receptor/ligand pair is:

```bash
/opt/vina/bin/vina \
  --receptor /inputs/pdbqt/3TBG_receptor.pdbqt \
  --ligand /inputs/pdbqt/ligand_paroxetine.pdbqt \
  --center_x X.XXX --center_y Y.YYY --center_z Z.ZZZ \
  --size_x 22.0 --size_y 22.0 --size_z 22.0 \
  --exhaustiveness 8 \
  --num_modes 9 \
  --seed 42 \
  --out /outputs/pdbqt/docked_3TBG_paroxetine.pdbqt \
  --log /outputs/logs/docked_3TBG_paroxetine.log
```

Substitute the Fe-centered coordinates from the receptor manifest; do not leave `X.XXX` literals in an executed job. AutoDock Vina is generally CPU-bound even when the Beam worker has an RTX 4090. Request the RTX 4090 as the controlled Beam hardware, record `gpu_device="RTX4090"`, and record `vina_compute_backend="CPU process on RTX4090 worker"` unless a separately validated CUDA-enabled Vina build is used. Do not claim GPU acceleration merely because the worker has a GPU.

The Beam wrapper follows the existing repository style:

```python
from beam import Image, function

image = Image(
    python_version="python3.11",
    python_packages=[
        "numpy",
        "rdkit",
        "meeko",
        "vina==1.2.7",
    ],
)


@function(
    gpu=["RTX4090"],
    image=image,
    memory="16Gi",
    cpu=8,
    timeout=900,
)
def run_cyp2d6_docking_remote(frozen_inputs: dict) -> dict:
    # No URL fetch here. Read frozen PDB/SMILES inputs, run the same
    # deterministic preparation and Vina command, and return JSON-safe data.
    return run_docking_pipeline(frozen_inputs)
```

The local path must call the same pure preparation/parser functions with a fixture directory, so tests do not need Beam credentials. The remote wrapper may be invoked only after the local dry-run validates the schema and command line.

#### Required JSON artifact schema

Write JSON with `allow_nan=False` and the following shape. The names may be extended, but these fields are mandatory.

```json
{
  "schema_version": "cyp2d6_docking.v1",
  "metadata": {
    "task_id": "EC-T2-01",
    "title": "CYP2D6 dual-isoform structural docking",
    "generated_at_utc": "<measured ISO-8601 timestamp>",
    "source_fixture": "data/fixtures/literature_mbi_reference_set.json",
    "source_fixture_sha256": "<sha256>",
    "pdb_ids": ["3TBG", "4WNW"],
    "expected_compounds": 10,
    "expected_runs": 20,
    "completed_runs": "<measured integer>",
    "vina_version": "1.2.7",
    "seed": 42,
    "exhaustiveness": 8,
    "grid_size_angstrom": [22.0, 22.0, 22.0],
    "execution": {
      "provider": "Beam",
      "gpu_device": "RTX4090",
      "vina_compute_backend": "CPU process on RTX4090 worker",
      "runtime_seconds": "<measured float>"
    }
  },
  "receptors": {
    "3TBG": {
      "source_url": "https://files.rcsb.org/download/3TBG.pdb",
      "source_pdb_sha256": "<sha256>",
      "resolution_angstrom": "<header value>",
      "chain": "A",
      "retained_heteroatoms": ["HEM"],
      "removed_waters": true,
      "alternate_location_policy": "blank_or_A_highest_occupancy",
      "heme_fe_coord_angstrom": ["<x>", "<y>", "<z>"],
      "grid_center_angstrom": ["<x>", "<y>", "<z>"],
      "grid_size_angstrom": [22.0, 22.0, 22.0],
      "prepared_pdbqt_sha256": "<sha256>",
      "preparation_tool": "<measured tool and version>"
    },
    "4WNW": {
      "source_url": "https://files.rcsb.org/download/4WNW.pdb",
      "source_pdb_sha256": "<sha256>",
      "resolution_angstrom": "<header value>",
      "chain": "A",
      "retained_heteroatoms": ["HEM"],
      "removed_waters": true,
      "alternate_location_policy": "blank_or_A_highest_occupancy",
      "heme_fe_coord_angstrom": ["<x>", "<y>", "<z>"],
      "grid_center_angstrom": ["<x>", "<y>", "<z>"],
      "grid_size_angstrom": [22.0, 22.0, 22.0],
      "prepared_pdbqt_sha256": "<sha256>",
      "preparation_tool": "<measured tool and version>"
    }
  },
  "docking_evaluations": [
    {
      "name": "Paroxetine",
      "smiles": "<fixture SMILES>",
      "target_cyp": "CYP2D6",
      "warhead": "<fixture value>",
      "ligand_pdbqt_sha256": "<sha256>",
      "docking_results": {
        "3TBG": {
          "status": "ok",
          "vina_affinity_kcal_mol": "<float>",
          "pose_1_pdbqt_path": "data/processed/pdbqt/cyp2d6/docked_3TBG_paroxetine.pdbqt",
          "pose_1_pdbqt_sha256": "<sha256>",
          "nearest_heavy_atom": "<atom label>",
          "min_dist_to_heme_fe_angstrom": "<float>",
          "reactive_sulfur_dist_angstrom": null,
          "asp301_contact": {
            "residue": "ASP301",
            "ligand_atom": "<basic amine atom>",
            "distance_angstrom": "<float or null>",
            "contact_type": "proximity_only"
          },
          "active_site_steric_proximity_le_5A": "<boolean>",
          "docking_latency_sec": "<float>",
          "error": null
        },
        "4WNW": {
          "status": "ok",
          "vina_affinity_kcal_mol": "<float>",
          "pose_1_pdbqt_path": "data/processed/pdbqt/cyp2d6/docked_4WNW_paroxetine.pdbqt",
          "pose_1_pdbqt_sha256": "<sha256>",
          "nearest_heavy_atom": "<atom label>",
          "min_dist_to_heme_fe_angstrom": "<float>",
          "reactive_sulfur_dist_angstrom": null,
          "asp301_contact": {
            "residue": "ASP301",
            "ligand_atom": "<basic amine atom>",
            "distance_angstrom": "<float or null>",
            "contact_type": "proximity_only"
          },
          "active_site_steric_proximity_le_5A": "<boolean>",
          "docking_latency_sec": "<float>",
          "error": null
        }
      },
      "provenance": {
        "rdkit_etkdgv3_seed": 42,
        "mmff_variant": "MMFF94",
        "meeko_version": "<measured>",
        "source_pdb_ids": ["3TBG", "4WNW"]
      }
    }
  ]
}
```

The real artifact must contain ten `docking_evaluations` entries and both receptor keys for every entry. If a pair fails, its receptor result must be `{ "status": "failed", "error": {"type": "...", "message": "..."} }`; it may not be omitted. Use `null` for a scientifically inapplicable sulfur distance. The pose-1 PDBQT may remain outside the Molab bundle, but its path and SHA-256 must be recorded.

For the Paroxetine inspection, calculate the nearest distance from its protonated/basic amine atom to Asp301 OD1/OD2 in MODEL 1 when those atoms are present. Report it as a geometric proximity/contact observation. If it is not within the predeclared contact threshold, record the negative finding; never rotate, filter, or hand-pick a pose to force a salt-bridge narrative.

### 6. Automated Verification Command

```bash
.venv/bin/python -m pytest -q \
  tests/test_cyp2d6_docking.py::test_cyp2d6_artifact_schema_and_cardinality \
  tests/test_cyp2d6_docking.py::test_receptor_manifest_has_sha256_and_fe_centered_grid \
  tests/test_cyp2d6_docking.py::test_all_twenty_runs_have_explicit_status \
  tests/test_cyp2d6_docking.py::test_paroxetine_asp301_observation_is_not_overclaimed
```

Run the Beam job only after this local command and the local dry-run parser pass. The remote command must be recorded in the report with the Beam job ID, image digest, and hardware result; do not paste credentials into the repository.

### 7. Predeclared Acceptance Gate (Done When)

- Both source PDB files have recorded byte-level SHA-256 values, validated resolutions, chain policy, alternate-location policy, water policy, and HEM/Fe coordinates.
- All ten fixture compounds are prepared with ETKDGv3 seed 42, MMFF94, and Meeko; failures are explicit rather than silently dropped.
- The Vina command uses version 1.2.7, seed 42, exhaustiveness 8, and a declared Fe-centered 22 Å cube for both receptors unless a documented geometry review changes it.
- The Beam job is scheduled on `gpu=["RTX4090"]`, but the report distinguishes worker hardware from Vina’s actual compute backend.
- The expected artifact has 20 explicit receptor-ligand result objects, finite numeric fields or `null`, no JSON NaN/Infinity, and deterministic provenance.
- Paroxetine’s Asp301 observation is present as a measured proximity result or a machine-readable not-measurable/failed result; no salt-bridge or binding-affinity claim is made without geometry.

### 8. Rollback Trigger

Abort the Tier 2 integration and retain the Tier 1 baseline if either PDB checksum changes unexpectedly, chain/HEM/Fe preparation is ambiguous, any ligand cannot be deterministically prepared, more than zero runs are silently missing, any numeric field is NaN/Infinity, the raw PDBQT cannot reproduce the artifact, the Asp301 validation is forced rather than measured, the Beam image cannot pin Vina 1.2.7, or the generated payload exceeds the Tier 2 asset budget.

---

## EC-T2-02: Dual-Isoform Enzymology Card and Embedded Assets

### 1. Card ID & Title

`EC-T2-02: Dual-Isoform CYP2D6 Enzymology Card and Embedded Assets Integration in Act 3`

### 2. Phase / Tier

Tier 2 — offline asset integration and Act 3 narrative extension.

### 3. Objective & Scientific / UX Rationale

Expose the validated CYP2D6 summary alongside the existing CYP3A4 active-site card so the notebook demonstrates isoform-aware enzymology without requiring a GPU or network at runtime. The UI must distinguish:

- CYP3A4 structures `2V0M` and `1TQN` already in the baseline;
- CYP2D6 structures `3TBG` and `4WNW` added by EC-T2-01;
- Vina scoring-function output versus heme-Fe/Asp301 geometric proximity;
- the Paroxetine isoform-matched observation versus the exploratory docking of the other fixture compounds.

### 4. Target Files to Touch or Create

- `models/embedded_assets.py` — generated by `scripts/package_assets.py`; add a gzip/base64 loader for the JSON summary only.
- `scripts/package_assets.py` — package `data/packaged/cyp2d6_docking_results.json` and record its SHA-256.
- `scripts/bundle_app.py` — inline the new summary asset through the existing generated-assets path.
- `app.py` — import the loader in the dependency cell and add an Act 3 dual-isoform card.
- `standalone_app.py` — generated output only.
- `tests/test_cyp2d6_ui.py` — create UI/source/loader tests.
- `docs/CYP2D6_DOCKING_REPORT.md` — link or cite the artifact provenance without embedding raw structures.

### 5. Exact Code & API Specifications

The package loader must follow the existing `models/embedded_assets.py` pattern:

```python
def load_cyp2d6_docking_results() -> dict:
    primary = BASE_DIR / "data" / "packaged" / "cyp2d6_docking_results.json"
    if primary.exists():
        return json.loads(primary.read_text(encoding="utf-8"))
    if not _CYP2D6_DOCKING_GZIP_B64:
        return {
            "schema_version": "cyp2d6_docking.v1",
            "metadata": {"status": "unavailable"},
            "docking_evaluations": [],
        }
    return json.loads(
        gzip.decompress(base64.b64decode(_CYP2D6_DOCKING_GZIP_B64))
        .decode("utf-8")
    )
```

The packaged path must be verified before it is embedded; a missing or schema-invalid artifact must not be converted into a misleading empty success. In standalone mode, the fallback loader must return a clear `mo.callout` with `kind="warn"` and preserve the existing CYP3A4 card.

Add the loader to the first dependency cell and return it from that cell. In Act 3, render one native summary card and one detail card:

```python
cyp2d6_isoform = mo.ui.dropdown(
    options=["3TBG", "4WNW"],
    value="3TBG",
    label="CYP2D6 crystallographic conformation:",
)

def cyp2d6_card(data: dict, pdb_id: str, compound_name: str):
    evaluations = data.get("docking_evaluations", [])
    evaluation = next(
        (item for item in evaluations if item.get("name") == compound_name),
        None,
    )
    result = (evaluation or {}).get("docking_results", {}).get(pdb_id, {})
    if result.get("status") != "ok":
        return mo.callout(
            f"CYP2D6 {pdb_id} docking is unavailable for {compound_name}; "
            f"status={result.get('status', 'missing')}",
            kind="warn",
        )
    return mo.md(
        f"""
        **CYP2D6 {pdb_id} — {compound_name}**  
        Vina score: `{float(result['vina_affinity_kcal_mol']):.2f} kcal/mol`  
        *(scoring-function output, not Kd)*  
        Nearest heavy atom to HEM Fe: `{result.get('min_dist_to_heme_fe_angstrom')} Å`  
        Asp301 observation: `{result.get('asp301_contact')}`  
        Active-site proximity proxy (≤5 Å): `{result.get('active_site_steric_proximity_le_5A')}`
        """
    )


@app.cell
def __(cyp2d6_docking_results, cyp2d6_isoform, selected_name):
    act3_cyp2d6_card = cyp2d6_card(
        cyp2d6_docking_results,
        cyp2d6_isoform.value,
        selected_name,
    )
    return (act3_cyp2d6_card,)
```

The implementation may use `mo.stat` from EC-T1-02 for the current Fe distance and a compact `mo.ui.table` for the two conformations, but it must not embed pose files or raw PDB text. The card must state that Paroxetine is the fixture’s CYP2D6-matched example and that the other nine compounds are an exploratory cross-panel.

Update `scripts/bundle_app.py` only through the same deterministic asset extraction pattern used for existing gzip/base64 payloads. The raw JSON, PDB, PDBQT, and logs stay outside `standalone_app.py`; only the summary needed to render the card is embedded.

### 6. Automated Verification Command

```bash
.venv/bin/python -m pytest -q \
  tests/test_cyp2d6_ui.py::test_cyp2d6_loader_is_offline_first \
  tests/test_cyp2d6_ui.py::test_dual_isoform_card_labels_scores_as_proxies \
  tests/test_cyp2d6_ui.py::test_standalone_does_not_embed_raw_pdb_or_pdbqt \
  tests/test_app_act3.py::test_marimo_check_app
```

### 7. Predeclared Acceptance Gate (Done When)

- The loader works from the packaged JSON and from the embedded compressed fallback with zero network requests.
- Act 3 exposes both `3TBG` and `4WNW`, preserves the selected compound, and renders status/error explicitly for every unavailable pair.
- The card labels Vina values as scoring-function outputs and distances as active-site proximity observations; no `Kd`, free-energy, or covalent-mechanism overclaim appears.
- Paroxetine is identified as the isoform-matched CYP2D6 example; the original `target_cyp` values remain visible or recoverable.
- No raw PDB/PDBQT/trajectory/weight bytes enter the standalone bundle.
- A missing asset degrades to a truthful warning while the baseline Act 3 content remains usable.

### 8. Rollback Trigger

Remove the new Act 3 card and restore the baseline bundle if the embedded loader makes a network call, raw structural files enter the bundle, the card renders missing results as zeros, a score is labeled as affinity/Kd, the CYP3A4 narrative changes unintentionally, or the asset package makes the size gate fail.

---

## EC-T2-03: Tier 2 Rebundling and Automated Docking Seam Gate

### 1. Card ID & Title

`EC-T2-03: Tier 2 Rebundling & Automated Docking Seam Gate`

### 2. Phase / Tier

Tier 2 exit gate — artifact reproducibility, offline integration, bundle size, and full regression.

### 3. Objective & Scientific / UX Rationale

Establish that the Beam-generated CYP2D6 data is real, reproducible, complete, and safely consumable by the single-file notebook. This gate separates a valid structural experiment from a visually plausible but untraceable JSON injection.

### 4. Target Files to Touch or Create

- `data/packaged/cyp2d6_docking_results.json` and `docs/CYP2D6_DOCKING_REPORT.md` — expected outputs from EC-T2-01.
- `data/processed/pdbqt/cyp2d6/` — raw pose/receptor files used by the reproducibility parser.
- `models/embedded_assets.py`, `scripts/package_assets.py`, `scripts/bundle_app.py`, and generated `standalone_app.py`.
- `tests/test_cyp2d6_docking.py`, `tests/test_cyp2d6_ui.py`, `tests/test_phase4_seam.py`, and `tests/test_devtools_audit.py`.

### 5. Exact Code & API Specifications

The gate must validate all of the following programmatically:

```python
assert artifact["schema_version"] == "cyp2d6_docking.v1"
assert set(artifact["receptors"]) == {"3TBG", "4WNW"}
evaluations = artifact["docking_evaluations"]
assert len(evaluations) == 10
assert all(set(item["docking_results"]) == {"3TBG", "4WNW"} for item in evaluations)
assert artifact["metadata"]["expected_runs"] == 20

for item in evaluations:
    for pdb_id in ("3TBG", "4WNW"):
        result = item["docking_results"][pdb_id]
        assert result["status"] in {"ok", "failed"}
        if result["status"] == "ok":
            for key in (
                "vina_affinity_kcal_mol",
                "min_dist_to_heme_fe_angstrom",
                "active_site_steric_proximity_le_5A",
            ):
                assert result[key] is not None
            assert math.isfinite(float(result["vina_affinity_kcal_mol"]))
            assert math.isfinite(float(result["min_dist_to_heme_fe_angstrom"]))
        else:
            assert result.get("error", {}).get("message")
```

The raw PDBQT parser must independently read MODEL 1, ignore hydrogens, calculate minimum heavy-atom-to-Fe distance, parse the first Vina affinity, and compare those values to the JSON within the declared rounding policy. It must verify every available pose file across 10 compounds × 2 receptors, not just Paroxetine.

Run the generated bundle through the same offline loader used by Molab and assert that the embedded summary is byte-for-byte equivalent after JSON parse to the packaged summary (or equivalent under an explicitly documented canonical JSON serialization). Scan the standalone bytes for `3TBG`, `4WNW`, and the schema version, and for absence of raw PDB `ATOM`/`HETATM` blocks and PDBQT pose records.

The Tier 2 asset budget is strict: retain the Tier 1 `< 200,000` decimal-byte bundle limit if the measured compressed summary permits it. If a scientifically required summary cannot fit, stop and ask for an explicit scope decision; do not silently raise the limit inside this card.

### 6. Automated Verification Command

```bash
.venv/bin/python -m pytest -q \
  tests/test_cyp2d6_docking.py \
  tests/test_cyp2d6_ui.py \
  tests/test_phase4_seam.py \
  tests/test_app_act3.py
```

After that command passes, run the full browser gate:

```bash
RUN_BROWSER_TESTS=1 PYTHONWARNINGS=error .venv/bin/python -m pytest -q -v
```

### 7. Predeclared Acceptance Gate (Done When)

- Ten compounds × two receptors are present with an explicit `ok` or `failed` status for all 20 combinations.
- No NaN, Infinity, missing error message, or silently omitted record exists.
- Raw PDBQT parsing reproduces every packaged affinity and distance field under the declared rounding policy.
- Receptor manifests contain PDB SHA-256 values, Fe-centered grid values, and preparation metadata.
- Paroxetine/Asp301 inspection is present, measured, and phrased as proximity rather than proof of binding or inactivation.
- The bundled loader is offline-first and raw PDB/PDBQT bytes are not embedded.
- `standalone_app.py` remains under 200,000 bytes decimal, `marimo check` and strict compile pass, and the browser suite remains at least 186 passed with zero warnings/errors.

### 8. Rollback Trigger

Do not promote the CYP2D6 artifact or regenerate the submission bundle if any of the 20 statuses is missing, raw-parser values disagree, the artifact contains non-finite numbers, the bundle exceeds 200,000 bytes, the standalone loader differs from the packaged artifact, or any full-suite/browser warning or error appears. Restore the last Tier 1 bundle and keep the docking output in an unintegrated experiment directory.

---

## EC-T3-01: Molab Cloud Gist Staging and Cold-Boot SLA

### 1. Card ID & Title

`EC-T3-01: Molab Cloud Gist Staging & Cold-Boot SLA Verification (<10 s)`

### 2. Phase / Tier

Tier 3 — staging and operational verification; external promotion remains an approval-gated action.

### 3. Objective & Scientific / UX Rationale

Verify the actual artifact that a judge will open, not only the local notebook. The staged Gist must be immutable, correspond to the measured standalone SHA-256, boot without Beam/GPU/network requirements, and meet the under-10-second cold-boot SLA on repeated fresh sessions.

Do not fabricate a Gist URL, Molab URL, account name, or credential. The implementer records the real values only after the authorized staging action and keeps secrets out of the repository.

### 4. Target Files to Touch or Create

- `scripts/verify_molab_cold_boot.py` — create a local/headless harness that records process start, first reachable page, Marimo-ready marker, first Act 1 table, and any network/console events.
- `tests/test_molab_staging.py` — create manifest/SLA/assertion tests that do not require credentials in ordinary CI.
- `docs/MOLAB_STAGING_REPORT.md` — create a measured report template with Gist revision, standalone SHA-256, run timestamps, durations, request allowlist, and screenshots.
- `standalone_app.py` — input artifact only; do not edit manually.
- An external Gist revision — created only by the user/authorized release operator after local gates pass.

### 5. Exact Code & API Specifications

Before staging, compute and record the artifact identity:

```bash
.venv/bin/python -c 'from pathlib import Path; import hashlib; p=Path("standalone_app.py"); print(hashlib.sha256(p.read_bytes()).hexdigest())'
```

The staging operator may create a Gist with the authenticated GitHub CLI only after approval:

```bash
gh gist create standalone_app.py \
  --public \
  --desc "OpenADMET x marimo competition staging artifact <version>"
```

Replace the description placeholder with the actual release identifier; never put a token in a shell history captured by the repository. Record the returned Gist URL and revision in the staging report, then verify that the downloaded file’s SHA-256 equals the local value. If the Molab UI provides a canonical “open from Gist” flow, use that exact URL from the UI rather than inventing a query-string format.

The cold-boot harness must run fresh processes/sessions and emit JSON like:

```json
{
  "artifact_sha256": "<sha256>",
  "gist_revision": "<measured revision>",
  "runs": [
    {
      "run": 1,
      "process_start_utc": "<timestamp>",
      "first_page_ms": "<measured>",
      "marimo_ready_ms": "<measured>",
      "act1_table_ready_ms": "<measured>",
      "external_requests": [],
      "gpu_initialization_detected": false,
      "console_errors": [],
      "console_warnings": []
    }
  ],
  "slo": {
    "threshold_seconds": 10.0,
    "pass": "<all required runs under threshold>"
  }
}
```

Run the local timing harness with a finite timeout; the exact command to implement is:

```bash
.venv/bin/python scripts/verify_molab_cold_boot.py \
  --artifact standalone_app.py \
  --runs 5 \
  --timeout-seconds 10 \
  --output docs/molab_cold_boot_results.json
```

The harness must distinguish server process startup from the first usable notebook state and must fail if it sees a remote request, Beam/CUDA import, uncaught exception, warning, or console error. For the hosted Molab check, repeat the same five-run protocol in fresh browser sessions and append the hosted measurements; a local pass is necessary but not sufficient evidence of hosted performance.

### 6. Automated Verification Command

```bash
.venv/bin/python -m pytest -q \
  tests/test_molab_staging.py::test_staging_manifest_has_artifact_identity \
  tests/test_molab_staging.py::test_cold_boot_report_has_five_runs_and_under_ten_seconds \
  tests/test_molab_staging.py::test_cold_boot_report_has_no_external_requests_or_gpu
```

The hosted checks are operational evidence, not a substitute for this deterministic manifest test.

### 7. Predeclared Acceptance Gate (Done When)

- The staged file’s SHA-256 equals the locally measured `standalone_app.py` SHA-256 and the Gist revision is recorded.
- Five fresh local runs and five fresh hosted Molab sessions reach a usable Act 1 table in under 10.0 seconds each; report median and p95.
- All runs record zero external requests beyond the documented local/Molab transport, zero GPU initialization, zero console errors, and zero warnings.
- The hosted notebook supports at least one Table 1.1 selection, one Act 5 alpha change, and one CSV download without a refresh or runtime exception.
- The report contains timestamps, browser/runtime versions, artifact identity, and a reproducible procedure; it contains no credential or token.

### 8. Rollback Trigger

Do not promote or submit the staged Gist if any run reaches the usable state at 10.0 seconds or later, if p95 is not below 10 seconds, if the Gist SHA differs, if any external request/GPU initialization/console warning is observed, or if the hosted app cannot exercise the required interactions. Keep the prior known-good staging revision live and mark the candidate revision as rejected rather than deleting it.

---

## EC-T3-02: 285-Second Video and JotForm Submission Package

### 1. Card ID & Title

`EC-T3-02: Final 285-Second Video Walkthrough Script & JotForm Submission Package`

### 2. Phase / Tier

Tier 3 — final communication and submission packaging.

### 3. Objective & Scientific / UX Rationale

Make the first five minutes communicate both scientific credibility and Marimo reactivity. The edit must show the signed-off claims and the new UI behavior without overclaiming docking or conformal guarantees. The script is timed to exactly 285 seconds (4:45), leaving a five-second sign-off margin below the 300-second ceiling.

### 4. Target Files to Touch or Create

- `docs/VIDEO_285_SECOND_SCRIPT.md` — create the timestamped storyboard and final voiceover.
- `docs/JOTFORM_SUBMISSION_PACKAGE.md` — create a submission-field checklist and link-verification record; never store credentials.
- `tests/test_submission_package.py` — create duration, segment-sum, required-feature, and placeholder checks.
- `artifacts/video/final_submission.mp4` — external/rendered output, not required in the code repository unless the competition rules explicitly require it.
- `docs/MOLAB_STAGING_REPORT.md` — source for the final verified Molab/Gist links and measured cold-boot claim.

### 5. Exact Code & API Specifications

The script must use these exact segments and durations:

| Timecode | Duration | Segment | Required visual and voiceover beats |
| --- | ---: | --- | --- |
| 0:00–0:45 | 45 s | Problem and Bathtub Audit | Introduce CYP450 TDI/MBI risk; show Act 2 random-vs-scaffold PR-AUC/MCC collapse and zero-leakage framing. |
| 0:45–2:00 | 75 s | AnyWidget and metabolic halos | Click Table 1.1; show the `BioactivationTracer` update, warhead overlays, malformed-SMILES safe fallback, and the native protocol disclosure. |
| 2:00–2:45 | 45 s | Physics and enzymology | Show Act 3 AIMNet2-NSE PR-AUC/MCC lift, neutral ROC-AUC, Brier improvement, CYP3A4 proximity proxy, and CYP2D6 3TBG/4WNW card if Tier 2 passes. |
| 2:45–3:30 | 45 s | Medicinal chemistry steering | Show an MMP activity cliff and one real out-of-fold error diagnosis; state that the MMP artifact is an OpenADMET label-shift catalog. |
| 3:30–4:15 | 45 s | TxConformal decision support | Move alpha from 0.05 to 0.15, show Table 5.1 and the 2D candidate card, then click the CSV download. State empirical FDP at alpha 0.10 as 2.67% across 250 runs, not as an unconditional guarantee. |
| 4:15–4:45 | 30 s | Engineering rigor | Show standalone file size, offline/no-GPU design, cold-boot measurement, test counts, and the zero-warning gate. Do not show a stale or unmeasured number. |
| 4:45–4:50 | 5 s | Sign-off | Display the verified Molab/Gist URL and competition title; end at 285 seconds of planned content and never exceed 300 seconds. |

The voiceover must follow this scientific wording or a meaning-preserving equivalent:

1. **0:00–0:45:** “Time-dependent inhibition of Cytochrome P450 can create dangerous drug–drug interaction liabilities. Random splits can hide the problem by placing related scaffolds in both train and test. Our Bathtub Audit compares naive random validation with a grouped Murcko scaffold holdout, making the apparent performance loss visible instead of hiding it.”
2. **0:45–2:00:** “Table 1.1 is a reactive entry point into the literature MBI set. Clicking a compound drives the `BioactivationTracer` and the downstream docking view through Marimo’s reactive DAG. The same app handles malformed SMILES defensively, and the assay protocol remains available in a native disclosure panel.”
3. **2:00–2:45:** “AIMNet2-NSE ΔSCF descriptors improve local decision metrics while global ROC-AUC is essentially neutral, so we report both outcomes. Vina poses are interpreted as active-site steric-proximity evidence near heme iron, not as binding free energies. The CYP2D6 panel adds a measured comparison of 3TBG and 4WNW, with Paroxetine and Asp301 treated as a geometric validation case.”
4. **2:45–3:30:** “Matched molecular pairs show actionable activity cliffs on conserved cores, and the out-of-fold inspector keeps model failures visible. These records are curated OpenADMET label shifts; they are not presented as a substitute for new wet-lab confirmation.”
5. **3:30–4:15:** “TxConformal applies weighted Benjamini–Hochberg selection to the current alpha. The displayed 2.67 percent FDP at alpha 0.10 is an empirical 250-run diagnostic on the 703-compound holdout. A chemist can inspect a candidate and export the exact selected pool with the active alpha and cutoff in the CSV.”
6. **4:15–4:45:** “The delivered notebook is a self-contained offline artifact. The final claim is supported by the measured standalone byte count, cold-boot SLA, browser assertions, and zero-warning checks. No runtime GPU or network is required in Molab.”
7. **4:45–4:50:** “OpenADMET brings cheminformatics to life. Thank you.”

The JotForm package must contain a checklist, not invented submission data:

```text
[ ] Competition title and track copied exactly from the official form.
[ ] Entrant/team names and contact email supplied by the user at submission time.
[ ] Final verified Molab URL copied from EC-T3-01.
[ ] Final verified Gist URL and immutable revision copied from EC-T3-01.
[ ] Video URL/file uploaded; ffprobe duration recorded and <= 300 seconds.
[ ] Notebook description states offline CPU runtime and names the OpenADMET endpoint.
[ ] Scientific claims reviewed for docking-proxy and empirical-FDP wording.
[ ] License, attribution, and third-party asset permissions confirmed.
[ ] Screenshots/thumbnail show the actual final UI, not a pre-Tier-1 image.
[ ] Required links opened in a clean browser session.
[ ] No API key, GitHub token, Beam credential, or private customer data is in the form or repository.
[ ] Submission confirmation receipt saved outside the code workspace.
```

Use `ffprobe` for the actual rendered file:

```bash
ffprobe -v error \
  -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 \
  artifacts/video/final_submission.mp4
```

The test module should parse the seven planned durations and assert `sum == 285`, required feature names occur in the script, and no placeholder such as `<MOLAB_URL>` remains in a package marked `READY_FOR_SUBMISSION`.

### 6. Automated Verification Command

```bash
.venv/bin/python -m pytest -q \
  tests/test_submission_package.py::test_video_segments_sum_to_285_seconds \
  tests/test_submission_package.py::test_video_script_covers_all_required_features \
  tests/test_submission_package.py::test_submission_package_has_no_unresolved_placeholders
```

Run `ffprobe` separately against the actual video and record its measured duration in the package checklist.

### 7. Predeclared Acceptance Gate (Done When)

- The planned script sums to exactly 285 seconds and the rendered video is strictly below 300 seconds; the measured duration is recorded.
- All seven segments show the correct current UI and use the scientifically calibrated wording above.
- Table selection, native stats, native accordions, Act 5 export, CYP2D6 card (if Tier 2 passed), and the offline bundle gate are each visible at least once where applicable.
- The final package has verified Molab/Gist links, a verified artifact revision, clean-browser link checks, permissions/attribution, and no unresolved placeholders or secrets.
- The JotForm checklist is complete without fabricating a URL, credential, team name, or submission receipt.

### 8. Rollback Trigger

Re-edit and re-record if the measured video is 300 seconds or longer, a required interaction is absent or stale, a spoken claim exceeds the evidence, a link fails in a clean browser, the final artifact SHA differs from the staged revision, or any submission field still contains a placeholder or secret.

---

## 1. Final dependency and exit checklist

The implementation is complete only when the following sequence is recorded with real command output:

1. EC-T1-01 through EC-T1-05 pass their focused tests.
2. EC-T1-06 regenerates the standalone file and records `standalone_app.py < 200,000` bytes decimal, `marimo check` success, strict compile success, at least 186 browser passes, and zero warnings/errors.
3. EC-T2-01 produces a checksum-bearing CYP2D6 artifact with 20 explicit runs or explicit machine-readable failures; it does not silently drop an unvalidated pair.
4. EC-T2-02 embeds only the compressed summary and renders both CYP2D6 structures without a runtime network/GPU dependency.
5. EC-T2-03 reproduces raw PDBQT values, validates the schema and Paroxetine/Asp301 observation, reruns the full browser gate, and preserves the bundle budget.
6. EC-T3-01 verifies the exact staged artifact in five fresh local and five fresh hosted sessions, all below the 10-second SLA with no unexpected requests, GPU initialization, warnings, or errors.
7. EC-T3-02 records the actual video duration and final submission links. No card is marked complete from a plan, screenshot, or expected value alone.

If any exit item fails, stop at that card, retain the last passing artifact, and report the concrete failure and rollback decision before continuing.