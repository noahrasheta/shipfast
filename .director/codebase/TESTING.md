# Testing Patterns

**Analysis Date:** 2026-02-20

## Test Framework

**Runner:**
- `pytest` 8.0.0+ (declared in `pyproject.toml` line 18)
- Config: `pyproject.toml` - testpaths configured at lines 28-29

**Assertion Library:**
- Built-in `assert` statements - Used throughout all test files
- Also uses pytest.raises() for exception testing (see `test_imports.py` line 192)

**Run Commands:**
```bash
pytest dc-due-diligence/tests                    # Run all tests
pytest dc-due-diligence/tests -v                 # Verbose output
pytest dc-due-diligence/tests --cov=converters   # Coverage report
pytest dc-due-diligence/tests -k test_pdf        # Run specific tests matching pattern
```

## Test File Organization

**Location:**
- Place test files in a `tests/` directory at the same level as the code being tested - See `dc-due-diligence/tests/`
- Tests are organized as a separate package alongside `converters/` in `dc-due-diligence/`

**Naming:**
- Use `test_<module>.py` pattern: `test_pdf_converter.py`, `test_folder_scanner.py`, `test_excel_converter.py`
- Create an `__init__.py` in the tests directory to make it a package (see `tests/__init__.py`)

**Directory Structure:**
```
dc-due-diligence/
├── converters/
│   ├── __init__.py
│   ├── base.py
│   ├── pdf.py
│   ├── excel.py
│   ├── scanner.py
│   └── ... (other converters)
├── tests/
│   ├── __init__.py
│   ├── test_pdf_converter.py
│   ├── test_excel_converter.py
│   ├── test_folder_scanner.py
│   ├── test_vision_converter.py
│   ├── test_word_converter.py
│   ├── test_powerpoint_converter.py
│   ├── test_imports.py
│   └── test_status_reporting.py
├── pyproject.toml
└── opportunity-example/  (optional real-world test data)
```

## Test Structure

**Suite Organization:**

Follow this pattern when writing new tests. See `test_pdf_converter.py` for reference.

```python
"""Tests for the PDF text extraction converter."""

from pathlib import Path
import pytest
from converters import ConfidenceLevel, ExtractionResult
from converters.pdf import PDFConverter, _clean_text, _rows_to_markdown


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

OPPORTUNITY_DIR = Path(__file__).resolve().parent.parent / "opportunity-example"

@pytest.fixture
def converter():
    return PDFConverter(vision_fallback=False)


# ------------------------------------------------------------------
# Unit tests for helper functions
# ------------------------------------------------------------------

class TestCleanText:
    def test_strips_trailing_spaces(self):
        assert _clean_text("hello   \nworld  ") == "hello\nworld"

    def test_collapses_blank_lines(self):
        result = _clean_text("a\n\n\n\n\nb")
        assert result == "a\n\n\nb"


# ------------------------------------------------------------------
# Converter behaviour tests
# ------------------------------------------------------------------

class TestPDFConverterBasics:
    def test_supported_extensions(self, converter):
        assert converter.supported_extensions == [".pdf"]

    def test_can_handle_pdf(self, converter):
        assert converter.can_handle(Path("report.pdf")) is True


# ------------------------------------------------------------------
# Integration tests against real opportunity PDFs
# ------------------------------------------------------------------

class TestRealPDFs:
    """Integration tests that run against the actual example documents."""

    @pytest.fixture
    def converter(self):
        return PDFConverter(vision_fallback=False)

    def _get_pdf(self, name: str) -> Path:
        pdf = OPPORTUNITY_DIR / name
        if not pdf.exists():
            pytest.skip(f"Example PDF not found: {name}")
        return pdf

    def test_text_pdf_extracts_content(self, converter):
        pdf = self._get_pdf("0a. Datanovax Teaser Part I ext.pdf")
        result = converter.convert(pdf)
        assert result.success is True
```

**Patterns:**
- Use fixture sections marked with comment headers (`# ------------------------------------------------------------------`) to organize test structure
- Group tests into classes by functionality: `TestCleanText`, `TestPDFConverterBasics`, `TestRealPDFs`
- Separate unit tests from integration tests with clear comment sections
- Use descriptive test method names that describe the exact behavior being tested

## Mocking

**Framework:** `unittest.mock` (standard library) via pytest - See `test_imports.py` for patterns

**Patterns:**

Use pytest's `tmp_path` fixture for temporary file creation instead of mocking I/O:

```python
@pytest.fixture
def simple_xlsx(tmp_path):
    """Create a simple .xlsx file with one sheet of data."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Site", "Power (MW)", "Cost ($/kWh)"])
    ws.append(["Dallas", 10, 0.045])
    path = tmp_path / "test_data.xlsx"
    wb.save(str(path))
    wb.close()
    return path
```

**What to Mock:**
- External API calls when they would make real network requests (handled via environment variables in `vision.py`)
- File system operations when testing error paths (use `pytest.raises()` instead)

**What NOT to Mock:**
- Converter implementations themselves - test real behavior
- File operations - use temporary files instead (`tmp_path` fixture)
- Standard library functions unless they have side effects
- Internal helper functions - test them directly as unit tests

## Fixtures and Test Data

**Pattern:**

Follow this pattern for test data. See `test_excel_converter.py` lines 32-92 for reference.

```python
import tempfile
from pathlib import Path
import pytest
import openpyxl

OPPORTUNITY_DIR = Path(__file__).resolve().parent.parent / "opportunity-example"

@pytest.fixture
def simple_xlsx(tmp_path):
    """Create a simple .xlsx file with one sheet of data."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Summary"
    ws.append(["Site", "Power (MW)"])
    ws.append(["Dallas", 10])
    path = tmp_path / "test_data.xlsx"
    wb.save(str(path))
    wb.close()
    return path

@pytest.fixture
def converter():
    return ExcelConverter()
```

**Location:**
- Place module-level constants like `OPPORTUNITY_DIR` at the top of test files (see `test_pdf_converter.py` line 15)
- Define fixtures immediately after constants
- Use `pytest.fixture` decorator on functions that return test data
- Fixtures can create temporary directories via `tmp_path` parameter (automatically provided by pytest)

**Real Data:**
- Store optional example/integration test data in `opportunity-example/` directory alongside tests
- Use `pytest.skip()` when real data is missing so tests don't fail in CI (see `test_pdf_converter.py` line 144)

## Coverage

**Requirements:** No enforced coverage target, but maintain reasonable coverage for critical modules.

**View Coverage:**
```bash
pytest dc-due-diligence/tests --cov=converters --cov-report=html
# Then open htmlcov/index.html in a browser
```

## Test Types

**Unit Tests:**
- Scope: Test individual functions and methods in isolation - Test helper functions like `_clean_text()`, `_rows_to_markdown()` (see `test_pdf_converter.py` lines 28-77)
- Approach: Use fixtures to create input data, call the function, assert the output. Use parametrized tests for multiple scenarios.
- Example from `test_folder_scanner.py`:
```python
class TestDetectFileType:
    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("report.pdf", FileType.PDF),
            ("data.xlsx", FileType.XLSX),
            ("contract.docx", FileType.DOCX),
        ],
    )
    def test_recognized_extensions(self, filename: str, expected: FileType):
        assert detect_file_type(Path(filename)) == expected
```

**Integration Tests:**
- Scope: Test multiple components working together - Test converters against real documents (see `test_pdf_converter.py` lines 130-228)
- Approach: Use real files from `opportunity-example/` or create temporary test files. Verify the entire conversion pipeline produces correct output.
- Example from `test_pdf_converter.py` lines 147-155:
```python
def test_text_pdf_extracts_content(self, converter):
    pdf = self._get_pdf("0a. Datanovax Teaser Part I ext.pdf")
    result = converter.convert(pdf)
    assert result.success is True
    assert result.page_count > 0
    assert len(result.text) > 100
```

**E2E Tests:**
- Not explicitly used in this codebase - Integration tests serve this purpose for document processing

## Common Patterns

**Error Testing:**

Use `pytest.raises()` to test error cases. See `test_imports.py` lines 187-193:

```python
def test_base_converter_requires_override():
    from converters import BaseConverter
    import pytest

    converter = BaseConverter()
    with pytest.raises(NotImplementedError):
        converter.convert(Path("/tmp/test.pdf"))
```

**Missing Files:**

Test missing file handling without actually deleting files. Use nonexistent paths:

```python
def test_missing_file_returns_error(self, converter):
    result = converter.convert(Path("/tmp/does_not_exist_12345.pdf"))
    assert result.success is False
    assert result.confidence == ConfidenceLevel.LOW
```

**Parametrized Tests:**

Use `@pytest.mark.parametrize` to test multiple scenarios with one test function - See `test_folder_scanner.py` lines 33-61:

```python
@pytest.mark.parametrize(
    "filename, expected",
    [
        ("report.pdf", FileType.PDF),
        ("report.PDF", FileType.PDF),
        ("data.xlsx", FileType.XLSX),
    ],
)
def test_recognized_extensions(self, filename: str, expected: FileType):
    assert detect_file_type(Path(filename)) == expected
```

**Conditional Test Skipping:**

Use `pytest.skip()` when test prerequisites aren't available - See `test_pdf_converter.py` lines 141-145:

```python
def _get_pdf(self, name: str) -> Path:
    pdf = OPPORTUNITY_DIR / name
    if not pdf.exists():
        pytest.skip(f"Example PDF not found: {name}")
    return pdf
```

This allows tests to run in CI without real data while running fully when data is available.

**Testing Data Properties:**

Always verify output properties match expected types and values - See `test_pdf_converter.py` lines 157-164:

```python
def test_text_pdf_has_metadata(self, converter):
    pdf = self._get_pdf("0a. Datanovax Teaser Part I ext.pdf")
    result = converter.convert(pdf)
    assert "avg_chars_per_page" in result.metadata
    assert isinstance(result.metadata["avg_chars_per_page"], float)
```

## Test Execution

**Run all tests:**
```bash
cd dc-due-diligence
pytest tests
```

**Run specific test file:**
```bash
pytest tests/test_pdf_converter.py
```

**Run specific test class:**
```bash
pytest tests/test_pdf_converter.py::TestPDFConverterBasics
```

**Run specific test with verbose output:**
```bash
pytest tests/test_pdf_converter.py::TestPDFConverterBasics::test_can_handle_pdf -v
```

**Run tests matching a pattern:**
```bash
pytest tests -k "pdf" -v
```

## Import Patterns in Tests

Always import from the package, not from individual modules:

```python
# Correct (as used in test_imports.py)
from converters import BaseConverter, ExtractionResult, ConfidenceLevel

# Also correct - specific submodule imports when testing that specific module
from converters.pdf import PDFConverter, _clean_text, _rows_to_markdown
```

This ensures the `__all__` exports in `converters/__init__.py` are tested as part of normal test execution.
