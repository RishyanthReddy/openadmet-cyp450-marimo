"""
Script to capture dedicated section screenshots of each Act in the OpenADMET platform.
"""

import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = BASE_DIR / "docs" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

ARTIFACT_DIR = Path("/Users/rishyanthreddy/.gemini/antigravity-cli/brain/fae2e0dc-c813-4546-b6d9-0af7042caaf8")

APP_URL = "http://localhost:2718"
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

SECTIONS = [
    ("header_and_act1", "Act 1: What TDI Is"),
    ("act2_bathtub_audit", "Act 2: The Bathtub Audit"),
    ("act3_quantum_and_docking", "Act 3: Physics-Grounded Quantum Reactivity"),
    ("act4_mmp_lead_redesign", "Act 4: Medicinal Chemistry Steering"),
    ("act5_txconformal_selection", "Act 5: TxConformal Candidate Prioritization"),
]


def capture_sections():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_BIN,
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--window-size=1440,1080"],
        )
        context = browser.new_context(viewport={"width": 1440, "height": 1080}, device_scale_factor=1)
        page = context.new_page()

        print(f"Navigating to {APP_URL}...")
        page.goto(APP_URL, wait_until="networkidle", timeout=15000)
        page.wait_for_timeout(3000)

        for name, heading_text in SECTIONS:
            print(f"Locating section: {heading_text}...")
            elem = page.locator(f"text={heading_text}").first
            if elem.count() > 0:
                elem.scroll_into_view_if_needed()
                page.wait_for_timeout(800)  # allow layout settle
                out_path = SCREENSHOTS_DIR / f"{name}.png"
                page.screenshot(path=str(out_path))
                print(f"  📸 Captured {out_path.name} ({out_path.stat().st_size} bytes)")
                
                # Copy to artifact dir
                art_path = ARTIFACT_DIR / f"{name}.png"
                art_path.write_bytes(out_path.read_bytes())
            else:
                print(f"  ⚠️ Could not find element for '{heading_text}'")

        browser.close()


if __name__ == "__main__":
    capture_sections()
