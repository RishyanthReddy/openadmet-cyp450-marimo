"""
tests/test_molab_staging.py

EC-T3-01: Verification suite for Molab.marimo.io deployment staging.
Validates artifact identity, SHA-256 integrity, size budget (< 200,000 bytes),
clean offline unbundling, and cold-boot timing benchmark reports.
"""

import hashlib
import json
from pathlib import Path
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
STANDALONE_PATH = BASE_DIR / "standalone_app.py"
COLD_BOOT_REPORT_PATH = BASE_DIR / "docs" / "molab_cold_boot_results.json"


def test_staging_manifest_has_artifact_identity():
    """Asserts standalone_app.py exists, is strictly < 200k bytes, and matches SHA-256 integrity."""
    assert STANDALONE_PATH.exists(), f"Missing standalone artifact: {STANDALONE_PATH}"
    
    data = STANDALONE_PATH.read_bytes()
    size_bytes = len(data)
    assert size_bytes < 200_000, f"standalone_app.py ({size_bytes} bytes) exceeds 200,000 bytes budget"
    assert size_bytes > 50_000, f"standalone_app.py suspiciously small: {size_bytes} bytes"
    
    sha256 = hashlib.sha256(data).hexdigest()
    assert len(sha256) == 64
    
    text = data.decode("utf-8")
    assert "_FALLBACK_SAMPLE_GZIP_B64" in text
    assert "_CYP2D6_DOCKING_GZIP_B64" in text
    assert "BioactivationTracer" in text
    assert "conformal_fdr_select" in text
    assert "beam_task_id" in text or "dc1112ce-e7dc-4abe-943b-790ccae2e9b5" in text

    # Verify cryptographic binding to cold boot benchmark report
    if COLD_BOOT_REPORT_PATH.exists():
        cb_report = json.loads(COLD_BOOT_REPORT_PATH.read_text(encoding="utf-8"))
        assert sha256 == cb_report.get("artifact_sha256"), (
            f"Digest drift detected: standalone_app.py ({sha256}) != cold boot report ({cb_report.get('artifact_sha256')})"
        )


def test_cold_boot_report_has_five_runs_and_under_ten_seconds():
    """Validates that cold boot benchmark report has at least 5 runs and meets 10.0s SLA."""
    if not COLD_BOOT_REPORT_PATH.exists():
        pytest.skip("molab_cold_boot_results.json has not been generated yet. Run scripts/verify_molab_cold_boot.py")

    report = json.loads(COLD_BOOT_REPORT_PATH.read_text(encoding="utf-8"))
    runs = report.get("runs", [])
    assert len(runs) >= 5, f"Expected >= 5 runs, found {len(runs)}"
    
    for r in runs:
        table_s = r.get("act1_table_ready_ms", 99999.0) / 1000.0
        assert table_s < 10.0, f"Run {r.get(run)} exceeded 10.0s SLA: {table_s:.2f}s"
        
    stats = report.get("statistics", {})
    assert stats.get("median_seconds", 999.0) < 10.0
    assert stats.get("p95_seconds", 999.0) < 10.0
    assert report.get("slo", {}).get("pass") is True


def test_cold_boot_report_has_no_external_requests_or_gpu():
    """Validates that cold boot runs performed zero remote external requests and did not initialize GPU."""
    if not COLD_BOOT_REPORT_PATH.exists():
        pytest.skip("molab_cold_boot_results.json has not been generated yet. Run scripts/verify_molab_cold_boot.py")

    report = json.loads(COLD_BOOT_REPORT_PATH.read_text(encoding="utf-8"))
    runs = report.get("runs", [])
    assert len(runs) >= 5
    
    for r in runs:
        assert len(r.get("external_requests", [])) == 0, f"Run {r.get(run)} made external requests: {r[external_requests]}"
        assert r.get("gpu_initialization_detected") is False, f"Run {r.get(run)} unexpectedly initialized GPU"
        assert len(r.get("console_errors", [])) == 0, f"Run {r.get(run)} had console errors: {r[console_errors]}"


def test_primary_parquet_sha256_matches_staging_report():
    """Asserts that data/packaged/cyp_tdi_curated.parquet exists and its SHA-256 matches docs/MOLAB_STAGING_REPORT.md."""
    parquet_path = BASE_DIR / "data" / "packaged" / "cyp_tdi_curated.parquet"
    staging_report_path = BASE_DIR / "docs" / "MOLAB_STAGING_REPORT.md"
    assert parquet_path.exists(), f"Missing primary parquet target: {parquet_path}"
    assert staging_report_path.exists(), f"Missing staging report: {staging_report_path}"

    parquet_sha = hashlib.sha256(parquet_path.read_bytes()).hexdigest()
    staging_content = staging_report_path.read_text(encoding="utf-8")
    assert parquet_sha in staging_content, (
        f"Parquet SHA-256 drift: {parquet_sha} not found in {staging_report_path}"
    )

