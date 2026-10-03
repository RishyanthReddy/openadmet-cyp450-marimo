"""Keep submission materials consistent without claiming they have been published."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

def test_video_timeline_is_continuous_and_under_five_minutes():
    text = (ROOT/'docs/VIDEO_285_SECOND_SCRIPT.md').read_text()
    intervals = re.findall(r"\| (\d+):(\d+)–(\d+):(\d+) \|", text)
    spans = [(int(a)*60+int(b), int(c)*60+int(d)) for a,b,c,d in intervals]
    assert spans[0][0] == 0
    assert all(start < stop for start, stop in spans)
    assert all(spans[i][1] == spans[i+1][0] for i in range(len(spans)-1))
    assert 0 < spans[-1][1] < 300


def test_video_explains_main_controls_and_evidence_limits():
    text = (ROOT/'docs/VIDEO_285_SECOND_SCRIPT.md').read_text().lower()
    for phrase in ('fragment', 'model', 'scaffold', '0.4652', '0.4753', 'unknown', 'alpha', 'error guarantee', 'download', 'ai assistance'):
        assert phrase.lower() in text.lower()


def test_submission_package_preserves_unfinished_release_gates():
    text = (ROOT/'docs/JOTFORM_SUBMISSION_PACKAGE.md').read_text()
    for phrase in ('Published to molab', 'hosted rendering', 'video upload', 'contact email', 'AI disclosure', 'receipt', 'approval'):
        assert phrase.lower() in text.lower()
    assert 'no repository LICENSE file exists' in text
    assert 'Fully Verified' not in text
