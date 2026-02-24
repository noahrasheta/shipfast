# Architecture Research

**Domain:** Claude Desktop/Cowork multi-agent analysis plugin
**Researched:** 2026-02-23
**Confidence:** HIGH (core findings verified via official Anthropic sources and reverse-engineering analysis)

---

## The Central Architectural Insight

**Cowork IS Claude Code, running inside a local Ubuntu VM.**

The single most important architectural discovery: Claude Cowork is not a different system requiring a fundamentally different architecture. It runs the Claude Code CLI inside a sandboxed Ubuntu 22.04 LTS virtual machine on the user's Mac. This means:

- The **Task tool is available** — parallel agent spawning works exactly as in the CLI version
- **Python is preinstalled** — the VM includes Python, Node.js, git, LibreOffice, Chromium, and standard Unix utilities
- **File access is via mounted folder** — user grants access to a folder; it's mounted bidirectionally into the VM
- **MCP servers pass through** — MCP servers configured in Claude Desktop are dynamically forwarded to the VM

The "no Python dependency" requirement means users don't manage Python themselves — not that Python is unavailable. In Cowork, all tooling runs inside the VM without user intervention.

**Source:** pvieito.com reverse-engineering analysis (HIGH confidence — matches official Anthropic documentation)

---

## Standard Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     Claude Desktop App (macOS)                    │
│  ┌──────────────────────┐    ┌──────────────────────────────────┐ │
│  │   Chat / Projects    │    │          Cowork Tab              │ │
│  │  (conversation mode) │    │    (agentic task mode)           │ │
│  └──────────────────────┘    └────────────────┬─────────────────┘ │
│                                               │ VirtioFS mount     │
│  ┌─────────────────────────────────────────────▼─────────────────┐ │
│  │                Ubuntu 22.04 LTS VM (ARM64)                    │ │
│  │  ┌─────────────────────────────────────────────────────────┐  │ │
│  │  │                  Claude Code CLI                         │  │ │
│  │  │  ┌────────────┐  ┌──────────┐  ┌──────────────────────┐ │  │ │
│  │  │  │ Task tool  │  │  Agents  │  │  Bash / Python / Node│ │  │ │
│  │  │  │ (parallel  │  │  (.md)   │  │  (preinstalled)      │ │  │ │
│  │  │  │  spawning) │  │          │  │                      │ │  │ │
│  │  │  └────────────┘  └──────────┘  └──────────────────────┘ │  │ │
│  │  └─────────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────────┐  │ │
│  │  │          Mounted User Folder (bidirectional)             │  │ │
│  │  │   data-room/ docs/ → research/ → EXECUTIVE_SUMMARY.docx │  │ │
│  │  └─────────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │        MCP Servers (Desktop-configured, passed to VM)       │   │
│  │  [Office-Word-MCP]  [Document-Edit-MCP]  [Filesystem-MCP]  │   │
│  └────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| Cowork Tab | Receives user task description, shows progress, delivers results | Claude Desktop UI — no build needed |
| Ubuntu VM | Isolated execution environment with preinstalled toolchain | Managed by Anthropic, always present for Cowork users |
| Claude Code CLI (in VM) | Executes skill, spawns agents, runs bash, reads/writes files | Same engine as existing dc-due-diligence |
| Plugin (installed) | Provides skill, agent definitions, sub-agent prompts | Markdown + JSON files — the thing we build |
| Mounted folder | Bidirectional file access — user's data room in, reports out | User grants access on task start |
| MCP servers | Extended capabilities: Word/PDF output generation | Configured once in Claude Desktop; optional |

---

## Plugin Architecture for Cowork

Cowork plugins use the same structure as Claude Code plugins, with one addition: a `sub-agents/` directory. Based on Anthropic's knowledge-work-plugins open-source reference:

```
dc-due-diligence-desktop/
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest (name, version, author)
├── .mcp.json                     # MCP server connections (Office-Word MCP, etc.)
├── skills/
│   └── due-diligence/
│       └── SKILL.md              # Orchestrator — same role as CLI version
├── agents/                       # Sub-agent definitions (same as CLI .claude/agents/)
│   ├── power-agent.md
│   ├── connectivity-agent.md
│   ├── water-cooling-agent.md
│   ├── land-zoning-agent.md
│   ├── ownership-agent.md
│   ├── environmental-agent.md
│   ├── commercials-agent.md
│   ├── natural-gas-agent.md
│   ├── market-comparables-agent.md
│   ├── risk-assessment-agent.md
│   ├── executive-summary-agent.md
│   └── client-summary-agent.md
├── commands/
│   └── due-diligence.md          # Slash command: /due-diligence
├── templates/
│   ├── agent-output-template.md  # Same as CLI version
│   └── scoring-rubric.md        # Same as CLI version
└── references/
    └── ...                       # Domain reference materials
```

### Key Difference from CLI Version

| Aspect | CLI Version (dc-due-diligence) | Desktop Version (dc-due-diligence-desktop) |
|--------|-------------------------------|---------------------------------------------|
| Entry point | `/due-diligence <path>` skill command | `/due-diligence` slash command or natural language |
| Document reading | Python converters (pdfplumber, openpyxl, etc.) | VM reads files natively; Claude reads via Bash/Read tools |
| Agent spawning | Task tool (Claude Code) | Task tool (Claude Code CLI inside VM) — SAME |
| Parallelism | Wave 1: 9 agents in parallel | Wave 1: 9 agents in parallel — SAME |
| Output format | Markdown + Python PDF generation | Word (.docx) via Office-Word MCP or LibreOffice in VM |
| Python dependency | User must set up venv | VM has Python preinstalled — zero user setup |
| Distribution | `/plugin install` via Claude Code CLI | In-app marketplace one-click install |

---

## Data Flow

### Full Pipeline (Desktop Version)

```
[User opens Cowork tab]
    ↓
[User: "run due diligence on ~/DataRoom/Westfield-DC"]
    ↓
[Cowork creates plan, user approves]
    ↓
[Claude Code CLI starts inside VM]
    ↓
[SKILL.md Orchestrator activates]
    ↓
[Phase 1: Folder Discovery]
    → Bash: find all PDF/Word/Excel/PowerPoint/image files
    → Claude reads files directly (Read tool, Bash cat, or via MCP doc reader)
    → No conversion step needed — VM tools handle binary files natively
    ↓
[Phase 2: Wave 1 — 9 Domain Agents in PARALLEL via Task tool]
    ┌──────────┬──────────┬──────────┬──────────┬──────────┐
    │ Power    │ Conn.    │ Water    │ Land     │ Ownership│
    │ agent    │ agent    │ agent    │ agent    │ agent    │
    └────┬─────┴────┬─────┴────┬─────┴────┬─────┴────┬─────┘
    ┌────┴─────┬────┴─────┬────┘         │          │
    │ Environ. │ Commerc. │ Nat.Gas      │ Mkt.Comp │
    │ agent    │ agent    │ agent        │ agent    │
    └──────────┴──────────┴──────────────┴──────────┘
    Each reads from mounted folder, does web research, writes research/*.md
    ↓ (all 9 complete)
[Phase 3: Wave 2 — Risk Assessment Agent (sequential)]
    → Reads all 9 domain reports
    → Writes research/risk-assessment-report.md
    ↓
[Phase 4: Wave 3 — Executive Summary Agent (sequential)]
    → Reads all 10 reports, applies scoring rubric
    → Writes EXECUTIVE_SUMMARY.md
    ↓
[Phase 5: Wave 4 — Client Summary Agent (sequential)]
    → Writes CLIENT_SUMMARY.md
    ↓
[Phase 6: Output Generation]
    Option A: Office-Word MCP converts markdown → .docx + .pdf
    Option B: LibreOffice in VM: soffice --headless --convert-to docx *.md
    Option C: Python-docx in VM (preinstalled Python): generates .docx
    ↓
[Outputs delivered to user's mounted folder]
    EXECUTIVE_SUMMARY.docx / .pdf
    CLIENT_SUMMARY.docx / .pdf
```

### Document Reading Flow (No Python Converters Needed)

```
User Folder (mounted into VM)
    ↓
Orchestrator runs: find . -name "*.pdf" -o -name "*.docx" etc.
    ↓
For each file:
    ├── PDF (text):  Read tool or `pdftotext` (preinstalled in VM via LibreOffice)
    ├── PDF (scan):  LibreOffice renders → Claude vision via Bash+API call
    ├── Word (.docx): `docx2txt` or python-docx (Python preinstalled in VM)
    ├── Excel:       `ssconvert` (LibreOffice) or python openpyxl (Python in VM)
    ├── PowerPoint:  LibreOffice converts to text
    └── Images:      Claude vision API (Anthropic API available in VM)
    ↓
Content passed to agents as text in their prompts
    ↓
No _converted/ manifest needed — agents work from shared folder directly
```

---

## Architectural Patterns

### Pattern 1: Sequential Wave Orchestration (Same as CLI)

**What:** Skill orchestrates multiple waves of agents. Wave 1 runs in parallel via Task tool. Each subsequent wave is sequential, depending on prior wave outputs.

**When to use:** When domain agents are independent but synthesis requires all inputs.

**Implementation in Cowork:** Identical to CLI version — SKILL.md instructs Task tool to launch agents, then waits, then launches synthesis agents.

```markdown
<!-- In SKILL.md — Phase: Wave 1 -->
Launch all 9 domain research agents in parallel using the Task tool.
Each agent should:
1. Read all documents in ${folder_path}
2. Conduct web research on their domain
3. Write their report to ${folder_path}/research/${domain}-report.md

Do not proceed to Wave 2 until all 9 agents have written their reports.
```

### Pattern 2: Plugin Slash Command Entry Point

**What:** User triggers workflow via `/due-diligence` slash command or natural language in Cowork tasks mode.

**When to use:** For a defined, repeatable workflow.

**Implementation:**

```markdown
<!-- In commands/due-diligence.md -->
---
name: due-diligence
description: Run full 9-domain data center due diligence analysis
---
Activate the due-diligence skill. Ask the user for the data room folder path.
```

### Pattern 3: VM-Native Document Processing

**What:** Use preinstalled VM tools (LibreOffice, Python, pdftotext) instead of custom Python converters for document reading.

**When to use:** Replacing the CLI version's Python converter pipeline.

**Trade-offs:**
- Simpler setup (no Python venv)
- Depends on VM toolchain being stable
- LibreOffice for Excel may lose some formatting vs openpyxl

**Example:**

```bash
# Read PDF (LibreOffice pdftotext equivalent)
pdftotext document.pdf - 2>/dev/null || python3 -c "
import subprocess
result = subprocess.run(['python3', '-m', 'pypdf'], ...)
"

# Convert Excel to CSV for reading
python3 -c "
import openpyxl
wb = openpyxl.load_workbook('data.xlsx')
# ... extract to text
"
```

### Pattern 4: MCP-Based Document Output

**What:** Use an MCP server configured in `.mcp.json` to generate Word/PDF output without custom Python code.

**When to use:** For clean .docx output without managing Office document libraries.

**Recommended MCP server:** `Office-Word-MCP-Server` (GongRzhe) or `document-edit-mcp` (alejandroBallesterosC).

**Trade-offs:**
- Cleaner architecture — no output Python scripts to maintain
- Requires user to have MCP configured (or bundled as Desktop Extension)
- Fallback: LibreOffice in VM can also produce .docx without MCP

### Pattern 5: Graceful Degradation on Missing Documents

**What:** Domain agents proceed with web research even if their specific domain has no broker documents.

**When to use:** Always — data rooms are always incomplete.

**Same as CLI version:** agents are instructed to note missing documents and rely on web research for gaps.

---

## Anti-Patterns

### Anti-Pattern 1: Assuming Desktop ≠ Task Tool

**What people do:** Assume Claude Desktop can't spawn parallel agents, design a sequential-only architecture.

**Why it's wrong:** Cowork runs Claude Code CLI inside a VM. The Task tool is fully available. A fully sequential 9-agent workflow takes significantly longer and delivers the same output.

**Do this instead:** Use the same parallel Wave 1 pattern as the CLI version. It works in Cowork.

### Anti-Pattern 2: Rebuilding Python Converters for Desktop

**What people do:** Port the full Python converter pipeline into the Desktop plugin.

**Why it's wrong:** The VM has Python, LibreOffice, and pdftotext preinstalled. The user never sees this. There's no venv to set up. A simpler bash-based or lightweight Python approach inside the skill works without a full converter framework.

**Do this instead:** Use VM-native tools for document reading. Reserve custom Python only where VM tools are insufficient (e.g., scanned PDFs requiring vision).

### Anti-Pattern 3: Project Instructions as Orchestrator

**What people do:** Put the entire 4-wave workflow in Claude Desktop project instructions, expecting it to run automatically.

**Why it's wrong:** Project instructions are persistent context, not workflow automation. They don't spawn agents or execute code. Cowork's agentic capability comes from the Claude Code CLI + Task tool inside the VM.

**Do this instead:** Use a Cowork Plugin with a SKILL.md orchestrator. Project instructions supplement but don't replace the skill.

### Anti-Pattern 4: Hardcoding Absolute Paths

**What people do:** Reference file paths as `/home/user/Documents/...` inside agent prompts.

**Why it's wrong:** The VM mounts the user's folder at a different path than their Mac filesystem path. The Cowork UI does path translation, but agents working inside the VM see the VM mount path.

**Do this instead:** Use `${CLAUDE_PLUGIN_ROOT}` for plugin-internal files. Pass the data room path as a parameter through the skill invocation. Use relative paths where possible.

---

## Build Order and Dependencies

The dependency chain determines build order:

```
1. Plugin scaffold + manifest
       ↓ (required before anything works)
2. Slash command entry point (/due-diligence)
       ↓ (required before skill is accessible)
3. SKILL.md orchestrator (Phase 1: validation + document inventory)
       ↓ (required before agents make sense)
4. Domain agent definitions (9 agents)
       ↓ (must exist before Wave 1 orchestration)
5. Synthesis agents (Risk Assessment, Executive Summary, Client Summary)
       ↓ (depend on domain agents)
6. Output generation (Word/PDF)
       ↓ (depends on synthesis agents producing markdown)
7. MCP server configuration (.mcp.json)
       ↓ (can add after core workflow works)
8. Distribution packaging (Desktop Extension .mcpb or marketplace)
```

### Phase Build Recommendations

**Phase 1 — Foundation:**
- Plugin manifest + slash command
- SKILL.md with document inventory only (no agents yet)
- Validate that Cowork can pick up the plugin and read files from a mounted folder

**Phase 2 — Agent Skeleton:**
- One domain agent end-to-end (Power agent)
- Validate Task tool spawning, file writing, web research all work inside VM
- This proves the full pipeline before building remaining 8 agents

**Phase 3 — Full Wave 1:**
- Remaining 8 domain agents (can be copied from CLI version with path adjustments)
- Validate parallel execution

**Phase 4 — Synthesis and Output:**
- Risk Assessment, Executive Summary, Client Summary agents
- Output generation (choose: MCP vs LibreOffice vs Python-docx in VM)

**Phase 5 — Polish and Distribution:**
- Document reading robustness (edge cases: password-protected PDFs, corrupted files)
- MCP configuration bundled for easier setup
- Desktop Extension packaging if distributing to non-technical users

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Anthropic API (web search) | Built-in to Claude Code in VM — no config | Same as CLI version |
| Exa / Firecrawl / Tavily MCP | Passed through from Desktop MCP config to VM | Optional; agents fall back to built-in web tools |
| Office-Word MCP | Configured in .mcp.json; passed to VM | Recommended for clean .docx output |
| LibreOffice | Preinstalled in VM | Fallback for PDF/docx conversion without MCP |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| SKILL.md ↔ Domain Agents | Task tool spawning; shared filesystem | Same as CLI version |
| Domain Agents ↔ Synthesis Agents | Filesystem (research/*.md files) | Same as CLI version |
| Synthesis Agents ↔ Output Layer | Filesystem (EXECUTIVE_SUMMARY.md, CLIENT_SUMMARY.md) | CLI used Python; Desktop uses MCP or LibreOffice |
| VM ↔ User Folder | VirtioFS bidirectional mount | Files appear on user's Mac in real time |
| Plugin ↔ MCP Servers | .mcp.json declares servers; VM receives them | Requires user to have MCP installed OR bundle as extension |

---

## Scaling Considerations

This plugin runs entirely locally — scaling is a non-issue for typical use. The relevant concern is execution time:

| Concern | Approach |
|---------|----------|
| 9 parallel agents × web research | Task tool parallelism handles this; same as CLI — no change needed |
| Large data rooms (100+ documents) | Skill should inventory and summarize rather than embed full text; pass summaries to agents |
| Slow document reading in VM | LibreOffice is slower than pdfplumber — add status messages; not a blocking concern |
| Output file size | Word documents are larger than markdown PDFs; not a practical concern |

---

## Sources

- [Getting started with Cowork | Claude Help Center](https://support.claude.com/en/articles/13345190-getting-started-with-cowork) — MEDIUM confidence (official, high level)
- [Inside Claude Cowork: How Anthropic Runs Claude Code in a Local VM on Your Mac](https://pvieito.com/2026/01/inside-claude-cowork) — HIGH confidence (reverse engineering, confirmed by community)
- [What Is Claude Cowork? VM, Plugins, and SaaS Impact](https://www.marc0.dev/en/blog/claude-cowork-engineering-deep-dive-vm-plugins-saaspocalypse-1770479461092) — MEDIUM confidence (engineering deep dive, matches official details)
- [Claude Cowork Architecture | Tensorlake](https://www.tensorlake.ai/blog/claude-cowork-architecture-overview) — MEDIUM confidence (technical overview)
- [Customize Cowork with plugins | Claude](https://claude.com/blog/cowork-plugins) — HIGH confidence (official Anthropic blog)
- [GitHub - anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) — HIGH confidence (official reference plugin structure)
- [Cowork: Claude Code Power for Knowledge Work](https://claude.com/product/cowork) — HIGH confidence (official Anthropic product page)
- [One-click MCP server installation for Claude Desktop](https://www.anthropic.com/engineering/desktop-extensions) — HIGH confidence (official Anthropic engineering blog)
- [Document Operations MCP Server](https://playbooks.com/mcp/alejandroballesteros-document-operations) — MEDIUM confidence (third-party MCP)
- [Office-Word-MCP-Server](https://github.com/GongRzhe/Office-Word-MCP-Server) — MEDIUM confidence (third-party MCP, actively maintained)

---

*Architecture research for: dc-due-diligence-desktop (Claude Desktop/Cowork plugin)*
*Researched: 2026-02-23*
