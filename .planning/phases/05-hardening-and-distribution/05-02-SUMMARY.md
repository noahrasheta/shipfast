---
phase: 05-hardening-and-distribution
plan: 02
subsystem: docs
tags: [due-diligence, readme, documentation, cowork, non-technical]

# Dependency graph
requires:
  - phase: 05-hardening-and-distribution
    plan: 01
    provides: Hardened orchestrator with pre-dispatch size warning and Wave-1 failure validation
provides:
  - Plain-language install and usage guide for non-technical users (dc-due-diligence-desktop/README.md)
  - Self-contained troubleshooting covering 6 real-world failure scenarios
  - Output description telling users what to expect when analysis completes
affects:
  - dc-due-diligence-desktop distribution packaging

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Plain-language README pattern: describe UI by action and location, not exact button labels (survives UI changes)"
    - "Jargon-free troubleshooting: each scenario is titled as the user's symptom, not the technical cause"

key-files:
  created:
    - dc-due-diligence-desktop/README.md
  modified: []

key-decisions:
  - "Install steps use UI description language ('look for an add/upload option') not exact button labels — Cowork UI changes during preview period"
  - "Troubleshooting uses symptom-first titles ('The analysis stopped partway through') matching how users would search/describe problems"
  - "Noted 'text files' as fallback output wording rather than 'markdown' — non-technical readers don't know what markdown is"

patterns-established:
  - "Symptom-first troubleshooting headers: title each entry as the user's experience, not the technical root cause"
  - "No-jargon output description: describe Word documents (.docx) and 'text files' — never 'markdown'"

requirements-completed:
  - INFRA-04

# Metrics
duration: 2min
completed: 2026-02-24
---

# Phase 5 Plan 02: Non-Technical README Summary

**114-line plain-language install and usage guide for Cowork users covering install (5 steps), usage (4 steps), all output deliverables, and 6 troubleshooting scenarios — zero terminal commands, git references, or developer jargon**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-24T20:38:58Z
- **Completed:** 2026-02-24T20:40:42Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Created `dc-due-diligence-desktop/README.md` with 6 sections: what the plugin does, prerequisites, install steps, usage steps, output description, troubleshooting
- Install section uses 5 numbered steps with concrete UI actions and no terminal commands
- Usage section uses 4 numbered steps explaining what happens during a run (20-40 min estimate, progress updates, synthesis phase)
- Output section describes all 7 deliverables in plain language (Executive Summary, Client Summary, Risk Assessment, 9 domain reports, Word/text file variants)
- Troubleshooting covers 6 real scenarios matching actual failure modes hardened in Plan 05-01 (retry, missing areas, missing command, no Word docs, long runtime, wrong score)
- Added a Tips section for best results as additional UX value

## Task Commits

Each task was committed atomically:

1. **Task 1: Write non-technical README for plugin installation and usage** - `af3e194` (feat)

**Plan metadata:** (docs commit — see final commit below)

## Files Created/Modified
- `dc-due-diligence-desktop/README.md` - Plain-language install and usage guide covering all 6 required sections, 114 lines, zero developer jargon

## Decisions Made
- Install steps use descriptive UI language ("look for an add/upload option") instead of exact button label quotes — Cowork's interface labels change during preview period, so descriptions age better than quoted labels
- Troubleshooting entries are titled with the user's symptom ("The analysis stopped partway through") rather than the technical cause — this matches how non-technical users describe and search for help
- Markdown output referred to as "text files" throughout — "markdown" is developer vocabulary that non-technical users don't recognize
- Word output referred to as ".docx files" (the file extension users see in Finder) rather than "Word documents" exclusively — recognizing the extension helps users locate the output

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

The plan's automated verification command `grep -ciE '(terminal|bash|CLI|git clone|api key|token|context window|environment variable)'` returned 4 instead of 0 — a false positive caused by "click" containing the substring "cli" (case-insensitive). Word-boundary grep confirmed zero standalone occurrences of any jargon term. The README is clean.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 5 is now complete. Both plans (05-01: orchestrator hardening, 05-02: non-technical README) are done.
- The plugin is hardened, documented, and ready for distribution.
- The only remaining step before distribution is packaging the ZIP file for upload, which is outside the scope of this planning project.

---
*Phase: 05-hardening-and-distribution*
*Completed: 2026-02-24*
