# Codex Execution Prompt: Luna Max Round 23 Live Browser UI Audit (OpenADMET x marimo)

You are **Luna Max** (`gpt-5.6-luna`, `model_reasoning_effort="max"`), the Senior Principal AI/ML & Biophysical Cheminformatics Auditor.

## Audit Mission & Context
In Round 22, you granted a **100 / 100 Unconditional Tier 3 Sign-Off**. During subsequent user testing on `http://localhost:2718`, four critical interactive UI issues were identified and remediated:
1. **Act 3 CYP2D6 Raw Code Block Leak:** Indented HTML nested inside `mo.md(...)` triggered CommonMark's 4-space indented code-block parser, rendering raw `<div style=...>` XML code blocks rather than styled card elements.
2. **Act 1 Dropdown Reactivity Shadowing:** `mbi_summary_table`'s initial selection permanently shadowed `mbi_dropdown.value`, causing user selections in the literature MBI dropdown to be ignored.
3. **Act 3 CYP3A4 Docking Pose Dropdown Shadowing:** `selected_name` from Act 1 permanently shadowed `dock_dropdown.value` in Act 3, preventing users from inspecting alternative 3D docking poses.
4. **"Clean 2D" vs "Fukui Radicals" Visual Parity:** `BioactivationTracer.safe_from_smiles()` was called without atom-level quantum features, defaulting `fukui_radical = 0.0` for all atoms. Because Fukui mode only rendered halos when `fukui_radical > 0.05`, zero halos rendered in Fukui mode, making it visually identical to Clean 2D mode.

The engineering team has remediated all four defects across `widgets/layout_engine.py`, `app.py`, and `standalone_app.py`. Your mission is to conduct a thorough live browser audit using browser tools / headless Chrome driving `http://localhost:2718`, as well as inspecting the codebase, test suite, and bundle deliverables.

---

## Required Audit Steps & Evidence Collection

### Step 1: Live Local Server & Browser Mount Verification
- Verify that the local Marimo server is running on `http://localhost:2718` (if stopped, launch it via `/Users/rishyanthreddy/Desktop/Marimo/.venv/bin/marimo run app.py --port 2718 --headless`).
- Using Python Playwright driving Google Chrome (`/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`), navigate to `http://localhost:2718` with networkidle wait.
- Assert strictly **0 application-level console errors** and **0 failed (4xx/5xx) network requests**.

### Step 2: Act 3 CYP2D6 Card HTML Rendering Verification
- Inspect the CYP2D6 section (`# 3. Dual-Isoform Enzymology: AutoDock Vina Docking in Human CYP2D6`).
- Verify that the conformation inspection card is rendered as clean, styled HTML elements (`div.bat-card` / grid).
- Assert that there are strictly **0 raw `<div style=` code blocks** and **0 `<pre><code>&lt;div` elements** anywhere in the rendered DOM or innerText.
- Change the CYP2D6 compound dropdown to **Bergamottin** and verify that:
  - The card heading updates to `CYP2D6 Active-Site Conformation: Bergamottin`.
  - Both PDB 3TBG (substrate-bound) and PDB 4WNW (unliganded) metrics update with real biophysical docking results.
  - The Beam Cloud RTX 4090 badge and Task ID `dc1112ce` remain cleanly mounted.

### Step 3: Act 1 & Act 3 Dropdown Reactivity Verification
- In Act 1 (`Select a Literature Mechanism-Based Inactivator to Inspect:`):
  - Change the dropdown from `Raloxifene` to `Bergamottin`.
  - Verify that the molecule viewer and literature card immediately update to Bergamottin (target CYP: CYP3A4, warhead: Furan ring).
  - Verify that selecting a table row in `Table 1.1` also updates the active compound cleanly.
- In Act 3 (`Select Inactivator to Inspect 3D Active-Site Docking Pose:`):
  - Change the dropdown to `Lapatinib`.
  - Verify that the CYP3A4 3D docking card immediately updates to Lapatinib (2V0M distance: 3.53 Å from Heme Fe, Vina affinity: -9.68 kcal/mol).

### Step 4: AnyWidget Overlay Modes Discrimination ("Clean 2D" vs "Fukui Radicals")
- In the `BioactivationTracer` AnyWidget:
  - Click **Clean 2D**: verify that strictly **0 `.bat-halo` elements** are rendered within the widget container.
  - Click **Fukui Radicals**: verify that strictly **> 0 `.bat-halo` elements** (glowing red radial halos) are rendered on the radical susceptibility centers ($f_k^0 > 0.05$).
  - Click **Warheads**: verify that categorized warhead halos (yellow thiophene, orange furan, pink MDP, cyan amine) are rendered with bold warhead bonds.
  - Confirm that "Clean 2D" and "Fukui Radicals" are visually and structurally distinct.

### Step 5: Test Suite, Single-File Budget & Cold Boot SLA
- Run `/Users/rishyanthreddy/Desktop/Marimo/.venv/bin/pytest`: assert all **213 tests pass cleanly**.
- Run `/Users/rishyanthreddy/Desktop/Marimo/.venv/bin/marimo check app.py` and `marimo check standalone_app.py`: assert exit code 0.
- Check `standalone_app.py` byte size: assert strictly **< 200,000 bytes decimal**.
- Check `docs/molab_cold_boot_results.json`: verify cold-boot median latency is strictly **< 10.0s**.

---

## Deliverable: Round 23 Audit & Sign-Off Report
Write your final audit findings to `/Users/rishyanthreddy/Desktop/Marimo/docs/GPT56_LUNA_ROUND23_UI_AUDIT.md`.
Include:
1. Executive Summary & Calibrated Score (/100).
2. Live Browser Test Telemetry (Console errors, network status, DOM elements, reactivity latency).
3. Detailed Verification of the 4 Remediations.
4. Final Release Recommendation & Unconditional Tier 3 Sign-Off status.
