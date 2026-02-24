---
phase: 05-hardening-and-distribution
plan: 01
subsystem: orchestration
tags: [due-diligence, orchestrator, ux, error-handling, cowork]

# Dependency graph
requires:
  - phase: 04-synthesis-and-document-output
    provides: Full orchestrator with synthesis dispatch, DOCX generation, and completion UX
provides:
  - Pre-dispatch data room size warning (30+ files threshold with 20-40 min estimate)
  - Enhanced post-Wave-1 validation with per-domain status reporting and FAILED_DOMAINS tracking
  - Explicit failure messaging with retry instructions (/due-diligence re-run skips completed agents)
  - Updated SKILL.md with hardening capabilities and no Phase 5 placeholder stub
affects:
  - dc-due-diligence-desktop orchestrator
  - SKILL.md capability documentation

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "FAILED_DOMAINS accumulator pattern for tracking per-domain completion status in bash"
    - "Pre-dispatch jq query against _dd_inventory.json for data room size assessment"

key-files:
  created: []
  modified:
    - dc-due-diligence-desktop/commands/due-diligence.md
    - dc-due-diligence-desktop/skills/due-diligence/SKILL.md

key-decisions:
  - "30-file threshold for pre-dispatch warning — matches existing batch ceiling (20 files/domain), leaves reasonable headroom"
  - "Synthesis proceeds regardless of failed domains — SYNTH-05 pattern (synthesis agents handle missing reports)"
  - "Retry messaging tells user to re-run /due-diligence — completed reports are kept, only failed agents re-dispatch"

patterns-established:
  - "FAILED_DOMAINS accumulator: empty string appended to as domains fail, tested with [ -n ] for failure branch"
  - "Warning: prefix on failure message — consistent with plan must_haves artifact contains check"

requirements-completed:
  - INFRA-04

# Metrics
duration: 2min
completed: 2026-02-24
---

# Phase 5 Plan 01: Orchestrator Hardening Summary

**Pre-dispatch size warning (30+ files triggers 20-40 min estimate) and enhanced Wave-1 completion validation that names failed domains and instructs retry via /due-diligence re-run**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-24T20:35:16Z
- **Completed:** 2026-02-24T20:37:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Added Pre-Dispatch Data Room Assessment section to orchestrator — warns users when data room exceeds 30 files, shows estimated 20-40 minute completion time, notes batched domains
- Replaced simple Domain Agent Results completion block with enhanced version that tracks FAILED_DOMAINS, names affected agents, explains scoring impact, and tells user how to retry
- Removed "Future Capabilities (Phase 5)" placeholder stub from SKILL.md
- Added "Hardening (Phase 5)" section to SKILL.md Current Capabilities listing all four hardening features

## Task Commits

Each task was committed atomically:

1. **Task 1: Add pre-dispatch size warning and enhanced Wave-1 validation to orchestrator** - `66fc80d` (feat)
2. **Task 2: Update SKILL.md with hardening capabilities, remove Phase 5 stub** - `a8f5350` (feat)

**Plan metadata:** (docs commit — see final commit below)

## Files Created/Modified
- `dc-due-diligence-desktop/commands/due-diligence.md` - Added Pre-Dispatch Data Room Assessment section (before Parallel Agent Dispatch) and replaced simple completion block with FAILED_DOMAINS-aware enhanced version
- `dc-due-diligence-desktop/skills/due-diligence/SKILL.md` - Added Hardening (Phase 5) section under Current Capabilities; removed Future Capabilities (Phase 5) placeholder

## Decisions Made
- 30-file threshold for pre-dispatch warning aligns with the 20-file-per-domain batch ceiling — a data room that size will definitely have batched domains and longer run times
- Synthesis proceeds regardless of failed domains, per SYNTH-05 — synthesis agents handle missing reports gracefully, so blocking synthesis on failure would be worse UX than proceeding with partial data
- Retry is achieved by re-running /due-diligence — the resume check (> 500 bytes) already skips completed agents, making retry transparent to the user

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 5 Plan 01 complete. Plan 02 (non-technical README and clean-machine install validation) is ready to execute.
- Both hardening features are in the orchestrator and documented in SKILL.md.

---
*Phase: 05-hardening-and-distribution*
*Completed: 2026-02-24*
