# Step 1: Fix bugs and suppress noise

## What This Delivers

A cleaner, more reliable pipeline -- the vision converter's file handle bug is fixed, Python dependencies are pinned so installs are reproducible, and agents stop flagging the absence of data center design documents (which is expected and not a meaningful finding).

## Tasks

- [x] Task 1: Fix unclosed file handle in vision converter
- [x] Task 2: Pin Python dependency versions
- [ ] Task 3: Suppress design doc commentary in domain agents

## Needs First

Nothing -- this step can start right away.

## Decisions

### Locked
- Suppress design doc commentary in domain agents -- the absence of design documents is expected at this stage of deal evaluation and is not a finding worth flagging
