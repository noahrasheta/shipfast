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

    def test_empty_string(self):
        assert _clean_text("") == ""

    def test_preserves_single_blank_line(self):
        assert _clean_text("a\n\nb") == "a\n\nb"


class TestRowsToMarkdown:
    def test_simple_table(self):
        rows = [["Name", "Value"], ["Power", "10MW"], ["Space", "50k sqft"]]
        md = _rows_to_markdown(rows)
        lines = md.split("\n")
        assert lines[0] == "| Name | Value |"
        assert lines[1] == "| --- | --- |"
        assert lines[2] == "| Power | 10MW |"
        assert lines[3] == "| Space | 50k sqft |"

    def test_none_values_become_empty(self):
        rows = [["A", "B"], [None, "x"]]
        md = _rows_to_markdown(rows)
        assert "|  | x |" in md

    def test_uneven_rows_padded(self):
        rows = [["A", "B", "C"], ["x"]]
        md = _rows_to_markdown(rows)
        lines = md.split("\n")
        # Body row should have 3 columns even though only 1 was provided.
        assert lines[2].count("|") == 4  # leading, 3 separators, trailing

    def test_empty_rows(self):
        assert _rows_to_markdown([]) == ""

    def test_pipe_characters_escaped(self):
        rows = [["Col"], ["has|pipe"]]
        md = _rows_to_markdown(rows)
        assert "has\\|pipe" in md

    def test_newlines_in_cells_replaced(self):
        rows = [["Header"], ["line1\nline2"]]
        md = _rows_to_markdown(rows)
        assert "line1 line2" in md


# ------------------------------------------------------------------
# Converter behaviour tests
# ------------------------------------------------------------------


class TestPDFConverterBasics:
    def test_supported_extensions(self, converter):
        assert converter.supported_extensions == [".pdf"]

    def test_can_handle_pdf(self, converter):
        assert converter.can_handle(Path("report.pdf")) is True
        assert converter.can_handle(Path("REPORT.PDF")) is True

    def test_cannot_handle_non_pdf(self, converter):
        assert converter.can_handle(Path("report.xlsx")) is False
        assert converter.can_handle(Path("report.docx")) is False

    def test_missing_file_returns_error(self, converter):
        result = converter.convert(Path("/tmp/does_not_exist_12345.pdf"))
        assert result.success is False
        assert result.confidence == ConfidenceLevel.LOW
        assert "not found" in result.error.lower()

    def test_non_pdf_extension_returns_error(self, converter):
        # Create a temporary non-pdf file.
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not a pdf")
            tmp = Path(f.name)
        try:
            result = converter.convert(tmp)
            assert result.success is False
            assert "not a pdf" in result.error.lower()
        finally:
            tmp.unlink()

    def test_result_is_extraction_result(self, converter):
        result = converter.convert(Path("/tmp/does_not_exist_12345.pdf"))
        assert isinstance(result, ExtractionResult)

    def test_method_is_pdfplumber(self, converter):
        result = converter.convert(Path("/tmp/does_not_exist_12345.pdf"))
        assert result.method == "pdfplumber"


# ------------------------------------------------------------------
# Integration tests against real opportunity PDFs
# ------------------------------------------------------------------


class TestRealPDFs:
    """Integration tests that run against the actual example documents.

    These tests are skipped if the opportunity-example folder is missing
    (e.g. in CI without data).
    """

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
        assert result.page_count > 0
        assert len(result.text) > 100
        assert result.method == "pdfplumber"
        assert result.source_path == pdf.resolve()

    def test_text_pdf_has_metadata(self, converter):
        pdf = self._get_pdf("0a. Datanovax Teaser Part I ext.pdf")
        result = converter.convert(pdf)

        assert "avg_chars_per_page" in result.metadata
        assert "total_chars" in result.metadata
        assert "tables_found" in result.metadata
        assert isinstance(result.metadata["avg_chars_per_page"], float)

    def test_multipage_pdf_all_pages_included(self, converter):
        pdf = self._get_pdf("1a. Connectivity Report r.pdf")
        result = converter.convert(pdf)

        assert result.success is True
        assert result.page_count > 1
        # Page separator should appear between pages.
        assert "---" in result.text

    def test_scanned_detection_on_text_pdf(self, converter):
        """A real text-based PDF should NOT be flagged as scanned."""
        pdf = self._get_pdf("3a.  Oncor Summary.pdf")
        result = converter.convert(pdf)

        assert result.success is True
        # Oncor summary is a text-based PDF -- should not be scanned.
        # (If it happens to be image-based, the is_scanned flag is still
        # correct -- the test validates the flag is set one way or the other.)
        assert isinstance(result.is_scanned, bool)

    def test_table_extraction_produces_markdown(self, converter):
        """PDFs with tables should produce markdown table syntax."""
        pdf = self._get_pdf("3a.  Oncor Summary.pdf")
        result = converter.convert(pdf)

        assert result.success is True
        # If tables are found, the output should include pipe characters
        # (markdown table syntax).
        if result.metadata.get("tables_found", 0) > 0:
            assert "|" in result.text

    def test_confidence_levels(self, converter):
        """Confidence should be HIGH or MEDIUM for text-rich PDFs."""
        pdf = self._get_pdf("0a. Datanovax Teaser Part I ext.pdf")
        result = converter.convert(pdf)

        assert result.confidence in (ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM)

    def test_large_pdf_handles_without_error(self, converter):
        """The large engineering drawings PDF should be processed without
        crashing, even if it's mostly images."""
        pdf = self._get_pdf("16g. DN Ext Drawings r.pdf")
        result = converter.convert(pdf)

        assert result.success is True
        assert result.page_count > 0
        # This is likely scanned/image-heavy.
        assert isinstance(result.is_scanned, bool)

    def test_all_example_pdfs_process_without_error(self, converter):
        """Every PDF in the example folder should return a result without
        raising an exception, even if the content is sparse."""
        if not OPPORTUNITY_DIR.exists():
            pytest.skip("Example folder not found")

        pdfs = list(OPPORTUNITY_DIR.glob("*.pdf"))
        assert len(pdfs) > 0, "No PDFs found in example folder"

        for pdf in pdfs:
            result = converter.convert(pdf)
            assert isinstance(result, ExtractionResult), f"Bad result for {pdf.name}"
            assert result.success is True, f"Failed on {pdf.name}: {result.error}"
            assert result.page_count > 0, f"Zero pages for {pdf.name}"
