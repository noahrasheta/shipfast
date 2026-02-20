# Architecture Research

**Analysis Date:** 2026-02-20
**Confidence:** HIGH -- based on official Claude Code documentation (code.claude.com), direct codebase inspection, and authoritative sources for comparison ecosystems.

## Recommended Architecture

The right architecture for shipfast is a **plugin-per-directory monorepo** with a unified marketplace registry at the root. Each plugin is a fully self-contained unit: its own manifest, skill orchestrator, agents, and optional supporting code. The repo itself acts as both the author workspace (where plugins are built) and the distribution surface (where the marketplace.json catalog lives). This is already the pattern in use and it is the correct one.

The planned landing page (shipfast.cc) should be a separate, static-site concern layered on top of the existing repo structure -- it reads from the same source of truth (the marketplace catalog and plugin READMEs) rather than maintaining a parallel data model.

### System Overview

```
shipfast/ (GitHub repo = author workspace + marketplace registry)
│
├── .claude-plugin/
│   └── marketplace.json          ← Registry: all plugins, sources, metadata
│
├── create-image/                 ← Plugin A (fully self-contained)
│   ├── .claude-plugin/
│   │   └── plugin.json           ← Plugin manifest (name, version, author)
│   ├── agents/                   ← Specialized task executors
│   ├── skills/create-image/      ← Orchestrator (SKILL.md entry point)
│   ├── scripts/                  ← Supporting Python code
│   └── references/               ← Reference docs agents read
│
├── dc-due-diligence/             ← Plugin B (fully self-contained)
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── agents/                   ← 12 domain specialists
│   ├── skills/due-diligence/     ← Orchestrator (SKILL.md entry point)
│   ├── converters/               ← Python document processing library
│   ├── templates/                ← Agent output format contracts
│   └── tests/                   ← pytest suite for converters
│
├── [future-plugin]/              ← New plugins follow same pattern
│
└── landing-page/                 ← (Future) Static site (Astro or plain HTML)
    ├── src/
    │   ├── pages/
    │   └── components/
    └── public/

```

### Component Responsibilities

| Component | Responsibility | Implementation |
|-----------|----------------|----------------|
| Marketplace registry | Unified plugin catalog for discovery and installation | `.claude-plugin/marketplace.json` at repo root |
| Plugin manifest | Per-plugin identity, version, and metadata | `<plugin>/.claude-plugin/plugin.json` |
| Skill orchestrator | Receives user command, coordinates the agent pipeline, manages phase transitions | `<plugin>/skills/<name>/SKILL.md` with YAML frontmatter |
| Domain agent | Stateless, specialized task executor spawned by the orchestrator via Task tool | `<plugin>/agents/<name>.md` with YAML frontmatter |
| Support layer | Python code, scripts, templates, reference docs that agents invoke or reference | `<plugin>/converters/`, `scripts/`, `templates/`, `references/` |
| Landing page | Public showcase and documentation site (future) | Static site in `landing-page/` or separate repo |

## Suggested Project Structure

The current structure is architecturally sound. The recommended evolution as new plugins are added:

```
shipfast/
  .claude-plugin/
    marketplace.json              # Plugin catalog -- update for every new plugin
  create-image/                   # Existing plugin
    .claude-plugin/plugin.json
    agents/
    skills/create-image/SKILL.md
    scripts/
    references/
  dc-due-diligence/               # Existing plugin
    .claude-plugin/plugin.json
    agents/
    skills/due-diligence/SKILL.md
    converters/
    templates/
    tests/
  [new-plugin]/                   # Future plugin (same shape)
    .claude-plugin/plugin.json
    agents/
    skills/<name>/SKILL.md
    [scripts/ if needed]
    [templates/ if needed]
    [tests/ if needed]
  landing-page/                   # Future -- only add when shipfast.cc work begins
    src/
    public/
  CLAUDE.md                       # Repo-level instructions (update per plugin added)
  README.md                       # Public-facing docs (update per plugin added)
```

**Three files to update for every new plugin** (current requirement, no change needed):
1. `.claude-plugin/marketplace.json` -- registers the plugin for installation
2. `CLAUDE.md` -- Plugin Reference section
3. `README.md` -- summary table row + detailed section

## Patterns That Work

### Pattern: Orchestrator-Agent Separation

**What:** The skill (SKILL.md) acts purely as a coordinator. It never does work itself -- it sequences, decides which agents to spawn, passes context between them, and presents results. Agents execute the actual tasks. Agents are stateless -- they receive all necessary context in their prompt.

**When to use:** Every plugin. This is the foundational pattern for Claude Code plugins.

**Trade-offs:** Agents require explicit context injection (paths, prior outputs, templates) because they have no shared state. The orchestrator SKILL.md can become verbose for complex pipelines, but the separation makes each agent independently testable and replaceable.

```markdown
# In SKILL.md (orchestrator)
## Phase 3: Dispatch Agents

Spawn `plugin-name:agent-name` via the Task tool. Include in the prompt:
- The confirmed user requirements
- Output from the previous agent (paste in full)
- Absolute path to the output directory
- Path to the output template: ${CLAUDE_PLUGIN_ROOT}/templates/output.md

Capture the result and pass it to the next agent.
```

### Pattern: Multi-Wave Parallel Execution

**What:** For plugins with independent parallel workloads, spawn all non-dependent agents in a single Task tool response block (Wave 1), wait for completion, then spawn synthesis agents in sequence (Wave 2, Wave 3). The dc-due-diligence plugin demonstrates this with 9 parallel domain agents → risk assessment → executive summary.

**When to use:** Any plugin where multiple agents can work independently on the same data before results are synthesized.

**Trade-offs:** High parallelism speeds up long pipelines but increases context consumption. Each agent's output returns to the main context window. If 9 agents each produce a 2,000-word report, the orchestrator's context will carry ~18,000 words before synthesis begins.

```markdown
# In SKILL.md -- spawn all Wave 1 agents in ONE response block
Use the Task tool to spawn these agents in a single message:
- plugin:agent-one  (reads input-folder/, writes output-folder/one-report.md)
- plugin:agent-two  (reads input-folder/, writes output-folder/two-report.md)
- plugin:agent-three (reads input-folder/, writes output-folder/three-report.md)

Wait for all three to complete, then spawn Wave 2.
```

### Pattern: File System as State Bus

**What:** Agents communicate through the filesystem, not through the orchestrator's context. Wave 1 agents write reports to `<folder>/research/<domain>-report.md`. Wave 2 agents read all files from that directory. The orchestrator never passes report content between waves -- it passes folder paths.

**When to use:** Multi-wave pipelines where agent outputs are large (full research reports, converted documents). Avoids context bloat in the orchestrator.

**Trade-offs:** Requires well-defined output paths (standardized filenames). Orchestrator must validate that expected output files exist before spawning the next wave.

```markdown
# Wave 1 agents write to predictable paths
Expected output: <folder>/research/power-report.md

# Wave 2 agent reads the directory, not injected content
The opportunity folder is: <absolute-folder-path>
Read all files in: <absolute-folder-path>/research/
Synthesize findings across all domain reports.
```

### Pattern: ${CLAUDE_PLUGIN_ROOT} for Portability

**What:** Never hardcode absolute paths in agent or skill Markdown files. Use `${CLAUDE_PLUGIN_ROOT}` to reference files within the plugin. Claude Code resolves this token to the plugin's installation directory (which differs between local development and installed-from-marketplace scenarios).

**When to use:** Every reference to a file inside the plugin directory in any agent or skill file.

**Trade-offs:** None. Hardcoding absolute paths breaks portability. This token is the correct approach per official Claude Code docs.

```markdown
# Correct -- portable across install locations
${CLAUDE_PLUGIN_ROOT}/templates/output-template.md
${CLAUDE_PLUGIN_ROOT}/references/api-guide.md

# Wrong -- breaks when plugin is installed from marketplace
/Users/noahrasheta/Dev/GitHub/shipfast/dc-due-diligence/templates/output-template.md
```

### Pattern: Monorepo Plugin Marketplace with Local Relative Sources

**What:** The marketplace.json at the repo root uses `./plugin-name` relative paths to reference plugins within the same repository. Claude Code resolves these relative to the cloned repository, making all plugins installable with `claude plugin install plugin-name@shipfast` after adding the marketplace.

**When to use:** For a single-author or small-team marketplace where all plugins live in the same GitHub repo.

**Trade-offs:** Relative paths require the marketplace to be added via git (GitHub, git URL), not via a raw URL to the marketplace.json file. This is not a practical limitation for this use case.

```json
{
  "name": "shipfast",
  "owner": { "name": "Noah Rasheta" },
  "metadata": { "pluginRoot": "./" },
  "plugins": [
    {
      "name": "create-image",
      "source": "./create-image",
      "description": "AI image generation using PaperBanana agentic framework"
    },
    {
      "name": "dc-due-diligence",
      "source": "./dc-due-diligence",
      "description": "Data center due diligence workflow automation"
    }
  ]
}
```

### Pattern: Static Site Plugin Catalog (For Future shipfast.cc)

**What:** The landing page reads from `marketplace.json` and each plugin's `README.md` at build time (using Astro or similar static site generators). No backend required. The site is just a rendered view of the repo data.

**When to use:** When building shipfast.cc. Build-time data ingestion keeps the site static, fast, and zero-maintenance.

**Trade-offs:** Data is only as fresh as the last build. For a personal plugin catalog this is fine -- plugins update infrequently. A GitHub Action can rebuild on every push to main.

```
Astro build pipeline:
1. Read .claude-plugin/marketplace.json
2. For each plugin, read plugin.json + README.md
3. Generate /plugins/{name} page from README content
4. Generate / (index) with plugin grid from marketplace.json
```

## Patterns to Avoid

### Anti-Pattern: Hardcoded Absolute Paths in Agent Files

**What people do:** Reference plugin files with absolute paths because it works during local development (e.g., `/Users/noahrasheta/.../templates/output.md`).

**Why it causes problems:** When users install the plugin from the marketplace, Claude Code copies it to `~/.claude/plugins/cache/`. The absolute path no longer exists in that location. The agent silently fails to find its template.

**Do this instead:** Always use `${CLAUDE_PLUGIN_ROOT}` for any reference to a file inside the plugin directory. For paths passed at runtime (like the user's opportunity folder), use the path provided by the orchestrator as a shell variable.

### Anti-Pattern: Shared Code Across Plugins via Relative Paths

**What people do:** Create a `shared/` directory at the repo root and reference it from multiple plugins with `../shared/utils.py`.

**Why it causes problems:** When a plugin is installed from the marketplace, Claude Code copies the plugin directory to its cache (`~/.claude/plugins/cache/`). Files outside the plugin directory (like `../shared/`) are not copied. The path traversal fails silently or with confusing errors.

**Do this instead:** Duplicate shared utilities into each plugin that needs them, OR use symlinks inside the plugin directory (Claude Code follows symlinks during the cache copy). The official docs explicitly call this out: "Plugins cannot reference files outside their directory using paths like `../shared-utils`."

### Anti-Pattern: Orchestrator Doing Agent Work

**What people do:** Write skill orchestrators that try to analyze documents, generate content, or make domain decisions inline in the SKILL.md -- treating the orchestrator as a "super agent" that does some things itself and delegates others.

**Why it causes problems:** Skills run in the main conversation context. Doing heavy analysis inline pollutes the user's conversation with verbose intermediate output and fills context with content that should be isolated. It also makes the pipeline non-testable (you cannot spawn just the analysis portion independently).

**Do this instead:** Keep the orchestrator purely mechanical: validate inputs, set up directories, spawn agents with explicit context, validate outputs, present results. Every substantive task belongs in a dedicated agent.

### Anti-Pattern: Version Mismatch Between plugin.json and marketplace.json

**What people do:** Set version in both `plugin.json` and in the marketplace entry. Update one but forget the other.

**Why it causes problems:** Claude Code uses the version to detect whether to update a cached plugin. The `plugin.json` version always wins over the marketplace.json version silently. If both define a version, the marketplace entry is ignored -- and users do not get updates when the manifest version is not bumped.

**Do this instead:** For plugins in the same repo as the marketplace (relative-path sources), set the version only in marketplace.json and omit it from `plugin.json`. For plugins sourced from external GitHub repos, set the version in `plugin.json` and omit it from the marketplace entry.

### Anti-Pattern: Monolithic Agent With Multiple Responsibilities

**What people do:** Create one large agent that analyzes documents, does web research, synthesizes findings, generates the report, and scores the result.

**Why it causes problems:** A monolithic agent hits context limits on large inputs, produces inconsistent output quality across dimensions it was not specialized for, and cannot be updated or replaced in isolation. The research shows the PaperBanana multi-agent approach achieves +17% quality improvement over single-shot generation precisely because of specialization.

**Do this instead:** Split responsibilities into focused agents. Each agent should excel at one thing. Synthesis comes from a dedicated synthesis agent that reads all domain reports.

## How Data Flows

### Plugin Installation Flow

```
User runs: /plugin marketplace add noahrasheta/shipfast
    |
Claude Code clones: github.com/noahrasheta/shipfast
    |
Reads: .claude-plugin/marketplace.json
    |
Registers: "shipfast" marketplace in user settings

User runs: /plugin install dc-due-diligence@shipfast
    |
Claude Code resolves source: "./dc-due-diligence" (relative to cloned marketplace)
    |
Copies plugin to: ~/.claude/plugins/cache/shipfast/dc-due-diligence/
    |
Resolves ${CLAUDE_PLUGIN_ROOT} = ~/.claude/plugins/cache/shipfast/dc-due-diligence/
    |
User can now run: /dc-due-diligence:due-diligence <folder>
```

### Skill Execution Flow (Sequential Pipeline -- create-image)

```
User: /create-image "a minimalist logo for a coffee brand"
    |
SKILL.md loaded -> Orchestrator gathers requirements (interactive)
    |
Task(research-agent, context=requirements+image_paths) -> Style brief
    |
Task(prompt-architect, context=style_brief+requirements) -> 5 prompts
    |
Task(generator-agent, context=5_prompts+output_dir) -> 5 image file paths
    |
Task(critic-agent, context=image_paths+prompts+requirements) -> Rankings
    |
Orchestrator presents ranked results to user
```

### Skill Execution Flow (Parallel Pipeline -- dc-due-diligence)

```
User: /due-diligence ./opportunity-folder
    |
SKILL.md: Validate input -> Setup venv -> Run converters.pipeline
    |
_converted/manifest.json created
    |
Wave 1: Task(power-agent), Task(connectivity-agent), Task(water-cooling-agent),
         Task(land-zoning-agent), Task(ownership-agent), Task(environmental-agent),
         Task(commercials-agent), Task(natural-gas-agent), Task(market-comparables-agent)
         [ALL IN ONE RESPONSE BLOCK -- run in parallel]
    |
research/*.md files written by each agent
    |
Wave 2: Task(risk-assessment-agent, reads=research/*.md) -> risk-assessment-report.md
    |
Wave 3: Task(executive-summary-agent, reads=all 10 reports) -> EXECUTIVE_SUMMARY.md
    |
Orchestrator reports completion with verdict
```

### State Management

State is managed through two mechanisms:

1. **Inline context passing (sequential pipelines):** The orchestrator captures each agent's text output and injects it into the next agent's Task prompt. Used in create-image where style brief → prompts → critique chain through text.

2. **Filesystem state (parallel and wave pipelines):** Agents write to predictable file paths. The next wave reads from those files directly. The orchestrator passes folder paths, not file contents. Used in dc-due-diligence where domain reports → risk synthesis → executive summary chain through files.

No database, no Redis, no message queue. The filesystem is the state bus.

## Cross-Platform Plugin Architecture (Future Goal)

The user intends to eventually support Cursor rules, OpenCode, and Codex in addition to Claude Code. The architectural implication is separating the **portable logic layer** from the **platform-specific layer**.

### Recommended Abstraction

```
<plugin>/
  core/                    <- Platform-agnostic: prompts, logic, templates
    prompts/
      research.md          <- Prompt content (works anywhere)
      analysis.md
    templates/
      output-template.md   <- Output format contract
  claude-code/             <- Claude Code-specific: SKILL.md, agents/, hooks
    skills/<name>/SKILL.md
    agents/
    hooks/
  cursor/                  <- Future: Cursor-specific (rules files, .mdc format)
    <name>.mdc
  opencode/                <- Future: OpenCode-specific
    skills/
```

This is a **medium confidence** recommendation since OpenCode and Codex plugin specs are not yet stable or publicly documented as of February 2026. The safe approach: wait until concrete format specs exist for secondary platforms before introducing the cross-platform structure. Premature abstraction here adds complexity with no current payoff.

**What IS portable today:**
- Prompt content and instructions (Markdown text)
- Output templates
- Python scripts and converters (invoked via Bash -- works on any platform with a shell)

**What is NOT portable:**
- SKILL.md frontmatter (Claude Code-specific)
- `${CLAUDE_PLUGIN_ROOT}` token (Claude Code-specific)
- `${ARGUMENTS}` substitution (Claude Code-specific)
- Agent spawning via Task tool (Claude Code-specific)
- `plugin.json` manifest format (Claude Code-specific)

## Landing Page Architecture (For shipfast.cc)

### Recommended: Astro (Static Site Generation)

Astro is the right choice for a plugin library/showcase site. It produces zero-JS static HTML by default, reads from the existing JSON/Markdown data at build time, has an excellent component model for building plugin cards and catalog pages, and deploys trivially to Cloudflare Pages, Vercel, or GitHub Pages.

**Data model for the catalog:**

```json
// Derived from marketplace.json + each plugin's plugin.json + README.md at build time
{
  "plugins": [
    {
      "name": "create-image",
      "slug": "create-image",
      "description": "AI image generation...",
      "version": "0.1.0",
      "author": "Noah Rasheta",
      "tags": ["image-generation", "gemini"],
      "installCommand": "/plugin install create-image@shipfast",
      "readmeHtml": "<rendered HTML from create-image/README.md>",
      "homepage": "https://shipfast.cc"
    }
  ]
}
```

**Page structure:**

```
/                -> Plugin grid (searchable/filterable by tag)
/plugins/        -> All plugins listing
/plugins/[slug]  -> Individual plugin page (renders README + install instructions)
```

**Comparison to other plugin marketplaces:**
- Raycast Store: Per-extension pages with metadata, commands list, download count, author profile. Each extension is a ZIP with manifest.
- VS Code Marketplace: Publisher-based namespacing, category taxonomy, version history. Marketplace.json equivalent is package.json `publisher` field.
- Obsidian Plugin Directory: YAML metadata in plugin manifest + community-plugins.json catalog. Very similar to Claude Code's marketplace.json pattern.

The pattern is consistent across ecosystems: a central catalog file (marketplace.json / community-plugins.json / extensions.json) lists all plugins with metadata and source pointers. Individual plugin directories are self-contained with their own manifests.

## Scaling Notes

| Scale | Approach |
|-------|----------|
| 1-10 plugins (current) | Single marketplace.json at repo root. All plugins in same repo. Manual update of three files per plugin. No automation needed. |
| 10-30 plugins | Consider adding a `pluginRoot: "./plugins"` metadata field and moving all plugins under a `plugins/` subdirectory to reduce root-level clutter. Add a validation CI check (GitHub Actions running `claude plugin validate .`) to catch broken manifests before merge. |
| 30+ plugins | Consider whether plugin sub-repos (each plugin as its own GitHub repo, referenced in marketplace.json via `"source": {"source": "github", "repo": "noahrasheta/plugin-name"}`) make more sense than the monorepo approach. This enables independent versioning and release channels. |
| Landing page traffic | Static site generation + CDN (Cloudflare Pages or Vercel) handles any reasonable traffic. No server required. Add search via Pagefind (local JS index, no backend) if plugin count warrants it. |

## Sources

- Claude Code Plugin Architecture: https://code.claude.com/docs/en/plugins (official docs, verified)
- Claude Code Plugins Reference: https://code.claude.com/docs/en/plugins-reference (official schema docs, verified)
- Claude Code Marketplace Guide: https://code.claude.com/docs/en/plugin-marketplaces (official docs, verified)
- Claude Code Skills Reference: https://code.claude.com/docs/en/skills (official docs, verified)
- Claude Code Subagents Reference: https://code.claude.com/docs/en/sub-agents (official docs, verified)
- Codebase inspection: `create-image/skills/create-image/SKILL.md`, `dc-due-diligence/skills/due-diligence/SKILL.md`, `.claude-plugin/marketplace.json`
- Raycast extension structure: raycast.com/store (verified current pattern)

## Quality Gate

Before considering this file complete, verify:
- [x] Architecture diagram or description present
- [x] Component responsibilities clearly defined
- [x] At least 2 patterns to follow and 2 to avoid
- [x] Code examples included for recommended patterns
- [x] Scaling notes are realistic for the project's expected size
- [x] No section left empty -- use "Not applicable" if nothing found
