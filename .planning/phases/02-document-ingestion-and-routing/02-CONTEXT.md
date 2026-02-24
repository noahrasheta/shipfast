# Phase 2: Document Ingestion and Routing - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Orchestrator inventories the full data room, categorizes documents by domain, and routes relevant files to each agent in batches that stay within the 20-file-per-chat platform limit. Document inventory is written to disk before any domain agent is dispatched. Actual domain agent execution is Phase 3 — this phase prepares the routing, not the analysis.

</domain>

<decisions>
## Implementation Decisions

### Inventory presentation
- Chat output shows summary counts only: total files, count per type (PDF, DOCX, XLSX, PPTX, images)
- Detailed inventory file also written to disk — agents can reference it, user can review later
- No confidence indicators on domain assignments — just assign the best-fit domain and move on

### Unrecognized file handling
- Files that don't match any of the 9 domains are logged as "uncategorized" and skipped (not routed to any agent)
- Skipped/uncategorized files are listed in the chat output so the user can see what was excluded
- Text-based files (.csv, .txt, .eml) should be attempted for reading and categorization — don't ignore them just because they aren't the 5 primary types
- Supported primary types: PDF, DOCX, XLSX, PPTX, images (per INGEST requirements), plus text-based files as a best-effort extension

### Batch splitting strategy
- When a domain has more than 20 files, split into multiple batches and run the domain agent multiple times — no data left behind
- No user confirmation step before agent dispatch — inventory → categorize → dispatch automatically (one command does it all)
- If an agent batch fails mid-run, retry once, then skip and continue with remaining domains (synthesis phase handles missing reports gracefully)

### Claude's Discretion
- Inventory file format (JSON vs markdown vs other) — pick what works best for downstream agent consumption
- Domain categorization rules — how files get matched to the 9 domains (keyword matching, content inspection, folder name signals, etc.)
- Whether to use folder/directory names as categorization hints
- Batch progress verbosity in chat (per-batch updates vs domain-level only)

</decisions>

<specifics>
## Specific Ideas

- CLI version dispatches all 9 domain agents in parallel — desktop version should do the same if Cowork supports it (Phase 1 smoke test still pending empirical validation; sequential fallback is the safe baseline)
- The user's mental model is "one command does everything" — no pauses or confirmation prompts during the ingestion/routing phase
- Keep chat output clean and minimal — the detailed routing info lives in the inventory file, not the conversation

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-document-ingestion-and-routing*
*Context gathered: 2026-02-24*
