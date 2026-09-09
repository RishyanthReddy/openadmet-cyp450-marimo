# Round 11 Adversarial Audit Verdict

## Executive summary

Calibrated score: **94/100**

Tier 1 is **not fully passed**. The modular `app.py` implementation is largely functional, but the generated standalone bundle has a reproducible JavaScript syntax failure that prevents all five `BioactivationTracer` widgets from mounting offline.

Therefore:

**Tier 2 is not authorized.**

The previous second-agent review suggested 98/100 authorization, but independent runtime verification overrules that recommendation.

Verified evidence:

- Focused Tier 1/DevTools tests: **22 passed**
- Normal suite: **192 passed, 8 skipped**
- Explicit browser suite: **200 passed**, zero warnings/errors
- Both `marimo check` commands: **exit 0**
- Strict compilation: **exit 0**
- Bundle size: **199,487 bytes**
- Deterministic temporary rebundle: **byte-identical**
- Current modular runtime: HTTP 200, all five Acts, zero console errors, zero network failures, 96 SVGs, 5 widgets, 22.63 ms p95 reactive latency
- Temporary standalone runtime: HTTP 200 and no external browser requests, but **five JavaScript syntax errors and zero mounted custom widgets**

## Card-by-card forensic evaluation

| Card | Verdict | Findings |
|---|---|---|
| EC-T1-01 | Partial | Act 1 uses the required native accordion and preserves the protocol content. Raw `<details>`/`<summary>` tags are absent. However, the DOME item is titled `"📋 DOME Recommendations Compliance (Machine Learning in Life Sciences)"`, while the authoritative specification requires the exact shorter title `"📋 DOME Recommendations Compliance"` ([plan:150](</Users/rishyanthreddy/Desktop/Marimo/docs/TIER1_TIER2_IMPLEMENTATION_PLAN.md:150>), [app.py:1616](</Users/rishyanthreddy/Desktop/Marimo/app.py:1616>)). |
| EC-T1-02 | Pass | All Act 2, Act 3, and Act 5 native `mo.stat` values and direction semantics are present. Current browser inspection confirmed all ten rendered stat cards, including neutral ROC-AUC and lower-is-better Brier/FDP semantics ([app.py:550](</Users/rishyanthreddy/Desktop/Marimo/app.py:550>), [app.py:874](</Users/rishyanthreddy/Desktop/Marimo/app.py:874>), [app.py:1446](</Users/rishyanthreddy/Desktop/Marimo/app.py:1446>)). |
| EC-T1-03 | Pass in modular app; fails standalone portability | The normalizer handles `None`, empty lists/dicts, row lists, dicts-of-columns, and DataFrame-like records. Table 1.1 is single-select with Raloxifene default and hidden SMILES ([app.py:96](</Users/rishyanthreddy/Desktop/Marimo/app.py:96>), [app.py:259](</Users/rishyanthreddy/Desktop/Marimo/app.py:259>)). Live clicks on two compounds updated both the Act 1 widget and Act 3 docking name. The generated bundle’s widget JavaScript, however, is invalid. |
| EC-T1-04 | Pass in modular app; fails standalone portability | Table 5.1 is correctly single-select, hides machine columns, and live selection updates the candidate card. Empty selection has a safe callout ([app.py:1381](</Users/rishyanthreddy/Desktop/Marimo/app.py:1381>), [app.py:1535](</Users/rishyanthreddy/Desktop/Marimo/app.py:1535>)). Literal specification gaps remain: the textual card does not explicitly display SMILES or nominal alpha, and the calculated safe layout is unused ([app.py:1542](</Users/rishyanthreddy/Desktop/Marimo/app.py:1542>)). |
| EC-T1-05 | Pass in modular app | The six-column schema, lazy data/filename callables, active-alpha closure, UTF-8 encoding, and algorithmic selected-index export are correctly implemented ([app.py:1392](</Users/rishyanthreddy/Desktop/Marimo/app.py:1392>), [app.py:1438](</Users/rishyanthreddy/Desktop/Marimo/app.py:1438>)). Live download at α=0.15 produced the correct filename, UTF-8 CSV, exact header, and current rows. |
| EC-T1-06 | Fail | Size, deterministic rebundling, static checks, compilation, and test counts pass. The actual standalone runtime does not: its inlined ESM fails syntax parsing, producing five console errors and zero `.bat-container` widgets. The checked-in DevTools report is also stale. |

## Root cause of the standalone failure

The source widget JavaScript is valid: `node --check widgets/bioactivation_tracer.js` exits 0.

The bundler removes line comments using:

```python
re.sub(r"//.*", "", no_comments)
```

at [scripts/bundle_app.py:34](</Users/rishyanthreddy/Desktop/Marimo/scripts/bundle_app.py:34>).

That regex incorrectly treats the `//` inside the SVG namespace string at [widgets/bioactivation_tracer.js:181](</Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:181>) as a comment. The generated bundle therefore contains:

```javascript
const svgNS = "http:
```

at [standalone_app.py:607](</Users/rishyanthreddy/Desktop/Marimo/standalone_app.py:607>).

Direct `node --check` on the extracted bundle ESM fails with `SyntaxError: Invalid or unexpected token`. A temporary-directory standalone launch reproduced the same failure in Chrome five times.

This is a hard portability defect, not a cosmetic discrepancy.

## Marimo reactivity and scoping audit

The modular DAG is structurally sound:

- Both `marimo check` commands passed.
- No duplicate definitions, cycles, or syntax failures were reported.
- Table selection is consumed through `table.value`; private widget internals are not used.
- `selected_name` is a reactive dependency of both the Act 1 viewer and Act 3 docking card.
- Candidate preview selection remains separate from algorithmic `_selected_indices`.
- The CSV builder closes over the active alpha, selected index set, and conformal cutoff.
- Alpha changes recompute the candidate table, KPI values, filename, and download payload.
- Current modular browser interaction produced no console errors or network failures.

Remaining silent-risk items:

- The retained Act 3 dropdown is effectively a fallback, but the UI does not clearly document that Table 1.1 is the primary source.
- The candidate card computes `safe_generate_molecule_layout` but discards the result.
- The dedicated tests are mostly source-substring tests. In particular, the DOME test accepts the parenthetical title because it only checks for a substring ([tests/test_tier1_ui.py:31](</Users/rishyanthreddy/Desktop/Marimo/tests/test_tier1_ui.py:31>)), and the CSV round-trip test constructs a mock CSV rather than invoking the application’s actual builder.

## DevTools artifact audit

The checked-in report says:

- timestamp: `2026-09-08T12:37:16Z`
- 84 SVGs
- 4 widgets
- 8.92 ms p95

The current source and bundle were modified around 20:11 IST, while the report was modified at 18:07 IST ([DEVTOOLS_AUDIT_REPORT.json:2](</Users/rishyanthreddy/Desktop/Marimo/docs/DEVTOOLS_AUDIT_REPORT.json:2>)). A fresh modular run measured:

- 96 SVGs
- 5 widgets
- 22.63 ms p95
- zero console errors
- zero network failures

The current count of five widgets is consistent with the new candidate preview widget. The problem is that the checked-in report does not certify the current build and still reports four. It must be regenerated and the expected count reconciled.

## Standalone bundle and offline portability

Passes:

- Exact size: **199,487 bytes**, 513 bytes below the 200,000-byte limit.
- Temporary rebundle was byte-identical to the checked-in file.
- Embedded datasets and fallback loaders work without project data files.
- Temporary standalone server returned HTTP 200 and rendered all five Acts.
- No external browser requests were observed.
- No Beam, CUDA, Torch, requests, urllib, or startup `fetch()` dependency exists in the standalone path.
- The PubMed URLs present are citation hyperlinks, not startup network dependencies.

Fails:

- The inlined AnyWidget ESM is syntactically invalid.
- All five intended custom widgets fail to mount.
- Chrome reports five unhandled syntax errors.
- This is a portable single-file Python application, not a self-contained WASM runtime; it still requires its declared Python environment dependencies.

## Final authorization

**Tier 1: Not passed.**

**Tier 2 Beam Cloud RTX 4090 Dual-Isoform CYP2D6 Docking: Not authorized.**

Required before reconsideration:

1. Make the bundler’s JavaScript comment removal string-safe, then regenerate `standalone_app.py`.
2. Verify the generated ESM with Node syntax checking and a standalone browser run with zero console errors and mounted widgets.
3. Change the DOME accordion key to the exact required title.
4. Regenerate `docs/DEVTOOLS_AUDIT_REPORT.json` from the current build and reconcile the expected widget count.
5. Strengthen the exact-title, standalone-runtime, candidate-card, and real CSV-builder tests.

No project files were modified during this audit.