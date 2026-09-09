# Final Adversarial Audit Report

## Verdict

**Calibrated score: 87/100**

**Phase 4 runtime gates: PASS in this macOS environment.**  
**Repository-wide submission-grade sign-off: WITHHELD — revision required.**

The project is technically strong, but the claimed live NCBI architecture is not connected to the active application path, and there are material security, provenance, and test-hygiene issues.

## Empirical verification

| Check | Result |
|---|---:|
| `pytest tests/test_ncbi_client.py -v` | **7 passed** |
| `pytest tests/test_fuzzing.py -v` | **22 passed** |
| `pytest tests/test_devtools_audit.py -v` | **8 passed** |
| `pytest tests/test_phase3_seam.py -v` | **9 passed** |
| `pytest tests/test_docking_ablation.py -v` | **5 passed** |
| `pytest tests/test_mmps.py -v` | **4 passed** |
| `pytest tests/test_txconformal.py -v` | **4 passed** |
| `pytest tests/ -q` | **168 passed, 0 skipped** |
| Marimo checks | **Both exit 0** |
| Embedded NCBI records | **16** |
| Isolated standalone export | **964,636-byte HTML generated successfully** |

No Git metadata is present, so commit-level provenance and tracked/untracked status could not be verified.

## Round 6 checklist

1. **Docking reproducibility — PASS, qualified.**  
   All 10 compounds across both receptors are checked against raw PDBQT data in [tests/test_docking_ablation.py:92](/Users/rishyanthreddy/Desktop/Marimo/tests/test_docking_ablation.py:92). Report generation is dynamically data-driven at [spikes/docking_ablation.py:476](/Users/rishyanthreddy/Desktop/Marimo/spikes/docking_ablation.py:476). The artifact still retains a historical alias and the application contains a hardcoded Act 1 docking map.

2. **Packaged conformal diagnostics — PASS.**  
   All eight full-holdout records contain `empirical_fdp_diagnostic_passed` and diagnostic notes. The UI appropriately says “Observed Screening FDP Diagnostic.” Legacy `fdr_controlled` field names remain in the model and artifact.

3. **Fail-closed browser tests — PASS locally.**  
   No `pytest.skip` remains, and live Chrome tests pass. Portability remains weak because Chrome is hardcoded to a macOS path at [tests/test_devtools_audit.py:23](/Users/rishyanthreddy/Desktop/Marimo/tests/test_devtools_audit.py:23).

4. **Terminology cleanup — PASS for active UI, not repository-wide.**  
   Active UI uses “active-site steric proximity,” but historical aliases and stale terminology remain in supporting documents and scripts.

5. **Row-level MMP provenance — FUNCTIONALLY PASS, qualified.**  
   The 34 MMPs carry assay measurements and deterministic row tokens via [scripts/generate_mmps.py:74](/Users/rishyanthreddy/Desktop/Marimo/scripts/generate_mmps.py:74). However, `cyp_splits.parquet` has no native source-row ID; the identifiers are synthesized from dataframe indices and molecule names.

## NCBI Entrez evaluation

The client itself is genuine and technically functional:

- It uses the real HTTPS `esummary.fcgi` endpoint at [models/ncbi_client.py:115](/Users/rishyanthreddy/Desktop/Marimo/models/ncbi_client.py:115).
- Credentials are passed through request parameters.
- A live force-refresh query succeeded.
- Live comparison found **zero metadata mismatches across all 16 cached records** for title, journal, date, DOI, and authors.
- The ten curated PMIDs are all verified.
- Offline disk/embedded fallback tests pass.

Important discrepancies remain:

- The active `app.py` imports `load_ncbi_pubmed_cache` but never calls it; Act 1 loads the pre-enriched embedded fixture at [app.py:150](/Users/rishyanthreddy/Desktop/Marimo/app.py:150).
- `NCBIEntrezClient` is never instantiated by either active application. The badge is driven statically by `entry["ncbi_verified"]` at [app.py:209](/Users/rishyanthreddy/Desktop/Marimo/app.py:209).
- Therefore, the documented “live queries → disk cache → embedded fallback” architecture is not active in the user-facing Act 1 runtime.
- The cache contains **16 records**, six unrelated to the ten curated MBIs.
- No cache record contains retrieval timestamp, source URL, raw response, or provenance hash.
- Two of the ten curated PMIDs have no DOI, so the report’s “10/10 PMIDs verified with DOI links” claim is inaccurate; the actual DOI coverage is **8/10**.
- Partial NCBI responses silently omit missing PMIDs instead of returning structured fallback records.
- There is no explicit retry, throttling, atomic cache write, or read-only-cache handling.
- Plaintext credentials exist in `.env`, and personal credential information is repeated in [docs/PHASE4_BROWSER_QA_REPORT.md:66](/Users/rishyanthreddy/Desktop/Marimo/docs/PHASE4_BROWSER_QA_REPORT.md:66).

## Phase 4 evaluation

### DevTools

The current artifact reports:

- 342 network responses
- 0 HTTP 4xx/5xx responses
- 0 console errors
- 84 SVG elements
- 4 `.bat-container` widgets
- 8.92 ms reactive p95
- Chrome 152

These results reproduce successfully. However:

- The pytest fixture rewrites the checked-in report at [tests/test_devtools_audit.py:206](/Users/rishyanthreddy/Desktop/Marimo/tests/test_devtools_audit.py:206).
- The test mostly verifies counts and DOM presence; it does not robustly prove all dropdown, slider, and button behaviors.
- Synthetic keyboard events are used for the latency measurement without asserting that the control value or rendered state changed.
- Transport-level request failures are not separately captured.

### Defensive fuzzing

The 22 cases pass, and the safe fallback exists at [widgets/layout_engine.py:259](/Users/rishyanthreddy/Desktop/Marimo/widgets/layout_engine.py:259). The warning banner exists at [widgets/bioactivation_tracer.js:146](/Users/rishyanthreddy/Desktop/Marimo/widgets/bioactivation_tracer.js:146).

Residual concern: active application paths still call strict `BioactivationTracer.from_smiles` rather than `safe_from_smiles`. Also, the warning text is interpolated into `innerHTML` without escaping.

### Standalone isolation

This gate passes strongly. Copying only `standalone_app.py` into an empty directory produced a self-contained export and embedded fallback badge. The standalone loader correctly falls back to embedded assets at [standalone_app.py:69](/Users/rishyanthreddy/Desktop/Marimo/standalone_app.py:69).

## Score breakdown

| Dimension | Score |
|---|---:|
| Scientific and chemical truth | **23/25** |
| Data provenance and MMP integrity | **13/15** |
| Statistical and conformal rigor | **18/20** |
| Architecture, portability, and bundling | **17/20** |
| AnyWidget frontend and defensive UI | **8/10** |
| Test coverage and evidence integrity | **8/10** |
| **Total** | **87/100** |

## Required pre-submission corrections

1. Wire `NCBIEntrezClient` into Act 1, or relabel the UI as build-time pre-verified fixture metadata.
2. Remove/rotate credentials, scrub documentation, and eliminate the hardcoded personal-email fallback.
3. Clean and provenance-tag the NCBI cache; handle partial responses and write failures.
4. Use safe molecule factories in active paths and escape warning HTML.
5. Make browser paths configurable and move report generation out of ordinary pytest execution.
6. Correct the “10/10 DOI links” statement and dynamicize the static docking proximity label.

**Final sign-off: CONDITIONAL / REVISION NEEDED.** The platform is ready for a controlled local demo, but I cannot defensibly grant a repository-wide 90+ submission-grade sign-off in its current state.