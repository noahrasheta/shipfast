# Phase 1: Foundation and Validation - Research

**Researched:** 2026-02-23
**Domain:** Cowork plugin scaffolding, ZIP distribution, slash commands, parallel sub-agent dispatch
**Confidence:** MEDIUM-HIGH (plugin format HIGH from official sources; parallel dispatch UNRESOLVED — empirical test required)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

None — user indicated no discussion needed for this phase. All implementation details are at Claude's discretion.

### Claude's Discretion

- Slash command UX (progress messages, data room preview, tone of output)
- Plugin identity (name, description text in Cowork's plugin list)
- File discovery output format (how workspace files are listed to user)
- Validation reporting (how parallel vs sequential test results are recorded)
- Plugin directory structure and file organization
- Parallel dispatch smoke test design
- Sequential fallback implementation approach

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-01 | Plugin uses correct Cowork format (.claude-plugin/plugin.json, commands/, skills/) and activates when uploaded | Plugin format fully documented; exact frontmatter fields confirmed from official reference |
| INFRA-02 | Plugin distributable as ZIP file that installs via drag-and-drop in Cowork — no terminal required | ZIP upload mechanism confirmed via official Anthropic help; install flow documented |
| INFRA-03 | User can type `/due-diligence` to trigger the full analysis workflow | Command file format confirmed from knowledge-work-plugins reference; slash command invocation pattern documented |
| PLAT-01 | Validate whether Cowork supports parallel sub-agent dispatch (Task tool equivalent) — document result | This is the empirical question — cannot be answered by reading. Smoke test design documented in Architecture Patterns. |
| PLAT-02 | Sequential execution fallback works correctly for all 9 domain agents if parallel is unavailable | Sequential orchestration is the default for Phase 1; pattern documented |
| PLAT-03 | Workflow handles Cowork session interruptions by writing intermediate results to disk after each agent completes | Disk-write pattern documented; workspace folder is bidirectional — files written survive session end |
</phase_requirements>

---

## Summary

Phase 1 has two distinct sub-problems: (1) scaffolding the correct Cowork plugin format so the plugin installs via ZIP and activates a slash command, and (2) answering empirically whether Cowork's orchestration layer supports parallel sub-agent dispatch. The first sub-problem has a clear, well-documented answer — the plugin format is confirmed against Anthropic's official `knowledge-work-plugins` GitHub reference. The second sub-problem cannot be resolved by research and must be answered by running a minimal smoke test inside Cowork.

The Cowork plugin format uses `plugin.json` (same schema as CLI plugins), a `commands/` directory for slash commands (different from CLI skill invocation), and a `skills/` directory for auto-triggered domain knowledge. Commands use YAML frontmatter with `description` and `argument-hint` fields. Skills use YAML frontmatter with `name` and `description` fields — only 100 tokens at startup, full SKILL.md loaded on trigger. The plugin is distributed as a ZIP archive uploaded via Cowork's plugin interface.

The parallel dispatch question is the load-bearing architectural unknown for all subsequent phases. Architecture research from `pvieito.com` reverse-engineering claims Cowork runs Claude Code CLI inside an Ubuntu 22.04 VM, which would make the Task tool available. Pitfalls research disputes this, citing multiple community sources that classify the Task tool as CLI-only. The conflict cannot be resolved from documentation alone. Phase 1 Plan 01-03 must build a two-agent smoke test and observe whether they run concurrently. The Phase 3 Wave 1 architecture depends on the result.

**Primary recommendation:** Scaffold the correct Cowork format first (Plans 01-01 and 01-02), then run the parallel dispatch smoke test (Plan 01-03). Build the orchestrator to work correctly in sequential mode regardless of the smoke test result — parallel dispatch is a performance upgrade, not a correctness requirement.

---

## Standard Stack

### Core

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| Cowork plugin format | Jan 2026 (current) | Plugin scaffold for ZIP install and slash command entry point | Official Anthropic format; the only format that works with Cowork's ZIP upload and plugin activation |
| `plugin.json` manifest | Same schema as CLI | Plugin identity (name, description, version, author) | Required file; Cowork will not recognize the plugin without it |
| `commands/` directory | Markdown + YAML frontmatter | Slash command definition — user-triggered explicit workflows | How Cowork plugins define `/due-diligence`; confirmed from `knowledge-work-plugins` reference |
| `skills/` directory | SKILL.md + optional resources | Auto-triggered domain knowledge and orchestration instructions | How Cowork skills work; skill metadata is 100 tokens at startup, loaded on demand |
| ZIP archive | Standard ZIP | Distribution to non-technical users | Cowork's "Upload plugin" interface accepts ZIP; no terminal required |

### Supporting

| Component | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| Workspace folder (bidirectional) | Cowork native | Read data room files, write reports and intermediate state | Always — this is how all file I/O happens inside Cowork |
| `${ARGUMENTS}` placeholder | Cowork template variable | Pass user-supplied arguments to command body | Use in command files when the command accepts input |
| `${CLAUDE_PLUGIN_ROOT}` | Cowork environment variable | Reference plugin-internal files without hardcoding paths | Use in skill/agent instructions to reference templates, rubrics |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `commands/` directory for slash command | CLI `skills/*/SKILL.md` entry point | CLI SKILL.md invocation does not work in Cowork; commands/ is the correct Cowork entry point |
| ZIP upload distribution | MCPB Desktop Extension | MCPB is for MCP server bundles; the core Cowork plugin does not need an MCP server for Phase 1. ZIP is sufficient and simpler. |
| Cowork native sub-agent dispatch | External orchestration (n8n-mcp, claude-flow) | External frameworks require developer setup and break the non-technical UX requirement |

**No installation commands needed** — the plugin is purely file-based (markdown + JSON). The user uploads a ZIP. No npm, no pip, no terminal.

---

## Architecture Patterns

### Recommended Plugin Structure

```
dc-due-diligence-desktop/
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest (name, description, version, author)
├── commands/
│   └── due-diligence.md          # Slash command: /due-diligence
├── skills/
│   └── due-diligence/
│       └── SKILL.md              # Orchestrator skill (auto-triggered or called by command)
└── agents/                       # Sub-agent definitions (Phase 2+)
```

Phase 1 only needs `.claude-plugin/`, `commands/`, and `skills/` — no agents yet. Agents are added in Phase 2 and Phase 3.

For Phase 1 specifically, the smoke test stub sub-agents can live in the `skills/` directory or inline in the command body — they do not require `agents/` files.

### Pattern 1: Plugin Manifest (plugin.json)

**What:** Declares plugin identity. Same schema as CLI plugin.json.
**When to use:** Always required — Cowork will not recognize the plugin without it.

```json
{
  "name": "dc-due-diligence-desktop",
  "description": "Run 9-domain data center due diligence analysis from Claude Cowork — no terminal required.",
  "version": "0.1.0",
  "author": {
    "name": "Data Canopy"
  }
}
```

Source: Official `anthropics/knowledge-work-plugins` sales plugin plugin.json (confirmed schema).

### Pattern 2: Command File (commands/due-diligence.md)

**What:** Defines the `/due-diligence` slash command. YAML frontmatter + markdown body.
**When to use:** Whenever the user needs an explicit trigger for the full workflow.
**Key fields:** `description` (shown in Cowork's slash command list), `argument-hint` (placeholder shown in input).

```markdown
---
description: Run full 9-domain data center due diligence analysis on a workspace folder
argument-hint: "<data room folder path>"
---

# /due-diligence

Run the full due diligence workflow on the data room documents in your workspace folder.

## Usage

```
/due-diligence <folder-path>
```

Process the data room at: $ARGUMENTS

[Orchestrator instructions here]
```

Source: Confirmed from `anthropics/knowledge-work-plugins/sales/commands/call-summary.md` (exact format).

Note: Cowork slash commands for plugins use the format `/plugin-name:command-name` in some contexts, but within the plugin itself the command file name (`due-diligence.md`) maps to `/due-diligence`. Verify exact invocation syntax during Plan 01-02 testing.

### Pattern 3: Skill File (skills/due-diligence/SKILL.md)

**What:** Orchestrator skill with YAML frontmatter. Metadata (~100 tokens) always loaded; body loaded on trigger.
**When to use:** Contains the full orchestration workflow instructions.
**Required frontmatter fields:** `name` (max 64 chars, lowercase alphanumeric and hyphens only), `description` (max 1024 chars, includes trigger phrases).

```markdown
---
name: due-diligence
description: "Run due diligence on a data center opportunity. Triggered by '/due-diligence', 'analyze this data center deal', 'run due diligence on these documents', or 'evaluate this site'."
---

# Due Diligence Orchestrator

[Orchestration instructions here — Phase 1 stub version]
```

Source: Official platform docs at `platform.claude.com/docs/en/agents-and-tools/agent-skills/overview` (confirmed required fields and constraints).

### Pattern 4: Workspace File Discovery

**What:** Orchestrator lists files in the mounted workspace folder using bash.
**When to use:** Phase 1 success criterion — orchestrator must count and display files.

```bash
# Find all document types in workspace folder
find "${WORKSPACE_FOLDER}" -maxdepth 3 \
  -name "*.pdf" -o -name "*.docx" -o -name "*.xlsx" \
  -o -name "*.pptx" -o -name "*.jpg" -o -name "*.png" \
  2>/dev/null | sort
```

The workspace folder path is provided by Cowork as a mounted directory. The exact variable name (`${WORKSPACE_FOLDER}`, `${ARGUMENTS}`, or prompting the user) needs to be confirmed during Phase 1 testing.

### Pattern 5: Parallel Dispatch Smoke Test

**What:** Dispatch two stub sub-agents, observe whether they execute concurrently or sequentially. Record the result as an architectural decision.
**When to use:** Plan 01-03 — the single most important Phase 1 deliverable.

Design the test so the result is observable:
1. Sub-agent A sleeps for 5 seconds, then writes `agent-a-done.txt` with a timestamp
2. Sub-agent B sleeps for 5 seconds, then writes `agent-b-done.txt` with a timestamp
3. Both dispatched simultaneously by orchestrator
4. If both files show the same timestamp range (within 2 seconds of each other) → parallel execution confirmed
5. If `agent-b-done.txt` is created 5+ seconds after `agent-a-done.txt` → sequential execution confirmed

Record the result in `.planning/STATE.md` under Decisions before proceeding to Phase 2.

### Pattern 6: ZIP Packaging

**What:** Package the plugin directory as a ZIP archive for Cowork upload.
**When to use:** Plan 01-02 — test the install path on a clean Cowork instance.

```bash
# From the repo root
zip -r dc-due-diligence-desktop.zip dc-due-diligence-desktop/ \
  --exclude "*.DS_Store" \
  --exclude "*/.git/*"
```

The resulting ZIP is what the non-technical user uploads via Cowork's "Upload plugin" interface.

### Anti-Patterns to Avoid

- **Using CLI SKILL.md as the entry point:** The `skills/*/SKILL.md` invocation model is how Claude Code discovers and triggers skills. In Cowork, the user entry point is a `commands/` file. The `skills/` directory still exists for orchestration instructions, but the slash command must be defined in `commands/`.
- **Hardcoding absolute paths:** Never hardcode `/Users/...` or `/home/...` paths in plugin files. Use `${CLAUDE_PLUGIN_ROOT}` for plugin-internal references and `${ARGUMENTS}` or user input for workspace paths.
- **Assuming Task tool availability before the smoke test:** Do not design Phase 1 orchestration around `Task tool` calls. Use natural language orchestration instructions and observe behavior during Plan 01-03.
- **Loading CLI plugin format into Cowork:** The `.claude-plugin/plugin.json` schema is the same, but the surrounding architecture (agents spawned via Task tool, Python converters, `${CLAUDE_PLUGIN_ROOT}` path discovery) is CLI-specific. Phase 1 builds fresh.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| File type detection | Custom extension parser | Bash `find` with `-name "*.pdf"` patterns | VM has full bash; find is reliable and zero-setup |
| Plugin install mechanism | Custom installer | Cowork ZIP upload interface | Built into Cowork; no code needed |
| Slash command routing | Custom command dispatcher | `commands/` directory file naming | Cowork reads filename → maps to slash command name automatically |
| Sub-agent coordination | Custom message-passing system | Shared workspace folder (files as IPC) | Agents write to disk; orchestrator reads — this is the proven pattern from the CLI version |
| Progress display | Custom UI | Natural language progress messages in orchestrator | Cowork surfaces tool calls in real time; adding text messages is sufficient for Phase 1 |

**Key insight:** Phase 1 is almost entirely file structure, not code. The plugin is markdown files and a JSON manifest. Don't over-engineer it — the scaffold is the work.

---

## Common Pitfalls

### Pitfall 1: Wrong Plugin Format — CLI vs Cowork

**What goes wrong:** Building the `commands/` entry point as `skills/due-diligence/SKILL.md` and expecting `/due-diligence` to trigger it in Cowork. The SKILL.md is auto-triggered by Claude when relevant, not by user slash command invocation.
**Why it happens:** The existing `dc-due-diligence` CLI plugin uses `skills/*/SKILL.md` as its entry point. Cowork uses a separate `commands/` directory for explicit user-triggered slash commands.
**How to avoid:** Define the slash command in `commands/due-diligence.md`. Keep SKILL.md for orchestration body instructions that the command invokes. Test that `/due-diligence` appears in Cowork's command list before writing any orchestration logic.
**Warning signs:** Plugin installs but `/due-diligence` doesn't appear in Cowork's autocomplete.

### Pitfall 2: Assuming Parallel Dispatch Without Testing

**What goes wrong:** The entire Phase 3 Wave 1 parallel architecture is designed before the smoke test runs. If parallel dispatch is not available, the orchestration design must be rebuilt.
**Why it happens:** The Architecture researcher has HIGH confidence the Task tool is available in Cowork's VM. The Pitfalls researcher has MEDIUM confidence it is not. Both positions have credible sources.
**How to avoid:** Run Plan 01-03 before making any Phase 2 architecture decisions. Do not commit to parallel orchestration patterns in any Phase 1 artifacts — keep the orchestrator stub sequential.
**Warning signs:** Phase 1 SKILL.md contains `spawn 9 agents in parallel` instructions before Plan 01-03 completes.

### Pitfall 3: ZIP Contains Incorrect Directory Structure

**What goes wrong:** ZIP is created with an extra nesting level (`dc-due-diligence-desktop/dc-due-diligence-desktop/.claude-plugin/plugin.json`) or is missing the `.claude-plugin/` directory entirely. Cowork silently fails to recognize the plugin.
**Why it happens:** `zip -r` from inside the plugin directory creates a flat ZIP; from the parent creates a nested ZIP. The exact expected structure is not officially documented.
**How to avoid:** Test ZIP upload on a real Cowork instance during Plan 01-02. Verify the plugin appears in Cowork's plugin list after upload. If it doesn't appear, check ZIP structure with `unzip -l`.
**Warning signs:** Plugin uploaded but does not appear in Cowork's installed plugins list.

### Pitfall 4: Slash Command Invocation Format Ambiguity

**What goes wrong:** Cowork plugin slash commands may be invoked as `/due-diligence` or `/dc-due-diligence-desktop:due-diligence` depending on the plugin name and command file name. Using the wrong format produces no response.
**Why it happens:** The `knowledge-work-plugins` reference shows commands as `/call-summary` (from a `sales` plugin), which suggests the command name is the file name, not prefixed by plugin name. But the official Cowork blog mentions `/sales:call-prep` format for skills. The distinction between commands and skills may affect how they're invoked.
**How to avoid:** Test both `/due-diligence` and `/dc-due-diligence-desktop:due-diligence` during Plan 01-02. Document the actual invocation syntax.
**Warning signs:** Slash command typed but nothing happens, or Cowork shows "command not found."

### Pitfall 5: Cowork Session Context for SKILL.md Level 2 Loading

**What goes wrong:** The SKILL.md body (Level 2 instructions) is only loaded when Claude reads the file via bash. In a Cowork environment that doesn't have full bash/filesystem access, this may not happen automatically.
**Why it happens:** Skills architecture relies on Claude running bash to `cat` the SKILL.md file. If the Cowork sandbox restricts bash tool availability differently than Claude Code, the skill instructions may not load.
**How to avoid:** For Phase 1, put all orchestration instructions inline in the `commands/due-diligence.md` file body. Don't rely on SKILL.md loading for the stub. Test SKILL.md loading behavior in Phase 1 to understand if it works in Cowork before depending on it in Phase 2.
**Warning signs:** Orchestrator executes but ignores SKILL.md instructions, produces only generic responses.

---

## Code Examples

Verified patterns from official sources:

### plugin.json (from anthropics/knowledge-work-plugins/sales)

```json
{
  "name": "sales",
  "version": "1.0.0",
  "description": "Prospect, craft outreach, and build deal strategy faster.",
  "author": {
    "name": "Anthropic"
  }
}
```

Source: `https://raw.githubusercontent.com/anthropics/knowledge-work-plugins/main/sales/.claude-plugin/plugin.json` (HIGH confidence — official Anthropic repo)

### Command file format (from anthropics/knowledge-work-plugins/sales/commands/call-summary.md)

```markdown
---
description: Process call notes or a transcript — extract action items, draft follow-up email, generate internal summary
argument-hint: "<call notes or transcript>"
---

# /call-summary

Process these call notes: $ARGUMENTS

If a file is referenced: @$1

[Command body with workflow instructions...]
```

Source: `https://raw.githubusercontent.com/anthropics/knowledge-work-plugins/main/sales/commands/call-summary.md` (HIGH confidence — official Anthropic repo)

### SKILL.md frontmatter format (from anthropics/knowledge-work-plugins/sales/skills/call-prep)

```markdown
---
name: call-prep
description: Prepare for a sales call with account context, attendee research, and suggested agenda. Trigger with "prep me for my call with [company]", "I'm meeting with [company] prep me", or "get me ready for [meeting]".
---

# Call Prep Skill

[Skill body loaded on trigger...]
```

Source: `https://raw.githubusercontent.com/anthropics/knowledge-work-plugins/main/sales/skills/call-prep/SKILL.md` (HIGH confidence — official Anthropic repo)

### SKILL.md field constraints (from official platform docs)

```yaml
# name field:
# - Max 64 characters
# - Only lowercase letters, numbers, hyphens
# - Cannot contain "anthropic" or "claude"
# - Example: "due-diligence" ✓   "Due-Diligence" ✗

# description field:
# - Non-empty, max 1024 characters
# - Should include WHAT the skill does AND WHEN to use it (trigger phrases)
# - Include phrases the user will say naturally to trigger it
```

Source: `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview` (HIGH confidence — official Anthropic platform docs)

### Workspace file listing (bash pattern)

```bash
# List all document types in workspace folder
WORKSPACE="${ARGUMENTS:-$(pwd)}"
echo "Scanning $WORKSPACE for documents..."
find "$WORKSPACE" -maxdepth 3 \( \
  -name "*.pdf" -o \
  -name "*.docx" -o \
  -name "*.xlsx" -o \
  -name "*.pptx" -o \
  -name "*.jpg" -o \
  -name "*.jpeg" -o \
  -name "*.png" \
\) 2>/dev/null | sort

COUNT=$(find "$WORKSPACE" -maxdepth 3 \( \
  -name "*.pdf" -o -name "*.docx" -o -name "*.xlsx" \
  -o -name "*.pptx" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \
\) 2>/dev/null | wc -l)
echo "Found $COUNT documents"
```

Source: Standard bash pattern; adapted for Cowork workspace context. Confidence: HIGH (standard bash).

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| DXT Desktop Extensions | MCPB Desktop Extensions | Renamed Jan 2026 | Same format, new name — use `mcpb` not `dxt` in documentation |
| CLI `skills/*/SKILL.md` as entry point | Cowork `commands/` directory for slash commands | Cowork launch Jan 2026 | Different invocation model; `commands/` is the slash command entry point |
| Claude Code Task tool for sub-agent spawning | Cowork native sub-agent dispatch (mechanism TBD) | Cowork launch Jan 2026 | Mechanism unconfirmed — needs empirical test |
| Agent Skills as Claude Code feature | Agent Skills as open cross-platform standard | Dec 2025 | SKILL.md format works in both Claude Code and Cowork |

**Deprecated/outdated:**
- `dxt` CLI tooling: Renamed to `mcpb`. Use `modelcontextprotocol/mcpb` package.
- Task tool assumption for Desktop: Conventional wisdom says it's CLI-only, but Cowork VM architecture may change this. Verify empirically.

---

## Open Questions

1. **Does Cowork's VM architecture make the Task tool available?**
   - What we know: Architecture research (pvieito reverse-engineering) says YES — Cowork runs Claude Code CLI in a VM. Pitfalls research says NO — Task tool is CLI-only.
   - What's unclear: Whether the Cowork VM faithfully runs `claude` with full Task tool capability, or whether Cowork's wrapper restricts which tools are exposed.
   - Recommendation: Smoke test in Plan 01-03. Dispatch two stub sub-agents with a sleep + file-write pattern. Compare timestamps to determine concurrent vs sequential execution.

2. **What is the exact slash command invocation format?**
   - What we know: `commands/call-summary.md` → accessible as `/call-summary` (per the sales plugin README listing). Cowork blog mentions `/sales:call-prep` format for skills.
   - What's unclear: Whether the plugin-prefix format (`/dc-due-diligence-desktop:due-diligence`) is required or optional, and whether it differs for commands vs skills.
   - Recommendation: Test both formats during Plan 01-02. Document the result.

3. **Does SKILL.md Level 2 loading work in Cowork's sandbox?**
   - What we know: Skills architecture requires Claude to `bash cat SKILL.md` to load body content. This works in Claude Code (full bash access). Cowork's VM should have bash, but the exact tool availability is not officially documented.
   - What's unclear: Whether Cowork exposes the bash tool to the orchestrator, or whether it restricts execution in ways that prevent SKILL.md loading.
   - Recommendation: During Plan 01-01, put a minimal test instruction in SKILL.md and verify it is followed during Plan 01-02 testing.

4. **How does the workspace folder path get passed to the command?**
   - What we know: `$ARGUMENTS` in command files receives user-supplied text. In the CLI version, the user types `/due-diligence /path/to/folder`. In Cowork, the user may have a different way to specify the data room.
   - What's unclear: Whether Cowork provides a folder-picker UI that populates `$ARGUMENTS`, or whether the user types a path, or whether the workspace folder is pre-set and the command just reads from it.
   - Recommendation: Test the user experience in Plan 01-02. Design the command to accept a path argument but also work with the default workspace folder if no argument is provided.

---

## Sources

### Primary (HIGH confidence)
- `https://raw.githubusercontent.com/anthropics/knowledge-work-plugins/main/sales/.claude-plugin/plugin.json` — confirmed plugin.json schema (name, version, description, author)
- `https://raw.githubusercontent.com/anthropics/knowledge-work-plugins/main/sales/commands/call-summary.md` — confirmed command file format (YAML frontmatter: description, argument-hint; body: $ARGUMENTS, @$1)
- `https://raw.githubusercontent.com/anthropics/knowledge-work-plugins/main/sales/skills/call-prep/SKILL.md` — confirmed SKILL.md frontmatter (name, description with trigger phrases)
- `https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview` — confirmed SKILL.md required fields, name constraints (64 chars, lowercase/hyphen/digit), description constraints (1024 chars), progressive loading architecture (Level 1: 100 tokens at startup, Level 2: loaded on trigger)
- `https://claude.com/blog/cowork-plugins` — confirmed plugin components: skills, connectors, slash commands, sub-agents; all file-based
- `https://github.com/anthropics/knowledge-work-plugins` — confirmed directory structure: .claude-plugin/, commands/, skills/, .mcp.json

### Secondary (MEDIUM confidence)
- `https://support.claude.com/en/articles/13345190-getting-started-with-cowork` — Cowork sub-agents described as supporting parallel workstreams; bidirectional workspace folder access confirmed
- `https://pvieito.com/2026/01/inside-claude-cowork` — VM architecture (Ubuntu 22.04, Claude Code CLI, Task tool potentially available); rated MEDIUM due to conflict with pitfalls findings
- `.planning/research/ARCHITECTURE.md` — project-level architecture research (pvieito analysis cited as HIGH confidence by architecture researcher)
- `.planning/research/PITFALLS.md` — project-level pitfalls research (Task tool listed as unavailable in Cowork by pitfalls researcher)
- `.planning/research/STACK.md` — technology stack research, confirmed ZIP install and MCPB format
- `.planning/research/FEATURES.md` — feature research, confirmed native file reading and slash command requirements

### Tertiary (LOW confidence — needs validation)
- Community sources on Task tool availability in Cowork — contradictory; cannot resolve without empirical test

---

## Metadata

**Confidence breakdown:**
- Plugin format (plugin.json, commands/, skills/): HIGH — confirmed from official Anthropic reference repo and platform docs
- ZIP distribution: HIGH — confirmed from multiple install guides and official blog
- Slash command invocation format: MEDIUM — command file format confirmed; exact invocation syntax (with/without plugin prefix) needs Plan 01-02 testing
- Parallel dispatch availability: LOW — irreconcilable research conflict; requires empirical smoke test
- Workspace folder path variable: LOW — `$ARGUMENTS` pattern confirmed for commands; exact Cowork workspace variable name needs testing

**Research date:** 2026-02-23
**Valid until:** 2026-03-23 (30 days; Cowork is a research preview that may ship updates)
