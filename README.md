# Shipfast

Plugins, skills, and coding resources by [Noah Rasheta](https://noahrasheta.com) -- hosted at [shipfast.cc](https://shipfast.cc)

---

I'm a podcast host with a bunch of side businesses and projects. I build Claude Code plugins, skills, and agents to automate the things I do repeatedly. This repo is where all of that lives -- open source, for anyone to use, fork, or build on.

The stuff here spans many domains because my work does too. Data infrastructure, automations, prompt engineering, content workflows, and whatever I'm tinkering with next. The common thread is Claude Code and agentic AI.

## Quick Start

Add the marketplace and install a plugin:

```
/plugin marketplace add noahrasheta/shipfast
/plugin install create-image@shipfast
```

## Plugins

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

**Status:** v0.1.0 -- initial release. Core pipeline functional.

---

## Links

- **Marketplace:** [shipfast.cc](https://shipfast.cc)
- **Personal site:** [noahrasheta.com](https://noahrasheta.com)
- **GitHub:** [github.com/noahrasheta/shipfast](https://github.com/noahrasheta/shipfast)

## License

MIT -- see [LICENSE](LICENSE) for details.
