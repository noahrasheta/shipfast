# Shipfast - Claude Code Plugin Marketplace

This repository is a plugin marketplace for Claude Code, hosted at [shipfast.cc](https://shipfast.cc). It contains open-source plugins, agents, and skills that extend Claude Code's capabilities.

## Repository Structure

```
shipfast/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog (lists all plugins)
├── dc-due-diligence/             # Plugin: Data center due diligence
│   ├── .claude-plugin/
│   │   └── plugin.json           # Plugin manifest
│   ├── agents/                   # 10 domain research agents
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

## DC Due Diligence Plugin Architecture

The `dc-due-diligence` plugin automates data center procurement analysis:

- **Skill** (`/due-diligence <folder>`): Orchestrates the full workflow
- **Converters**: Python pipeline that processes PDFs, spreadsheets, Word docs into markdown
- **Agents**: 9 domain research agents + 1 test agent, all spawned in parallel via the Task tool
  - Power, Connectivity, Water & Cooling, Natural Gas, Environmental
  - Ownership & Control, Land & Zoning, Commercials, Market Comparables
  - Test Agent (pipeline validation)
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
