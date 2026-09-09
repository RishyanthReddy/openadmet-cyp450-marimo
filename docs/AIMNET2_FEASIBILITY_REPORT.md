# AIMNET2-NSE ΔSCF FEASIBILITY REPORT (GATE 1)
> **Generated at:** 2026-09-03 04:17:39 UTC
> **Task:** `EC-0-2-01` (Phase 0 Feasibility Spike, Gate 1)
> **Gate 1 Verdict:** **PASS (GO)**

---

## 1. Executive Summary & Gate 1 Criteria

| Gate 1 Metric | Acceptance Threshold | Observed Value | Status |
| :--- | :--- | :--- | :---: |
| **Steady-State Inference Latency** | $< 0.50\text{s}$ / molecule | **0.0240s (24 ms / mol)** [P95: **0.0523s**] | **PASS** |
| **Numerical Stability** | 0 NaN or Inf values | **0 NaNs (100% stable across all 50 molecules)** | **PASS** |
| **Vertical IP Sanity** | Drug-like range ($5.0 - 12.0\text{ eV}$) | **6.43 - 9.36 eV** (mean: 7.75 eV) | **PASS** |
| **GPU Hardware** | Modern Cloud Accelerator | **NVIDIA GeForce RTX 4090** (VRAM: 20.5 MB) | **PASS** |

> [!NOTE]
> **Warmup vs Steady-State Latency on RTX 4090:**
> The very first molecule incurred a one-time 31.4s PyTorch CUDA JIT kernel compilation and cuBLAS/Warp graph initialization.
> Immediately following that single warmup call, all subsequent molecules ran at **0.024s (24 milliseconds)** median latency and **0.052s** P95 latency, beating the 0.50s Gate 1 SLA by a factor of 20x.

---

## 2. Benchmark Summary Statistics

- **GPU Hardware:** **NVIDIA GeForce RTX 4090** (Beam Cloud Serverless Worker)
- **Molecules Tested:** 50 (25 confirmed CYP3A4 TDI liabilities, 25 non-TDI compounds)
- **Model Weights:** `isayevlab/aimnet2-nse` (Hugging Face / PyTorch via modern `warp-lang`)
- **Calculated Quantities:** $\Delta\text{SCF}$ vertical ionization ($IP_v = E(N-1) - E(N)$) and attachment ($EA_v = E(N) - E(N+1)$)
- **Atomic Responses:** Partial charge deltas $\Delta q_i^+ = q_i(+1) - q_i(0)$ for radical cation
- **Model Download & Load Time:** 9.691s
- **One-Time CUDA JIT Warmup (Molecule 1):** 31.438s
- **Steady-State Median Latency (Molecules 2-50):** **0.0240s / molecule (24 ms)**
- **P95 Latency:** **0.0523s / molecule (52 ms)**
- **Peak VRAM Allocated:** 20.5 MB (remarkably lightweight; $< 0.1\%$ of the RTX 4090's 24 GB VRAM)

---

## 3. Sample Predictions (First 5 Molecules)

| Molecule ID | SMILES | True TDI | $E(N)$ [eV] | $IP_v$ [eV] | $EA_v$ [eV] | Max $\Delta q_i^+$ | Latency [s] |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `OCNT-2312083` | `CN1C=C(CN2C=C(C3=CC=CC4=C...` | True | -25403.8308 | **8.097** | -1.0285 | +0.054 | 31.4385s |
| `OCNT-0475270` | `CCC1=C(S(=O)(=O)N2CCN(C3C...` | False | -43783.2635 | **7.8914** | -0.375 | +0.069 | 0.8824s |
| `OCNT-0456896` | `CCOC1=C(OCC)C=C(C(=O)N/C(...` | False | -42721.9167 | **6.5921** | -0.1735 | +0.045 | 0.0331s |
| `OCNT-2395442` | `O=C(CN1C=NN=N1)N1CCOC(C2=...` | False | -27985.7943 | **9.3612** | -0.7098 | +0.069 | 0.0232s |
| `OCNT-2317688` | `COC1=CC(C)=CC=C1NC(=O)C1=...` | True | -27962.0712 | **8.1885** | 0.0417 | +0.066 | 0.0251s |

---

## 4. Architectural Impact on Phase 1 & 2

> [!TIP]
> **Gate 1 Passed:** With inference running at $< 0.1\text{s}$ per molecule on GPU, full extraction of vertical $IP_v$, $EA_v$, and atomic charge responses across all 6,145 compounds in Phase 1 (`EC-1-3-01`) will require **less than 15 minutes of GPU compute**, well within our single Beam Cloud account budget.

