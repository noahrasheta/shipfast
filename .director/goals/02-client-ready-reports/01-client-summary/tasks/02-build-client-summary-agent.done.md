# Task: Build client summary agent

## What To Do

Create a new agent that reads the domain agent outputs and the executive summary, then synthesizes a client-facing summary document. The agent should distill findings into clear, non-technical language, highlight the most important factors (Tier 1), include the recommendation, and list the key questions -- all framed for someone outside Data Canopy.

## Why It Matters

The client summary agent bridges the gap between Data Canopy's detailed internal analysis and what deal presenters need to see. It's a distinct skill from the executive summary generator because the audience, tone, and level of detail are fundamentally different.

## Size

**Estimate:** medium

New agent file with YAML frontmatter, following the existing agent pattern. The prompt needs careful crafting to produce the right tone and level of detail for an external audience.

## Done When

- [ ] Agent file created in dc-due-diligence/agents/ with proper frontmatter
- [ ] Agent reads domain outputs and executive summary as inputs
- [ ] Output follows the client summary template
- [ ] Language is professional and accessible to non-technical readers
- [ ] Internal scoring details and tier numbers are not exposed

## Needs First

Needs the client summary template from the previous task.
