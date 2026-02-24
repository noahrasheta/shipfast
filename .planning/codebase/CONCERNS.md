# Codebase Concerns

**Analysis Date:** 2026-02-23

## Tech Debt

**Vision API Model Hardcoding:**
- Issue: The vision model is hardcoded to `claude-sonnet-4-20250514` without configuration option
- Files: `dc-due-diligence/converters/vision.py` (line 32)
- Impact: Model version cannot be updated without code changes; potential breaking changes if API deprecates this model
- Fix approach: Extract model selection to environment variable or plugin configuration parameter, defaulting to the hardcoded value for backwards compatibility

**Broad Exception Catching:**
- Issue: Multiple converters use bare `except Exception` without logging exception types
- Files:
  - `dc-due-diligence/converters/pdf.py` (line 99)
  - `dc-due-diligence/converters/excel.py` (line 70)
  - `dc-due-diligence/converters/powerpoint.py` (line 62)
  - `dc-due-diligence/converters/word.py` (line 62)
  - `dc-due-diligence/converters/pipeline.py` (line 411)
- Impact: Difficult to diagnose failures; swallows potential programming errors alongside genuine failures
- Fix approach: Catch specific exceptions (pdfplumber errors, openpyxl errors, etc.) separately; log exception type and traceback for debugging

**Loose Confidence Thresholds:**
- Issue: PDF and vision converters use hardcoded character-per-page thresholds (200 chars) to determine if document is scanned
- Files: `dc-due-diligence/converters/pdf.py` (lines 19-29)
- Impact: Thresholds may not work well across different document types; no way to tune for specific use cases
- Fix approach: Move thresholds to configurable constants with documented reasoning; allow override at converter instantiation

**API Key Dependency Uncertainty:**
- Issue: VisionConverter requires `ANTHROPIC_API_KEY` environment variable; silently falls back to anthropic SDK default if not provided
- Files: `dc-due-diligence/converters/vision.py` (lines 110-122)
- Impact: Fails at conversion time with authentication error if key isn't set; user must restart Claude Code after setting env var
- Fix approach: Validate API key availability at pipeline initialization time with clear error message

## Known Bugs

**Scanned PDF Detection False Negatives:**
- Symptoms: Low-density but valid PDFs (like financial tables with lots of whitespace) may be misclassified as scanned and routed to vision API unnecessarily
- Files: `dc-due-diligence/converters/pdf.py` (lines 150-164)
- Trigger: PDFs with valid text but average < 200 chars/page (spreadsheets, forms, spaced layouts)
- Workaround: None -- converters will attempt vision extraction. Results are still correct, just slower and more expensive

**Gibberish Detection Overly Aggressive:**
- Symptoms: Valid PDFs with technical content, CJK characters, or special formatting may be flagged as gibberish
- Files: `dc-due-diligence/converters/pdf.py` (lines 160-164, 310-320)
- Trigger: Documents with mathematical symbols, chemical formulas, code blocks, or non-ASCII characters where readable_ratio < 0.75
- Workaround: Confidence will be marked as LOW but extraction proceeds; vision fallback is triggered

**Manifest Not Validated Before Reading:**
- Symptoms: If manifest.json is corrupted or incomplete, agents may fail when reading file confidence information
- Files: `dc-due-diligence/skills/due-diligence/SKILL.md` (Phase 2, step 3)
- Trigger: Incomplete pipeline run that partially writes manifest; manual manifest editing
- Workaround: Re-run pipeline to regenerate manifest

## Security Considerations

**API Key Exposure Risk:**
- Risk: ANTHROPIC_API_KEY passed to VisionConverter as parameter; could be logged in exception messages
- Files: `dc-due-diligence/converters/vision.py`, `dc-due-diligence/converters/pipeline.py`
- Current mitigation: Exception handlers catch and re-raise with generic error message
- Recommendations:
  - Mask API key in all string representations
  - Use `None` as default and only access via environment variable
  - Add warning in documentation about shell history logging

**File Path Traversal in Document Processing:**
- Risk: Pipeline uses user-provided folder path without validation; could theoretically process files outside intended directory if symlinks exist
- Files: `dc-due-diligence/converters/scanner.py` (line 245)
- Current mitigation: OSError exception handler catches file read failures
- Recommendations:
  - Resolve all paths with `Path.resolve()` and verify they're within opportunity folder
  - Reject symlinks outside the scanned root with explicit error

**Vision API Token Limits:**
- Risk: Large PDFs or high-resolution images sent to vision API; no defense against token exhaustion or API rate limiting
- Files: `dc-due-diligence/converters/vision.py` (line 35: `_MAX_TOKENS_PER_PAGE = 4096`)
- Current mitigation: Max tokens set to 4096; image resizing to 2048 dimension limit
- Recommendations:
  - Implement exponential backoff retry logic for 429 (rate limit) responses
  - Track total tokens used per run and warn when approaching limits
  - Document per-run cost expectations

## Performance Bottlenecks

**Vision API Sequential Processing:**
- Problem: PDFs are processed page-by-page sequentially through vision API; scales linearly with page count
- Files: `dc-due-diligence/converters/vision.py` (lines 211-220)
- Cause: Anthropic SDK client is created once per VisionConverter instance; each page waits for previous API response
- Improvement path:
  - Consider concurrent requests with semaphore (max 3-5 parallel) to leverage API connection pooling
  - Implement batching if Anthropic API supports multi-image requests in future
  - Cache vision results to avoid re-processing same PDF if pipeline is re-run

**Large PDF In-Memory Rendering:**
- Problem: All PDF pages rendered to PIL images in memory before encoding to JPEG
- Files: `dc-due-diligence/converters/vision.py` (lines 68-78)
- Cause: pypdfium2 renders each page fully; no streaming support
- Improvement path:
  - Monitor memory usage for PDFs > 500 pages
  - Implement disk-based caching of rendered pages if needed
  - Consider reducing render DPI from 200 to 150 for very large documents

**String Concatenation in Pipeline:**
- Problem: All page texts concatenated with string joins in memory
- Files: `dc-due-diligence/converters/pipeline.py` (line 148)
- Cause: Using `"\n\n---\n\n".join(page_texts)` creates intermediate strings for large documents
- Improvement path: For documents > 1000 pages, use StringIO or write to file incrementally

**Excel Sheet Iteration Inefficiency:**
- Problem: openpyxl reads entire workbook into memory; no lazy sheet loading
- Files: `dc-due-diligence/converters/excel.py` (line 87)
- Cause: `load_workbook` with default settings; no option for read_only mode for very large sheets
- Improvement path:
  - Document performance expectations for workbooks > 50MB
  - Consider using `data_only=True` more carefully to avoid formula recalculation delays
  - Provide option to skip sheets by name pattern

## Fragile Areas

**Markdown Filename Collision Handling:**
- Files: `dc-due-diligence/converters/pipeline.py` (lines 343-344, 516-530)
- Why fragile: Filename uniqueness maintained with numeric suffixes; concurrent pipeline runs could create race condition on `used_filenames` dict
- Safe modification:
  - Single-threaded pipeline is safe as-is
  - If multi-threading added: use thread-safe Counter or atomic file operations
  - Prefer UUID-based filenames for distributed scenarios
- Test coverage: Covered by `test_pipeline_handles_duplicate_filenames` in tests

**Page Order Preservation in PDF Extraction:**
- Files: `dc-due-diligence/converters/pdf.py` (lines 209-254)
- Why fragile: Table extraction uses bounding box positioning; if pdfplumber changes coordinate system or table detection logic, order could shift
- Safe modification:
  - Test with multiple PDF libraries (PyPDF2, pikepdf) to verify coordinate assumptions
  - Log bounding boxes and table count for validation
  - Add integration tests with real-world data center PDFs
- Test coverage: Basic PDF tests exist; no regression tests with actual broker documents

**Confidence Level String Matching:**
- Files: `dc-due-diligence/converters/pipeline.py` (line 101, 283)
- Why fragile: Direct string comparison `f.confidence == "low"` instead of enum checks
- Safe modification:
  - Change `ConvertedFile.confidence` from string to ConfidenceLevel enum
  - Update manifest JSON serialization to preserve enum
  - This requires changes to skill code that reads manifest
- Test coverage: Tests use hardcoded strings; would need updates

**Template and Style File Path Resolution:**
- Files: `dc-due-diligence/converters/generate_pdf.py` (line 25)
- Why fragile: CSS stylesheets located via `Path(__file__).resolve().parent.parent / "templates" / "pdf-styles"`
- Safe modification:
  - Assumes templates directory exists relative to converter module
  - If converters module is packaged differently, paths break
  - Add validation that stylesheet files exist before conversion attempt
  - Consider fallback to inline CSS if file-based lookup fails
- Test coverage: No test for missing stylesheet graceful handling

## Scaling Limits

**Document Folder Size:**
- Current capacity: Tested with ~50 files, ~500MB total
- Limit: Processing all files sequentially; manifest JSON loaded entirely into memory
- Scaling path:
  - Implement streaming manifest reading for > 1000 files
  - Add file size filtering to skip very large documents (> 100MB)
  - Implement early termination if converted folder exceeds disk space

**Vision API Cost:**
- Current capacity: ~$0.03 per page at current pricing (Sonnet 4)
- Limit: A 500-page scanned PDF = ~$15 in API calls; unclear budgeting/cost tracking
- Scaling path:
  - Add dry-run mode that estimates cost without making API calls
  - Implement page sampling: extract every Nth page for large documents
  - Cache vision results per file hash to avoid re-processing

**Concurrent Agent Execution:**
- Current capacity: Pipeline runs single-threaded per skill execution
- Limit: Multi-agent architecture in skills can spawn 9 agents in parallel (Wave 1); depends on Claude Code task limits
- Scaling path:
  - Document max parallelism constraints
  - Implement task queue with rate limiting if needed
  - Add monitoring for agent spawn failure due to resource limits

## Dependencies at Risk

**Anthropic SDK Version:**
- Risk: requirements.txt pins `anthropic==0.83.0`; API changes between minor versions could break
- Impact: Vision extraction fails if API response format changes
- Migration plan:
  - Document minimum supported anthropic version in pyproject.toml
  - Add integration test that validates API response structure
  - Track Anthropic SDK releases and test quarterly

**pdfplumber Maintenance:**
- Risk: pdfplumber is actively maintained but relatively small ecosystem
- Impact: Extraction logic depends on specific table detection algorithm; significant refactor needed if library changes
- Migration plan:
  - Maintain vendor copy of critical pdfplumber functions if possible
  - Track issues at github.com/jsvine/pdfplumber for stability concerns
  - Have fallback plan to switch to pypdf for basic text extraction

**markdown-pdf Library Stability:**
- Risk: markdown-pdf uses PyMuPDF which is pure Python but complex; depends on pymupdf wheels
- Impact: PDF generation crashes on unsupported file format or platform
- Migration plan:
  - Document supported platforms (macOS, Linux, Windows)
  - Add smoke test for PDF generation in CI
  - Consider weasyprint as alternative if markdown-pdf becomes unmaintained

**Python 3.11+ Requirement:**
- Risk: pyproject.toml requires Python 3.11+; 3.10 EOL is Oct 2026
- Impact: Users on older Python versions cannot install; slow adoption of new minor versions
- Migration plan:
  - Document support matrix: Python 3.11 (primary), 3.12 (tested), 3.13 (experimental)
  - Set reminder to test with Python 3.14 when released
  - Consider dropping 3.11 support in v1.0 to use new language features

## Missing Critical Features

**Incremental Conversion:**
- Problem: Pipeline always re-processes all files; no way to update only changed documents
- Blocks: Re-running analysis on same folder with new documents requires re-converting everything
- Suggested implementation:
  - Store file modification times in manifest
  - Skip unchanged files, only convert new/modified ones
  - Update manifest incrementally

**Document Encryption Support:**
- Problem: Encrypted PDFs fail silently with extraction error
- Blocks: Cannot process password-protected broker documents
- Suggested implementation:
  - Add optional password parameter to convert_folder
  - Prompt user for password if PDF is encrypted
  - Document security implications of password handling

**Asset Reference Preservation:**
- Problem: Extracted markdown loses references to embedded images/links in source documents
- Blocks: Cannot reconstruct document structure with visual elements
- Suggested implementation:
  - Extract embedded images from PDFs/Office documents
  - Store image references in manifest with confidence scores
  - Include images in generated summaries if needed

## Test Coverage Gaps

**End-to-End Real Document Testing:**
- What's not tested: Actual broker documents (real PDFs, Word docs, complex spreadsheets)
- Files: Test data exists in `/tests/` but uses synthetic documents
- Risk: Converter failures on real-world documents may not be caught until production use
- Priority: High
- Recommendation: Add integration tests with anonymized/redacted real broker documents

**API Failure Scenarios:**
- What's not tested: Vision API authentication failures, rate limiting, network errors
- Files: `dc-due-diligence/tests/` has no test for anthropic.APIError handling
- Risk: Production failures with no test coverage; unclear error messages to users
- Priority: High
- Recommendation: Mock anthropic client to test timeout, auth, and rate limit scenarios

**Filesystem Edge Cases:**
- What's not tested: Permission errors, disk full, symlink behavior, very long path names
- Files: `dc-due-diligence/converters/scanner.py` (line 245) catches OSError but only one test
- Risk: Silent failures or incomplete processing if permissions/disk issues occur
- Priority: Medium
- Recommendation: Add tests for mkdir failures, read permission denied, disk space limits

**Large Document Processing:**
- What's not tested: PDFs > 500 pages, Excel files > 50MB, deeply nested folder structures
- Files: No load/stress tests exist
- Risk: Memory exhaustion or timeout on large documents; no prior warning
- Priority: Medium
- Recommendation: Add parametrized tests with synthetic large documents; measure memory usage

**Manifest Corruption Handling:**
- What's not tested: Invalid JSON, missing required fields, partial writes
- Files: `dc-due-diligence/skills/due-diligence/SKILL.md` reads manifest but has no error handling
- Risk: Skill crashes if manifest is corrupted; unclear recovery path
- Priority: Low
- Recommendation: Add validation schema; implement graceful degradation if fields missing

---

*Concerns audit: 2026-02-23*
