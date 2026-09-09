# IMPLEMENTATION PLAN AUTHORING PROMPT FOR GPT-5.6-LUNA (MAX REASONING)

You are the Lead System Architect and Principal Computational Chemist for the **Bring Cheminformatics to Life — molab Notebook Competition #3 (OpenADMET × marimo)**.

### Context
In your Round 10 Audit (`docs/GPT56_LUNA_AUDIT_ROUND10_FINAL.md`), you officially granted an unconditional **98 / 100 — Submission-Grade Sign-Off**.
In your Strategic Competition Advisory (`docs/LUNA_COMPETITION_STRATEGY_ADVISORY.md`), you outlined a three-tier roadmap to make this submission the undisputed #1 Grand Prize winner:
- **Tier 1:** High-Impact Native Marimo UI Polish (`mo.accordion`, `mo.stat`, `mo.ui.table` bi-directional row selection, `mo.download` CSV export).
- **Tier 2:** Controlled Offline GPU Enzymology on Beam Cloud RTX 4090 (dual-isoform CYP2D6 `3TBG` & `4WNW` docking).
- **Tier 3:** Molab Cloud Staging & < 5-Minute Video Walkthrough Script.

---

## YOUR TASK
Author a comprehensive, production-grade, task-by-task **EXECUTION PLAN & TECHNICAL SPECIFICATION** document at:
`docs/TIER1_TIER2_IMPLEMENTATION_PLAN.md`

The plan must be granular and actionable so the engineering agent can implement it strictly one task card at a time with deliberate engineering rigor.

### Structure Required for Each Execution Card:
Every card must be formatted with:
1. **Card ID & Title** (e.g., `EC-T1-01: Native mo.accordion Refactor...`)
2. **Phase / Tier:** Tier 1, Tier 2, or Tier 3
3. **Objective & Scientific / UX Rationale**
4. **Target Files to Touch or Create**
5. **Exact Code & API Specifications:**
   - For `mo.ui.table`: Show exact syntax for single row selection, defensive handling when selection is empty (`table.value` is empty dict/list), and how state binds to downstream cells.
   - For `mo.stat`: Show exact values, labels, captions, and `direction` flags for Acts 2, 3, 5.
   - For `mo.download`: Show CSV generation schema and dynamic binding to active $\alpha$ slider.
   - For `mo.accordion`: Show key-value dictionary syntax and placement in Acts 1 and 5.
   - For CYP2D6 Docking: Show PDB preparation, grid box parameters, Vina execution on Beam RTX 4090, and JSON artifact schema.
6. **Automated Verification Command:** The exact `pytest` command to verify the card.
7. **Predeclared Acceptance Gate (Done When):** Specific, falsifiable criteria.
8. **Rollback Trigger:** Specific condition under which the change must be reverted.

### Specific Execution Cards to Formalize:
- `EC-T1-01`: Native `mo.accordion` Refactor for In Vitro Assay Protocol (Act 1) & DOME Checklist (Act 5).
- `EC-T1-02`: Native `mo.stat` KPI Metric Callout Cards across Acts 2, 3, and 5.
- `EC-T1-03`: Bi-directional Reactive `mo.ui.table` Row Selection in Act 1 (Table 1.1 $\leftrightarrow$ `BioactivationTracer` + 3D Docking Card).
- `EC-T1-04`: Bi-directional Reactive `mo.ui.table` Row Selection in Act 5 (Table 5.1 $\leftrightarrow$ 2D Candidate Structure Card).
- `EC-T1-05`: One-Click `mo.download` Prioritized Candidate Pool Export in Act 5.
- `EC-T1-06`: Tier 1 Automated Rebundling & Seam Integration Gate (asserting 186+ tests pass, bundle size < 200 KB, 0 warnings).
- `EC-T2-01`: Beam Cloud CYP2D6 Structural Docking Pipeline (`3TBG` & `4WNW` on RTX 4090).
- `EC-T2-02`: Dual-Isoform Enzymology Card & Embedded Assets Integration in Act 3.
- `EC-T2-03`: Tier 2 Rebundling & Automated Docking Seam Gate.
- `EC-T3-01`: Molab Cloud Gist Staging & Cold-Boot SLA Verification (< 10s).
- `EC-T3-02`: Final 285-Second Video Walkthrough Script & JotForm Submission Package.

Deliver the complete, exhaustive plan directly to `docs/TIER1_TIER2_IMPLEMENTATION_PLAN.md`.
