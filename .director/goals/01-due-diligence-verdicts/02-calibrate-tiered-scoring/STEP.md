# Step 2: Calibrate scoring with tiered weighting

## What This Delivers

A scoring system that produces nuanced verdicts instead of defaulting to "pass." Tier 1 domains (Power, Land/Zoning, Connectivity) carry the most weight and can sink a deal on their own. Tier 2 (Environmental, Commercials, Ownership) matters but won't independently kill a deal. Tier 3 (Water/Cooling, Natural Gas, Market Comparables) provides context but doesn't drive pass/fail.

## Tasks

- [x] Task 1: Redesign scoring rubric with tiered qualitative weights
- [ ] Task 2: Update risk assessment agent for tier-based reasoning
- [ ] Task 3: Update executive summary generator to reflect tiered scoring

## Needs First

Needs the bugs and noise cleaned up from Step 1.

## Decisions

### Locked
- Use qualitative reasoning for tier weighting, not numerical multipliers -- there are no exact weights; agents use logic about what matters most
- Tier 1 (Power, Land/Zoning, Connectivity) can sink a deal on its own
- Power is the single most important domain

### Deferred
- Exact numerical scoring weights -- use reasoning-based evaluation instead
