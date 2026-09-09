#!/usr/bin/env python3
"""
Builds spikes/spike_02_vertical_slice.py cleanly using template substitution.
"""

import gzip
import base64
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JSON_PATH = BASE_DIR / "data" / "processed" / "slice_100_payload.json"
NOTEBOOK_PATH = BASE_DIR / "spikes" / "spike_02_vertical_slice.py"

with open(JSON_PATH, "rb") as f:
    raw_bytes = f.read()

b64_payload = base64.b64encode(gzip.compress(raw_bytes)).decode("ascii")

TEMPLATE = '''# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.24.0",
#     "anywidget>=0.9.13",
#     "traitlets>=5.14.0",
#     "pandas>=2.0.0",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="full", app_title="CYP-TDI 100-Molecule Vertical Slice")


@app.cell
def __():
    import marimo as mo
    import base64
    import gzip
    import json
    from pathlib import Path
    import pandas as pd
    import anywidget
    import traitlets

    # Embedded 59.5KB payload fallback for 100% cloud portability on molab.marimo.io
    EMBEDDED_B64_PAYLOAD = "%%B64_PAYLOAD%%"

    # Load local file if available, otherwise decompress embedded fallback
    local_path = Path("data/processed/slice_100_payload.json")
    if local_path.exists():
        with open(local_path, "r") as f:
            molecules_data = json.load(f)
    else:
        decompressed = gzip.decompress(base64.b64decode(EMBEDDED_B64_PAYLOAD.encode("ascii")))
        molecules_data = json.loads(decompressed.decode("utf-8"))

    df_slice = pd.DataFrame([
        {
            "ID": m["id"],
            "SMILES": m["smiles"],
            "CYP3A4 TDI (True)": "POSITIVE (TDI)" if m["cyp3a4_is_tdi"] else "NEGATIVE (Safe)",
            "Baseline Prob": m["baseline_prob"],
            "Baseline Pred": "TDI Risk" if m["baseline_pred"] else "Low Risk",
            "MW": m["mw"],
            "LogP": m["logp"],
            "TPSA": m["tpsa"],
            "MS Ionization Area": f"{m['nh4f_area']:,.0f}" if m.get("nh4f_area") else "N/A",
        }
        for m in molecules_data
    ])

    return anywidget, base64, df_slice, gzip, json, molecules_data, mo, traitlets


@app.cell
def __(anywidget, traitlets):
    class BioactivationTracerWidget(anywidget.AnyWidget):
        """Custom anywidget for client-side vector chemical rendering and atom-level halo highlighting."""
        _esm = """
        function render({ model, el }) {
            const container = document.createElement("div");
            container.style.display = "flex";
            container.style.flexDirection = "column";
            container.style.alignItems = "center";
            container.style.justifyContent = "center";
            container.style.backgroundColor = "#0f172a";
            container.style.border = "1px solid #334155";
            container.style.borderRadius = "12px";
            container.style.padding = "16px";
            container.style.boxShadow = "0 10px 25px -5px rgba(0, 0, 0, 0.3)";
            container.style.fontFamily = "system-ui, -apple-system, sans-serif";

            function draw() {
                const mol = model.get("molecule");
                if (!mol || !mol.atoms || mol.atoms.length === 0) {
                    container.innerHTML = `<div style="color: #64748b; padding: 40px;">Select a molecule from the table to inspect vector bioactivation halos.</div>`;
                    return;
                }

                // Compute bounding box
                let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
                mol.atoms.forEach(a => {
                    if (a.x < minX) minX = a.x;
                    if (a.x > maxX) maxX = a.x;
                    if (a.y < minY) minY = a.y;
                    if (a.y > maxY) maxY = a.y;
                });

                const width = 440;
                const height = 300;
                const padding = 36;

                const dx = (maxX - minX) || 1;
                const dy = (maxY - minY) || 1;
                const scale = Math.min((width - 2 * padding) / dx, (height - 2 * padding) / dy);

                function toSvgX(x) {
                    return padding + (x - minX) * scale + ((width - 2 * padding) - dx * scale) / 2;
                }
                function toSvgY(y) {
                    return height - (padding + (y - minY) * scale + ((height - 2 * padding) - dy * scale) / 2);
                }

                let svg = `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" style="overflow: visible;">
                    <defs>
                        <radialGradient id="highRiskHalo" cx="50%" cy="50%" r="50%">
                            <stop offset="0%" stop-color="#ef4444" stop-opacity="0.85"/>
                            <stop offset="60%" stop-color="#f97316" stop-opacity="0.4"/>
                            <stop offset="100%" stop-color="#ef4444" stop-opacity="0"/>
                        </radialGradient>
                        <radialGradient id="moderateRiskHalo" cx="50%" cy="50%" r="50%">
                            <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.75"/>
                            <stop offset="70%" stop-color="#0284c7" stop-opacity="0.3"/>
                            <stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
                        </radialGradient>
                    </defs>`;

                // 1. Render Halo layers behind bonds
                mol.atoms.forEach(a => {
                    if (a.halo_intensity > 0.15) {
                        const cx = toSvgX(a.x);
                        const cy = toSvgY(a.y);
                        const r = 16 + a.halo_intensity * 20;
                        const grad = a.halo_intensity > 0.5 ? "url(#highRiskHalo)" : "url(#moderateRiskHalo)";
                        svg += `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${grad}" pointer-events="none"/>`;
                    }
                });

                // 2. Render Bonds
                if (mol.bonds) {
                    mol.bonds.forEach(b => {
                        const a1 = mol.atoms[b.source];
                        const a2 = mol.atoms[b.target];
                        const x1 = toSvgX(a1.x), y1 = toSvgY(a1.y);
                        const x2 = toSvgX(a2.x), y2 = toSvgY(a2.y);

                        if (b.order === 2) {
                            const offset = 2.5;
                            const angle = Math.atan2(y2 - y1, x2 - x1) + Math.PI / 2;
                            const ox = Math.cos(angle) * offset;
                            const oy = Math.sin(angle) * offset;
                            svg += `<line x1="${x1 + ox}" y1="${y1 + oy}" x2="${x2 + ox}" y2="${y2 + oy}" stroke="#94a3b8" stroke-width="2"/>`;
                            svg += `<line x1="${x1 - ox}" y1="${y1 - oy}" x2="${x2 - ox}" y2="${y2 - oy}" stroke="#94a3b8" stroke-width="2"/>`;
                        } else {
                            svg += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#cbd5e1" stroke-width="2.5" stroke-linecap="round"/>`;
                        }
                    });
                }

                // 3. Render Atom Nodes & Labels
                const elementColors = {
                    "N": "#60a5fa",
                    "O": "#f87171",
                    "S": "#facc15",
                    "F": "#4ade80",
                    "Cl": "#2dd4bf",
                    "Br": "#c084fc",
                    "P": "#fb923c"
                };

                mol.atoms.forEach(a => {
                    const cx = toSvgX(a.x);
                    const cy = toSvgY(a.y);
                    const isHetero = a.symbol !== "C";

                    if (isHetero) {
                        const color = elementColors[a.symbol] || "#e2e8f0";
                        svg += `<circle cx="${cx}" cy="${cy}" r="11" fill="#0f172a" stroke="#334155" stroke-width="1.5"/>`;
                        svg += `<text x="${cx}" y="${cy + 4}" font-size="12" font-weight="bold" fill="${color}" text-anchor="middle" font-family="system-ui">${a.symbol}</text>`;
                    } else if (a.halo_intensity > 0.3) {
                        svg += `<circle cx="${cx}" cy="${cy}" r="4" fill="#f8fafc"/>`;
                    }
                });

                svg += `</svg>`;

                container.innerHTML = `
                    <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 13px; font-weight: 600; color: #38bdf8;">BioactivationTracer Vector View</span>
                        <span style="font-size: 11px; color: #94a3b8;">${mol.id} • Halo Gradient Threshold: 0.15</span>
                    </div>
                    ${svg}
                    <div style="display: flex; gap: 16px; margin-top: 8px; font-size: 11px; color: #94a3b8;">
                        <span style="display: flex; align-items: center; gap: 4px;"><span style="width: 10px; height: 10px; border-radius: 50%; background: #ef4444; display: inline-block;"></span> High Susceptibility Halo</span>
                        <span style="display: flex; align-items: center; gap: 4px;"><span style="width: 10px; height: 10px; border-radius: 50%; background: #38bdf8; display: inline-block;"></span> Moderate Polar Response</span>
                    </div>
                `;
            }

            model.on("change:molecule", draw);
            draw();
            el.appendChild(container);
        }
        export default { render };
        """
        molecule = traitlets.Dict(default_value={}).tag(sync=True)

    tracer_widget = BioactivationTracerWidget()
    return BioactivationTracerWidget, tracer_widget


@app.cell
def __(df_slice, mo):
    molecule_table = mo.ui.table(
        df_slice,
        selection="single",
        pagination=True,
        page_size=8,
        label="100-Molecule Stratified Dataset Slice (OpenADMET CYP3A4 TDI Benchmark)"
    )
    return (molecule_table,)


@app.cell
def __(molecule_table, molecules_data, tracer_widget):
    # Reactive bridge: update widget when table row selection changes
    selected_idx = 0
    if molecule_table.value is not None and len(molecule_table.value) > 0:
        selected_id = molecule_table.value.iloc[0]["ID"]
        # Find matching molecule in full payload
        for i, m in enumerate(molecules_data):
            if m["id"] == selected_id:
                selected_idx = i
                break

    selected_mol = molecules_data[selected_idx]
    tracer_widget.molecule = selected_mol
    return selected_idx, selected_mol


@app.cell
def __(mo, selected_mol):
    is_positive = selected_mol["cyp3a4_is_tdi"]
    prob = selected_mol["baseline_prob"]
    pred = selected_mol["baseline_pred"]

    status_color = "#ef4444" if is_positive else "#10b981"
    status_text = "POSITIVE (Confirmed TDI Liability)" if is_positive else "NEGATIVE (Safe Non-TDI)"

    pred_color = "#ef4444" if pred else "#10b981"
    pred_text = "HIGH TDI RISK" if pred else "LOW TDI RISK"

    nh4f = f"{selected_mol['nh4f_area']:,.0f} area units" if selected_mol.get("nh4f_area") else "Not tested in Octant library"

    callout_html = f"""
    <div style="background: #1e293b; border-left: 4px solid {status_color}; padding: 16px; border-radius: 8px; color: #f8fafc; font-family: system-ui; height: 100%; box-sizing: border-box;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h3 style="margin: 0; font-size: 18px; color: #f8fafc;">Compound: <span style="color: #38bdf8;">{selected_mol['id']}</span></h3>
            <span style="background: {status_color}22; color: {status_color}; border: 1px solid {status_color}; font-weight: bold; padding: 4px 10px; border-radius: 9999px; font-size: 12px;">Assay: {status_text}</span>
        </div>
        <p style="margin: 0 0 12px 0; font-family: monospace; font-size: 12px; color: #cbd5e1; word-break: break-all;">
            {selected_mol['smiles']}
        </p>
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 12px; background: #0f172a; padding: 12px; border-radius: 6px;">
            <div>
                <div style="font-size: 11px; color: #94a3b8;">ECFP4 Model Prob</div>
                <div style="font-size: 15px; font-weight: bold; color: {pred_color};">{prob:.3f} ({pred_text})</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #94a3b8;">Molecular Weight</div>
                <div style="font-size: 15px; font-weight: bold; color: #f8fafc;">{selected_mol['mw']} g/mol</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #94a3b8;">Calculated LogP</div>
                <div style="font-size: 15px; font-weight: bold; color: #f8fafc;">{selected_mol['logp']}</div>
            </div>
            <div>
                <div style="font-size: 11px; color: #94a3b8;">Topological PSA</div>
                <div style="font-size: 15px; font-weight: bold; color: #f8fafc;">{selected_mol['tpsa']} Å²</div>
            </div>
        </div>
        <div style="margin-top: 12px; font-size: 12px; color: #94a3b8;">
            <strong>Buffer-Specific Mass Spec QC:</strong> {nh4f}
        </div>
    </div>
    """
    card = mo.Html(callout_html)
    return card, is_positive, nh4f, pred, pred_color, pred_text, prob, status_color, status_text


@app.cell
def __(card, mo, molecule_table, tracer_widget):
    header = mo.md(
        """
        # Phase 0 Milestone: 100-Molecule Baseline Vertical Slice
        > **Task `EC-0-4-01`**: Demonstrating end-to-end data ingestion $\\to$ 2,048-bit ECFP4 baseline modeling $\\to$ reactive molecule selection $\\to$ client-side `BioactivationTracer` anywidget vector rendering.
        """
    )
    ui_layout = mo.vstack([
        header,
        mo.hstack([tracer_widget, card], justify="start", align="stretch", gap=2),
        molecule_table
    ], gap=1.5)
    return header, ui_layout


@app.cell
def __(ui_layout):
    ui_layout
    return


if __name__ == "__main__":
    app.run()
'''

final_content = TEMPLATE.replace("%%B64_PAYLOAD%%", b64_payload)

with open(NOTEBOOK_PATH, "w") as f:
    f.write(final_content)

print(f"✓ Built {NOTEBOOK_PATH} ({NOTEBOOK_PATH.stat().st_size:,} bytes)")
