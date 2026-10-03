# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.25.0",
#     "anywidget>=0.9.0",
#     "rdkit>=2023.9.0",
#     "pandas>=2.0.0",
#     "numpy>=1.24.0",
#     "pyarrow>=14.0.0",
#     "traitlets>=5.14.0",
#     "altair==6.3.0",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(
    width="full",
    app_title="OpenADMET: When Can We Trust a CYP Prediction?",
)


@app.cell
def __():
    import csv
    import html
    import io
    import json
    import os
    import sys
    from pathlib import Path
    import numpy as np
    import pandas as pd
    import marimo as mo

    # Ensure repository root is on sys.path
    try:
        BASE_DIR = Path(__file__).resolve().parent
    except NameError:
        BASE_DIR = Path.cwd()
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))

    from models.embedded_assets import (
        get_dataset_provenance_status,
        load_augmented_results,
        load_curated_dataset,
        load_cyp2d6_docking_results,
        load_dmpnn_baseline_results,
        load_docking_ablation_results,
        load_ecfp_baseline_results,
        load_literature_mbi_reference_set,
        load_mmp_transformations,
        load_ncbi_pubmed_cache,
        load_oof_error_cases,
        load_tanimoto_shift_summary,
        load_txconformal_selection_results,
    )
    from models.txconformal_selector import conformal_fdr_select
    from models.ncbi_client import NCBIEntrezClient
    from widgets.bioactivation_tracer import BioactivationTracer
    from widgets.layout_engine import generate_molecule_layout, safe_generate_molecule_layout

    return (
        BASE_DIR,
        BioactivationTracer,
        NCBIEntrezClient,
        conformal_fdr_select,
        csv,
        generate_molecule_layout,
        get_dataset_provenance_status,
        html,
        io,
        json,
        load_augmented_results,
        load_curated_dataset,
        load_cyp2d6_docking_results,
        load_dmpnn_baseline_results,
        load_docking_ablation_results,
        load_ecfp_baseline_results,
        load_literature_mbi_reference_set,
        load_mmp_transformations,
        load_ncbi_pubmed_cache,
        load_oof_error_cases,
        load_tanimoto_shift_summary,
        load_txconformal_selection_results,
        mo,
        np,
        os,
        pd,
        safe_generate_molecule_layout,
        sys,
    )


@app.cell
def __():
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

    return (normalize_single_table_value,)


@app.cell
def __(mo):
    def metric_stat(value, label, caption="", **_options):
        from html import escape
        return mo.Html(
            '<div class="cyp-stat"><div class="cyp-stat-label">' + escape(str(label))
            + '</div><div class="cyp-stat-value">' + escape(str(value))
            + '</div><div class="cyp-stat-caption">' + escape(str(caption)) + '</div></div>'
        )
    return (metric_stat,)


@app.cell
def __(get_dataset_provenance_status, load_curated_dataset, mo):
    # Determine active dataset provenance and compound count
    _df = load_curated_dataset()
    _status = get_dataset_provenance_status()
    _num_cpds = len(_df) if _df is not None else 0

    _source = (f"Full Curated Dataset · {_num_cpds:,} compounds" if _status == "PRIMARY_PARQUET_VERIFIED"
               else f"Portable sample · {_num_cpds:,} molecules")
    header_md = mo.Html(f"""
    <style>
      .cyp-paper {{ --ink:#252d2a; --muted:#65706a; --rule:#d5d8cf; --paper:#faf9f4;
        background:var(--paper); color:var(--ink); padding:32px clamp(16px,4vw,64px) 64px;
        max-width:1280px; margin:auto; font-family:Arial,Helvetica,sans-serif; }}
      .cyp-paper p {{ line-height:1.75; max-width:85ch; }}
      .cyp-paper h2 {{ font-family:Georgia,serif; font-size:clamp(25px,3vw,37px); font-weight:400;
        letter-spacing:-.035em; line-height:1.2; color:var(--ink); }}
      .cyp-paper h3 {{ color:var(--ink); letter-spacing:-.02em; }}
      .cyp-masthead {{ display:flex; justify-content:space-between; gap:16px; padding-bottom:14px;
        border-bottom:2px solid var(--ink); font:11px monospace; letter-spacing:.12em; text-transform:uppercase; }}
      .cyp-hero {{ display:grid; grid-template-columns:3fr 1fr; gap:36px; align-items:end; padding:44px 0 36px; }}
      .cyp-hero h1 {{ font:400 clamp(42px,6vw,76px)/1.02 Georgia,serif; letter-spacing:-.055em; margin:0; max-width:850px; }}
      .cyp-hero h1 em {{ color:#a34a31; font-weight:400; }}
      .cyp-hero aside {{ border-left:1px solid var(--rule); padding-left:20px; font-size:14px; line-height:1.7; }}
      .cyp-index {{ display:flex; flex-wrap:wrap; border-top:1px solid var(--rule); border-bottom:1px solid var(--rule); padding:16px 0; gap:12px 26px; }}
      .cyp-index a {{ color:var(--ink); text-decoration:none; font-size:13px; }}
      .cyp-index a:hover {{ color:#a34a31; text-decoration:underline; }}
      .cyp-index a:focus-visible {{ outline:2px solid #a34a31; outline-offset:5px; }}
      .cyp-index b {{ font:11px monospace; color:#a34a31; margin-right:6px; }}
      .cyp-chapter {{ border-top:1px solid var(--ink); padding-top:22px; margin-top:38px; scroll-margin-top:24px; }}
      .cyp-section-label {{ font:11px monospace; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); margin-bottom:14px; }}
      .cyp-question {{ border-left:3px solid #a34a31; padding:8px 24px; margin:18px 0; }}
      .cyp-paper div[style*="border-radius"] {{ border-radius:2px !important; box-shadow:none !important; }}
      .cyp-paper div[style*="background: #f1f1e9"], .cyp-paper div[style*="background-color: #f1f1e9"] {{ background:#f1f1e9 !important; }}
      .cyp-assay-details {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px 20px;
        margin-top:12px; padding:14px; background:white; color:#526156; border:1px solid var(--rule); font-size:12px; line-height:1.5; }}
      .cyp-assay-details span {{ min-width:0; overflow-wrap:anywhere; }}
      .cyp-assay-details strong {{ display:block; color:#252d2a; margin-bottom:3px; }}
      @media(max-width:900px) {{ .cyp-assay-details {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
      @media(max-width:540px) {{ .cyp-assay-details {{ grid-template-columns:1fr; gap:10px; }} }}
      .cyp-stat {{ height:100%; padding:20px; border:1px solid var(--rule); background:white; color:#252d2a; box-sizing:border-box; }}
      .cyp-stat-label {{ font-size:14px; line-height:1.4; }}
      .cyp-stat-value {{ font-size:28px; font-weight:600; margin:10px 0; }}
      .cyp-stat-caption {{ font-size:13px; line-height:1.6; color:#526156; overflow-wrap:anywhere; }}
      .cyp-paper div:has(> div > .cyp-stat) {{ display:grid !important; grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr)); gap:12px !important; }}
      .cyp-paper div:has(> .cyp-stat) {{ min-width:0; }}
      .cyp-paper .vega-embed {{ max-width:100%; overflow-x:auto; }}
      /* Keep the paper and its inherited text together in either system theme.
         Native marimo controls manage their own theme within this surface. */
      @media(max-width:760px) {{
        .cyp-paper {{ padding:16px 12px 32px; font-size:14px; }}
        .cyp-paper .paragraph {{ margin-block:10px !important; line-height:1.6; }}
        .cyp-paper h2 {{ font-size:27px; margin-block:12px; }}
        .cyp-paper h3 {{ font-size:20px; margin-block:12px; }}
        .cyp-hero h1 {{ font-size:38px; line-height:1.05; }}
        .cyp-hero aside {{ border-left:0; padding-left:0; font-size:14px; }}
        .cyp-masthead {{ gap:6px; font-size:9px; letter-spacing:.08em; }}
        .cyp-index a {{ display:flex; align-items:center; min-height:44px; }}
        .cyp-index {{ padding:4px 0; column-gap:18px !important; row-gap:0 !important; }}
        .cyp-question {{ padding:0 0 0 12px; margin:8px 0; }}
        .cyp-chapter {{ margin-top:24px; padding-top:16px; }}
        .cyp-paper div[style*="flex-flow: row"] {{ flex-flow:column !important; align-items:stretch !important; }}
        .cyp-paper div[style*="flex: 1"] {{ min-width:0; }}
        .cyp-paper .mo-label:has(select), .cyp-paper .mo-label:has(input[type="text"]) {{
          display:flex; flex-direction:column; align-items:stretch; width:100%; gap:8px; padding-right:0; }}
        .cyp-paper select,.cyp-paper input[type="text"] {{ width:100%; max-width:100%; min-height:44px; font-size:16px; }}
        .cyp-paper .bat-top-bar {{ flex-wrap:wrap; }}
        .cyp-paper .bat-badge {{ max-width:100%; white-space:normal; }}
        .cyp-paper .bat-btn {{ min-height:40px; }}
        .cyp-paper .bat-svg-wrapper {{ min-height:230px; }}

        .cyp-hero {{ grid-template-columns:1fr; gap:14px; padding:20px 0; }}
        .cyp-masthead {{ flex-wrap:wrap; }}
        .cyp-index {{ gap:14px 20px; }}
        .cyp-paper div[style*="grid-template-columns"] {{ grid-template-columns:minmax(0,1fr) !important; }}
        .cyp-paper div[style*="flex-direction: row"][style*="flex-wrap: nowrap"] {{ flex-direction:column !important; }}
        .cyp-paper div[style*="justify-content: space-between"][style*="display: flex"] {{ flex-wrap:wrap; gap:8px; }}
        .cyp-paper span[style*="white-space: nowrap"] {{ white-space:normal !important; }}
      }}
    </style>
    <header>
      <div class="cyp-masthead"><span>OpenADMET / CYP450</span><span>An interactive study · Rishyanth Reddy</span></div>
      <div class="cyp-hero">
        <h1>When can we trust<br>a <em>CYP prediction?</em></h1>
        <aside>A suspicious fragment is a starting point. Follow the assay, the model and the evidence to decide what to test next.</aside>
      </div>
      <nav class="cyp-index" aria-label="Study chapters">
        <a href="#cyp-assay"><b>01</b> The assay</a><a href="#cyp-split"><b>02</b> The split</a>
        <a href="#cyp-descriptors"><b>03</b> The descriptors</a><a href="#cyp-edit"><b>04</b> The chemical edit</a>
        <a href="#cyp-shortlist"><b>05</b> Your shortlist</a>
      </nav>
      <p style="font:11px monospace; color:var(--muted); margin-top:14px;">{_source} · Precomputed results, live exploration</p>
    </header>
    """)
    return (header_md,)


@app.cell
def __():
    import altair as alt
    return (alt,)


@app.cell
def __(mo):
    reveal_evidence = mo.ui.switch(label="Reveal the answer", value=False)
    return (reveal_evidence,)


@app.cell
def __(mo, reveal_evidence):
    guided_start = mo.vstack([
        mo.md("""
### Before you look at the results
**Does a reactive-looking fragment prove that a molecule inhibits CYP over time?**

Start with **Raloxifene** below. Its literature record describes bioactivation. The saved CYP3A4 docking pose puts the nearest heavy atom 2.23 Å from heme iron—but proximity alone does not establish that reaction. These are two different kinds of evidence, even when they appear beside the same molecule.

Then ask whether extra chemistry helps the model: the saved descriptor experiment changes PR-AUC from **0.4652 to 0.4753**. That modest average change cannot tell us whether a particular prediction is trustworthy.

The calculations have already been run. The controls let you explore their results. The halos are **illustrative motif weights**: they help you notice a fragment, but do not measure its reactivity.
"""),
        reveal_evidence,
        mo.callout(
            "An alert is a hypothesis. A measured TDI label describes an assay; a literature mechanism needs separate evidence. No matched alert does not establish safety."
            if reveal_evidence.value else "Make your prediction first, then reveal the answer and test it against the evidence below.",
            kind="info",
        ),
    ])
    return (guided_start,)


@app.cell
def __(load_literature_mbi_reference_set, mo):
    # Act 1: Narrative Intro on TDI Fundamentals vs MBI
    act1_intro = mo.md(
        """
## Act 1: What does the assay actually tell us?

CYP enzymes help clear many medicines from the body. If a drug inhibits one of them, it can change how another drug is cleared. Here the question is whether inhibition grows stronger after the compound has spent time with the enzyme.

### Measuring time-dependent inhibition
A microsomal preincubation assay compares inhibition before and after incubation with NADPH. In the OpenADMET challenge, a greater-than-twofold IC50 shift is one route to a positive TDI label; the challenge also supplies inferred labels in some cases. The notebook uses those supplied labels rather than applying a new threshold.

### TDI observation vs. irreversible MBI mechanism
**Time-dependent inhibition (TDI) does not, by itself, prove mechanism-based inactivation (MBI).** Slow-binding reversible inhibition, quasi-irreversible metabolic intermediate complexation (MIC), and irreversible covalent modification can lead to different interpretations of a time-dependent effect.

A structural alert tells us where to investigate. An assay tells us what happened under its conditions. Establishing an irreversible mechanism takes further evidence, such as recovery experiments or identifying the modified enzyme or heme.

Choose a literature example below. Its mechanism comes from the cited literature; the highlighted fragments are structural matches.
"""
    )

    act1_protocol_content = mo.md(
        r"""
**Preincubation.** Compare inhibition with and without NADPH preincubation in human liver microsomes. Midazolam and dextromethorphan are example probe substrates for CYP3A4 and CYP2D6.

**Labels.** The challenge uses a greater-than-twofold IC50 shift and additional inference rules. See the linked OpenADMET tutorial for the exact definitions. Labels are taken from the source file, including its missing values.

**Mechanism.** Reversible inhibition, metabolic-intermediate complexation and irreversible covalent modification require different follow-up experiments. A shift alone does not settle which mechanism occurred.
"""
    )
    act1_protocol = mo.accordion(
        {
            "How the preincubation assay works": act1_protocol_content,
        },
        multiple=False,
    )

    # Load 10 literature reference MBIs
    mbi_data = load_literature_mbi_reference_set()
    mbi_entries = mbi_data.get("entries", [])
    mbi_options = {e["name"]: e for e in mbi_entries}

    return act1_intro, act1_protocol, mbi_data, mbi_entries, mbi_options


@app.cell
def __(mbi_options, mo):
    # Act 1 Shared Selection State for Literature MBIs
    get_selected_mbi, set_selected_mbi = mo.state("Raloxifene")

    mbi_dropdown = mo.ui.dropdown(
        full_width=True,
        options=list(mbi_options.keys()),
        value="Raloxifene",
        on_change=set_selected_mbi,
        label="Choose a literature example:",
    )
    custom_smiles_input = mo.ui.text(
        full_width=True,
        value="",
        placeholder="Paste custom candidate SMILES (e.g. c1ccccc1, macrocycle, invalid syntax)...",
        label="Or enter a SMILES:",
    )
    return custom_smiles_input, get_selected_mbi, mbi_dropdown, set_selected_mbi


@app.cell
def __(mbi_entries, mo, normalize_single_table_value, set_selected_mbi):
    # Act 1 Reference Table of All 10 MBIs with Single Selection
    table_rows = [
        {
            "Compound": entry["name"],
            "SMILES": entry["smiles"],
            "Target CYP": entry["target_cyp"],
            "Reactive Warhead": entry.get("reactive_warhead_motif", entry.get("warhead", "N/A")),
            "PubMed ID": f"PMID: {entry.get('pubmed_id', entry.get('pmid', 'N/A'))}",
            "NCBI Journal": entry.get("ncbi_journal", "N/A"),
            "Evidence Level": entry.get("evidence_level", "Literature MBI"),
            "NCBI Verified": "✅ Entrez Verified" if entry.get("ncbi_verified") else "Pending",
            "In OpenADMET?": "✅ Yes" if entry.get("openadmet_presence", entry.get("in_openadmet_data")) else "Reference Fixture",
        }
        for entry in mbi_entries
    ]
    default_mbi_index = next(
        (index for index, row in enumerate(table_rows) if row["Compound"] == "Raloxifene"),
        0,
    )

    def _on_table_select(val):
        row = normalize_single_table_value(val)
        if row and row.get("Compound"):
            set_selected_mbi(row["Compound"])

    mbi_summary_table = mo.ui.table(
        data=table_rows,
        selection="single",
        on_change=_on_table_select,
        hidden_columns=["SMILES"],
        label="Table 1.1: Curated Reference Set of 10 Documented Literature Cytochrome P450 Mechanism-Based Inactivators",
    )

    act1_table_section = mo.vstack([
        mo.md("### 3. Literature examples — choose a molecule"),
        mbi_summary_table,
    ])

    return act1_table_section, default_mbi_index, mbi_summary_table, table_rows


@app.cell
def __(get_selected_mbi, mbi_dropdown, mbi_entries, mbi_summary_table, normalize_single_table_value):
    _tbl_row = normalize_single_table_value(mbi_summary_table.value)
    selected_name = get_selected_mbi() or mbi_dropdown.value or (_tbl_row.get("Compound") if _tbl_row else None) or "Raloxifene"
    selected_entry = next(
        (entry for entry in mbi_entries if entry.get("name") == selected_name),
        mbi_entries[0] if mbi_entries else {},
    )
    selected_row = _tbl_row if (_tbl_row and _tbl_row.get("Compound") == selected_name) else {"Compound": selected_name}
    return selected_entry, selected_name, selected_row


@app.cell
def __(
    BioactivationTracer,
    NCBIEntrezClient,
    custom_smiles_input,
    html,
    load_docking_ablation_results,
    mbi_dropdown,
    mo,
    safe_generate_molecule_layout,
    selected_entry,
    selected_name,
):
    # Act 1 Interactive Molecule Viewer & Literature MBI Card
    entry = selected_entry

    # Check if custom candidate SMILES was provided (Task 4.2 Defensive Fuzzing)
    custom_smi = custom_smiles_input.value.strip()
    if custom_smi:
        layout = safe_generate_molecule_layout(custom_smi)
        widget = BioactivationTracer.safe_from_smiles(
            smiles=custom_smi,
            overlay_mode="warheads",
        )
        widget_ui = mo.ui.anywidget(widget)
        _escaped_smi = html.escape(custom_smi)
        _escaped_err = html.escape(str(layout.get("error") or "Invalid SMILES"))

        if not layout["is_valid"]:
            fuzz_callout = mo.callout(
                f"This SMILES could not be read. Check the structure and try again.",
                kind="danger",
            )
        elif layout.get("has_bioactivation_alert"):
            alerts_str = ", ".join(sorted(set(html.escape(str(a["family"])) for a in layout.get("warhead_alerts", []))))
            fuzz_callout = mo.callout(
                f"Matched structural alert: {alerts_str}. A matched motif is a hypothesis to investigate, not a measured TDI result.",
                kind="warn",
            )
        else:
            fuzz_callout = mo.callout(
                f"No matched alert in {layout['num_atoms']} heavy atoms. A missing alert does not establish safety.",
                kind="success",
            )

        card_md = mo.Html(
            f"""
            <div style="padding: 16px; border: 1px solid #d5d8cf; border-radius: 10px; background: #ffffff; color: #252d2a; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
              <h3 style="margin: 0 0 8px 0; color: #252d2a; font-size: 16px;">Your structure</h3>
              <p style="margin: 0 0 6px 0; font-size: 13px;"><strong>Input SMILES:</strong> <code style="word-break: break-all;">{_escaped_smi}</code></p>
              <p style="margin: 0 0 6px 0; font-size: 13px;"><strong>Heavy Atoms:</strong> {layout.get('num_atoms', 0)} | <strong>Bonds:</strong> {layout.get('num_bonds', 0)}</p>
              <p style="margin: 0; font-size: 13px;"><strong>Layout Status:</strong> {'Structure drawn' if layout['is_valid'] else 'Structure unavailable'}</p>
            </div>
            """
        )
        act1_viewer = mo.vstack([
            mo.hstack([mbi_dropdown, custom_smiles_input], justify="start", gap=1),
            fuzz_callout,
            mo.hstack([widget_ui, card_md], justify="start", align="start", widths=[1, 2], gap=1),
        ])
        dist_info = ("Custom", "Custom Candidate", f"Custom SMILES: {_escaped_smi}")
        dock_comp = None
        docking_ablation = {}
        ncbi_client = None
        ncbi_record = {}
    else:
        # Standard Literature MBI View with Dynamic Docking and Live/Cached NCBI Metadata
        widget = BioactivationTracer.safe_from_smiles(
            smiles=entry.get("smiles", ""),
            overlay_mode="warheads",
        )
        widget_ui = mo.ui.anywidget(widget)

        # Dynamically pull 2V0M distance from real docking ablation artifact
        docking_ablation = load_docking_ablation_results()
        dock_comp = next((c for c in docking_ablation.get("docking_evaluations", []) if c["name"] == selected_name), None)
        if dock_comp and "2V0M" in dock_comp.get("docking_results", {}):
            d2 = dock_comp["docking_results"]["2V0M"]
            fe_dist_str = f"{d2['min_dist_to_heme_fe_angstrom']:.2f} Å"
            aff_str = f"Favorable ({d2['vina_affinity_kcal_mol']:.2f} kcal/mol)"
            atom_lbl = d2.get("nearest_heavy_atom", "heavy atom")
            sulf_txt = f"; sulfur at {d2['reactive_sulfur_dist_angstrom']:.2f} Å" if "reactive_sulfur_dist_angstrom" in d2 else ""
            role_str = f"Nearest heavy atom ({atom_lbl}) at {fe_dist_str} from Heme Fe{sulf_txt}"
            dist_info = (fe_dist_str, aff_str, role_str)
        else:
            dist_info = ("Unavailable", "No saved score", "No saved docking result for this molecule")

        _pmid = entry.get("pubmed_id", entry.get("pmid", ""))

        # Wire NCBIEntrezClient live/cache fetch
        ncbi_client = NCBIEntrezClient()
        ncbi_record = ncbi_client.fetch_summaries([_pmid]).get(_pmid, {}) if _pmid else {}

        _is_verified = ncbi_record.get("ncbi_verified", entry.get("ncbi_verified", False))
        _ncbi_badge = (
            '<span style="background: #eff3e9; color: #065f46; border: 1px solid #cad8c2; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">✓ PubMed record found</span>'
            if _is_verified
            else '<span style="background: #eeeee5; color: #65706a; padding: 2px 8px; border-radius: 4px; font-size: 11px;">Unverified</span>'
        )
        _ncbi_title = ncbi_record.get("title", entry.get("ncbi_title", entry.get("literature_citation", "N/A")))
        _journal = ncbi_record.get("journal", entry.get("ncbi_journal", "N/A"))
        _pubdate = ncbi_record.get("pubdate", entry.get("ncbi_pubdate", "N/A"))
        _ncbi_pub = f"{_journal} ({_pubdate})"

        _pmid_display = (
            f'<a href="https://pubmed.ncbi.nlm.nih.gov/{_pmid}/" target="_blank" style="color: #315a49; text-decoration: underline; font-weight: 600;">PMID: {_pmid} ↗</a>'
            if _pmid
            else "N/A"
        )
        _doi = ncbi_record.get("doi", entry.get("ncbi_doi"))
        _doi_url = ncbi_record.get("doi_url", entry.get("ncbi_doi_url"))
        _doi_display = (
            f'<a href="{_doi_url}" target="_blank" style="color: #315a49; text-decoration: underline;">{_doi} ↗</a>'
            if _doi and _doi_url
            else (_doi or "N/A (Print Era Citation)")
        )

        card_md = mo.Html(
            f"""
            <div style="padding: 16px; border: 1px solid #d5d8cf; border-radius: 10px; background: #ffffff; color: #252d2a; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
              <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eeeee5; padding-bottom: 8px; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <h3 style="margin: 0; color: #252d2a; font-size: 18px;">{entry.get('name', 'Unknown')}</h3>
                  {_ncbi_badge}
                </div>
                <span style="background: #fef2f2; color: #b91c1c; border: 1px solid #fca5a5; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; white-space: nowrap;">
                  Evidence: {entry.get('evidence_level', 'Definitive Literature MBI')}
                </span>
              </div>

              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 13px;">
                <div>
                  <strong>Target CYP Isoform:</strong> <span style="color: #315a49; font-weight: 600;">{entry.get('target_cyp', 'N/A')}</span><br>
                  <strong>Warhead Motif:</strong> <code>{entry.get('reactive_warhead_motif', entry.get('warhead', 'N/A'))}</code><br>
                  <strong>Proposed Reactive Intermediate:</strong> {entry.get('inactivation_mechanism', entry.get('mechanism_intermediate', 'Reactive Electrophilic Adduct'))}<br>
                  <strong>2V0M Distance to Catalytic Heme Fe:</strong> <span style="color: #35604b; font-weight: 700;">{dist_info[0]}</span> ({dist_info[1]})
                </div>
                <div>
                  <strong>NCBI Verified Title:</strong> <em>{_ncbi_title}</em><br>
                  <strong>Journal & Date:</strong> {_ncbi_pub}<br>
                  <strong>PubMed ID:</strong> {_pmid_display} | <strong>DOI:</strong> {_doi_display}<br>
                  <strong>Mechanistic Structural Role:</strong> {dist_info[2]}<br>
                  <strong>Chemical SMILES:</strong> <code style="font-size: 11px; word-break: break-all;">{entry.get('smiles', '')}</code>
                </div>
              </div>
            </div>
            """
        )

        act1_viewer = mo.vstack([
            mo.hstack([mbi_dropdown, custom_smiles_input], justify="start", gap=1),
            mo.hstack([widget_ui, card_md], justify="start", align="start", widths=[1, 2], gap=1),
        ])

    return act1_viewer, card_md, dist_info, dock_comp, docking_ablation, entry, ncbi_client, ncbi_record, widget, widget_ui


@app.cell
def __(
    BASE_DIR,
    load_dmpnn_baseline_results,
    load_ecfp_baseline_results,
    load_tanimoto_shift_summary,
    mo,
):
    # Act 2: Narrative Intro on the Bathtub Audit
    act2_intro = mo.md(
        """
## Act 2: How much does the split matter?

A model may look good when it sees close relatives of its training molecules. That is useful, but it is a different task from predicting an unfamiliar chemical series.

Here a **random split** is compared with a **Bemis-Murcko scaffold split**, which keeps core frameworks together. The “Bathtub Effect” is the observed score difference, not proof of memorization or prospective performance. Change the model and metric below: a small difference can hide a weak model, so look at the absolute scores too.

The grouped folds contain 1,208–1,275 molecules. Parent identities and nonempty scaffolds are kept apart; related molecules can still have similar fingerprints. Acyclic molecules use a separate identity-based grouping rule. Endpoint masks and class proportions matter when comparing the results.
"""
    )

    # Load baseline benchmark results and tanimoto shift summaries with fallback resilience
    ecfp_data = load_ecfp_baseline_results()
    dmpnn_data = load_dmpnn_baseline_results()
    tani_data = load_tanimoto_shift_summary()

    ecfp_file = BASE_DIR / "data" / "packaged" / "ecfp_baseline_results.json"
    dmpnn_file = BASE_DIR / "data" / "packaged" / "dmpnn_baseline_results.json"
    tani_file = BASE_DIR / "data" / "curated" / "tanimoto_shift_summary.json"

    return act2_intro, dmpnn_data, dmpnn_file, ecfp_data, ecfp_file, tani_data, tani_file


@app.cell
def __(mo):
    # Act 2 Interactive Controls
    model_dropdown = mo.ui.dropdown(
        full_width=True,
        options=["LightGBM (ECFP4 2048-bit)", "Logistic Regression (ECFP4)", "Chemprop v2 D-MPNN (Graph)"],
        value="LightGBM (ECFP4 2048-bit)",
        label="Choose a model:",
    )

    metric_radio = mo.ui.radio(
        options=["PR-AUC (Precision-Recall)", "MCC (Matthews Correlation)", "ROC-AUC", "Brier Probability Error"],
        value="PR-AUC (Precision-Recall)",
        label="Choose a metric:",
    )

    act2_controls = mo.hstack([model_dropdown, metric_radio], justify="start", gap=1.25)
    return act2_controls, metric_radio, model_dropdown


@app.cell
def __(metric_stat, dmpnn_data, ecfp_data, metric_radio, model_dropdown, mo):
    # Act 2 Reactive Metric Comparison Card
    arch = model_dropdown.value
    metric_choice = metric_radio.value

    metric_key_map = {
        "PR-AUC (Precision-Recall)": ("pr_auc", "pr_auc", True),
        "MCC (Matthews Correlation)": ("mcc", "mcc", True),
        "ROC-AUC": ("roc_auc", "roc_auc", True),
        "Brier Probability Error": ("brier_score", "brier", False),
    }
    raw_key, ci_key, higher_is_better = metric_key_map[metric_choice]

    if "LightGBM" in arch:
        m_dict = ecfp_data.get("models", {}).get("lightgbm", {})
    elif "Logistic" in arch:
        m_dict = ecfp_data.get("models", {}).get("logistic_regression", {})
    else:
        m_dict = dmpnn_data.get("dmpnn", {})

    rand_oof = m_dict.get("random_5fold", {}).get("overall_oof", {})
    scaff_oof = m_dict.get("grouped_5fold", {}).get("overall_oof", {})

    rand_val = rand_oof.get(raw_key, 0.0)
    scaff_val = scaff_oof.get(raw_key, 0.0)

    rand_ci = rand_oof.get("bootstrap_ci_95", {}).get(ci_key, {})
    scaff_ci = scaff_oof.get("bootstrap_ci_95", {}).get(ci_key, {})

    delta = rand_val - scaff_val
    pct_inflation = (delta / max(scaff_val, 1e-4)) * 100 if higher_is_better else ((scaff_val - rand_val) / max(rand_val, 1e-4)) * 100

    if higher_is_better and delta > 0.015:
        verdict = f"⚠️ Higher score with random validation (+{pct_inflation:.1f}%)"
        verdict_color = "#dc2626"
        verdict_bg = "#fef2f2"
    elif not higher_is_better and (scaff_val - rand_val) > 0.005:
        verdict = f"⚠️ Higher error with scaffold validation (+{pct_inflation:.1f}%)"
        verdict_color = "#dc2626"
        verdict_bg = "#fef2f2"
    else:
        verdict = f"✅ Small difference between splits (Δ ≈ {delta:+.4f})"
        verdict_color = "#16a34a"
        verdict_bg = "#eff3e9"

    act2_kpis = mo.hstack([
        metric_stat(value=f"{rand_val:.4f}", label="Random CV", caption=arch, bordered=True),
        metric_stat(value=f"{scaff_val:.4f}", label="Scaffold CV", caption=metric_choice, bordered=True),
        metric_stat(value=f"{scaff_val - rand_val:+.4f}", label="Scaffold minus random", caption="Observed difference; not a significance test", bordered=True),
    ], widths="equal")
    card_comparison_md = mo.vstack([
        mo.md(f"### {arch} — {metric_choice}\n**{verdict}**\n\nRandom and scaffold CV ask different generalization questions. Similar scores alone do not establish prospective reliability. The graph model also has lower absolute PR-AUC in this benchmark; compare values as well as differences."),
        act2_kpis,
    ])
    return (
        act2_kpis,
        arch,
        card_comparison_md,
        ci_key,
        delta,
        higher_is_better,
        m_dict,
        metric_choice,
        metric_key_map,
        pct_inflation,
        rand_ci,
        rand_oof,
        rand_val,
        raw_key,
        scaff_ci,
        scaff_oof,
        scaff_val,
        verdict,
        verdict_bg,
        verdict_color,
    )


@app.cell
def __(alt, arch, metric_choice, mo, pd, rand_ci, rand_val, scaff_ci, scaff_val):
    _rows = []
    for _label, _value, _ci in (("Random CV", rand_val, rand_ci), ("Scaffold CV", scaff_val, scaff_ci)):
        _rows.append({"split": _label, "value": _value, "lower": _ci.get("ci_lower"), "upper": _ci.get("ci_upper")})
    _base = alt.Chart(pd.DataFrame(_rows)).encode(y=alt.Y("split:N", title=None))
    _points = _base.mark_point(filled=True, size=130).encode(x=alt.X("value:Q", title=metric_choice, scale=alt.Scale(zero=False)), color=alt.Color("split:N", legend=None), tooltip=["split", alt.Tooltip("value:Q", format=".4f"), alt.Tooltip("lower:Q", format=".4f"), alt.Tooltip("upper:Q", format=".4f")])
    _intervals = _base.mark_rule(strokeWidth=3).encode(x="lower:Q", x2="upper:Q")
    benchmark_chart = mo.vstack([
        mo.ui.altair_chart((_intervals + _points).properties(height=150, width="container", title=arch), chart_selection=False, legend_selection=False),
        mo.md("Points show out-of-fold metrics; bars show reported 95% molecule-level bootstrap intervals where available. These intervals are not a paired test of the difference."),
    ])
    return (benchmark_chart,)


@app.cell
def __(alt, mo, pd, tani_data):
    _random = tani_data["random_baseline_comparison"]
    _holdout = tani_data["holdout_scaffold"]["test_vs_train"]
    _rows = [
        {"split": _label, "mean": _summary["mean"], "novel_fraction": _summary["fraction_novel_chemotypes_lt_0_4"], "n": _summary["count"]}
        for _label, _summary in (("Random CV", _random), ("Scaffold TEST holdout", _holdout))
    ]
    _chart = alt.Chart(pd.DataFrame(_rows)).mark_bar().encode(
        x=alt.X("mean:Q", title="Mean nearest-training-neighbor Tanimoto", scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("split:N", title=None), color=alt.Color("split:N", legend=None),
        tooltip=["split", "n", alt.Tooltip("mean:Q", format=".4f"), alt.Tooltip("novel_fraction:Q", format=".1%")],
    ).properties(height=130, width="container")
    tanimoto_svg_chart = mo.vstack([
        mo.ui.altair_chart(_chart, chart_selection=False, legend_selection=False),
        mo.md("Random CV mean: **0.4862**; scaffold TEST holdout mean: **0.4428**, with **40.7%** below 0.40 similarity. These summaries compare 6,145 CV predictions with a 1,208-compound holdout; they are different populations, not a paired experiment. Exact histogram bins are unavailable in the packaged summary."),
    ])
    return (tanimoto_svg_chart,)


@app.cell
def __(mo, ecfp_data, dmpnn_data):
    benchmark_table_data = []
    for _name, _results in (
        ("LightGBM (ECFP4 2048-bit)", ecfp_data["models"]["lightgbm"]),
        ("Logistic Regression (ECFP4)", ecfp_data["models"]["logistic_regression"]),
        ("Chemprop v2 D-MPNN (Graph)", dmpnn_data["dmpnn"]),
    ):
        _random = _results["random_5fold"]["overall_oof"]
        _grouped = _results["grouped_5fold"]["overall_oof"]
        _row = {"Model Architecture": _name}
        for _key, _label in (("pr_auc", "PR-AUC"), ("mcc", "MCC")):
            for _split, _summary in (("Random", _random), ("Scaffold", _grouped)):
                _ci = _summary.get("bootstrap_ci_95", {}).get(_key, {})
                _interval = f" [{_ci['ci_lower']:.4f}, {_ci['ci_upper']:.4f}]" if _ci.get("ci_lower") is not None and _ci.get("ci_upper") is not None else " (CI unavailable)"
                _row[f"{_split} 5-Fold {_label}"] = f"{_summary[_key]:.4f}{_interval}"
            _row[f"{_label} Scaffold minus random"] = f"{_grouped[_key] - _random[_key]:+.4f}"
        _row["Interpretation"] = "Observed split difference; not a significance test"
        benchmark_table_data.append(_row)

    act2_benchmark_table = mo.ui.table(
        data=benchmark_table_data,
        label="Table 2.1: Model results under random and scaffold validation",
    )

    act2_section = mo.vstack([
        mo.md("### 2. Compare the models"),
        act2_benchmark_table,
    ])

    return act2_benchmark_table, act2_section, benchmark_table_data


@app.cell
def __(
    BASE_DIR,
    load_augmented_results,
    load_cyp2d6_docking_results,
    load_docking_ablation_results,
    mo,
):
    # Act 3: Narrative Intro on Quantum Reactivity & Enzymology
    act3_intro = mo.md(
        """
## Act 3: Do electronic descriptors help?

Fingerprints describe a molecule's structural patterns. Electronic descriptors ask about a different part of the chemistry: how readily the molecule gives up or accepts charge. That is an appealing idea for CYP reactions, where the iron-oxo oxidant **Compound I** can generate reactive intermediates.

This experiment adds ten AIMNet2-family descriptors to a 2D model. The changes are modest: PR-AUC rises by 0.0101 and MCC by 0.0209. ROC-AUC across 3,584 compounds remains essentially unchanged. These results suggest a question worth testing; they do not yet establish a significant improvement or a mechanism.

**Vertical Ionization Potential** estimates electron-removal energy, **Chemical Hardness** describes resistance to charge change, and the **Radical Fukui Index** describes electronic response to electron addition and removal. None is an enzyme reaction rate.

There is also a limit to what can be traced in this cache. The small Beam experiment names an NSE model, but the full-feature script's uncached path selects `aimnet2`; the saved full cache lacks a model and conformer record. The benchmark is therefore described as AIMNet2-family augmentation. The molecule viewer uses illustrative halos, not these atom-level calculations.
"""
    )

    # Load augmented benchmark results, docking ablation results, and CYP2D6 results
    aug_data = load_augmented_results()
    dock_data = load_docking_ablation_results()
    cyp2d6_dock_data = load_cyp2d6_docking_results()

    aug_file = BASE_DIR / "data" / "packaged" / "augmented_results.json"
    dock_file = BASE_DIR / "data" / "packaged" / "docking_ablation_results.json"

    return act3_intro, aug_data, aug_file, cyp2d6_dock_data, dock_data, dock_file


@app.cell
def __(mo):
    # Act 3 Interactive Controls: Metric Selector
    act3_metric_radio = mo.ui.radio(
        options=["PR-AUC (Precision-Recall)", "MCC (Matthews Correlation)", "ROC-AUC (Global Ranking)", "Brier Score (Probability Error)"],
        value="PR-AUC (Precision-Recall)",
        label="Choose a metric:",
    )
    return (act3_metric_radio,)


@app.cell
def __(metric_stat, act3_metric_radio, aug_data, mo):
    # Act 3 Reactive Comparison Card: 2D Baseline vs Physics-Augmented
    _metric_choice = act3_metric_radio.value

    _metric_map = {
        "PR-AUC (Precision-Recall)": ("pr_auc", "pr_auc", True),
        "MCC (Matthews Correlation)": ("mcc", "mcc", True),
        "ROC-AUC (Global Ranking)": ("roc_auc", "roc_auc", True),
        "Brier Score (Probability Error)": ("brier_score", "brier", False),
    }
    _raw_k, _ci_k, _higher_better = _metric_map[_metric_choice]

    _b2d = aug_data.get("baseline_2d", {})
    _a_aim = aug_data.get("augmented_aimnet2", {})

    _b2d_val = _b2d.get(_raw_k, 0.0)
    _aim_val = _a_aim.get(_raw_k, 0.0)

    _b2d_ci = _b2d.get("bootstrap_ci_95", {}).get(_ci_k, {})
    _aim_ci = _a_aim.get("bootstrap_ci_95", {}).get(_ci_k, {})

    _delta = _aim_val - _b2d_val

    _verdict = f"Observed change: {_delta:+.4f}"
    _verdict_color = "#526156"
    _verdict_bg = "#f1f1e9"
    _scientific_insight = (
        "These are small changes. The reported intervals do not establish a statistically significant improvement or explain a mechanism. "
        "Brier measures probability error, rather than calibration alone."
    )

    act3_kpis = mo.hstack(
        [
            metric_stat(
                value="+0.0101",
                label="PR-AUC lift",
                caption="0.4652 baseline → 0.4753 AIMNet2-family; grouped scaffold CV",
                direction="increase",
                target_direction="increase",
                bordered=True,
            ),
            metric_stat(
                value="+0.0209",
                label="MCC lift",
                caption="0.3298 baseline → 0.3507 AIMNet2-family; grouped scaffold CV",
                direction="increase",
                target_direction="increase",
                bordered=True,
            ),
            metric_stat(
                value="+0.0023",
                label="ROC-AUC change",
                caption="0.7868 baseline → 0.7891 AIMNet2-family; neutral within uncertainty",
                direction=None,
                target_direction="increase",
                bordered=True,
            ),
            metric_stat(
                value="-0.0031",
                label="Brier error change",
                caption="0.1573 baseline → 0.1542 AIMNet2-family; lower is better",
                direction="decrease",
                target_direction="decrease",
                bordered=True,
            ),
        ],
        widths="equal",
        gap=0.75,
    )

    act3_card_comparison_md = mo.vstack([
        mo.md(
            f"""
            <div style="padding: 16px; border: 1px solid #d5d8cf; border-radius: 10px; background: #ffffff; color: #252d2a; box-shadow: 0 1px 3px rgba(0,0,0,0.05); margin-top: 12px; margin-bottom: 12px;">
              <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eeeee5; padding-bottom: 8px; margin-bottom: 12px;">
                <h4 style="margin: 0; color: #252d2a; font-size: 16px;">With and without electronic descriptors — {_metric_choice}</h4>
                <span style="background: {_verdict_bg}; color: {_verdict_color}; border: 1px solid {_verdict_color}33; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; white-space: nowrap;">
                  {_verdict}
                </span>
              </div>

              <div style="display: grid; grid-template-columns: 1fr 1fr 1.3fr; gap: 16px; font-size: 13px;">
                <div style="padding: 12px; background: #f1f1e9; border-radius: 8px; border-left: 4px solid #8c968e;">
                  <span style="color: #65706a; font-size: 11px; font-weight: 600; text-transform: uppercase;">2D Baseline (ECFP4 + RDKit)</span><br>
                  <span style="font-size: 24px; font-weight: 700; color: #303a32;">{_b2d_val:.4f}</span><br>
                  <span style="font-size: 11px; color: #65706a;">
                    95% CI: [{_b2d_ci.get('ci_lower', 0.0):.4f}, {_b2d_ci.get('ci_upper', 0.0):.4f}]
                  </span>
                </div>

                <div style="padding: 12px; background: #f1f1e9; border-radius: 8px; border-left: 4px solid #8c6d43;">
                  <span style="color: #65706a; font-size: 11px; font-weight: 600; text-transform: uppercase;">Plus electronic descriptors</span><br>
                  <span style="font-size: 24px; font-weight: 700; color: #303a32;">{_aim_val:.4f}</span><br>
                  <span style="font-size: 11px; color: #65706a;">
                    95% CI: [{_aim_ci.get('ci_lower', 0.0):.4f}, {_aim_ci.get('ci_upper', 0.0):.4f}]
                  </span>
                </div>

                <div style="padding: 12px; background: #f1f1e9; border-radius: 8px; border-left: 4px solid #65706a;">
                  <span style="color: #65706a; font-size: 11px; font-weight: 600; text-transform: uppercase;">Reading this result</span><br>
                  <p style="margin: 4px 0 0 0; font-size: 12px; line-height: 1.4; color: #37443b;">
                    {_scientific_insight}
                  </p>
                </div>
              </div>
            </div>
            """
        ),
        act3_kpis,
    ])
    return (act3_card_comparison_md, act3_kpis)


@app.cell
def __(dock_data, mo, selected_name):
    # Act 3 Macromolecular 3D Docking Explorer (CYP3A4 PDB 2V0M vs 1TQN)
    evals = dock_data.get("docking_evaluations", [])
    compound_names = [e["name"] for e in evals] if evals else ["Raloxifene"]
    _default_name = selected_name if selected_name in compound_names else (compound_names[0] if compound_names else "Raloxifene")

    dock_dropdown = mo.ui.dropdown(
        full_width=True,
        options=compound_names,
        value=_default_name,
        label="Choose a molecule for CYP3A4 docking:",
    )

    return compound_names, dock_dropdown, evals


@app.cell
def __(dock_dropdown, evals, mo):
    # Act 3 Reactive Docking Card
    _sel_name = dock_dropdown.value or "Raloxifene"
    _target_eval = next((e for e in evals if e["name"] == _sel_name), None)

    if _target_eval:
        _v2 = _target_eval["docking_results"]["2V0M"]
        _t1 = _target_eval["docking_results"]["1TQN"]
        _dist_2v0m = _v2["min_dist_to_heme_fe_angstrom"]
        _aff_2v0m = _v2["vina_affinity_kcal_mol"]
        _dist_1tqn = _t1["min_dist_to_heme_fe_angstrom"]
        _aff_1tqn = _t1["vina_affinity_kcal_mol"]
    else:
        _dist_2v0m, _aff_2v0m = 2.24, -9.79
        _dist_1tqn, _aff_1tqn = 5.73, -9.97

    _docking_inspection_md = mo.Html(
        f"""
        <div style="margin-top: 16px; padding: 16px; border: 1px solid #d5d8cf; border-radius: 10px; background: #ffffff; color: #252d2a; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eeeee5; padding-bottom: 8px; margin-bottom: 12px;">
            <h4 style="margin: 0; color: #252d2a; font-size: 16px;">
               CYP3A4 Crystallographic Active-Site Docking: {_sel_name}
            </h4>
            <span style="background: #eff3e9; color: #065f46; border: 1px solid #cad8c2; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; white-space: nowrap;">
              AutoDock Vina v1.2.7 (CPU backend)
            </span>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1fr 1.2fr; gap: 14px; font-size: 13px;">
            <div style="padding: 12px; background: #eff3e9; border-radius: 8px; border-left: 4px solid #54775f;">
              <strong style="color: #065f46;">Substrate-Bound State (PDB: 2V0M, 2.80 Å)</strong><br>
              <div style="margin-top: 6px;">
                <strong>Min Distance to Heme Fe:</strong> <span style="font-size: 16px; font-weight: 700; color: #35604b;">{_dist_2v0m:.2f} Å</span><br>
                <strong>Vina score:</strong> <span style="font-weight: 600;">{_aff_2v0m:.2f} kcal/mol</span><br>
                <span style="color: #35604b; font-size: 11px; font-weight: 600;">Whole-ligand distance, not a reaction-site distance</span>
              </div>
            </div>

            <div style="padding: 12px; background: #f1f1e9; border-radius: 8px; border-left: 4px solid #8c968e;">
              <strong style="color: #526156;">Unliganded Resting State (PDB: 1TQN, 2.05 Å)</strong><br>
              <div style="margin-top: 6px;">
                <strong>Min Distance to Heme Fe:</strong> <span style="font-size: 16px; font-weight: 700; color: #37443b;">{_dist_1tqn:.2f} Å</span><br>
                <strong>Vina score:</strong> <span style="font-weight: 600;">{_aff_1tqn:.2f} kcal/mol</span><br>
                <span style="color: #65706a; font-size: 11px;">A different receptor conformation</span>
              </div>
            </div>

            <div style="padding: 12px; background: #f1f1e9; border-radius: 8px; border-left: 4px solid #8c6d43;">
              <strong style="color: #695333;">What this pose shows</strong><br>
              <p style="margin: 4px 0 0 0; font-size: 12px; line-height: 1.4; color: #37443b;">
                For {_sel_name}, the top saved pose places its nearest heavy atom <strong>{_dist_2v0m:.2f} Å from the heme iron</strong>. Raloxifene's reference pose has a distance of <strong>2.23 Å</strong>.
                This describes where the ligand sits in the model. It does not identify the reacting atom or demonstrate inactivation.

              </p>
            </div>
          </div>
        </div>
        """
    )

    act3_docking_section = mo.vstack([
        mo.md("### 2. Docking in CYP3A4"),
        mo.Html(
            """
            <div style="padding: 10px 14px; background: #f1f1e9; border-left: 4px solid #315a49; font-size: 12px; color: #526156; margin-bottom: 12px; border-radius: 4px; line-height: 1.5;">
              <strong>Comparing different isoforms:</strong> The literature examples involve several CYP isoforms. Here they are docked into CYP3A4 structures 2V0M (2.80 Å) and 1TQN (2.05 Å). A pose in CYP3A4 does not transfer a mechanism demonstrated for another isoform.

            </div>
            """
        ),
        dock_dropdown,
        _docking_inspection_md,
    ])

    return (act3_docking_section,)


@app.cell
def __(cyp2d6_dock_data, mo):
    # Act 3 Dual-Isoform CYP2D6 Structural Docking Controls (Beam Cloud RTX 4090)
    cyp2d6_evals = cyp2d6_dock_data.get("docking_evaluations", [])
    cyp2d6_compound_names = [e["name"] for e in cyp2d6_evals] if cyp2d6_evals else []
    _default_compound = (
        "Paroxetine"
        if "Paroxetine" in cyp2d6_compound_names
        else (cyp2d6_compound_names[0] if cyp2d6_compound_names else None)
    )

    cyp2d6_compound_dropdown = mo.ui.dropdown(
        full_width=True,
        options=cyp2d6_compound_names,
        value=_default_compound,
        label="Choose a molecule for CYP2D6 docking:",
    )

    cyp2d6_isoform_dropdown = mo.ui.dropdown(
        full_width=True,
        options=[
            "All Conformations (Side-by-Side)",
            "Substrate-Bound State (PDB: 3TBG, 2.10 Å)",
            "Unliganded Resting State (PDB: 4WNW, 3.30 Å)",
        ],
        value="All Conformations (Side-by-Side)",
        label="Choose the CYP2D6 structure:",
    )

    return cyp2d6_compound_dropdown, cyp2d6_compound_names, cyp2d6_evals, cyp2d6_isoform_dropdown


@app.cell
def __(
    cyp2d6_compound_dropdown,
    cyp2d6_dock_data,
    cyp2d6_evals,
    cyp2d6_isoform_dropdown,
    mo,
):
    # Act 3 Reactive Dual-Isoform CYP2D6 Card (Beam Cloud RTX 4090)
    _sel_compound = cyp2d6_compound_dropdown.value
    _target_eval = next((e for e in cyp2d6_evals if e["name"] == _sel_compound), None) if _sel_compound else None

    _meta = cyp2d6_dock_data.get("metadata", {})
    _exec_meta = _meta.get("execution", {})
    _gpu_device = _exec_meta.get("gpu_device", "NVIDIA GeForce RTX 4090")
    _vram = _exec_meta.get("vram_gb", 23.52)
    _beam_task = _exec_meta.get("beam_task_id", "dc1112ce-e7dc-4abe-943b-790ccae2e9b5")

    if _target_eval:
        _res_3tbg = _target_eval["docking_results"]["3TBG"]
        _res_4wnw = _target_eval["docking_results"]["4WNW"]
        _target_cyp = _target_eval.get("target_cyp", "CYP2D6")
        _warhead = _target_eval.get("warhead") or _target_eval.get("reactive_warhead_motif") or "characterized bioactivation"
        _is_paroxetine = bool(_sel_compound == "Paroxetine")
        if _is_paroxetine:
            _iso_badge = '<span style="background: #eff3e9; color: #065f46; border: 1px solid #cad8c2; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700;">🟢 Isoform-Matched Canonical Reference</span>'
        else:
            _iso_badge = f'<span style="background: #f1f1e9; color: #526156; border: 1px solid #cbd1c7; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">⚪ Exploratory Cross-Isoform Panel (Primary Target: {_target_cyp})</span>'
        _narrative_text = (
            "<strong>Canonical CYP2D6 Mechanism:</strong> Paroxetine features a basic piperidine amine that provides active-site electrostatic guidance toward Asp301 (6.71 Å in 3TBG, non-contact proximity), positioning the ligand within the active-site cavity (whole-molecule nearest-heavy-atom proximity: 4.89 Å [fluorine] from heme iron in 3TBG, indicating ligand proximity; the nearest fluorine is not a demonstrated bioactivation site). Bioactivation of the methylenedioxyphenyl warhead yields a reactive carbene that forms a quasi-irreversible metabolite-intermediate complex (MIC) with the heme iron."
            if _is_paroxetine
            else f"<strong>Exploratory Cross-Isoform Probe:</strong> {_sel_compound} is clinically characterized as a mechanism-based inactivator of {_target_cyp} bearing a {_warhead} warhead. Cross-docking into CYP2D6 evaluates active-site cavity steric accommodation versus isoform-specific selectivity."
        )
        _vina_3tbg_html = f'<span style="font-weight: 700; color: #35604b;">{_res_3tbg["vina_affinity_kcal_mol"]:.2f} kcal/mol</span>'
        _fe_dist_3tbg_html = f'<span style="font-size: 15px; font-weight: 700; color: #35604b;">{_res_3tbg["min_dist_to_heme_fe_angstrom"]:.2f} Å</span> ({_res_3tbg.get("nearest_heavy_atom", "N/A")})'
        _vina_4wnw_html = f'<span style="font-weight: 700; color: #37443b;">{_res_4wnw["vina_affinity_kcal_mol"]:.2f} kcal/mol</span>'
        _fe_dist_4wnw_html = f'<span style="font-size: 15px; font-weight: 700; color: #37443b;">{_res_4wnw["min_dist_to_heme_fe_angstrom"]:.2f} Å</span> ({_res_4wnw.get("nearest_heavy_atom", "N/A")})'
        _asp_3tbg = _res_3tbg.get("asp301_contact")
        _asp_4wnw = _res_4wnw.get("asp301_contact")
        _contact_3tbg_label = "Direct Salt Bridge Contact (≤ 4.0 Å)" if _asp_3tbg and _asp_3tbg.get("contact_type") == "salt_bridge" else "Active-Site Proximity (Non-Contact)"
        _asp_3tbg_html = f'<span style="color: #35604b; font-weight: 600;">{_asp_3tbg["distance_angstrom"]:.2f} Å ({_contact_3tbg_label})</span>' if _asp_3tbg else '<span style="color: #8c968e;">N/A (Non-Basic Pharmacophore)</span>'
        _contact_4wnw_label = "Direct Salt Bridge Contact (≤ 4.0 Å)" if _asp_4wnw and _asp_4wnw.get("contact_type") == "salt_bridge" else "Active-Site Proximity (Non-Contact)"
        _asp_4wnw_html = f'<span style="color: #37443b; font-weight: 600;">{_asp_4wnw["distance_angstrom"]:.2f} Å ({_contact_4wnw_label})</span>' if _asp_4wnw else '<span style="color: #8c968e;">N/A (Non-Basic Pharmacophore)</span>'
        _prox_3tbg = "Nearest ligand atom within 5.0 Å" if _res_3tbg.get("active_site_steric_proximity_le_5A") else "Nearest ligand atom beyond 5.0 Å"
        _prox_4wnw = "Nearest ligand atom within 5.0 Å" if _res_4wnw.get("active_site_steric_proximity_le_5A") else "Nearest ligand atom beyond 5.0 Å"
    else:
        _target_cyp = "None"
        _warhead = "None"
        _is_paroxetine = False
        _iso_badge = '<span style="background: #eeeee5; color: #65706a; border: 1px solid #cbd1c7; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">⚪ No Structural Evaluation Available</span>'
        _narrative_text = "<strong>No Active-Site Evaluation:</strong> No docking evaluation record is available for the current selection."
        _vina_3tbg_html = '<span style="color: #8c968e; font-weight: 600;">No Evaluation Available</span>'
        _fe_dist_3tbg_html = '<span style="color: #8c968e; font-weight: 600;">No Evaluation Available</span>'
        _vina_4wnw_html = '<span style="color: #8c968e; font-weight: 600;">No Evaluation Available</span>'
        _fe_dist_4wnw_html = '<span style="color: #8c968e; font-weight: 600;">No Evaluation Available</span>'
        _asp_3tbg_html = '<span style="color: #8c968e;">No Evaluation Available</span>'
        _asp_4wnw_html = '<span style="color: #8c968e;">No Evaluation Available</span>'
        _prox_3tbg = "No Evaluation Available"
        _prox_4wnw = "No Evaluation Available"

    _sel_conformation = cyp2d6_isoform_dropdown.value or "All Conformations (Side-by-Side)"
    _show_3tbg = ("3TBG" in _sel_conformation or "All" in _sel_conformation)
    _show_4wnw = ("4WNW" in _sel_conformation or "All" in _sel_conformation)

    _card_3tbg_html = f"""
    <div style="padding: 12px; background: #eff3e9; border-radius: 8px; border-left: 4px solid #54775f;">
      <strong style="color: #065f46;">Substrate-Bound State (PDB: 3TBG, 2.10 Å)</strong><br>
      <div style="margin-top: 6px; line-height: 1.6;">
        <strong>Vina Binding Score:</strong> {_vina_3tbg_html}<br>
        <strong>Min Distance to Heme Fe:</strong> {_fe_dist_3tbg_html}<br>
        <strong>Asp301 Anchor Distance:</strong> {_asp_3tbg_html}<br>
        <span style="color: #35604b; font-size: 11px; font-weight: 600;">{_prox_3tbg}</span>
      </div>
    </div>
    """ if _show_3tbg else ""

    _card_4wnw_html = f"""
    <div style="padding: 12px; background: #f1f1e9; border-radius: 8px; border-left: 4px solid #8c968e;">
      <strong style="color: #526156;">Unliganded Resting State (PDB: 4WNW, 3.30 Å)</strong><br>
      <div style="margin-top: 6px; line-height: 1.6;">
        <strong>Vina Binding Score:</strong> {_vina_4wnw_html}<br>
        <strong>Min Distance to Heme Fe:</strong> {_fe_dist_4wnw_html}<br>
        <strong>Asp301 Anchor Distance:</strong> {_asp_4wnw_html}<br>
        <span style="color: #65706a; font-size: 11px; font-weight: 600;">{_prox_4wnw}</span>
      </div>
    </div>
    """ if _show_4wnw else ""

    _grid_cols = "1fr 1fr 1.2fr" if (_show_3tbg and _show_4wnw) else "1.2fr 1.2fr"

    _cyp2d6_inspection_md = mo.Html(
        f"""
        <div style="margin-top: 16px; padding: 16px; border: 1px solid #d5d8cf; border-radius: 10px; background: #ffffff; color: #252d2a; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eeeee5; padding-bottom: 8px; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
            <div>
              <h4 style="margin: 0; color: #252d2a; font-size: 16px;">
                 CYP2D6 Active-Site Conformation: {_sel_compound or 'None Selected'}
              </h4>
              <div style="margin-top: 4px;">{_iso_badge}</div>
            </div>
            <span style="background: #f4efe4; color: #695333; border: 1px solid #ded3be; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; white-space: nowrap;">
              AutoDock Vina v1.2.7 · computed on Beam Cloud with the CPU backend
            </span>
          </div>

          <div style="display: grid; grid-template-columns: {_grid_cols}; gap: 14px; font-size: 13px;">
            {_card_3tbg_html}
            {_card_4wnw_html}

            <div style="padding: 12px; background: #f1f1e9; border-radius: 8px; border-left: 4px solid #8c6d43;">
              <strong style="color: #695333;">Asp301 Anchor & Bioactivation Geometry</strong><br>
              <p style="margin: 4px 0 0 0; font-size: 12px; line-height: 1.45; color: #37443b;">
                {_narrative_text}
              </p>
            </div>
          </div>
        </div>
        """
    )

    act3_cyp2d6_section = mo.vstack([
        mo.md("### 3. Docking in CYP2D6"),
        mo.Html(
            """
            <div style="padding: 10px 14px; background: #f4efe4; border-left: 4px solid #8c6d43; font-size: 12px; color: #695333; margin-bottom: 12px; border-radius: 4px; line-height: 1.5;">
              <strong>Where these docking results come from:</strong> Human CYP2D6 is responsible for the hepatic clearance of ~25% of clinical therapeutics, featuring a canonical electrostatic anchor residue (<strong>Asp301</strong>). Vina used a CPU backend on Beam Cloud for the substrate-bound (PDB 3TBG, 2.10 Å) and unliganded (PDB 4WNW, 3.30 Å) structures. Vina scores are empirical scoring functions, providing geometric proximity proxies rather than experimental free energies or covalent inactivation constants ($k_{inact}/K_I$).
            </div>
            """
        ),
        mo.vstack([cyp2d6_compound_dropdown, cyp2d6_isoform_dropdown], gap=1),
        _cyp2d6_inspection_md,
    ])

    return (act3_cyp2d6_section,)


@app.cell
def __(mo):
    # Act 3 Summary Benchmark Table
    act3_table_data = [
        {
            "Feature Representation": "2D Baseline (ECFP4 2048-bit + RDKit PhysChem)",
            "Scaffold 5-Fold PR-AUC": "0.4652 [0.4324, 0.5019]",
            "Scaffold 5-Fold MCC": "0.3298 [0.2960, 0.3646]",
            "Scaffold 5-Fold ROC-AUC": "0.7868 [0.7706, 0.8032]",
            "Brier Score": "0.1573 [0.1506, 0.1644]",
            "Observed change": "Standard 2D Baseline",
        },
        {
            "Feature Representation": "Physics-Augmented (2D + AIMNet2-family ΔSCF)",
            "Scaffold 5-Fold PR-AUC": "0.4753 [0.4414, 0.5110]",
            "Scaffold 5-Fold MCC": "0.3507 [0.3156, 0.3850]",
            "Scaffold 5-Fold ROC-AUC": "0.7891 [0.7725, 0.8053]",
            "Brier Score": "0.1542 [0.1473, 0.1615]",
            "Observed change": "✅ +0.0101 PR-AUC, +0.0209 MCC, -0.0031 Brier",
        },
    ]

    act3_benchmark_table = mo.ui.table(
        data=act3_table_data,
        label="Table 3.1: Model results with and without electronic descriptors",
    )

    act3_table_section = mo.vstack([
        mo.md("### 3. The descriptor comparison in numbers"),
        act3_benchmark_table,
    ])

    return act3_benchmark_table, act3_table_data, act3_table_section


@app.cell
def __(load_mmp_transformations, mo):
    # Act 4: Narrative Intro on MMP Activity Cliffs & Lead Optimization
    act4_intro = mo.md(
        r"""
## Act 4: What can a small chemical edit change?

Two close analogues can have different assay labels. Looking at them side by side can help suggest a next experiment without throwing away the whole chemical series.

The dataset contains **34 unique matched molecular pairs** with different TDI labels: 25 CYP3A4 pairs and 9 CYP2D6 pairs. Each has a shared core of at least ten heavy atoms and one ring, with a substituent change of at most six heavy atoms.

These are observed label differences. They do not prove that the edit prevents a particular reaction, preserves binding affinity, or makes a compound safe. Choose a pair, then look at a model error below. The proposed mechanism explanations are hypotheses.
"""
    )

    mmp_data = load_mmp_transformations()
    mmp_pairs = mmp_data.get("pairs", [])
    mmp_options = {
        f"{p['mmp_id']} ({p['isoform']}): {p['transformation'].split('>>')[0].strip()} ➔ {p['transformation'].split('>>')[1].strip()}": p
        for p in mmp_pairs
    }

    return act4_intro, mmp_data, mmp_options, mmp_pairs


@app.cell
def __(mmp_options, mo):
    # Act 4 Interactive MMP Selector
    mmp_dropdown = mo.ui.dropdown(
        full_width=True,
        options=list(mmp_options.keys()),
        value=list(mmp_options.keys())[0] if mmp_options else None,
        label="Choose a molecular pair:",
    )
    return (mmp_dropdown,)


@app.cell
def __(BioactivationTracer, mmp_dropdown, mmp_options, mo):
    # Act 4 Reactive MMP Side-by-Side Viewer
    _selected_key = mmp_dropdown.value
    _pair = mmp_options.get(_selected_key, {})

    if _pair:
        _mol_act = _pair["mol_active"]
        _mol_inact = _pair["mol_inactive"]

        # Left: Inactivator Lead with warhead halos
        _widget_act = BioactivationTracer.safe_from_smiles(
            smiles=_mol_act["smiles"],
            overlay_mode="warheads",
        )
        _ui_act = mo.ui.anywidget(_widget_act)

        # Right: Safe Redesigned Analog
        _widget_inact = BioactivationTracer.safe_from_smiles(
            smiles=_mol_inact["smiles"],
            overlay_mode="clean",
        )
        _ui_inact = mo.ui.anywidget(_widget_inact)

        _cliff_card = mo.md(
            f"""
            <div style="margin-top: 12px; padding: 14px; border: 1px solid #d5d8cf; border-radius: 8px; background: #f1f1e9; font-size: 13px;">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <strong style="color: #252d2a; font-size: 15px;">{_pair['mmp_id']} — {_pair['isoform']} Observed label change</strong>
                <span style="background: #eff3e9; color: #16a34a; border: 1px solid #cad8c2; padding: 3px 10px; border-radius: 6px; font-weight: 600; font-size: 11px; white-space: nowrap;">
                  {_pair.get('curation_status', 'OPENADMET_LABEL_SHIFT')}
                </span>
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 10px; margin-bottom: 8px;">
                <div style="background: #ffffff; color: #252d2a; padding: 8px; border-radius: 6px; border: 1px solid #d5d8cf;">
                  <span style="color: #65706a; font-size: 10px; font-weight: 600;">TRANSFORMATION</span><br>
                  <code style="font-size: 11px;">{_pair['transformation']}</code>
                </div>
                <div style="background: #ffffff; color: #252d2a; padding: 8px; border-radius: 6px; border: 1px solid #d5d8cf;">
                  <span style="color: #65706a; font-size: 10px; font-weight: 600;">Δ MOLECULAR WEIGHT</span><br>
                  <strong style="font-size: 14px; color: #252d2a;">{_pair['delta_mw']:+.1f} Da</strong>
                </div>
                <div style="background: #ffffff; color: #252d2a; padding: 8px; border-radius: 6px; border: 1px solid #d5d8cf;">
                  <span style="color: #65706a; font-size: 10px; font-weight: 600;">Δ cLogP</span><br>
                  <strong style="font-size: 14px; color: #252d2a;">{_pair['delta_logp']:+.2f}</strong>
                </div>
                <div style="background: #ffffff; color: #252d2a; padding: 8px; border-radius: 6px; border: 1px solid #d5d8cf;">
                  <span style="color: #65706a; font-size: 10px; font-weight: 600;">Δ TPSA</span><br>
                  <strong style="font-size: 14px; color: #252d2a;">{_pair['delta_tpsa']:+.1f} Å²</strong>
                </div>
              </div>
              <p style="margin: 0; color: #37443b; font-size: 12px; line-height: 1.4;">
                <strong>What this pair shows:</strong> This pair has different TDI labels on a shared core. The edit suggests an experiment; its effect on mechanism and binding affinity has not been established.
              </p>
              <div class="cyp-assay-details">
                <span><strong>TDI-positive row:</strong> {_mol_act.get('source_row_id', 'N/A')} (ΔpIC50 = {_mol_act.get('pic50_shift', 'N/A')})</span>
                <span><strong>TDI-negative row:</strong> {_mol_inact.get('source_row_id', 'N/A')} (ΔpIC50 = {_mol_inact.get('pic50_shift', 'N/A')})</span>
                <span><strong>Assay ID:</strong> {_mol_act.get('assay_id', 'OCTANT_CYP_HLM_IC50_SHIFT')}</span>
                <span><strong>Source:</strong> {_mol_act.get('source_dataset', 'cyp-challenge-TRAIN_TDI.csv')}</span>
                <span><strong>Measurement:</strong> {_mol_act.get('measurement_type', 'Preincubation IC50 Shift Ratio')}</span>
                <span><strong>Threshold:</strong> Source challenge labels; see assay definitions</span>
                <span><strong>Replicates:</strong> {_mol_act.get('replicate_summary', 'Not recorded in this artifact')}</span>
              </div>
            </div>
            """
        )

        act4_mmp_viewer = mo.vstack([
            mo.md("### 2. One core, two assay labels"),
            mmp_dropdown,
            mo.hstack([
                mo.vstack([
                    mo.md("<div style='text-align: center; font-weight: 600; color: #dc2626;'>TDI-positive label</div>"),
                    _ui_act,
                ]),
                mo.vstack([
                    mo.md("<div style='text-align: center; font-weight: 600; color: #16a34a;'>TDI-negative label</div>"),
                    _ui_inact,
                ]),
            ], justify="center", gap=1.5),
            _cliff_card,
        ])
    else:
        act4_mmp_viewer = mo.md("No MMP pair selected.")

    return (act4_mmp_viewer,)


@app.cell
def __(BioactivationTracer, load_oof_error_cases, mo):
    # Act 4 Out-of-Fold (OOF) Model Error Inspector - Loaded from Packaged Provenance Catalog
    _oof_payload = load_oof_error_cases()
    oof_cases = _oof_payload.get("cases", [])

    oof_dropdown = mo.ui.dropdown(
        full_width=True,
        options=[c["display_label"] for c in oof_cases],
        value=oof_cases[0]["display_label"] if oof_cases else "",
        label="Choose a prediction error:",
    )

    return oof_cases, oof_dropdown


@app.cell
def __(BioactivationTracer, mo, oof_cases, oof_dropdown):
    # Act 4 Reactive OOF Error Diagnosis Card
    _selected_label = oof_dropdown.value
    _case = next(
        (c for c in oof_cases if c.get("display_label") == _selected_label or f"{c.get('category')}: {c.get('name', '')}" == _selected_label),
        oof_cases[0] if oof_cases else {},
    )

    _smiles = _case.get("assay_smiles", _case.get("smiles", ""))
    _widget = BioactivationTracer.safe_from_smiles(
        smiles=_smiles,
        overlay_mode="warheads",
    )
    _widget_ui = mo.ui.anywidget(_widget)

    _is_fn = "Negative" in _case.get("category", "")
    _badge_bg = "#fef2f2" if _is_fn else "#fefce8"
    _badge_color = "#dc2626" if _is_fn else "#a16207"

    _pred_prob = _case.get("pred_prob_augmented", _case.get("pred_prob", 0.0))
    _pred_2d = _case.get("pred_prob_2d", 0.0)
    _true_tdi = 1 if _case.get("cyp3a4_is_tdi") in (1, True) else 0

    _oof_card = mo.md(
        f"""
        <div style="padding: 16px; border: 1px solid #d5d8cf; border-radius: 10px; background: #ffffff; color: #252d2a; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
          <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eeeee5; padding-bottom: 8px; margin-bottom: 12px;">
            <h4 style="margin: 0; color: #252d2a; font-size: 16px;">{_case.get('molecule_name', '')} ({_case.get('chemical_name', '')})</h4>
            <span style="background: {_badge_bg}; color: {_badge_color}; border: 1px solid {_badge_color}33; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; white-space: nowrap;">
              {_case.get('category', '')}
            </span>
          </div>

          <div style="display: grid; grid-template-columns: 1fr 1.4fr; gap: 16px; font-size: 13px;">
            <div style="padding: 12px; background: #f1f1e9; border-radius: 8px;">
              <strong>Source assay label:</strong> <span style="color: {'#dc2626' if _true_tdi == 1 else '#16a34a'}; font-weight: 700;">{'TDI Active (1)' if _true_tdi == 1 else 'TDI-negative (0)'}</span><br>
              <strong>2D Baseline Probability (p̂):</strong> <span style="font-weight: 600; color: #37443b;">{_pred_2d:.4f}</span><br>
              <strong>Augmented Model Probability (p̂):</strong> <span style="font-size: 16px; font-weight: 700; color: #303a32;">{_pred_prob:.4f}</span><br>
              <strong>Evaluation Provenance:</strong> Grouped Scaffold 5-Fold CV (Fold {_case.get('cv_fold_5', 0)})<br>
              <strong>Source Assay:</strong> {_case.get('source_dataset', 'Octant HLM Assay')}<br>
              <strong>Chemical SMILES:</strong> <code style="font-size: 11px; word-break: break-all;">{_smiles}</code>
            </div>

            <div style="padding: 12px; background: #f1f1e9; border-radius: 8px; border-left: 4px solid {_badge_color};">
              <strong style="color: #252d2a;">What the saved evidence supports:</strong><br>
              <p style="margin: 4px 0 0 0; font-size: 12px; line-height: 1.4; color: #37443b;">
                {_case.get('rationale', '')}
              </p>
            </div>
          </div>
        </div>
        """
    )

    act4_oof_section = mo.vstack([
        mo.md("""### 3. Where the model gets it wrong
*Examines real out-of-fold diagnostic failure modes across Grouped Scaffold 5-Fold CV, including false negatives and false positives. The proposed explanations are hypotheses, not validated causal attributions.*"""),
        oof_dropdown,
        mo.hstack([_widget_ui, _oof_card], justify="start", gap=1),
    ])

    return (act4_oof_section,)


@app.cell
def __(BASE_DIR, load_txconformal_selection_results, mo):
    # Act 5: Narrative Intro on TxConformal Selection
    act5_intro = mo.md(
        r"""
## Act 5: Which molecules would we test next?

Suppose there is room to test only a shortlist. A low predicted TDI probability is a useful starting point, but how should it become a decision?

This example uses **TxConformal-inspired weighted conformal selection** with the Benjamini-Hochberg procedure. Move the nominal FDR level, alpha, to see how the shortlist changes. A smaller alpha asks for stronger evidence against the null hypothesis that a molecule has a TDI label.

The predictive model was fitted on TRAIN labels only, then calibrated separately. The plot contains the first 100 TEST molecules in source order, rather than a representative sample. Selection is rerun on this pool at your chosen alpha.

The historical 2.67% mean false discovery proportion at alpha 0.10 comes from **250-run Monte Carlo** resampling of a larger, 703-compound holdout. It is not the measured error rate of the shortlist below. Estimated density weights and ordinary BH do not give a verified guarantee under arbitrary chemical shift, and a selected molecule is not certified safe.
"""
    )

    tx_data = load_txconformal_selection_results()
    tx_file = BASE_DIR / "data" / "packaged" / "txconformal_selection_results.json"

    return act5_intro, tx_data, tx_file


@app.cell
def __(mo):
    # Act 5 Interactive Conformal Selection Slider
    alpha_slider = mo.ui.slider(
        start=0.05,
        stop=0.20,
        step=0.01,
        value=0.10,
        label="Choose alpha for this shortlist:",
    )
    return (alpha_slider,)


@app.cell
def __(mo):
    get_candidate_focus, set_candidate_focus = mo.state(None)
    return get_candidate_focus, set_candidate_focus


@app.cell
def __(metric_stat, alpha_slider, conformal_fdr_select, csv, io, mo, tx_data, normalize_single_table_value, set_candidate_focus):
    # Act 5 Reactive Candidate Selection Sandbox: Real Weighted Benjamini-Hochberg Step-Up Selection
    _target_alpha = alpha_slider.value
    _mc_summary = tx_data.get("monte_carlo_robustness_summary", {})
    _candidates = tx_data.get("test_candidates_sample", [])

    # Dynamic Benjamini-Hochberg Step-Up Selection Procedure via conformal_fdr_select
    _p_values = [float(c.get("weighted_pvalue", 1.0)) for c in _candidates]
    _sel_result = conformal_fdr_select(_p_values, _target_alpha)
    _selected_indices = set(_sel_result["selected_indices"])
    _critical_cutoff = _sel_result["critical_cutoff"]
    _selected_count = _sel_result["selected_count"]
    _m = len(_p_values)

    # Identify nearest benchmark Monte Carlo calibration point (evaluated on the 703-compound test set)
    _benchmark_nominal_alphas = [0.05, 0.10, 0.15, 0.20]
    _nearest_alpha = min(_benchmark_nominal_alphas, key=lambda a: abs(a - _target_alpha))
    _mc_key = f"alpha_{_nearest_alpha:.2f}"
    _stats = _mc_summary.get(_mc_key, {"mean_fdp": 0.0267, "mean_selection_size": 30.0, "mean_power": 0.1876})
    _benchmark_mean_fdp = float(_stats.get("mean_fdp", 0.0267))

    # Construct table rows with exact dynamic BH selection status and stable machine columns
    candidate_rows = []
    for _idx, c in enumerate(_candidates):
        _p_val = float(c.get("weighted_pvalue", 1.0))
        _prob = float(c.get("predicted_liability_prob", 0.5))
        _is_selected = _idx in _selected_indices

        candidate_rows.append({
            "candidate_id": c.get("molecule_name", f"candidate-{_idx:03d}"),
            "molecule_name": c.get("molecule_name", "Unknown"),
            "smiles": c.get("smiles", ""),
            "predicted_liability_prob": _prob,
            "weighted_conformal_pvalue": _p_val,
            "selection_status": (
                f"✅ Selected (p ≤ {_critical_cutoff:.4f})"
                if _is_selected else "Excluded (p > BH cutoff)"
            ),
        })

    candidate_table = mo.ui.table(
        data=candidate_rows,
        on_change=lambda value: set_candidate_focus(normalize_single_table_value(value).get("candidate_id")),
        selection="single",
        initial_selection=[0] if candidate_rows else [],
        hidden_columns=["candidate_id", "smiles"],
        label=(
            f"Table 5.1: TxConformal Prioritized Candidate Shortlist — "
            f"N={len(candidate_rows)} display candidates; nominal α={_target_alpha:.2f}"
        ),
    )

    # Act 5 One-Click Prioritized Candidate CSV Export (EC-T1-05)
    EXPORT_COLUMNS = [
        "molecule_name",
        "smiles",
        "predicted_liability_prob",
        "weighted_conformal_pvalue",
        "nominal_alpha_threshold",
        "conformal_cutoff_pstar",
    ]

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
        data=build_candidate_csv(),
        filename=candidate_csv_filename(),
        mimetype="text/csv",
        disabled=not bool(_selected_indices),
        label="Download Selected Candidates (CSV)",
    )

    act5_kpis = mo.hstack([
        metric_stat(value=f"{_selected_count} / {_m}", label="Selected in this pool", bordered=True),
        metric_stat(value=f"{_target_alpha:.2f}", label="Nominal alpha", bordered=True),
        metric_stat(value=f"{_critical_cutoff:.4f}", label="BH cutoff", bordered=True),
    ], widths="equal")
    conformal_card = mo.vstack([
        act5_kpis,
        mo.md("Green points meet the selection rule. Click a point or a table row to look at that molecule, then download the selected set."),
        mo.accordion({"How this relates to the earlier benchmark": mo.md(
            f"At the nearest saved alpha, **{_nearest_alpha:.2f}**, the 250-run diagnostic had a mean FDP of **{_benchmark_mean_fdp:.2%}** and selected **{_stats.get('mean_selection_size', 30.0):.1f}** molecules on average. Each run resampled 200 molecules from the 703-compound TEST holdout. These summaries describe that experiment, not the current 100-molecule pool."
        )}),
    ])
    return (
        EXPORT_COLUMNS,
        act5_kpis,
        build_candidate_csv,
        candidate_csv_filename,
        candidate_download,
        candidate_rows,
        candidate_table,
        conformal_card,
        selected_export_rows,
    )


@app.cell
def __(alpha_slider, alt, candidate_rows, mo, pd, normalize_single_table_value, set_candidate_focus):
    _plot_rows = sorted(candidate_rows, key=lambda row: row["weighted_conformal_pvalue"])
    _plot_rows = [dict(row, rank=i + 1, bh_threshold=(i + 1) / max(len(_plot_rows), 1) * alpha_slider.value, selected="Selected" if row["selection_status"].startswith("✅") else "Excluded") for i, row in enumerate(_plot_rows)]
    _base = alt.Chart(pd.DataFrame(_plot_rows)).encode(x=alt.X("rank:Q", title="Rank in this display pool"))
    _points = _base.mark_circle(size=55).encode(y=alt.Y("weighted_conformal_pvalue:Q", title="Weighted conformal p-value", scale=alt.Scale(domain=[0, 1])), color=alt.Color("selected:N", scale=alt.Scale(domain=["Selected", "Excluded"], range=["#35604b", "#8c968e"])), tooltip=["molecule_name", alt.Tooltip("weighted_conformal_pvalue:Q", format=".5f"), alt.Tooltip("predicted_liability_prob:Q", format=".4f"), "selected"])
    _pick = alt.selection_point(name="candidate_pick", fields=["candidate_id"], on="click", clear="dblclick")
    _points = _points.add_params(_pick)
    _line = _base.mark_line(color="#315a49", strokeDash=[5, 3], tooltip=False).encode(y="bh_threshold:Q")
    selection_plot = mo.ui.altair_chart((_line + _points).properties(height=260, width="container"), chart_selection=False, legend_selection=False, on_change=lambda value: set_candidate_focus(normalize_single_table_value(value).get("candidate_id") if value is not None and len(value) == 1 else None), label="Click one candidate to inspect it. Dashed line: nominal α × rank / pool size.")
    return (selection_plot,)


@app.cell
def __(BioactivationTracer, alpha_slider, candidate_table, candidate_rows, get_candidate_focus, mo, normalize_single_table_value, safe_generate_molecule_layout):
    # Act 5 Reactive Candidate 2D Structure Inspection Card
    _focus = get_candidate_focus()
    selected_candidate = next((row for row in candidate_rows if row["candidate_id"] == _focus), None) if _focus else normalize_single_table_value(candidate_table.value)
    if not selected_candidate:
        candidate_card = mo.callout(
            "Select a candidate row in Table 5.1 above to inspect its 2D chemical structure.",
            kind="info",
        )
    else:
        smiles = str(selected_candidate.get("smiles", ""))
        _layout = safe_generate_molecule_layout(smiles)
        if not _layout or not _layout.get("atoms"):
            candidate_card = mo.callout(
                f"2D coordinates unavailable for candidate SMILES: {smiles}",
                kind="warn",
            )
        else:
            _widget = BioactivationTracer.safe_from_smiles(
                smiles=smiles,
                overlay_mode="warheads",
            )
            candidate_card = mo.vstack(
                [
                    mo.md(
                        f"### 2D Candidate Structure\n"
                        f"**{selected_candidate.get('molecule_name', 'Unknown')}**  \n"
                        f"`SMILES`: `{smiles}`  \n"
                        f"Active nominal α: `{alpha_slider.value:.2f}`  \n"
                        f"Predicted liability probability: "
                        f"{float(selected_candidate.get('predicted_liability_prob', 0.0)):.4f}  \n"
                        f"Weighted conformal p-value: "
                        f"{float(selected_candidate.get('weighted_conformal_pvalue', 1.0)):.4f}  \n"
                        f"Status: {selected_candidate.get('selection_status', 'Unknown')}"
                    ),
                    mo.ui.anywidget(_widget),
                ]
            )
    return (candidate_card,)


@app.cell
def __(
    alpha_slider,
    candidate_card,
    candidate_download,
    candidate_table,
    conformal_card,
    mo,
    selection_plot,
):
    act5_conformal_section = mo.vstack([
        mo.md("### 3. Explore the 100-molecule shortlist"),
        alpha_slider,
        conformal_card,
        selection_plot,
        mo.md("BH is rerun on the current 100-row display pool. The separate 250-run benchmark resamples 200 candidates from the full holdout; its FDP is not the FDP of this displayed shortlist. Model fitting used TRAIN labels only; density weighting used unlabeled calibration/test features."),
        candidate_table,
        candidate_card,
        candidate_download,
    ])
    return (act5_conformal_section,)


@app.cell
def __(mo):
    # Act 5 Honest Limitations, DOME Checklist, and Citations
    act5_limitations_md = mo.md(
        r"""
### 4. What would we need to know next?

A sensible shortlist is the beginning of an experiment. The next checks would be a repeat TDI assay, a look at inhibition recovery, and testing whether the result carries over to a different chemical series or assay setup.

**Assay context matters.** Probe substrate, incubation conditions and additional metabolism can change the picture. CYP3A4 also has a flexible binding pocket; one docking pose does not capture all of its behavior.

**The statistical results have a scope.** Scaffold validation is useful but not a prospective study. The descriptor changes need a stronger comparison, and the selection benchmark does not certify individual molecules as safe.

### 5. Methods and sources
"""
    )

    dome_content = mo.md(
        """
| DOME axis | Implementation in OpenADMET Cytochrome P450 Platform |
| :--- | :--- |
| **Data (D)** | 6,145 compounds curated with dual-SMILES policy. Strict missingness masks (3,584 3A4, 1,497 2D6). Zero target leakage verified programmatically. Murcko scaffold clustering with 0 parent InChIKey overlap across folds. |
| **Optimization (O)** | Fixed LightGBM hyperparameters; Chemprop v2 D-MPNN trained for 20 epochs on MPS. No early stopping or validation checkpoint selection is implemented. |
| **Model (M)** | 2D ECFP4 tabular baselines, continuous message-passing graph neural networks (D-MPNN), AIMNet2-family electronic descriptors with incomplete cache provenance, and AutoDock Vina v1.2.7 macromolecular docking. |
| **Evaluation (E)** | Strict Grouped Murcko Scaffold 5-Fold CV + 60/20/20 holdout. 1000-resample molecule-level bootstrap 95% confidence intervals across PR-AUC, MCC, ROC-AUC, and Brier scores. Empirical FDR evaluated under covariate shift via weighted conformal selection. |
"""
    )
    act5_dome_accordion = mo.accordion(
        {
            "Methods and reproducibility (DOME)": dome_content,
        },
        multiple=False,
    )

    act5_citations_md = mo.md(
        """
---
### 6. Sources

1. **OpenADMET Challenge (2026):** [CYP Challenge tutorial and assay definitions](https://github.com/OpenADMET/CYP-Challenge-Tutorial). This notebook competition is separate from the blind prediction challenge.
2. **Octant Bio:** High-throughput Cytochrome P450 reactivity and microsomal stability datasets (*willitfly* and *reactivity* libraries).
3. **AIMNet2 family:** [Isayev Lab model documentation](https://isayevlab.github.io/aimnetcentral/models/guide/); [AIMNet2-NSE open-shell study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12851018/).
4. **TxConformal:** Jin, Huang, Diamant et al. (2026), [*TxConformal: Controlling False Discoveries in AI-Driven Therapeutic Discovery*](https://doi.org/10.64898/2026.04.27.721076), bioRxiv preprint. This notebook is a simplified empirical demonstration, not a verified implementation of every published guarantee.
5. **RCSB Protein Data Bank:** CYP3A4 Crystal Structures **2V0M** (Ketoconazole-bound complex, 2.80 Å) and **1TQN** (Unliganded resting state, 2.05 Å).
6. **AutoDock Vina v1.2.7:** Eberhardt et al. (2021) *AutoDock Vina 1.2.0: Automating docking calculations for macromolecular complexes*.
"""
    )

    act5_limitations_and_dome = mo.vstack([
        act5_limitations_md,
        act5_dome_accordion,
        act5_citations_md,
        mo.md("**Authorship and AI disclosure:** Rishyanth Reddy developed this scientific exploration with AI assistance for code, review, and presentation. Precomputed artifacts are retained for reproducibility. Assay labels, descriptor estimates, docking hypotheses, and illustrative halos are distinct evidence types."),
    ])

    return (act5_limitations_and_dome,)


@app.cell(expand_output=True)
def __(
    act1_intro,
    act1_protocol,
    act1_table_section,
    act1_viewer,
    act2_controls,
    act2_intro,
    act2_section,
    act3_card_comparison_md,
    act3_cyp2d6_section,
    act3_docking_section,
    act3_intro,
    act3_metric_radio,
    act3_table_section,
    act4_intro,
    act4_mmp_viewer,
    act4_oof_section,
    act5_conformal_section,
    act5_intro,
    act5_limitations_and_dome,
    card_comparison_md,
    header_md,
    mo,
    tanimoto_svg_chart,
    guided_start,
    benchmark_chart,
):
    # Each chapter keeps its controls beside the evidence they change.
    def _chapter(anchor, label, content):
        return mo.Html(f'<section class="cyp-chapter" id="{anchor}"><div class="cyp-section-label">{label}</div>{mo.vstack(content).text}</section>')

    main_view = mo.Html('<article class="cyp-paper">' + mo.vstack([

        header_md,
        mo.Html('<div class="cyp-question">' + guided_start.text + '</div>'),
        _chapter("cyp-assay", "01 / Observation", [act1_intro, act1_viewer, act1_protocol, mo.accordion({"Browse all literature examples": act1_table_section})]),
        _chapter("cyp-split", "02 / Generalisation", [act2_intro, act2_controls, card_comparison_md,
            benchmark_chart, mo.accordion({"Chemical distance and full benchmark table": mo.vstack([tanimoto_svg_chart, act2_section])})]),
        _chapter("cyp-descriptors", "03 / Mechanistic evidence", [act3_intro, act3_metric_radio,
            act3_card_comparison_md, mo.accordion({"Inspect the saved docking results": mo.vstack([act3_docking_section, act3_cyp2d6_section]), "Full descriptor benchmark": act3_table_section})]),
        _chapter("cyp-edit", "04 / Counterexamples", [act4_intro, act4_mmp_viewer, act4_oof_section]),
        _chapter("cyp-shortlist", "05 / The next experiment", [act5_intro, act5_conformal_section]),
        mo.md("""### What I would take into the next experiment

**The split changes the question.** Random validation and scaffold validation test different kinds of generalisation; compare both before trusting a score on new chemistry.

**More descriptors did not settle it.** The observed PR-AUC gain was 0.0101. The reported intervals do not establish a reliable improvement, and incomplete cache provenance limits reproduction of the electronic features.

**A shortlist is a choice about what to test.** The alpha control changes an exploratory selection rule; it does not certify a compound as safe or guarantee the error rate of this sample. For Raloxifene, the literature supplies evidence that its docking distance alone cannot. For an unfamiliar candidate, the next step is an experiment, not a stronger claim from the picture.
"""),
        act5_limitations_and_dome,
    ]).text + '</article>')
    main_view
    return (main_view,)


if __name__ == "__main__":
    app.run()



