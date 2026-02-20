# Task: Wire client summary into orchestrator as new wave

## What To Do

Add the client summary agent as a new wave in the due diligence orchestrator skill (SKILL.md). It should run after the executive summary is generated (Wave 3), reading from the domain agent outputs and executive summary to produce the client-facing document.

## Why It Matters

The orchestrator manages the entire pipeline sequence. Adding the client summary as Wave 4 ensures it runs at the right time with all the inputs it needs, without disrupting the existing three-wave flow.

## Size

**Estimate:** small

Adding a single Task tool call to the orchestrator skill after the existing Wave 3 section. Follows the established pattern for wave execution.

## Done When

- [ ] Client summary agent is triggered as Wave 4 in the orchestrator
- [ ] Agent receives the correct input paths (domain outputs + executive summary)
- [ ] Output is written to a predictable path in the opportunity folder
- [ ] Existing three-wave pipeline is unchanged

## Needs First

Needs the client summary agent built from the previous task.
