# Submission readiness plan

Prepared 2026-10-03. Core implementation has been completed locally with explicit direct-Codex authorization. See [current verification](SUBMISSION_VERIFICATION.md) for actual evidence; publication and final submission gates remain open.

## Outcome and submission contract

Deliver a public, runnable molab notebook that answers one question clearly: **When should we trust a CYP liability prediction?** A reader should be able to explore molecular evidence, see why evaluation choices matter, understand the limits of physics augmentation, and inspect a statistically selected candidate set.

The official competition requires a molab link and video explainer. It emphasizes intuition, chemical validity, creativity, and purposeful customization. Unrunnable submissions are disqualified. AI assistance must be disclosed.

References:
- https://marimo.io/pages/events/notebook-competition-3
- https://docs.google.com/spreadsheets/d/1xEd-njH43jTWQfr-2wjXULhiGKXl6zEvmKIobWOO8Ks/edit?gid=620363524
- https://form.jotform.com/262315091510143

The posted deadline is October 4, 2026, 11:59 PM PST. Use October 4 evening in Zurich as our internal target, leaving time for upload and access problems. Do not depend on interpreting PST versus Pacific daylight time in the final hour.

Submission acceptance criteria:
1. The exact public molab link loads the final version in a fresh viewer session.
2. Every visible control works; invalid input and missing data receive useful explanations.
3. Displayed scientific quantities are traceable to the artifacts that produced them.
4. Structural alerts, computed descriptors, model predictions, assay measurements, docking geometry, and literature evidence are distinctly labeled.
5. Evaluation and candidate-selection data provenance are checked, including model training versus calibration/test separation.
6. The notebook, README, video, and submission description agree on metrics, capabilities, and limitations.
7. Relevant automated and live browser checks pass against the final artifact; skips and limitations are recorded.
8. The video and notebook are viewable by judges without access to our credentials.
9. The public package contains no secrets.
10. The final submission receipt and tested artifact revision are recorded.

## Starting evidence

- Default suite freshly passed: 213 passed, 9 skipped. This does not verify hosted operation.
- Local marimo is 0.24.0; notebook metadata permits marimo >=0.11.0.
- Current standalone artifact is 199,861 bytes, 139 bytes below the repository's enforced 200,000-byte budget.
- The official competition page reviewed does not establish that byte budget as a competition rule. Verify platform constraints before describing it as a molab requirement.
- Primary curated data contains 6,145 compounds; endpoints have separate assay masks.
- Runtime primarily displays precomputed artifacts. Beam credentials are available locally, but availability does not establish a spending budget.
- Default molecule halo scores are motif heuristics; their current quantum wording needs correction or genuine atom-level results.
- Historical verification reports and submission documents refer to older artifact versions.
- Existing untracked docs/assets and screenshots must be preserved.

## Decisions and remaining inputs

Confirmed by the user on October 3:
1. Reliable submission first; Studio only if time remains.
2. Choose the strongest centerpiece for the competition. Recommended question: **When should we trust a CYP liability prediction?** This connects the original custom widget, chemical evidence, honest model failures, and reactive candidate selection. It is a strategic recommendation, not a prediction of winning.
3. Up to **$25 total** for targeted Beam recomputation. Prioritize repairing scientifically necessary artifacts over broad retraining or extra benchmarks. Check pricing before launch, track cumulative spend, and bound job count/duration; do not exceed the ceiling. Computational use of saved credentials is authorized for this bounded scope; revealing or publishing them is not.
4. No final public molab link or recorded video is ready. Include creating both. An older candidate link is recorded in docs/JOTFORM_SUBMISSION_PACKAGE.md, but it is not the verified final entry.

Remaining implementation inputs:
1. Actual time available before the internal submission target. Until specified, use the core-first order and drop stretch tasks as needed.
2. Implementation ownership: the session currently exposes no Antigravity delegation tools. The user's control-plane instructions permit direct Codex implementation only with explicit approval of a fallback. Obtain that before implementation-file edits; do not block planning or read-only validation.
3. Entrant/team identity, contact email, and preferred narration/recording approach are needed for the final package, not for early notebook work.

Suggested working title: **From Molecular Alerts to Measured Evidence: When Can We Trust a CYP Prediction?**

## Step 1 — Preserve the baseline and freeze scope

Estimated effort: 30–45 minutes.

Actions:
1. Recheck git status and diff; preserve all existing tracked and untracked user work.
2. Record the baseline commit, standalone hash/size, dependencies, artifact hashes, and current test result in a new current verification record.
3. Work on an isolated branch or appropriate checkout without destructive resets.
4. Separate required submission tasks from optional launch-week experiments.
5. Agree on a feature freeze at least several hours before submission.

Required scope: scientific wording/provenance, narrative, two linked visual explorations, reliable packaging, browser verification, and accurate video/submission materials.

Stretch scope: Studio companion, Pixi reproduction notebook, Lens-assisted review, optional WASM export, actual atom-level quantum overlays, and a 3D docking viewer.

Acceptance: every change has a purpose and a verification gate; there is a recoverable baseline.

## Step 2 — Audit and repair the scientific contract

Estimated effort: 2–4 hours; targeted recomputation may add time.

Expected files: app.py, widgets/layout_engine.py, widgets/bioactivation_tracer.js, models/txconformal_selector.py, scripts/package_assets.py, relevant packaged artifacts and documentation. Touch only files required by confirmed findings.

Actions:
1. Make an evidence map for each displayed number: source file, dataset subset, model version, computation method, and timestamp/hash.
2. Correct default halo labels to structural-alert heuristics. Retain a clearly named heuristic overlay unless verified atom-level quantum values are available.
3. If enabling quantum halos, validate SMILES identity, hydrogen convention, conformer, atom mapping, charge/spin state, model identifier, and the reported descriptor definition. Show unavailable rather than inventing a value.
4. Separate measured TDI from a mechanism-based inactivation hypothesis. Literature examples can involve different isoforms; preserve those distinctions.
5. Describe docking scores and geometry as model outputs. Distinguish whole-ligand minimum heme distance from distance of a chemically implicated reactive atom; avoid interpreting the nearest fluorine as a reaction site.
6. State that Vina uses a CPU backend even when its Beam worker has a GPU. Preserve accurate attribution for GPU descriptor computations.
7. Replace stale augmentation values with the current artifact values: PR-AUC delta +0.0101 and MCC delta +0.0209. Show uncertainty and avoid claiming demonstrated significance without an appropriate comparison.
8. Audit split independence. Confirm grouping identities, fold overlap, endpoint masks, training/calibration/test boundaries, and how packaged candidate p-values were generated.
9. Specifically trace scripts/package_assets.py's OOF predictions used in selection. Resolve any model/calibration/test mismatch with the dedicated selector's training-only workflow; regenerate affected selection artifacts if necessary. Do not silently reuse incompatible p-values.
10. Explain that current alpha changes selection in the displayed candidate pool; historical Monte Carlo summaries describe a separate experiment and may use discrete alpha buckets.
11. Review chemical edge cases: salts, charges, stereochemistry, invalid SMILES, acyclic grouping, and missing assay values. Use RDKit stereochemical depiction where needed or state display limitations accurately.
12. Correct D-MPNN training documentation where it claims validation checkpointing or early stopping absent from the current training script. Describe actual confidence-interval resampling units; avoid calling molecule-level bootstrap group-level bootstrap.
13. Present molecular pairs as observed label changes, not proven causal redesign recommendations. Treat error explanations as hypotheses unless attribution supports them.

Acceptance: misleading labels are removed; all main claims have artifact support; unresolved scientific issues are either corrected or visibly bounded. Selection results cannot ship with unexplained evaluation leakage.

## Step 3 — Make the five acts one learnable story

Estimated effort: 1–2 hours.

Expected files: app.py and later regenerated standalone_app.py.

Actions:
1. Add a short opening: question, why it matters, what the reader will do, and the distinction between precomputed evidence and interactive exploration.
2. Add a compact navigation/outline and a suggested five-minute path.
3. Choose one literature molecule for the evidence story and one dataset pair/error case for measured-data exploration. Do not force one molecule through unavailable results.
4. Add short captions and one takeaway per act. Place methods, provenance, and advanced explanations in disclosures.
5. Carry a selected compound between compatible views using stable identity; make unavailable evidence explicit.
6. Include a reveal interaction: ask the reader what an alert implies, then show measured or literature evidence and its limitations.
7. End with an actionable interpretation: what the evidence supports, where it is uncertain, and what experiment would be needed next.

Acceptance: a newcomer can identify the central question within 30 seconds and explain two scientific insights after the guided path.

## Step 4 — Add the most useful reactive explorations

Estimated effort: 3–5 hours.

Actions:
1. Build an evaluation comparison plot for random versus scaffold validation, linked to the chosen model and endpoint.
2. Display confidence intervals only for metrics that have them. Show sample count and positive prevalence so values have context.
3. Add a similarity distribution or chemical-neighborhood view tied to available precomputed nearest-neighbor evidence. Use existing artifacts; avoid unnecessary retraining.
4. Build a candidate-selection plot whose threshold, count, and selected rows update with alpha.
5. Link plot/table selection to the molecule inspector; export exactly the currently selected pool with alpha, cutoff, identifiers, and p-values.
6. Keep the historical Monte Carlo diagnostic panel visually separate from current-pool results. Label the nearest precomputed alpha bucket if used.
7. Improve molecular-pair presentation: highlight changed groups and show measured labels, endpoint, and source identity together.
8. Preserve keyboard usability, readable contrast, safe text rendering, and correct widget cleanup on rerender.
9. Use checks for meaningful state changes, stale selections, empty result sets, and CSV consistency. Avoid tests that merely mirror implementation text.

Acceptance: controls change evidence and decisions; the linked views and exports agree; no decorative control implies unsupported computation.

## Step 5 — Integrate recent marimo features selectively

Estimated effort: 1–2 hours for a compatibility pass; Studio may add 3–6 hours.

1. Test a chosen marimo 0.25+ version in an isolated environment. Check notebook linting, rendering, widget lifecycle, bundling, and browser behavior before adopting it. Pin the tested version/range consistently.
2. Add persistent expanded outputs to cells that benefit from them. Check readability in the submitted molab frontend, not only the local editor.
3. Use Lens optionally in the development environment for visual review. Judges must not need an agent connection to follow the notebook.
4. Prototype one Studio view using existing named notebook outputs: a short guided report or presentation. Confirm it supports the needed widgets and state updates before broadening it.
5. Studio is experimental. Continue only if the prototype works within its allotted time and does not compromise required submission work. Keep the main molab entry fully usable.
6. Add a Pixi reproduction workflow for heavier native/GPU computation, preferably a separate reproduction notebook/environment. Validate resolved packages and hardware-specific behavior; CUDA-enabled PyTorch does not provide GPU hardware.
7. Confirm actual Pixi support in the hosted session before making it a startup dependency. Keep the primary precomputed notebook lightweight.
8. If using fsspec storage, load pinned public versions with hash checking and a graceful cache/fallback. Keep credentials out of public notebooks.
9. Prototype single-file/offline WASM only after checking RDKit, PyArrow, widget, and filesystem/network compatibility. Pixi's Conda dependencies cannot be installed by Pyodide.
10. Defer marimohub and the experimental Jev pet palette. Jev literature classification is an optional separate experiment requiring TypeSafe credentials and manual validation; Beam credentials do not cover it.

References:
- https://github.com/marimo-team/marimo/releases/tag/0.25.0
- https://marimo.io/blog/introducing-marimo-studio
- https://marimo.io/blog/pixi-sandboxes
- https://docs.marimo.io/guides/package_management/sandboxes/
- https://marimo.io/blog/introducing-marimo-lens

Acceptance: every adopted feature works in its actual target environment and improves presentation, exploration, or reproducibility. Optional features can be dropped independently.

## Step 6 — Package and document the final notebook

Estimated effort: 1–2 hours.

Expected files: scripts/bundle_app.py, standalone_app.py, README.md, docs/JOTFORM_SUBMISSION_PACKAGE.md, and a current verification manifest.

Actions:
1. Keep app.py and widget/model source authoritative. Regenerate the standalone through scripts/bundle_app.py rather than hand-editing its embedded code.
2. Address the 139-byte headroom before adding features. Verify whether the repository budget remains necessary; do not remove its gate without documenting the reason and updating related expectations.
3. If the budget is retained, create useful headroom through packaging/compression or explicitly scoped external artifacts. Preserve readable source and scientific metadata.
4. Label full-data versus fallback mode, row counts, and any limitations. Do not display a reduced sample as if it were the complete dataset.
5. Update runtime dependency metadata separately from training/reproduction dependencies.
6. Document source datasets, licenses, original custom contribution, Beam computation provenance, reproduction commands, and AI assistance.
7. Verify the repository's actual license before claiming MIT. Add an approved license if one is absent rather than relying on a statement in historical documents.
8. Scan staged/public artifacts for credentials without printing their values. Confirm cloud-upload exclusions, especially .env, before sending any workspace to a worker.
9. Remove unsupported claims such as guaranteed offline operation, universal risk guarantees, or hosted timing inferred from local measurements.
10. Record the exact final artifact hash/size and environment used by every fresh report.

Acceptance: source, standalone, README, and submission metadata agree; secrets stay private; fallback behavior is visible.

## Step 7 — Verify locally and in a fresh hosted session

Estimated effort: 1–3 hours, depending on deployment and startup behavior.

Commands to adapt to the chosen environment:

```sh
.venv/bin/python -m marimo check app.py standalone_app.py
.venv/bin/python -m pytest -q
RUN_BROWSER_TESTS=1 .venv/bin/python -m pytest -q tests/test_devtools_audit.py tests/test_tier1_ui.py
.venv/bin/python scripts/verify_molab_cold_boot.py --artifact standalone_app.py --runs 5 --output /tmp/marimo-final-local-cold-boot.json
```

The cold-boot script launches local processes. Its results must be labeled local, regardless of its filename; its zero-external-request criterion needs deliberate reconciliation with any chosen remote artifact mode. Measure hosted startup separately.

Browser checks:
1. Start the final standalone in a clean local environment and exercise every act.
2. Check literature table selection, molecule overlays, custom valid/invalid SMILES, salts/stereo examples, model/endpoint selectors, receptor selection, pairs, errors, alpha, empty selections, and CSV content.
3. Check narrow and wide viewports, keyboard operation, clipped outputs, render failures, console errors, and failed requests.
4. Confirm package installation/startup and fallback mode in a clean session.
5. Present the concrete final diff and verification evidence for user approval before publishing or deployment, as required by the control-plane instructions.
6. After authorized publishing, open the exact final molab link from a fresh unauthenticated viewer context; use a fresh/forked compute session if execution requires it.
7. Repeat the primary guided path and download. Confirm public sharing permissions and that the link serves the intended revision.
8. Record fresh hosted evidence: URL, revision/hash where observable, timestamp, browser/session details, control checks, startup timing, and known limitations.

Acceptance: no critical errors on the exact entry link; local and hosted evidence are distinguished; all required interactions work. Do not inherit historical PASS labels.

## Step 8 — Prepare and record the explainer

Estimated effort: 1–2 hours plus user recording/upload time.

Expected files: docs/VIDEO_285_SECOND_SCRIPT.md and docs/JOTFORM_SUBMISSION_PACKAGE.md.

Actions:
1. Rewrite the existing storyboard against the frozen notebook. Correct its stale metrics, artifact size, halo wording, and unimplemented visual actions.
2. Confirm any video duration requirement from the live form; the existing 285-second script is a project target, not independently verified as an official limit.
3. Plan roughly four minutes: question and molecule evidence; scaffold comparison; modest physics result; molecular pair/error case; interactive selection and honest conclusion.
4. Show three or four clear interactions with a readable cursor and text. Spend most of the video on what the viewer learns.
5. Include the custom widget's contribution and brief precomputation/reproduction context. Keep engineering verification brief.
6. Have the user narrate, or choose another agreed recording approach. Ensure the narration matches the actual screen and artifact metrics.
7. Upload the video to Google Drive as requested by the previously inspected form, verify judge access, and check duration/audio/readability.
8. Test the video URL in an unauthenticated browser.

Acceptance: video and notebook describe the same artifact and claims; judges can watch it.

## Step 9 — Complete the submission package and submit

Estimated effort: 30–60 minutes plus buffer.

Actions:
1. Confirm entrant/team identity and contact details directly with the user.
2. Prepare the exact dataset/model title, short description, public molab URL, and accessible video link.
3. Cross-check the latest live form fields and requirements; do not rely only on an older checklist.
4. Perform a final access check after all uploads and link changes.
5. Show the concrete final submission package for approval before externally submitting it.
6. Submit after authorization and record receipt/confirmation and timestamp.
7. Save the submitted version and avoid unverified last-minute changes to the public entry.

Acceptance: confirmed submission receipt, working public links, and a preserved submitted artifact.

## Scheduling and stop rules

Planning estimates are not guaranteed durations. A focused core pass may take approximately 12–20 hours; optional Studio/Pixi/WASM work can add several hours. Narrow scope according to actual time available.

Order of work:
1. Scientific corrections and evaluation provenance.
2. Clear story and functioning reactive explorations.
3. Packaging and fresh local/hosted verification.
4. Video and submission.
5. Optional integrations only when the required path is on schedule.

Stop rules:
- Do not start broad retraining, another endpoint, or a new AI assistant merely to increase feature count.
- Paid Beam work has a user-approved $25 cumulative ceiling and must have a bounded purpose. Cache its artifacts; do not tie default slider interactions to paid jobs. Do not exceed the ceiling without explicit further approval.
- If the 0.25 upgrade fails its compatibility checkpoint, keep a tested working version and defer features that depend on the upgrade.
- If Studio or WASM hits unresolved compatibility problems after its prototype window, retain the working molab notebook and omit the companion from required submission scope.
- Scientific or runnable-link failures outrank presentation additions.
- Freeze code before recording; fixes after recording require checking narration and screenshots again.
- Publishing/deployment, merge, and final form submission remain explicit user approval gates under the user's instructions.

## Suggestions for the entrant

- Choose one result you can explain in your own words and one surprising molecule example. Make both prominent.
- Use a colleague as a first-time reader for ten minutes. Ask what they learned, where they got lost, and what claim they would challenge.
- Record in your own voice if practical; it makes the scientific decisions and custom contribution personal.
- Keep the modest descriptor improvement and visible model errors. Explain why they matter rather than overstating success.
- Treat precomputed Beam results as a reproducibility asset: show how they were produced, when, and what changes would require recomputation.
- Leave time for access permissions and the receipt. A polished extra feature cannot compensate for an inaccessible entry.
