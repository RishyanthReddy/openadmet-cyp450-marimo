#!/usr/bin/env python3
"""
scripts/verify_molab_cold_boot.py

EC-T3-01: Molab.marimo.io Cold-Boot & Staging Validation Harness.

Measures cold boot latency, DOM mount latency, interactive readiness,
network isolation, and GPU non-initialization across repeated fresh sessions.
Generates machine-readable results conforming to EC-T3-01 schema specifications.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
VENV_BIN = BASE_DIR / ".venv" / "bin"
MARIMO_BIN = VENV_BIN / "marimo" if (VENV_BIN / "marimo").exists() else Path(shutil.which("marimo") or "marimo")


def find_chrome_binary() -> str:
    env_bin = os.environ.get("CHROME_PATH") or os.environ.get("CHROME_BIN")
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


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def measure_single_cold_boot(
    artifact_path: Path,
    port: int,
    timeout_seconds: float = 10.0,
    chrome_bin: str | None = None,
) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    process_start_utc = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()

    cmd = [
        str(MARIMO_BIN),
        "run",
        str(artifact_path),
        "--port",
        str(port),
        "--headless",
    ]
    proc = subprocess.Popen(
        cmd,
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    external_requests = []
    console_errors = []
    console_warnings = []
    first_page_ms = None
    marimo_ready_ms = None
    act1_table_ready_ms = None
    gpu_initialization_detected = False

    try:
        # 1. Poll for HTTP 200 reachability
        deadline = t0 + timeout_seconds
        app_url = f"http://127.0.0.1:{port}"
        import urllib.request

        while time.perf_counter() < deadline:
            try:
                with urllib.request.urlopen(app_url, timeout=0.5) as resp:
                    if resp.status == 200:
                        first_page_ms = round((time.perf_counter() - t0) * 1000, 2)
                        break
            except Exception:
                time.sleep(0.05)

        if first_page_ms is None:
            raise TimeoutError(f"HTTP server did not respond within {timeout_seconds}s")

        # 2. Launch headless browser session
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=chrome_bin or find_chrome_binary(),
                headless=True,
                args=[
                    "--disable-gpu",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            def handle_request(req):
                u = req.url
                if not (
                    u.startswith("http://127.0.0.1")
                    or u.startswith("http://localhost")
                    or u.startswith("data:")
                    or u.startswith("blob:")
                ):
                    external_requests.append(u)

            def handle_console(msg):
                txt = msg.text
                if msg.type == "error":
                    # Ignore harmless browser font/favicon issues if any
                    if "favicon" not in txt.lower():
                        console_errors.append(txt)
                elif msg.type == "warning":
                    if "deprecated" not in txt.lower():
                        console_warnings.append(txt)

            page.on("request", handle_request)
            page.on("console", handle_console)

            # 3. Navigate to app URL
            page.goto(app_url, wait_until="domcontentloaded", timeout=int(timeout_seconds * 1000))

            # 4. Wait for Marimo app root mount
            page.wait_for_selector(
                "div[data-marimo-app], div.marimo, #app, marimo-app",
                timeout=int(timeout_seconds * 1000),
            )
            marimo_ready_ms = round((time.perf_counter() - t0) * 1000, 2)

            # 5. Wait for interactive elements / Table 1.1 or bioactivation tracer
            page.wait_for_selector(
                "table, .bat-container, [role='table'], .marimo-table",
                timeout=int(timeout_seconds * 1000),
            )
            act1_table_ready_ms = round((time.perf_counter() - t0) * 1000, 2)

            context.close()
            browser.close()

    finally:
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=2.0)
            combined = (stdout or b"").decode("utf-8", errors="ignore") + (stderr or b"").decode("utf-8", errors="ignore")
            if "cuda" in combined.lower() or "beam" in combined.lower() or "gpu" in combined.lower():
                # Verify if it was real GPU init vs just path string
                if "cuda initialized" in combined.lower() or "device: cuda" in combined.lower():
                    gpu_initialization_detected = True
        except Exception:
            proc.kill()

    return {
        "process_start_utc": process_start_utc,
        "first_page_ms": first_page_ms or 0.0,
        "marimo_ready_ms": marimo_ready_ms or 0.0,
        "act1_table_ready_ms": act1_table_ready_ms or 0.0,
        "external_requests": external_requests,
        "gpu_initialization_detected": gpu_initialization_detected,
        "console_errors": console_errors,
        "console_warnings": console_warnings,
    }


def run_cold_boot_verification(
    artifact_path: Path = BASE_DIR / "standalone_app.py",
    runs_count: int = 5,
    timeout_seconds: float = 10.0,
    gist_revision: str = "candidate-standalone-rc1",
    output_path: Path = BASE_DIR / "docs" / "molab_cold_boot_results.json",
) -> dict[str, Any]:
    if not artifact_path.exists():
        raise FileNotFoundError(f"Artifact not found: {artifact_path}")

    artifact_bytes = artifact_path.read_bytes()
    artifact_sha256 = hashlib.sha256(artifact_bytes).hexdigest()
    chrome_bin = find_chrome_binary()

    print(f"=== EC-T3-01: Molab Cold-Boot Verification ({runs_count} runs) ===")
    print(f"Artifact: {artifact_path} ({len(artifact_bytes):,} bytes)")
    print(f"SHA-256:  {artifact_sha256}")
    print(f"Browser:  {chrome_bin}")
    print(f"Timeout:  {timeout_seconds}s per run\n")

    runs = []
    for i in range(1, runs_count + 1):
        port = get_free_port()
        print(f"Run {i}/{runs_count} (port {port})...", end=" ", flush=True)
        t_start = time.perf_counter()
        result = measure_single_cold_boot(
            artifact_path=artifact_path,
            port=port,
            timeout_seconds=timeout_seconds,
            chrome_bin=chrome_bin,
        )
        result["run"] = i
        runs.append(result)
        elapsed = time.perf_counter() - t_start
        print(
            f"Table Ready: {result['act1_table_ready_ms']:.1f} ms | "
            f"Ext Requests: {len(result['external_requests'])} | "
            f"Console Errors: {len(result['console_errors'])} | "
            f"Total: {elapsed:.2f}s"
        )
        time.sleep(0.5)

    table_times = [r["act1_table_ready_ms"] / 1000.0 for r in runs]
    all_under_sla = all(t < timeout_seconds for t in table_times)
    zero_ext = all(len(r["external_requests"]) == 0 for r in runs)
    zero_err = all(len(r["console_errors"]) == 0 for r in runs)
    zero_gpu = all(not r["gpu_initialization_detected"] for r in runs)
    sla_pass = all_under_sla and zero_ext and zero_err and zero_gpu

    import numpy as np
    summary_report = {
        "artifact_sha256": artifact_sha256,
        "gist_revision": gist_revision,
        "measured_runs_count": runs_count,
        "runs": runs,
        "statistics": {
            "min_seconds": round(float(np.min(table_times)), 3),
            "max_seconds": round(float(np.max(table_times)), 3),
            "median_seconds": round(float(np.median(table_times)), 3),
            "p95_seconds": round(float(np.percentile(table_times, 95)), 3),
        },
        "slo": {
            "threshold_seconds": timeout_seconds,
            "all_under_threshold": all_under_sla,
            "zero_external_requests": zero_ext,
            "zero_console_errors": zero_err,
            "zero_gpu_initialization": zero_gpu,
            "pass": sla_pass,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary_report, indent=2), encoding="utf-8")
    print(f"\nReport written to: {output_path}")
    print(f"Median Cold Boot:  {summary_report['statistics']['median_seconds']} s")
    print(f"P95 Cold Boot:     {summary_report['statistics']['p95_seconds']} s")
    print(f"SLO Status:        {'PASS' if sla_pass else 'FAIL'}")
    return summary_report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify Molab cold boot SLA and staging readiness.")
    parser.add_argument("--artifact", type=Path, default=BASE_DIR / "standalone_app.py", help="Path to standalone notebook")
    parser.add_argument("--runs", type=int, default=5, help="Number of fresh cold-boot runs")
    parser.add_argument("--timeout-seconds", type=float, default=10.0, help="SLA threshold timeout in seconds")
    parser.add_argument("--gist-revision", type=str, default="candidate-standalone-rc1", help="Gist revision identifier")
    parser.add_argument("--output", type=Path, default=BASE_DIR / "docs" / "molab_cold_boot_results.json", help="Path for output JSON")

    args = parser.parse_args()
    report = run_cold_boot_verification(
        artifact_path=args.artifact,
        runs_count=args.runs,
        timeout_seconds=args.timeout_seconds,
        gist_revision=args.gist_revision,
        output_path=args.output,
    )
    if not report["slo"]["pass"]:
        sys.exit(1)
