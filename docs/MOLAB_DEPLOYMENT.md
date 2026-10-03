# Molab deployment — October 3, 2026

- Live app: https://molab.marimo.io/notebooks/nb_cwmWFFrjMKyWzjSj7iuriG/app
- Saved notebook: https://molab.marimo.io/notebooks/nb_cwmWFFrjMKyWzjSj7iuriG
- Title: When can we trust a CYP prediction?
- Source repository: https://github.com/RishyanthReddy/openadmet-cyp450-marimo
- Source commit: `718eee2e0a48d19e961d63fa4ea87d507ad00536`
- Branch: `codex/submission-readiness` (not merged into main).
- Standalone SHA-256: `92fcfff16fa893e30abc7dfed49bedfc940729ea48f35f7e0fef8aaf8dbded65`.

Deployment was explicitly authorized by the entrant. The source was opened on molab and saved as a named notebook in their workspace; the app URL comes from its Share menu.

## Checks on the original deployment (before the narrative revision)

All five sections, molecular widgets, tables and plots rendered. The reveal switch updated its explanation. Choosing LR updated the random/scaffold scores to 0.4097/0.3738. Choosing Paroxetine updated the docking display (3.02 Å). Alpha 0.20 selected 76 of 100; alpha 0.05 selected 41 of 100. Selecting OCNT-0022129 updated the candidate structure and details.

The hosted notebook uses its labelled embedded portable sample of 100 molecules. It needs no Beam credentials or runtime GPU computation. No additional Beam jobs or spending occurred.

Before publication, the local suite passed **237 tests, zero skips**, including browser tests. Local responsive checks covered 1440, 1024, 768 and 390 pixel widths; desktop screenshots were also inspected at 1920 pixels. Local startup timings are recorded in MOLAB_STAGING_REPORT.md.

## Remaining checks and submission work

- Hosted CSV download was clicked, but the browser download-event capture timed out; successful file download is not verified. Local CSV checks passed.
- Anonymous access has not been independently checked in a signed-out browser.
- Hosted chart-point selection and invalid custom-input recovery were not repeated; these passed locally.
- Record/upload the final narrated video, confirm entrant details and access to both links, then obtain approval for final competition submission.

## Revised release verification

Final source: `718eee2e0a48d19e961d63fa4ea87d507ad00536`. The final app link above supersedes the earlier saved copies; those copies were preserved. The opening Raloxifene example, collapsed secondary panels, corrected explanations and closing findings were verified in the hosted app. Alpha 0.05 updated the current selection to 41/100 and cutoff 0.0205.

CSV content and filename are now prepared on each alpha change instead of through a click-time callback. The hosted link has a concrete CSV file URL and filename; the browser tool still did not capture its download, so successful hosted file delivery remains unverified. The local browser downloaded and checked exact CSV rows and values successfully.

An unauthenticated HTTP request to the final app returned 200 with its notebook title; this verifies the public page, not the anonymous interactive runtime. The entrant has been asked to check incognito runtime access and download.

Final full suite: **237 passed, zero skips, exit 0 in 44.80s**. A preceding run completed all tests but crashed at interpreter shutdown; the repeat completed cleanly. Five local cold starts for the final artifact: median 3.111s, p95 3.727s, zero external notebook requests and console errors. No paid compute was used.

## Entrant confirmation — October 3, 2026

After receiving instructions to open the final app in a private/incognito window and locate the export button, the entrant confirmed: “yes can access and doenload”. Public interactive access and hosted CSV delivery are therefore verified by the entrant. The earlier download-event limitation describes the automation tool, not an outstanding release check. Final narrated video and competition submission remain outstanding.
