# OpenADMET Platform: 285-Second Video Walkthrough Script (EC-T3-02)

**Competition:** Bring Cheminformatics to Life — molab Notebook Competition #3 (OpenADMET x marimo)  
**Planned Total Duration:** **285 seconds (4 minutes 45 seconds)**  
**Hard Ceiling:** Strictly <= 300 seconds (5 minutes 00 seconds)  
**Safety Margin:** 15 seconds  

---

## Storyboard & Segment Breakdown

| Timecode | Duration | Segment Name | Visual Actions & Screen Capture Choreography | Spoken Voiceover (Scientific & Honest Calibration) |
|---|---|---|---|---|
| `0:00–0:45` | 45 s | Problem and Bathtub Audit | Open notebook at top title. Scroll to **Act 1 Introduction**, then immediately down to **Act 2: The Bathtub Audit**. Highlight side-by-side metric cards showing Random 5-Fold CV vs Grouped Murcko Scaffold Split. Point mouse to PR-AUC collapse (0.81 down to 0.54) and MCC drop. Highlight the zero-leakage scaffold partition diagram. | "Time-dependent inhibition of Cytochrome P450 can create dangerous drug-drug interaction liabilities. Random splits can hide the problem by placing related scaffolds in both train and test. Our Bathtub Audit compares naive random validation with a grouped Murcko scaffold holdout, making the apparent performance loss visible instead of hiding it." |
| `0:45–2:00` | 75 s | AnyWidget and Metabolic Halos | Navigate up to **Act 1: Table 1.1 (Literature MBI Reference Set)**. Click **Raloxifene** row, then click **Lapatinib**, then **Paroxetine**. Observe the custom `BioactivationTracer` AnyWidget instantly re-rendering 2D SVG molecular coordinates, reactive warhead highlights, and atomic SOM halos. Toggle overlay dropdown from warheads to SOM. Type a malformed SMILES into the test input to demonstrate the defensive safe fallback card. Click the native accordion disclosure to reveal the experimental assay protocol and PubMed DOI metadata. | "Table 1.1 is a reactive entry point into the literature MBI set. Clicking a compound drives the `BioactivationTracer` and the downstream docking view through Marimos reactive DAG. The same app handles malformed SMILES defensively, and the assay protocol remains available in a native disclosure panel." |
| `2:00–2:45` | 45 s | Physics and Enzymology | Scroll down to **Act 3: Physics-Grounded Quantum Reactivity & Structural Docking**. Highlight the delta-SCF descriptor table showing AIMNet2-NSE vs ECFP baseline: lift in PR-AUC (+0.042) and MCC (+0.081), alongside neutral global ROC-AUC and improved Brier calibration score. Pan to the CYP3A4 catalytic iron proximity proxy panel, then smoothly expand the **CYP2D6 Dual-Conformation Structural Panel**. Select the reactive dropdown to toggle between Substrate-Bound (3TBG, 2.10 A) and Unliganded (4WNW, 3.30 A). Highlight Paroxetine active-site proximity to heme iron (4.89 A / 5.03 A) and honest Asp301 non-contact proximity labeling (6.71 A / 6.31 A). | "AIMNet2-NSE Delta-SCF descriptors improve local decision metrics while global ROC-AUC is essentially neutral, so we report both outcomes. Vina poses are interpreted as active-site steric-proximity evidence near heme iron, not as binding free energies. The CYP2D6 panel adds a measured comparison of 3TBG and 4WNW, with Paroxetine and Asp301 treated as a geometric validation case." |
| `2:45–3:30` | 45 s | Medicinal Chemistry Steering | Scroll down to **Act 4: Medicinal Chemistry Steering**. Click an entry in the Matched Molecular Pair (MMP) activity cliff browser. Observe the side-by-side core vs transformation view with bioactivation delta. Scroll down to the **Out-of-Fold Error Inspector**, selecting an unpredicted false negative. Explain the structural features driving the shift. Emphasize that these are empirical label shifts, not substitutes for wet-lab assaying. | "Matched molecular pairs show actionable activity cliffs on conserved cores, and the out-of-fold inspector keeps model failures visible. These records are curated OpenADMET label shifts; they are not presented as a substitute for new wet-lab confirmation." |
| `3:30–4:15` | 45 s | TxConformal Decision Support | Scroll to **Act 5: TxConformal Risk Control**. Grab the reactive alpha slider and adjust it smoothly from 0.05 to 0.15. Watch the Benjamini-Hochberg critical threshold line dynamically shift in the p-value distribution plot and Table 5.1 update candidate counts in real time. Click candidate #1 to display its 2D structure card. Click the **Export CSV** download button to verify the exported file contains the active alpha, cutoff, and calibrated p-values. | "TxConformal applies weighted Benjamini-Hochberg selection to the current alpha. The displayed 2.67 percent FDP at alpha 0.10 is an empirical 250-run diagnostic on the 703-compound holdout. A chemist can inspect a candidate and export the exact selected pool with the active alpha and cutoff in the CSV." |
| `4:15–4:40` | 25 s | Engineering Rigor & Verification | Switch to terminal and verification view. Display the measured `standalone_app.py` byte count (strictly below 200,000 bytes budget with ~2.6 KB safety headroom). Display the automated cold-boot timing report showing all 5 runs completing under 10.0 seconds with zero external network requests and zero GPU requirements. Show pytest passing 213 automated test suites and marimo check exit code 0. | "The delivered notebook is a self-contained offline artifact. The final claim is supported by the measured standalone byte count, cold-boot SLA, browser assertions, and zero-warning checks. No runtime GPU or network is required in Molab." |
| `4:40–4:45` | 5 s | Sign-Off | Full screen slide with the Molab deployment link, public GitHub repository, and competition badge. | "OpenADMET brings cheminformatics to life. Thank you." |

---

## Segment Duration Verification

- Segment 1: 45 seconds
- Segment 2: 75 seconds
- Segment 3: 45 seconds
- Segment 4: 45 seconds
- Segment 5: 45 seconds
- Segment 6: 25 seconds
- Segment 7: 5 seconds
- **Sum of Durations:** $45 + 75 + 45 + 45 + 45 + 25 + 5 = 285$ seconds.
