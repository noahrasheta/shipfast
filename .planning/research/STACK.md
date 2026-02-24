# Stack Research

**Domain:** Claude Desktop/Cowork plugin — complex multi-agent document analysis workflow
**Researched:** 2026-02-23
**Confidence:** MEDIUM (core platform capabilities verified via official Anthropic sources and recent 2026 articles; Cowork sub-agent parallelism nuances are LOW confidence due to limited first-party documentation on parallel dispatch limits)

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Claude Agent Skills (SKILL.md) | Open standard (Dec 2025) | Orchestration layer — defines multi-step workflow, triggers sub-agents, loads instructions | The canonical format for Cowork/Desktop workflow plugins. Replaces Claude Code's `.claude-plugin/` system for Desktop targets. Skills are folder + SKILL.md; Claude auto-discovers and triggers them by name/description match. Works in both Cowork and Claude Code. Confidence: HIGH (official Anthropic blog + anthropics/skills GitHub) |
| Claude Cowork | Jan 2026 research preview | Execution environment for non-technical users | Brings Claude Code-style agentic execution to the Desktop without terminal. File access, sub-agent dispatch, built-in web search, and native office file output — all zero-config for the end user. Available on Pro, Max, Team, Enterprise. Confidence: HIGH (official Anthropic launch + VentureBeat coverage) |
| Claude Desktop | Current (2.x) | Host application | Required for Cowork. Ships with built-in Node.js runtime, so Node-based MCP servers need zero user-side installation. Supports DXT/MCPB one-click extension installs. Confidence: HIGH (official Anthropic documentation) |
| MCPB Desktop Extensions (.mcpb) | Current (renamed from DXT) | Distribution format for non-technical users | ZIP archive containing MCP server + manifest.json. Double-click to install — no terminal, no JSON editing, no Node.js setup. Claude Desktop includes a built-in Node.js runtime, so Node MCP servers are dependency-free for the user. The only viable distribution mechanism that meets the "non-technical user" constraint. Confidence: HIGH (Anthropic engineering blog) |

### Built-in Capabilities (No Extra Configuration)

These are native to Claude Desktop/Cowork and require no MCP servers or separate setup:

| Capability | Details | Confidence |
|------------|---------|------------|
| Native PDF reading | Direct attachment or folder access up to 30MB/file, 20 files/chat. Pages processed as both text streams and images (handles scanned docs). | HIGH — Anthropic help center |
| Native DOCX/XLSX/PPTX reading | Supported file formats in Claude Desktop/Cowork. No Python converters required. | HIGH — Anthropic help center |
| Native DOCX/XLSX/PPTX/PDF output | Claude's built-in file creation skill (sandboxed code interpreter, no user Python). Available since Sep 2025. Max, Team, Enterprise GA; Pro rollout confirmed. | HIGH — official Claude blog + multiple sources |
| Built-in web search | Claude Desktop includes native WebSearch/WebFetch. Research preview with dynamic filtering. Available globally on all paid plans since May 2025. | HIGH — Anthropic blog |
| File workspace access | Cowork grants access to a user-designated folder. Claude reads, writes, creates files within it. No explicit folder-mounting MCP needed. | HIGH — official Cowork getting-started guide |
| Sub-agent dispatch | Cowork can spawn independent Claude instances (sub-agents) with their own context windows to parallelize work. Dispatch pattern triggered via natural language ("work on these in parallel") or structured skill instructions. | MEDIUM — confirmed in multiple community sources; exact parallelism limits not documented |
| Progress visibility | Tool uses shown in real time as Claude works. Native behavior — not something you build. | MEDIUM — multiple user reviews confirm; not in official docs |

### Supporting Libraries / MCP Servers (Optional, For Enhancement)

These are not required for core functionality but enhance specific capabilities when configured:

| Technology | Version/Source | Purpose | When to Use |
|------------|----------------|---------|-------------|
| Anthropic `docx` Skill | `anthropics/skills` GitHub (published Dec 2025) | Advanced DOCX creation: tracked changes, comments, formatting, letterheads | Use when default file creation skill doesn't produce sufficiently formatted output. This skill is what powers Claude's docx capability under the hood. |
| Anthropic `pdf` Skill | `anthropics/skills` GitHub (published Dec 2025) | PDF generation, merging, splitting, form-filling | Use when PDF output needs specific layout or multi-doc manipulation beyond basic generation. |
| Tavily MCP (`tavily-ai/tavily-mcp`) | Official, production-grade | Real-time web search with richer results than built-in | Use if built-in web search proves too shallow for domain research. Requires Tavily API key. Available via one-click Smithery install. Free tier: 1,000 searches/month. |
| Exa MCP (`exa-labs/exa-mcp-server`) | Official, free/open-source | Deep web search, company research | Use as Tavily alternative. Superior for niche/technical domain lookups. Requires Exa API key. |
| `@wonderwhy-er/desktop-commander` | v2+ (Jan 2026, 5.3k stars) | Terminal access, file system search, process management | NOT needed for this plugin — Cowork provides file access natively. Only relevant if advanced shell operations are needed (outside scope). |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| `modelcontextprotocol/mcpb` CLI | Build and package `.mcpb` extension files | Creates the ZIP archive from MCP server source + manifest.json. Renamed from `dxt` tooling. Run once by developer; user never needs it. |
| Claude Desktop (dev mode) | Test plugin locally | `claude --plugin-dir ./my-plugin` for Code; for Cowork skills, place skill folder in designated skills directory during development. |
| `anthropics/skills` repo | Reference implementations | Official Anthropic skills for docx, pdf, xlsx, pptx are source-available. Use as implementation reference for how document output is achieved. |

---

## Installation (For End User — Zero Terminal)

```
1. User downloads the .mcpb file (or ZIP) from shared link / Google Drive
2. User double-clicks the .mcpb file
3. Claude Desktop opens the extension manager — user clicks Install
4. Skills are discovered automatically when Cowork opens the plugin folder
5. User opens Cowork, points it at their data room folder
6. User types: "Run due diligence on the documents in this folder"
```

No terminal. No Node.js install. No npm. No Python. No JSON editing.

---

## Alternatives Considered

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| Claude Agent Skills (SKILL.md) | Claude Code Plugin system (.claude-plugin + agents/*.md) | The CLI plugin system uses the Task tool for sub-agent spawning — a Claude Code-only capability. SKILL.md is the cross-platform standard that works in both Cowork and Code. The CLI plugin format does not work in Claude Desktop/Cowork. |
| MCPB Desktop Extension | Manual claude_desktop_config.json editing | Config file editing requires terminal literacy. Non-technical users cannot do this reliably. MCPB is the only zero-friction distribution path for Claude Desktop. |
| MCPB Desktop Extension | Marketplace install (anthropic.com/extensions) | The Anthropic official extension marketplace is available, but publishing requires Anthropic review. For internal/team distribution, MCPB file sharing is faster. Both are viable final distribution paths. |
| Native Cowork sub-agents | External orchestration framework (claude-flow, n8n-mcp) | claude-flow and n8n require external setup and technical knowledge. Cowork's built-in sub-agent dispatch covers the parallelism need without additional tooling. Adding frameworks increases complexity without commensurate benefit for a non-technical user. |
| Anthropic docx/pdf Skills | docx-mcp (Rust standalone binary) | docx-mcp is promising (no Python, standalone binary) but requires compiling from source (Rust toolchain) or distributing a pre-compiled binary, which is more complex than using Anthropic's own built-in skills. Reserve as fallback only if native output quality is insufficient. |
| Anthropic docx/pdf Skills | Office-Word-MCP-Server (Python) | Requires Python — directly violates the no-Python constraint. |
| Anthropic docx/pdf Skills | mcp-md-pdf (Python/Node) | Requires markdown-to-PDF conversion pipeline. Native skill produces better-formatted output and is already bundled. |
| Built-in web search | Tavily MCP (mandatory) | Built-in web search covers most domain research needs. Tavily is an enhancement, not a requirement. Making Tavily mandatory would require API key setup, which breaks non-technical UX. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Python-based MCP servers (Office-Word-MCP-Server, mcp-md-pdf, Document MCP by alejandroballesteros) | All require Python 3.10+ and pip installation — directly violates the no-Python constraint. Non-technical user cannot set up a Python environment. | Anthropic's built-in docx/pdf skills via native code interpreter, or docx-mcp (Rust binary) as fallback |
| Claude Code Task tool / sub-agent architecture from CLI plugin | Task tool spawning is Claude Code-only. It does not function in Claude Desktop/Cowork context. Designing for it will produce a plugin that fails silently in Cowork. | Claude Cowork's native sub-agent dispatch via skill instructions ("work on these in parallel") |
| `.claude-plugin/` manifest + `agents/*.md` format (CLI plugin system) | This system was designed for Claude Code CLI only. Claude Desktop does not support the plugin manifest format or the Task-tool-based orchestration it relies on. Attempting to reuse dc-due-diligence's existing architecture directly will not work in Desktop. | Agent Skills (SKILL.md) format for Cowork; MCP servers for tool capabilities |
| Manual `claude_desktop_config.json` editing as primary install method | Requires finding and editing a hidden JSON config file in the OS application support directory — a terminal/developer action. Non-technical users cannot do this reliably. | MCPB Desktop Extensions for all MCP server distribution |
| Desktop Commander MCP for file access | Adds unnecessary terminal/process execution capability that's a security concern. Cowork natively handles file workspace access — Desktop Commander is overkill. | Native Cowork workspace folder access |
| n8n-mcp, claude-flow, or other external orchestration frameworks | Require Node.js/Docker setup and developer knowledge. Add significant operational complexity. Cowork handles orchestration natively. | Cowork's built-in agentic orchestration |

---

## Stack Patterns by Variant

**If parallel sub-agent execution in Cowork proves limited (fallback):**
- Design workflow as sequential wave execution: 9 domain research agents run one at a time, each writing their report to disk, then Risk Assessment reads all reports, then Executive Summary reads all reports
- This eliminates parallelism dependency entirely
- Trade-off: ~9x slower than CLI version (minutes vs. seconds)
- Because: Even if Cowork sub-agent dispatch has constraints, sequential execution is guaranteed to work and produces the same outputs

**If Cowork sub-agent parallelism is confirmed to work as expected:**
- Design SKILL.md to explicitly request parallel dispatch: "Spawn 9 sub-agents simultaneously, one per domain. Each sub-agent: [instructions]..."
- Include synchronization instruction: "After all 9 sub-agents complete, synthesize findings in a Risk Assessment"
- This mirrors the CLI plugin's Wave 1 architecture
- Because: Reduces wall-clock time from ~45 minutes (sequential) to ~5-10 minutes (parallel)

**If built-in web search is insufficient for domain research depth:**
- Add Tavily or Exa MCP to the MCPB package
- Require user to obtain and enter API key during installation (MCPB manifest supports secure key storage via OS keychain)
- Because: Tavily provides real-time crawling + extraction; Exa provides high-quality academic/technical source retrieval

**If native file creation skill produces insufficient output formatting:**
- Install Anthropic `docx` and `pdf` skills from `anthropics/skills`
- These are the same skills that power Claude's native document creation — using them directly gives more control over output structure
- Because: The published skills expose more formatting controls than the implicit built-in behavior

---

## Version Compatibility

| Component | Compatible With | Notes |
|-----------|-----------------|-------|
| Agent Skills (SKILL.md open standard) | Claude Code (CLI), Claude Desktop/Cowork, OpenAI Codex CLI | Published as cross-platform open standard Dec 18, 2025. Works in both target environments. |
| MCPB Desktop Extensions | Claude Desktop 2.x+, Windows + macOS | Renamed from DXT. Built-in Node.js runtime handles Node-based MCP servers. Python and binary MCP servers also supported. |
| Cowork sub-agents | Claude Pro/Max/Team/Enterprise (Jan 2026+) | Not available on free tier. Research preview status — may change. |
| Built-in file creation (docx/pdf/xlsx/pptx) | Max, Team, Enterprise GA; Pro in rollout (Sep 2025+) | All paid plans should have it by Q1 2026. Free tier TBD. |
| Built-in web search | All paid plans, globally (May 2025+) | Free tier also available. |

---

## Critical Architecture Decision: Skills vs. Plugins

The `dc-due-diligence` CLI plugin uses the **Claude Code plugin architecture** (`.claude-plugin/plugin.json` manifest + `agents/*.md` agent files + `skills/*/SKILL.md` orchestrator). This format is **Claude Code (terminal) exclusive**.

For Claude Desktop/Cowork, the correct format is the **Agent Skills specification** (`SKILL.md` + optional scripts/references/assets). This is the architecture to adopt for `dc-due-diligence-desktop`.

Key differences:

| Aspect | CLI Plugin (existing) | Desktop Skill (new) |
|--------|----------------------|---------------------|
| Entry point | `skills/due-diligence/SKILL.md` via `/due-diligence` slash command | `SKILL.md` in skill folder, auto-discovered by name match |
| Sub-agent spawning | `Task` tool (Claude Code native) | Cowork sub-agent dispatch via instructions |
| File reading | Python converters (pdfplumber, openpyxl, etc.) | Native Cowork file access (no conversion) |
| Document output | `markdown-pdf` Python library | Native docx/pdf skills (sandboxed code interpreter) |
| Distribution | Git clone / `claude --plugin-dir` | MCPB double-click install |
| Target user | Developer with terminal | Non-technical knowledge worker |

The Desktop version is a ground-up rewrite using the Skills architecture, not a port of the plugin architecture.

---

## Sources

- [Introducing Agent Skills | Claude](https://www.anthropic.com/news/skills) — Agent Skills official announcement (Oct 2025), skill format, SKILL.md spec. Confidence: HIGH
- [Agent Skills - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — Official specification for SKILL.md format, frontmatter fields, trigger behavior. Confidence: HIGH
- [anthropics/skills GitHub](https://github.com/anthropics/skills) — Official skill implementations including docx, pdf, pptx, xlsx. Source-available reference. Confidence: HIGH
- [Introducing Cowork | Claude](https://claude.com/blog/cowork-research-preview) — Official Cowork launch blog (Jan 2026), capabilities, file access, sub-agent architecture. Confidence: HIGH
- [Getting started with Cowork | Claude Help Center](https://support.claude.com/en/articles/13345190-getting-started-with-cowork) — Official user guide: folder access, plan requirements, available skills. Confidence: HIGH
- [One-click MCP server installation for Claude Desktop | Anthropic Engineering](https://www.anthropic.com/engineering/desktop-extensions) — MCPB/DXT format spec, manifest.json structure, built-in Node.js runtime, installation flow. Confidence: HIGH
- [modelcontextprotocol/mcpb GitHub](https://github.com/modelcontextprotocol/mcpb) — Official MCPB CLI tooling. Confidence: HIGH
- [Claude can now create and edit files | Claude Blog](https://claude.com/blog/create-files) — Official announcement of docx/pdf/xlsx/pptx output capability (Sep 2025). Confidence: HIGH
- [Create and edit files with Claude | Claude Help Center](https://support.claude.com/en/articles/12111783-create-and-edit-files-with-claude) — File creation capabilities, supported formats, plan availability. Confidence: HIGH
- [Anthropic launches Cowork | VentureBeat](https://venturebeat.com/technology/anthropic-launches-cowork-a-claude-desktop-agent-that-works-in-your-files-no) — Third-party launch coverage confirming capabilities. Confidence: MEDIUM
- [Claude Cowork Tutorial | DataCamp](https://www.datacamp.com/tutorial/claude-cowork-tutorial) — Detailed usage guide including skills behavior, docx/pdf output, sub-agent coordination. Confidence: MEDIUM
- [How to Deploy MCP Servers Using .dxt Extensions | Glama](https://glama.ai/blog/2025-07-11-getting-started-with-mcp-desktop-extensions-dxt-in-claude-desktop) — DXT/MCPB structure, installation flow for non-technical users. Confidence: MEDIUM
- [docx-mcp GitHub](https://github.com/hongkongkiwi/docx-mcp) — Rust-based DOCX MCP server (standalone binary, no Python). Fallback option. Confidence: MEDIUM (single source, not officially vetted)
- [tavily-ai/tavily-mcp GitHub](https://github.com/tavily-ai/tavily-mcp) — Tavily official MCP server for enhanced web search. Confidence: HIGH
- [Exa MCP Server](https://exa.ai/mcp) — Exa official MCP server for deep web search. Confidence: HIGH
- [Getting started with Cowork | Claude Help Center](https://support.claude.com/en/articles/13345190-getting-started-with-cowork) — Sub-agent parallel dispatch behavior ("when task has independent parts, Claude spins up multiple workers"). Confidence: MEDIUM (help center confirms, no hard limit docs found)

---

*Stack research for: dc-due-diligence-desktop (Claude Desktop/Cowork plugin)*
*Researched: 2026-02-23*
