"""
EC-3-1-03: BioactivationTracer AnyWidget Python Wrapper & Traitlet Integration.

Provides the AnyWidget class bridging Python RDKit 2D layouts and quantum reactivity
features with client-side ES6 SVG rendering in Marimo notebooks.
"""

from __future__ import annotations

import pathlib
from typing import Any
import anywidget
import traitlets

from widgets.layout_engine import (
    generate_molecule_layout,
    safe_generate_molecule_layout,
)

_MODULE_DIR = pathlib.Path(__file__).parent
_JS_PATH = _MODULE_DIR / "bioactivation_tracer.js"
_CSS_PATH = _MODULE_DIR / "bioactivation_tracer.css"

# Read asset files or provide inlined fallback
if _JS_PATH.exists():
    _DEFAULT_ESM = _JS_PATH.read_text(encoding="utf-8")
else:
    _DEFAULT_ESM = "export function render({ model, el }) { el.innerHTML = 'BioactivationTracer JS missing'; }"

if _CSS_PATH.exists():
    _DEFAULT_CSS = _CSS_PATH.read_text(encoding="utf-8")
else:
    _DEFAULT_CSS = ".bat-container { border: 1px solid #ccc; }"


class BioactivationTracer(anywidget.AnyWidget):
    """
    Interactive 2D molecule viewer with metabolic bioactivation overlays,
    quantum reactivity halos, and bidirectional atom selection state.
    """
    _esm = _DEFAULT_ESM
    _css = _DEFAULT_CSS

    # Synchronized Traitlets
    layout = traitlets.Dict(default_value={}).tag(sync=True)
    overlay_mode = traitlets.Unicode("warheads").tag(sync=True)
    selected_atom_idx = traitlets.CInt(allow_none=True, default_value=None).tag(sync=True)
    selected_atom_metadata = traitlets.Dict(default_value={}).tag(sync=True)

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
        """
        Updates the 2D layout and warhead annotations for a new SMILES string.
        """
        new_layout = generate_molecule_layout(
            smiles=smiles,
            quantum_features=quantum_features,
            atom_fukui_map=atom_fukui_map,
        )
        self.layout = new_layout
        # Reset selection on molecule change
        self.selected_atom_idx = None
        self.selected_atom_metadata = {}

    @classmethod
    def from_smiles(
        cls,
        smiles: str,
        quantum_features: dict[str, Any] | None = None,
        overlay_mode: str = "warheads",
    ) -> BioactivationTracer:
        """Convenience factory to instantiate directly from a SMILES string."""
        return cls(smiles=smiles, quantum_features=quantum_features, overlay_mode=overlay_mode)

    @classmethod
    def safe_from_smiles(
        cls,
        smiles: str,
        quantum_features: dict[str, Any] | None = None,
        overlay_mode: str = "warheads",
    ) -> BioactivationTracer:
        """Defensive factory that gracefully handles unparseable SMILES strings."""
        layout = safe_generate_molecule_layout(smiles, quantum_features=quantum_features)
        return cls(layout=layout, overlay_mode=overlay_mode)


def get_inlined_widget_definition() -> str:
    """
    Returns a Python code snippet with inlined JS and CSS strings for single-file deployment.
    """
    esm_escaped = _DEFAULT_ESM.replace('"""', r'\"\"\"')
    css_escaped = _DEFAULT_CSS.replace('"""', r'\"\"\"')

    return f'''
import anywidget
import traitlets

class BioactivationTracer(anywidget.AnyWidget):
    _esm = """{esm_escaped}"""
    _css = """{css_escaped}"""

    layout = traitlets.Dict(default_value={{}}).tag(sync=True)
    overlay_mode = traitlets.Unicode("warheads").tag(sync=True)
    selected_atom_idx = traitlets.CInt(allow_none=True, default_value=None).tag(sync=True)
    selected_atom_metadata = traitlets.Dict(default_value={{}}).tag(sync=True)
'''
