# Shipfast

Plugins, skills, and coding resources by [Noah Rasheta](https://noahrasheta.com) -- hosted at [shipfast.cc](https://shipfast.cc)

---

I'm a podcast host with a bunch of side businesses and projects. I build Claude Code plugins, skills, and agents to automate the things I do repeatedly. This repo is where all of that lives -- open source, for anyone to use, fork, or build on.

The stuff here spans many domains because my work does too. Data infrastructure, automations, prompt engineering, content workflows, and whatever I'm tinkering with next. The common thread is Claude Code and agentic AI.

## Quick Start

Add the marketplace and install any plugin:

```
/plugin marketplace add noahrasheta/shipfast
/plugin install <plugin-name>@shipfast
```

## Plugins

| Plugin | What it does | Command |
|--------|-------------|---------|
| [create-image](#create-image) | AI image generation with multi-agent pipeline | `/create-image` |
| [dc-due-diligence](#dc-due-diligence) | Data center site analysis across 9 domains | `/due-diligence <folder>` |

---

### create-image

AI image generation using the PaperBanana agentic framework with Nano Banana Pro (Gemini 3 Pro). Invoke `/create-image` and a team of specialized agents handles the rest -- from analyzing reference images to generating 5 variants and ranking them.

**What it does:**
- Asks structured clarifying questions about what you want (subject, style, mood, aspect ratio, resolution, reference images, etc.)
- Spawns 4 agents in a sequential pipeline: Research Agent, Prompt Architect, Generator Agent, Critic Agent
- Generates 5 image variants (Faithful, Enhanced, Alt Composition, Style Variation, Bold/Creative)
- Critiques each image on 4 dimensions from the PaperBanana paper (Faithfulness, Readability, Conciseness, Aesthetics)
- Presents ranked results with a top recommendation and offers iteration

**Based on:** [PaperBanana](https://arxiv.org/abs/2601.23265) (Google Cloud AI Research & Peking University) -- a multi-agent framework that outperforms single-shot image generation by +17% overall.

**Prerequisites:**
```bash
pip install google-genai Pillow python-dotenv
```

Add your Gemini API key to a `.env` file in the project where you'll run the plugin:
```
GEMINI_API_KEY=your-key-here
```

Get an API key from [Google AI Studio](https://aistudio.google.com/).

**Usage:**
```
/create-image
```

Or with an initial description:
```
/create-image an infographic about global coffee consumption in the style of Visual Capitalist
```

Generated images are saved to a `shipfast-images/` folder in your project directory for easy access.

**Status:** v0.1.0 -- initial release. Core pipeline functional.

---

### dc-due-diligence

Automated due diligence for data center site opportunities. Point it at a folder of broker documents (PDFs, spreadsheets, Word docs, PowerPoint decks, images) and it runs a full analysis across 9 domains, synthesizes cross-domain risks, and produces a scored executive summary with a **Pursue / Proceed with Caution / Pass** verdict.

**What it does:**
- Converts all documents in the folder to markdown (PDF, Excel, Word, PowerPoint, images via vision API)
- Spawns 9 domain research agents in parallel, each analyzing the converted documents and conducting independent web research to verify broker claims:
  - **Power** -- utility interconnection, grid capacity, substation, redundancy design
  - **Connectivity** -- fiber carriers, route diversity, carrier neutrality
  - **Water & Cooling** -- water supply, cooling system design, scarcity risk
  - **Land, Zoning & Entitlements** -- zoning compliance, permits, building readiness
  - **Ownership & Control** -- property ownership verification, middleman detection, litigation
  - **Environmental** -- natural hazards, contamination, Phase I ESA status
  - **Commercials** -- deal terms, land cost, power rates, lease structure
  - **Natural Gas** -- pipeline access, on-site generation feasibility, permitting
  - **Market Comparables** -- comparable transactions, market rates, competition
- Runs a **Risk Assessment** agent that reads all 9 domain reports and identifies cross-cutting risks, deal-breakers, and compound risks
- Generates an **Executive Summary** that scores each category (High / Medium / Low), applies a tiered verdict system, and delivers a stakeholder-ready report

**Output:**
- `<folder>/EXECUTIVE_SUMMARY.md` -- scored summary with verdict, strengths, concerns, deal-breakers, and next steps
- `<folder>/research/*.md` -- 10 detailed research reports (one per domain + risk assessment)

#### Installation

**Step 1: Add the marketplace and install the plugin**

```
/plugin marketplace add noahrasheta/shipfast
/plugin install dc-due-diligence@shipfast
```

Python 3.11+ is required on your machine. The plugin automatically sets up its Python virtual environment the first time you run `/due-diligence` -- no manual setup step needed.

**Step 2 (only if your folder has images or scanned PDFs): Set ANTHROPIC_API_KEY**

The document converter uses the Anthropic API directly to extract text from images and scanned PDFs via Claude's vision capability. This runs as a Python subprocess, separate from Claude Code itself, so it needs its own API key.

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):
```bash
export ANTHROPIC_API_KEY=your-key-here
```

Then **restart Claude Code** so it picks up the new variable. Environment variables are inherited at launch time -- adding the key while Claude Code is running won't take effect until you restart it.

If your folder only contains native PDFs, Word docs, Excel files, and PowerPoint decks, you do not need this -- those formats are converted using local Python libraries with no API calls.

#### How web research works

The 12 research agents verify broker claims using web research. There are two layers, and the baseline works with zero configuration:

**Baseline (always available):** Agents use Claude Code's built-in `WebSearch` and `WebFetch` tools. These work automatically -- no API keys or setup needed.

**Enhanced (optional):** If you have Tavily, Exa, or Firecrawl configured as MCP servers in Claude Code, agents will automatically detect and use them via `ToolSearch` for deeper search capabilities. This is a nice-to-have, not a requirement.

#### Usage

```
/due-diligence ./path/to/opportunity-folder
```

The folder should contain the broker-provided documents for the opportunity. The plugin handles conversion, analysis, and reporting end to end.

**Status:** v0.2.1 -- tiered domain weighting, Key Questions section, client-facing summary with PDF output, scoring calibration.

---

## Links

- **Marketplace:** [shipfast.cc](https://shipfast.cc)
- **Personal site:** [noahrasheta.com](https://noahrasheta.com)
- **GitHub:** [github.com/noahrasheta/shipfast](https://github.com/noahrasheta/shipfast)

## License

MIT -- see [LICENSE](LICENSE) for details.
