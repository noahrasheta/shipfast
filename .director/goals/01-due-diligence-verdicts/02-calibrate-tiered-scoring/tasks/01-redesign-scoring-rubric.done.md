# Task: Redesign scoring rubric with tiered qualitative weights

## What To Do

Redesign the scoring rubric template to reflect three tiers of domain importance. Tier 1 (Power, Land/Zoning, Connectivity) carries the most weight and poor results here can sink a deal alone. Tier 2 (Environmental, Commercials, Ownership) matters but won't independently kill a deal. Tier 3 (Water/Cooling, Natural Gas, Market Comparables) provides context but doesn't drive pass/fail. The rubric should guide qualitative reasoning, not impose numerical multipliers.

## Why It Matters

The current scoring treats all domains equally, which means mediocre scores across the board produce a "pass" verdict even when critical factors like power availability are weak. Tiered weighting ensures the verdict reflects what actually matters for a data center investment.

## Size

**Estimate:** medium

Requires rethinking the scoring template structure, writing clear tier definitions, and crafting evaluation guidance that produces nuanced verdicts (not just pass/fail). Needs careful wording to guide agent reasoning.

## Done When

- [x] Scoring rubric template reflects Tier 1/2/3 domain groupings
- [x] Rubric includes guidance for how Tier 1 failures affect the overall verdict
- [x] Rubric uses qualitative reasoning language, not numerical formulas
- [x] Power is explicitly identified as the most critical individual domain

## Needs First

Needs the bugs and noise cleaned up from Step 1.

## Completed

**Date:** 2026-02-20

**What changed:**
- Rewrote `dc-due-diligence/templates/scoring-rubric.md` with full Domain Tiers section defining Tier 1 (Critical), Tier 2 (Important), Tier 3 (Context), and Risk Assessment as a synthesis layer
- Power explicitly identified as the single most important domain with special callout for how Low Power scores affect verdicts
- Verdict logic rewritten to use tier-based qualitative reasoning instead of counting Low scores against thresholds
- Tier 3 scores explicitly cannot trigger a Pass verdict on their own
- Updated `dc-due-diligence/agents/executive-summary-agent.md` to reflect new tier classifications, tier names, and verdict reasoning in the At a Glance table and Phase 5 verdict determination
