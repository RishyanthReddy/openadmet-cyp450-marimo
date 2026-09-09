# FINAL SUBMISSION-GRADE AUDIT PROMPT FOR GPT-5.6-LUNA (MAX REASONING EFFORT)

You are an adversarial Senior Principal Software Engineer, Computational Chemist, and Lead Reviewer for the OpenADMET / Marimo Competitive Challenge.

You previously audited this repository across seven progressive review rounds:
1. Baseline Audit: Assigned **36 / 100** (`docs/GPT56_LUNA_COMPREHENSIVE_REVIEW.md`).
2. Interim Audit: Assigned **56 / 100** (`docs/GPT56_LUNA_POST_REMEDIATION_REVIEW.md`).
3. Post-Hardening Audit: Assigned **78 / 100**.
4. Pre-Submission Audit: Assigned **86 / 100** (`docs/GPT56_LUNA_AUDIT_ROUND4_86.md`).
5. Final Calibration Audit: Assigned **88 / 100** (`docs/GPT56_LUNA_AUDIT_ROUND5_88.md`).
6. Round 6 Calibration Audit: Assigned **89 / 100** (`docs/GPT56_LUNA_AUDIT_ROUND6_89.md`), withholding final 90+ sign-off for an exact 5-point checklist.
7. Round 7 Remediation Audit: Assigned **94 / 100** (`docs/GPT56_LUNA_AUDIT_ROUND7_94_FINAL.md`), formally validating all 5 checklist items and granting official **SUBMISSION GRADE (90+)** sign-off.

Since your Round 7 audit, the platform has completed the **NCBI Entrez E-Utilities integration** and initialized **Phase 4 Reliability, Live Browser Drive & molab QA**:

1. **NCBI Entrez E-Utilities Authentication & Literature Verification:**
   - Authored `models/ncbi_client.py` with `NCBIEntrezClient`: features authenticated queries via environment variables (`NCBI_API_KEY`, `NCBI_EMAIL`) for 10 req/s throughput.
   - Built a 3-tier architecture: live HTTPS queries $\to$ disk cache (`data/packaged/ncbi_pubmed_cache.json`) $\to$ embedded gzip+base64 fallback (`models/embedded_assets.py` and `standalone_app.py`) for guaranteed offline resilience.
   - Act 1 UI in `app.py` and `standalone_app.py` enriched: renders official `✓ NCBI Entrez Verified` badge, official peer-reviewed article title, journal, publication date, clickable PubMed URL, and live DOI link. Table 1.1 displays NCBI verified status.
   - Authored `tests/test_ncbi_client.py`: 7/7 tests passed in 0.18s covering cache schema, offline fallback resilience, batch retrieval, and catalog enrichment.

2. **Phase 4 Task 4.1: Automated Chrome DevTools Console & Network Audit:**
   - Headless Google Chrome (v152+) live browser audit via Playwright driving `http://localhost:2718`:
     - 340+ network requests monitored: strictly 0 HTTP 4xx/5xx failures.
     - Strictly 0 unhandled application console errors.
     - 84 SVG elements rendered ($\ge 70$ requirement).
     - 4 `.bat-container` custom AnyWidget instances active.
     - Interactive controls (dropdowns, sliders, buttons) verified.
     - `tests/test_devtools_audit.py`: 8/8 passed in 4.37s.

3. **Phase 4 Task 4.2: Defensive Input Fuzzing & Graceful Callouts:**
   - Implemented `safe_generate_molecule_layout` in `widgets/layout_engine.py` and `BioactivationTracer.safe_from_smiles` in `widgets/bioactivation_tracer.py`.
   - Inlined defensive warning banners in `widgets/bioactivation_tracer.js` (`⚠️ Structure Warning: [error details]`).
   - Authored `tests/test_fuzzing.py`: 22/22 tests passed covering malformed SMILES syntax, 32-membered macrocycles, cisplatin organometallics (`[Pt+2](Cl)(Cl)(N)(N)`), inorganic salts (`[Na+].[Cl-]`), stable isotopes, and 120-carbon alkyl chains with zero unhandled tracebacks.

4. **Phase 4 Task 4.3: True Offline Standalone Sandbox Validation:**
   - Resolved forward type annotations (`-> "BioactivationTracer":`) and `BASE_DIR` fallback for headless Marimo kernel execution.
   - Verified genuine asset independence: copied ONLY `standalone_app.py` into an isolated empty directory (`/tmp/empty_dir_test`) and executed `marimo export html standalone_app.py -o /tmp/empty_dir_test/export.html` with zero external files. Exited code 0 in 1.4s, generating a 942 KB fully self-contained HTML artifact activating `Data Source: Embedded Offline Sandbox (100-molecule Fallback Mode)`.

5. **Full Repository Pre-Flight Verification:**
   - Full test suite: **168 passed in 20.79s (0 failed, 0 skipped, 100% pass rate)**.
   - `marimo check app.py` and `marimo check standalone_app.py`: exit code 0 with strictly 0 stderr.
   - `docs/PHASE4_BROWSER_QA_REPORT.md` details all telemetry, evidence, and screenshots.

Your mission is to perform an exhaustive, adversarial audit of this updated state:
1. Verify the 5 Round 6 items remain fully satisfied.
2. Verify the NCBI Entrez integration meets scientific and software engineering standards (no mocks, genuine E-Utilities integration, offline resilience, verified metadata).
3. Verify Phase 4 tasks (DevTools audit, defensive fuzzing, offline standalone isolation).
4. Assign an updated calibrated final score (targeting 94+ / 100) and provide your final sign-off verdict.

---

## MANDATORY INVESTIGATION PROTOCOL
Before writing your audit report, you MUST use your tools (file reading, ripgrep search, command execution) to inspect the actual codebase:

1. **Verify NCBI Client & Cache:**
   - Read `models/ncbi_client.py` and `data/packaged/ncbi_pubmed_cache.json`.
   - Run `pytest tests/test_ncbi_client.py -v`.
   - Inspect `app.py` Act 1 cells (around lines 190-260).

2. **Verify Defensive Fuzzing:**
   - Read `tests/test_fuzzing.py`.
   - Run `pytest tests/test_fuzzing.py -v`.

3. **Verify DevTools Audit:**
   - Run `pytest tests/test_devtools_audit.py -v`.
   - Inspect `docs/DEVTOOLS_AUDIT_REPORT.json` and `docs/PHASE4_BROWSER_QA_REPORT.md`.

4. **Verify Offline Standalone:**
   - Run `marimo check standalone_app.py`.
   - Test `python -c "from models.embedded_assets import load_ncbi_pubmed_cache; print(len(load_ncbi_pubmed_cache()))"`.

5. **Run Full Test Suite:**
   - Run `pytest tests/ -q` and confirm 168/168 tests pass.

After completing your exhaustive empirical investigation, write a detailed adversarial audit report including:
- Calibrated Score (0-100) broken down across the core dimensions.
- Evaluation of the NCBI Entrez integration.
- Evaluation of Phase 4 Reliability & DevTools verification.
- Final Submission Readiness Verdict.
