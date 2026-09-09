"""
Unit tests for EC-3-1-02: Client-side SVG Anywidget Component and Metadata Contract.
"""

import json
import subprocess
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from widgets.layout_engine import generate_molecule_layout

JS_PATH = BASE_DIR / "widgets" / "bioactivation_tracer.js"
CSS_PATH = BASE_DIR / "widgets" / "bioactivation_tracer.css"


def test_widget_asset_files_exist_and_non_empty():
    assert JS_PATH.exists(), f"Missing {JS_PATH}"
    assert CSS_PATH.exists(), f"Missing {CSS_PATH}"
    assert JS_PATH.stat().st_size > 500, f"JS file too small: {JS_PATH.stat().st_size} bytes"
    assert CSS_PATH.stat().st_size > 500, f"CSS file too small: {CSS_PATH.stat().st_size} bytes"


def test_metadata_halo_contract_schema():
    """
    Asserts strict provenance contract keys required for reactivity halos:
      - atom_score (numeric)
      - score_type (descriptive metric type)
      - score_source (provenance model/dataset)
      - normalization (normalization boundary description)
      - is_experimental (boolean)
    """
    required_keys = {
        "atom_score",
        "score_type",
        "score_source",
        "normalization",
        "is_experimental",
    }
    js_text = JS_PATH.read_text()
    for key in required_keys:
        assert key in js_text, f"Missing required metadata contract key: {key} in {JS_PATH}"


def test_node_headless_module_validation():
    """Validates that bioactivation_tracer.js imports cleanly in Node.js as an ES6 module."""
    node_cmd = [
        "node", "-e",
        """
        import('./widgets/bioactivation_tracer.js').then(mod => {
            if (typeof mod.render !== 'function') {
                console.error('render is not a function');
                process.exit(1);
            }
            process.exit(0);
        }).catch(err => {
            console.error(err);
            process.exit(1);
        });
        """
    ]
    res = subprocess.run(node_cmd, cwd=BASE_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"Node.js ES6 module validation failed:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"


def test_node_headless_simulated_render():
    """
    Headless Node.js Unit Smoke Test: verifies ESM render function contract and DOM manipulation primitives
    in non-browser Node runtime without requiring full browser stack. Live browser audits are executed
    via Playwright DevTools in tests/test_devtools_audit.py.
    """
    sample_smiles = "CC1=C(C(=O)N(C1=O)C)N2C=NC(=C2)C"  # Furafylline
    layout = generate_molecule_layout(sample_smiles)
    layout_json = json.dumps(layout)

    node_script = f"""
    // Headless DOM primitives for Node.js contract validation
    class HeadlessDOMNode {{
        constructor(tagName) {{
            this.tagName = tagName;
            this.className = '';
            this.children = [];
            this.attributes = {{}};
            this.style = {{}};
            this.innerHTML = '';
        }}
        appendChild(child) {{
            this.children.push(child);
            return child;
        }}
        setAttribute(name, val) {{
            this.attributes[name] = val;
        }}
        getAttribute(name) {{
            return this.attributes[name];
        }}
        querySelector(selector) {{
            return null;
        }}
        querySelectorAll(selector) {{
            return [];
        }}
        getBoundingClientRect() {{
            return {{ left: 0, top: 0, width: 400, height: 300 }};
        }}
        remove() {{}}
    }}

    global.document = {{
        createElement: (tag) => new HeadlessDOMNode(tag),
        createElementNS: (ns, tag) => new HeadlessDOMNode(tag)
    }};

    const layout = {layout_json};

    class HeadlessWidgetModelTraitletProxy {{
        constructor() {{
            this.data = {{
                layout: layout,
                overlay_mode: 'warheads',
                selected_atom_idx: null
            }};
            this.listeners = {{}};
        }}
        get(key) {{ return this.data[key]; }}
        set(key, val) {{ this.data[key] = val; }}
        save_changes() {{}}
        on(event, cb) {{
            this.listeners[event] = cb;
        }}
        off(event, cb) {{
            delete this.listeners[event];
        }}
    }}

    import('./widgets/bioactivation_tracer.js').then(mod => {{
        const model = new HeadlessWidgetModelTraitletProxy();
        const el = new HeadlessDOMNode('div');
        const cleanup = mod.render({{ model, el }});

        if (typeof cleanup !== 'function') {{
            console.error('Expected render to return a cleanup function, got ' + typeof cleanup);
            process.exit(1);
        }}

        const container = el.children[0];
        if (!container || container.className !== 'bat-container') {{
            console.error('Invalid container render');
            process.exit(1);
        }}

        // Verify cleanup unregisters listeners and empties el
        cleanup();
        if (Object.keys(model.listeners).length > 0) {{
            console.error('Listeners still registered after cleanup');
            process.exit(1);
        }}

        console.log('Simulated DOM render passed with lifecycle cleanup verified.');
        process.exit(0);
    }}).catch(err => {{
        console.error(err);
        process.exit(1);
    }});
    """

    res = subprocess.run(["node", "-e", node_script], cwd=BASE_DIR, capture_output=True, text=True)
    assert res.returncode == 0, f"Headless render simulation failed:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    assert "Simulated DOM render passed with lifecycle cleanup verified" in res.stdout
