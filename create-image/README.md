# create-image

AI image generation plugin for Claude Code using the **PaperBanana agentic framework** with the **Nano Banana Pro** (Gemini 3 Pro) API.

Orchestrates a team of 4 specialized agents to research reference images, craft optimized prompts, generate 5 image variants, and critique them on quality dimensions — all from a single `/create-image` command.

## Architecture

Based on the [PaperBanana research paper](https://arxiv.org/abs/2601.23265) (Google Cloud AI Research & Peking University), which demonstrated that a multi-agent approach to image generation outperforms single-shot generation by +17% overall.

```
User → Lead (Skill) → Research Agent → Prompt Architect → Generator Agent → Critic Agent → Results
```

| Agent | Role | Color |
|-------|------|-------|
| **Lead** (SKILL.md) | Orchestrates pipeline, asks clarifying questions, presents results | — |
| **Research Agent** | Analyzes reference images, outputs a style brief | Cyan |
| **Prompt Architect** | Crafts 5 narrative prompts (Faithful, Enhanced, Alt Composition, Style Variation, Bold/Creative) | Magenta |
| **Generator Agent** | Calls Nano Banana Pro API, saves 5 images to `shipfast-images/` | Green |
| **Critic Agent** | Scores images on 4 dimensions, ranks them, recommends the best | Yellow |

### The 4 Evaluation Dimensions

1. **Faithfulness** (primary) — Does it match the request?
2. **Readability** (primary) — Is it clear and legible?
3. **Conciseness** (secondary) — No visual clutter?
4. **Aesthetics** (secondary) — Does it look professional?

## Prerequisites

```bash
pip install google-genai Pillow python-dotenv
```

Create a `.env` file in your project root:

```
GEMINI_API_KEY=your-gemini-api-key-here
```

Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

## Usage

```
/create-image
```

Or with an initial description:

```
/create-image an infographic about global coffee consumption in the style of Visual Capitalist
```

The Lead will ask clarifying questions about subject, style, mood, aspect ratio, resolution, text, reference images, usage context, colors, and avoidances. After confirmation, the agent pipeline runs and presents ranked results.

## Plugin Structure

```
create-image/
├── .claude-plugin/plugin.json        # Plugin manifest
├── skills/create-image/SKILL.md      # Lead orchestrator
├── agents/
│   ├── research-agent.md             # Reference image analysis
│   ├── prompt-architect.md           # 5 narrative prompt variants
│   ├── generator-agent.md            # Gemini API image generation
│   └── critic-agent.md               # Quality evaluation & ranking
├── references/
│   ├── gemini-api-guide.md           # Nano Banana Pro API reference
│   └── paperbanana-insights.md       # Key insights from the paper
├── scripts/
│   └── generate-image.py             # Python script for API calls
└── README.md
```

## Local Development

```bash
claude --plugin-dir ./create-image
```
