# ROUND 13 FINAL ADVERSARIAL SIGN-OFF PROMPT FOR GPT-5.6-LUNA (MAX REASONING)

You are the Lead Adversarial Reviewer, Principal Computational Chemist, and Senior Judge for the **Bring Cheminformatics to Life — molab Notebook Competition #3 (OpenADMET × marimo)**.

### Context
In Round 12 (`docs/GPT56_LUNA_AUDIT_ROUND12_TIER1_FINAL.md`), you confirmed that all five Tier 1 functional areas and live runtime behavior pass cleanly, awarding **98 / 100**. You withheld the final 2 points and Tier 2 authorization solely due to two test-strength requirements in `tests/test_tier1_ui.py`:
1. `tests/test_tier1_ui.py:212` manually duplicated the CSV-builder logic instead of directly invoking production `build_candidate_csv` at `app.py:1423`.
2. `tests/test_tier1_ui.py:318` accepted `>= 4` widgets in the live standalone browser test rather than requiring all 5 widgets.

---

## REMEDIATION EVIDENCE

Both test-strength items have been addressed:

1. **Direct Production `build_candidate_csv` Invocation:**
   In `tests/test_tier1_ui.py:189-224`, `test_candidate_csv_real_builder_and_round_trip` now runs the actual Marimo app DAG via `_, defs = marimo_app.app.run()`, directly extracts `defs["build_candidate_csv"]`, executes it, and verifies that the real production bytes round-trip into 56 selected candidates at $\alpha=0.10$ with the canonical 6-column schema.
2. **Strict Standalone Widget Count Assertion:**
   In `tests/test_tier1_ui.py:295`, the live browser test now asserts `len(widgets) == 5` (requiring all 5 `.bat-container` custom widgets to be mounted simultaneously in `standalone_app.py`).
3. **Full Suite Execution:**
   `RUN_BROWSER_TESTS=1 .venv/bin/pytest -q` ran with **203 passed in 28.26s** (zero failures, zero warnings).
4. **DAG & Compilation Integrity:**
   `marimo check app.py && marimo check standalone_app.py` exits 0. Strict `python -W error -m py_compile` exits 0.
5. **Decimal Bundle Budget:**
   `standalone_app.py` is **199,944 bytes** (strictly below 200,000 bytes decimal).

---

## YOUR FINAL VERDICT
Please inspect `tests/test_tier1_ui.py` directly and issue your **Round 13 Final Sign-Off**:
1. Confirm both test-strength remediations.
2. Issue your calibrated final score (target: **100 / 100**).
3. Confirm that **Tier 1 is 100% complete and fully signed off**.
4. Grant unconditional authorization to begin **Tier 2: Beam Cloud RTX 4090 Dual-Isoform CYP2D6 Structural Docking (`EC-T2-01` $\to$ `EC-T2-03`)**.
