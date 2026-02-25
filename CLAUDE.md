# Shipfast

Noah Rasheta's personal collection of Claude Code plugins, skills, agents, and coding resources -- hosted at [shipfast.cc](https://shipfast.cc).

## About This Repo

This is where I build and publish the tools I actually use day to day. My work is diverse -- podcast hosting, side businesses, real estate, data infrastructure, and whatever else I'm building at the moment -- so the plugins here will span many domains. The common thread is that they're all things I made to solve real problems with Claude Code.

This also serves as a Claude Code plugin marketplace. Eventually it may expand to other agentic coding platforms like OpenCode.

## My Role (Claude)

You are a **Claude Code specialist** and **marketplace manager** for this repo. Your core expertise:

- Claude Code plugin architecture (manifests, agents, skills, hooks, commands)
- Marketplace installation and distribution (`/plugin marketplace add`, `/plugin install`)
- Skill creation best practices (SKILL.md format, orchestration patterns, agent spawning)
- Plugin validation and local development workflows
- Keeping the marketplace catalog in sync as plugins are added or updated

When Noah adds new plugins or skills, help him structure them correctly, validate them, and register them in the marketplace.

## Repository Structure

```
shipfast/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog (lists all plugins)
├── create-image/                 # Plugin: AI image generation
│   ├── .claude-plugin/
│   │   └── plugin.json           # Plugin manifest
│   ├── agents/                   # PaperBanana agent team
│   └── skills/
│       └── create-image/
│           └── SKILL.md          # Orchestrator skill
├── create-prd/                  # Plugin: AI-optimized PRD generation
│   ├── .claude-plugin/
│   │   └── plugin.json           # Plugin manifest
│   ├── skills/
│   │   └── create-prd/
│   │       └── SKILL.md          # Conversational PRD builder skill
│   ├── references/               # AI PRD best practices guide
│   └── examples/                 # Sample PRD (FocusFlow)
├── dc-due-diligence/             # Plugin: Data center due diligence
│   ├── .claude-plugin/
│   │   └── plugin.json           # Plugin manifest
│   ├── agents/                   # 12 specialized research agents
│   ├── skills/
│   │   └── due-diligence/
│   │       └── SKILL.md          # Orchestrator skill
│   ├── converters/               # Document conversion pipeline (Python)
│   ├── templates/                # Agent output template + scoring rubric
│   └── tests/                    # Test suite
├── CLAUDE.md                     # This file
├── README.md
└── LICENSE
```

## Adding a New Plugin

1. Create a new directory at the repo root: `my-plugin/`
2. Add `.claude-plugin/plugin.json` inside it with name, description, version, author
3. Structure agents as `agents/<name>.md`, skills as `skills/<name>/SKILL.md`
4. Add the plugin entry to `.claude-plugin/marketplace.json` in the `plugins` array
5. Add a plugin reference section to this file (`CLAUDE.md`)
6. Add a row to the plugin summary table in `README.md` and a detailed `### my-plugin` section
7. Validate with `/plugin-dev:plugin-validator` and review skills with `/plugin-dev:skill-reviewer`

## Key Conventions

- **Plugin manifests** go in `<plugin>/.claude-plugin/plugin.json`, not at the plugin root
- **Skills** use directory format: `skills/<skill-name>/SKILL.md` (not flat `skills/<name>.md`)
- **Agent files** must have YAML frontmatter with `name` and `description` fields
- **Paths in agents** use `${CLAUDE_PLUGIN_ROOT}` to reference files within the plugin (never hardcode absolute paths)
- **Marketplace catalog** at `.claude-plugin/marketplace.json` lists all available plugins
- **Three files to update** when adding a plugin: `marketplace.json`, `CLAUDE.md` (plugin reference), `README.md` (summary table + detailed section)
- **Plugins are Claude Code only** -- the plugin system (agents, skills, Task tool orchestration) requires Claude Code (CLI). Plugins do not work in Claude Desktop.

## Versioning

When bumping a plugin's version, **all version references must be updated together**. The source of truth is `<plugin>/.claude-plugin/plugin.json`.

### dc-due-diligence version locations

Update ALL of these when changing the version:

1. `dc-due-diligence/.claude-plugin/plugin.json` -- `"version"` field (source of truth)
2. `dc-due-diligence/skills/due-diligence/SKILL.md` -- `version` in YAML frontmatter
3. `dc-due-diligence/pyproject.toml` -- `version` field under `[project]`
4. `README.md` -- `**Status:**` line in the `### dc-due-diligence` section

### create-image version locations

Update ALL of these when changing the version:

1. `create-image/.claude-plugin/plugin.json` -- `"version"` field (source of truth)
2. `README.md` -- `**Status:**` line in the `### create-image` section

### create-prd version locations

Update ALL of these when changing the version:

1. `create-prd/.claude-plugin/plugin.json` -- `"version"` field (source of truth)
2. `README.md` -- `**Status:**` line in the `### create-prd` section

### Adding a new plugin

When adding a new plugin, add a version locations section here following the same pattern. List every file where the version string appears.

## Plugin Reference: create-prd

The `create-prd` plugin generates AI-optimized Product Requirements Documents through guided conversation:

- **Skill** (`/create-prd`): Runs an adaptive brainstorming conversation that assesses the user's technical level and extracts their product vision
- **Conversation Flow**: 7 phases -- Vision & Context, Technical Assessment, Features & Scope, User Experience, Business Context (optional), Generate PRD, Refine
- **Adaptive**: Non-technical users get plain-language questions and recommended tech stacks; technical users get direct stack/integration questions
- **Output**: Comprehensive PRD in markdown with testable acceptance criteria, explicit scope boundaries, phased implementation, data models, and environment setup
- **Compatibility**: PRD output works with Claude Code, Cursor, Windsurf, Lovable, GSD, Director, Conductor, or any LLM-based builder
- **References**: Bundled best practices guide (`references/ai_prd_best_practices.md`) and sample PRD (`examples/sample_prd.md`)

## Plugin Reference: create-image

The `create-image` plugin generates AI images using the PaperBanana agentic framework:

- **Skill** (`/create-image [description]`): Orchestrates the full image generation pipeline
- **Agents**: 4 specialized agents (Research, Prompt Architect, Generator, Critic) running sequentially
- **Framework**: Based on Google Cloud AI Research's PaperBanana paper (+17% improvement over single-shot generation)
- **Output**: 5 image variants with multi-dimensional critique and ranked recommendations

## Plugin Reference: dc-due-diligence

The `dc-due-diligence` plugin automates data center due diligence analysis:

- **Skill** (`/due-diligence <folder-path>`): Orchestrates the full analysis pipeline
- **Agents**: 12 specialized agents -- 9 domain research (Power, Connectivity, Water/Cooling, Land/Zoning, Ownership, Environmental, Commercials, Natural Gas, Market Comparables), 1 Risk Assessment, 1 Executive Summary Generator, 1 Test Agent
- **Pipeline**: Three-wave execution -- Wave 1: 9 domain agents in parallel analyzing broker documents, Wave 2: Risk Assessment synthesizing cross-domain findings, Wave 3: Executive Summary scoring all categories
- **Output**: Scored executive summary with Pursue / Proceed with Caution / Pass verdict, plus 10 detailed research reports
- **Infrastructure**: Docling-based document converters (PDF, Excel, Word, PowerPoint, images, CSV, HTML) -- fully offline, no API calls. Automatic PII redaction via GLiNER (bank accounts, SSNs, EINs, credit cards redacted; emails, phone numbers, company names preserved for research).
- **Web research**: Agents use Claude Code's built-in WebSearch/WebFetch (no config needed). Tavily, Exa, or Firecrawl MCP servers are used automatically if configured in Claude Code.
- **Setup**: Python venv is created automatically on first run. No API keys needed for document conversion or redaction -- everything runs locally. First setup downloads ~3-5 GB of models (Docling layout/table models + GLiNER PII model).

## Local Development

Test a plugin locally without installing from the marketplace:

```bash
claude --plugin-dir ./<plugin-name>
```

Validate plugin structure:

```bash
claude plugin validate ./<plugin-name>
```
