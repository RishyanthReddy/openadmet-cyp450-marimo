"""
EC-INTEGRATION-P4-01: Phase 4 Seam Integration Acceptance Gate.
Validates end-to-end platform reliability, defensive chemotype fuzzing,
NCBI Entrez E-Utilities integration, Chrome DevTools browser verification,
and standalone offline portability.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

APP_PATH = BASE_DIR / "app.py"
STANDALONE_PATH = BASE_DIR / "standalone_app.py"
CACHE_FILE = BASE_DIR / "data" / "packaged" / "ncbi_pubmed_cache.json"
DEVTOOLS_REPORT = BASE_DIR / "docs" / "DEVTOOLS_AUDIT_REPORT.json"


def find_chrome_binary() -> str:
    env_bin = os.environ.get("CHROME_BIN") or os.environ.get("GOOGLE_CHROME_BIN")
    if env_bin and Path(env_bin).exists():
        return env_bin
    candidates = [
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
    ]
    for cand in candidates:
        if cand and Path(cand).exists():
            return str(cand)
    return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class TestPhase4MarimoIntegrity:
    """Quality Gate 4.1: Static DAG and compilation cleanliness."""

    def test_marimo_check_master_app_code_zero(self):
        res = subprocess.run(
            [sys.executable, "-m", "marimo", "check", str(APP_PATH)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"marimo check app.py failed:\n{res.stderr}"

    def test_marimo_check_standalone_app_code_zero(self):
        res = subprocess.run(
            [sys.executable, "-m", "marimo", "check", str(STANDALONE_PATH)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"marimo check standalone_app.py failed:\n{res.stderr}"

    def test_zero_deprecation_warnings_on_compile(self):
        res = subprocess.run(
            [sys.executable, "-W", "error", "-m", "py_compile", str(APP_PATH), str(STANDALONE_PATH)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"py_compile failed:\n{res.stderr}"


class TestPhase4NCBIEntrezHygiene:
    """Quality Gate 4.2: NCBI Entrez client, cache provenance, and literature parity."""

    def test_ncbi_cache_curated_ten_records_and_provenance(self):
        assert CACHE_FILE.exists(), "NCBI cache file missing"
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        assert len(cache) == 10, f"Expected exactly 10 curated records, got {len(cache)}"

        for pmid, rec in cache.items():
            assert rec["ncbi_verified"] is True
            assert rec.get("title") and len(rec["title"]) > 10
            assert rec.get("journal") and rec["journal"] != "N/A"
            assert "retrieved_at_utc" in rec
            assert rec["source_endpoint"] == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
            assert "provenance_sha256" in rec and len(rec["provenance_sha256"]) == 64

    def test_ncbi_doi_and_pubmed_coverage(self):
        cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        with_doi = [r for r in cache.values() if r.get("doi")]
        without_doi = [r for r in cache.values() if not r.get("doi")]

        assert len(with_doi) == 8, f"Expected 8/10 DOI links, got {len(with_doi)}"
        assert len(without_doi) == 2, f"Expected 2/10 print-era PMIDs without DOI, got {len(without_doi)}"

        # All 10 must have live PubMed links
        for r in cache.values():
            assert r["pubmed_url"].startswith("https://pubmed.ncbi.nlm.nih.gov/")

    def test_ncbi_no_hardcoded_personal_credentials(self, monkeypatch):
        from models.ncbi_client import NCBIEntrezClient
        monkeypatch.setattr("models.ncbi_client._get_env_fallback", lambda k, default=None: None)
        monkeypatch.delenv("NCBI_EMAIL", raising=False)
        monkeypatch.delenv("NCBI_API_KEY", raising=False)

        client = NCBIEntrezClient(email=None, cache_path=Path("/tmp/test_cache.json"))
        assert "@gmail.com" not in (client.email or "")

    def test_ncbi_partial_response_resilience(self, tmp_path):
        from models.ncbi_client import NCBIEntrezClient
        client = NCBIEntrezClient(cache_path=tmp_path / "cache.json")
        client._query_ncbi = lambda pmids: {
            "9652662": {
                "pmid": "9652662",
                "title": "Mibefradil",
                "journal": "Lancet",
                "pubdate": "1998",
                "authors": ["A"],
                "author_display": "A",
                "doi": "10.1016/s0140-6736",
                "pubmed_url": "https://pubmed.ncbi.nlm.nih.gov/9652662/",
                "doi_url": "https://doi.org/10.1016/s0140-6736",
                "ncbi_verified": True,
            }
        }
        res = client.fetch_summaries(["9652662", "0000000"], force_refresh=True)
        assert res["9652662"]["ncbi_verified"] is True
        assert res["0000000"]["ncbi_verified"] is False
        assert "Partial Response" in res["0000000"]["title"]


class TestPhase4DefensiveFuzzingAndAnyWidget:
    """Quality Gate 4.3: Defensive chemotype layout and safe widget constructors."""

    def test_safe_layout_engine_fuzzing(self):
        from widgets.layout_engine import safe_generate_molecule_layout

        # Malformed syntax
        bad = safe_generate_molecule_layout("TOTALLY_INVALID_SMILES")
        assert bad["is_valid"] is False
        assert bad["error"] is not None
        assert bad["num_atoms"] == 0

        # Boundary chemotypes
        macro = safe_generate_molecule_layout("C1" + "C" * 30 + "C1")
        assert macro["is_valid"] is True
        assert macro["num_atoms"] == 32

        salt = safe_generate_molecule_layout("[Na+].[Cl-]")
        assert "is_valid" in salt

    def test_safe_bioactivation_tracer_constructor(self):
        from widgets.bioactivation_tracer import BioactivationTracer
        widget = BioactivationTracer.safe_from_smiles("INVALID_CHEMISTRY(((")
        assert isinstance(widget, BioactivationTracer)
        assert widget.layout["is_valid"] is False

    def test_bioactivation_tracer_js_xss_protection(self):
        js_path = BASE_DIR / "widgets" / "bioactivation_tracer.js"
        js_code = js_path.read_text(encoding="utf-8")
        # Ensure warning banner and badge use textContent and safe DOM construction
        assert "strongEl.textContent" in js_code
        assert "msgSpan.textContent" in js_code
        assert "svgWrapper.replaceChildren(warnBox)" in js_code
        assert "badgeEl.textContent" in js_code
        assert "badgeEl.innerHTML" not in js_code

    def test_all_application_paths_use_safe_from_smiles(self):
        """Asserts strictly zero occurrences of strict BioactivationTracer.from_smiles in app.py and standalone_app.py."""
        app_code = APP_PATH.read_text(encoding="utf-8")
        standalone_code = STANDALONE_PATH.read_text(encoding="utf-8")

        assert "BioactivationTracer.from_smiles(" not in app_code, "app.py still contains strict from_smiles"
        assert "BioactivationTracer.from_smiles(" not in standalone_code, "standalone_app.py still contains strict from_smiles"

    def test_custom_smi_html_escaped(self):
        """Asserts that custom SMILES and fuzzing outputs are escaped via html.escape."""
        app_code = APP_PATH.read_text(encoding="utf-8")
        assert "html.escape(custom_smi)" in app_code
        assert "html.escape(str(layout.get(" in app_code


class TestPhase4DevToolsAuditReportArtifact:
    """Quality Gate 4.4: Chrome DevTools audit report verified."""

    def test_devtools_audit_artifact_passed(self):
        assert DEVTOOLS_REPORT.exists(), f"DevTools report missing at {DEVTOOLS_REPORT}"
        data = json.loads(DEVTOOLS_REPORT.read_text(encoding="utf-8"))
        assert data["audit_status"] == "PASS"
        assert data["unhandled_console_errors"] == 0
        assert len(data.get("network_failures", [])) == 0
        assert data["total_svg_elements"] >= 70
        assert data["total_anywidget_instances"] >= 2
        assert data["details"]["reactive_render_p95_ms"] < 500.0


class TestPhase4OfflineStandalonePortability:
    """Quality Gate 4.5: True asset independence in standalone mode."""

    def test_embedded_assets_loader(self):
        from models.embedded_assets import (
            load_ncbi_pubmed_cache,
            load_literature_mbi_reference_set,
            load_docking_ablation_results,
        )
        cache = load_ncbi_pubmed_cache()
        assert len(cache) == 10
        mbi = load_literature_mbi_reference_set()
        assert len(mbi["entries"]) == 10
        dock = load_docking_ablation_results()
        assert len(dock["docking_evaluations"]) == 10
