## Round 20 Audit & Sign-Off

Calibrated score: **98 / 100**

Unconditional Tier 3 Sign-Off (100/100): **Not granted.**

| Gate | Score | Finding |
|---|---:|---|
| Gate 1 — Docking Integrity & Biophysical Grounding | **40/40** | Docking schema, 20 runs, Beam provenance, raw payload binding, PDBQT reproducibility, and honest Asp301 proximity checks pass. |
| Gate 2 — Reactive UI Integration & Scientific Calibration | **28/30** | Static empty-list fallback and canonical-narrative leakage are fixed, but no-evaluation cards still display numeric sentinels. |
| Gate 3 — Molab Bundling, SLA & Staging | **30/30** | Artifact identity, size budget, cold-boot report, staging records, and focused package tests pass. |

### Gate 2 blocking finding

The empty-evaluation branch assigns numeric sentinel values:

- `0.0 kcal/mol`
- `99.9 Å`

Those values are still rendered by the card templates as visible metrics in both artifacts:

- [app.py:1127](/Users/rishyanthreddy/Desktop/Marimo/app.py:1127), [app.py:1159](/Users/rishyanthreddy/Desktop/Marimo/app.py:1159)
- [standalone_app.py:1958](/Users/rishyanthreddy/Desktop/Marimo/standalone_app.py:1958), [standalone_app.py:1990](/Users/rishyanthreddy/Desktop/Marimo/standalone_app.py:1990)

The canonical Paroxetine narrative itself is correctly guarded by an actual matching evaluation at [app.py:1094](/Users/rishyanthreddy/Desktop/Marimo/app.py:1094) and [standalone_app.py:1925](/Users/rishyanthreddy/Desktop/Marimo/standalone_app.py:1925).

I executed both cells with `docking_evaluations=[]`: the no-evaluation badge and narrative appeared, the canonical narrative did not, but `0.00 kcal/mol` and `99.90 Å` remained in the rendered output.

### Verification completed

- Artifact size: **197,267 bytes**
- SHA-256: **`04bbfe4f794b683c0766fd6fd1306379a006ef030b42af3f7bd1b0f6098bece0`**
- Focused tests: **10 passed**
- Full default suite: **210 passed, 9 skipped**
- `marimo check app.py`: **exit 0**
- `marimo check standalone_app.py`: **exit 0**
- Cold-boot report: 5 runs, median **4.044 s**, p95 **4.591 s**
- Existing DevTools report remains internally consistent and PASS.
- The opt-in browser rerun was environment-blocked: Chrome aborted at launch, yielding 210 passed, 2 failures, and 7 errors.

Required correction: render Vina affinity and heme-distance fields as explicit `No Evaluation Available` values when `_target_eval is None`, and add a regression test for the empty-evaluation branch.