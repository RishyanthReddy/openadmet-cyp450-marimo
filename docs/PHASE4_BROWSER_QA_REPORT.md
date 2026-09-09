# Phase 4 Live Browser Drive & Reliability QA Report

**OpenADMET: Cytochrome P450 Bioactivation & Conformal Risk Control**  
**Audit Date:** September 8, 2026  
**Auditor:** Automated Chrome DevTools MCP & Playwright Testing Framework  
**Verdict:** **ALL ACCEPTANCE GATES SATISFIED (100% PASS)**

---

### 1. Executive Summary

Phase 4 reliability, live browser drive, defensive chemotype fuzzing, and offline zero-network acceptance testing have been successfully completed across all 5 Acts of the OpenADMET platform.

| Quality Gate | Target / Requirement | Observed Result | Verdict |
| :--- | :--- | :--- | :--- |
| **Console Errors** | Strictly 0 unhandled application errors | **0 errors** (over 340+ requests) | **PASS** |
| **Network Failures** | 0 HTTP 4xx / 5xx responses | **0 failures** | **PASS** |
| **SVG Elements** | $\ge 70$ vector graphic elements | **84 SVGs rendered** | **PASS** |
| **AnyWidgets** | $\ge 2$ custom AnyWidget instances | **4 `.bat-container` instances** | **PASS** |
| **Interactive Controls** | Responsive dropdowns, tabs, and sliders | **100% interactive across 5 Acts** | **PASS** |
| **NCBI Verification** | Real-time & cached Entrez E-Utilities | **10/10 PMIDs verified (8/10 DOI links, 2 print-era)** | **PASS** |
| **Defensive Fuzzing** | Zero unhandled tracebacks on bad SMILES | **22/22 fuzzing test cases passed** | **PASS** |
| **Standalone Isolation** | Offline execution in empty directory | **Clean export in `/tmp/empty_dir_test`** | **PASS** |
| **Full Pytest Suite** | 100% passing across all 27 suites | **168 passed in 20.79s (0 failed, 0 skipped)** | **PASS** |
| **Marimo Check** | Code 0 on `app.py` & `standalone_app.py` | **Code 0, 0 stderr** | **PASS** |

---

### 2. Live Interactive Browser Drive across All 5 Acts

Headless Google Chrome (v152+ on macOS) was driven via Playwright against `http://localhost:2718` to test real user interactions and visual fidelity:

1. **Act 1: Mechanism-Based Inactivators & NCBI Entrez Verification**
   - **Interactive Switcher:** Tested dynamic molecule switching across the 10 literature reference MBIs (Raloxifene $\to$ Mibefradil $\to$ Lapatinib $\to$ Clopidogrel).
   - **NCBI Entrez Integration:** Verified that each selected compound displays the official `✓ NCBI Entrez Verified` badge, official peer-reviewed article title, journal, publication date, live clickable PubMed ID links, and DOI links (where available; 8/10 DOI links with 2 print-era records).
   - **Table 1.1:** Verified the curated reference table containing all 10 compounds with NCBI status and target CYP isoforms.
   - **Visual Evidence:** Captured `phase4_act1_raloxifene_ncbi.png`, `phase4_act1_mibefradil_ncbi.png`, `phase4_act1_lapatinib_ncbi.png`, and `phase4_act1_table1_1_ncbi.png`.

2. **Act 2: The Bathtub Audit**
   - Verified the empirical evaluation of the "bathtub curve" hypothesis.
   - Verified out-of-fold performance comparison between baseline 2D ECFP4 LightGBM and Chemprop D-MPNN architectures.
   - Verified interactive Tanimoto shift distribution SVG.
   - **Visual Evidence:** Captured `phase4_act2_bathtub_audit.png`.

3. **Act 3: Physics-Grounded Quantum Reactivity**
   - Verified AIMNet2-NSE $\Delta\text{SCF}$ vertical ionization potentials (IP) and electron affinities (EA) calculated on Beam Cloud NVIDIA RTX 4090.
   - Verified 3D macromolecular docking active-site steric proximity card (`2V0M` and `1TQN`) comparing nearest heavy atom distances against the catalytic heme iron ($Fe$).
   - **Visual Evidence:** Captured `phase4_act3_quantum_docking.png`.

4. **Act 4: Medicinal Chemistry Steering & MMP Activity Cliffs**
   - Verified the Matched Molecular Pair (MMP) interactive activity cliff viewer with side-by-side AnyWidgets displaying bioactivation warhead halos.
   - Verified row-level empirical assay provenance displaying source row IDs and experimental $\Delta pIC_{50}$ shifts.
   - Tested Out-of-Fold (OOF) error case diagnostic tabs.
   - **Visual Evidence:** Captured `phase4_act4_mmp_lead_redesign.png`.

5. **Act 5: TxConformal Candidate Prioritization**
   - Verified the weighted conformal risk control candidate selection table (Jin et al. 2026).
   - Verified dynamic candidate filtering with observed screening FDP diagnostics across $\alpha \in [0.05, 0.20]$.
   - Verified honest limitations disclosure, DOME-aligned reporting checklist, and methodology citations.
   - **Visual Evidence:** Captured `phase4_act5_conformal_selection.png` and `phase4_full_page_overview.png`.

---

### 3. NCBI Entrez E-Utilities Authentication & Integration

- **Authenticated API Credentials:** Integrated authentic NCBI account credentials via environment variables (`NCBI_API_KEY` and `NCBI_EMAIL`), unlocking authenticated 10 requests/second rate limits.
- **Resilient Multi-Tier Architecture:**
  - *Tier 1 (Live Queries):* Direct HTTPS calls to NCBI Entrez `esummary.fcgi` with authenticated rate limits and official account User-Agent headers.
  - *Tier 2 (Disk Cache):* `data/packaged/ncbi_pubmed_cache.json` caching all 10 reference records.
  - *Tier 3 (Embedded Fallback):* Gzip-compressed Base64 payload embedded directly into `models/embedded_assets.py` and `standalone_app.py` for guaranteed offline zero-network execution.
- **Unit & Integration Coverage:** Authored `tests/test_ncbi_client.py` covering cache schema, offline fallback resilience, batch fetching, and catalog enrichment (7/7 tests passed in 0.18s).

---

### 4. Defensive Chemotype Fuzzing (`EC-4-3-01`)

Authored `tests/test_fuzzing.py` and implemented `safe_generate_molecule_layout` and `BioactivationTracer.safe_from_smiles`:
- **Malformed Inputs Tested:** Empty strings, whitespace, syntax errors (`C(((`, `>>><<<`, invalid valence).
- **Challenging Chemotypes Tested:** 32-membered macrocycles, organometallics (cisplatin `[Pt+2](Cl)(Cl)(N)(N)`), inorganic salts (`[Na+].[Cl-]`), stable isotopes (`[13CH4]`), and 120-carbon linear alkyl chains.
- **Outcome:** 22/22 fuzzing tests passed cleanly with 0 uncaught Python tracebacks. When malformed inputs are provided, the widget gracefully renders a styled warning banner: `⚠️ Structure Warning: [error details]`.

---

### 5. Standalone Empty-Directory Acceptance (`EC-4-2-01`)

Tested asset independence by isolating `standalone_app.py` in an empty directory (`/tmp/empty_dir_test`):
- Executed `marimo export html standalone_app.py -o /tmp/empty_dir_test/export.html` with zero external files.
- Result: **Exited code 0 in 1.4s, generating a 942 KB fully functional self-contained HTML artifact**.
- Active provenance badge verified: `Data Source: Embedded Offline Sandbox (100-molecule Fallback Mode)`.
- All 10 literature MBIs, MMP transformations, and benchmark results decode and render in-memory without disk or network access.

---

### 6. Phase 4 Sign-Off Verdict

All criteria for Phase 4 (Reliability, Live Browser Drive & molab QA) have been systematically executed and verified under deliberate engineering rigor. The platform is hardened, scientifically grounded, resilient to network disruption and malformed inputs, and ready for Phase 5 (Cloud Deployment & Final Submission).
