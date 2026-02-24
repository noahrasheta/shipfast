# Phase 3: Domain Analysis Agents - Context

**Gathered:** 2026-02-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Port all 9 domain agents (Power, Connectivity, Water/Cooling, Land/Zoning, Ownership, Environmental, Commercials, Natural Gas, Market Comparables) to Cowork. Each agent reads its assigned documents from the routing inventory, conducts live web research to verify claims, writes a structured report to disk, and flags any embedded prompt injection attempts. Synthesis agents and output formatting belong to Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Report output
- Reports written to `research/` subfolder inside the workspace (e.g., `research/power-report.md`)
- Same long-form markdown structure as CLI version: Claim Extraction, Web Verification, Risk Assessment, Scoring sections
- Overwrite on re-run — one clean report per domain, no versioning
- Each report includes a "Documents Analyzed" section listing the exact files the agent processed — traceability for users and downstream synthesis agents

### Web research scope
- Full claim-by-claim verification — same depth as CLI version (this is the core value proposition)
- Built-in WebSearch/WebFetch only — no MCP search tool dependencies (Exa, Firecrawl, Brave)
- Same research intensity across all 9 agents — consistent two-phase methodology (extract claims from documents, then verify each via web)
- Unverifiable claims flagged as "Unverified — no public data found" in the report — honest and transparent, not escalated as a risk factor

### Claude's Discretion
- Agent dispatch order (which of the 9 runs first/last)
- Progress feedback to user during sequential run
- Resume/skip logic when interrupted mid-run (check for existing report files)
- Prompt injection detection implementation details
- Adaptation of CLI agent templates to Cowork's native file reading (no `_converted/` path)

</decisions>

<specifics>
## Specific Ideas

- CLI agent templates in `dc-due-diligence/agents/` are the reference implementation — port the research methodology and report structure, adapt the file access pattern for Cowork's native reading
- The two-phase research approach (Phase 1: Claim Extraction from documents, Phase 2: Web Verification) should be preserved exactly as designed in the CLI agents
- Document Safety Protocol from CLI agents should be carried over verbatim — it's battle-tested

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-domain-analysis-agents*
*Context gathered: 2026-02-24*
