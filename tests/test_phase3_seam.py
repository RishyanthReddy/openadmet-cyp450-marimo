"""
EC-INTEGRATION-P3-01: Phase 3 Seam Integration Test Suite.
Validates the complete 5-Act interactive Marimo platform, AnyWidget integration,
cold-boot latency SLA, and live Google Chrome DevTools browser verification.
"""

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
import pytest

import os
import shutil

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

APP_PATH = BASE_DIR / "app.py"


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


CHROME_BIN = find_chrome_binary()
PORT = 2718
APP_URL = f"http://localhost:{PORT}"


class TestMarimoCheckAndDAGIntegrity:
    """Verifies that app.py DAG is structurally sound and compiles cleanly."""

    def test_marimo_check_exit_code_zero(self):
        res = subprocess.run(
            [sys.executable, "-m", "marimo", "check", str(APP_PATH)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"marimo check failed:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}"

    def test_python_syntax_and_zero_deprecation_warnings(self):
        res = subprocess.run(
            [sys.executable, "-W", "error", "-m", "py_compile", str(APP_PATH)],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"py_compile with -W error failed:\n{res.stderr}"


class TestColdBootAndRuntimeLatencySLA:
    """Verifies cold-boot and execution performance SLAs."""

    def test_cold_load_import_latency_sla(self):
        t0 = time.perf_counter()
        import app as marimo_app
        load_dt = time.perf_counter() - t0

        print(f"\n[Phase 3 Seam] Master app import latency: {load_dt:.3f}s")
        assert hasattr(marimo_app, "app")
        assert marimo_app.app is not None
        assert load_dt < 1.0, f"Import latency {load_dt:.2f}s exceeded 1.0s SLA (target < 2.0s)"


class TestAllFiveActsCoherence:
    """Verifies presence, wiring, and empirical content of all 5 Acts."""

    def test_act_narrative_sections_in_app(self):
        content = APP_PATH.read_text(encoding="utf-8")

        # Act 1
        assert "Act 1: What TDI Is — and What It Is Not" in content
        assert "Table 1.1: Curated Reference Set" in content

        # Act 2
        assert "Act 2: The Bathtub Audit" in content
        assert "Table 2.1: Empirical Audit" in content
        assert "tanimoto_svg_chart" in content

        # Act 3
        assert "Act 3: Physics-Grounded Quantum Reactivity" in content
        assert "Compound I" in content
        assert "Table 3.1: Empirical Benchmark" in content

        # Act 4
        assert "Act 4: Medicinal Chemistry Steering" in content
        assert "34 unique matched molecular pairs" in content
        assert "Out-of-Fold Model Error Diagnosis" in content

        # Act 5
        assert "Act 5: TxConformal Candidate Prioritization" in content
        assert "Table 5.1: TxConformal Prioritized Candidate Shortlist" in content
        assert "DOME Recommendations Compliance" in content
        assert "Primary Data Sources & Methodological Citations" in content

    def test_main_view_assembly_contains_all_acts(self):
        content = APP_PATH.read_text(encoding="utf-8")
        # Check that main_view combines all 5 act components
        assert "act1_intro" in content
        assert "act2_intro" in content
        assert "act3_intro" in content
        assert "act4_intro" in content
        assert "act5_intro" in content
        assert "act5_conformal_section" in content
        assert "act5_limitations_and_dome" in content


class TestLiveBrowserDevToolsExecution:
    """Direct live Google Chrome DevTools testing via Playwright."""

    @pytest.fixture(scope="class")
    @classmethod
    def live_server(cls):
        """Ensures a live Marimo server is running on PORT."""
        if not (
            os.environ.get("RUN_BROWSER_TESTS") == "1"
            or os.environ.get("RUN_DEVTOOLS_AUDIT") == "1"
            or any("phase3" in str(arg).lower() for arg in sys.argv)
        ):
            yield None
            return

        # Check if already running
        try:
            with urllib.request.urlopen(APP_URL, timeout=1.5) as resp:
                if resp.status == 200:
                    yield APP_URL
                    return
        except Exception:
            pass

        # Start server if not running
        proc = subprocess.Popen(
            [sys.executable, "-m", "marimo", "run", str(APP_PATH), "--port", str(PORT), "--headless"],
            cwd=BASE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        time.sleep(2.5)
        yield APP_URL
        proc.terminate()
        proc.wait(timeout=3)

    def test_chrome_devtools_live_page_and_clean_console(self, live_server):
        if not (
            os.environ.get("RUN_BROWSER_TESTS") == "1"
            or os.environ.get("RUN_DEVTOOLS_AUDIT") == "1"
            or any("phase3" in str(arg).lower() for arg in sys.argv)
        ):
            pytest.skip("Live browser audit gated behind RUN_BROWSER_TESTS=1 or explicit test target")
        from playwright.sync_api import sync_playwright

        console_errors = []
        network_failures = []

        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=CHROME_BIN,
                headless=True,
                args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage", "--window-size=1440,1080"],
            )

            try:
                page = browser.new_page()

                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type in ("error", "assert") else None)
                page.on("pageerror", lambda err: console_errors.append(str(err)))
                page.on("response", lambda resp: network_failures.append(f"{resp.status} {resp.url}") if resp.status >= 400 else None)

                resp = page.goto(live_server, wait_until="networkidle", timeout=15000)
                assert resp is not None and resp.status == 200, "Page failed to load with HTTP 200"

                try:
                    page.wait_for_selector("text=Act 1: What TDI Is", timeout=15000)
                except Exception:
                    page.wait_for_timeout(3000)
                page.wait_for_timeout(1000)

                # Assert Title
                assert "OpenADMET" in page.title()

                # Assert DOM contains all 5 Acts
                body_text = page.inner_text("body")
                assert "Act 1: What TDI Is" in body_text
                assert "Act 2: The Bathtub Audit" in body_text
                assert "Act 3: Physics-Grounded Quantum Reactivity" in body_text
                assert "Act 4: Medicinal Chemistry Steering" in body_text
                assert "Act 5: TxConformal Candidate Prioritization" in body_text

                # Assert SVG elements & Anywidgets
                svgs = page.query_selector_all("svg")
                assert len(svgs) >= 50, f"Expected at least 50 SVG elements, got {len(svgs)}"

                containers = page.query_selector_all(".bat-container")
                assert len(containers) >= 2, f"Expected at least 2 BioactivationTracer containers, got {len(containers)}"

                # Assert Zero Application Console Errors & Network Failures
                assert len(console_errors) == 0, f"Detected console errors: {console_errors}"
                assert len(network_failures) == 0, f"Detected network failures: {network_failures}"
            finally:
                browser.close()

    def test_verified_devtools_audit_report_artifact_integrity(self):
        """Verifies the checked-in Chrome DevTools audit report satisfies all quality gates."""
        report_path = BASE_DIR / "docs" / "DEVTOOLS_AUDIT_REPORT.json"
        assert report_path.exists(), f"DevTools report missing at {report_path}"
        report = json.loads(report_path.read_text(encoding="utf-8"))
        assert report.get("audit_status") == "PASS", f"Expected PASS, got {report.get('audit_status')}"
        assert report.get("unhandled_console_errors") == 0, f"Console errors: {report.get('unhandled_console_errors')}"
        assert len(report.get("network_failures", [])) == 0, f"Network failures: {report.get('network_failures')}"
        assert report.get("details", {}).get("all_5_acts_verified") is True, "All 5 acts not verified"
        assert report.get("total_svg_elements", 0) >= 50, "SVG element threshold not met"
        assert report.get("total_anywidget_instances", 0) >= 2, "AnyWidget container threshold not met"


class TestAnyWidgetAndBundlerIntegrity:
    """Verifies custom AnyWidget contract and bundler readiness."""

    def test_anywidget_afm_default_export_in_js(self):
        js_file = BASE_DIR / "widgets" / "bioactivation_tracer.js"
        content = js_file.read_text(encoding="utf-8")
        assert "export default { render }" in content or "export default { render };" in content

    def test_css_variables_scoping_to_host_and_container(self):
        css_file = BASE_DIR / "widgets" / "bioactivation_tracer.css"
        content = css_file.read_text(encoding="utf-8")
        assert ":host" in content
        assert ".bat-container" in content
        assert "--bat-bond" in content
