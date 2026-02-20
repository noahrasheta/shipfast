# Coding Conventions

**Analysis Date:** 2026-02-20

## Naming Patterns

**Files:**
- Use `snake_case` for Python module files: `pdf.py`, `scanner.py`, `vision.py`
- Use `snake_case` for test files: `test_pdf_converter.py`, `test_folder_scanner.py`
- Use UPPERCASE for constants in module-level configuration files (see `pdf.py` line 19-24)

**Functions:**
- Use `snake_case` for all function names: `convert()`, `scan_folder()`, `_extract_page()`
- Use `_leading_underscore` for private/internal functions: `_clean_text()` in `pdf.py`, `_rows_to_markdown()` in `pdf.py`
- Use lowercase for method names: `can_handle()`, `convert()`, `is_reliable` (properties in `base.py`)

**Variables:**
- Use `snake_case` for local variables and parameters: `result`, `source_path`, `page_count`
- Use `UPPER_SNAKE_CASE` for module constants: `_SCANNED_CHARS_PER_PAGE_THRESHOLD` in `pdf.py` line 21
- Use `lowercase_with_underscores` for instance attributes: `self._vision_fallback`, `self._api_key` in `pdf.py`

**Types:**
- Use `PascalCase` for class names: `BaseConverter`, `ExtractionResult`, `PDFConverter`, `ConfidenceLevel`
- Use `PascalCase` for Enum names: `FileType`, `ConfidenceLevel` (in `base.py` and `scanner.py`)

## Code Style

**Formatting:**
- No explicit formatter is configured in the codebase. Follow PEP 8 manually.
- Use 4 spaces for indentation (consistent across all Python files: `pdf.py`, `scanner.py`, `pipeline.py`)
- Maximum line length: No strict enforced limit, but aim for readability (lines in `pdf.py` are typically under 100 characters)

**Linting:**
- No linting tool is configured. Follow Python conventions manually.
- Code does not enforce a linter configuration file.

## Import Organization

Use the following import order in all Python files. See `pdf.py`, `excel.py`, and `converters/__init__.py` for reference.

**Order:**
1. Module docstring (describing the file's purpose)
2. `from __future__ import annotations` (for forward compatibility)
3. Standard library imports (alphabetically): `import enum`, `import json`, `from pathlib import Path`, `from typing import Any`
4. Third-party package imports (alphabetically): `import pdfplumber`, `import openpyxl`, `import anthropic`
5. Local relative imports: `from converters.base import BaseConverter, ExtractionResult`

**Path Aliases:**
- Not used in this codebase. All imports use full relative paths: `from converters.pdf import PDFConverter`
- Use relative imports for converters submodule: `from converters.base import BaseConverter` (in `pdf.py` line 17)

## Error Handling

Use the following error handling patterns. See `pdf.py` lines 62-94 and `excel.py` lines 42-79 for reference.

**Patterns:**
- Use conditional checks before operations (before opening files, before accessing properties)
- Return error states wrapped in the expected result type (`ExtractionResult` with `success=False`) rather than raising exceptions
- Always catch broad `Exception` types and transform to user-friendly error messages (see `pdf.py` line 85)
- Set `confidence=ConfidenceLevel.LOW` and populate `error` field when extraction fails
- Document why confidence is low in `confidence_reason` field

**Example from `pdf.py` (lines 83-94):**
```python
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

**Framework:** Python's `logging` module - Used in `scanner.py` line 18

**Patterns:**
- Create a module-level logger: `logger = logging.getLogger(__name__)` (in `scanner.py` line 18)
- Use logger for informational messages about processing progress
- Do not use print() for logging in library code (though `pipeline.py` uses print() for user-facing output)

## Comments

**When to Comment:**
- Add docstrings to all public classes and functions
- Add comments for complex logic (see `pdf.py` lines 189-216 explaining table extraction strategy)
- Avoid comments restating obvious code; comment "why" not "what"

**Docstring Pattern:**
- Use triple-quoted docstrings for all modules, classes, and public functions
- For modules: Describe overall purpose and key concepts (see `base.py` lines 1-7)
- For classes: Include description and document key attributes (see `base.py` lines 24-42)
- For functions: Include description, parameters (using proper format), and any return info (see `pdf.py` lines 53-58)

**Example from `pdf.py` (lines 53-58):**
```python
def convert(self, path: Path) -> ExtractionResult:
    """Open a PDF with pdfplumber, extract all pages, and return markdown.

    Scanned documents (very little embedded text) are detected and
    automatically routed to Claude vision if *vision_fallback* is enabled.
    """
```

## Function Design

**Size:** Keep functions focused on a single responsibility. Most converter functions are 50-100 lines. Use helper functions to break complex logic into smaller pieces (see `pdf.py` lines 117-269 with `_extract()`, `_extract_page()`, `_extract_text_outside_tables()` helper functions).

**Parameters:**
- Accept file paths as `Path` objects, not strings (see `base.py` line 100: `def can_handle(self, path: Path) -> bool`)
- Use keyword arguments for optional parameters: `vision_fallback: bool = True` (in `pdf.py` line 37)
- Limit parameters to 3-4; use dataclasses for complex configurations (see `ExtractionResult` in `base.py` lines 24-53)

**Return Values:**
- Return dataclass instances for structured results: `ExtractionResult` from all converters
- Always return typed results even for error cases (never return None; return `ExtractionResult` with `success=False`)
- Use properties for computed values: `is_reliable`, `is_low_confidence`, `confidence_summary` (in `base.py` lines 55-87)

## Module Design

**Exports:** Use `__all__` to explicitly declare public exports - See `converters/__init__.py` lines 32-51

**Pattern from `converters/__init__.py`:**
```python
__all__ = [
    "BaseConverter",
    "ConfidenceLevel",
    "ExtractionResult",
    # ... list all public exports
]
```

**Barrel Files:** Use a package `__init__.py` to re-export frequently imported items from submodules. The `converters` package re-exports converters, result types, and utility functions (see `converters/__init__.py` lines 16-30). This allows downstream code to use `from converters import PDFConverter` instead of `from converters.pdf import PDFConverter`.

## Plugin and Skill Conventions

**Agent Files:**
- Name agent files as `lowercase-with-dashes.md` (e.g., `research-agent.md`, `power-agent.md`)
- Include YAML frontmatter with `name` and `description` fields (see `research-agent.md` lines 1-26)
- Use backtick-wrapped code for file path references in agent instructions

**Skill Files:**
- Use directory format: `skills/<skill-name>/SKILL.md` (see `skills/due-diligence/SKILL.md`)
- Begin with YAML frontmatter specifying `name`, `description`, and `version`
- Use structured phases with numbered steps for orchestration workflows (see `skills/due-diligence/SKILL.md` lines 8-100+)

**File Paths in Agents:**
- Use `${CLAUDE_PLUGIN_ROOT}` to reference files within a plugin (documented in `CLAUDE.md` line 66)
- Never hardcode absolute paths in agent instructions

## Type Hints

Use type hints on all function signatures and class attributes.

**Patterns:**
- Use `from __future__ import annotations` at the top of every module (see all converter files)
- Use `Path` type for file paths: `path: Path` (in `base.py` line 100)
- Use union types with `|` operator: `error: str | None` (in `base.py` line 53)
- Use generics for collections: `list[str]`, `dict[str, Any]` (in `base.py` line 98)
- Use dataclass field hints with default factories: `metadata: dict = field(default_factory=dict)` (in `base.py` line 52)

## Dataclass Usage

Use dataclasses extensively for structured return types and data containers.

**Pattern from `base.py` (lines 24-53):**
```python
@dataclass
class ExtractionResult:
    """Standard result returned by every converter."""
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

Benefits: Type-safe, auto-generated `__init__`, easy serialization, clear field documentation.
