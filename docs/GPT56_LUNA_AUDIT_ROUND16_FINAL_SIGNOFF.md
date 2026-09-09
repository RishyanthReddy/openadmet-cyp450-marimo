## Round 16 verdict

**Calibrated score: 94 / 100**

**Unconditional Tier 3 sign-off: Not granted.**

| Gate | Score | Assessment |
|---|---:|---|
| EC-T2-01 Docking Integrity | **35/40** | 20/20 runs, raw pose hashes, coordinates, Fe distances, nearest-atom labels, and Asp301 distances independently reproduce. Residual provenance remains unresolved. |
| EC-T2-02 UI Integration | **30/30** | Act 3 is mounted and reactive in both apps; selectors consume `.value`; all 10 warheads are populated; fluorine/whole-molecule proximity wording is now honest. |
| EC-T2-03 Bundling & Seams | **29/30** | Bundle is exactly 196,007 bytes; embedded docking JSON is canonically identical to the packaged artifact. Targeted tests pass. Full-suite clean verification remains blocked by the read-only environment. |

### Residual 1: provenance — not remediated to unconditional standard

The fields exist in the artifact and report ([artifact](</Users/rishyanthreddy/Desktop/Marimo/data/packaged/cyp2d6_docking_results.json:24>), [report](</Users/rishyanthreddy/Desktop/Marimo/docs/CYP2D6_DOCKING_REPORT.md:3>)), but they are still hard-coded literals in the packaging script ([beam script](</Users/rishyanthreddy/Desktop/Marimo/spikes/beam_cyp2d6_docking.py:399>)).

The Beam return object contains telemetry/results but no provider-issued task record or resolved image digest ([beam script](</Users/rishyanthreddy/Desktop/Marimo/spikes/beam_cyp2d6_docking.py:280>). The `remote_command` is an invocation string, not an execution record. Therefore the digest and task ID are present but not independently linked to a Beam-issued run.

### Residual 2: nearest atom vs. warhead — verified fixed

Independent parsing confirms Paroxetine’s nearest atom is `F (F)` at **4.89 Å** in 3TBG and **5.03 Å** in 4WNW. The report explicitly defines these as whole-molecule fluorine proximity proxies ([boundary #4](</Users/rishyanthreddy/Desktop/Marimo/docs/CYP2D6_DOCKING_REPORT.md:52>)), and the UI uses the corrected narrative ([app.py](</Users/rishyanthreddy/Desktop/Marimo/app.py:1196), [standalone_app.py](</Users/rishyanthreddy/Desktop/Marimo/standalone_app.py:2027>)).

Verification performed:

- Relevant Tier 2/staging/package tests: **15 passed**.
- Independent raw-pose validation: **20/20 scores, distances, labels, and hashes matched**.
- Bundle size: **196,007 < 200,000 bytes**.
- Embedded payload: canonical JSON equality confirmed.
- Full local suite: **202 passed, 9 skipped, 5 failures, 2 errors**, with all observed failures/errors caused by unavailable writable temp/bytecode locations; the claimed clean **209 passed** result could not be independently reproduced here.
- Minor documentation inconsistency: the video voiceover still says **195,780 bytes** while the current artifact is 196,007 bytes ([video script](</Users/rishyanthreddy/Desktop/Marimo/docs/VIDEO_285_SECOND_SCRIPT.md:19>)).

Tier 3 should remain gated until a provider-issued Beam execution record binds the task ID, image digest, command, and artifact output.