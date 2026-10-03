# Submission candidate verification

## Candidate

Branch: `codex/submission-readiness`. Artifact: `standalone_app.py`.

- SHA-256: `9a93ab962af66ed0004b1070cb7a6e730f3a29ddc2ea50c26518bd14e4bff50d`.
- Size: **187,396 bytes**; internal budget headroom: **12,604 bytes**.
- Primary dataset SHA-256: `6faaf1d741b33223916bfaf85cf8db6c29e332b7aef098916640eac63f19e2f2`.

## Checks and their scope

- `marimo check --strict app.py standalone_app.py`: passed.
- Earlier metric-card revision passed 27 targeted checks and browser overflow assertions. Current spacing-only revision passed strict marimo validation and 4 staging checks; desktop cards were inspected in the in-app browser, and the assay grid was measured at 390px with no internal overflow. Full suite not repeated for this spacing change.
- A fresh uv environment resolved the script lock and installed only the notebook runtime dependencies. The notebook was copied into an isolated temporary folder and run there. This verifies the embedded fallback without repository data or the original chemistry environment.
- A separate compatibility environment `/tmp/marimo-submission-env` runs the broader repository suite with marimo 0.25.0; it shares original chemistry dependencies and is not a clean installation.
- Live standalone interactions passed: reveal switch, actual architecture metric changes, literature table-to-docking linkage, invalid-to-valid custom structure, a real chart-point click, table selection after chart selection, alpha endpoints, and exact CSV identities/p-values/cutoff/alpha.
- Real-DOM widget check passed: invalid-to-valid model update preserves tooltip, warning text cannot inject an image, hover provenance is present, dark-mode variables exist, and cleanup removes the component.
- Chemical/provenance regressions passed: heuristic/quantum separation, explicit atom-map validation, stereoisomer identity/wedges, invalid BH inputs, partition disjointness, full-precision packaging and sample flags.
- Five local fresh starts: median 3.651s, p95 4.527s; no external notebook requests or console errors. Initial package installation requires internet. See `molab_cold_boot_results.json` for timestamps and raw results.
- Literal saved-credential scan of tracked/candidate files and decoded standalone gzip payloads found no matches; `.env` is untracked and excluded from Beam upload. This is a scoped scan, not a universal secrets guarantee.
- Desktop and 390px mobile screenshots were inspected. Mobile comparison grids now stack into one column.

## Science and presentation changes

Selection packaging now consumes the TRAIN-only workflow, rather than mixing OOF scores with calibration. New provenance includes input and holdout hashes, training parameters and display-pool policy. Default molecule halos are explicitly heuristic. Random/scaffold tables and the chemical-distance plot now read the saved results; unsupported histogram bins and stale logistic-regression table values were removed.

The text was rewritten around questions a chemist would ask. Current selection counts and cutoff are prominent; historical resampling is in a disclosure. Unsupported safety, causal redesign, mechanistic significance and GPU-docking claims were corrected. The full quantum cache's missing model/conformer provenance remains disclosed.

## Release gates

Publication, a fresh hosted molab check, final narrated video/upload/access check, entrant details and final submission remain open. No push, deployment, merge or form submission has occurred. Existing untracked user assets are preserved and excluded from the proposed release.

Studio, experimental pet/Jev integrations, a Pixi GPU environment and WASM export were deferred in favor of the reliable notebook. The candidate uses marimo 0.25.0, inline dependency metadata, a uv lock, expanded output, native widgets/disclosures, and linked Altair selections. No new external service or account is required for notebook interaction.

## Card spacing

Literature viewers use a 1:2 molecule/evidence split and top alignment so the text card does not stretch to match the molecule height. Assay metadata uses three columns on desktop, two below 900px, and one below 540px.

## Release verification

User authorized deployment. Final full suite with browser checks: **237 passed in 45.75 seconds**, zero skips. Current notebook SHA-256: `9a93ab962af66ed0004b1070cb7a6e730f3a29ddc2ea50c26518bd14e4bff50d`. Saved-credential literal scan found no matches; .env is not tracked. Hosted verification follows publication.

## Revised narrative release — October 3

237 tests passed, zero skips, in 47.75s (`RUN_BROWSER_TESTS=1 GENERATE_DEVTOOLS_REPORT=1`). Strict marimo checks passed. The revised notebook is 188,571 bytes, SHA-256 `e5a2d0010142774720a3a2dbbf5a93541168be0c4be81c643aa2d642dbec04c5`. Five local cold starts: median 3.515s, p95 4.381s; zero external notebook requests and console errors. Accordion tests open the relevant panels; widget checks assert five mounted molecule viewers instead of depending on decorative SVG counts.

Final export revision: 188,575 bytes; SHA-256 `92fcfff16fa893e30abc7dfed49bedfc940729ea48f35f7e0fef8aaf8dbded65`. Full browser-enabled suite passed 237 tests with exit 0 in 44.80s. Local cold-start timings and hosted limits are in MOLAB_DEPLOYMENT.md.
