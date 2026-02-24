# Roadmap: dc-due-diligence-desktop

## Overview

Build a Claude Cowork-native version of the data center due diligence plugin that non-technical users can install via ZIP upload and trigger with a single slash command. The roadmap begins by resolving the single load-bearing unknown — whether Cowork supports parallel sub-agent dispatch — before scaling to agent content. Phases flow from platform validation to document ingestion to domain agents to synthesis and output, ending with hardening and distribution for a non-technical audience.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation and Validation** - Prove plugin loads in Cowork, slash command fires, and validate whether parallel sub-agent dispatch is available (completed 2026-02-24)
- [x] **Phase 2: Document Ingestion and Routing** - Build orchestrator document inventory and per-agent file routing that keeps each agent within token budget (completed 2026-02-24)
- [x] **Phase 3: Domain Analysis Agents** - Port all 9 domain agents with web research, disk writes, and safety protocol (completed 2026-02-24)
- [x] **Phase 4: Synthesis and Document Output** - Add Risk Assessment, Executive Summary, Client Summary, and Word/PDF output (completed 2026-02-24)
- [ ] **Phase 5: Hardening and Distribution** - Stress test with large data rooms, validate clean-machine install, write non-technical README

## Phase Details

### Phase 1: Foundation and Validation
**Goal**: A working Cowork plugin stub installs via ZIP, activates via `/due-diligence`, reads files from the workspace folder, and the parallel dispatch question is answered empirically
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, PLAT-01, PLAT-02, PLAT-03
**Success Criteria** (what must be TRUE):
  1. User uploads ZIP file in Cowork plugin interface and plugin activates without any terminal interaction
  2. User types `/due-diligence` and the slash command triggers the orchestrator workflow
  3. Orchestrator lists files present in the mounted workspace folder and displays the count
  4. Empirical test confirms whether sub-agent dispatch runs concurrently or sequentially — result documented and architecture decision recorded
  5. Sequential fallback executes all orchestrator steps correctly when parallel dispatch is unavailable
**Plans**: 3 plans in 3 waves (sequential — each depends on prior)

Plans:
- [x] 01-01-PLAN.md — Scaffold Cowork plugin directory structure (plugin.json, commands/due-diligence.md, skills/due-diligence/SKILL.md) [Wave 1, autonomous]
- [ ] 01-02-PLAN.md — ZIP packaging, file discovery, slash command validation in Cowork [Wave 2, has checkpoint]
- [ ] 01-03-PLAN.md — Parallel dispatch smoke test and architecture decision recording [Wave 3, has checkpoint]

### Phase 2: Document Ingestion and Routing
**Goal**: Orchestrator inventories the full data room, categorizes documents by domain, and routes relevant files to each agent in batches that stay within the 20-file-per-chat platform limit
**Depends on**: Phase 1
**Requirements**: INGEST-01, INGEST-02, INGEST-03, INGEST-04, INGEST-05
**Success Criteria** (what must be TRUE):
  1. Orchestrator reads and displays an inventory of all PDF, DOCX, XLSX, PPTX, and image files in the workspace folder
  2. Orchestrator correctly reads a scanned PDF or image file using native vision/OCR (no Python required)
  3. Orchestrator categorizes a 50-file data room and routes each file to its domain bucket without exceeding the 20-file limit for any single agent dispatch
  4. Document inventory file is written to the workspace folder before any domain agent is dispatched
**Plans**: 2 plans in 2 waves (sequential — Plan 02 depends on Plan 01)

Plans:
- [x] 02-01-PLAN.md — Expand file discovery, add native document reading, and write _dd_inventory.json to disk [Wave 1, autonomous]
- [x] 02-02-PLAN.md — Domain categorization with keyword matching, batch splitting for 20-file limit, and routing metadata [Wave 2, autonomous]

### Phase 3: Domain Analysis Agents
**Goal**: All 9 domain agents analyze their assigned documents, conduct live web research, write reports to disk, and detect embedded prompt injection
**Depends on**: Phase 2
**Requirements**: DOMAIN-01, DOMAIN-02, DOMAIN-03, DOMAIN-04, DOMAIN-05, DOMAIN-06, DOMAIN-07, DOMAIN-08, DOMAIN-09, DOMAIN-10, DOMAIN-11, DOMAIN-12
**Success Criteria** (what must be TRUE):
  1. Each of the 9 domain agents (Power, Connectivity, Water/Cooling, Land/Zoning, Ownership, Environmental, Commercials, Natural Gas, Market Comparables) produces a report written to the workspace folder
  2. At least one domain agent returns a verifiable recent data point from live web research (not training-data hallucination) — confirmed by querying for data that changes frequently
  3. If an agent's run is interrupted, its completed report is already on disk and the orchestrator skips that domain on resume
  4. Any document containing an embedded instruction attempt is flagged in the agent report rather than executed
**Plans**: 3 plans in 1 wave (parallel — all 3 plans create independent agent files with no shared files)

Plans:
- [x] 03-01-PLAN.md — Port Power, Connectivity, Water/Cooling agents + orchestrator dispatch logic (resume, parallel dispatch, checkpoint) [Wave 1, autonomous]
- [x] 03-02-PLAN.md — Port Land/Zoning, Ownership, Environmental, Commercials agents [Wave 1, autonomous]
- [x] 03-03-PLAN.md — Port Natural Gas and Market Comparables agents — complete 9-agent roster [Wave 1, autonomous]

### Phase 4: Synthesis and Document Output
**Goal**: Risk Assessment, Executive Summary, and Client Summary agents synthesize domain reports into a Pursue/Proceed/Pass verdict, with final deliverables in Word and PDF format
**Depends on**: Phase 3
**Requirements**: SYNTH-01, SYNTH-02, SYNTH-03, SYNTH-04, SYNTH-05, OUTPUT-01, OUTPUT-02, OUTPUT-03, OUTPUT-04
**Success Criteria** (what must be TRUE):
  1. Risk Assessment agent reads all available domain reports and produces a cross-domain risk file in the workspace folder
  2. Executive Summary agent produces a scored report with a Pursue / Proceed with Caution / Pass verdict using the same normalized scoring rubric as the CLI version
  3. Client Summary agent produces an external-facing report without internal scoring language
  4. Final reports are available as Word (.docx) files the user can open and edit
  5. Final reports are also available as PDF files ready for distribution
  6. Workflow completes successfully when one or more domain reports are missing (graceful degradation)
**Plans**: 3 plans in 2 waves (Wave 1 parallel agent porting, Wave 2 orchestrator wiring)

Plans:
- [x] 04-01-PLAN.md — Port Risk Assessment and Executive Summary agents with embedded scoring rubric [Wave 1, autonomous]
- [x] 04-02-PLAN.md — Port Client Summary agent with embedded template structure [Wave 1, autonomous]
- [x] 04-03-PLAN.md — Add synthesis dispatch, DOCX generation, and completion UX to orchestrator [Wave 2, autonomous, depends on 04-01 + 04-02]

### Phase 5: Hardening and Distribution
**Goal**: Plugin survives large data rooms, installs cleanly on a fresh Cowork instance a non-technical user has never configured, and ships with documentation they can follow
**Depends on**: Phase 4
**Requirements**: INFRA-04
**Success Criteria** (what must be TRUE):
  1. Plugin runs successfully on a data room with 50+ files without context window exhaustion or silent agent failure
  2. A non-technical user following only the README can install the plugin and complete a full analysis run with no external help
  3. README is written in plain language with no terminal commands, no git references, and no technical jargon
**Plans**: 2 plans in 2 waves (sequential — Plan 02 depends on Plan 01)

Plans:
- [ ] 05-01-PLAN.md — Harden orchestrator with pre-dispatch data room warning, enhanced post-Wave-1 validation, failure messaging, and SKILL.md cleanup [Wave 1, autonomous]
- [ ] 05-02-PLAN.md — Write non-technical README with plain-language install, usage, output, and troubleshooting guide [Wave 2, autonomous, depends on 05-01]

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation and Validation | 3/3 | Complete   | 2026-02-24 |
| 2. Document Ingestion and Routing | 2/2 | Complete | 2026-02-24 |
| 3. Domain Analysis Agents | 3/3 | Complete | 2026-02-24 |
| 4. Synthesis and Document Output | 3/3 | Complete | 2026-02-24 |
| 5. Hardening and Distribution | 0/2 | Not started | - |
