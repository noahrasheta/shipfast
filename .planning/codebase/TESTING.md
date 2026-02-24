# Testing Patterns

**Analysis Date:** 2026-02-23

## Test Framework

**Runner:**
- `pytest` 8.0.0+ (declared in `dc-due-diligence/pyproject.toml` line 19)
- Config: `dc-due-diligence/pyproject.toml` lines 29-30

**Assertion Library:**
- Built-in `assert` statements - Used throughout all test files
- `pytest.raises()` for exception testing (see `test_imports.py` line 192)
- `capsys` fixture for capturing and testing print output (see `test_status_reporting.py`)

**Run Commands:**
```bash
pytest dc-due-diligence/tests                    # Run all tests
pytest dc-due-diligence/tests -v                 # Verbose output
pytest dc-due-diligence/tests --cov=converters   # Coverage report
pytest dc-due-diligence/tests -k test_pdf        # Run tests matching pattern
pytest dc-due-diligence/tests::test_imports      # Run specific test file
```

## Test File Organization

**Location:**
- Place test files in a `tests/` directory at the same level as the code being tested
- Tests are organized as a separate package alongside source modules (see `dc-due-diligence/tests/`)
- Store an `__init__.py` in the tests directory to make it a package

**Naming:**
- Use `test_<module>.py` pattern: `test_pdf_converter.py`, `test_folder_scanner.py`, `test_excel_converter.py`
- Each test file corresponds to one converter or functional module

**Directory Structure:**
```
dc-due-diligence/
├── converters/
│   ├── __init__.py
│   ├── base.py
│   ├── pdf.py
│   ├── excel.py
│   ├── powerpoint.py
│   ├── word.py
│   ├── vision.py
│   ├── scanner.py
│   ├── pipeline.py
│   └── generate_pdf.py
├── tests/
│   ├── __init__.py
│   ├── test_imports.py
│   ├── test_pdf_converter.py
│   ├── test_excel_converter.py
│   ├── test_powerpoint_converter.py
│   ├── test_word_converter.py
│   ├── test_vision_converter.py
│   ├── test_folder_scanner.py
│   └── test_status_reporting.py
├── agents/
├── skills/
├── templates/
├── pyproject.toml
└── opportunity-example/  (optional real-world test data)
```

## Test Structure

**Suite Organization:**

Use comment headers to organize test files into clear sections. See `test_folder_scanner.py` for reference.

```python
"""Tests for the folder scanner and file type detection."""

from __future__ import annotations

from pathlib import Path

import pytest

from converters.scanner import (
    FileEntry,
    FileType,
    ScanResult,
    _should_skip,
    detect_file_type,
    scan_folder,
)


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

OPPORTUNITY_DIR = Path(__file__).resolve().parent.parent / "opportunity-example"

@pytest.fixture
def converter():
    return PDFConverter(vision_fallback=False)


# ------------------------------------------------------------------
# detect_file_type
# ------------------------------------------------------------------


class TestDetectFileType:
    """Tests for the file type detection function."""

    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("report.pdf", FileType.PDF),
            ("data.xlsx", FileType.XLSX),
        ],
    )
    def test_recognized_extensions(self, filename: str, expected: FileType):
        """All supported extensions are correctly identified."""
        assert detect_file_type(Path(filename)) == expected


# ------------------------------------------------------------------
# scan_folder
# ------------------------------------------------------------------


class TestScanFolder:
    """Tests for the folder scanning function."""

    def test_scan_empty_folder(self, tmp_path: Path):
        """Scanning an empty folder returns an empty plan."""
        result = scan_folder(tmp_path)
        assert result.root == tmp_path
```

**Patterns:**
- Use comment headers with dashes to separate logical sections
- Group tests into classes by functionality: `TestDetectFileType`, `TestScanFolder`, `TestRealPDFs`
- Separate unit tests from integration tests with clear comment sections
- Use descriptive test method names that describe exact behavior: `test_scan_empty_folder`, `test_scan_recursive`, `test_unknown_types_flagged`

## Mocking

**Framework:** `unittest.mock` via pytest (standard library)

**Approach:** Avoid mocking in most cases. Instead, use real files and actual implementations.

**Patterns:**

Use `pytest`'s `tmp_path` fixture for temporary file creation instead of mocking file I/O:

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
- External API calls that would make real network requests (e.g., Anthropic API in `vision.py` - handled via environment variables)
- System-level operations when testing error paths (use `pytest.raises()` instead)

**What NOT to Mock:**
- Converter implementations - test real behavior against real files
- File operations - use `tmp_path` fixture to create actual test files
- Standard library functions unless they have external side effects
- Internal helper functions - test them directly as unit tests
- Classes from converters - instantiate and use them directly

**Example: Testing Missing Files Without Mocking**

```python
def test_pdf_converter_missing_file_marked_as_failure():
    from converters import PDFConverter, ConfidenceLevel

    converter = PDFConverter(vision_fallback=False)
    result = converter.convert(Path("/tmp/nonexistent_abc123.pdf"))
    assert result.success is False
    assert result.confidence == ConfidenceLevel.LOW
    assert result.confidence_reason == "file not found"
    assert result.error is not None
```

## Fixtures and Test Data

**Fixture Pattern:**

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

@pytest.fixture
def sample_result():
    """Create a sample PipelineResult with various file states."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create directories and files here
        yield result
```

**Location:**
- Place module-level constants like `OPPORTUNITY_DIR` at the top of test files
- Define fixtures immediately after constants
- Use `@pytest.fixture` decorator on functions that return test data
- Fixtures receive `tmp_path` parameter automatically provided by pytest for temporary directories
- Use `yield` in fixtures to support cleanup after the test

**Real Data:**
- Store optional example/integration test data in `opportunity-example/` directory alongside tests
- Use `pytest.skip()` when real data is missing so tests don't fail in CI
- Example from `test_pdf_converter.py` line 144:
```python
def _get_pdf(self, name: str) -> Path:
    pdf = OPPORTUNITY_DIR / name
    if not pdf.exists():
        pytest.skip(f"Example PDF not found: {name}")
    return pdf
```

## Coverage

**Requirements:** No enforced coverage target, but maintain reasonable coverage for critical modules.

**View Coverage:**
```bash
cd dc-due-diligence
pytest tests --cov=converters --cov-report=html
# Then open htmlcov/index.html in a browser
```

## Test Types

**Unit Tests:**
- Scope: Test individual functions and methods in isolation
- Examples: Helper functions like `_clean_text()`, `_rows_to_markdown()`, `_should_skip()` (see `test_pdf_converter.py`, `test_folder_scanner.py`)
- Approach: Use fixtures to create input data, call the function, assert the output
- Use parametrized tests with `@pytest.mark.parametrize` for multiple scenarios
- Example from `test_folder_scanner.py` (lines 33-61):
```python
class TestDetectFileType:
    """Tests for the file type detection function."""

    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("report.pdf", FileType.PDF),
            ("report.PDF", FileType.PDF),
            ("data.xlsx", FileType.XLSX),
            ("data.XLSX", FileType.XLSX),
            ("pro_forma.xlsb", FileType.XLSB),
            ("contract.docx", FileType.DOCX),
        ],
    )
    def test_recognized_extensions(self, filename: str, expected: FileType):
        """All supported extensions are correctly identified."""
        assert detect_file_type(Path(filename)) == expected
```

**Integration Tests:**
- Scope: Test multiple components working together
- Examples: Converters processing real documents from `opportunity-example/` (see `test_pdf_converter.py` lines 130-228)
- Approach: Use real files or create temporary test files with actual structure. Verify entire conversion pipeline produces correct output.
- Example from `test_folder_scanner.py` (lines 387-415):
```python
class TestRealWorldStructure:
    """Tests that mimic the structure of a real broker package."""

    def test_mixed_file_types(self, tmp_path: Path):
        """A folder mimicking a real broker package is scanned correctly."""
        (tmp_path / "0a. Datanovax Teaser Part I ext.pdf").write_bytes(b"fake")
        (tmp_path / "0b. Datanovax Teaser part II.pdf").write_bytes(b"fake")
        (tmp_path / "0c. DN Pic.jpg").write_bytes(b"fake")

        result = scan_folder(tmp_path)

        assert len(result.files) == 3
        assert all(e.converter is not None for e in result.files)
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

**Testing Result Objects:**

Always verify properties of returned objects match expected types and values. See `test_imports.py` (lines 48-62):

```python
def test_extraction_result_defaults():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="sample text",
        method="test",
        success=True,
        confidence=ConfidenceLevel.HIGH,
    )
    assert result.page_count == 0
    assert result.is_scanned is False
    assert result.metadata == {}
    assert result.error is None
```

**Testing Properties:**

Test computed properties work correctly. See `test_imports.py` (lines 65-92):

```python
def test_extraction_result_is_reliable_high():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="good text",
        method="pdfplumber",
        success=True,
        confidence=ConfidenceLevel.HIGH,
        confidence_reason="strong text density, 450 avg chars/page",
    )
    assert result.is_reliable is True
    assert result.is_low_confidence is False
```

**Parametrized Tests:**

Use `@pytest.mark.parametrize` to test multiple scenarios with one test function. See `test_folder_scanner.py` (lines 33-61):

```python
@pytest.mark.parametrize(
    "filename, expected",
    [
        ("report.pdf", FileType.PDF),
        ("report.PDF", FileType.PDF),
        ("data.xlsx", FileType.XLSX),
        ("data.XLSX", FileType.XLSX),
        ("pro_forma.xlsb", FileType.XLSB),
        ("pro_forma.XLSB", FileType.XLSB),
    ],
)
def test_recognized_extensions(self, filename: str, expected: FileType):
    assert detect_file_type(Path(filename)) == expected
```

**Conditional Test Skipping:**

Use `pytest.skip()` when test prerequisites aren't available. See `test_pdf_converter.py` (lines 141-145):

```python
def _get_pdf(self, name: str) -> Path:
    pdf = OPPORTUNITY_DIR / name
    if not pdf.exists():
        pytest.skip(f"Example PDF not found: {name}")
    return pdf
```

This allows tests to run in CI without real data while running fully when data is available.

**Testing File Operations:**

Create real files with `tmp_path` fixture instead of mocking. See `test_folder_scanner.py` (lines 101-114):

```python
def test_scan_flat_folder(self, tmp_path: Path):
    """Scanning a folder with files produces entries for each."""
    (tmp_path / "report.pdf").write_bytes(b"%PDF-1.4 fake")
    (tmp_path / "data.xlsx").write_bytes(b"fake xlsx")
    (tmp_path / "photo.jpg").write_bytes(b"\xff\xd8fake")

    result = scan_folder(tmp_path)

    assert len(result.files) == 3
    assert len(result.supported) == 3
    assert len(result.unsupported) == 0
```

**Testing Output Capture:**

Use `capsys` fixture to capture and verify printed output. See `test_status_reporting.py` (lines 135-163):

```python
def test_status_report_verbose(sample_result, capsys):
    """Test verbose status report output."""
    print_status_report(sample_result, verbose=True)
    captured = capsys.readouterr()

    assert "DOCUMENT PROCESSING REPORT" in captured.out
    assert "Total files found: 5" in captured.out
    assert "FAILED CONVERSIONS" in captured.out
    assert "broken.pdf" in captured.out
```

## Import Patterns in Tests

Always import from the package, not from individual modules when possible:

```python
# Preferred (as used in test_imports.py)
from converters import BaseConverter, ExtractionResult, ConfidenceLevel

# Also correct - specific submodule imports when testing that module's internals
from converters.pdf import PDFConverter, _clean_text, _rows_to_markdown

# Avoid
from converters.base import BaseConverter  # Use package import instead
```

This ensures the `__all__` exports in `converters/__init__.py` are tested as part of normal test execution.

## Test Execution Commands

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

**Run specific test method:**
```bash
pytest tests/test_pdf_converter.py::TestPDFConverterBasics::test_can_handle_pdf
```

**Run with verbose output:**
```bash
pytest tests -v
```

**Run tests matching a pattern:**
```bash
pytest tests -k "pdf" -v
```

**Run with coverage:**
```bash
pytest tests --cov=converters --cov-report=term-missing
```

## Test Data Characteristics

**Real World Structure:**

The `opportunity-example/` directory contains realistic broker packages mimicking actual data center due diligence documents. Tests use these files for integration testing when available.

**File Types Covered:**
- PDFs (text-based and scanned)
- Excel spreadsheets (.xlsx and .xlsb)
- Word documents (.docx)
- PowerPoint presentations (.pptx)
- Images (PNG, JPG, TIFF)

**Special Files Handled:**
- Files with special characters: `0a. Datanovax Teaser (Part I) ext.pdf`
- Nested folder structures: `Phase 1 Docs/`, `Phase 2 (Expansion)/`
- Empty sheets in spreadsheets
- Scanned PDFs requiring vision extraction
- Corrupted/encrypted PDFs

---

*Testing analysis: 2026-02-23*
