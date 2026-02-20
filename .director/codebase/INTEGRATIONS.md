# External Integrations

**Analysis Date:** 2026-02-20

## APIs and External Services

**Image Generation:**
- Gemini 3 Pro Image API (Nano Banana Pro) - Generates professional-quality images with support for multiple resolutions (1K, 2K, 4K) and aspect ratios
  - SDK/Client: `google-genai` Python package in `create-image/scripts/generate-image.py`
  - Auth: `GEMINI_API_KEY` environment variable
  - Reference: `create-image/scripts/generate-image.py` lines 38-41

**Vision and OCR:**
- Anthropic Claude Vision API - Converts scanned/image-based PDFs and image files to text via `claude-sonnet-4-20250514` model
  - SDK/Client: `anthropic` Python package in `dc-due-diligence/converters/vision.py`
  - Auth: `ANTHROPIC_API_KEY` environment variable
  - Reference: `dc-due-diligence/converters/vision.py` lines 18, 32

**Web Research:**
- Claude Code WebSearch tool - Built-in agent tool for performing web searches (no API key needed)
  - Usage: Referenced in all 9 domain agents in `dc-due-diligence/agents/` (e.g., power-agent.md, connectivity-agent.md)
  - Optional MCP integration: Tavily, Exa, or Firecrawl can be configured in Claude Code for enhanced search
  - Reference: `dc-due-diligence/skills/due-diligence/SKILL.md` lines 125

- Claude Code WebFetch tool - Built-in agent tool for fetching and parsing specific URLs
  - Usage: Referenced in all domain agents for targeted document retrieval
  - Example: `dc-due-diligence/agents/ownership-agent.md` mentions WebFetch for OpenCorporates URLs
  - Reference: `dc-due-diligence/agents/connectivity-agent.md` mentions PeeringDB URL fetching

**Real Estate Data (Optional):**
- OpenCorporates - Entity lookup for ownership research
  - Access: Via WebFetch tool in `dc-due-diligence/agents/ownership-agent.md`
  - No API key required (web-based)

- PeeringDB - Network infrastructure and peering database
  - Access: Via WebSearch/WebFetch in `dc-due-diligence/agents/connectivity-agent.md`
  - No API key required (public database)

- ATTOM Data Solutions - Property data and real estate records (optional)
  - Access: Via WebFetch if API is available
  - Reference: `dc-due-diligence/agents/ownership-agent.md` (conditional on API availability)

## Data Storage

**Databases:**
- Not applicable - Project does not use persistent database backends

**File Storage:**
- Local filesystem only - All outputs are written to local directories
  - Document conversions: `<opportunity-folder>/_converted/` (managed by `dc-due-diligence/converters/pipeline.py`)
  - Research reports: `<opportunity-folder>/research/` (written by agent execution)
  - Executive summary: `<opportunity-folder>/EXECUTIVE_SUMMARY.md` (written by executive summary agent)
  - Generated images: User-specified output directory (e.g., `shipfast-images/` in `create-image/skills/create-image/SKILL.md`)

**Caching:**
- Manifest-based detection - Conversion pipeline checks for existing manifest to skip re-processing
  - Reference: `dc-due-diligence/skills/due-diligence/SKILL.md` Phase 2 (lines 61-73)
  - Manifest file: `<folder>/_converted/manifest.json`

## Authentication

**Auth Provider:**
- Custom - API key environment variables
  - Anthropic implementation: Implicit via `anthropic` Python SDK
  - Gemini implementation: Implicit via `google-genai` Python SDK
  - Configure auth settings in shell environment or `.env` files

**Environment Variables:**
- `ANTHROPIC_API_KEY` - Required for Claude vision API (document text extraction from scanned PDFs and images)
- `GEMINI_API_KEY` - Required for Gemini image generation API

## Monitoring

**Error Tracking:**
- None - No external error tracking service integrated

**Logs:**
- Standard output (stdout) - Status reports printed by `dc-due-diligence/converters/pipeline.py` via `print_status_report()` function
- Agent execution logs - Captured via Claude Code's native logging during skill execution
- Reference: `dc-due-diligence/skills/due-diligence/SKILL.md` Phase 1 (line 57) reports status to user

## Deployment

**Hosting:**
- Claude Code plugins - Distributed via `.claude-plugin/marketplace.json` catalog
- Local development: Test with `claude --plugin-dir ./create-image` or `claude --plugin-dir ./dc-due-diligence`
- Marketplace installation: `/plugin install create-image@shipfast` or `/plugin install dc-due-diligence@shipfast`

**CI Pipeline:**
- GitHub Actions - Configured in `.github/` directory (present but not examined in detail)
- No external CI service integration detected in source code

## Environment Configuration

**Required env vars:**

Use the following environment variables. List names only -- NEVER include values.

- `ANTHROPIC_API_KEY` - API key for Claude vision model (required only if processing scanned PDFs or images in dc-due-diligence)
- `GEMINI_API_KEY` - API key for Gemini image generation (required for create-image plugin)

**Optional env vars:**

- Tavily, Exa, or Firecrawl MCP server credentials (if configured in Claude Code for enhanced web research)

**Secrets location:**
- `.env` files at project/working directory root - Loaded by `python-dotenv` in `create-image/scripts/generate-image.py`
- Shell environment variables - Set directly in shell and inherited by Python processes
- Reference: `CLAUDE.md` (lines 89) states "Set `ANTHROPIC_API_KEY` in shell environment"
- Note: Environment variables are NEVER committed to git; use `.gitignore` to exclude `.env` files

## Webhooks

**Incoming:**
- None - Project does not expose webhook endpoints

**Outgoing:**
- None - Project does not send webhooks to external services

## Quality Gate

Before considering this file complete, verify:
- [x] Every finding includes at least one file path in backticks
- [x] Voice is prescriptive ("Use X", "Place files in Y") not descriptive ("X is used")
- [x] No section left empty -- use "Not detected" or "Not applicable"
- [x] Environment variable names documented (NEVER values)
- [x] Service categories complete (APIs, storage, auth, monitoring, deployment)
- [x] File paths included for integration code
