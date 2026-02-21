# Task: Build Key Questions aggregation into executive summary generator

## What To Do

Update the executive summary generator to collect Key Questions from all domain agent outputs, deduplicate and prioritize them by tier, and present them as a dedicated section in the executive summary. Tier 1 questions should appear first and be flagged as critical.

## Why It Matters

This is the deliverable Data Canopy asked for -- a clear list of what they need answered before committing to an opportunity. Without aggregation, the questions are scattered across 9 separate domain reports and easy to miss.

## Size

**Estimate:** medium

The executive summary generator already reads all domain agent outputs. This adds a new extraction and synthesis step for the Key Questions, plus a template section for displaying them.

## Done When

- [ ] Executive summary includes a Key Questions section after the verdict
- [ ] Questions are organized by tier priority (Tier 1 first)
- [ ] Duplicate or overlapping questions from different agents are merged
- [ ] Each question indicates which domain raised it
- [ ] Executive summary template updated with the Key Questions section

## Needs First

Needs domain agents surfacing Key Questions from the previous task.
