# Round 19 Audit & Sign-Off

**Calibrated score: 98 / 100**  
**Unconditional Tier 3 sign-off: NOT GRANTED**

| Gate | Score | Finding |
|---|---:|---|
| EC-T2-01 Docking Integrity & Biophysical Grounding | **40/40** | Docking/provenance tests pass. |
| EC-T2-02 Reactive UI Integration & Scientific Calibration | **28/30** | Valid path passes, but no-evaluation fallback still defaults to Paroxetine. |
| EC-T2-03 Offline Standalone Bundling & Architecture Seams | **30/30** | Artifact identity, size, bundled reports, tests, and Marimo validation pass. |

Verified:

- `standalone_app.py`: **196,557 bytes**, SHA-256 `8aec126bd451b06762e0a7d9bfb36045de7cbf4fb9ff3a97337f517eb5b51c15`.
- Cold-boot report: matching digest, 5 runs, median **4.559 s**, P95 **4.787 s**, zero network/GPU/errors.
- DevTools report: matching digest and size, **96 SVGs**, **5 AnyWidgets**, zero errors/failures.
- Targeted suite: **32 passed, 1 skipped**.
- Full suite: **210 passed, 9 skipped**.
- `marimo check standalone_app.py`: exit 0.

Blocking finding: the claimed fallback remediation is incomplete. Both [app.py:1059](/Users/rishyanthreddy/Desktop/Marimo/app.py:1059) and [standalone_app.py:1892](/Users/rishyanthreddy/Desktop/Marimo/standalone_app.py:1892) still inject `["Paroxetine"]`; [app.py:1089](/Users/rishyanthreddy/Desktop/Marimo/app.py:1089) and [standalone_app.py:1920](/Users/rishyanthreddy/Desktop/Marimo/standalone_app.py:1920) still default the selected compound to `"Paroxetine"`. With empty evaluations, the UI can therefore show the canonical Paroxetine badge/narrative alongside null metrics.

The independent cold-boot rerun was attempted but blocked by the managed sandbox’s localhost socket permission; the recorded evidence remains cryptographically bound to the artifact. Remove the static Paroxetine defaults and guard the canonical narrative on an actual evaluation before granting unconditional sign-off.