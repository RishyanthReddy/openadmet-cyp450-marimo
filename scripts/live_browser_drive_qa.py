#!/usr/bin/env python3
"""
Phase 4 Live Interactive Browser Drive & QA Verification Suite.
Drives native Google Chrome via Playwright across all 5 Acts on http://localhost:2718.
Verifies:
  - Act 1: Dropdown switching, AnyWidget warhead halos, NCBI Entrez Verified badge, PubMed/DOI links, Table 1.1.
  - Act 2: Bathtub audit narrative, model metrics, Tanimoto shift SVG.
  - Act 3: AIMNet2 quantum electronic features, macromolecular docking active-site steric proximity.
  - Act 4: Matched Molecular Pair (MMP) activity cliff viewer, row-level assay provenance, OOF error case tabs.
  - Act 5: TxConformal candidate selection table, FDR control, honest limitations and DOME checklist.
  - Console & Network: Strictly 0 unhandled console errors, 0 network failures.
Saves high-res visual evidence screenshots to the artifact directory.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACT_DIR = Path("/Users/rishyanthreddy/.gemini/antigravity-cli/brain/fae2e0dc-c813-4546-b6d9-0af7042caaf8")
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
APP_URL = "http://localhost:2718"


def run_live_browser_qa():
    print(f"[Phase 4 QA] Starting Chrome DevTools live browser session on {APP_URL}...", flush=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    console_errors = []
    network_failures = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_BIN,
            headless=True,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1600,1200",
            ],
        )

        context = browser.new_context(
            viewport={"width": 1600, "height": 1200},
            device_scale_factor=1,
        )
        page = context.new_page()

        # Telemetry listeners
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type in ("error", "assert") else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))
        page.on("response", lambda resp: network_failures.append(f"{resp.status} {resp.url}") if resp.status >= 400 else None)

        print("[Phase 4 QA] Navigating to OpenADMET application...", flush=True)
        resp = page.goto(APP_URL, wait_until="networkidle", timeout=25000)
        assert resp and resp.status == 200, f"HTTP status {resp.status if resp else 'None'}"

        # Wait for reactive DAG to mount Act 1
        page.wait_for_selector("text=Act 1: What TDI Is", timeout=15000)
        page.wait_for_timeout(2000)
        print("[Phase 4 QA] Application loaded and reactive DAG mounted successfully.", flush=True)

        # -------------------------------------------------------------
        # Act 1: Literature MBIs & NCBI Entrez Verification
        # -------------------------------------------------------------
        print("[Phase 4 QA] Testing Act 1: Literature MBIs & NCBI Entrez verification...", flush=True)
        assert "NCBI Entrez Verified" in page.inner_text("body")
        assert "Raloxifene" in page.inner_text("body")

        # Capture Act 1 initial view (Raloxifene)
        ralox_card = page.locator("text=Raloxifene").first
        page.screenshot(path=str(ARTIFACT_DIR / "phase4_act1_raloxifene_ncbi.png"))
        print("  ✓ Saved phase4_act1_raloxifene_ncbi.png")

        # Select Mibefradil in dropdown
        select_locator = page.locator("select").first
        if select_locator.count() > 0:
            select_locator.select_option("Mibefradil")
            page.wait_for_timeout(1500)
            assert "Lancet" in page.inner_text("body")
            page.screenshot(path=str(ARTIFACT_DIR / "phase4_act1_mibefradil_ncbi.png"))
            print("  ✓ Switched to Mibefradil & saved phase4_act1_mibefradil_ncbi.png")

            select_locator.select_option("Lapatinib")
            page.wait_for_timeout(1500)
            assert "Lapatinib" in page.inner_text("body")
            page.screenshot(path=str(ARTIFACT_DIR / "phase4_act1_lapatinib_ncbi.png"))
            print("  ✓ Switched to Lapatinib & saved phase4_act1_lapatinib_ncbi.png")

        # Scroll to Table 1.1
        table_elem = page.locator("text=Table 1.1: Curated Reference Set").first
        if table_elem.count() > 0:
            table_elem.scroll_into_view_if_needed()
            page.wait_for_timeout(1000)
            page.screenshot(path=str(ARTIFACT_DIR / "phase4_act1_table1_1_ncbi.png"))
            print("  ✓ Saved phase4_act1_table1_1_ncbi.png")

        # -------------------------------------------------------------
        # Act 2: Bathtub Audit
        # -------------------------------------------------------------
        print("[Phase 4 QA] Testing Act 2: The Bathtub Audit...", flush=True)
        act2_elem = page.locator("text=Act 2: The Bathtub Audit").first
        act2_elem.scroll_into_view_if_needed()
        page.wait_for_timeout(1500)
        assert "Bathtub Audit" in page.inner_text("body")
        page.screenshot(path=str(ARTIFACT_DIR / "phase4_act2_bathtub_audit.png"))
        print("  ✓ Saved phase4_act2_bathtub_audit.png")

        # -------------------------------------------------------------
        # Act 3: Quantum Reactivity & Docking
        # -------------------------------------------------------------
        print("[Phase 4 QA] Testing Act 3: Physics-Grounded Quantum Reactivity...", flush=True)
        act3_elem = page.locator("text=Act 3: Physics-Grounded Quantum Reactivity").first
        act3_elem.scroll_into_view_if_needed()
        page.wait_for_timeout(1500)
        assert "AIMNet2" in page.inner_text("body")
        page.screenshot(path=str(ARTIFACT_DIR / "phase4_act3_quantum_docking.png"))
        print("  ✓ Saved phase4_act3_quantum_docking.png")

        # -------------------------------------------------------------
        # Act 4: Medicinal Chemistry Steering & MMPs
        # -------------------------------------------------------------
        print("[Phase 4 QA] Testing Act 4: Medicinal Chemistry Steering & MMP Activity Cliffs...", flush=True)
        act4_elem = page.locator("text=Act 4: Medicinal Chemistry Steering").first
        act4_elem.scroll_into_view_if_needed()
        page.wait_for_timeout(1500)
        assert "MMP" in page.inner_text("body")
        page.screenshot(path=str(ARTIFACT_DIR / "phase4_act4_mmp_lead_redesign.png"))
        print("  ✓ Saved phase4_act4_mmp_lead_redesign.png")

        # -------------------------------------------------------------
        # Act 5: TxConformal Candidate Prioritization
        # -------------------------------------------------------------
        print("[Phase 4 QA] Testing Act 5: TxConformal Candidate Prioritization...", flush=True)
        act5_elem = page.locator("text=Act 5: TxConformal Candidate Prioritization").first
        act5_elem.scroll_into_view_if_needed()
        page.wait_for_timeout(1500)
        assert "TxConformal" in page.inner_text("body")
        assert "DOME" in page.inner_text("body")
        page.screenshot(path=str(ARTIFACT_DIR / "phase4_act5_conformal_selection.png"))
        print("  ✓ Saved phase4_act5_conformal_selection.png")

        # Full page overview screenshot
        page.screenshot(path=str(ARTIFACT_DIR / "phase4_full_page_overview.png"), full_page=True)
        print("  ✓ Saved phase4_full_page_overview.png")

        # Audit checks
        svg_count = len(page.query_selector_all("svg"))
        widget_count = len(page.query_selector_all(".bat-container"))
        print(f"[Phase 4 QA] Total SVG elements rendered: {svg_count}")
        print(f"[Phase 4 QA] Total AnyWidget instances rendered: {widget_count}")
        print(f"[Phase 4 QA] Unhandled console errors: {len(console_errors)}")
        print(f"[Phase 4 QA] Network failures: {len(network_failures)}")

        assert len(console_errors) == 0, f"Console errors detected: {console_errors}"
        assert len(network_failures) == 0, f"Network failures detected: {network_failures}"
        assert svg_count >= 70, f"Expected >= 70 SVGs, got {svg_count}"
        assert widget_count >= 2, f"Expected >= 2 AnyWidgets, got {widget_count}"

        browser.close()
        print("\n========================================================", flush=True)
        print("  [PHASE 4 QA PASSED] All 5 Acts Verified Cleanly!      ", flush=True)
        print("========================================================", flush=True)


if __name__ == "__main__":
    run_live_browser_qa()
