# Round 18 Audit & Sign-Off Report

**Calibrated score: 98 / 100**  
**Unconditional Tier 3 sign-off: NOT GRANTED**

| Gate | Score | Assessment |
|---|---:|---|
| EC-T2-01 Docking Integrity & Biophysical Grounding | **40/40** | Provider payload binding and docking provenance pass locally. |
| EC-T2-02 Reactive UI Integration & Scientific Calibration | **30/30** | Reactive wiring, scientific framing, and offline embedded-data checks pass. |
| EC-T2-03 Offline Standalone Bundling & Architecture Seams | **28/30** | Bundle size and static seams pass, but artifact identity and live-browser verification are unresolved. |

## Verified

- Raw Beam payload: 551,055 bytes; SHA-256 `7abd0177…94109`, matching both the execution record and packaged artifact.
- All 20 docking runs matched across Vina score, Fe distance, nearest atom, and pose SHA-256: **80 field comparisons passed**.
- All 20 provider pose texts hash correctly and are byte-identical to local pose files.
- Receptor source/prepared-PDBQT hashes: **4/4 passed**.
- Packaging script now requires the execution record and directly accesses required provider fields: [beam script](/Users/rishyanthreddy/Desktop/Marimo/spikes/beam_cyp2d6_docking.py:380).
- Targeted suite: **32 passed, 1 skipped**.
- Full non-browser suite: **210 passed, 9 skipped**.
- `marimo check standalone_app.py`: exit 0.
- Strict Python compilation: exit 0.
- Embedded CYP2D6 JSON equals the packaged JSON; raw PDB/PDBQT markers are absent from the standalone bundle.
- Bundle size: **196,415 bytes**, below the 200,000-byte limit.

Evidence: [payload-binding test](/Users/rishyanthreddy/Desktop/Marimo/tests/test_cyp2d6_docking.py:185), [execution record](/Users/rishyanthreddy/Desktop/Marimo/data/packaged/beam_cyp2d6_execution_record.json:4), [docking artifact](/Users/rishyanthreddy/Desktop/Marimo/data/packaged/cyp2d6_docking_results.json:24).

## Blocking findings

1. **Standalone artifact digest drift**

   The current `standalone_app.py` hashes to:

   `455016a0425966eac0e17cb6f84cfb4938f30803718f424f18d9097182dad94c`

   This conflicts with:

   - [MOLAB_STAGING_REPORT.md](/Users/rishyanthreddy/Desktop/Marimo/docs/MOLAB_STAGING_REPORT.md:19): `9f808c61…`
   - [molab_cold_boot_results.json](/Users/rishyanthreddy/Desktop/Marimo/docs/molab_cold_boot_results.json:2): `72430959…`

   Therefore, the staging/cold-boot evidence is not cryptographically bound to the current deliverable.

2. **Live browser gate not reproduced**

   `RUN_BROWSER_TESTS=1 PYTHONWARNINGS=error ... pytest` failed because Chrome aborted during Playwright launch (`TargetClosedError`/`SIGABRT`) before page assertions. The prior [DevTools report](/Users/rishyanthreddy/Desktop/Marimo/docs/DEVTOOLS_AUDIT_REPORT.json:1) is not bound to the current standalone digest.

A further defense-in-depth issue remains: the UI contains static CYP2D6 defaults on the no-evaluation path ([app.py](/Users/rishyanthreddy/Desktop/Marimo/app.py:1098)); this does not affect the valid embedded artifact path but is not fully fail-closed for malformed data.

## Final decision

Round 18 successfully closes the requested provider-payload and packaging-record remediations. However, **unconditional Tier 3 sign-off is withheld** until the current standalone artifact receives one consistent digest across the bundle, staging report, cold-boot report, and hosted artifact, followed by a clean live-browser verification.

The Antigravity second-pass was attempted but cancelled before producing evidence; this report is based on independent local verification.