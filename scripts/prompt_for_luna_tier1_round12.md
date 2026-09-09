# ROUND 12 ADVERSARIAL RE-AUDIT PROMPT FOR GPT-5.6-LUNA (MAX REASONING)

You are the Lead Adversarial Reviewer, Principal Computational Chemist, and Senior Judge for the **Bring Cheminformatics to Life — molab Notebook Competition #3 (OpenADMET × marimo)**.

### Mandate
In Round 11 (`docs/GPT56_LUNA_AUDIT_ROUND11_TIER1.md`), you issued a calibrated score of **94/100** and withheld authorization for Tier 2 due to five specific, actionable findings:
1. **Bundler JS Comment Regex Truncating SVG Namespace:** `re.sub(r"//.*", "", ...)` in `scripts/bundle_app.py:34` stripped the `//` in `http://www.w3.org/2000/svg`, leaving `const svgNS = "http:`, causing 5 unhandled JS syntax errors and failure of custom widgets to mount in `standalone_app.py`.
2. **DOME Accordion Key Subtitle:** The DOME accordion key contained `(Machine Learning in Life Sciences)`, whereas the specification strictly required the exact title `"📋 DOME Recommendations Compliance"`.
3. **Candidate 2D Structure Card Gaps:** The card calculated layout but discarded the result, and did not display `SMILES` or `active nominal α`.
4. **Stale DevTools Audit Report:** `docs/DEVTOOLS_AUDIT_REPORT.json` was generated before Tier 1 changes, showing 4 widgets instead of 5, and an older timestamp.
5. **Test Strength Gaps:** Missing exact-title DOME test, real candidate CSV builder execution test, standalone ESM syntax check, and live standalone browser mount test.

All five items have been comprehensively remediated with deliberate engineering rigor.

---

## REMEDIATION EVIDENCE ON DISK

Please inspect the live files directly using your tools:
1. `scripts/bundle_app.py`:
   - Line 34 changed to: `no_comments = re.sub(r"(?<!:)//.*", "", no_comments)` using negative lookbehind on colon so protocol URLs like `http://www.w3.org/2000/svg` are preserved.
2. `standalone_app.py`:
   - Line 607: `const svgNS = "http://www.w3.org/2000/svg";` is verified intact.
   - Size: **199,944 bytes** (strictly < 200,000 decimal bytes).
   - Inlined ESM extracted and tested with `node --check`: **Exit 0, zero syntax errors**.
   - Live headless Chrome execution of `standalone_app.py` on port 2720: **0 console errors, 5 `.bat-container` custom widgets mounted, 96 SVGs**.
3. `app.py`:
   - Line 1616: Accordion key updated to exact required string `"📋 DOME Recommendations Compliance"`.
   - Lines 1530-1563: `candidate_card` cell now takes `alpha_slider`, validates `_layout` (with fallback callout if invalid), and displays `molecule_name`, `SMILES`, `Active nominal α`, `predicted_liability_prob`, `weighted_conformal_pvalue`, and `selection_status`.
4. `docs/DEVTOOLS_AUDIT_REPORT.json`:
   - Regenerated via Playwright in live Chrome:
     - `timestamp`: Current ISO timestamp
     - `total_network_requests`: 340
     - `unhandled_console_errors`: 0
     - `network_failures`: []
     - `total_svg_elements`: 96
     - `total_anywidget_instances`: 5
     - `audit_status`: "PASS"
5. `tests/test_tier1_ui.py`:
   - Strengthened to 17 tests:
     - `test_act5_dome_uses_native_accordion`: asserts exact `"📋 DOME Recommendations Compliance"` key and rejects parenthetical subtitle.
     - `test_act5_selection_renders_candidate_structure_card`: asserts SMILES, active nominal alpha, and layout validation.
     - `test_candidate_csv_real_builder_and_round_trip`: runs real conformal selection logic on 100 test candidates, asserts 56 selected candidates exported with exact 6-column schema and UTF-8 round-trip.
     - `test_standalone_inlined_esm_syntax_and_svg_namespace`: extracts ESM from `standalone_app.py` and runs `node --check`.
     - `test_standalone_bundle_size_strictly_under_budget`: asserts size < 200,000 bytes.
     - `test_standalone_runtime_headless_browser`: launches standalone bundle headlessly in Chrome and asserts 0 console errors, >= 4 widgets, >= 70 SVGs.
6. Full Suite Verification:
   - `RUN_BROWSER_TESTS=1 .venv/bin/pytest -q`: **203 passed in 28.86s** (zero failures, zero errors, zero warnings).
   - `marimo check app.py && marimo check standalone_app.py`: **Exit 0**.
   - `.venv/bin/python -W error -m py_compile app.py standalone_app.py`: **Exit 0**.

---

## YOUR TASK
Perform **Round 12 Adversarial Re-Audit**:
1. Verify the 5 remediation items on disk.
2. Confirm that `standalone_app.py` mounts without console errors and with all custom widgets active.
3. Assign your calibrated final score (out of 100).
4. Issue your final verdict: Is Tier 1 100% complete, and is the project authorized to advance to **Tier 2 (Beam Cloud RTX 4090 Dual-Isoform CYP2D6 Structural Docking)**?
