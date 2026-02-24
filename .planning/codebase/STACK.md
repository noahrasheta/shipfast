# Technology Stack

**Analysis Date:** 2026-02-23

## Languages

**Primary:**
- Python 3.11+ - Data processing, document conversion pipeline, and utility scripts
- Markdown - Agent definitions, skill orchestration files, and configuration

**Secondary:**
- Bash - Setup scripts, environment configuration, file path resolution

## Runtime

**Environment:**
- Python 3.11 or higher (required, enforced in `dc-due-diligence/pyproject.toml`)
- Virtual environment (`.venv/`) created automatically by `setup.sh` during plugin installation

**Package Manager:**
- pip (Python Package Installer)
- Lockfile: `requirements.txt` contains pinned versions for reproducibility

## Frameworks

**Core:**
- No traditional frameworks (agents/skills use Claude Code's agentic infrastructure)

**Document Processing:**
- pdfplumber 0.11.9 - PDF text extraction and parsing
- python-docx 1.2.0 - Word document (.docx) processing
- python-pptx 1.0.2 - PowerPoint (.pptx) processing
- openpyxl 3.1.5 - Excel spreadsheet processing
- pyxlsb 1.0.10 - Legacy Excel binary format (.xlsb) support
- PyMuPDF 1.27.1 - Advanced PDF manipulation
- pypdfium2 5.5.1 - PDF to image conversion (for vision extraction)

**Image Processing:**
- Pillow 12.1.1 - Image resizing, format conversion, JPEG compression
- google-genai (Python SDK) - Google Gemini 3 Pro image generation API

**API Clients:**
- anthropic 0.83.0 - Claude API for vision extraction and text analysis
- google-genai - Google Gemini API for image generation

**Utilities:**
- pydantic 2.12.5 - Data validation and serialization
- markdown-pdf 1.13.1 - Markdown to PDF conversion
- lxml 6.0.2 - XML parsing (used by document converters)

**Testing:**
- pytest 9.0.2 - Test runner and framework
- Configuration: `pyproject.toml` specifies testpaths as `tests/`

**Build System:**
- setuptools 68.0+ - Package building and installation

## Key Dependencies

**Critical:**
- anthropic 0.83.0 - Enables Claude vision API calls for scanned document extraction. Without this, image-based PDFs cannot be processed.
- pdfplumber 0.11.9 - Primary PDF text extraction engine. Handles structured PDFs with native text layers.
- python-docx 1.2.0 - Essential for .docx document processing in data center due diligence workflows.

**Infrastructure:**
- pydantic 2.12.5 - Provides strong typing and validation for converter outputs (ExtractionResult dataclass).
- google-genai - Connects to Google Gemini 3 Pro for image generation in create-image plugin.

## Configuration

**Environment:**
- ANTHROPIC_API_KEY - Required by dc-due-diligence plugin for vision extraction (scanned PDFs/images). Set in shell environment or `.env` file.
- GEMINI_API_KEY - Required by create-image plugin for Nano Banana Pro (Gemini 3 Pro) image generation. Set in `.env` file in project root.

**Build:**
- `pyproject.toml` - Specifies project metadata, dependencies, and pytest configuration
- `requirements.txt` - Pinned dependency versions for reproducible installs
- `setup.sh` - Automated environment setup that creates `.venv/` and installs dependencies

## Platform Requirements

**Development:**
- Python 3.11 or higher
- bash shell
- ~500MB disk space for virtual environment and dependencies
- macOS/Linux/Windows (via WSL)

**Production:**
- Claude Code (CLI) - Required to run plugins and skills
- Anthropic API account with Claude API access
- Google AI account with Gemini API access (for create-image plugin)
- Network connectivity to Anthropic and Google APIs

## Python Virtual Environment

- Location: `dc-due-diligence/.venv/`
- Creation: Automatic on first run via `setup.sh`
- Activation: Not required for plugin execution (orchestrator calls `.venv/bin/python3` directly)
- Isolation: Prevents dependency conflicts with system Python

---

*Stack analysis: 2026-02-23*
