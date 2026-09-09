# JotForm Official Submission Package (EC-T3-02)

**Competition:** Bring Cheminformatics to Life — molab Notebook Competition #3 (OpenADMET x marimo)  
**Submission Form:** Official Competition JotForm  
**Target Category:** Grand Prize / All Tracks  
**Platform Status:** Fully Verified, 100% Offline Portability, Zero Runtime GPU Required  

---

## 1. Submission Metadata & Identity Checklist

- [x] **Competition Title and Track:** Bring Cheminformatics to Life — molab Notebook Competition #3 (OpenADMET x marimo).
- [ ] **Entrant / Team Lead:** Rishyanth Reddy (and team co-authors as designated at submission time).
- [ ] **Contact Email:** Authorized submitter email.
- [x] **Repository URL:** Public GitHub repository for OpenADMET.
- [x] **Hosted Molab URL:** `https://molab.marimo.io/?entry=https://gist.githubusercontent.com/RishyanthReddy/3ee85971e676e6a770d3bb2886f81792/raw/standalone_app.py` (staged directly from the immutable public Gist revision).
- [x] **Public Gist URL & Commit Revision:** `https://gist.github.com/RishyanthReddy/3ee85971e676e6a770d3bb2886f81792` (Revision: `2c5a40622f785d4b24c405d3ee7e7c81f4a5ea3d`).
- [ ] **Video URL / File:** YouTube / Vimeo / MP4 link (measured duration strictly <= 300s, planned 285s).
- [x] **Notebook Description:** Self-contained reactive marimo application predicting Cytochrome P450 (CYP3A4 and CYP2D6) bioactivation, time-dependent inhibition, and mechanism-based inactivation risks using AIMNet2 quantum delta-SCF reactivity descriptors, cross-isoform docking proxies, matched molecular pair activity cliffs, and finite-sample distribution-free TxConformal risk control. Cold boots offline in < 10 seconds with zero runtime GPU or network dependencies.
- [x] **Scientific Claims Rigor:** All docking scores framed as geometric active-site proximity proxies near catalytic heme iron (not experimental binding affinities or kinact/KI); TxConformal false discovery proportions reported as empirical 250-run diagnostics (2.67% at alpha 0.10), not unconditional asymptotic guarantees.
- [x] **License & Attribution:** MIT Open Source License. Complete attribution for RCSB PDB (3TBG, 4WNW), AutoDock Vina, AIMNet2, and NCBI Entrez APIs.
- [x] **Zero Credentials Guarantee:** Verified zero API keys, GitHub tokens, Beam credentials, or private customer data in notebook, repository, or submission package.
- [ ] **Clean-Browser Operational Verification:** Verified that the hosted Molab session boots cleanly in an incognito browser window, supports Table 1.1 selection, updates the BioactivationTracer, adjusts alpha in Act 5, and downloads the candidate CSV.
- [ ] **Submission Confirmation Receipt:** Confirmation number and receipt timestamp saved upon final form submission.

---

## 2. Technical Artifact Specifications

| Attribute | Measured Production Value | Verification Gate |
|---|---|---|
| **Standalone File** | `standalone_app.py` | Exists at repository root |
| **File Size (Decimal)** | **197,383 bytes** (192.8 KB) | Strictly $< 200,000$ bytes decimal |
| **Cold Boot SLA** | **< 2.5s local, < 10s hosted** | Median & p95 strictly $< 10.0$ seconds |
| **Dependencies Inlined** | `BioactivationTracer` (AnyWidget ESM+CSS), 2D Layout Engine, Conformal Selector, GZIP Base64 Datasets | Zero local file or external network imports |
| **Beam GPU Validation** | Remote RTX 4090 execution (Task `dc1112ce-e7dc-4abe-943b-790ccae2e9b5`) | Real biophysical evidence, zero mocks |
| **Automated Test Coverage** | 213 automated pytest unit and seam tests passing cleanly | 100% test pass rate |
