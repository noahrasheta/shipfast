# dc-due-diligence-desktop

## What This Is

A Claude Desktop/Cowork-native version of the data center due diligence plugin. Designed for non-technical team members who use Claude Desktop daily but aren't comfortable in a terminal. The user opens a folder of data room documents in Claude Desktop, initiates the workflow, and receives scored due diligence reports in doc/PDF format — same analytical rigor as the CLI version, friendlier interface.

## Core Value

A non-technical co-worker can run a full 9-domain data center due diligence analysis from Claude Desktop without ever touching a terminal, and get results in an editable document format.

## Requirements

### Validated

<!-- Capabilities proven in dc-due-diligence (CLI version) that this plugin must replicate -->

- ✓ 9-domain parallel research analysis (Power, Connectivity, Water/Cooling, Land/Zoning, Ownership, Environmental, Commercials, Natural Gas, Market Comparables) — existing
- ✓ External web research per domain agent — existing
- ✓ Cross-domain risk assessment synthesis — existing
- ✓ Executive summary with Pursue/Proceed with Caution/Pass verdict — existing
- ✓ Client-facing summary (no internal scoring language) — existing
- ✓ Graceful handling of incomplete data rooms (missing domains still analyzed) — existing
- ✓ Document safety protocol (embedded instruction detection) — existing
- ✓ Scoring rubric with normalized category scores — existing

### Active

<!-- New requirements for the Desktop version -->

- [ ] Native file reading — use Claude Desktop's built-in PDF, Excel, Word, PowerPoint, image reading instead of Python converters
- [ ] Doc/PDF output — final reports in editable document format (Word/PDF), not markdown
- [ ] One-command UX — user opens folder, says "run due diligence" or similar, workflow runs to completion
- [ ] Claude Desktop distribution — installable without terminal (MCP config, project template, or zip package)
- [ ] Cowork compatibility — works within Claude Cowork for team collaboration
- [ ] No Python dependency — eliminate the Python venv/converter requirement entirely
- [ ] Agent orchestration via Desktop — replicate multi-agent workflow within Claude Desktop's capabilities (MCP tools, Projects, or equivalent)
- [ ] Web research via Desktop — leverage Claude Desktop's web search capabilities or MCP-based search tools
- [ ] Progress visibility — user can see workflow progress as it runs

### Out of Scope

- Modifying the existing `dc-due-diligence` CLI plugin — that stays as-is
- Claude Code CLI compatibility — this plugin targets Desktop exclusively
- Real-time collaboration during analysis — one person runs it, shares results after
- Custom scoring rubric editing from Desktop UI — use the same rubric as CLI version
- Mobile or web-only access — Mac Claude Desktop app only

## Context

**Existing system:** The `dc-due-diligence` plugin in this marketplace is a proven Claude Code CLI plugin with 12 agents, Python document converters, and a 4-wave execution pipeline. It works well but requires terminal comfort.

**Target user:** A co-worker who uses Claude Desktop daily, is comfortable with the app, but won't use a terminal. He processes data center opportunities and needs the same analytical output.

**Technical landscape (needs research):**
- Claude Desktop supports MCP servers for custom tool integration
- Claude Desktop can natively read PDFs, images, and potentially other document types
- Extensions like Desktop Commander exist for file system operations
- Claude Desktop Projects allow custom instructions
- Cowork enables team collaboration on projects
- The exact capabilities and limitations for orchestrating complex multi-agent workflows in Desktop are unknown — this is the primary technical risk

**Current CLI architecture to adapt:**
- Wave 1: 9 domain agents in parallel (Task tool spawning)
- Wave 2: Risk Assessment agent (sequential)
- Wave 3: Executive Summary generator (sequential)
- Wave 4: Client Summary agent (sequential)
- Python converters: PDF (pdfplumber), Excel (openpyxl), Word (python-docx), PowerPoint (python-pptx), Vision (Anthropic API)
- Output: Markdown reports + PDF generation via markdown-pdf

**Key adaptation challenges:**
- Claude Desktop may not support Task tool / parallel subagent spawning
- Workflow may need to be sequential rather than parallel
- File reading mechanism is fundamentally different (native vs Python converters)
- Output generation needs doc/PDF capability without Python libraries
- Distribution mechanism for non-technical users is unknown

## Constraints

- **Platform**: Mac Claude Desktop app — must work without any terminal interaction
- **User skill level**: Non-technical — installation and usage must be straightforward
- **Feature parity**: Must cover all 9 domains + risk assessment + executive summary + client summary
- **No Python**: Cannot rely on Python venv or pip — user won't set that up
- **Distribution**: Must be shareable (zip, shared drive, or marketplace) without requiring git

## Key Decisions

<!-- Decisions that constrain future work. Add throughout project lifecycle. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Separate plugin, not fork of existing | CLI version works well for Noah; Desktop version has fundamentally different architecture | — Pending |
| Name: dc-due-diligence-desktop | Clear distinction from dc-due-diligence (CLI) | — Pending |
| Doc/PDF output instead of markdown | Co-worker wants editable, readable documents | — Pending |
| No Python dependency | Non-technical user can't manage venvs or pip | — Pending |
| Architecture approach (MCP vs Project vs hybrid) | Needs research into Claude Desktop capabilities | — Pending |

---
*Last updated: 2026-02-23 after initialization*
