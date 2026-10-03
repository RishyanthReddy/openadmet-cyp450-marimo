# Local staging report for the submission candidate

This report covers **local headless Chrome**, not a deployed molab session. Dependency installation and hosted startup are separate checks. The historical gist and repository-main URLs refer to an older candidate until publication is approved.

- Standalone file: `standalone_app.py`, **188,575 bytes**; 11,425 bytes below the repository's internal 200,000-byte budget. This budget is not claimed as a competition rule.
- Artifact SHA-256: `92fcfff16fa893e30abc7dfed49bedfc940729ea48f35f7e0fef8aaf8dbded65`.
- Primary Parquet SHA-256: `6faaf1d741b33223916bfaf85cf8db6c29e332b7aef098916640eac63f19e2f2`.
- marimo: 0.25.0; Python floor: 3.11; adjacent uv script lock included.
- No additional Beam jobs or spend. Saved results are used at runtime.

## Five fresh local starts

| Run | Table/widget readiness, seconds | External notebook requests | Console errors |
|---|---:|---:|---:|
| 1 | 3.018 | 0 | 0 |
| 2 | 3.081 | 0 | 0 |
| 3 | 3.878 | 0 | 0 |
| 4 | 3.125 | 0 | 0 |
| 5 | 3.111 | 0 | 0 |

Median **3.111s**, p95 **3.727s**. The report is bound to the artifact hash above. GPU initialization detection is based on server log messages; the standalone code does not import or run the training/GPU workflows.

## Hosted deployment

The candidate has since been published. See [MOLAB_DEPLOYMENT.md](MOLAB_DEPLOYMENT.md) for the saved app URL, hosted checks, and remaining verification limits.
