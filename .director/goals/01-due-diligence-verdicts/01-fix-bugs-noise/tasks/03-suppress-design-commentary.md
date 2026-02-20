# Task: Suppress design doc commentary in domain agents

## What To Do

Update the domain agent prompts to stop flagging the absence of data center design documents as a finding. Currently agents note this as a gap or risk, but it's expected -- opportunities at this stage don't include design documents, and flagging their absence adds noise without value.

## Why It Matters

Every domain agent flagging "no design documents provided" inflates the risk assessment and contributes to the overly-strict scoring that makes every deal get "pass." Removing this noise is a prerequisite for meaningful scoring calibration.

## Size

**Estimate:** small

Review each domain agent's prompt and remove or update the sections that reference design document expectations. Straightforward text changes across multiple agent files.

## Done When

- [ ] No domain agent flags missing design documents as a finding or risk
- [ ] Agents still flag genuinely missing information relevant to their domain
- [ ] Agent output is cleaner without design document commentary

## Needs First

Nothing -- this can start right away.
