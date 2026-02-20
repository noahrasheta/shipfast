# Codebase Summary

**Project:** shipfast
**Analysis Date:** 2026-02-20

## What This Project Is

Shipfast is a personal Claude Code plugin marketplace run by Noah Rasheta. It hosts two plugins you can install directly into Claude Code: one that generates AI images using a research-backed multi-agent approach, and one that automates data center investment due diligence by analyzing broker documents across 12 specialized domains. Both plugins are distributed through a marketplace catalog and installable with a single command.

The project is built around Claude Code's plugin and agent system. Each plugin contains a skill (which acts as a coordinator) and a set of agents (which do the actual work). The image plugin calls Google's Gemini API to generate images; the due diligence plugin converts uploaded documents into text and then dispatches domain-expert agents to research and score the opportunity.

## Built With

The project is primarily Markdown and Python. Agent definitions and skill orchestrators are written in Markdown with YAML frontmatter -- this is the Claude Code plugin format. Python 3.11+ powers the document conversion pipeline in the due diligence plugin, using libraries like pdfplumber, openpyxl, python-docx, and python-pptx to extract text from PDFs, spreadsheets, and presentations. The image plugin uses Google's `google-genai` Python SDK to call Gemini 3 Pro. Tests run with pytest. There is no web server, no database, and no frontend -- everything runs as Claude Code agent workflows.

## What It Can Do

- Users can run `/create-image [description]` to generate 5 AI image variants, ranked by quality across faithfulness, readability, conciseness, and aesthetics
- Users can run `/due-diligence <folder-path>` to analyze a data center investment opportunity, receiving a scored executive summary with a Pursue / Proceed with Caution / Pass verdict
- Users can install plugins from the marketplace with `/plugin install create-image@shipfast` or `/plugin install dc-due-diligence@shipfast`
- Users can test plugins locally without marketplace installation using `claude --plugin-dir ./<plugin-name>`

## How It's Organized

The repo has two top-level plugin directories (`create-image/` and `dc-due-diligence/`), a marketplace registry at `.claude-plugin/marketplace.json`, and project documentation at the root. Each plugin is fully self-contained: it has its own manifest, agents, skill orchestrator, and any supporting Python code or templates it needs. The due diligence plugin has the most depth -- it includes 12 agents, a full Python document conversion library, a test suite, and output templates that keep all agent reports consistent.

---

## Key Findings

### Technology

Python 3.11+ is required for the document conversion pipeline, managed via an auto-created virtualenv (`dc-due-diligence/setup.sh`). The Claude Code plugin system is the core framework for both plugins. Key API dependencies are `anthropic>=0.40.0` (vision extraction) and `google-genai` (image generation). Notably, there is no lockfile -- `pyproject.toml` uses loose lower bounds without a `poetry.lock` or `requirements.txt` pin, which is a dependency stability risk.

- Python 3.11+, pip/setuptools - See `dc-due-diligence/pyproject.toml`
- pytest 8.0.0+ for testing - See `dc-due-diligence/pyproject.toml`
- anthropic 0.40.0+, google-genai - See `dc-due-diligence/converters/vision.py`, `create-image/scripts/generate-image.py`
- No lockfile present - See CONCERNS.md (dependency risk)

### Integrations

Two external APIs are required depending on which plugin you use. `ANTHROPIC_API_KEY` is only needed for dc-due-diligence when processing scanned PDFs or images. `GEMINI_API_KEY` is required for the create-image plugin. Web research within due diligence agents uses Claude Code's built-in WebSearch/WebFetch tools (no key needed), with optional enhancement via Tavily, Exa, or Firecrawl MCP servers.

- Gemini 3 Pro Image API: image generation - See `create-image/scripts/generate-image.py`
- Anthropic Claude Vision API (`claude-sonnet-4-20250514`): scanned document OCR - See `dc-due-diligence/converters/vision.py`
- Claude Code WebSearch/WebFetch: agent web research (built-in, no config) - See `dc-due-diligence/agents/`
- OpenCorporates, PeeringDB: optional web lookups via WebFetch (no API key) - See `dc-due-diligence/agents/ownership-agent.md`, `connectivity-agent.md`
- Local filesystem only for output storage -- no database - See `INTEGRATIONS.md`

### Architecture

The project uses an orchestrator-agent pattern inside a plugin-based monorepo. Each plugin's skill coordinates a multi-step pipeline by spawning agents via Claude Code's Task tool. Agents are stateless -- they receive all context in their prompt and write outputs to files. The due diligence pipeline uses a three-wave execution model (9 parallel domain agents, then risk synthesis, then executive summary). The image pipeline is sequential (Research → Prompt Architect → Generator → Critic). State is passed between agents through the filesystem and via the orchestrator capturing and forwarding prior agent output.

- Pattern: Plugin marketplace monorepo with orchestrator-agent pipelines - See `create-image/skills/create-image/SKILL.md`, `dc-due-diligence/skills/due-diligence/SKILL.md`
- Agents are stateless; orchestrators manage phase transitions - See `ARCHITECTURE.md`
- Document conversion is a separate Python layer invoked via Bash subprocess - See `dc-due-diligence/converters/pipeline.py`

### Conventions

Python code follows PEP 8 with no enforced linter or formatter. All converter modules follow a consistent pattern: inherit from `BaseConverter`, implement `convert(path: Path) -> ExtractionResult`, never raise exceptions (return `ExtractionResult(success=False)` on failure). Agent files use kebab-case with `-agent.md` suffix. Skills live at `skills/<skill-name>/SKILL.md`. Always use `${CLAUDE_PLUGIN_ROOT}` for plugin-relative paths -- never hardcode absolute paths. Use `from __future__ import annotations` and full type hints in all Python files.

- Converter pattern: extend `BaseConverter` - See `dc-due-diligence/converters/base.py`
- Return `ExtractionResult` with `success=False` on error, never raise - See `dc-due-diligence/converters/pdf.py` lines 83-94
- Plugin paths: use `${CLAUDE_PLUGIN_ROOT}` token, never absolute paths - See `CLAUDE.md`
- Type hints required; use `Path` for file paths, not strings - See `dc-due-diligence/converters/base.py`

### Testing

Tests cover only the dc-due-diligence Python converter library. There are no tests for the create-image plugin, and no tests for any agent or skill Markdown files. The test suite uses pytest with real-file integration tests and synthetic fixture-based unit tests. Integration tests gracefully skip when example documents are absent (`pytest.skip()`), making CI safe without real data. Coverage is not enforced.

- Test location: `dc-due-diligence/tests/` - Run with `cd dc-due-diligence && python -m pytest tests/`
- Converters are well-tested; skills, agents, and create-image plugin have no tests - See `TESTING.md`
- Use `tmp_path` fixture for temporary files; `pytest.skip()` when real data is absent - See `dc-due-diligence/tests/test_pdf_converter.py`

### Concerns

The highest-priority concern is an unclosed image file handle in `vision.py` that can cause memory leaks during large batch processing. The `anthropic` SDK dependency is loosely pinned (`>=0.40.0`), meaning a future major version could silently break vision extraction. The hardcoded vision model name (`claude-sonnet-4-20250514`) will break if that model is deprecated. The converter factory in `pipeline.py` and the scanner's type map in `scanner.py` must be kept in sync manually -- they can silently diverge when adding new converters.

- HIGH: Image file not closed in `vision.py` line 277 - See `CONCERNS.md`
- MEDIUM: Loose `anthropic` SDK pin in `pyproject.toml` - See `CONCERNS.md`
- MEDIUM: Hardcoded vision model string in `vision.py` lines 24-45 - See `CONCERNS.md`
- MEDIUM: `_get_converter()` dict and `_TYPE_TO_CONVERTER` dict must stay in sync - See `dc-due-diligence/converters/pipeline.py`, `dc-due-diligence/converters/scanner.py`

---

## Things Worth Noting

- There is no lockfile. If you install the package fresh, you may get a different version of `anthropic` or `openpyxl` than what was tested. Consider adding `poetry.lock` or pinning versions in `pyproject.toml` to avoid unexpected breakage.
- The create-image plugin has no tests at all. Any change to `generate-image.py` or the agent Markdown files is untested.
- The vision converter calls the Anthropic API once per PDF page, sequentially. A 100-page scanned PDF will make 100 API calls in a row, which is slow and may hit rate limits.
- Three files must be updated every time a new plugin is added: `.claude-plugin/marketplace.json`, `CLAUDE.md` (Plugin Reference section), and `README.md` (summary table and detailed section). Missing any of these leaves the marketplace catalog out of sync.
- Manifest files written by the conversion pipeline (`_converted/manifest.json`) contain full absolute paths. These should not be committed to version control.
- No progress indicator exists during long document conversion runs. If a folder has many large PDFs, the process can appear hung.

---

## For Builder Agents

Use the following guidance when working in this codebase.

**File structure:**
- Place new plugins at repo root as `<plugin-name>/` with kebab-case name
- Place new agents in `<plugin>/agents/<agent-name>.md` (kebab-case, `-agent.md` suffix)
- Place new skill orchestrators in `<plugin>/skills/<skill-name>/SKILL.md`
- Place new Python converters in `dc-due-diligence/converters/<format>.py`
- Place new tests in `dc-due-diligence/tests/test_<module>.py`
- Place new output templates in `<plugin>/templates/<name>.md`
- Place new reference guides in `<plugin>/references/<name>.md`
- Place new utility scripts in `<plugin>/scripts/<name>.py`

**Naming conventions:**
- Use `kebab-case` for agent files: `research-agent.md`, `power-agent.md`
- Use `snake_case` for Python modules: `pdf.py`, `test_pdf_converter.py`
- Use `PascalCase` for Python class names: `PDFConverter`, `ExtractionResult`
- Use `UPPER_SNAKE_CASE` for Python module constants: `_SCANNED_CHARS_PER_PAGE_THRESHOLD`
- Use `snake_case` for Python functions and variables

**Key patterns to follow:**
- New converters: inherit `BaseConverter`, implement `convert(path: Path) -> ExtractionResult`, return error results instead of raising - See `dc-due-diligence/converters/base.py`
- When adding a converter, update both `_get_converter()` in `pipeline.py` AND `_TYPE_TO_CONVERTER` in `scanner.py` -- they must stay in sync
- New agents: include YAML frontmatter with `name` and `description`; use `${CLAUDE_PLUGIN_ROOT}` for all file path references, never hardcode absolute paths - See `dc-due-diligence/agents/power-agent.md`
- New skills: use YAML frontmatter with `name`, `description`, `version`; structure as numbered phases (Validation → Setup → Execution → Results) - See `dc-due-diligence/skills/due-diligence/SKILL.md`
- New plugins: register in `.claude-plugin/marketplace.json`, add Plugin Reference section to `CLAUDE.md`, add row to summary table and detailed section in `README.md`
- Use `tmp_path` pytest fixture for test file creation; skip with `pytest.skip()` when real data is unavailable - See `dc-due-diligence/tests/test_excel_converter.py`
- Use `from __future__ import annotations` at the top of every Python module
- Use type hints on all function signatures

**Things to avoid:**
- Do not hardcode absolute paths in agent Markdown files -- use `${CLAUDE_PLUGIN_ROOT}` - See `CLAUDE.md` and `CONVENTIONS.md`
- Do not raise exceptions in converter `convert()` methods -- return `ExtractionResult(success=False)` instead - See `CONCERNS.md`
- Do not leave image file handles open after use -- use context managers (`with Image.open(path) as img:`) - See `CONCERNS.md` (vision.py line 277)
- Do not add a new converter without also writing tests in `dc-due-diligence/tests/` - See `TESTING.md`
- Do not commit `.env` files, `_converted/` output directories, or generated images - See `.gitignore`

---

## Cross-Reference Findings

The following connections across mapper outputs are worth highlighting:

- **STACK + CONCERNS:** The `anthropic>=0.40.0` loose pin in `pyproject.toml` directly affects the vision model hardcoded in `vision.py` as `claude-sonnet-4-20250514`. A major SDK update could break both the auth layer and the model call simultaneously. These two risks compound each other.
- **ARCHITECTURE + CONCERNS:** The orchestrator-agent pattern relies on agents writing output files to `<folder>/research/`. If the vision pipeline produces corrupted text (partial failures noted in CONCERNS.md), agents receive that text without warning. There is no validation gate between the conversion layer and the agent analysis layer.
- **CONVENTIONS + CONCERNS:** CONVENTIONS.md documents the correct error-handling pattern (return `ExtractionResult(success=False)`), but CONCERNS.md flags that `vision.py` violates a related pattern by leaving the image file handle open. The conventions are sound; the violation is isolated to one file.
- **TESTING + STRUCTURE:** Tests exist only for the `dc-due-diligence/converters/` layer. The `create-image/` plugin and all agent/skill Markdown files have no test coverage. Any builder adding features to `create-image/` should be aware there is no safety net.
- **INTEGRATIONS + CONCERNS:** The manifest file (`_converted/manifest.json`) written by `pipeline.py` stores absolute paths. INTEGRATIONS.md notes it is local-only, but CONCERNS.md flags the security implication if shared. Builders should document this in setup instructions for any workflow that distributes opportunity folders.
- **ARCHITECTURE + CONVENTIONS:** The converter factory pattern described in ARCHITECTURE.md (Converter abstraction) requires that `pipeline.py` and `scanner.py` stay synchronized. CONCERNS.md identifies this as a fragile coupling. No automated test verifies the sync -- a builder adding a converter must update both files manually.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| STACK.md | HIGH | All key libraries, versions, and config files identified with specific line references |
| INTEGRATIONS.md | HIGH | API keys, SDKs, and service usage all traced to specific files; no external services missed |
| ARCHITECTURE.md | HIGH | Both pipelines fully documented with step-by-step data flow and file references |
| STRUCTURE.md | HIGH | Complete directory tree with annotated purposes; Where-to-Add-New-Code section is comprehensive |
| CONVENTIONS.md | HIGH | Python conventions derived from actual code with inline examples; plugin conventions from CLAUDE.md |
| TESTING.md | HIGH | Test suite is small and well-scoped; coverage gaps clearly identified |
| CONCERNS.md | HIGH | Specific line numbers, reproducible triggers, and fix approaches for every concern |

**Gaps:** No analysis was possible for GitHub Actions workflows (`.github/workflows/`) beyond confirming files exist. The `create-image/temp/` directory contents were not examined. No linter or formatter configuration exists to analyze.

Ready for builder agents.
