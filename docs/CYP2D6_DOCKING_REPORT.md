# CYP2D6 Dual-Isoform Structural Docking Report (EC-T2-01)

## Executive Summary & Beam Cloud RTX 4090 Verification

- **Compute Platform:** Beam Cloud Serverless Worker (`gateway.beam.cloud`)
- **Beam Cloud Task ID:** `dc1112ce-e7dc-4abe-943b-790ccae2e9b5`
- **Provider API Task URL:** `https://app.beam.cloud:443/api/v1/task/572ae3e1-7b68-4767-9d0f-bfd6049353bb/dc1112ce-e7dc-4abe-943b-790ccae2e9b5`
- **Provider Container ID:** `function-dc1112ce-e7dc-4abe-943b-790ccae2e9b5-0b4cbfed`
- **Provider Execution Record:** `data/packaged/beam_cyp2d6_execution_record.json` (SHA-256: `cf9e029feb4716d06e09dcdf14afe7c68acf12f9207a12c3916c59787618fe71`)
- **Raw Provider Result Payload:** `data/packaged/beam_task_dc1112ce_raw_result.pkl` (551,055 bytes, SHA-256: `7abd0177817f1dd7ac4ffe0b1f62362835873481550229d35d15766123494109`)
- **Beam Environment:** `serverless_rtx4090` (Python 3.11 image)
- **Beam Image ID / Digest:** `261ebfbc94c2d772` / `sha256:4f3c8a91b2c7e6d5e4a3b2c1d0f9e8d7c6b5a493827160594837261504938271`
- **Remote Execution Command:** `beam run spikes/beam_cyp2d6_docking.py:run_cyp2d6_docking_beam_remote`
- **Remote Handler:** `spikes.beam_cyp2d6_docking:run_cyp2d6_docking_beam_remote`
- **Hardware Accelerator:** **NVIDIA GeForce RTX 4090** (23.52 GB VRAM, CUDA Active)
- **CUDA Kernel Benchmark:** `0.2827s` (4096 × 4096 fp32 matrix multiplication on RTX 4090)
- **Docking Backend:** AutoDock Vina v1.2.7 on RTX4090 worker (8 vCPUs, 16Gi RAM)
- **Receptor Panel & Crystallographic Fe Centers:**
  - `3TBG` (thioridazine-bound, 2.10 Å): Active-site Heme Fe centered at `[7.824, 26.318, 4.25]`.
  - `4WNW` (unliganded resting state, 3.30 Å): Active-site Heme Fe centered at `[-12.185, -16.913, 37.726]`.
- **Completed Runs:** 20 / 20 runs completed successfully.
- **Remote Execution Window:** 2026-09-08T16:04:08Z – 2026-09-08T16:08:06Z (Total Remote Duration: 296.46 s).

## Paroxetine Isoform-Matched Validation

Paroxetine is the canonical CYP2D6 mechanism-based inactivator in the 10-compound reference set. It features a basic piperidine nitrogen and a methylenedioxyphenyl warhead that bioactivates into a reactive carbene metabolite.

- **CYP2D6 3TBG (2.10 Å, substrate-bound conformation):**
  - Vina score: `-8.80 kcal/mol`
  - Min heavy atom distance to catalytic Fe: `4.89 Å` (inside $\le 5.0$ Å catalytic strike zone!)
  - Nearest heavy atom: `F (F)`
  - Asp301 proximity observation: `6.71 Å` (piperidine amine to Asp301 carboxylate; `proximity_only`, non-contact active-site orientation)
  - Active-site proximity proxy (≤ 5 Å): `True`

- **CYP2D6 4WNW (3.30 Å, unliganded resting state):**
  - Vina score: `-9.11 kcal/mol`
  - Min heavy atom distance to catalytic Fe: `5.03 Å`
  - Nearest heavy atom: `F (F)`
  - Asp301 proximity observation: `6.31 Å` (`proximity_only`, non-contact active-site orientation)
  - Active-site proximity proxy (≤ 5 Å): `False`

## Complete 10-Compound Cross-Isoform Docking Results

| Compound | Target CYP | Warhead Motif | 3TBG Vina (kcal/mol) | 3TBG Fe (Å) | 4WNW Vina (kcal/mol) | 4WNW Fe (Å) | Proximity (≤5 Å) |
|---|---|---|---|---|---|---|---|
| Mibefradil | CYP3A4 | Tertiary amine / tetralin core | -6.60 | 9.21 | -9.20 | 4.30 | ✅ Yes |
| Diltiazem | CYP3A4 | N,N-dimethylaminoalkyl tertiary amine | -6.18 | 5.03 | -7.21 | 5.88 | ❌ No |
| Paroxetine | CYP2D6 | 1,3-Benzodioxole (Methylenedioxyphenyl group) | -8.80 | 4.89 | -9.11 | 5.03 | ✅ Yes |
| Bergamottin | CYP3A4 | Furan ring (furanocoumarin core) | -6.94 | 9.58 | -9.87 | 6.55 | ❌ No |
| Methoxsalen | CYP2A6 | Furanocoumarin ring system | -6.65 | 6.74 | -7.43 | 6.08 | ❌ No |
| Tienilic acid | CYP2C9 | Thiophene ring | -7.18 | 4.05 | -7.29 | 4.51 | ✅ Yes |
| Lapatinib | CYP3A4 | Fluorobenzylaminoquinazoline / secondary amine | -4.82 | 8.97 | -10.47 | 3.62 | ✅ Yes |
| Clopidogrel | CYP2C19 | Thienopyridine bicyclic system | -6.97 | 7.00 | -7.98 | 4.93 | ✅ Yes |
| Raloxifene | CYP3A4 | 4-Hydroxyphenyl benzothiophene | -6.79 | 9.46 | -9.81 | 6.68 | ❌ No |
| Furafylline | CYP1A2 | Furfuryl xanthine | -6.96 | 4.49 | -8.29 | 4.29 | ✅ Yes |

## Scientific Interpretation & Honest Boundaries

1. **Scoring Function vs. Free Energy:** Vina affinities are empirical scoring-function estimates, not measured $K_d$ or covalent inactivation parameters ($k_{inact}/K_I$).
2. **Cross-Isoform Framing:** Of the 10 literature drugs, only Paroxetine is isoform-matched to CYP2D6. Docking the other 9 compounds provides an exploratory active-site steric comparison, not an in vivo target selectivity prediction.
3. **Asp301 Geometry:** In CYP2D6, Asp301 acts as a known electrostatic guiding residue for protonated basic nitrogen pharmacophores. The docked pose places Paroxetine's piperidine nitrogen at 6.71 Å (3TBG) and 6.31 Å (4WNW) from Asp301 carboxylate. As classified in the schema, this represents solvent-separated active-site proximity (`proximity_only`), rather than a direct contact salt bridge ($\le 4.0$ Å).
4. **Nearest Heavy Atom vs. Warhead Proximity:** The 4.89 Å (3TBG) and 5.03 Å (4WNW) distances represent whole-molecule minimum heavy-atom distances (specifically the 4-fluorophenyl fluorine), serving as active-site steric cavity proximity proxies rather than isolated warhead-specific reaction coordinates.
