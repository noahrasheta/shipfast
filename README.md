# Shipfast

A Claude Code plugin marketplace at [shipfast.cc](https://shipfast.cc)

---

I'm Noah Rasheta, and this is my collection of open-source Claude Code plugins, skills, and agents. I built these for my own work in data center procurement, real estate analysis, and other domains where agentic AI and autonomous workflows save real time. Everything here is shared for the community to use, fork, and build on.

This marketplace represents hands-on work in agentic AI: multi-agent orchestration, document processing pipelines, parallel research workflows, and structured output generation -- all running inside Claude Code.

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

## Links

- **Marketplace:** [shipfast.cc](https://shipfast.cc)
- **Personal site:** [noahrasheta.com](https://noahrasheta.com)
- **GitHub:** [github.com/noahrasheta/shipfast](https://github.com/noahrasheta/shipfast)

## License

MIT -- see [LICENSE](LICENSE) for details.
