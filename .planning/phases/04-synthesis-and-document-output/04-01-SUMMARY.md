# Plan 04-01 Summary

## What was done

Ported Risk Assessment and Executive Summary agents from CLI (`dc-due-diligence/agents/`) to Cowork desktop plugin (`dc-due-diligence-desktop/agents/`).

### Task 1: Risk Assessment Agent
- Created `dc-due-diligence-desktop/agents/risk-assessment-agent.md`
- Replaced all `${OPPORTUNITY_FOLDER}` references with `${WORKSPACE_FOLDER}` (15 occurrences)
- Removed `${PLUGIN_DIR}/templates/agent-output-template.md` reference -- output format is embedded in the agent file
- Added "Your Task" section matching Cowork pattern (workspace folder, research reports path, output path)
- Replaced `_converted/manifest.json` reference with `_dd_inventory.json` for source document count
- No Document Safety Protocol added (reads agent reports, not broker documents)
- Preserved complete: Tiered Domain Framework, Analysis Workflow (Phases 1-4), Cross-Domain Risk Categories (7 categories), Common Risk Patterns (8 patterns), Output Format template, Confidence Score Calculation, Traffic Light Rules, Key Reminders

### Task 2: Executive Summary Agent
- Created `dc-due-diligence-desktop/agents/executive-summary-agent.md`
- Replaced all `${OPPORTUNITY_FOLDER}` references with `${WORKSPACE_FOLDER}` (16 occurrences)
- Removed `${PLUGIN_DIR}/templates/scoring-rubric.md` reference -- embedded scoring rubric directly
- Embedded complete scoring rubric (~34KB): Domain Tiers, Category Scoring Criteria (all 10 categories), Overall Verdict Logic, Edge Cases and Judgment Calls (7 tiebreaker principles), Quick Reference Table, Verdict Quick Reference
- Added "Your Task" section referencing embedded Scoring Rubric section
- Replaced `_converted/manifest.json` reference with `_dd_inventory.json`
- No Document Safety Protocol (reads agent reports, not broker documents)
- Preserved complete: Workflow (Phases 1-6), Terminology Normalization map, Conflict Detection and Resolution, Key Questions Aggregation (Phase 3.5), Category Scoring (Phase 4), Verdict Determination (Phase 5), Strategic Framing (Phase 5.5), Output Format, Writing Style, Key Reminders

## Verification

- risk-assessment-agent.md: 0 OPPORTUNITY_FOLDER, 0 PLUGIN_DIR, 15 WORKSPACE_FOLDER, 0 _converted
- executive-summary-agent.md: 0 OPPORTUNITY_FOLDER, 0 PLUGIN_DIR, 16 WORKSPACE_FOLDER, 4 Scoring Rubric refs, 64 Tier 1 refs, 0 _converted

## Requirements satisfied

- SYNTH-01: Risk Assessment agent reads all domain reports and produces cross-domain risk file
- SYNTH-02: Executive Summary agent produces scored report with Pursue/Proceed/Pass verdict
- SYNTH-03: Executive Summary uses same normalized scoring rubric as CLI version (embedded)
- SYNTH-05: Both agents handle missing domain reports gracefully
