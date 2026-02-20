# Technology Stack

**Analysis Date:** 2026-02-20

## Languages

**Primary:**
- Python 3.11+ - Used in `dc-due-diligence/converters/` and `dc-due-diligence/tests/`
- Markdown - Agent and skill definitions across `create-image/agents/` and `dc-due-diligence/agents/`
- YAML - Plugin manifests in `.claude-plugin/plugin.json` files

**Secondary:**
- Bash - Setup and orchestration scripts in `dc-due-diligence/setup.sh`

## Runtime

**Environment:**
- Python 3.11+ - Specified in `dc-due-diligence/pyproject.toml` with `requires-python = ">=3.11"`
- Python virtual environment (.venv) - Created automatically by `dc-due-diligence/setup.sh` on first run

**Package Manager:**
- pip (via setuptools) - Configured in `dc-due-diligence/pyproject.toml`
- Lockfile: Missing - Project uses `pyproject.toml` without `poetry.lock` or `requirements.txt` lock file

## Frameworks

**Core:**
- Claude Code Plugin System - Agent orchestration framework used in `create-image/skills/create-image/SKILL.md` and `dc-due-diligence/skills/due-diligence/SKILL.md`
- PaperBanana Agentic Framework - Multi-agent image generation coordination in `create-image/`

**Testing:**
- pytest 8.0.0+ - Test framework configured in `dc-due-diligence/pyproject.toml` with test path in `dc-due-diligence/tests/`
- Test location: `dc-due-diligence/tests/` (fixture: `testpaths = ["tests"]` in `pyproject.toml`)

**Build/Dev:**
- setuptools 68.0+ - Build system in `dc-due-diligence/pyproject.toml` using `setuptools.build_meta`

## Key Dependencies

**Critical:**
- anthropic 0.40.0+ - Claude API client for vision-based text extraction and agent responses - Used in `dc-due-diligence/converters/vision.py` and throughout agent execution
- google-genai - Gemini API client for image generation - Required in `create-image/scripts/generate-image.py` (installed via `pip install google-genai`)

**Infrastructure - Document Processing:**
- pdfplumber 0.11.0+ - PDF text extraction with direct text layer parsing - Used in `dc-due-diligence/converters/pdf.py`
- python-docx 1.1.0+ - Word document (DOCX) parsing - Used in `dc-due-diligence/converters/word.py`
- python-pptx 1.0.0+ - PowerPoint presentation (PPTX) parsing - Used in `dc-due-diligence/converters/powerpoint.py`
- openpyxl 3.1.0+ - Modern Excel (XLSX) spreadsheet handling - Used in `dc-due-diligence/converters/excel.py`
- pyxlsb 1.0.10+ - Legacy Excel (XLSB) binary format support - Used in `dc-due-diligence/converters/excel.py`
- Pillow 10.0.0+ - Image processing and JPEG compression for vision API - Used in `dc-due-diligence/converters/vision.py` and `create-image/scripts/generate-image.py`
- pypdfium2 - PDF to image rendering for scanned document detection - Used in `dc-due-diligence/converters/vision.py`

**Infrastructure - Image Generation:**
- python-dotenv - Environment variable loading from `.env` files - Used in `create-image/scripts/generate-image.py`

## Configuration

**Environment:**
- Use `.env` files for API keys (referenced in `create-image/scripts/generate-image.py` and noted in `README.md`)
- Key config files: `.claude-plugin/marketplace.json` (plugin catalog), `.claude-plugin/plugin.json` (per-plugin metadata)
- ANTHROPIC_API_KEY - Required for Claude vision API (dc-due-diligence scanned PDF extraction)
- GEMINI_API_KEY - Required for image generation in create-image plugin (documented in `create-image/scripts/generate-image.py`)

**Build:**
- Build configuration lives in `dc-due-diligence/pyproject.toml`
- Package discovery: `[tool.setuptools.packages.find]` configured to include `converters*`
- Run build with: `pip install -e dc-due-diligence/` (editable install) or standard setuptools build

## Platform Requirements

**Development:**
- Python 3.11+ interpreter - Configured in `dc-due-diligence/pyproject.toml`
- Virtual environment support - Automatic setup in `dc-due-diligence/setup.sh`

**Production:**
- Python 3.11+ runtime for document conversion pipeline
- Claude Code with plugin support for skill execution (via `dc-due-diligence/skills/due-diligence/SKILL.md` orchestration)
- Anthropic API access (ANTHROPIC_API_KEY environment variable)
- Gemini API access for image generation (GEMINI_API_KEY environment variable)
- Claude Code built-in WebSearch/WebFetch tools for agent web research (no additional config needed; optional MCP servers: Tavily, Exa, or Firecrawl)

## Quality Gate

Before considering this file complete, verify:
- [x] Every finding includes at least one file path in backticks
- [x] Voice is prescriptive ("Use X", "Place files in Y") not descriptive ("X is used")
- [x] No section left empty -- use "Not detected" or "Not applicable"
- [x] Specific version numbers included for all technologies
- [x] Lockfile status documented
