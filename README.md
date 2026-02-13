# Shipfast

Plugins, skills, and coding resources by [Noah Rasheta](https://noahrasheta.com) -- hosted at [shipfast.cc](https://shipfast.cc)

---

I'm a podcast host with a bunch of side businesses and projects. I build Claude Code plugins, skills, and agents to automate the things I do repeatedly. This repo is where all of that lives -- open source, for anyone to use, fork, or build on.

The stuff here spans many domains because my work does too. Data infrastructure, real estate, content workflows, and whatever I'm tinkering with next. The common thread is Claude Code and agentic AI.

## Quick Start

Add the marketplace and install a plugin:

```
/plugin marketplace add noahrasheta/shipfast
/plugin install dc-due-diligence@shipfast
```

## Plugins

### dc-due-diligence

Data center due diligence workflow automation. Point it at a folder of data room documents and get a structured executive summary with scored categories.

**What it does:**
- Processes PDFs, spreadsheets, Word docs, and images into analyzable markdown
- Spawns 9 domain research agents in parallel (power, connectivity, water, gas, environmental, ownership, zoning, commercials, market comparables)
- Each agent produces a standardized report with traffic-light scoring and confidence percentages
- Validates all outputs against a structured template

**Usage:**

```
/dc-due-diligence:due-diligence ./path/to/opportunity-folder
```

**Status:** v0.1.0 -- pipeline validation phase. Test agent functional, full 9-agent parallel orchestration in progress.

---

*More plugins coming as I build them.*

## Links

- **Marketplace:** [shipfast.cc](https://shipfast.cc)
- **Personal site:** [noahrasheta.com](https://noahrasheta.com)
- **GitHub:** [github.com/noahrasheta/shipfast](https://github.com/noahrasheta/shipfast)

## License

MIT -- see [LICENSE](LICENSE) for details.
