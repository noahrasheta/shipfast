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
- **Infrastructure**: Python document converters (PDF, Excel, Word, PowerPoint, images via Anthropic vision API)
- **Web research**: Agents use Claude Code's built-in WebSearch/WebFetch (no config needed). Tavily, Exa, or Firecrawl MCP servers are used automatically if configured in Claude Code.
- **Setup**: Run `setup.sh` to create Python venv and install converter dependencies. Set `ANTHROPIC_API_KEY` in shell environment only if the opportunity folder contains images or scanned PDFs.

## Local Development

Test a plugin locally without installing from the marketplace:

```bash
claude --plugin-dir ./<plugin-name>
```

Validate plugin structure:

```bash
claude plugin validate ./<plugin-name>
```
