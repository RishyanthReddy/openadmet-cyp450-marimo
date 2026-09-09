# Round 15 Final Tier 2 Audit

Verdict: **92 / 100 — no unconditional Tier 3 sign-off.**

| Gate | Score | Assessment |
|---|---:|---|
| EC-T2-01 Docking Integrity | **35/40** | 20/20 runs, all successful; raw PDBQT values, coordinates, hashes, and `proximity_only` Asp301 labeling reproduce correctly. Provenance is recorded, but not independently authenticated. |
| EC-T2-02 UI Integration | **28/30** | Panel is mounted and reactive; selector filters 3TBG/4WNW; all ten warheads are populated. Minor provenance-display and scientific-narrative issues remain. |
| EC-T2-03 Bundling & Seams | **29/30** | `standalone_app.py` is exactly 195,780 bytes; embedded payload matches the packaged artifact byte-for-byte after canonicalization. Relevant tests pass; sandbox tempdir warnings prevent a fully clean verification claim. |

## What passes:

- Artifact contains 10 compounds × 2 receptors with 20 successful runs: `data/packaged/cyp2d6_docking_results.json`.
- Raw ligand and pose SHA-256 hashes match the packaged metadata.
- Heme Fe coordinates and Paroxetine Asp301 distances match raw PDB/PDBQT evidence.
- The report and UI now use non-contact/proximity language: `docs/CYP2D6_DOCKING_REPORT.md`.
- Selector reactivity is genuinely wired through `.value`: `app.py:1067`, `app.py:1144`.
- Act 3 is mounted in the main view: `app.py:1867`.
- All ten artifact warheads exactly match the fixture and are non-empty.
- Bundle enforcement is present at `scripts/bundle_app.py:585`.

## Blocking residuals:

1. **Beam provenance is recorded but not independently verifiable:**
   The task ID is hard-coded in the packaging script (`beam_cyp2d6_docking.py:399`); the returned Beam result contains telemetry/results but no provider-issued task record, and no immutable image digest is stored. The implementation plan explicitly requires the Beam job ID, image digest, and hardware result (`docs/TIER1_TIER2_IMPLEMENTATION_PLAN.md:1112`).

2. **The UI narrative still implies that the reactive methylenedioxyphenyl warhead is at the 4.89 Å Fe distance:**
   In `app.py`, the artifact and raw pose identify the nearest atom as fluorine, not the reactive warhead: `cyp2d6_docking_results.json:214`. This should be labeled as whole-molecule nearest-heavy-atom proximity unless a warhead-specific distance is computed.

## Verification summary:

- Tier 2 docking/UI tests: **9 passed**.
- Additional staging/package/phase seam tests: **19 passed**.
- Both Marimo checks returned exit 0, but emitted sandbox temp-directory warnings.
- The exact prescribed pytest command could not create its capture tempfile; the capture-disabled retry passed.
- Antigravity review was attempted but cancelled before execution.

Therefore, the five Round 14 surface remediations are substantially present, but Tier 2 does not yet meet the unconditional 100/100 standard.
