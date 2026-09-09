#!/usr/bin/env python3
"""
EC-3-1-03: Single-File Marimo App Bundler & Asset Inliner.

Utility script that extracts, compresses, and generates self-contained inline strings
for deployment in a single standalone `app.py` file without external directory dependencies.
"""

from __future__ import annotations

import base64
import gzip
import io
import json
import re
import sys
import tokenize
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

WIDGETS_DIR = BASE_DIR / "widgets"
MODELS_DIR = BASE_DIR / "models"
PACKAGED_DIR = BASE_DIR / "data" / "packaged"
FIXTURES_DIR = BASE_DIR / "data" / "fixtures"


def get_inlined_js() -> str:
    """Returns contents of bioactivation_tracer.js with comments and excess blank lines stripped."""
    js_path = WIDGETS_DIR / "bioactivation_tracer.js"
    raw = js_path.read_text(encoding="utf-8")
    no_comments = re.sub(r"/\*[\s\S]*?\*/", "", raw)
    no_comments = re.sub(r"(?<!:)//.*", "", no_comments)
    lines = no_comments.splitlines()
    in_template = False
    compressed_lines = []
    for line in lines:
        count = line.count("`")
        if count % 2 != 0:
            in_template = not in_template
        if in_template:
            compressed_lines.append(line.rstrip())
        else:
            stripped = line.strip()
            if stripped:
                compressed_lines.append(stripped)
    return "\n".join(compressed_lines)


def get_inlined_css() -> str:
    """Returns contents of bioactivation_tracer.css with comments and excess indentation stripped."""
    css_path = WIDGETS_DIR / "bioactivation_tracer.css"
    raw = css_path.read_text(encoding="utf-8")
    no_comments = re.sub(r"/\*[\s\S]*?\*/", "", raw)
    min_css = re.sub(r"\s*([\{\};:,])\s*", r"\1", no_comments)
    min_css = re.sub(r";\}", "}", min_css)
    lines = [line.strip() for line in min_css.splitlines() if line.strip()]
    return "\n".join(lines)


def get_inlined_layout_engine_source() -> str:
    """Returns layout_engine.py code for inlining."""
    engine_path = WIDGETS_DIR / "layout_engine.py"
    return engine_path.read_text(encoding="utf-8")


def get_inlined_layout_engine_body() -> str:
    """Returns layout_engine.py definitions indented for cell 1 with comments and docstrings stripped."""
    raw = get_inlined_layout_engine_source()
    if 'if __name__ == "__main__":' in raw:
        raw = raw[:raw.index('if __name__ == "__main__":')]
    start_marker = "ELEMENT_COLORS = {"
    if start_marker in raw:
        raw = raw[raw.index(start_marker):]
    raw = re.sub(r'"""[\s\S]*?"""', '', raw)
    lines = [
        "    " + l.rstrip()
        for l in raw.splitlines()
        if l.strip() and not l.strip().startswith("#")
    ]
    return "\n".join(lines)


def get_inlined_conformal_selector_body() -> str:
    """Returns conformal_fdr_select function extracted from txconformal_selector.py, indented for cell 1 with comments and docstrings stripped."""
    selector_path = MODELS_DIR / "txconformal_selector.py"
    raw = selector_path.read_text(encoding="utf-8")
    start_marker = "def conformal_fdr_select("
    end_marker = "def apply_benjamini_hochberg("
    if start_marker in raw and end_marker in raw:
        fn_code = raw[raw.index(start_marker):raw.index(end_marker)].rstrip()
    else:
        raise ValueError("Could not extract conformal_fdr_select from txconformal_selector.py")
    fn_code = re.sub(r'"""[\s\S]*?"""', '', fn_code)
    lines = [
        "    " + l.rstrip()
        for l in fn_code.splitlines()
        if l.strip() and not l.strip().startswith("#")
    ]
    return "\n".join(lines)


def get_embedded_assets_source() -> str:
    """Returns models/embedded_assets.py code containing base64 data payloads."""
    assets_path = MODELS_DIR / "embedded_assets.py"
    return assets_path.read_text(encoding="utf-8")


def verify_bundle_components() -> dict[str, Any]:
    """
    Validates that all single-file bundling components are present, non-empty,
    and decode cleanly into valid structures.
    """
    from models.embedded_assets import (
        load_fallback_dataset,
        load_literature_mbi_reference_set,
        load_mmp_transformations,
        load_ncbi_pubmed_cache,
        load_cyp2d6_docking_results,
    )

    js_src = get_inlined_js()
    css_src = get_inlined_css()
    layout_src = get_inlined_layout_engine_source()
    layout_body = get_inlined_layout_engine_body()
    conformal_body = get_inlined_conformal_selector_body()

    df_fallback = load_fallback_dataset()
    mbis = load_literature_mbi_reference_set()
    mmps = load_mmp_transformations()
    ncbi_cache = load_ncbi_pubmed_cache()
    cyp2d6 = load_cyp2d6_docking_results()

    mbi_entries = mbis.get("entries", mbis)
    mmp_pairs = mmps.get("pairs", mmps)
    cyp2d6_evals = cyp2d6.get("docking_evaluations", [])
    cyp2d6_runs = sum(len(c.get("docking_results", {})) for c in cyp2d6_evals)

    status = {
        "js_bytes": len(js_src.encode("utf-8")),
        "css_bytes": len(css_src.encode("utf-8")),
        "layout_engine_bytes": len(layout_src.encode("utf-8")),
        "layout_body_lines": len(layout_body.splitlines()),
        "conformal_body_lines": len(conformal_body.splitlines()),
        "fallback_df_rows": len(df_fallback),
        "literature_mbis_count": len(mbi_entries),
        "mmp_transformations_count": len(mmp_pairs),
        "ncbi_cache_records": len(ncbi_cache),
        "cyp2d6_docking_runs": cyp2d6_runs,
        "bundle_ready": True,
    }

    assert status["ncbi_cache_records"] >= 10
    assert status["cyp2d6_docking_runs"] == 20

    assert status["js_bytes"] > 500
    assert status["css_bytes"] > 500
    assert status["layout_body_lines"] > 50
    assert status["conformal_body_lines"] > 20
    assert status["fallback_df_rows"] == 100
    assert status["literature_mbis_count"] == 10
    assert status["mmp_transformations_count"] == 34

    return status


def generate_standalone_app(output_path: Path = BASE_DIR / "standalone_app.py") -> Path:
    """
    Assembles a completely self-contained Marimo notebook file by inlining:
      1. bioactivation_tracer.js and bioactivation_tracer.css into the AnyWidget class
      2. 2D RDKit layout engine logic
      3. Base64-encoded GZIP fallback payloads for all datasets and benchmark JSONs
      4. All reactive UI Acts (1 through 5) from app.py
    """
    print(f"Generating standalone single-file app: {output_path}...", flush=True)

    app_py_text = (BASE_DIR / "app.py").read_text(encoding="utf-8")
    js_content = get_inlined_js()
    css_content = get_inlined_css()
    layout_engine_code = get_inlined_layout_engine_body()
    conformal_selector_code = get_inlined_conformal_selector_body()

    # Read base64 assets and expected SHA from embedded_assets.py
    from models.embedded_assets import PARQUET_EXPECTED_SHA256
    embedded_src = (MODELS_DIR / "embedded_assets.py").read_text(encoding="utf-8")

    # Extract base64 constants from embedded_assets.py and indent them for def __()
    b64_pattern = re.compile(r'(_[A-Z0-9_]+_GZIP_B64\s*=\s*"""[\s\S]*?""")', re.MULTILINE)
    b64_matches = b64_pattern.findall(embedded_src)
    b64_block = "\n".join("    " + m for m in b64_matches)

    # Escape quotes for inlined JS and CSS
    js_escaped = js_content.replace('\\', '\\\\').replace('"""', r'\"\"\"')
    css_escaped = css_content.replace('\\', '\\\\').replace('"""', r'\"\"\"')

    # Find the split point in app.py where cell 2 starts
    split_marker = "@app.cell\ndef __():\n    def normalize_single_table_value"
    if split_marker not in app_py_text:
        raise ValueError(f"Could not find cell 2 marker '{split_marker}' in app.py")

    remaining_cells = app_py_text[app_py_text.index(split_marker):]

    import tokenize
    tokens = list(tokenize.tokenize(io.BytesIO(remaining_cells.encode("utf-8")).readline))
    comment_lines = set()
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            comment_lines.add(tok.start[0])

    lines = remaining_cells.splitlines()
    filtered_lines = []
    for idx, line in enumerate(lines, start=1):
        if idx in comment_lines and line.strip().startswith("#"):
            continue
        filtered_lines.append(line.rstrip())

    remaining_cells = "\n".join(filtered_lines)

    # Compact leading indentation within multiline HTML strings
    tokens_html = list(tokenize.tokenize(io.BytesIO(remaining_cells.encode("utf-8")).readline))
    string_spans = []
    for tok in tokens_html:
        if tok.type == tokenize.STRING and tok.start[0] != tok.end[0]:
            if "<div" in tok.string or "<table" in tok.string or "<span" in tok.string:
                string_spans.append((tok.start, tok.end))

    line_in_html_string = set()
    for start, end in string_spans:
        for r in range(start[0], end[0]):
            line_in_html_string.add(r + 1)

    html_compressed_lines = []
    for idx, line in enumerate(remaining_cells.splitlines(), start=1):
        if idx in line_in_html_string:
            stripped = line.lstrip()
            if stripped.startswith(
                (
                    "<",
                    "</",
                    "style=",
                    "class=",
                    "font-",
                    "color:",
                    "margin:",
                    "padding:",
                    "border",
                    "background",
                    "gap:",
                    "flex",
                    "width:",
                    "align-",
                )
            ):
                html_compressed_lines.append(stripped)
            else:
                html_compressed_lines.append(line)
        else:
            html_compressed_lines.append(line)

    remaining_cells = "\n".join(html_compressed_lines)
    remaining_cells = re.sub(r"\n{3,}", "\n\n", remaining_cells)

    standalone_code = f'''# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.11.0",
#     "anywidget>=0.9.0",
#     "rdkit>=2023.9.0",
#     "pandas>=2.0.0",
#     "numpy>=1.24.0",
#     "pyarrow>=14.0.0",
#     "traitlets>=5.14.0",
# ]
# ///

# Standalone single-file bundle generated by scripts/bundle_app.py
# All dependencies inlined: BioactivationTracer widget, layout engine, and fallback datasets.

import marimo

__generated_with = "0.11.0"
app = marimo.App(
    width="full",
    app_title="OpenADMET: Cytochrome P450 Bioactivation & Conformal Risk Control",
)


@app.cell
def __():
    import base64
    import csv
    import gzip
    import hashlib
    import html
    import io
    import json
    import math
    import os
    import sys
    import time
    from pathlib import Path
    from typing import Any
    import numpy as np
    import pandas as pd
    import marimo as mo
    import traitlets
    import anywidget
    from rdkit import Chem
    from rdkit.Chem import rdDepictor

    try:
        BASE_DIR = Path(__file__).resolve().parent
    except NameError:
        BASE_DIR = Path.cwd()

    # --- Embedded Datasets & Benchmarks (GZIP + Base64) ---
{b64_block}

    PARQUET_PRIMARY_PATH = BASE_DIR / "data" / "packaged" / "cyp_tdi_curated.parquet"
    PARQUET_EXPECTED_SHA256 = "{PARQUET_EXPECTED_SHA256}"
    DATASET_PROVENANCE_STATUS = "UNINITIALIZED"

    def load_fallback_dataset() -> pd.DataFrame:
        raw_gz = base64.b64decode(_FALLBACK_SAMPLE_GZIP_B64)
        raw_parquet = gzip.decompress(raw_gz)
        return pd.read_parquet(io.BytesIO(raw_parquet))

    def load_literature_mbi_reference_set() -> dict:
        raw_gz = base64.b64decode(_LITERATURE_MBI_GZIP_B64)
        raw_json = gzip.decompress(raw_gz).decode("utf-8")
        return json.loads(raw_json)

    def load_mmp_transformations() -> dict:
        raw_gz = base64.b64decode(_MMP_TRANSFORMATIONS_GZIP_B64)
        raw_json = gzip.decompress(raw_gz).decode("utf-8")
        return json.loads(raw_json)

    def load_ecfp_baseline_results() -> dict:
        p = BASE_DIR / "data" / "packaged" / "ecfp_baseline_results.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return json.loads(gzip.decompress(base64.b64decode(_ECFP_BASELINE_GZIP_B64)).decode("utf-8"))

    def load_dmpnn_baseline_results() -> dict:
        p = BASE_DIR / "data" / "packaged" / "dmpnn_baseline_results.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return json.loads(gzip.decompress(base64.b64decode(_DMPNN_BASELINE_GZIP_B64)).decode("utf-8"))

    def load_tanimoto_shift_summary() -> dict:
        p = BASE_DIR / "data" / "curated" / "tanimoto_shift_summary.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return json.loads(gzip.decompress(base64.b64decode(_TANIMOTO_SHIFT_GZIP_B64)).decode("utf-8"))

    def load_augmented_results() -> dict:
        p = BASE_DIR / "data" / "packaged" / "augmented_results.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return json.loads(gzip.decompress(base64.b64decode(_AUGMENTED_RESULTS_GZIP_B64)).decode("utf-8"))

    def load_docking_ablation_results() -> dict:
        p = BASE_DIR / "data" / "packaged" / "docking_ablation_results.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return json.loads(gzip.decompress(base64.b64decode(_DOCKING_ABLATION_GZIP_B64)).decode("utf-8"))

    def load_txconformal_selection_results() -> dict:
        p = BASE_DIR / "data" / "packaged" / "txconformal_selection_results.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return json.loads(gzip.decompress(base64.b64decode(_TXCONFORMAL_SELECTION_GZIP_B64)).decode("utf-8"))

    def load_oof_error_cases() -> dict:
        p = BASE_DIR / "data" / "packaged" / "oof_error_cases.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return json.loads(gzip.decompress(base64.b64decode(_OOF_ERROR_CASES_GZIP_B64)).decode("utf-8"))

    def load_ncbi_pubmed_cache() -> dict:
        p = BASE_DIR / "data" / "packaged" / "ncbi_pubmed_cache.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return json.loads(gzip.decompress(base64.b64decode(_NCBI_PUBMED_CACHE_GZIP_B64)).decode("utf-8"))

    def load_cyp2d6_docking_results() -> dict:
        p = BASE_DIR / "data" / "packaged" / "cyp2d6_docking_results.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
        return json.loads(gzip.decompress(base64.b64decode(_CYP2D6_DOCKING_GZIP_B64)).decode("utf-8"))

    def get_dataset_provenance_status() -> str:
        global DATASET_PROVENANCE_STATUS
        return DATASET_PROVENANCE_STATUS

    def load_curated_dataset(max_retries: int = 3) -> pd.DataFrame:
        global DATASET_PROVENANCE_STATUS
        if PARQUET_PRIMARY_PATH.exists():
            for attempt in range(1, max(1, max_retries) + 1):
                try:
                    raw_bytes = PARQUET_PRIMARY_PATH.read_bytes()
                    computed_sha = hashlib.sha256(raw_bytes).hexdigest()
                    if computed_sha == PARQUET_EXPECTED_SHA256:
                        df = pd.read_parquet(io.BytesIO(raw_bytes))
                        DATASET_PROVENANCE_STATUS = "PRIMARY_PARQUET_VERIFIED"
                        return df
                    else:
                        break
                except Exception:
                    if attempt < max_retries:
                        time.sleep(0.05 * attempt)
        DATASET_PROVENANCE_STATUS = "EMBEDDED_OFFLINE_FALLBACK"
        return load_fallback_dataset()

    # --- Inlined Layout Engine (Dynamically Sourced from widgets/layout_engine.py) ---
{layout_engine_code}

    # --- Inlined Conformal Selector (Dynamically Sourced from models/txconformal_selector.py) ---
{conformal_selector_code}

    # --- Inlined BioactivationTracer AnyWidget ---
    _INLINED_ESM = """{js_escaped}"""
    _INLINED_CSS = """{css_escaped}"""

    class BioactivationTracer(anywidget.AnyWidget):
        _esm = _INLINED_ESM
        _css = _INLINED_CSS

        layout = traitlets.Dict(default_value={{}}).tag(sync=True)
        overlay_mode = traitlets.Unicode("warheads").tag(sync=True)
        selected_atom_idx = traitlets.CInt(allow_none=True, default_value=None).tag(sync=True)
        selected_atom_metadata = traitlets.Dict(default_value={{}}).tag(sync=True)

        def __init__(
            self,
            smiles: str | None = None,
            layout: dict[str, Any] | None = None,
            overlay_mode: str = "warheads",
            quantum_features: dict[str, Any] | None = None,
            **kwargs: Any,
        ) -> None:
            super().__init__(**kwargs)
            self.overlay_mode = overlay_mode

            if layout is not None:
                self.layout = layout
            elif smiles is not None:
                self.update_smiles(smiles, quantum_features=quantum_features)

        def update_smiles(
            self,
            smiles: str,
            quantum_features: dict[str, Any] | None = None,
            atom_fukui_map: dict[int, float] | None = None,
        ) -> None:
            new_layout = generate_molecule_layout(
                smiles=smiles,
                quantum_features=quantum_features,
                atom_fukui_map=atom_fukui_map,
            )
            self.layout = new_layout
            self.selected_atom_idx = None
            self.selected_atom_metadata = {{}}

        @classmethod
        def from_smiles(
            cls,
            smiles: str,
            quantum_features: dict[str, Any] | None = None,
            overlay_mode: str = "warheads",
        ) -> "BioactivationTracer":
            return cls(smiles=smiles, quantum_features=quantum_features, overlay_mode=overlay_mode)

        @classmethod
        def safe_from_smiles(
            cls,
            smiles: str,
            quantum_features: dict[str, Any] | None = None,
            overlay_mode: str = "warheads",
        ) -> "BioactivationTracer":
            layout = safe_generate_molecule_layout(smiles, quantum_features=quantum_features)
            return cls(layout=layout, overlay_mode=overlay_mode)

    class NCBIEntrezClient:
        """Inlined offline-first NCBI client for standalone bundle."""
        def __init__(
            self,
            api_key: str | None = None,
            email: str | None = None,
            cache_path: Path | None = None,
            timeout: float = 10.0,
        ):
            self.api_key = api_key or os.environ.get("NCBI_API_KEY")
            self.email = email or os.environ.get("NCBI_EMAIL", "")
            self.cache_path = cache_path
            self.timeout = timeout
            self._cache = load_ncbi_pubmed_cache()

        def fetch_summaries(self, pmids: list[str], force_refresh: bool = False) -> dict[str, dict[str, Any]]:
            results = {{}}
            for pmid in pmids:
                p = str(pmid).strip()
                if p in self._cache:
                    results[p] = self._cache[p]
                else:
                    results[p] = {{
                        "pmid": p,
                        "title": "NCBI Metadata (Offline Fallback - Uncached Reference PMID)",
                        "journal": "N/A",
                        "pubdate": "N/A",
                        "doi": None,
                        "authors": [],
                        "author_display": "N/A",
                        "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{{p}}/",
                        "doi_url": None,
                        "ncbi_verified": False,
                    }}
            return results

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


{remaining_cells}
'''

    output_path.write_text(standalone_code, encoding="utf-8")
    file_size_bytes = output_path.stat().st_size
    file_size_kb = file_size_bytes / 1024
    print(f"Successfully generated {output_path} ({file_size_bytes} bytes, {file_size_kb:.1f} KB).", flush=True)
    if file_size_bytes >= 200_000:
        raise ValueError(
            f"standalone_app.py exceeds 200,000 bytes decimal budget: {file_size_bytes} bytes"
        )
    return output_path


if __name__ == "__main__":
    status = verify_bundle_components()
    print("Single-file bundle components verified successfully:")
    for k, v in status.items():
        print(f"  {k}: {v}")

    standalone_file = generate_standalone_app()
    print(f"Done! Standalone app created at {standalone_file}.")
