# Codebase Structure

**Analysis Date:** 2026-02-20

## Directory Layout

```
shipfast/
├── .claude-plugin/
│   └── marketplace.json              # Marketplace catalog listing all plugins
├── .director/                        # Director onboarding and analysis metadata (generated)
│   ├── brainstorms/
│   ├── codebase/                     # Analysis documents (this directory)
│   └── goals/
├── .github/workflows/                # GitHub Actions CI/CD
├── create-image/                     # Plugin: AI image generation via PaperBanana framework
│   ├── .claude-plugin/
│   │   └── plugin.json               # Plugin metadata (name, version, author, license)
│   ├── agents/                       # 4 task-executing agents
│   │   ├── research-agent.md         # Analyzes reference images for style brief
│   │   ├── prompt-architect.md       # Crafts 5 narrative prompts
│   │   ├── generator-agent.md        # Calls Gemini API to generate images
│   │   └── critic-agent.md           # Evaluates images on 4 dimensions
│   ├── skills/
│   │   └── create-image/
│   │       └── SKILL.md              # Orchestrator: collects requirements, spawns 4-agent pipeline
│   ├── scripts/
│   │   └── generate-image.py         # Python wrapper for Gemini 3 Pro API
│   ├── references/                   # Reference materials
│   │   ├── gemini-api-guide.md       # Nano Banana Pro API reference
│   │   └── paperbanana-insights.md   # Key findings from the PaperBanana paper
│   ├── temp/                         # Temporary working files and examples
│   ├── .gitignore
│   └── README.md
├── dc-due-diligence/                 # Plugin: Data center due diligence workflow
│   ├── .claude-plugin/
│   │   └── plugin.json               # Plugin metadata
│   ├── agents/                       # 12 specialized analysis agents + orchestrator
│   │   ├── power-agent.md            # Power infrastructure & grid analysis
│   │   ├── connectivity-agent.md     # Fiber carriers & network access
│   │   ├── water-cooling-agent.md    # Water supply & cooling system design
│   │   ├── land-zoning-agent.md      # Zoning, permits, entitlements
│   │   ├── ownership-agent.md        # Property ownership & litigation
│   │   ├── environmental-agent.md    # Natural hazards & contamination
│   │   ├── commercials-agent.md      # Deal terms, pricing, lease structure
│   │   ├── natural-gas-agent.md      # Pipeline access & on-site generation
│   │   ├── market-comparables-agent.md # Market analysis & comps
│   │   ├── risk-assessment-agent.md  # Cross-domain risk synthesis
│   │   ├── executive-summary-agent.md # Scoring & verdict generation
│   │   └── test-agent.md             # Test/validation agent
│   ├── skills/
│   │   └── due-diligence/
│   │       └── SKILL.md              # Orchestrator: validates folder, converts docs, spawns 12 agents
│   ├── converters/                   # Python document conversion pipeline
│   │   ├── __init__.py
│   │   ├── base.py                   # BaseConverter class
│   │   ├── pipeline.py               # Main pipeline orchestrator (scans folder, routes to converters)
│   │   ├── scanner.py                # Folder scanner & file type detection
│   │   ├── pdf.py                    # PDF converter (pdfplumber)
│   │   ├── excel.py                  # Excel converter (openpyxl, pyxlsb)
│   │   ├── word.py                   # Word document converter (python-docx)
│   │   ├── powerpoint.py             # PowerPoint converter (python-pptx)
│   │   └── vision.py                 # Image & scanned PDF converter (Anthropic vision API)
│   ├── templates/                    # Output templates for agents
│   │   ├── agent-output-template.md  # Standardized structure all agents follow
│   │   └── scoring-rubric.md         # Category scoring guide for executive summary
│   ├── tests/                        # pytest test suite
│   │   ├── __init__.py
│   │   ├── test_imports.py           # Verify dependencies installed
│   │   ├── test_folder_scanner.py    # Scanner unit tests
│   │   ├── test_pdf_converter.py     # PDF conversion tests
│   │   ├── test_excel_converter.py   # Excel conversion tests
│   │   ├── test_word_converter.py    # Word conversion tests
│   │   ├── test_powerpoint_converter.py # PowerPoint conversion tests
│   │   ├── test_vision_converter.py  # Vision API conversion tests
│   │   └── test_status_reporting.py  # Pipeline status report tests
│   ├── pyproject.toml                # Python package metadata & dependencies
│   ├── setup.sh                      # Auto-setup script: creates .venv, installs dependencies
│   └── .gitignore
├── CLAUDE.md                         # Noah's role, plugin architecture conventions, local development instructions
├── README.md                         # Marketplace overview, plugin summaries, quick start
├── LICENSE                           # MIT license
└── .gitignore
```

## Directory Purposes

**`.claude-plugin/`:**
- Purpose: Marketplace registry metadata for Claude Code plugin discovery and installation
- Contains: `marketplace.json` listing all available plugins with names, sources, descriptions
- Key files: `.claude-plugin/marketplace.json`

**`create-image/`:**
- Purpose: Self-contained Claude Code plugin for AI image generation using the PaperBanana multi-agent framework
- Contains: Agent definitions, skill orchestrator, Python script for Gemini API calls, reference materials
- Key files: `create-image/skills/create-image/SKILL.md` (orchestrator), `create-image/agents/` (4 agents), `create-image/scripts/generate-image.py` (API wrapper)

**`dc-due-diligence/`:**
- Purpose: Self-contained Claude Code plugin for automated data center due diligence analysis across 9 domains
- Contains: 12 agents (9 domain + 3 synthesis), Python document conversion pipeline, output templates, test suite, setup automation
- Key files: `dc-due-diligence/skills/due-diligence/SKILL.md` (orchestrator), `dc-due-diligence/agents/` (12 agents), `dc-due-diligence/converters/pipeline.py` (document processing), `dc-due-diligence/templates/` (output templates)

**`dc-due-diligence/converters/`:**
- Purpose: Python library for converting documents (PDF, Excel, Word, PowerPoint, images) to markdown for text-based analysis
- Contains: Format-specific converter classes, pipeline orchestrator, folder scanner, result dataclasses
- Key files: `pipeline.py` (main entry point), `scanner.py` (file detection), `base.py` (base class), format-specific converters

**`dc-due-diligence/agents/`:**
- Purpose: Specialized task executors, each handling one analysis domain or synthesis step
- Contains: 12 markdown files defining agent behavior, roles, workflows
- Key files: 9 domain agents (power, connectivity, water-cooling, land-zoning, ownership, environmental, commercials, natural-gas, market-comparables), 2 synthesis agents (risk-assessment, executive-summary), 1 test agent

**`dc-due-diligence/templates/`:**
- Purpose: Standardized output format definitions that agents read and follow
- Contains: Markdown templates defining section structure, risk scoring, category definitions
- Key files: `agent-output-template.md` (all domain agents use this), `scoring-rubric.md` (executive summary scoring rules)

**`dc-due-diligence/tests/`:**
- Purpose: pytest test suite validating converter functionality and integration
- Contains: Unit tests for each converter, scanner tests, status reporting tests
- Key files: One test file per converter module plus scanner and reporting tests

**`.github/workflows/`:**
- Purpose: GitHub Actions CI/CD automation
- Contains: Workflow YAML files for code review and deployment
- Key files: `claude.yml`, `claude-code-review.yml`

## Key File Locations

**Entry Points:**
- `create-image/skills/create-image/SKILL.md`: User invokes `/create-image [description]` → skill orchestrates 4-agent pipeline
- `dc-due-diligence/skills/due-diligence/SKILL.md`: User invokes `/due-diligence <folder-path>` → skill orchestrates document conversion + 12-agent analysis

**Configuration:**
- `.claude-plugin/marketplace.json`: Plugin registry with name, source paths, descriptions
- `create-image/.claude-plugin/plugin.json`: Plugin metadata for create-image (version, author, license)
- `dc-due-diligence/.claude-plugin/plugin.json`: Plugin metadata for dc-due-diligence (version, author)
- `dc-due-diligence/pyproject.toml`: Python package metadata, dependencies (pdfplumber, openpyxl, python-docx, python-pptx, anthropic, Pillow)

**Core Logic:**
- `create-image/agents/research-agent.md`: Analyzes reference images → produces style brief
- `create-image/agents/prompt-architect.md`: Crafts 5 narrative prompts
- `create-image/agents/generator-agent.md`: Calls Gemini API → saves images
- `create-image/agents/critic-agent.md`: Evaluates images on 4 dimensions
- `dc-due-diligence/converters/pipeline.py`: Main document processing orchestrator (scans folder, routes files to converters, produces manifest)
- `dc-due-diligence/converters/pdf.py`: PDF to markdown conversion (pdfplumber)
- `dc-due-diligence/converters/excel.py`: Excel to markdown conversion (openpyxl, pyxlsb)
- `dc-due-diligence/converters/word.py`: Word to markdown conversion (python-docx)
- `dc-due-diligence/converters/powerpoint.py`: PowerPoint to markdown conversion (python-pptx)
- `dc-due-diligence/converters/vision.py`: Image and scanned PDF to markdown (Anthropic vision API)
- `dc-due-diligence/agents/power-agent.md`: Power infrastructure analysis (9 domain agents follow same pattern)
- `dc-due-diligence/agents/risk-assessment-agent.md`: Cross-domain risk synthesis
- `dc-due-diligence/agents/executive-summary-agent.md`: Scoring and verdict generation

**Testing:**
- `dc-due-diligence/tests/test_imports.py`: Verify dependencies are installed
- `dc-due-diligence/tests/test_pdf_converter.py`: PDF conversion validation
- `dc-due-diligence/tests/test_excel_converter.py`: Excel conversion validation
- `dc-due-diligence/tests/test_word_converter.py`: Word conversion validation
- `dc-due-diligence/tests/test_powerpoint_converter.py`: PowerPoint conversion validation
- `dc-due-diligence/tests/test_vision_converter.py`: Vision API conversion validation

## Naming Conventions

**Files:**
- Agent files: kebab-case with `-agent.md` suffix -- See `create-image/agents/research-agent.md`, `dc-due-diligence/agents/power-agent.md`
- Converter modules: lowercase with `.py` extension -- See `dc-due-diligence/converters/pdf.py`, `excel.py`, `vision.py`
- Skill directories: skill name in kebab-case -- See `create-image/skills/create-image/`, `dc-due-diligence/skills/due-diligence/`
- Test files: `test_<module>.py` format -- See `dc-due-diligence/tests/test_pdf_converter.py`
- Template files: descriptive kebab-case -- See `agent-output-template.md`, `scoring-rubric.md`

**Directories:**
- Plugins at repo root: lowercase kebab-case -- See `create-image/`, `dc-due-diligence/`
- Agent subdirectory: `agents/` (plural)
- Skill subdirectory: `skills/` with skill name as subdirectory -- `skills/<skill-name>/`
- Support directories: `converters/`, `scripts/`, `templates/`, `tests/`, `references/`

## Where to Add New Code

Use the following locations when adding new code to this project.

**New Plugin:**
- Create root-level directory with plugin name in kebab-case
- Add `.claude-plugin/plugin.json` with name, description, version, author, homepage, repository, license, keywords
- Add `skills/<skill-name>/SKILL.md` as the orchestrator entry point
- Add `agents/<agent-name>.md` files for task-executing agents
- Add supporting code in `scripts/`, `templates/`, `references/` as needed
- Register in `.claude-plugin/marketplace.json` by adding entry to `plugins` array with `name`, `source` (relative path), `description`
- Add plugin reference section to `CLAUDE.md` (## Plugin Reference: <name>)
- Add plugin row to plugin summary table in `README.md` and a detailed `### plugin-name` section

**New Agent in Existing Plugin:**
- Place implementation in `<plugin>/agents/<agent-name>.md`
- Include YAML frontmatter: `name:`, `description:` (with example triggers and commentary), optionally `color:` for visual distinction, optionally `tools:` list, optionally `model: inherit`
- Write prescriptive Markdown body with role statement, task definition, workflow phases, output format specification, file paths using `${CLAUDE_PLUGIN_ROOT}` or `${OPPORTUNITY_FOLDER}` tokens
- Follow the pattern in existing agents: See `dc-due-diligence/agents/power-agent.md` (domain agent) or `dc-due-diligence/agents/risk-assessment-agent.md` (synthesis agent)
- Update the orchestrator skill (`skills/<skill-name>/SKILL.md`) to spawn the new agent with appropriate context

**New Skill (Orchestrator) in Existing Plugin:**
- Place implementation in `<plugin>/skills/<skill-name>/SKILL.md`
- Include YAML frontmatter: `name:`, `description:` (include trigger phrases for Claude Code to recognize), optionally `version:`
- Structure as numbered phases: Input Validation → Setup → Execution → Results
- In execution phase, spawn agents via Task tool with explicit context (prior outputs, file paths, templates)
- Use `${ARGUMENTS}` for user input, `${CLAUDE_PLUGIN_ROOT}` for plugin-relative paths
- Follow the pattern in existing skills: See `create-image/skills/create-image/SKILL.md` (sequential pipeline) or `dc-due-diligence/skills/due-diligence/SKILL.md` (parallel waves)

**New Document Converter (in dc-due-diligence):**
- Create new Python module in `dc-due-diligence/converters/<format>.py`
- Inherit from `BaseConverter` defined in `converters/base.py`
- Implement `convert(file_path: Path) -> ExtractionResult` method
- Return `ExtractionResult` with extracted text and confidence level (HIGH, MEDIUM, LOW, FAILED)
- Handle format-specific exceptions gracefully with detailed logging
- Add your converter class to the `CONVERTERS` dict in `converters/pipeline.py`
- Write tests in `dc-due-diligence/tests/test_<format>_converter.py`
- Follow patterns in existing converters: See `converters/pdf.py` (pdfplumber), `converters/excel.py` (openpyxl), `converters/vision.py` (Anthropic API)

**New Test:**
- Place test in `dc-due-diligence/tests/test_<module>.py`
- Use pytest conventions: test functions named `test_<scenario>`, use assertions and fixtures
- Follow patterns in existing tests: See `tests/test_pdf_converter.py`, `tests/test_imports.py`
- Run tests locally: `cd dc-due-diligence && python -m pytest tests/`

**New Template (Output Format):**
- Create markdown file in `<plugin>/templates/<name>.md`
- Define section structure agents should follow (use headers, subsections, placeholders)
- Reference by absolute path in agent instructions (e.g., `${CLAUDE_PLUGIN_ROOT}/templates/agent-output-template.md`)
- Example: See `dc-due-diligence/templates/agent-output-template.md` (all domain agents use this), `scoring-rubric.md` (executive summary uses this)

**New Reference/Guide:**
- Create markdown file in `<plugin>/references/<name>.md`
- Document domain knowledge, API details, paper insights, or best practices agents should know
- Reference by path in agent instructions
- Example: See `create-image/references/gemini-api-guide.md`, `paperbanana-insights.md`

**Utilities/Scripts:**
- Place in `<plugin>/scripts/<name>.py`
- Should be callable via Bash subprocess (shebang: `#!/usr/bin/env python3`)
- Document usage in header comments
- Example: See `create-image/scripts/generate-image.py`

## Special Directories

**`dc-due-diligence/.venv/`:**
- Purpose: Python virtual environment (created by `setup.sh`)
- Generated: Yes (created at first plugin run)
- Committed: No (added to `.gitignore`)

**`create-image/temp/` and `dc-due-diligence/temp/`:**
- Purpose: Temporary working files, examples, drafts
- Generated: Yes (user/development generated)
- Committed: Selectively (may contain useful examples)

**`.director/`:**
- Purpose: Director onboarding metadata and analysis documents
- Generated: Yes (auto-generated by Director onboarding)
- Committed: Yes (should be checked in to preserve analysis history)

**`<opportunity-folder>/_converted/` (dc-due-diligence output)**
- Purpose: Staging directory for converted documents
- Generated: Yes (created by conversion pipeline)
- Committed: No (not applicable -- created at runtime in user's opportunity folder)

**`<opportunity-folder>/research/` (dc-due-diligence output)**
- Purpose: Output directory for all domain research reports and risk assessment
- Generated: Yes (created by agents during execution)
- Committed: No (user-generated analysis output)

**`<current-project>/shipfast-images/` (create-image output)**
- Purpose: Output directory for generated images
- Generated: Yes (created by generator agent)
- Committed: No (generated images, typically too large)

## Quality Gate

Before considering this file complete, verify:
- [x] Every finding includes at least one file path in backticks
- [x] Voice is prescriptive ("Use X", "Place files in Y") not descriptive ("X is used")
- [x] No section left empty -- all sections have concrete findings
- [x] Directory tree present and annotated with purposes
- [x] "Where to Add New Code" has 8+ entries (new plugin, new agent, new skill, new converter, new test, new template, new reference, utilities)
- [x] All paths use backtick formatting
- [x] Naming conventions documented with examples
