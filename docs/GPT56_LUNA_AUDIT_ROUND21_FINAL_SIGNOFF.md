# Round 21 Audit & Sign-Off

The required numeric-sentinel remediation passes. However, strict unconditional Tier 3 sign-off is **not granted**.

| Gate | Score | Assessment |
|---|---:|---|
| EC-T2-01 Docking Integrity & Biophysical Grounding | **40/40** | Docking, provider-payload, PDBQT reproducibility, and Asp301 tests pass. |
| EC-T2-02 Reactive UI Integration & Scientific Calibration | **30/30** | Both artifacts render `No Evaluation Available`; actual cell execution produced no `0.00 kcal/mol`/`99.90 Å` sentinels and preserved real evaluated metrics. |
| EC-T3-01/02 Molab Bundling, SLA & Staging | **29/30** | Artifact identity, size, focused package tests, and report-contract checks pass; one staging metadata contradiction remains. |

**Strict total: 99/100**  
**Unconditional Tier 3 Sign-Off: NOT GRANTED**

Verified:

- [`app.py:1136`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1136) and [`standalone_app.py:1967`](/Users/rishyanthreddy/Desktop/Marimo/standalone_app.py:1967) explicitly render `No Evaluation Available`.
- Card templates interpolate those values directly at [`app.py:1153`](/Users/rishyanthreddy/Desktop/Marimo/app.py:1153) and [`standalone_app.py:1984`](/Users/rishyanthreddy/Desktop/Marimo/standalone_app.py:1984).
- Focused tests: **12 passed**.
- Full suite: **212 passed, 9 skipped**.
- Both `marimo check` commands and strict compilation passed.
- `standalone_app.py`: **197,383 bytes**, SHA-256 `952160741c621f504f68380b2b3f84d13c3e496f3168a5d264e7f04fb7caafae`; standalone, cold-boot, DevTools, staging, and submission size references agree.

Blocking finding:

- [`docs/MOLAB_STAGING_REPORT.md:20`](/Users/rishyanthreddy/Desktop/Marimo/docs/MOLAB_STAGING_REPORT.md:20) documents Parquet SHA `cf5238…`, but the actual Parquet file and embedded constant are `2f5610…`. The report therefore incorrectly marks that checksum as verified. Update/regenerate this metadata before unconditional release sign-off.

Additional notes:

- [`tests/test_cyp2d6_ui.py:109`](/Users/rishyanthreddy/Desktop/Marimo/tests/test_cyp2d6_ui.py:109) manually emulates the fallback rather than invoking the registered Marimo cell; my independent cell execution passed, but the regression test should be strengthened.
- Submission documents still state **210** tests at [`JOTFORM_SUBMISSION_PACKAGE.md:37`](/Users/rishyanthreddy/Desktop/Marimo/docs/JOTFORM_SUBMISSION_PACKAGE.md:37) and [`VIDEO_285_SECOND_SCRIPT.md:19`](/Users/rishyanthreddy/Desktop/Marimo/docs/VIDEO_285_SECOND_SCRIPT.md:19), while the current suite has 212.
- Fresh cold-boot and browser reruns were sandbox-blocked by localhost bind/Chrome restrictions; the checked-in report contract passes. Antigravity review was likewise unavailable due sandbox restrictions.