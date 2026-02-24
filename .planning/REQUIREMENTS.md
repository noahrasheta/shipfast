# Requirements: dc-due-diligence-desktop

**Defined:** 2026-02-23
**Core Value:** A non-technical co-worker can run a full 9-domain data center due diligence analysis from Claude Desktop without ever touching a terminal, and get results in an editable document format.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Plugin Infrastructure

- [x] **INFRA-01**: Plugin uses correct Cowork format (.claude-plugin/plugin.json, commands/, skills/) and activates when uploaded
- [x] **INFRA-02**: Plugin distributable as ZIP file that installs via drag-and-drop in Cowork — no terminal required
- [x] **INFRA-03**: User can type `/due-diligence` to trigger the full analysis workflow
- [ ] **INFRA-04**: Plugin includes clear README with setup instructions a non-technical user can follow

### Document Ingestion

- [ ] **INGEST-01**: Orchestrator reads PDF files from workspace folder using Cowork's native file reading
- [ ] **INGEST-02**: Orchestrator reads DOCX, XLSX, PPTX files from workspace folder using native file reading
- [ ] **INGEST-03**: Orchestrator reads scanned PDFs and images using Claude's native vision/OCR capabilities
- [ ] **INGEST-04**: Orchestrator handles data rooms with 50+ files by batching or routing documents across agents to stay within the 20-file-per-chat platform limit
- [ ] **INGEST-05**: Orchestrator creates a document inventory/index of all files in the data room before dispatching agents

### Domain Analysis

- [ ] **DOMAIN-01**: Power agent analyzes power infrastructure, utility providers, capacity, and redundancy
- [ ] **DOMAIN-02**: Connectivity agent analyzes fiber routes, carrier availability, and network infrastructure
- [ ] **DOMAIN-03**: Water & Cooling agent analyzes cooling systems, water sources, and efficiency
- [ ] **DOMAIN-04**: Land & Zoning agent analyzes property details, zoning compliance, and entitlements
- [ ] **DOMAIN-05**: Ownership agent analyzes ownership structure, liens, and transaction history
- [ ] **DOMAIN-06**: Environmental agent analyzes environmental risks, compliance, and remediation
- [ ] **DOMAIN-07**: Commercials agent analyzes financial terms, lease structures, and pricing
- [ ] **DOMAIN-08**: Natural Gas agent analyzes gas infrastructure, supply, and backup generation
- [ ] **DOMAIN-09**: Market Comparables agent analyzes comparable transactions and market positioning
- [ ] **DOMAIN-10**: Each domain agent conducts web research using built-in WebSearch for live market data, regulatory info, and utility rates
- [ ] **DOMAIN-11**: Each domain agent writes its report to the workspace folder as an intermediate file (session resilience)
- [ ] **DOMAIN-12**: Each domain agent implements document safety protocol to detect and flag embedded prompt injection attempts

### Synthesis & Scoring

- [ ] **SYNTH-01**: Risk Assessment agent reads all 9 domain reports and identifies cross-cutting risks
- [ ] **SYNTH-02**: Executive Summary agent produces scored summary with Pursue / Proceed with Caution / Pass verdict
- [ ] **SYNTH-03**: Executive Summary applies the same scoring rubric and normalized category scores as the CLI version
- [ ] **SYNTH-04**: Client Summary agent produces external-facing report without internal scoring language
- [ ] **SYNTH-05**: Synthesis agents handle missing domain reports gracefully (continue with available data)

### Output & Delivery

- [ ] **OUTPUT-01**: All reports written to the workspace folder as files the user can access
- [ ] **OUTPUT-02**: Final deliverables generated in Word (DOCX) format for easy editing
- [ ] **OUTPUT-03**: Final deliverables also generated in PDF format for distribution
- [ ] **OUTPUT-04**: Markdown versions of all reports also available in workspace folder

### Platform Validation

- [ ] **PLAT-01**: Validate whether Cowork supports parallel sub-agent dispatch (Task tool equivalent) — if yes, use parallel Wave 1; if no, use sequential execution
- [ ] **PLAT-02**: Sequential execution fallback works correctly for all 9 domain agents if parallel is unavailable
- [x] **PLAT-03**: Workflow handles Cowork session interruptions by writing intermediate results to disk after each agent completes

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Enhanced Search

- **SEARCH-01**: Agents use MCP-enhanced web search (Brave/Tavily/Exa) if configured in Claude Desktop
- **SEARCH-02**: Graceful fallback to built-in WebSearch when MCP search servers are not configured

### Team Collaboration

- **TEAM-01**: Completed analysis shareable as Cowork project with colleagues (Team plan)
- **TEAM-02**: Organization-wide plugin provisioning when Cowork ships that feature

### Performance

- **PERF-01**: Parallel sub-agent dispatch optimization (if validated but not initially implemented)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Modifying existing dc-due-diligence CLI plugin | CLI version works well; Desktop is a separate plugin |
| Claude Code CLI compatibility | Desktop-exclusive by design; different architectures |
| Real-time collaboration during analysis | Analysis is single-user trigger; share results after |
| Custom scoring rubric editing | Use same rubric as CLI; avoids complexity and version drift |
| Python dependency for any functionality | Non-technical user can't manage venvs or pip |
| Mobile or web-only access | Claude Desktop Mac app only |
| Git-based distribution | Non-technical user won't clone repos |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1 | Complete (Plan 01-01) |
| INFRA-02 | Phase 1 | Complete |
| INFRA-03 | Phase 1 | Complete |
| INFRA-04 | Phase 5 | Pending |
| INGEST-01 | Phase 2 | Pending |
| INGEST-02 | Phase 2 | Pending |
| INGEST-03 | Phase 2 | Pending |
| INGEST-04 | Phase 2 | Pending |
| INGEST-05 | Phase 2 | Pending |
| DOMAIN-01 | Phase 3 | Pending |
| DOMAIN-02 | Phase 3 | Pending |
| DOMAIN-03 | Phase 3 | Pending |
| DOMAIN-04 | Phase 3 | Pending |
| DOMAIN-05 | Phase 3 | Pending |
| DOMAIN-06 | Phase 3 | Pending |
| DOMAIN-07 | Phase 3 | Pending |
| DOMAIN-08 | Phase 3 | Pending |
| DOMAIN-09 | Phase 3 | Pending |
| DOMAIN-10 | Phase 3 | Pending |
| DOMAIN-11 | Phase 3 | Pending |
| DOMAIN-12 | Phase 3 | Pending |
| SYNTH-01 | Phase 4 | Pending |
| SYNTH-02 | Phase 4 | Pending |
| SYNTH-03 | Phase 4 | Pending |
| SYNTH-04 | Phase 4 | Pending |
| SYNTH-05 | Phase 4 | Pending |
| OUTPUT-01 | Phase 4 | Pending |
| OUTPUT-02 | Phase 4 | Pending |
| OUTPUT-03 | Phase 4 | Pending |
| OUTPUT-04 | Phase 4 | Pending |
| PLAT-01 | Phase 1 | Pending |
| PLAT-02 | Phase 1 | Pending |
| PLAT-03 | Phase 1 | Complete |

**Coverage:**
- v1 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0

---
*Requirements defined: 2026-02-23*
*Last updated: 2026-02-24 after Plan 01-01 — INFRA-01 marked complete*
