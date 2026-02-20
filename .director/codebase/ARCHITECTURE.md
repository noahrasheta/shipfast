# Architecture

**Analysis Date:** 2026-02-20

## Pattern Overview

**Overall:** Plugin-based marketplace with orchestrator-agent pattern -- A monorepo of independent Claude Code plugins, each implementing a multi-agent workflow orchestrated by a skill that spawns specialized agents via the Task tool.

**Key Characteristics:**
- Each plugin is self-contained with its own manifest, agents, skills, and supporting files -- See `create-image/`, `dc-due-diligence/`
- Plugins follow a strict Agent + Skill separation: Skills orchestrate and decide which agents to spawn; agents execute specialized tasks -- See `create-image/skills/create-image/SKILL.md` (orchestrator), `create-image/agents/` (task executors)
- Agents communicate through text-based handoffs: the skill captures agent output and passes it as context to the next agent in the pipeline -- See `create-image/skills/create-image/SKILL.md` Phase 3
- Multi-wave parallel execution pattern: dc-due-diligence spawns 9 domain agents in Wave 1 (parallel), then synthesis agents in Wave 2-3 -- See `dc-due-diligence/skills/due-diligence/SKILL.md` phases
- Marketplace catalog at repository root provides unified discovery -- See `.claude-plugin/marketplace.json`
- Each plugin uses `${CLAUDE_PLUGIN_ROOT}` token for file references, enabling portable plugin distribution -- See `dc-due-diligence/agents/power-agent.md` (uses `${OPPORTUNITY_FOLDER}`, `${CLAUDE_PLUGIN_ROOT}`)

## Layers

**Marketplace Registry Layer:**
- Purpose: Provides a unified catalog of all available plugins and their metadata for discovery and installation
- Location: `.claude-plugin/marketplace.json`
- Contains: Plugin names, sources, descriptions, ownership metadata
- Depends on: None (read-only registry)
- Used by: Claude Code plugin installation system (`/plugin marketplace add`, `/plugin install`)

**Plugin Layer:**
- Purpose: Encapsulates a complete tool/workflow as an independently installable, versioned package
- Location: `create-image/`, `dc-due-diligence/` (each plugin is a root-level directory)
- Contains: Plugin manifest, agents, skills, supporting assets (scripts, templates, references, tests)
- Depends on: Claude Code task execution system, external APIs (Gemini API for create-image, Anthropic API for dc-due-diligence document conversion)
- Used by: End users via `/plugin install`, then by invoking the plugin's skill command

**Skill/Orchestrator Layer:**
- Purpose: Receives user input, coordinates the multi-agent workflow, manages phase transitions, and presents results
- Location: `<plugin>/skills/<skill-name>/SKILL.md` -- See `create-image/skills/create-image/SKILL.md`, `dc-due-diligence/skills/due-diligence/SKILL.md`
- Contains: YAML frontmatter with trigger patterns and description; Markdown-formatted workflow phases written in prescriptive English
- Depends on: Agent layer (spawns agents via Task tool with context from the skill)
- Used by: User commands that trigger the skill

**Agent Layer:**
- Purpose: Specialized task executors focused on a single domain or analysis step; designed to be spawned and managed by the orchestrator skill
- Location: `<plugin>/agents/<agent-name>.md` -- See `create-image/agents/`, `dc-due-diligence/agents/`
- Contains: YAML frontmatter with name, description, example patterns, tool configuration; Markdown-formatted agent instructions
- Depends on: Tools available to Claude Code (Read, Bash, Grep, Write, Task, WebSearch, WebFetch, etc.); supporting scripts and reference files in the plugin
- Used by: Orchestrator skill spawning via Task tool; agents may spawn other agents (nested Task calls)

**Support/Infrastructure Layer:**
- Purpose: Provides Python converters, generation scripts, templates, and test fixtures to agents
- Location: `<plugin>/converters/` (Python), `<plugin>/scripts/` (Python), `<plugin>/templates/` (Markdown), `<plugin>/tests/` (pytest), `<plugin>/references/` (Markdown guides)
- Contains: Reusable code modules (document conversion pipeline, image generation API wrapper), output templates (agent response format, scoring rubric), test suite
- Depends on: External libraries (pdfplumber, openpyxl, python-docx, python-pptx, Anthropic SDK, google-genai, Pillow)
- Used by: Agents via Bash subprocess calls (e.g., `python -m converters.pipeline <folder>`), Python dependencies listed in `pyproject.toml`

## Data Flow

**Create-Image Pipeline:**

1. User invokes `/create-image` [description] -- SKILL.md (Orchestrator)
2. Orchestrator gathers requirements through structured clarifying questions, validates Python dependencies and GEMINI_API_KEY -- `create-image/skills/create-image/SKILL.md` Phase 1-2
3. Orchestrator spawns Research Agent with confirmed requirements and reference image paths (if provided) -- `create-image/agents/research-agent.md`
4. Research Agent analyzes reference images (using Read tool) and outputs a style brief
5. Orchestrator captures style brief, spawns Prompt Architect with style brief + requirements -- `create-image/agents/prompt-architect.md`
6. Prompt Architect outputs 5 narrative prompts
7. Orchestrator spawns Generator Agent with 5 prompts, aspect ratio, resolution, reference paths, output directory -- `create-image/agents/generator-agent.md`
8. Generator Agent calls `create-image/scripts/generate-image.py` via Bash, saves 5 images to `shipfast-images/`, returns file paths
9. Orchestrator spawns Critic Agent with image paths, prompts used, and requirements -- `create-image/agents/critic-agent.md`
10. Critic Agent evaluates images on 4 dimensions (Faithfulness, Readability, Conciseness, Aesthetics), ranks results
11. Orchestrator presents ranked results to user, offers iteration

**Data Center Due Diligence Pipeline:**

1. User invokes `/due-diligence <folder-path>` -- SKILL.md (Orchestrator)
2. Orchestrator validates folder path, locates plugin directory, ensures Python venv setup -- `dc-due-diligence/skills/due-diligence/SKILL.md` Phase 1
3. Orchestrator checks for existing `_converted/manifest.json`; if absent, spawns document conversion pipeline via `python -m converters.pipeline <folder>` -- Phase 2
4. Conversion pipeline (documented in `dc-due-diligence/converters/pipeline.py`) processes all files:
   - Scans folder via `scanner.py` for supported file types (PDF, Excel, Word, PowerPoint, images)
   - Routes each file to appropriate converter: `pdf.py`, `excel.py`, `word.py`, `powerpoint.py`, `vision.py` (for scanned PDFs/images)
   - Writes markdown output to `<folder>/_converted/`
   - Produces manifest at `<folder>/_converted/manifest.json`
5. Orchestrator reads manifest, verifies at least one file converted successfully
6. Orchestrator spawns 9 domain research agents in parallel, each with:
   - Opportunity folder path
   - Converted documents directory path
   - Reference to agent's output template at `dc-due-diligence/templates/agent-output-template.md`
   - Each agent writes its report to `<folder>/research/<domain>-report.md`
7. Domain agents (power, connectivity, water-cooling, land-zoning, ownership, environmental, commercials, natural gas, market-comparables) follow two-phase approach:
   - Phase 1: Extract claims from documents (Read tool)
   - Phase 2: Verify claims independently via WebSearch/WebFetch and optional Tavily/Exa/Firecrawl MCP servers
8. Orchestrator waits for all 9 domain agents to complete
9. Orchestrator spawns Risk Assessment Agent with all 9 domain reports -- `dc-due-diligence/agents/risk-assessment-agent.md`
10. Risk Assessment Agent synthesizes cross-domain risks, identifies compound risk patterns, outputs risk assessment report
11. Orchestrator spawns Executive Summary Agent with all findings (9 domain reports + risk assessment) -- `dc-due-diligence/agents/executive-summary-agent.md`
12. Executive Summary Agent scores each category (High/Medium/Low), applies verdict logic, produces final executive summary
13. Orchestrator reports completion with output locations

**State Management:**
- Create-image: Managed implicitly through skill phases -- style brief from Research Agent → Prompt Architect receives it → Generator receives both briefs and prompts, etc.
- Due diligence: Managed through folder structure -- converted documents in `_converted/`, domain reports in `research/`, final outputs at root of opportunity folder
- No database or persistent state beyond files written to the opportunity folder

## Key Abstractions

**Plugin:**
- Purpose: A self-contained, distributable Claude Code tool packaged with metadata, orchestration logic, specialized agents, and supporting infrastructure
- Examples: `create-image/`, `dc-due-diligence/`
- Pattern: Each plugin has a `<plugin>/.claude-plugin/plugin.json` manifest, a `<plugin>/skills/<name>/SKILL.md` orchestrator, agent files in `<plugin>/agents/`, and optional supporting code/templates
- Follow this pattern when creating a new plugin: Create root directory, add `.claude-plugin/plugin.json` with name/description/version/author, structure agents as `agents/<name>.md`, structure skill as `skills/<skill-name>/SKILL.md`, register in `.claude-plugin/marketplace.json`, update CLAUDE.md and README.md

**Skill (Orchestrator):**
- Purpose: A Claude Code workflow that receives user input and orchestrates a multi-agent pipeline by spawning agents sequentially, in parallel, or in waves
- Examples: `create-image/skills/create-image/SKILL.md`, `dc-due-diligence/skills/due-diligence/SKILL.md`
- Pattern: YAML frontmatter with `name:`, `description:` (including trigger phrases), optionally `version:`; Markdown body with structured phases, each phase describing actions and agent spawning. Use `${ARGUMENTS}` for user input, `${OPPORTUNITY_FOLDER}` or `${CLAUDE_PLUGIN_ROOT}` for plugin-relative paths
- Follow this pattern: Start with input validation phase, prepare environment (directories, dependencies, resources), spawn agents with explicit context (prior outputs, paths, templates), manage phase transitions, present final results to user

**Agent:**
- Purpose: A specialized Claude Code task executor focused on a single domain, analysis step, or generation task; spawned by an orchestrator and designed to be stateless (receives all context in the prompt)
- Examples: `create-image/agents/research-agent.md`, `dc-due-diligence/agents/power-agent.md`
- Pattern: YAML frontmatter with `name:`, `description:` (including example triggers and commentary), optionally `color:` (for visual distinction), `tools:` (list of allowed tools), optionally `model: inherit`. Markdown body with clear role statement, task definition, workflow phases
- Follow this pattern: Start with role/expertise statement, define task clearly with file paths, specify input sources (documents, prior agent outputs, etc.), describe workflow phases with numbered steps and file operations, define output format with specific file path, include safety/validation sections for agents handling untrusted data (like broker documents)

**Converter (Infrastructure):**
- Purpose: A Python module that transforms one document format into markdown for text-based analysis
- Examples: `dc-due-diligence/converters/pdf.py`, `dc-due-diligence/converters/vision.py`, `dc-due-diligence/converters/pipeline.py`
- Pattern: Inherit from `BaseConverter`, implement `convert()` method returning `ExtractionResult` with extracted text and confidence level, handle errors gracefully with detailed logging
- Follow this pattern when adding a new converter: Extend `BaseConverter`, implement the required methods, add your converter class to the `CONVERTERS` dict in `pipeline.py`, ensure it raises appropriate exceptions and logs detailed status

**Template (Output Format):**
- Purpose: A standardized markdown template defining the structure and content agents should produce
- Examples: `dc-due-diligence/templates/agent-output-template.md`, `dc-due-diligence/templates/scoring-rubric.md`
- Pattern: Markdown with sections, subsections, and placeholders for agent findings; agents read these templates and follow their structure verbatim
- Follow this pattern when defining agent output: Create a template markdown file, have agents reference it by path and structure their output to match exactly, use the template to ensure consistency across all agents

## Entry Points

**CLI Entry: `/create-image`**
- Location: `create-image/skills/create-image/SKILL.md`
- Triggers: User command `/create-image` or `/create-image [description]`
- Responsibilities: Collect user requirements for image generation, orchestrate the 4-agent pipeline (Research → Prompt Architect → Generator → Critic), present ranked results and iterate if requested

**CLI Entry: `/due-diligence`**
- Location: `dc-due-diligence/skills/due-diligence/SKILL.md`
- Triggers: User command `/due-diligence <folder-path>`
- Responsibilities: Validate opportunity folder, run document conversion pipeline, orchestrate 9 parallel domain agents, run synthesis agents (Risk Assessment, Executive Summary), produce scored verdict and research reports

**Plugin Registration**
- Location: `.claude-plugin/marketplace.json`
- Triggers: `/plugin marketplace add noahrasheta/shipfast` followed by `/plugin install <plugin-name>@shipfast`
- Responsibilities: List available plugins with metadata so Claude Code can discover and install them

## Error Handling

**Strategy:** Explicit validation with user-facing error messages; scripts return non-zero exit codes on failure; agents document uncertainty and gaps in their output rather than failing silently.

**Patterns:**
- Use Bash return codes to validate operations (test -f for file existence, test -d for directories) -- See `dc-due-diligence/skills/due-diligence/SKILL.md` Phase 1 input validation
- Use Python subprocess exit codes to detect pipeline failures -- See `dc-due-diligence/skills/due-diligence/SKILL.md` Phase 2 checking `converters.pipeline` exit code
- Agents document failed claim verification and low-confidence extractions rather than stopping -- See `dc-due-diligence/converters/pipeline.py` `ConfidenceLevel` and status reporting
- Agents include "Document Safety Protocol" section to detect and flag manipulation attempts in untrusted documents -- See `dc-due-diligence/agents/power-agent.md` document safety section
- Orchestrators report all errors to the user with actionable remediation steps (e.g., "Please check the path and try again")

## Cross-Cutting Concerns

**Logging:** Use Python's `logging` module with DEBUG/INFO/WARNING levels in converters and scripts. Agents and skills use text-based status reporting via printed output to keep the user informed of progress.

**Validation:**
- Skills validate user input early (paths exist, required parameters provided, dependencies installed) -- See `dc-due-diligence/skills/due-diligence/SKILL.md` Phase 1
- Agents validate document content as untrusted data and flag suspicious patterns as risks -- See `dc-due-diligence/agents/power-agent.md` Document Safety Protocol
- Converters validate file format and report confidence levels for extracted content -- See `dc-due-diligence/converters/base.py` `ConfidenceLevel` enum

**Configuration:**
- Environment variables for sensitive API keys (GEMINI_API_KEY, ANTHROPIC_API_KEY) -- See `create-image/skills/create-image/SKILL.md` Phase 2 API key verification
- `.env` files for local development (never committed) -- See `create-image/README.md` prerequisites
- `pyproject.toml` for Python package metadata and dependencies -- See `dc-due-diligence/pyproject.toml`

## Quality Gate

Before considering this file complete, verify:
- [x] Every finding includes at least one file path in backticks
- [x] Voice is prescriptive ("Use X pattern", "Place files in Y") not descriptive ("X pattern is used")
- [x] No section left empty -- all sections have concrete findings
- [x] Layers documented with file paths and dependencies
- [x] Data flow described with file references for each step
- [x] Entry points listed with trigger patterns and paths
- [x] Key abstractions include pattern examples and "follow this pattern when" guidance
