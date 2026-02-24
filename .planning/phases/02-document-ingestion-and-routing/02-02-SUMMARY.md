---
phase: 02-document-ingestion-and-routing
plan: 02
subsystem: routing
tags: [cowork, plugin, categorization, routing, batch-splitting, domain-keywords]

# Dependency graph
requires:
  - phase: 02-01
    provides: Expanded file discovery, _dd_inventory.json schema, Native Document Reading instructions
provides:
  - Domain categorization logic with 9-domain keyword matching (two-pass approach)
  - Batch splitting for domains exceeding 20-file platform limit
  - Routing metadata schema for _dd_inventory.json (domains, batches, uncategorized)
  - Routing checkpoint (_dd_status.json phase="routing")
  - Document Routing Workflow section in SKILL.md with keyword reference table
  - Automatic dispatch flow (no user confirmation)
affects:
  - Phase 3 (domain agents consume routing metadata from _dd_inventory.json)
  - Phase 4 (synthesis agents reference domain assignments)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two-pass categorization: filename heuristics (fast) then content inspection (Read tool, first page only)"
    - "9-domain keyword dictionary: power, connectivity, water-cooling, land-zoning, ownership, environmental, commercials, natural-gas, market-comparables"
    - "Batch splitting: deterministic max-20 per dispatch, files 1-20 batch 1, 21-40 batch 2, etc."
    - "Routing metadata: domains.{name}.{files, count, batches} in _dd_inventory.json"
    - "Uncategorized handling: logged with reason, displayed in chat, NOT routed to agents"
    - "Automatic dispatch: no confirmation prompt, routing flows directly to Phase 3"

key-files:
  created: []
  modified:
    - dc-due-diligence-desktop/commands/due-diligence.md
    - dc-due-diligence-desktop/skills/due-diligence/SKILL.md

key-decisions:
  - "Two-pass categorization: filename heuristics first (no file reading), content inspection only for unmatched files"
  - "Single domain assignment: each file assigned to exactly ONE domain or uncategorized (no duplicates)"
  - "Deterministic batch splitting: sequential file order, max 20 per batch"
  - "Uncategorized files displayed in chat output per user decision"
  - "No user confirmation: categorization and routing happen automatically"
  - "Session checkpoint updated to phase=routing after routing completes"
  - "Routing metadata written to _dd_inventory.json before any agent dispatch (INGEST-05)"

patterns-established:
  - "Domain keyword matching: case-insensitive filename + parent directory check"
  - "Content inspection fallback: Read tool first page (~500 words), vision for scanned PDFs/images"
  - "Batch schema: {batch: N, files: [...]} array per domain in inventory JSON"
  - "Uncategorized schema: [{path, reason}] array in inventory JSON"
  - "Status progression: inventory_complete -> routing_complete in _dd_inventory.json"

requirements-completed: [INGEST-04, INGEST-05]

# Metrics
duration: 3min
completed: 2026-02-24
---

# Phase 2 Plan 02: Domain Categorization and Routing Summary

**Domain categorization with keyword matching, batch splitting, and routing metadata**

## Performance

- **Duration:** 3 min
- **Started:** 2026-02-24
- **Completed:** 2026-02-24
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Added Domain Categorization section to commands/due-diligence.md with two-pass approach: Pass 1 uses filename/path keyword heuristics against 9-domain keyword tables, Pass 2 inspects content of unmatched files via Read tool
- Added Document Routing section with batch splitting logic (BATCH_SIZE=20), inventory JSON update schema for domain assignments and batch metadata, routing checkpoint update, and automatic dispatch flow
- Added Document Routing Workflow section to SKILL.md documenting the 5-step pipeline (categorize, batch, update inventory, checkpoint, dispatch)
- Added Domain Keyword Reference table to SKILL.md with all 9 domains and their primary keywords
- Added Batch Splitting Rules to SKILL.md documenting the 20-file platform limit and deterministic splitting approach
- Added Uncategorized Files handling to SKILL.md documenting exclusion behavior and chat display
- Domain keyword sets are consistent between commands/due-diligence.md and SKILL.md
- Session resilience supports both "inventory" and "routing" checkpoint phases in both files

## Task Commits

Each task was committed atomically:

1. **Task 1: Add domain categorization and batch routing to command file** - `d9a9719` (feat)
2. **Task 2: Update SKILL.md with routing workflow and keyword reference** - `01aa833` (feat)

## Files Created/Modified

- `dc-due-diligence-desktop/commands/due-diligence.md` - Domain Categorization section (two-pass with 9-domain keyword tables), Document Routing section (batch splitting, inventory update, routing checkpoint, automatic dispatch)
- `dc-due-diligence-desktop/skills/due-diligence/SKILL.md` - Document Routing Workflow section, Domain Keyword Reference table, Batch Splitting Rules, Uncategorized Files handling

## Decisions Made

- Two-pass categorization approach conserves context window by using fast filename matching first
- Single domain assignment per file eliminates duplicate processing in Phase 3
- Deterministic batch splitting ensures reproducible routing across session resumes
- No confirmation prompt per user decision — one command does everything
- Uncategorized files logged and displayed but not routed to any agent

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- _dd_inventory.json schema fully defined with domain assignments and batch metadata
- All 9 domain keyword sets documented for Phase 3 agent reference
- Session resilience supports resume at routing checkpoint (skip to Phase 3 dispatch)
- Automatic dispatch flow ready — Phase 3 agents will receive routed document batches
- No blockers

## Self-Check: PASSED

- FOUND: dc-due-diligence-desktop/commands/due-diligence.md (modified)
- FOUND: dc-due-diligence-desktop/skills/due-diligence/SKILL.md (modified)
- FOUND: commit d9a9719 (Task 1)
- FOUND: commit 01aa833 (Task 2)
- VERIFIED: Domain Categorization section present in command file
- VERIFIED: Document Routing section present in command file
- VERIFIED: BATCH_SIZE=20 in command file
- VERIFIED: 9 domain keyword tables in both files
- VERIFIED: Uncategorized handling in both files
- VERIFIED: routing_complete status in command file
- VERIFIED: No user confirmation prompt in routing flow
- VERIFIED: Two-pass approach documented (Pass 1 + Pass 2)

---
*Phase: 02-document-ingestion-and-routing*
*Completed: 2026-02-24*
