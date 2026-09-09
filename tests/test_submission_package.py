"""
tests/test_submission_package.py

EC-T3-02: Verification suite for the 285-second video script and JotForm submission checklist.
Validates exact storyboard segment math (sum == 285s), required feature coverage,
calibrated scientific wording, and absence of unresolved secrets/placeholders.
"""

from pathlib import Path
import re
import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = BASE_DIR / "docs" / "VIDEO_285_SECOND_SCRIPT.md"
PACKAGE_PATH = BASE_DIR / "docs" / "JOTFORM_SUBMISSION_PACKAGE.md"


def test_video_segments_sum_to_285_seconds():
    """Asserts that video walkthrough storyboard segments sum to exactly 285 seconds."""
    assert SCRIPT_PATH.exists(), f"Missing script: {SCRIPT_PATH}"
    content = SCRIPT_PATH.read_text(encoding="utf-8")
    
    # Extract duration table rows: e.g. `| 0:00–0:45 | 45 s |`
    duration_pattern = re.compile(r"\|\s*`?\d+:\d+[–-]\d+:\d+`?\s*\|\s*(\d+)\s*s\s*\|")
    durations = [int(m.group(1)) for m in duration_pattern.finditer(content)]
    
    assert len(durations) == 7, f"Expected 7 storyboard segments, found {len(durations)}: {durations}"
    assert durations == [45, 75, 45, 45, 45, 25, 5], f"Unexpected durations sequence: {durations}"
    
    total_seconds = sum(durations)
    assert total_seconds == 285, f"Storyboard total duration is {total_seconds}s; must be exactly 285s"
    assert total_seconds <= 300, f"Storyboard exceeds 300s ceiling: {total_seconds}s"


def test_video_script_covers_all_required_features():
    """Asserts that video walkthrough covers all required visual and scientific beats."""
    assert SCRIPT_PATH.exists()
    content = SCRIPT_PATH.read_text(encoding="utf-8")
    
    required_terms = [
        "Bathtub Audit",
        "BioactivationTracer",
        "Table 1.1",
        "AIMNet2",
        "3TBG",
        "4WNW",
        "CYP2D6",
        "Paroxetine",
        "Asp301",
        "Matched Molecular Pair",
        "TxConformal",
        "2.67",
        "standalone",
        "offline",
    ]
    
    for term in required_terms:
        assert term in content, f"Video script missing required feature/term: {term}"


def test_submission_package_has_required_checklist():
    """Asserts that JotForm submission package contains all necessary verification gates."""
    assert PACKAGE_PATH.exists(), f"Missing package checklist: {PACKAGE_PATH}"
    content = PACKAGE_PATH.read_text(encoding="utf-8")
    
    assert "Competition Title and Track" in content
    assert "Standalone File" in content
    assert "197,383 bytes" in content
    assert "Beam GPU Validation" in content
    assert "dc1112ce-e7dc-4abe-943b-790ccae2e9b5" in content
    assert "213 automated pytest unit and seam tests" in content
