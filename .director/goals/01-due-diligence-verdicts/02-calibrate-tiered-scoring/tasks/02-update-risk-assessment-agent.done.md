# Task: Update risk assessment agent for tier-based reasoning

## What To Do

Update the risk assessment agent's prompt to evaluate findings through the lens of tiered domain importance. The agent should weigh Tier 1 findings heavily, use Tier 2 findings to adjust confidence, and treat Tier 3 findings as contextual information. Its output should explain why the verdict is what it is, referencing the tier that drove the decision.

## Why It Matters

The risk assessment agent synthesizes all domain findings into the overall verdict. Without tier awareness, it treats a weak water supply the same as weak power infrastructure, producing misleading assessments.

## Size

**Estimate:** medium

The agent prompt needs significant rewriting to incorporate tier-based reasoning patterns. Needs to reference the redesigned rubric and produce output that clearly traces the verdict back to the most important domains.

## Done When

- [ ] Risk assessment agent prompt references the tiered domain framework
- [ ] Agent output explains which tier drove the verdict
- [ ] A weak Tier 1 finding produces a cautious or negative verdict regardless of other scores
- [ ] Agent reasoning is transparent -- the output shows why each domain was weighted as it was

## Needs First

Needs the redesigned scoring rubric from the previous task.
