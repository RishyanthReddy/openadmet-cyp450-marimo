# Codex Execution Prompt: Luna Max Round 18 Final Sign-Off (OpenADMET x marimo)

You are **Luna Max** (`gpt-5.6-luna`, `model_reasoning_effort="max"`), the Senior Principal AI/ML & Biophysical Cheminformatics Auditor.

In Round 17, you calibrated the platform at **94 / 100** (Gate 2 UI Integration: 30/30, Gate 3 Bundling: 29/30). You requested:
1. **Binding the local results to the provider payload digest (`7abd0177...`):** Providing the raw provider result payload and demonstrating cryptographic equivalence to the packaged JSON.
2. **Eliminating silent static fallbacks in the packaging script:** Enforcing strict presence of the provider execution record without fallback defaults.
3. **Clean execution of tests without filesystem write errors:** Eliminating temporary file writes in tests.

---

## Remediations Executed for Round 18

### 1. Raw Provider Result Payload Saved and Cryptographically Bound
- Downloaded and saved the raw unpickled result payload returned by the Beam Cloud API task `dc1112ce-e7dc-4abe-943b-790ccae2e9b5` to:
  `data/packaged/beam_task_dc1112ce_raw_result.pkl` (551,055 bytes).
- Byte-level SHA-256: `7abd0177817f1dd7ac4ffe0b1f62362835873481550229d35d15766123494109`.
- This matches the `result_payload_sha256` recorded in `data/packaged/beam_cyp2d6_execution_record.json` and `data/packaged/cyp2d6_docking_results.json`.
- Implemented automated verification test in `tests/test_cyp2d6_docking.py` (`test_beam_provider_payload_cryptographic_binding`):
  - Loads `beam_task_dc1112ce_raw_result.pkl`
  - Asserts SHA-256 == `7abd0177817f1dd7ac4ffe0b1f62362835873481550229d35d15766123494109`
  - Unpickles payload via `cloudpickle.loads` and confirms NVIDIA GeForce RTX 4090 telemetry
  - Cryptographically verifies all 20 docking evaluations (Vina score, Fe distance, nearest heavy atom, and pose SHA-256) in `cyp2d6_docking_results.json` match the raw Beam provider output identically.

### 2. Zero Silent Fallbacks in Packaging Script
- `spikes/beam_cyp2d6_docking.py` now strictly requires `data/packaged/beam_cyp2d6_execution_record.json` to exist and asserts `task_id == "dc1112ce-e7dc-4abe-943b-790ccae2e9b5"` and `status == "COMPLETE"`.
- All execution fields (`task_id`, `provider_api_task_url`, `container_id`, `image_id`, `image_digest`, `handler`, `started_at_utc`, `ended_at_utc`, `result_payload_sha256`) are accessed directly from `exec_record` without defaults.

### 3. Disk-Write Free ESM Validation
- Refactored `tests/test_tier1_ui.py` so that `node --input-type=module --check` validates inlined ESM via stdin directly, completely eliminating `NamedTemporaryFile` and disk writes.

### 4. Full Suite & Artifact Specifications
- `standalone_app.py`: **196,415 bytes** decimal (strictly $< 200,000$ bytes budget, **3,585 bytes safety headroom**).
- SHA-256: `9f808c6157a7a87e7cb80e5d044f32ff7381319ba39d5abd27aaf5267eb58fe1`.
- Pytest suite: **210 passed, 9 skipped** (the 9 skipped are live Playwright Chrome tests, which also pass when run with `RUN_BROWSER_TESTS=1`).

---

## Verification Instructions for Luna Max
1. Inspect `data/packaged/beam_task_dc1112ce_raw_result.pkl`, `data/packaged/beam_cyp2d6_execution_record.json`, `data/packaged/cyp2d6_docking_results.json`, and `tests/test_cyp2d6_docking.py`.
2. Run `.venv/bin/pytest tests/test_cyp2d6_docking.py tests/test_cyp2d6_ui.py tests/test_molab_staging.py tests/test_submission_package.py tests/test_tier1_ui.py` (or run full suite with `PYTHONPYCACHEPREFIX=/tmp/pycache .venv/bin/pytest -o cache_dir=/tmp/pytest_cache`).
3. Verify `standalone_app.py` byte size (196,415 < 200,000 bytes) and run `marimo check standalone_app.py`.
4. Render your final **Round 18 Audit & Sign-Off Report** across the three gates:
   - **Gate 1: EC-T2-01 Docking Integrity & Biophysical Grounding (/40)**
   - **Gate 2: EC-T2-02 Reactive UI Integration & Scientific Calibration (/30)**
   - **Gate 3: EC-T2-03 Offline Standalone Bundling & Architecture Seams (/30)**
   Confirm whether **Unconditional Tier 3 Sign-Off** is granted.