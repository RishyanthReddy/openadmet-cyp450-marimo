# Round 14 Final Tier 2 Audit

Verdict: **Not approved for unconditional sign-off**  
Calibrated score: **82 / 100**  
Tier 3 authorization: **Not granted**

| Gate | Result |
|---|---:|
| EC-T2-01 docking integrity | 32/40 |
| EC-T2-02 UI integration | 22/30 |
| EC-T2-03 bundling/seams | 28/30 |

What passes:

- JSON contains 10 compounds × 2 receptors = 20 successful runs, with valid SHA-256 provenance.
- All raw PDBQT pose hashes, Vina scores, and Fe distances independently reproduce.
- Paroxetine artifact values are internally consistent: 3TBG `-8.80`, Fe `4.89 Å`, Asp301 `6.71 Å`; 4WNW `-9.11`, Fe `5.03 Å`, Asp301 `6.31 Å`. ([artifact](</Users/rishyanthreddy/Desktop/Marimo/data/packaged/cyp2d6_docking_results.json:202>), [report](</Users/rishyanthreddy/Desktop/Marimo/docs/CYP2D6_DOCKING_REPORT.md:17))
- Embedded standalone payload exactly equals the packaged JSON after decompression.
- Bundle size is **199,290 bytes**, below the strict 200,000-byte limit.
- Targeted Tier 2 tests pass: **9 passed** with capture disabled.
- Direct extracted ESM validation passes with Node.

Blocking findings:

1. **Remote Beam provenance is not independently verifiable.**  
   The UUID `dc1112ce-e7dc-4abe-943b-790ccae2e9b5` appears only in the audit prompt, not the artifact, report, or execution record. The artifact stores only `task_id: "EC-T2-01"` ([artifact](</Users/rishyanthreddy/Desktop/Marimo/data/packaged/cyp2d6_docking_results.json:4>)). The Beam script records telemetry but no Beam job ID or image digest ([beam script](</Users/rishyanthreddy/Desktop/Marimo/spikes/beam_cyp2d6_docking.py:380>), contrary to the documented requirement ([plan](</Users/rishyanthreddy/Desktop/Marimo/docs/TIER1_TIER2_IMPLEMENTATION_PLAN.md:1112)).

2. **The submitted geometry narrative conflicts with repository evidence.**  
   The prompt gives different Fe coordinates and claims Asp301 distances of 4.89/5.03 Å. The raw logs and manifest use Fe coordinates `[7.824, 26.318, 4.25]` and `[-12.185, -16.913, 37.726]` ([3TBG log](</Users/rishyanthreddy/Desktop/Marimo/data/processed/pdbqt/cyp2d6/logs/docked_3TBG_paroxetine.log:23>), [4WNW log](</Users/rishyanthreddy/Desktop/Marimo/data/processed/pdbqt/cyp2d6/logs/docked_4WNW_paroxetine.log:23>)), while Asp301 is 6.71/6.31 Å.

3. **The UI overcalls Asp301 geometry.**  
   The artifact marks the observation `proximity_only`, but the UI labels it “Electrostatic Salt Bridge” ([app.py](</Users/rishyanthreddy/Desktop/Marimo/app.py:1114>), [artifact](</Users/rishyanthreddy/Desktop/Marimo/data/packaged/cyp2d6_docking_results.json:215>)).

4. **The isoform selector is not functionally reactive.**  
   `cyp2d6_isoform_dropdown` offers 3TBG/4WNW conformations, not CYP2D6-vs-CYP3A4 selection, and its `.value` is never consumed. The card always renders both conformations ([app.py](</Users/rishyanthreddy/Desktop/Marimo/app.py:1067>), [app.py](</Users/rishyanthreddy/Desktop/Marimo/app.py:1176>)). Main-view wiring itself is correct ([app.py](</Users/rishyanthreddy/Desktop/Marimo/app.py:1830>).

5. **Exploratory mechanism callouts can render `None warhead`.**  
   The fixture uses `reactive_warhead_motif`, but the docking pipeline reads `warhead`; all packaged values are null ([pipeline](</Users/rishyanthreddy/Desktop/Marimo/spikes/beam_cyp2d6_docking.py:369>), [app.py](</Users/rishyanthreddy/Desktop/Marimo/app.py:1097>)).

Verification caveat:

- `marimo check` exits 0 but emits an unhandled temporary-directory exception.
- Exact `py_compile` fails because this read-only environment cannot write `__pycache__`.
- Full suite produced **196 passed, 9 skipped, 5 failed, 2 errors**; the failures/errors are environment write/temp-file failures, so the claimed 203-pass result is not independently confirmed here.

Required before sign-off: record the real Beam job/image provenance, correct the UI’s selector and chemistry labels, map the warhead field correctly, and rerun the complete suite in a writable environment.