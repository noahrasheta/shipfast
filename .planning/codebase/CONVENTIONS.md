# Coding Conventions

**Analysis Date:** 2026-02-23

## Naming Patterns

**Files:**
- Use `snake_case` for Python module files: `pdf.py`, `scanner.py`, `excel.py`, `vision.py`, `word.py`, `powerpoint.py`
- Use `snake_case` for test files: `test_pdf_converter.py`, `test_folder_scanner.py`, `test_excel_converter.py`
- Use `lowercase-with-dashes` for agent markdown files: `research-agent.md`, `power-agent.md`, `connectivity-agent.md`
- Use UPPERCASE for skill markdown files: `SKILL.md`

**Functions and Methods:**
- Use `snake_case` for all function names: `convert()`, `scan_folder()`, `detect_file_type()`, `_extract_page()`
- Use `_leading_underscore` for private/internal functions: `_clean_text()`, `_rows_to_markdown()`, `_should_skip()`, `_extract()`, `_compute_readable_ratio()`
- Use lowercase for method names and properties: `can_handle()`, `convert()`, `is_reliable`, `is_low_confidence`

**Variables:**
- Use `snake_case` for local variables and parameters: `result`, `source_path`, `page_count`, `total_chars`, `text_parts`
- Use `UPPER_SNAKE_CASE` for module-level constants: `_SCANNED_CHARS_PER_PAGE_THRESHOLD`, `_HIGH_CONFIDENCE_CHARS_PER_PAGE`, `_MIN_READABLE_CHAR_RATIO`, `_READABLE_CHARS`, `_EXTENSION_TO_TYPE`, `_MIME_TO_TYPE`
- Use `_leading_underscore_lowercase` for private module-level constants: `_SKIP_NAMES` (set), `_TYPE_TO_CONVERTER` (dict)

**Types and Classes:**
- Use `PascalCase` for class names: `BaseConverter`, `ExtractionResult`, `PDFConverter`, `ExcelConverter`, `VisionConverter`, `ConfidenceLevel`, `FileType`, `ScanResult`, `FileEntry`
- Use `PascalCase` for Enum names: `ConfidenceLevel` (with uppercase values like `HIGH`, `MEDIUM`, `LOW`)
- Use `PascalCase` for Enum values representing file types: `FileType.PDF`, `FileType.XLSX`, `FileType.IMAGE_JPG`

## Code Style

**Formatting:**
- Follow PEP 8 conventions manually (no strict formatter enforced)
- Use 4 spaces for indentation consistently across all Python files
- Target line length around 79-88 characters for readability, though no hard limit enforced

**Linting:**
- No linting tool configured in the codebase
- Follow Python standard library conventions manually

## Import Organization

Use the following import order in all Python files:

1. **Module docstring** - Describe the file's purpose, key concepts, and module responsibilities (see `pdf.py`, `base.py`, `scanner.py` for patterns)

2. **Future imports** - Add `from __future__ import annotations` for forward compatibility (present in all converter files)

3. **Standard library imports** - Alphabetically ordered:
   - `import enum`
   - `import json`
   - `import logging`
   - `import mimetypes`
   - `from dataclasses import dataclass, field`
   - `from pathlib import Path`
   - `from typing import Any`

4. **Third-party package imports** - Alphabetically ordered:
   - `import anthropic`
   - `import openpyxl`
   - `import pdfplumber`
   - `import pillow` (as `from PIL import Image`)
   - `import pyxlsb`

5. **Local relative imports** - From the converters package:
   - `from converters.base import BaseConverter, ConfidenceLevel, ExtractionResult`
   - `from converters.excel import ExcelConverter`
   - `from converters.vision import VisionConverter`

**Path Aliases:**
- Not used in this codebase
- All imports use full relative paths: `from converters.pdf import PDFConverter`

**Example from `pdf.py` (lines 1-17):**
```python
"""
PDF text extraction using pdfplumber.

Handles text-based (machine-generated) PDFs by extracting body text and tables,
producing clean markdown output.  Scanned/image-based PDFs are detected via a
text-to-page ratio heuristic and automatically routed to Claude vision for
extraction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pdfplumber

from converters.base import BaseConverter, ConfidenceLevel, ExtractionResult
```

## Error Handling

**Strategy:** Never raise exceptions for expected failures. Return error states wrapped in the expected result type instead.

**Patterns:**
- Use conditional checks before risky operations (file existence, extension validation)
- Return `ExtractionResult` with `success=False` rather than raising exceptions
- Always catch broad `Exception` types and transform to user-friendly error messages
- Set `confidence=ConfidenceLevel.LOW` when extraction fails
- Populate `error` field with specific error details
- Document the failure reason in `confidence_reason` field

**Example from `pdf.py` (lines 75-108):**
```python
def convert(self, path: Path) -> ExtractionResult:
    path = Path(path).resolve()

    if not path.exists():
        return ExtractionResult(
            source_path=path,
            text="",
            method="pdfplumber",
            success=False,
            confidence=ConfidenceLevel.LOW,
            confidence_reason="file not found",
            error=f"File not found: {path}",
        )

    if not path.suffix.lower() == ".pdf":
        return ExtractionResult(
            source_path=path,
            text="",
            method="pdfplumber",
            success=False,
            confidence=ConfidenceLevel.LOW,
            confidence_reason="unsupported file type",
            error=f"Not a PDF file: {path.suffix}",
        )

    try:
        result = self._extract(path)
    except Exception as exc:
        return ExtractionResult(
            source_path=path,
            text="",
            method="pdfplumber",
            success=False,
            confidence=ConfidenceLevel.LOW,
            confidence_reason="extraction crashed",
            error=f"Extraction failed: {exc}",
        )
```

## Logging

**Framework:** Python's `logging` module

**Patterns:**
- Create a module-level logger at the top of each module: `logger = logging.getLogger(__name__)` (see `scanner.py` line 18)
- Use `logger.debug()` for detailed diagnostic information (file skipping details)
- Use `logger.warning()` for unexpected but recoverable situations
- Use `logger.info()` for informational messages about processing progress
- Do not use `print()` in library code for internal logging (though `pipeline.py` uses `print()` for user-facing output)

**Example from `scanner.py`:**
```python
import logging

logger = logging.getLogger(__name__)

# Usage in functions:
logger.debug("Skipping: %s", item)
logger.warning("Encountered unexpected file type: %s", file_type)
logger.info("Scanned folder: %s files found", total_count)
```

## Comments and Docstrings

**When to Comment:**
- Add docstrings to all public classes and functions
- Add comments for complex algorithmic logic (e.g., table extraction strategy in `pdf.py`)
- Avoid comments that restate obvious code; comment "why" not "what"
- Use comment headers (`# ------------------------------------------------------------------`) to separate test suite sections

**Docstring Pattern:**
- Use triple-quoted docstrings for all modules, classes, and public functions
- For modules: Describe overall purpose, key concepts, and responsibilities
- For classes: Include description and document important attributes using `Attributes:` section
- For functions: Include description, parameters (with types), and return type

**Module Docstring Example from `base.py` (lines 1-7):**
```python
"""
Base converter interface and shared data models.

All file type converters inherit from BaseConverter and return ExtractionResult
instances so downstream agents receive a consistent structure regardless of
the source file format.
"""
```

**Class Docstring Example from `base.py` (lines 25-42):**
```python
@dataclass
class ExtractionResult:
    """Standard result returned by every converter.

    Attributes:
        source_path: Absolute path to the original file.
        text: The extracted text content (markdown-formatted where possible).
        method: Short label for how the text was extracted.
        success: Whether the extraction completed without critical errors.
        confidence: Overall confidence in the extracted text quality.
        confidence_reason: Human-readable explanation of why the confidence
            level was assigned.
        page_count: Number of pages (for PDFs) or sheets (for spreadsheets).
        is_scanned: True if the document appears to be scanned/image-based.
        metadata: Arbitrary extra info specific to the file type.
        error: Error message if success is False.
    """
```

**Function Docstring Example from `pdf.py` (lines 67-72):**
```python
def convert(self, path: Path) -> ExtractionResult:
    """Open a PDF with pdfplumber, extract all pages, and return markdown.

    Scanned documents (very little embedded text) are detected and
    automatically routed to Claude vision if *vision_fallback* is enabled.
    """
```

## Function Design

**Size:**
- Keep functions focused on a single responsibility
- Most converter functions are 50-150 lines
- Break complex logic into smaller private helper functions
- Example: `pdf.py` has `_extract()` (131-207), `_extract_page()` (209-254), `_extract_text_outside_tables()` (256-302), and several module-level helpers

**Parameters:**
- Accept file paths as `Path` objects, not strings (see `base.py` line 100: `path: Path`)
- Use keyword arguments for optional parameters: `vision_fallback: bool = True`
- Limit parameters to 3-4; use dataclasses for complex configurations
- Always include default values for optional parameters

**Return Values:**
- Return dataclass instances for structured results (e.g., `ExtractionResult`)
- Always return typed results even for error cases - never return `None`
- Use properties for computed/derived values: `is_reliable`, `is_low_confidence`, `confidence_summary` (see `base.py` lines 55-87)

## Module Design

**Exports:** Use `__all__` to explicitly declare public exports in package `__init__.py` files.

**Pattern from `converters/__init__.py` (lines 39-63):**
```python
__all__ = [
    "BaseConverter",
    "ConfidenceLevel",
    "ConvertedFile",
    "CONVERTED_DIR_NAME",
    "convert_folder",
    "ExcelConverter",
    "ExtractionResult",
    "FileEntry",
    "FileType",
    # ... etc
]
```

**Barrel Files:** Use package `__init__.py` to re-export frequently imported items from submodules.
- The `converters` package re-exports converters, result types, and utility functions
- This allows downstream code to use `from converters import PDFConverter` instead of `from converters.pdf import PDFConverter`
- Always maintain `__all__` to be explicit about what's public

## Type Hints

Use type hints on all function signatures and class attributes.

**Patterns:**
- Use `from __future__ import annotations` at the top of every module (enables forward references)
- Use `Path` type for file paths: `path: Path` (not strings)
- Use union types with `|` operator: `error: str | None`
- Use generics for collections: `list[str]`, `dict[str, Any]`
- Use dataclass field hints with default factories for mutable defaults: `metadata: dict = field(default_factory=dict)`
- Use `Enum` types for fixed option sets: `confidence: ConfidenceLevel`

**Example from `base.py` (lines 44-53):**
```python
@dataclass
class ExtractionResult:
    source_path: Path
    text: str
    method: str
    success: bool
    confidence: ConfidenceLevel
    confidence_reason: str = ""
    page_count: int = 0
    is_scanned: bool = False
    metadata: dict = field(default_factory=dict)
    error: str | None = None
```

## Dataclass Usage

Use dataclasses extensively for structured return types and data containers.

**Advantages:**
- Type-safe with type hints
- Auto-generated `__init__` method
- Easy serialization to JSON
- Clear field documentation in one place
- Immutability with `frozen=True` if needed

**All major data types in converters use dataclasses:**
- `ExtractionResult` - Standard result from every converter
- `FileEntry` - Single file discovered during scanning
- `ScanResult` - Folder scan results with file entries and metadata
- `ConvertedFile` - Result of converting a single file
- `PipelineResult` - Result of processing an entire folder
- `PDFResult` - Result of generating a PDF report

## Agent and Skill Conventions

**Agent Files:**
- Name as `lowercase-with-dashes.md` (e.g., `power-agent.md`, `connectivity-agent.md`)
- Include YAML frontmatter with `name` and `description` fields
- Use backtick-wrapped code for file path references
- Store in `agents/` directory of a plugin

**Skill Files:**
- Use directory format: `skills/<skill-name>/SKILL.md`
- Begin with YAML frontmatter specifying `name`, `description`, and `version`
- Use structured phases with numbered steps for orchestration workflows
- Store in `skills/` directory of a plugin

**File Paths in Agents:**
- Use `${CLAUDE_PLUGIN_ROOT}` to reference files within a plugin (see `CLAUDE.md` line 66)
- Never hardcode absolute paths in agent instructions

---

*Convention analysis: 2026-02-23*
