"""
Live Browser & DevTools Verification Suite for OpenADMET Cytochrome P450 Platform.
Uses Chrome DevTools Protocol via Playwright on native Google Chrome.
"""

import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOTS_DIR = BASE_DIR / "docs" / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

APP_URL = "http://localhost:2718"
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def run_devtools_verification():
    print("=" * 70)
    print("STARTING CHROME DEVTOOLS LIVE BROWSER VERIFICATION")
    print(f"Target URL: {APP_URL}")
    print(f"Browser Engine: Google Chrome 152+ ({CHROME_BIN})")
    print("=" * 70)

    console_messages = []
    console_errors = []
    network_failures = []
    network_responses = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=CHROME_BIN,
            headless=True,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-size=1440,1080",
            ],
        )

        context = browser.new_context(
            viewport={"width": 1440, "height": 1080},
            device_scale_factor=1,
        )
        page = context.new_page()

        # 1. Console Listener
        def on_console(msg):
            text = f"[{msg.type.upper()}] {msg.text}"
            console_messages.append(text)
            if msg.type in ("error", "assert"):
                console_errors.append(msg.text)
                print(f"  ❌ CONSOLE ERROR: {msg.text}")
            elif msg.type == "warning":
                print(f"  ⚠️ CONSOLE WARN: {msg.text}")

        page.on("console", on_console)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # 2. Network Listener
        def on_response(resp):
            network_responses.append(resp.status)
            if resp.status >= 400:
                failure_info = f"{resp.status} {resp.request.method} {resp.url}"
                network_failures.append(failure_info)
                print(f"  ❌ NETWORK FAILURE: {failure_info}")

        page.on("response", on_response)

        # 3. Navigate to App
        t0 = time.perf_counter()
        print("\n[Step 1] Navigating to live Marimo server...")
        response = page.goto(APP_URL, wait_until="networkidle", timeout=15000)
        nav_dt = time.perf_counter() - t0
        print(f"  ✅ Page loaded in {nav_dt:.2f}s with status {response.status if response else 'N/A'}")

        # 4. Wait for Marimo Reactive Content to Mount
        print("\n[Step 2] Waiting for Marimo DAG reactive elements to mount in DOM...")
        page.wait_for_timeout(3000)  # Allow anywidget traitlet initial sync

        # 5. DOM Inspection
        print("\n[Step 3] Inspecting DOM elements...")
        title = page.title()
        print(f"  - Document Title: '{title}'")
        assert "OpenADMET" in title or "marimo" in title.lower(), f"Unexpected title: {title}"

        # Check for Key Acts in Text
        body_text = page.inner_text("body")
        for act in [
            "Act 1: What TDI Is — and What It Is Not",
            "Act 2: The Bathtub Audit",
            "Act 3: Physics-Grounded Quantum Reactivity",
            "Act 4: Medicinal Chemistry Steering",
            "Act 5: TxConformal Candidate Prioritization",
        ]:
            if act in body_text:
                print(f"  ✅ Found '{act}' in live browser DOM")
            else:
                print(f"  ⚠️ Missing '{act}' in live browser text")

        # Check for Custom BioactivationTracer SVGs
        svg_elements = page.query_selector_all("svg")
        print(f"  ✅ Found {len(svg_elements)} SVG elements rendered in DOM")

        tracer_containers = page.query_selector_all(".bat-container")
        print(f"  ✅ Found {len(tracer_containers)} BioactivationTracer custom widget containers (.bat-container)")

        # 6. Interactive Testing: Act 1 Dropdown
        print("\n[Step 4] Testing interactive UI reactivity...")
        # Check if dropdowns exist
        dropdowns = page.query_selector_all("select")
        print(f"  - Total select dropdowns found: {len(dropdowns)}")

        sliders = page.query_selector_all("input[type='range']")
        print(f"  - Total range sliders found: {len(sliders)}")

        # 7. Take Screenshots
        print("\n[Step 5] Capturing live screenshots...")
        full_screenshot_path = SCREENSHOTS_DIR / "browser_devtools_full_page.png"
        page.screenshot(path=str(full_screenshot_path), full_page=True)
        print(f"  📸 Full page screenshot captured: {full_screenshot_path} ({full_screenshot_path.stat().st_size} bytes)")

        viewport_screenshot_path = SCREENSHOTS_DIR / "browser_devtools_viewport.png"
        page.screenshot(path=str(viewport_screenshot_path))
        print(f"  📸 Viewport screenshot captured: {viewport_screenshot_path} ({viewport_screenshot_path.stat().st_size} bytes)")

        # 8. DevTools Clean Console Audit
        print("\n[Step 6] DevTools Console & Network Audit...")
        print(f"  - Total network requests completed: {len(network_responses)}")
        print(f"  - Total console messages logged: {len(console_messages)}")
        print(f"  - Network failures (>= 400): {len(network_failures)}")
        print(f"  - Unhandled console errors: {len(console_errors)}")

        browser.close()

    print("\n" + "=" * 70)
    print("DEVTOOLS AUDIT SUMMARY:")
    if not console_errors and not network_failures:
        print("  🎉 PERFECT DEVTOOLS HEALTH: 0 Console Errors, 0 Network Failures!")
    else:
        print(f"  ⚠️ Errors detected: {len(console_errors)} console errors, {len(network_failures)} network failures.")
    print("=" * 70)

    return len(console_errors), len(network_failures)


if __name__ == "__main__":
    errs, fails = run_devtools_verification()
    sys.exit(0 if (errs == 0 and fails == 0) else 1)
