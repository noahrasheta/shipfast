# Pitfalls Research

**Domain:** Claude Desktop / Cowork plugin for complex multi-agent document analysis workflows
**Researched:** 2026-02-23
**Confidence:** MEDIUM-HIGH (verified via official Anthropic docs, help center, and multiple community sources)

---

## Critical Pitfalls

### Pitfall 1: Assuming Task Tool / Parallel Subagent Spawning Works in Desktop

**What goes wrong:**
The CLI version's entire Wave 1 architecture depends on spawning 9 domain agents in parallel via the Task tool. Claude Desktop and Cowork do NOT have the Task tool. Multi-agent orchestration via Task tool spawning is a Claude Code CLI feature only. Building the Desktop version with the same orchestration model results in a non-functional plugin.

**Why it happens:**
The CLI plugin works so well that developers assume the underlying orchestration primitives (Task tool, parallel subagent spawning) are universal Claude capabilities. They aren't — they are Claude Code CLI-specific. Claude Desktop's agentic capabilities come through Cowork's built-in agent runner and MCP-exposed tools, not the Task tool.

**How to avoid:**
Design the Desktop version's orchestration around what Cowork actually supports: sequential agent-style prompting, MCP tool calls, and Cowork's native sub-agent spawning (which differs from Task tool spawning). Verify each orchestration primitive against the Cowork plugin spec before building. Plan for sequential execution of the 9 domain agents rather than true parallel execution.

**Warning signs:**
- Design documents reference "spawning agents via Task tool" in a Desktop context
- Architecture diagrams show Wave 1 parallel execution without identifying the Desktop mechanism that enables it
- Developer testing the orchestration in Claude Code CLI but planning to ship for Desktop

**Phase to address:**
Architecture / Foundation phase — must be resolved before writing any agent orchestration logic.

---

### Pitfall 2: Context Window Exhaustion from Loading All Documents Plus All Agents

**What goes wrong:**
A data room may contain 15-30 files (PDFs, Excel, Word, PowerPoint, images). In Claude Desktop, these files are uploaded into the conversation context. Each file consumes tokens. With 30MB file limits and 200K token context windows, a document-heavy data room can exhaust the context window before even one domain agent runs. Compounding this: MCP server tool definitions consume 14K-66K tokens before any user content. The workflow fails silently mid-analysis or produces partial reports with no clear explanation to the user.

**Why it happens:**
The CLI version processes documents through Python converters that produce normalized markdown written to disk — documents are never loaded into Claude's context window all at once. The Desktop version's "native file reading" model fundamentally changes this: files loaded into conversation directly consume context. Developers underestimate this because desktop file attachment feels lightweight but tokenizes at scale.

**How to avoid:**
Never load all data room files simultaneously. Design a document routing strategy where only the files relevant to each domain agent are provided at that step. Pre-calculate approximate token budget per domain: ~15K tokens for agent instructions + tool definitions, leaving ~17K tokens per domain for relevant documents from a 200K window split across 9 domains. Consider a document registry MCP tool that lists available files without loading them, letting each agent request only what it needs.

**Warning signs:**
- "Load the entire data room" instructions in the orchestrator prompt
- No token budget planning in the architecture
- Testing with small document sets (2-3 files) but production use involves 15+ files
- Context compaction triggering mid-workflow (Claude summarizing and discarding earlier file content)

**Phase to address:**
Architecture phase — document loading strategy must be decided before building agent prompts.

---

### Pitfall 3: Assuming MCP Server Dependencies Are Pre-installed for Non-Technical Users

**What goes wrong:**
Many Desktop MCP workflows require Node.js, Python runtimes, or specific packages. Non-technical users don't have these installed. An MCP server that requires `uvx`, `npx`, or a Python venv will silently fail to start, and the user sees a confusing "tool not available" error or no error at all — the workflow just doesn't do anything useful. The user concludes the plugin is broken and stops using it.

**Why it happens:**
Developers test on their own machines where Node.js, Python, and common tools are already present. The installation docs say "run `npx...`" which works fine for them. They don't test on a clean macOS machine with only Claude Desktop installed.

**How to avoid:**
Use Desktop Extensions (.mcpb format) for distribution. MCPB bundles all dependencies into a single installable file — no terminal, no Node.js install, no Python venv. Critically: MCPB cannot portably bundle compiled Python dependencies (pydantic, etc.), which is why Node.js is the recommended MCP server runtime for Desktop Extensions — Claude Desktop ships with Node.js bundled on macOS and Windows. If any MCP server is needed, build it in Node.js and package as .mcpb. Validate by installing on a clean macOS machine with only Claude Desktop.

**Warning signs:**
- MCP server written in Python with compiled dependencies
- Installation instructions include `pip install`, `uv sync`, or `python -m venv`
- Distribution method is "send them this folder and edit claude_desktop_config.json"
- No clean-machine install test performed

**Phase to address:**
Distribution planning phase — decide runtime and packaging before writing a line of MCP server code.

---

### Pitfall 4: Web Research Silently Missing in Desktop

**What goes wrong:**
The CLI version's 9 domain agents each conduct independent web research using Claude Code's built-in WebSearch and WebFetch tools. These built-in tools do not exist in Claude Desktop or Cowork. If the Desktop plugin is designed assuming agents can call WebSearch, those calls produce no results — or worse, Claude hallucinates web research findings it never actually retrieved. Reports look complete but contain fabricated market data, utility rate comparisons, and regulatory findings.

**Why it happens:**
WebSearch and WebFetch are Claude Code CLI-specific tools. In Desktop, web access requires either: (a) Cowork's built-in browser integration via "Claude in Chrome" extension, or (b) an MCP-based search tool (Brave Search MCP, Exa MCP, Firecrawl MCP) installed separately. Without explicit web research capability verification, agents silently fall back to training data, which may be stale or incorrect for domain-specific queries like current utility rates or recent zoning changes.

**How to avoid:**
Explicitly verify and configure web research capability as a prerequisite step before the analysis runs. If "Claude in Chrome" extension is available, document it as the web research path. If an MCP search server is configured, detect and use it. If neither is available, warn the user that web research is disabled and reports will rely on training data — do not silently produce research-looking output from training data alone. Design agent prompts with a conditional web research section that gracefully acknowledges the limitation.

**Warning signs:**
- Agent prompts reference `WebSearch` or `WebFetch` tool calls (CLI-only tools)
- No check for web research capability in the orchestrator setup phase
- Testing done with web-enabled Claude Code but production deployment is Desktop-only

**Phase to address:**
Agent design phase — web research strategy must be determined before writing any domain agent prompts.

---

### Pitfall 5: Treating Claude Desktop Like Claude Code for Slash Commands and Skills

**What goes wrong:**
The CLI plugin is invoked via `/due-diligence <folder-path>`, a Claude Code skill slash command. Claude Desktop does not support Claude Code skills, SKILL.md-based slash commands, or the same plugin system. Building a "Desktop version" of the SKILL.md orchestrator results in a plugin that cannot be invoked. The user has no entry point — they open Claude Desktop and don't know how to start the workflow.

**Why it happens:**
The Shipfast plugin marketplace is built around Claude Code's plugin system (plugin.json, agents/*.md, skills/*/SKILL.md). It's natural to assume the same structure works for Desktop. It doesn't. Desktop uses a different plugin architecture: Cowork plugins bundle skills (different concept), connectors, and sub-agents via a separate manifest format.

**How to avoid:**
Create a completely separate plugin structure for the Desktop version — not a fork of the CLI plugin. The invocation entry point in Cowork is a natural language instruction or a Cowork plugin slash command (distinct from Claude Code skill slash commands). Document the Desktop plugin's manifest format independently. Keep the two plugins in separate directories with separate plugin.json manifests.

**Warning signs:**
- Desktop plugin directory contains a `skills/*/SKILL.md` file intended for Claude Code
- Plugin manifest references `type: "skill"` in Claude Code format
- "How do I run this in Desktop?" is unanswered in the design
- Developer conflates Claude Code plugin system with Cowork plugin system

**Phase to address:**
Foundation phase — plugin architecture and entry point design must be settled before any content is written.

---

### Pitfall 6: Cowork Session Amnesia Across Multi-Step Long Workflows

**What goes wrong:**
Cowork does not retain memory between sessions. A due diligence workflow takes 15-45 minutes. If the session times out, the user closes the window, or Cowork restarts mid-analysis, all in-progress state is lost. The user restarts and re-uploads all documents. Wave 1 results (the 9 domain reports) are lost if they were only in-memory and not written to disk. The user cannot resume — they must start over.

**Why it happens:**
The CLI version handles this via explicit file system writes after each wave (research/*.md files on disk). The Desktop version's "native" approach may avoid file writes, keeping intermediate results only in context. This is an invisible architecture decision that becomes catastrophic when a session ends unexpectedly.

**How to avoid:**
Design the Desktop plugin to write intermediate results to disk (the data room folder or a subdirectory) after each domain agent completes, not just at the end. Use an MCP filesystem server or Cowork's file access to write reports as they're generated. Build a resume capability: if partial reports exist on disk from a previous run, detect and skip completed domains. Treat every intermediate result as ephemeral until it's on disk.

**Warning signs:**
- Architecture relies on in-context accumulation of agent results across 9 sequential domains
- No intermediate file writes in the design
- "Resume from checkpoint" not addressed in the design
- Workflow tested only on small document sets that complete in under 5 minutes

**Phase to address:**
Architecture phase — state persistence strategy must be decided before agent sequencing is designed.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Sequential instead of parallel for all 9 domains | Simpler to build, no orchestration complexity | 3-5x slower workflow (15-45 min vs 5-15 min); user abandons mid-run | Acceptable for MVP; optimize in v2 if user feedback warrants |
| Skip web research for MVP | No dependency on Chrome extension or MCP search | Reports rely on training data; stale market data and utility rates; false confidence in output quality | Never acceptable for production; must flag clearly if skipped |
| Use Claude.ai file upload instead of MCP filesystem | No MCP server to build | 20 file limit per conversation; 30MB cap; no programmatic file writing; no resume capability | Never for production; fine for feasibility testing only |
| Hardcode domain agent prompts into orchestrator | Simpler single-file design | Cannot update individual agents without editing monolithic file; harder to test domain agents independently | Only if plugin will never be updated |
| No document routing — load all files for each agent | Simpler orchestrator logic | Context window exhaustion at 6+ files in data room; workflow fails on realistic document sets | Never acceptable |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| MCP Filesystem Server | Giving broad access to home directory; user approves all-or-nothing | Scope to specific folder (the data room + output directory only); request minimum permissions |
| Cowork + "Claude in Chrome" for web research | Assuming Chrome extension is always installed and active | Check capability at workflow start; inform user if web research is unavailable; don't proceed silently with training-data-only research |
| MCPB / Desktop Extension packaging | Building MCP server in Python with compiled deps | Use Node.js for any MCP server bundled as .mcpb; Claude Desktop ships Node.js on macOS/Windows |
| MCP tool call timeouts | Long-running document processing in a single MCP tool call hits 60-second timeout | Break processing into per-file tool calls; implement async patterns; return structured error if timeout occurs |
| Cowork plugin distribution | Sending a zip with JSON config edits to non-technical user | Distribute as .mcpb via direct file share (no terminal, no JSON editing needed) |
| Claude.ai document upload (Excel) | Expecting formula-aware extraction from complex multi-region spreadsheets | Merged cells and presentation-style layouts break xlsx parsing; validate with real broker document samples before committing to this approach |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Loading all data room files into one context | Context compaction triggers mid-workflow; later domain agents get compressed/summarized earlier documents | Per-agent document routing; only load relevant files per domain | At ~5-8 large PDFs in a single conversation |
| Many MCP servers active simultaneously | 8-18% context used at session start; full context exhausted after 5 prompts | Keep MCP servers to minimum needed; use Tool Search / deferred loading | With 3+ verbose MCP servers active |
| Sequential 9-domain workflow in one long context | Context fills with domain report #7-9 getting compressed context from documents analyzed for domains #1-3 | Write domain reports to disk as generated; clear document context between domains; use separate sub-contexts per domain | At domain 5+ in a large document set |
| Expecting Cowork to infer workflow state across sessions | User opens new session and workflow starts from scratch | Explicit session state files (progress tracker in output folder); Personal Preferences injection for workflow context | Every session restart |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Broad MCP filesystem permissions (home directory access) | Cowork agent could read/modify sensitive files outside the data room | Scope filesystem MCP to the specific data room folder and output directory only |
| No document safety protocol in Desktop agent prompts | Broker documents containing embedded "ignore previous instructions" style text could redirect agent behavior | Port the Document Safety Protocol from CLI agents verbatim to all Desktop agent prompts |
| Storing API keys for optional MCP services in plugin files | Credentials committed to the plugin or distributed in the .mcpb | Document API keys as user-configured environment variables in installation instructions; never embed in plugin |
| Auto-approving all MCP tool permissions | User installs plugin, clicks "Always approve" on broad permissions without understanding scope | Document exactly which permissions are needed and why in the installation guide; request minimum viable permissions |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No progress feedback during 15-45 minute workflow | User thinks the workflow crashed or stalled after 2 minutes of silence; cancels and loses work | Explicit step-by-step progress messages after each domain agent completes ("Power analysis complete (1/9)...") |
| Presenting raw markdown reports as final output | Non-technical user gets markdown with `##` headers and `**bold**` syntax; can't share with clients | Write final reports as .docx or .pdf using Cowork's document creation capabilities or the docx/pdf Skills |
| Asking user to specify folder path in a chat message | Non-technical user doesn't know absolute paths; types relative path or wrong format | Instruct user to drag-and-drop the data room folder into the chat; or use MCP filesystem browsing to select folder |
| Silent failure when one domain agent produces no output | Final executive summary is missing a section with no explanation | Explicit failure reporting after each agent: if a domain report is missing or under 500 characters, report it to the user before continuing |
| No instruction for what to do with output files | User doesn't know where reports were saved or how to find them | Always display the exact output folder path and file names at workflow completion; offer to open the folder |
| One-size-fits-all workflow invocation | Advanced user wants to re-run just one domain; has to re-run everything | Design for selective re-run: "re-run Power analysis only" — detect existing reports and skip completed domains |

---

## "Looks Done But Isn't" Checklist

- [ ] **Web research**: Often missing verification that agents actually performed web research vs. generating training-data answers that look like research — verify by checking for specific recent data points (current utility rates, recent regulatory filings) that couldn't come from training data
- [ ] **Document routing**: Often missing per-domain document filtering — verify that Power agent only receives power-related documents, not the entire data room on every agent call
- [ ] **Output format**: Often missing real document generation — verify that `.docx` output is a proper Word file (not markdown renamed to .docx) by opening it in Word/Pages
- [ ] **Session resume**: Often missing resume logic — verify by canceling mid-run and restarting; the workflow should detect completed domain reports and skip them
- [ ] **Non-technical installation**: Often missing clean-machine test — verify by installing the plugin on a machine with no developer tools, no Node.js, no Python; the workflow must work with only Claude Desktop installed
- [ ] **Large data room test**: Often missing realistic load test — verify with a 15+ file, mixed-format data room (PDF, Excel, Word, PowerPoint, images) before declaring the plugin production-ready
- [ ] **Error messaging**: Often missing user-facing error context — verify that when a domain agent fails, the user receives an actionable message, not a raw error or silent continuation

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Built orchestration around Task tool before verifying availability | HIGH — requires architectural redesign | Audit all agent spawning logic; replace Task tool calls with Cowork sub-agent patterns or sequential prompting; retest entire pipeline |
| Context window exhausted mid-workflow | MEDIUM — workflow must restart | Add document routing logic; rerun from beginning with routing fix; previously written domain reports can be reused if on disk |
| MCP server fails to start for non-technical user | HIGH — user trust is lost | Pivot to MCPB packaging; rewrite MCP server in Node.js; re-distribute; provide one-click re-install |
| Web research producing training-data fabrications | HIGH — analysis quality is compromised | Add explicit web research verification step; add capability check at workflow start; document clearly when web research is disabled |
| Session amnesia loses partial results | MEDIUM — if disk writes are in place | Implement resume detection against on-disk reports; re-run failed/missing domains only |
| User can't figure out how to start the workflow | MEDIUM — add onboarding | Add one-paragraph "Getting Started" to plugin manifest description; add Cowork Personal Preferences snippet that teaches users the trigger phrase |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Task tool assumption | Phase 1: Architecture | Prototype orchestration with Cowork before building agents; confirm 9-domain sequential flow works |
| Context window exhaustion | Phase 1: Architecture | Token budget analysis for realistic document sets (15+ files); per-agent document routing designed before agents written |
| MCP dependency for non-technical install | Phase 1: Distribution design | Confirm MCPB / Node.js runtime approach before writing MCP server code |
| Missing web research | Phase 2: Agent design | Web research capability check in orchestrator setup; agent prompts handle missing capability gracefully |
| Wrong plugin entry point (SKILL.md for Desktop) | Phase 1: Foundation | Cowork plugin manifest written and tested as entry point before any agent content written |
| Session amnesia / no resume | Phase 2: Agent design | Intermediate file writes after every domain agent; resume detection logic before Wave 1 starts |
| Markdown instead of document output | Phase 3: Output | Test actual .docx/.pdf generation with Cowork Skills before user testing |
| No progress visibility | Phase 2: UX | Progress messages after every agent built into orchestrator; test with a non-technical user watching the workflow run |
| Large data room performance | Phase 3: Testing | Required: integration test with 15+ file mixed-format data room before any user testing |
| Non-technical install friction | Phase 4: Distribution | Required: clean-machine install test before sharing with any non-technical user |

---

## Sources

- [One-click MCP server installation for Claude Desktop (Anthropic Engineering)](https://www.anthropic.com/engineering/desktop-extensions) — MCPB format, Node.js requirement, dependency bundling constraints
- [Getting started with Cowork (Anthropic Help Center)](https://support.claude.ai/en/articles/13345190-getting-started-with-cowork) — session memory limitations, no Projects integration
- [Uploading files to Claude (Anthropic Help Center)](https://support.claude.ai/en/articles/8241126-what-kinds-of-documents-can-i-upload-to-claude) — 30MB limit, 20 files per chat, context window constraints
- [The Hidden Cost of MCPs and Custom Instructions on Your Context Window](https://selfservicebi.co.uk/analytics%20edge/improve%20the%20experience/2025/11/23/the-hidden-cost-of-mcps-and-custom-instructions-on-your-context-window.html) — MCP tool definition token costs (14K-66K tokens)
- [MCP and Context Windows: Lessons Learned During Development](https://medium.com/@pekastel/mcp-and-context-windows-lessons-learned-during-development-590e0b047916) — multiple MCP servers exhausting context
- [Claude Desktop vs Claude Code (Arsturn)](https://www.arsturn.com/blog/claude-desktop-vs-claude-code-should-you-switch-for-mcp-features) — multi-agent orchestration is CLI/Agent SDK only, not Desktop
- [The Task Tool: Claude Code's Agent Orchestration System (DEV Community)](https://dev.to/bhaidar/the-task-tool-claude-codes-agent-orchestration-system-4bf2) — Task tool is Claude Code CLI specific
- [Enabling and using web search (Anthropic Help Center)](https://support.claude.ai/en/articles/10684626-enabling-and-using-web-search) — web search availability in Desktop vs. Code
- [How I mastered Claude Cowork — the amnesia problem](https://ai.plainenglish.io/how-i-mastered-claude-cowork-the-amnesia-problem-c8dabcfa3abb) — session memory loss patterns and workarounds
- [Claude Desktop Extensions: The End of Local MCP Friction (Medium)](https://medium.com/@pekastel/claude-desktop-extensions-the-end-of-local-mcp-friction-0455c9ef49c3) — non-technical user friction before MCPB
- [Resilient AI Agents With MCP: Timeout And Retry Strategies (Octopus)](https://octopus.com/blog/mcp-timeout-retry) — 60-second timeout on MCP tool calls, async patterns
- [Claude Cowork Tutorial (DataCamp)](https://www.datacamp.com/tutorial/claude-cowork-tutorial) — Cowork capabilities and limitations
- [Anthropic brings agentic plugins to Cowork (TechCrunch)](https://techcrunch.com/2026/01/30/anthropic-brings-agentic-plugins-to-cowork/) — Cowork plugin system architecture

---
*Pitfalls research for: dc-due-diligence-desktop — Claude Desktop / Cowork plugin development*
*Researched: 2026-02-23*
