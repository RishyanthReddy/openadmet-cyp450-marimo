# Round 17 Audit & Sign-Off Report

Verdict: **94 / 100**  
Unconditional Tier 3 sign-off: **Not granted**

| Gate | Score | Assessment |
|---|---:|---|
| EC-T2-01 Docking Integrity & Biophysical Grounding | **35/40** | 20-run artifact, raw-pose geometry, hashes, Fe distances, and Paroxetine/Asp301 framing validate. Provider linkage remains incomplete. |
| EC-T2-02 Reactive UI Integration & Scientific Calibration | **30/30** | Targeted UI and docking tests pass; both apps consume the corrected Paroxetine narrative and dynamic CYP2D6 metadata. |
| EC-T2-03 Offline Standalone Bundling & Architecture Seams | **29/30** | `standalone_app.py` is 196,415 bytes, below budget, with matching SHA-256 and canonically identical embedded docking JSON. Clean full-suite verification remains unavailable. |

Evidence reviewed: [execution record](</Users/rishyanthreddy/Desktop/Marimo/data/packaged/beam_cyp2d6_execution_record.json:2>), [packaged results](</Users/rishyanthreddy/Desktop/Marimo/data/packaged/cyp2d6_docking_results.json:24>), [Beam script](</Users/rishyanthreddy/Desktop/Marimo/spikes/beam_cyp2d6_docking.py:380>), [tests](</Users/rishyanthreddy/Desktop/Marimo/tests/test_cyp2d6_docking.py:45>), and [scientific report](</Users/rishyanthreddy/Desktop/Marimo/docs/CYP2D6_DOCKING_REPORT.md:5>).

The provider record is internally consistent: its SHA-256 matches packaged metadata, and task ID, URL, container, image digest, handler, status, timestamps, and result digest agree. However:

- The provider record contains no explicit command or output-payload field.
- `remote_command` remains locally hard-coded in the packaging script.
- The script retains silent static fallbacks if the record is absent.
- The local results file hashes to `59e2846d…`, not the provider payload digest `7abd0177…`; no raw provider payload is present to establish that binding.
- `verified_by_provider_api: true` is a local assertion that could not be independently re-fetched here.

Verification results:

- Exact requested pytest command: **could not start** because the enforced read-only environment has no writable temporary directory.
- Read-only-safe variant: **202 passed, 9 skipped, 5 failed, 2 errors**; failures were temp-file, bytecode, or temporary-JavaScript write errors.
- Targeted non-writing checks: **20 passed**.
- `marimo check standalone_app.py`: exit code 0, but emitted an unhandled temporary-directory exception.
- Standalone size: **196,415 bytes**, SHA-256 matches documentation.
- Documentation is materially synchronized; [video script line 19](</Users/rishyanthreddy/Desktop/Marimo/docs/VIDEO_285_SECOND_SCRIPT.md:19>) uses approximate “~4 KB” headroom and retains the 209-test claim, while exact size appears in the submission/staging reports.

Conclusion: the Round 17 remediations materially improve the evidence, but the provider-to-command/output binding and clean verification requirements are not independently closed. No files were modified.