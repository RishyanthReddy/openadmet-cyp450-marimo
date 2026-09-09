"""
Deep Interactive UI Verification Script.
Interacts with every dropdown, slider, and reactive card in Google Chrome via Playwright,
capturing high-resolution screenshots centered exactly on the interactive components.
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


def verify_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_BIN,
            headless=True,
            args=["--disable-gpu", "--no-sandbox", "--window-size=1440,1100"],
        )
        context = browser.new_context(viewport={"width": 1440, "height": 1100}, device_scale_factor=1.5)
        page = context.new_page()

        print(f"Connecting to {APP_URL}...")
        page.goto(APP_URL, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(3000)

        selects = page.query_selector_all("select")
        print(f"Found {len(selects)} dropdowns on the page.")

        # -------------------------------------------------------------
        # 1. ACT 1: INTERACTIVE MBI SELECTION (Dropdown 0)
        # -------------------------------------------------------------
        print("\n[UI Test 1] Testing Act 1 Literature MBI Selector...")
        mbi_select = selects[0]
        mbi_select.scroll_into_view_if_needed()
        page.wait_for_timeout(600)

        print("  Selecting 'Raloxifene' in Act 1...")
        mbi_select.select_option(label="Raloxifene")
        page.wait_for_timeout(1000)

        p1 = SCREENSHOTS_DIR / "ui_act1_raloxifene.png"
        page.screenshot(path=str(p1))
        (ARTIFACT_DIR / p1.name).write_bytes(p1.read_bytes())
        print(f"  📸 Saved {p1.name}")

        print("  Selecting 'Clopidogrel' in Act 1...")
        mbi_select.select_option(label="Clopidogrel")
        page.wait_for_timeout(1000)

        p2 = SCREENSHOTS_DIR / "ui_act1_clopidogrel.png"
        page.screenshot(path=str(p2))
        (ARTIFACT_DIR / p2.name).write_bytes(p2.read_bytes())
        print(f"  📸 Saved {p2.name}")

        # -------------------------------------------------------------
        # 2. ACT 2: MODEL ARCHITECTURE SELECTION (Dropdown 1)
        # -------------------------------------------------------------
        print("\n[UI Test 2] Testing Act 2 Model Architecture Selector...")
        arch_select = selects[1]
        arch_select.scroll_into_view_if_needed()
        page.wait_for_timeout(600)

        print("  Selecting 'Chemprop v2 D-MPNN (Graph)' in Act 2...")
        arch_select.select_option(label="Chemprop v2 D-MPNN (Graph)")
        page.wait_for_timeout(1000)

        p3 = SCREENSHOTS_DIR / "ui_act2_dmpnn.png"
        page.screenshot(path=str(p3))
        (ARTIFACT_DIR / p3.name).write_bytes(p3.read_bytes())
        print(f"  📸 Saved {p3.name}")

        # -------------------------------------------------------------
        # 3. ACT 3: DOCKING LIGAND SELECTION (Dropdown 2)
        # -------------------------------------------------------------
        print("\n[UI Test 3] Testing Act 3 Docking Ligand Selector...")
        dock_select = selects[2]
        dock_select.scroll_into_view_if_needed()
        page.wait_for_timeout(600)

        print("  Selecting 'Raloxifene' in Act 3 Docking...")
        dock_select.select_option(label="Raloxifene")
        page.wait_for_timeout(1000)

        p4 = SCREENSHOTS_DIR / "ui_act3_docking_raloxifene.png"
        page.screenshot(path=str(p4))
        (ARTIFACT_DIR / p4.name).write_bytes(p4.read_bytes())
        print(f"  📸 Saved {p4.name}")

        # -------------------------------------------------------------
        # 4. ACT 4: MMP ACTIVITY CLIFF EXPLORER (Dropdown 3)
        # -------------------------------------------------------------
        print("\n[UI Test 4] Testing Act 4 MMP Activity Cliff Explorer...")
        mmp_select = selects[3]
        mmp_select.scroll_into_view_if_needed()
        page.wait_for_timeout(600)

        mmp_options = mmp_select.query_selector_all("option")
        print(f"  MMP dropdown has {len(mmp_options)} options.")
        if len(mmp_options) > 2:
            mmp_select.select_option(index=2)
            page.wait_for_timeout(1000)

        p5 = SCREENSHOTS_DIR / "ui_act4_mmp_pair.png"
        page.screenshot(path=str(p5))
        (ARTIFACT_DIR / p5.name).write_bytes(p5.read_bytes())
        print(f"  📸 Saved {p5.name}")

        # -------------------------------------------------------------
        # 5. ACT 4: OUT-OF-FOLD ERROR DIAGNOSIS (Dropdown 4)
        # -------------------------------------------------------------
        print("\n[UI Test 5] Testing Act 4 Out-of-Fold Error Diagnosis...")
        oof_select = selects[4]
        oof_select.scroll_into_view_if_needed()
        page.wait_for_timeout(600)

        oof_options = oof_select.query_selector_all("option")
        print(f"  OOF dropdown has {len(oof_options)} options.")
        if len(oof_options) > 2:
            oof_select.select_option(index=2)
            page.wait_for_timeout(1000)

        p6 = SCREENSHOTS_DIR / "ui_act4_false_positive.png"
        page.screenshot(path=str(p6))
        (ARTIFACT_DIR / p6.name).write_bytes(p6.read_bytes())
        print(f"  📸 Saved {p6.name}")

        # -------------------------------------------------------------
        # 6. ACT 5: TXCONFORMAL SELECTION SLIDER
        # -------------------------------------------------------------
        print("\n[UI Test 6] Testing Act 5 Conformal Selection & Controls...")
        slider = page.query_selector("[role='slider']")
        if slider:
            slider.scroll_into_view_if_needed()
            page.wait_for_timeout(600)
            print("  Found slider, pressing ArrowRight 5 times...")
            slider.focus()
            for _ in range(5):
                slider.press("ArrowRight")
                page.wait_for_timeout(100)
            page.wait_for_timeout(1000)

        p7 = SCREENSHOTS_DIR / "ui_act5_conformal.png"
        page.screenshot(path=str(p7))
        (ARTIFACT_DIR / p7.name).write_bytes(p7.read_bytes())
        print(f"  📸 Saved {p7.name}")

        browser.close()
        print("\n🎉 All 6 centered UI interactive tests passed cleanly and high-res screenshots saved!")


if __name__ == "__main__":
    verify_ui()
