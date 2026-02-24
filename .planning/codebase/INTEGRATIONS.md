# External Integrations

**Analysis Date:** 2026-02-23

## APIs & External Services

**AI/LLM Services:**
- Anthropic Claude API - Vision extraction for scanned PDFs and image documents
  - SDK/Client: anthropic 0.83.0
  - Auth: ANTHROPIC_API_KEY (environment variable)
  - Used by: `dc-due-diligence/converters/vision.py` — calls `claude-sonnet-4-20250514` model for text extraction from images
  - Model: claude-sonnet-4-20250514 (vision-capable model)
  - Max tokens: 4096 per page extraction request

- Google Gemini API (Nano Banana Pro / Gemini 3 Pro) - Image generation
  - SDK/Client: google-genai Python SDK
  - Auth: GEMINI_API_KEY (environment variable)
  - Used by: `create-image/scripts/generate-image.py` — calls `gemini-3-pro-image-preview` model
  - Features: Reference image support (up to 14 images), multiple aspect ratios and resolutions

**Web Research (Optional):**
- Claude Code built-in WebSearch/WebFetch - Used by all 12 domain agents for research
  - SDK: No explicit SDK (built into Claude Code runtime)
  - Used by: Agents in `dc-due-diligence/agents/` (e.g., water-cooling-agent.md, power-agent.md)
  - Auto-detection: Tavily, Exa, or Firecrawl MCP servers used automatically if configured in Claude Code
  - No configuration needed in plugin

## Data Storage

**Databases:**
- None (stateless architecture)

**File Storage:**
- Local filesystem only
- Input: Opportunity folder structure with broker documents (PDFs, Excel, Word, PowerPoint, images)
- Output:
  - `_converted/` subdirectory with extracted markdown text and manifest.json
  - `research/` subdirectory with domain-specific research reports (markdown)
  - `shipfast-images/` directory for generated images (create-image plugin)

**Caching:**
- Manifest-based caching: `<opportunity-folder>/_converted/manifest.json` prevents re-processing of already-converted documents
- Conversion skipped if manifest exists with at least one successful conversion

## Authentication & Identity

**Auth Provider:**
- Custom API key model (no centralized auth provider)
- Two independent API keys managed separately:
  - ANTHROPIC_API_KEY - For Anthropic Claude API
  - GEMINI_API_KEY - For Google Gemini API

**Auth Mechanism:**
- Environment variables read at runtime
- `.env` file support via python-dotenv (optional, for local development)
- No OAuth, no token refresh logic

## Monitoring & Observability

**Error Tracking:**
- None (no external error tracking service)

**Logs:**
- Python logging module used by converters (`logging.getLogger()`)
- Status reports printed to stdout by pipeline (`converters/pipeline.py`)
- Test logs available via pytest output

**Verbose Output:**
- Conversion pipeline prints detailed status including:
  - File counts by type
  - Successful/failed conversion counts
  - Low-confidence extractions
  - Specific error messages for failed files

## CI/CD & Deployment

**Hosting:**
- GitHub repository (source only) - `https://github.com/noahrasheta/shipfast`
- No cloud deployment (plugins run locally in Claude Code)

**CI Pipeline:**
- None detected

**Distribution:**
- Claude Code plugin marketplace - Installed via `/plugin marketplace add` and `/plugin install`
- Local development via `claude --plugin-dir ./dc-due-diligence`

## Environment Configuration

**Required env vars:**
- ANTHROPIC_API_KEY - Must be set for vision extraction (scanned PDFs)
  - If not set when vision extraction is needed, agents will skip image processing
  - Set in shell environment or read from `.env` file (dc-due-diligence plugin)
- GEMINI_API_KEY - Must be set for create-image plugin
  - Set in `.env` file in project root (create-image plugin requirement)

**Secrets location:**
- Shell environment or `.env` file (local development)
- No secrets stored in repository

**Startup validation:**
- Python dependencies verified on first plugin invocation
- ANTHROPIC_API_KEY checked when vision conversion needed (if folder contains images/scanned PDFs)
- GEMINI_API_KEY checked during create-image phase setup
- Python virtual environment created automatically if missing

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None (agents use synchronous API calls only)

## Document Processing Pipeline

**Supported Input Formats:**
- PDF (.pdf) - Via pdfplumber (native text) or Claude vision (scanned images)
- Excel (.xlsx, .xlsb) - Via openpyxl and pyxlsb
- Word (.docx) - Via python-docx
- PowerPoint (.pptx) - Via python-pptx
- Images (.png, .jpg, .tiff) - Via Claude vision and Pillow

**Processing Chain:**
1. Scanner identifies file types and creates processing plan (`converters/scanner.py`)
2. Appropriate converter processes each file:
   - PDFConverter: Native text or route to VisionConverter if scanned
   - ExcelConverter: Parses sheets into markdown tables
   - WordConverter: Extracts text and structure
   - PowerPointConverter: Extracts slide text and layouts
   - VisionConverter: Claude API calls for images and scanned PDFs
3. Standardized ExtractionResult returned with confidence level
4. Manifest.json written with all conversion metadata

**Output Format:**
- Markdown text files in `_converted/` directory
- Manifest JSON with conversion metadata (method, confidence, success status)

## Agent Web Research Integration

**Claude Code Built-in Tools:**
- WebSearch - Returns search results with titles, URLs, snippets
- WebFetch - Fetches and extracts content from specific URLs

**Optional MCP Servers:**
- Tavily - Advanced web search (auto-used if configured)
- Exa - Semantic web search (auto-used if configured)
- Firecrawl - JavaScript-heavy website scraping (auto-used if configured)

**No Configuration Required:**
- Agents use Claude Code's built-in web research capabilities
- MCP servers detected and used automatically if available in Claude Code config
- No API keys needed in plugin for web research

---

*Integration audit: 2026-02-23*
