# Project Research Summary

**Project:** dc-due-diligence-desktop
**Domain:** Claude Desktop/Cowork plugin — multi-agent document analysis workflow
**Researched:** 2026-02-23
**Confidence:** MEDIUM (core platform facts HIGH; Cowork parallelism mechanism UNRESOLVED — see critical conflict below)

---

## CRITICAL RESEARCH CONFLICT: Task Tool Availability in Cowork

Before reading this summary, understand that the 4 researchers produced directly contradictory findings on the single most important architectural question: whether the Task tool (parallel sub-agent dispatch) is available inside Claude Cowork.

**Architecture researcher says YES:**
> "Cowork IS Claude Code, running inside a local Ubuntu VM. The Task tool is available — parallel agent spawning works exactly as in the CLI version."
> Source: pvieito.com reverse-engineering analysis (rated HIGH confidence)

**Pitfalls researcher says NO:**
> "Claude Desktop and Cowork do NOT have the Task tool. Multi-agent orchestration via Task tool spawning is a Claude Code CLI feature only."
> Sources: Multiple community sources, Arsturn comparison article, DEV Community Task tool breakdown

**Stack and Features researchers are intermediate:** Both confirmed that sub-agent parallelism exists but described it as "Cowork's native sub-agent dispatch" (distinct language from "Task tool"), flagged its limits as unknown, and rated parallel dispatch at LOW-MEDIUM confidence.

**Synthesis judgment:** The conflict is irreconcilable from research alone and must be resolved by empirical testing. The Architecture researcher's source (pvieito reverse-engineering) is technically credible and specific — it claims Cowork literally runs `claude` CLI inside a VM, which would make the Task tool available. The Pitfalls researcher's sources are consistent with the conventional understanding of Desktop limitations but may not account for the VM architecture. The safest interpretation: **the Task tool MAY be available via the VM, but this cannot be assumed without a validation test.** Build Phase 1 to include a "can the orchestrator spawn a parallel sub-agent?" smoke test before committing to either architecture.

**Recommendation: Build for sequential execution first. If Task tool is confirmed available in the VM, upgrade to parallel Wave 1 as a performance enhancement in the same phase or the next.**

---

## Executive Summary

The `dc-due-diligence-desktop` plugin is a non-technical-user-facing port of the existing `dc-due-diligence` CLI plugin, targeting Claude Cowork (a Claude Desktop agentic mode). The core concept is sound: Cowork gives non-technical knowledge workers access to multi-step agentic workflows without terminal access, Python management, or git. The existing 12-agent, 4-wave analysis pipeline maps naturally to Cowork's capabilities — the question is whether it maps exactly (with Task tool parallelism) or approximately (with sequential fallback). Research strongly supports that Cowork eliminates the three biggest CLI pain points: Python dependencies, file conversion setup, and terminal-based plugin installation.

The recommended architecture is a ground-up rewrite using the Cowork plugin format (not a fork of the CLI plugin), distributed as a ZIP upload via Cowork's plugin interface. The plugin uses native file reading (no Python converters), Cowork's built-in web search (no MCP required for web research), and Claude's native document creation capability for Word/PDF output. The 9 domain agents, Risk Assessment, Executive Summary, and Client Summary agents carry over with path and invocation adjustments. Document routing — giving each domain agent only its relevant files rather than the full data room — is a critical design requirement that does not exist in the CLI version and must be added.

The two highest-risk areas are: (1) whether Cowork supports Task-tool-level parallelism (unresolved — must be validated empirically in Phase 1), and (2) context window exhaustion from naive document loading (well-documented risk with a clear mitigation: per-agent document routing). Secondary risks include web search availability (built-in in Cowork, but agents must not hardcode CLI-specific `WebSearch` tool calls), session persistence (intermediate results must be written to disk after each agent, not accumulated in context), and non-technical installation friction (use ZIP upload, not terminal-based install). All secondary risks have known mitigations.

---

## Key Findings

### Recommended Stack

Cowork plugins use a `plugin.json` manifest plus `skills/`, `agents/`, and `commands/` directories — structurally similar to the CLI plugin format but invoked differently. The distribution mechanism for non-technical users is ZIP upload via Cowork's "Upload plugin" interface (no terminal, no git). MCPB Desktop Extensions (.mcpb format) are relevant only if the plugin bundles an MCP server; the core plugin does not require one. Claude Desktop ships with Node.js bundled, so any MCP server the plugin needs should be written in Node.js and packaged as .mcpb.

**Core technologies:**
- Agent Skills / Cowork Plugin format (SKILL.md + plugin.json + agents/*.md): orchestration layer — the canonical format for Cowork workflow plugins
- Claude Cowork (Jan 2026 research preview): execution environment — provides file access, agentic workflow, built-in web search, document output, all zero-config for the user
- ZIP plugin distribution: delivery format — non-technical users upload via Cowork's plugin interface, no terminal required
- MCPB Desktop Extensions: optional, only if an MCP server is needed for document output or enhanced web search

**What is NOT needed (vs. CLI version):**
- Python venv — VM or Cowork handles document reading natively
- Python converters (pdfplumber, openpyxl, markdown-pdf) — native file reading replaces them
- `claude --plugin-dir` installation — ZIP upload replaces it
- Task tool (CLI-specific) — Cowork sub-agent dispatch replaces it (mechanism TBD)

### Expected Features

Research is aligned on what must ship for v1 and what can wait.

**Must have (table stakes):**
- ZIP-installable plugin with correct Cowork format — without this, non-technical distribution fails
- `/due-diligence` slash command entry point — single trigger for full workflow
- Native reading of all document types (PDF, DOCX, XLSX, PPTX, images) — replaces Python converters entirely
- All 9 domain agent files — feature parity with CLI version
- Sequential orchestration as the guaranteed fallback — correctness over performance
- Risk Assessment and Executive Summary agents — required for Pursue/Proceed/Pass verdict
- Intermediate file writes after each agent — session resilience against Cowork timeouts
- Document safety protocol — prompt injection defense, carried over from CLI version
- Document routing — per-agent file filtering to avoid context window exhaustion (critical addition not in CLI version)

**Should have (differentiators, add after v1 validation):**
- Doc/PDF output (Word and PDF reports instead of markdown)
- Parallel sub-agent dispatch in Wave 1 — if Task tool is confirmed available OR if Cowork native dispatch achieves true parallelism
- Client-facing summary agent — existing CLI logic, straightforward port
- MCP-enhanced web search integration (Brave/Tavily/Exa) — graceful enhancement

**Defer to v2+:**
- Cowork project sharing workflow — requires Team/Enterprise plan adoption
- Organization-wide plugin provisioning — Anthropic has announced this as a future feature; wait for platform to ship
- Scoring rubric customization — adds complexity without proven demand

### Architecture Approach

The plugin's architecture mirrors the CLI version's 4-wave structure but with platform-appropriate substitutions. Cowork mounts the user's data room folder bidirectionally — the orchestrator discovers documents via file system tools, routes relevant files to each domain agent, and agents write their reports back to the data room folder as they complete. The output layer uses Claude's native document creation skill or a LibreOffice-based conversion (if the VM hypothesis is confirmed) rather than Python-based markdown-pdf. The key structural addition is document routing: the orchestrator must categorize documents by domain before dispatching agents, so each agent works within a manageable token budget.

**Major components:**
1. Plugin manifest + slash command entry point — defines the workflow trigger and Cowork plugin identity
2. SKILL.md orchestrator — drives all 4 waves, handles document inventory, routing, and agent dispatch
3. 9 domain agent files — domain-specific analysis with web research and file write
4. Synthesis agents (Risk Assessment, Executive Summary, Client Summary) — sequential, depend on Wave 1 outputs
5. Output layer — converts markdown reports to Word/PDF via native Cowork capability or VM tools
6. Document router — categorizes data room files before agent dispatch; critical addition for context management

### Critical Pitfalls

1. **Task tool assumption without validation** — designing the entire orchestration around Task-tool parallelism before confirming it works in Cowork will produce a broken plugin. Build and test a minimal parallel dispatch smoke test in Phase 1 before designing Wave 1 architecture.

2. **Context window exhaustion from loading all documents** — a data room with 15+ files loaded into one context will exhaust the 200K token window before all domain agents run. Per-agent document routing (only load files relevant to each domain) is the mitigation. This must be designed before any agent prompts are written, not added later.

3. **Web research silent failure** — agent prompts that reference `WebSearch` or `WebFetch` as tool calls (CLI-specific) will silently fail in Cowork. Cowork has built-in web search, but agents must use it through natural language instructions, not hardcoded tool call syntax. Verify web research actually executes (not training-data hallucination) during Phase 2 agent testing.

4. **Session amnesia destroying partial results** — a 15-45 minute workflow interrupted mid-run loses all in-context accumulated results. Each domain agent must write its report to disk before the orchestrator proceeds. Resume detection (skip domains whose reports already exist on disk) must be built into Wave 1.

5. **Wrong plugin format (CLI vs. Cowork)** — the CLI plugin's SKILL.md-based slash command system does not work in Claude Desktop. The Desktop plugin must use Cowork's plugin format with a `commands/` directory entry point. These are separate architectures requiring separate implementations, not a fork.

---

## Implications for Roadmap

Based on combined research, a 5-phase roadmap is recommended.

### Phase 1: Foundation and Validation

**Rationale:** The unresolved Task tool conflict and plugin format question must be answered before any agent content is written. Building 12 agent files on top of an unvalidated orchestration mechanism is the highest-risk failure mode in this project. Phase 1 proves the scaffold works before investing in content.

**Delivers:** A working Cowork plugin stub that: installs via ZIP, activates via `/due-diligence` slash command, reads files from the mounted workspace folder, and dispatches at least one sub-agent. The parallel dispatch question is answered empirically here.

**Addresses:** ZIP install, slash command entry point, workspace folder access (from FEATURES.md P1 list)

**Avoids:**
- Wrong plugin format (Pitfall 5) — resolve before writing any content
- Task tool assumption (Pitfall 1) — validate parallelism mechanism empirically
- Non-technical installation friction (Pitfall 3) — test on clean machine

**Research flag:** This phase needs careful testing, not research. The outcome of the parallel dispatch test directly determines the Phase 2 architecture. Do not skip this validation step.

### Phase 2: Document Routing and Single-Agent Pipeline

**Rationale:** Before building all 9 domain agents, prove the full pipeline with one agent end-to-end. The document routing system (the critical addition not in the CLI version) must be designed and validated before it's too late to change. Context window budget planning happens here.

**Delivers:** Full pipeline proof: orchestrator inventories data room, routes power-related documents to the Power agent, Power agent conducts web research, writes its report to disk. Session resume detection built in.

**Addresses:** Native file reading, document safety protocol, web research verification, intermediate file writes (from FEATURES.md P1 list)

**Avoids:**
- Context window exhaustion (Pitfall 2) — document routing designed and tested with realistic document set
- Web research silent failure (Pitfall 4) — verified with observable recent data points
- Session amnesia (Pitfall 6) — disk write pattern established in this phase

**Research flag:** Document routing logic for data center documents (which file types go to which domain) may benefit from a short research pass. The categorization heuristics from the CLI version's agent prompts are a good starting point.

### Phase 3: Full Wave 1 and Synthesis Agents

**Rationale:** Once the single-agent pipeline is proven, the remaining 8 domain agents are largely copy-paste from the CLI version with path and tool-call adjustments. Synthesis agents (Risk Assessment, Executive Summary) follow immediately since they depend on Wave 1 outputs.

**Delivers:** Complete 9-domain analysis pipeline producing markdown reports in the data room folder, plus Risk Assessment and Executive Summary markdown outputs. This is the complete functional MVP.

**Addresses:** All 9 domain agents, Risk Assessment, Executive Summary (from FEATURES.md P1 list)

**Avoids:**
- Sequential fallback as the default — all agents write to disk; parallel dispatch added here if Phase 1 confirmed it works

**Research flag:** Standard pattern. Agent content is carried from CLI version. No additional research needed unless specific domain prompts need updates for 2026 market conditions.

### Phase 4: Output Quality and UX Polish

**Rationale:** The MVP produces markdown reports. Phase 4 upgrades output to Word/PDF documents and adds the UX details non-technical users need: progress messages, folder path display at completion, error messaging when an agent fails.

**Delivers:** Word (.docx) and PDF output reports, Client Summary agent, progress visibility at each wave, error handling with user-facing messages.

**Addresses:** Doc/PDF output, Client Summary agent (from FEATURES.md P2 list)

**Avoids:**
- Presenting raw markdown to non-technical users (UX Pitfall)
- Silent failure when domain agent produces no output (UX Pitfall)
- No instruction for where output files landed (UX Pitfall)

**Research flag:** Document output mechanism needs a decision: use native Cowork file creation skill, Office-Word MCP server, or LibreOffice in VM (if VM hypothesis is confirmed). This decision depends on Phase 1's Task tool validation — if Cowork runs in a VM, LibreOffice is available for free. If not, native Cowork skill or an MCP server is needed.

### Phase 5: Distribution and Hardening

**Rationale:** Polish the non-technical user experience for distribution. Large data room stress testing, clean-machine install test, security review of MCP permissions and document safety protocol.

**Delivers:** Production-ready plugin with verified clean-machine installation, tested with realistic 15+ file data rooms, MCP permissions scoped correctly, optional Tavily/Exa MCP configuration documented.

**Addresses:** MCP-enhanced web search, non-technical distribution (from FEATURES.md P2/P3 list)

**Avoids:**
- MCP server dependency failures (Pitfall 3) — Node.js runtime, no Python MCP servers
- Broad filesystem permissions (Security Pitfall)
- Large data room performance failure (Performance Trap)

**Research flag:** Standard distribution and security patterns. No additional research needed beyond confirming MCPB packaging approach works for the specific MCP servers chosen.

### Phase Ordering Rationale

- Phase 1 before everything else because the Task tool conflict is a load-bearing question — every subsequent architecture decision depends on the answer
- Phase 2 before scaling to 9 agents because document routing must be proven with one agent before it's embedded in 12
- Phase 3 follows naturally from proven pipeline — agent content is the lowest-risk work
- Phase 4 deferred until correct output exists — formatting correct output is easier than formatting incorrect output
- Phase 5 last because hardening is most effective once the workflow is stable and all features are present

### Research Flags

Phases needing deeper research during planning:
- **Phase 1:** No research needed — needs empirical testing. The Task tool question cannot be answered by reading; it must be answered by running a Cowork plugin that tries to dispatch a sub-agent.
- **Phase 4:** Output mechanism decision (native skill vs. MCP vs. LibreOffice) depends on Phase 1 findings. A short research pass during Phase 4 planning to evaluate current state of Cowork's native document creation skill quality.

Phases with standard patterns (skip research-phase):
- **Phase 2:** Document routing heuristics can be derived from existing agent prompts
- **Phase 3:** Agent content is a port, not a new design
- **Phase 5:** Distribution and security follow established MCPB patterns

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Core platform capabilities (native file reading, web search, ZIP install, document output) verified via official Anthropic sources. MCPB format, plugin structure, and plan requirements all confirmed. |
| Features | HIGH | MVP feature set well-defined and consistent across all 4 researchers. Parallel dispatch is the only P1 feature with unresolved mechanism. |
| Architecture | MEDIUM | The 4-wave structure is sound and directly maps from the CLI version. The Cowork-specific mechanism for Wave 1 parallelism is the single unresolved question. All other architectural decisions (document routing, disk writes, output layer) are well-grounded. |
| Pitfalls | MEDIUM | Task tool conflict is the central uncertainty; pitfalls researcher may have missed the VM architecture detail. All other pitfalls (context exhaustion, session amnesia, web research failure, format mismatch) are independently confirmed by multiple sources and should be treated as definite risks. |

**Overall confidence:** MEDIUM-HIGH

The project is well-understood except for the one empirical question about Cowork's VM architecture and Task tool availability. That question is answerable in Phase 1 with a 30-minute prototype test. Everything else — the plugin format, the agent content, the distribution mechanism, the context management strategy — is on solid footing.

### Gaps to Address

- **Task tool / parallelism mechanism:** Build a minimal Cowork plugin that attempts to dispatch two sub-agents in parallel. Observe whether they actually run concurrently. This is the only gap that cannot be closed by reading more documentation — it requires running code.

- **Document output quality baseline:** Before Phase 4, test what Claude's native document creation skill produces for a markdown-to-docx conversion. If quality is acceptable, no MCP server is needed. If not, evaluate Office-Word MCP server or LibreOffice (if VM is confirmed).

- **Web search verification method:** During Phase 2, design a test that proves agents are performing live web research rather than generating training-data answers. The test must query for information that changes frequently (e.g., current utility rates in a specific geography) and verify the answer contains a recent data point.

- **Cowork plugin format verification:** The Architecture researcher and Pitfalls researcher use slightly different language for the plugin structure (Architecture cites `knowledge-work-plugins` GitHub as the reference; Pitfalls references a `commands/` directory as the entry point). Confirm the exact required plugin structure against the official `anthropics/knowledge-work-plugins` reference before scaffolding Phase 1.

---

## Sources

### Primary (HIGH confidence)
- [Introducing Cowork | Claude](https://claude.com/blog/cowork-research-preview) — Cowork capabilities, file access, sub-agent architecture
- [Getting started with Cowork | Claude Help Center](https://support.claude.com/en/articles/13345190-getting-started-with-cowork) — workspace, plan requirements, available skills
- [Customize Cowork with plugins | Claude](https://claude.com/blog/cowork-plugins) — plugin structure, slash commands, sub-agents
- [anthropics/knowledge-work-plugins GitHub](https://github.com/anthropics/knowledge-work-plugins) — official plugin format examples
- [One-click MCP server installation for Claude Desktop | Anthropic Engineering](https://www.anthropic.com/engineering/desktop-extensions) — MCPB format, Node.js runtime, distribution
- [Agent Skills - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — SKILL.md specification
- [Claude can now create and edit files | Claude Blog](https://claude.com/blog/create-files) — docx/pdf/xlsx/pptx output capability
- [Create and edit files with Claude | Claude Help Center](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude) — file creation plan availability

### Secondary (MEDIUM confidence)
- [Inside Claude Cowork: How Anthropic Runs Claude Code in a Local VM on Your Mac](https://pvieito.com/2026/01/inside-claude-cowork) — VM architecture reverse-engineering (HIGH for the Architecture researcher; rated MEDIUM here due to conflict with Pitfalls findings)
- [Claude Cowork Tutorial | DataCamp](https://www.datacamp.com/tutorial/claude-cowork-tutorial) — usage guide, sub-agent coordination
- [What Is Claude Cowork? VM, Plugins, and SaaS Impact](https://www.marc0.dev/en/blog/claude-cowork-engineering-deep-dive-vm-plugins-saaspocalypse-1770479461092) — engineering deep dive
- [The Hidden Cost of MCPs and Custom Instructions on Your Context Window](https://selfservicebi.co.uk/analytics%20edge/improve%20the%20experience/2025/11/23/the-hidden-cost-of-mcps-and-custom-instructions-on-your-context-window.html) — MCP token costs
- [Claude Desktop vs Claude Code | Arsturn](https://www.arsturn.com/blog/claude-desktop-vs-claude-code-should-you-switch-for-mcp-features) — Task tool is CLI-specific (supports Pitfalls position)
- [How I mastered Claude Cowork — the amnesia problem](https://ai.plainenglish.io/how-i-mastered-claude-cowork-the-amnesia-problem-c8dabcfa3abb) — session memory loss patterns

### Tertiary (LOW confidence — needs validation)
- [The Task Tool: Claude Code's Agent Orchestration System | DEV Community](https://dev.to/bhaidar/the-task-tool-claude-codes-agent-orchestration-system-4bf2) — Task tool described as CLI-only (may predate VM architecture)
- [Claude Code Sub-Agents: Parallel vs Sequential Patterns | ClaudeFa.st](https://claudefa.st/blog/guide/agents/sub-agent-best-practices) — parallel vs sequential patterns

---
*Research completed: 2026-02-23*
*Ready for roadmap: yes — pending empirical Task tool validation in Phase 1*
