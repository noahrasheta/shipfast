# Feature Research

**Domain:** Claude Desktop/Cowork plugin — complex multi-agent document analysis workflow
**Researched:** 2026-02-23
**Confidence:** MEDIUM (most capabilities verified via official sources and recent 2026 articles; Cowork sub-agent parallelism nuances LOW confidence due to limited first-party docs)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist in a Desktop-native workflow plugin. Missing these = workflow breaks or product feels unusable.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Native file reading (PDF, Word, Excel, PowerPoint) | User drops data room folder in; workflow must read everything in it | LOW | Claude Desktop natively reads PDF, DOCX, XLSX, PPTX up to 30MB per file, up to 20 files per chat. This replaces all Python converters from the CLI version. Confidence: HIGH (official Anthropic help article + Feb 2026 release confirmation) |
| Native scanned PDF / image OCR | Data rooms often include scanned broker docs or image-heavy PDFs | MEDIUM | Claude processes PDF pages as images + text streams. Works for most docs. Degrades on poor scans, dense tables, and docs > ~100 pages (visual analysis limit). May still need fallback instruction for low-quality scans. Confidence: MEDIUM |
| Web search per domain agent | 9-domain analysis requires live market data, regulatory lookups, utility rates | MEDIUM | Claude Desktop has built-in WebSearch/WebFetch. MCP-based alternatives (Brave, Tavily, Exa) add capability but require configuration. Built-in is table stakes; MCP search is a differentiator. Confidence: HIGH |
| Multi-step orchestrated workflow from single prompt | User says "run due diligence on this folder" and gets the full 9-domain output | HIGH | Cowork uses Claude's agentic architecture. Orchestration pattern must be defined in plugin commands/skills. The key unknown: whether Cowork supports parallel sub-agent dispatch as freely as Claude Code's Task tool. Confidence: MEDIUM |
| Progress visibility during long-running analysis | Analysis takes minutes; user needs to know it's working | MEDIUM | Claude Cowork shows tool uses as they happen. Skills progress indicators show tool calls in real time. Not a custom-build concern — it's native behavior. Confidence: MEDIUM |
| Output written to local files | Final reports must land in the user's folder, not just in the conversation | MEDIUM | Cowork reads AND writes files in the designated workspace folder. Claude can read, edit, create files directly. This is native Cowork capability. Confidence: HIGH |
| Plugin installable via ZIP upload | Non-technical user cannot use git clone or npm; must be drag-and-drop | LOW | Cowork supports ZIP upload: user downloads ZIP, drags into the Cowork interface, clicks Upload. No terminal required. Confidence: HIGH (multiple install guides confirm this) |
| No Python dependency | Non-technical user cannot manage venvs or pip | LOW | Native file reading in Desktop/Cowork eliminates the Python converter requirement entirely. Doc/PDF output via Claude's built-in code interpreter (sandboxed) also requires no user-side Python. Confidence: HIGH |
| Workspace folder access | Plugin must read all files in a user-specified data room folder | LOW | Cowork gives Claude access to a specific folder the user designates. Claude can read/write/organize files within that folder. Confidence: HIGH |

### Differentiators (Competitive Advantage)

Features that distinguish the Desktop version from the CLI version or from a raw Claude conversation. Not required for basic function, but meaningfully better UX or capability.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Doc/PDF output (not markdown) | Co-worker gets editable Word docs and printable PDFs — not raw markdown files | MEDIUM | Claude's built-in file builder (available to Max/Team/Enterprise, released Feb 2026) can generate DOCX and PDF in a sandboxed environment. Alternative: Document Edit MCP server for local doc creation. This is a meaningful UX upgrade over the CLI version. Confidence: MEDIUM |
| Cowork sharing — send finished reports | Share the project and output files with colleagues in Claude for Work org | LOW | Team/Enterprise plans support shared projects. Projects have flexible sharing across org. Files in the workspace are accessible to shared project members. Dependency: requires Team or Enterprise plan. Confidence: MEDIUM |
| One-command slash command trigger | `/due-diligence` starts the full workflow — zero extra prompting | LOW | Cowork plugin commands/ directory enables slash commands. User types `/due-diligence` and the orchestrator takes over. Same pattern as Anthropic's open-source knowledge-work-plugins. Confidence: HIGH |
| Parallel domain analysis via sub-agents | 9 domains analyzed simultaneously instead of sequentially — faster results | HIGH | This is the critical differentiator AND the primary technical risk. Cowork uses the same agentic architecture as Claude Code. Whether sub-agents can be dispatched in parallel (as the CLI version does with the Task tool) requires validation. If parallel dispatch works: ~9x speedup. If not: sequential execution still works but is slower. Confidence: LOW — needs implementation validation |
| MCP-enhanced web search (Brave/Tavily/Exa) | Richer research results vs. built-in WebSearch, especially for financial/regulatory domains | MEDIUM | If the user has Brave, Tavily, or Exa MCP configured in Claude Desktop, agents can use them automatically (same pattern as CLI dc-due-diligence). This is opt-in and degrades gracefully to built-in WebSearch. Confidence: HIGH |
| Document safety protocol (embedded instruction detection) | Prevents prompt injection attacks from broker documents | LOW | This is existing logic from the CLI version, ported as a skill/instruction in the plugin. No platform-specific complexity. Confidence: HIGH |
| Client-facing summary generation | Produces clean external report without internal scoring language | LOW | Existing agent logic from CLI version — adapts straightforwardly as a Cowork agent/skill. Confidence: HIGH |

### Anti-Features (Deliberately NOT Building)

Features that seem appealing but should be excluded from this plugin.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Real-time collaboration during active analysis | "Multiple people could review in parallel while it runs" | Cowork's shared projects are view-shared, not co-edited live sessions. Concurrent writes to the same workspace folder create race conditions. The analysis itself is a single-user trigger. | Share the completed project (with output files) after analysis finishes. This is explicitly Out of Scope in PROJECT.md. |
| Custom scoring rubric editing from Desktop UI | Power users want to tweak weights on the fly | Adds UI complexity, breaks reproducibility, creates version drift vs. the canonical CLI version rubric | Use the same locked rubric as the CLI version. Advanced users can edit the plugin's skills files directly. |
| Python dependency for anything | "We could add back some Python scripts for edge cases" | Breaks the No Python constraint. Non-technical users won't manage venvs. One exception creates dependency creep. | Use native file reading + Claude's sandboxed code interpreter for any computation. Document MCP server for doc creation if needed. |
| Mobile or web-only access | "Can this work in the Claude.ai web interface?" | Claude.ai web interface does not support Cowork plugins or the Cowork workspace folder model. Plugin format requires the Desktop app. | This is a Desktop-exclusive plugin by design (PROJECT.md Out of Scope). |
| Git-based plugin distribution | "Just share a GitHub repo link" | Non-technical users won't clone repos. Creates update friction. Requires terminal. | ZIP file distribution via Cowork's "Upload plugin" interface. Once organization-wide provisioning ships (future Cowork feature), that becomes the upgrade path. |
| Fully automated one-click install for non-org users | "Make it a single download and double-click" | Desktop Extensions (.mcpb) are for MCP server bundles, not Cowork plugins. The Cowork ZIP upload is the closest equivalent and already requires no terminal. | ZIP upload via Cowork interface. Document this clearly in the plugin's README for the co-worker. |
| Claude Code CLI compatibility shim | "Could we make one plugin work in both CLI and Desktop?" | The CLI version uses the Task tool, Python converters, and markdown-pdf — all incompatible with the Desktop/Cowork architecture. A compatibility shim would add complexity without value to either version. | Keep them as separate plugins: dc-due-diligence (CLI) and dc-due-diligence-desktop (Cowork). Explicit decision in PROJECT.md. |

---

## Feature Dependencies

```
[ZIP plugin distribution]
    └──requires──> [Plugin has correct Cowork format: .claude-plugin/plugin.json + commands/ + skills/]

[Single-command trigger /due-diligence]
    └──requires──> [Plugin commands/due-diligence.md slash command definition]
                       └──requires──> [Orchestrator skill or agent that drives full workflow]

[9-domain parallel analysis]
    └──requires──> [Orchestrator can dispatch sub-agents in parallel]
                       └──requires──> [Validation: Cowork supports parallel sub-agent dispatch]
                       └──requires──> [9 domain agent files (one per domain)]

[Domain agent web research]
    └──requires──> [WebSearch available in Cowork context]
                       └──enhances──> [MCP search servers (Brave/Tavily/Exa) if configured]

[Doc/PDF output generation]
    └──requires──> [Claude file builder capability (Max/Team/Enterprise plan)]
         OR
    └──requires──> [Document Edit MCP server installed in Claude Desktop]

[Workspace folder file reading]
    └──requires──> [User designates folder in Cowork workspace]
    └──supports──> [Native reading: PDF, DOCX, XLSX, PPTX, images]

[Cowork project sharing]
    └──requires──> [Team or Enterprise Claude plan]

[Output written to local files]
    └──requires──> [Cowork workspace folder write access]
    └──depends-on──> [Doc/PDF output generation OR markdown file write]

[Cross-domain risk assessment]
    └──requires──> [9 domain agents complete first]
    └──sequential-dependency──> [Executive summary requires risk assessment to complete]

[Scanned PDF / OCR handling]
    └──degraded-by──> [Poor image quality, docs > 100 pages visual limit]
    └──fallback──> [Text extraction still works even if visual analysis limited]
```

### Dependency Notes

- **Parallel sub-agents requires validation**: The entire performance story hinges on whether Cowork's orchestrator can dispatch multiple sub-agents simultaneously, as Claude Code does with the Task tool. If parallel dispatch is confirmed, the 9-domain analysis runs concurrently. If not, the workflow runs sequentially — still correct, but slower. This is the highest-risk dependency in the project.
- **Doc/PDF output has a plan dependency**: Native file builder requires Max, Team, or Enterprise plan. If the co-worker is on a Pro plan, doc output requires the Document Edit MCP server as fallback. MVP should handle both paths.
- **Cowork sharing requires Team plan**: If the team uses individual Pro accounts rather than a Team plan, sharing is limited to sending ZIP files or sharing conversation links. Document this constraint clearly.
- **ZIP distribution requires correct plugin format**: The plugin must validate against Cowork's expected plugin format (.claude-plugin/plugin.json, commands/, skills/). If malformed, upload silently fails or plugin doesn't activate.

---

## MVP Definition

### Launch With (v1)

Minimum viable product that validates the core concept: non-technical user runs full 9-domain due diligence from Cowork.

- [ ] ZIP-installable plugin with correct Cowork format — without this, distribution breaks for non-technical users
- [ ] `/due-diligence <folder-path>` slash command that triggers full orchestration — the core UX
- [ ] Native file reading of all document types (PDF, DOCX, XLSX, PPTX, images) — replaces Python converters entirely
- [ ] 9-domain agent files (Power, Connectivity, Water/Cooling, Land/Zoning, Ownership, Environmental, Commercials, Natural Gas, Market Comparables) — feature parity with CLI version
- [ ] Sequential orchestration fallback (if parallel is unconfirmed) — correctness over performance for v1
- [ ] Risk assessment and executive summary agents — required for the Pursue/Proceed/Pass verdict
- [ ] Markdown output to workspace folder — simpler than doc output; validates the pipeline before adding file format complexity
- [ ] Document safety protocol — existing logic, low effort to port, protects against prompt injection

### Add After Validation (v1.x)

- [ ] Doc/PDF output (Word and PDF reports instead of markdown) — add once core pipeline is validated and plan-level file builder capability is confirmed
- [ ] Parallel sub-agent dispatch (if validated as supported in Cowork) — performance upgrade once sequential version is proven correct
- [ ] Client-facing summary agent — existing CLI logic, straightforward port; lower priority than core analysis
- [ ] MCP-enhanced web search integration — graceful enhancement for users with Brave/Tavily/Exa configured

### Future Consideration (v2+)

- [ ] Cowork project sharing workflow — requires Team/Enterprise plan adoption; defer until team migrates from individual Pro accounts
- [ ] Organization-wide plugin provisioning — Anthropic has announced this as a future Cowork feature; wait for the platform to ship it rather than building a workaround
- [ ] Scoring rubric customization — defer unless there's a specific request; adds complexity without proven demand

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| ZIP plugin distribution | HIGH | LOW | P1 |
| `/due-diligence` slash command | HIGH | LOW | P1 |
| Native file reading (PDF/DOCX/XLSX/PPTX) | HIGH | LOW | P1 |
| 9 domain agent files | HIGH | MEDIUM | P1 |
| Sequential orchestration (correctness) | HIGH | MEDIUM | P1 |
| Risk assessment + executive summary | HIGH | MEDIUM | P1 |
| Markdown output to workspace | HIGH | LOW | P1 |
| Document safety protocol | HIGH | LOW | P1 |
| Doc/PDF output (Word/PDF) | HIGH | MEDIUM | P2 |
| Parallel sub-agent dispatch | HIGH | HIGH | P2 |
| Client-facing summary agent | MEDIUM | LOW | P2 |
| MCP-enhanced web search | MEDIUM | LOW | P2 |
| Cowork project sharing | MEDIUM | LOW | P3 |
| Scoring rubric customization | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch (v1)
- P2: Should have, add after validation (v1.x)
- P3: Nice to have, future consideration (v2+)

---

## Platform Capability Summary (What Desktop/Cowork Provides Natively)

Understanding what the platform gives for free vs. what must be built is critical to scoping correctly.

### What Claude Desktop/Cowork Provides Natively (No Custom Build)

| Capability | Details | Confidence |
|------------|---------|------------|
| PDF reading | Native, including page-as-image OCR. Up to 30MB, 20 files per chat. Visual analysis limit ~100 pages. | HIGH |
| DOCX, XLSX, PPTX reading | Native file support confirmed Feb 2026. Same size limits. | HIGH |
| Image reading (vision) | Native multimodal capability. Replaces the Anthropic vision API converter from CLI. | HIGH |
| Web search (built-in) | WebSearch and WebFetch available in Cowork agent context. No MCP needed. | HIGH |
| File write to workspace | Cowork can read, create, edit, rename, organize files in designated workspace folder. | HIGH |
| Slash command framework | Plugin commands/ directory defines slash commands available in Cowork. | HIGH |
| Sub-agent dispatch | Cowork uses same agentic architecture as Claude Code. Sub-agent pattern supported. Parallel dispatch: needs validation. | MEDIUM (parallel is LOW) |
| Progress visibility | Tool uses shown as they happen during skills execution. Native, not custom. | MEDIUM |
| ZIP plugin install | Upload plugin interface in Cowork. Drag-and-drop, no terminal. | HIGH |
| Sandboxed Python environment (file creation) | Claude's code interpreter runs Python in a sandboxed env to generate DOCX/PDF. No user-side Python required. Available on Max/Team/Enterprise. | MEDIUM |

### What Requires MCP Servers (Optional Enhancements)

| Capability | MCP Server | Required? |
|------------|------------|-----------|
| Enhanced web search (Brave, Tavily, Exa) | Brave MCP, Tavily MCP, Exa MCP | No — degrades to built-in WebSearch |
| Local filesystem beyond workspace folder | Filesystem MCP, Desktop Commander MCP | No — Cowork workspace folder covers the use case |
| Document creation/editing (Word, Excel) | Document Edit MCP (alejandroBallesterosC) | Optional — alternative to built-in file builder |
| Terminal/shell access | Desktop Commander MCP | Not needed — no Python dependency requirement |

### What Claude Desktop Cannot Do (vs. Claude Code CLI)

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No Task tool (parallel subagent spawning is unconfirmed in Cowork) | 9-domain parallel execution may not be achievable; sequential fallback needed | Design orchestrator to work sequentially; test parallel dispatch during implementation |
| No Python venv/pip access | Python-based converters and markdown-pdf unavailable | Eliminated by design (native file reading + sandboxed file builder) |
| No git operations or CLI access | Cannot self-update, cannot write complex scripts | Not needed for this plugin's scope |
| No direct access to CLAUDE.md or Claude Code plugin system | Plugin system is Cowork's, not Claude Code's .claude-plugin format | Use Cowork plugin format (.claude-plugin/plugin.json + commands/ + skills/) |

---

## Competitor Feature Analysis

| Feature | dc-due-diligence (CLI, existing) | Raw Claude Conversation | dc-due-diligence-desktop (this plugin) |
|---------|-------------------------------|-------------------------|----------------------------------------|
| File ingestion | Python converters (PDF, Excel, Word, PowerPoint, Vision API) | Manual upload per file, no batch | Native reading of full folder via Cowork workspace |
| Orchestration | Task tool — 9 parallel agents | Single-threaded, manual | Sub-agents (parallel TBD, sequential confirmed) |
| Web research | WebSearch/WebFetch + optional MCP | Manual prompting | Same WebSearch/WebFetch + optional MCP |
| Output format | Markdown + PDF (Python markdown-pdf) | Markdown in conversation | Markdown to workspace (v1), Doc/PDF (v1.x) |
| Distribution | Git clone, terminal setup | N/A | ZIP upload via Cowork |
| User skill required | Terminal comfort, Python | None | None |
| Setup time | 10-30 min (git, venv, API key) | 0 | 5 min (ZIP upload) |
| Parallel execution | Yes (Task tool) | No | TBD — primary research question |
| Sharing | Export markdown files | Share conversation link | Share Cowork project (Team plan) |

---

## Sources

- [Create and edit files with Claude — Anthropic Help Center](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude) — native file creation/reading capabilities (HIGH confidence)
- [Claude can now create and edit files — Anthropic Blog](https://claude.com/blog/create-files) — Feb 2026 file builder release (HIGH confidence)
- [Getting started with Cowork — Anthropic Help Center](https://support.claude.com/en/articles/13345190-getting-started-with-cowork) — Cowork workspace, file access, plugin framework (HIGH confidence)
- [Customize Cowork with plugins — Anthropic Blog](https://claude.com/blog/cowork-plugins) — plugin structure, slash commands, sub-agents (HIGH confidence)
- [anthropics/knowledge-work-plugins — GitHub](https://github.com/anthropics/knowledge-work-plugins) — official plugin format examples, commands/skills structure (HIGH confidence)
- [One-click MCP server installation for Claude Desktop — Anthropic Engineering](https://www.anthropic.com/engineering/desktop-extensions) — .mcpb/.dxt distribution format (HIGH confidence)
- [What are projects? — Anthropic Help Center](https://support.claude.com/en/articles/9517075-what-are-projects) — Projects features, knowledge files, collaboration (HIGH confidence)
- [Claude Cowork Features & Workflow Guide — Geeky Gadgets, 2026](https://www.geeky-gadgets.com/claude-cowork-features-workspace/) — Cowork capabilities, macOS-only, local storage (MEDIUM confidence)
- [Can Claude Read Scanned PDFs? — DataStudios](https://www.datastudios.org/post/can-claude-read-scanned-pdfs-ocr-support-and-text-quality) — OCR limitations for scanned docs (MEDIUM confidence)
- [Create custom subagents — Claude Code Docs](https://code.claude.com/docs/en/sub-agents) — sub-agent capabilities and "no nested subagents" constraint (HIGH confidence for Claude Code; extrapolated to Cowork with MEDIUM confidence)
- [Claude Code Sub-Agents: Parallel vs Sequential Patterns — ClaudeFa.st](https://claudefa.st/blog/guide/agents/sub-agent-best-practices) — parallel vs sequential execution patterns (MEDIUM confidence)
- [Building Desktop Extensions with MCPB — Anthropic Help Center](https://support.claude.com/en/articles/12922929-building-desktop-extensions-with-mcpb) — .mcpb format details (HIGH confidence)
- [How to Install Plugins in Claude Cowork — MinDBees](https://www.mindbees.com/blog/install-plugins-claude-cowork/) — ZIP upload installation method (MEDIUM confidence)

---
*Feature research for: dc-due-diligence-desktop (Claude Desktop/Cowork plugin)*
*Researched: 2026-02-23*
