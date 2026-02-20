# Task: Add gap and question extraction to domain agent prompts

## What To Do

Update each domain agent's prompt to explicitly identify gaps in the available data and formulate specific questions that Data Canopy should ask before making a final decision. Each agent should output a "Key Questions" section alongside its regular analysis, listing 2-5 questions specific to its domain.

## Why It Matters

Domain agents are closest to the source material and best positioned to notice what's missing. Having them surface questions directly -- rather than just noting gaps in prose -- creates structured input for the executive summary's Key Questions section.

## Size

**Estimate:** medium

Requires updating all 9 domain agent prompts with question extraction instructions and output format. The changes per agent are small, but there are 9 agents to update consistently.

## Done When

- [ ] All 9 domain agents include a Key Questions section in their output
- [ ] Questions are specific and actionable (not vague like "more information needed")
- [ ] Questions reflect the tier importance of their domain
- [ ] Output format is consistent across all agents for easy aggregation

## Needs First

Needs the tiered scoring calibrated from Step 2, so questions reflect weighted importance.
