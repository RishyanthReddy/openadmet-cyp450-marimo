# Local staging report for the submission candidate

This report covers **local headless Chrome**, not a deployed molab session. Dependency installation and hosted startup are separate checks. The historical gist and repository-main URLs refer to an older candidate until publication is approved.

- Standalone file: `standalone_app.py`, **187,396 bytes**; 12,604 bytes below the repository's internal 200,000-byte budget. This budget is not claimed as a competition rule.
- Artifact SHA-256: `9a93ab962af66ed0004b1070cb7a6e730f3a29ddc2ea50c26518bd14e4bff50d`.
- Primary Parquet SHA-256: `6faaf1d741b33223916bfaf85cf8db6c29e332b7aef098916640eac63f19e2f2`.
- marimo: 0.25.0; Python floor: 3.11; adjacent uv script lock included.
- No additional Beam jobs or spend. Saved results are used at runtime.

## Five fresh local starts

| Run | Table/widget readiness, seconds | External notebook requests | Console errors |
|---|---:|---:|---:|
| 1 | 4.712 | 0 | 0 |
| 2 | 3.785 | 0 | 0 |
| 3 | 3.627 | 0 | 0 |
| 4 | 3.651 | 0 | 0 |
| 5 | 3.486 | 0 | 0 |

Median **3.651s**, p95 **4.527s**. The report is bound to the artifact hash above. GPU initialization detection is based on server log messages; the standalone code does not import or run the training/GPU workflows.

## Hosted release still to verify

After approval, publish the candidate branch and use a GitHub revision-specific molab notebook link. In a fresh hosted session, verify all five sections, molecule/table linkage, model and metric controls, custom-input recovery, chart/table candidate selection, alpha, and CSV download. Record the public revision and final URL. Do not label this notebook deployed or submission-ready until that check and the final video/access checks are complete.
