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
├── dc-due-diligence/             # Plugin: Data center due diligence
│   ├── .claude-plugin/
│   │   └── plugin.json           # Plugin manifest
│   ├── agents/                   # Domain research agents
│   ├── skills/
│   │   └── due-diligence/
│   │       └── SKILL.md          # Orchestrator skill
│   ├── converters/               # Python document processing pipeline
│   ├── templates/                # Agent output templates
│   └── tests/                    # Test fixtures
├── CLAUDE.md                     # This file
├── README.md
└── LICENSE
```

## Adding a New Plugin

1. Create a new directory at the repo root: `my-plugin/`
2. Add `.claude-plugin/plugin.json` inside it with name, description, version, author
3. Add the plugin entry to `.claude-plugin/marketplace.json` in the `plugins` array
4. Structure agents as `agents/<name>.md`, skills as `skills/<name>/SKILL.md`

## Key Conventions

- **Plugin manifests** go in `<plugin>/.claude-plugin/plugin.json`, not at the plugin root
- **Skills** use directory format: `skills/<skill-name>/SKILL.md` (not flat `skills/<name>.md`)
- **Agent files** must have YAML frontmatter with `name` and `description` fields
- **Paths in agents** use `${CLAUDE_PLUGIN_ROOT}` to reference files within the plugin (never hardcode absolute paths)
- **Marketplace catalog** at `.claude-plugin/marketplace.json` lists all available plugins

## Plugin Reference: dc-due-diligence

The `dc-due-diligence` plugin automates data center procurement analysis:

- **Skill** (`/due-diligence <folder>`): Orchestrates the full workflow
- **Converters**: Python pipeline that processes PDFs, spreadsheets, Word docs into markdown
- **Agents**: 9 domain research agents + 1 test agent, all spawned in parallel via the Task tool
- **Templates**: Standardized output format all agents must follow

## Local Development

Test a plugin locally without installing from the marketplace:

```bash
claude --plugin-dir ./dc-due-diligence
```

Validate plugin structure:

```bash
claude plugin validate ./dc-due-diligence
```
