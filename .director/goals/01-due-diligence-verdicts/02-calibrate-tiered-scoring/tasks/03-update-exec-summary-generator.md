# Task: Update executive summary generator to reflect tiered scoring

## What To Do

Update the executive summary generator agent to present findings organized by tier importance. The summary should lead with Tier 1 findings, clearly indicate which tier each domain belongs to, and ensure the overall verdict section reflects the tiered weighting from the risk assessment.

## Why It Matters

The executive summary is what Data Canopy reads to make decisions. If the summary doesn't reflect the tiered importance of each domain, the internal team has to mentally reweight the findings themselves -- which defeats the purpose of automated analysis.

## Size

**Estimate:** medium

Requires updating the agent prompt and the executive summary template to organize findings by tier and ensure the verdict section references tier-based reasoning.

## Done When

- [ ] Executive summary organizes domain findings by tier (Tier 1 first, then Tier 2, then Tier 3)
- [ ] Overall verdict section references which tier drove the recommendation
- [ ] Summary template updated to accommodate tier groupings
- [ ] Pursue / Proceed with Caution / Pass verdict reflects tiered weighting

## Needs First

Needs the risk assessment agent updated with tier-based reasoning.
