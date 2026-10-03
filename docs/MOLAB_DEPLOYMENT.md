# Molab deployment — October 3, 2026

- Live app: https://molab.marimo.io/notebooks/nb_fhAT4HqfpJRRthfvvYWsmo/app
- Saved notebook: https://molab.marimo.io/notebooks/nb_fhAT4HqfpJRRthfvvYWsmo
- Title: When can we trust a CYP prediction?
- Source repository: https://github.com/RishyanthReddy/openadmet-cyp450-marimo
- Source commit: `2036788de21c8ab5b44611277c74d02deda4e562`
- Branch: `codex/submission-readiness` (not merged into main).
- Standalone SHA-256: `9a93ab962af66ed0004b1070cb7a6e730f3a29ddc2ea50c26518bd14e4bff50d`.

Deployment was explicitly authorized by the entrant. The source was opened on molab and saved as a named notebook in their workspace; the app URL comes from its Share menu.

## Verified in the hosted app

All five sections, molecular widgets, tables and plots rendered. The reveal switch updated its explanation. Choosing LR updated the random/scaffold scores to 0.4097/0.3738. Choosing Paroxetine updated the docking display (3.02 Å). Alpha 0.20 selected 76 of 100; alpha 0.05 selected 41 of 100. Selecting OCNT-0022129 updated the candidate structure and details.

The hosted notebook uses its labelled embedded portable sample of 100 molecules. It needs no Beam credentials or runtime GPU computation. No additional Beam jobs or spending occurred.

Before publication, the local suite passed **237 tests, zero skips**, including browser tests. Local responsive checks covered 1440, 1024, 768 and 390 pixel widths; desktop screenshots were also inspected at 1920 pixels. Local startup timings are recorded in MOLAB_STAGING_REPORT.md.

## Remaining checks and submission work

- Hosted CSV download was clicked, but the browser download-event capture timed out; successful file download is not verified. Local CSV checks passed.
- Anonymous access has not been independently checked in a signed-out browser.
- Hosted chart-point selection and invalid custom-input recovery were not repeated; these passed locally.
- Record/upload the final narrated video, confirm entrant details and access to both links, then obtain approval for final competition submission.
