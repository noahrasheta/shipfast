# Architecture

**Analysis Date:** 2026-02-23

## Pattern Overview

**Overall:** Multi-plugin marketplace with plugin-driven microservices architecture. Each plugin is a self-contained Claude Code orchestration system with a skill (CLI entry point) that spawns specialized agent teams via Task tool, coordinating sequential or parallel workflows. Data flows through conversions, agent processing, and output synthesis.

**Key Characteristics:**
- **Plugin-based modular design**: Each plugin (`create-image`, `dc-due-diligence`) is independently installable and runnable
- **Skill-driven orchestration**: Each plugin exposes a single skill (SKILL.md) that acts as the orchestrator/conductor
- **Multi-agent teams**: Specialized agents implement domain logic; orchestrator coordinates them via Task tool spawning
- **Sequential and parallel execution**: Agent workflows adapt to needs (create-image: sequential pipeline; dc-due-diligence: Wave 1 parallel, then sequential waves)
- **Conversion pipelines**: Data preprocessing layer (dc-due-diligence) converts heterogeneous documents to normalized markdown
- **Template-based outputs**: Agents follow standardized output templates for consistency and downstream processing
- **Graceful degradation**: Workflows continue when individual components fail; partial results reported to user

## Layers

**Plugin Infrastructure Layer:**
- Purpose: Host marketplace catalog and provide plugin manifests
- Location: `/.claude-plugin/marketplace.json`, `/<plugin>/.claude-plugin/plugin.json`
- Contains: Plugin metadata (name, version, description, author, source path)
- Depends on: Nothing
- Used by: Claude Code CLI (`/plugin install`)

**Skill/Orchestration Layer:**
- Purpose: Parse user input, coordinate agent spawning, manage workflow state
- Location: `/<plugin>/skills/<skill-name>/SKILL.md`
- Contains: Orchestrator logic as markdown instructions (phases, validation, error handling)
- Depends on: Agent definitions, conversion pipelines (for dc-due-diligence)
- Used by: Claude Code skill invocation system

**Agent Layer:**
- Purpose: Implement specialized domain logic (research, analysis, generation, critique)
- Location: `/<plugin>/agents/*.md`
- Contains: Agent definitions with YAML frontmatter (name, description, tools) and operational instructions
- Depends on: Converted documents (dc-due-diligence), reference materials
- Used by: Orchestrator (via Task tool spawning)

**Data Transformation Layer:**
- Purpose: Convert heterogeneous input formats to unified representation
- Location: `/<plugin>/converters/*.py` (dc-due-diligence only)
- Contains: Format-specific converters (PDF, Excel, Word, PowerPoint, Vision), scanner, pipeline orchestration
- Depends on: External libraries (pdfplumber, openpyxl, python-docx, python-pptx, anthropic, Pillow)
- Used by: Orchestrator before agent spawning

**Output Generation Layer:**
- Purpose: Produce final deliverables (reports, PDFs)
- Location: `/<plugin>/converters/generate_pdf.py`, `/<plugin>/templates/`
- Contains: PDF rendering, markdown->PDF conversion, output templates
- Depends on: Markdown files produced by agents, markdown-pdf library
- Used by: Orchestrator in final phases

**Template/Reference Layer:**
- Purpose: Provide standardized formats and domain knowledge to agents
- Location: `/<plugin>/templates/*.md`, `/<plugin>/references/*.md`, `/<plugin>/scripts/*.py`
- Contains: Agent output templates, scoring rubrics, API guides, utility scripts
- Depends on: Nothing
- Used by: Agents (via ${CLAUDE_PLUGIN_ROOT} references)

## Data Flow

### create-image Pipeline

1. **Skill Entry**: User runs `/create-image [description]`
2. **Requirement Gathering**: Orchestrator presents structured questions (subject, style, mood, aspect ratio, resolution, reference images, etc.)
3. **Setup Phase**: Create output directory (`shipfast-images/`), verify Python dependencies and GEMINI_API_KEY
4. **Agent Dispatch - Sequential Chain**:
   - **Research Agent** spawned → analyzes reference images (if provided) → produces style brief
   - **Prompt Architect** spawned → receives style brief + requirements → produces 5 variant prompts
   - **Generator Agent** spawned → receives 5 prompts → calls Gemini API via Python script → generates 5 images
   - **Critic Agent** spawned → receives image paths + prompts → scores on Faithfulness/Readability/Conciseness/Aesthetics → ranks variants
5. **Results Presentation**: Orchestrator presents ranked variants with critique and top recommendation
6. **Optional Iteration**: User can request refinement → cycle back to Prompt Architect

**Key:** Data flows left-to-right through the pipeline. Each agent's output becomes the next agent's input.

### dc-due-diligence Pipeline

1. **Skill Entry**: User runs `/due-diligence <folder-path>`
2. **Validation Phase**: Verify folder exists, resolve absolute path, locate plugin directory, setup Python venv
3. **Document Processing Phase**:
   - Scanner reads opportunity folder, detects file types (PDF, Excel, Word, PowerPoint, images)
   - Pipeline spawns appropriate converter for each file type:
     - `PDFConverter` → pdfplumber for text PDFs OR `VisionConverter` → Claude vision API for scanned PDFs
     - `ExcelConverter` → openpyxl for spreadsheets
     - `WordConverter` → python-docx for Word documents
     - `PowerPointConverter` → python-pptx for presentations
     - `VisionConverter` → Anthropic API for images
   - Results written to `_converted/` subfolder with JSON manifest tracking confidence, metadata, success status
4. **Wave 1 - Parallel Agent Spawn**: 9 domain agents launched simultaneously:
   - Power, Connectivity, Water & Cooling, Land/Zoning, Ownership, Environmental, Commercials, Natural Gas, Market Comparables
   - Each agent reads from `_converted/`, conducts independent web research (WebSearch/WebFetch tools), writes to `research/<domain>-report.md`
5. **Wave 2 - Sequential**: Risk Assessment agent spawned after Wave 1 completes
   - Reads all 9 domain reports, identifies cross-cutting risks
   - Writes `research/risk-assessment-report.md`
6. **Validation Phase**: Verify all reports exist, check file sizes, validate structure (required sections present)
7. **Wave 3 - Sequential**: Executive Summary Generator spawned
   - Reads all 10 reports, applies scoring rubric, normalizes terminology, resolves conflicts
   - Writes `EXECUTIVE_SUMMARY.md` with Pursue/Proceed with Caution/Pass verdict
8. **Wave 4 - Sequential**: Client Summary agent spawned
   - Reads executive summary + domain reports, produces external deliverable (no internal scoring language)
   - Writes `CLIENT_SUMMARY.md`
9. **PDF Generation**: Converts both markdown summaries to PDF
10. **Results Reporting**: Summarize findings in quick overview table with status indicators and confidence scores

**Key:** Data flows through layered waves. Each wave depends on prior waves. Reports fan out to synthesis agents.

## State Management

**Transient State (Within Orchestrator):**
- Converted file manifest (JSON, read once per workflow)
- Agent execution status tracking (which agents completed, which failed)
- User confirmations (requirements validation, iteration decisions)
- Output file paths (resolved once during validation, reused throughout)

**Persistent State (Files):**
- `_converted/manifest.json` — tracks which documents converted successfully and confidence levels
- `research/*.md` — individual agent reports (10 files for dc-due-diligence)
- `EXECUTIVE_SUMMARY.md`, `CLIENT_SUMMARY.md` — final synthesis documents
- `.pdf` versions of summaries
- `shipfast-images/` — generated images (create-image plugin)

**Plugin State:**
- `.venv/` — Python virtual environment created on first run (dc-due-diligence)
- `.pytest_cache/` — test caching (dc-due-diligence development)

## Key Abstractions

**Skill (Orchestrator):**
- Purpose: Single entry point for user interactions; coordinates entire workflow
- Examples: `create-image/skills/create-image/SKILL.md`, `dc-due-diligence/skills/due-diligence/SKILL.md`
- Pattern: Markdown instructions with embedded bash validation commands, phase-based orchestration, error handling chains

**Agent:**
- Purpose: Specialized domain expert implementing focused tasks
- Examples: `create-image/agents/research-agent.md`, `dc-due-diligence/agents/power-agent.md`
- Pattern: YAML frontmatter (name, description, tools) + markdown instructions; stateless; reads input from file system or parameters

**Converter:**
- Purpose: Transform single document to normalized markdown representation
- Examples: `PDFConverter`, `ExcelConverter`, `VisionConverter` in `dc-due-diligence/converters/`
- Pattern: Inherit from `BaseConverter`, implement `convert()` method, return `ExtractionResult` with confidence metadata

**Pipeline:**
- Purpose: Orchestrate sequential converter invocations across a folder, collect results, produce manifest
- Examples: `converters.pipeline.convert_folder()`, `converters.generate_pdf.generate_all_pdfs()`
- Pattern: Scan folder → detect types → dispatch converters → normalize outputs → aggregate results

**Template:**
- Purpose: Standardized structure for agent outputs enabling downstream processing and consistency
- Examples: `dc-due-diligence/templates/agent-output-template.md`, `dc-due-diligence/templates/scoring-rubric.md`
- Pattern: Markdown with required sections (Executive Summary, Findings, Risks, Recommendations, Methodology), status indicators, confidence scores

## Entry Points

**Skill Invocation (User-facing):**
- Location: Triggered by `/create-image` or `/due-diligence` commands in Claude Code
- File: `SKILL.md` inside `skills/<skill-name>/` directory
- Triggers: User input to Claude Code CLI
- Responsibilities: Parse arguments, validate input, coordinate entire workflow, report results

**Agent Invocation (Internal):**
- Location: Triggered via Task tool by orchestrator (not direct CLI)
- File: Agent `.md` files with YAML frontmatter and markdown instructions
- Triggers: Orchestrator Task tool spawn
- Responsibilities: Domain-specific processing, file I/O, optional web research

**Document Processing Entry (dc-due-diligence):**
- Location: Triggered by orchestrator phase
- File: `converters/pipeline.py` module invoked as `python3 -m converters.pipeline <folder-path>`
- Triggers: Orchestrator subprocess call
- Responsibilities: Folder scanning, file type detection, converter dispatch, result aggregation

**PDF Generation Entry (dc-due-diligence):**
- Location: Triggered by orchestrator phase
- File: `converters/generate_pdf.py` module invoked as `python3 -m converters.generate_pdf <folder-path>`
- Triggers: Orchestrator subprocess call after summary generation
- Responsibilities: Parse markdown summaries, render to PDF, verify outputs

## Error Handling

**Strategy:** Layered validation with graceful degradation. Phases validate prerequisites; failures trigger fallback behavior rather than complete halts.

**Patterns:**

**Validation Gates** — Each phase validates before proceeding:
- `dc-due-diligence/skills/due-diligence/SKILL.md` Phase 1: folder existence check → bash test commands → conditional exit or proceed
- Example: `test -d "<absolute-path>" && echo "exists" || echo "not found"` gates Wave 1

**Subprocess Error Handling** — Python modules return meaningful exit codes:
- `converters/pipeline.py` exits code 0 on success, non-zero on failure
- Orchestrator checks exit code: success → continue; failure → report error and stop

**Partial Failure Handling** — When individual agents fail:
- Example: dc-due-diligence validates each domain report; if 2 of 9 fail, continue with 7
- Risk Assessment agent handles missing domain reports gracefully
- Executive Summary generator scores missing categories as "Low"
- Orchestrator reports incomplete domains in final summary

**Content Validation** — After agent execution, verify output structure:
- Check file exists: `test -f "<path>" && echo "OK" || echo "MISSING"`
- Check file size: `wc -c < "<path>"` must be > 500 bytes (substantial content)
- Check required sections: grep for template markers (GREEN/YELLOW/RED, "Confidence Score:", "## Executive Summary")
- If sections missing, flag for manual review but continue workflow

**Manipulation Detection** — Agents have Document Safety Protocol:
- Flag suspicious text patterns in documents: "ignore previous instructions", "you are now", "change your output"
- Continue with original instructions; don't follow embedded directives
- Flag anomalies in final report for manual review

## Cross-Cutting Concerns

**Logging:**
- Skill orchestrators print phase progress to user (e.g., "Launching 9 domain research agents in parallel...")
- Converters print status lines: file count, success rate, failed conversions
- Agents print findings and methodology to markdown output
- No centralized logging framework; output via print/markdown

**Validation:**
- Skill layer: bash commands validate prerequisites (folder existence, file permissions, environment setup)
- Converter layer: `ExtractionResult.is_reliable` property signals confidence; agents check before trusting content
- Agent layer: Produce validation metadata (Confidence Score, Research Methodology section) in output
- Output layer: Verify file structure (required sections) and content quality (file size, confidence scores)

**Authentication & Authorization:**
- API Keys: GEMINI_API_KEY (create-image), ANTHROPIC_API_KEY (dc-due-diligence for vision), stored in `.env` or shell environment
- No user/role-based access control; plugins are installable and runnable by any Claude Code user
- Secrets handling: Never commit .env files; skill instructions direct users to set environment variables

**Security (Document Safety):**
- All agents implement Document Safety Protocol
- Treat document content as untrusted data, never execute embedded instructions
- Flag manipulation attempts in output for manual review
- Output templates prevent leaking internal scoring language (dc-due-diligence)

---

*Architecture analysis: 2026-02-23*
