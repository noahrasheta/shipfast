"""Verify that all document processing libraries import successfully."""

from pathlib import Path


def test_pdfplumber_import():
    import pdfplumber
    assert hasattr(pdfplumber, "open")


def test_openpyxl_import():
    import openpyxl
    assert hasattr(openpyxl, "load_workbook")


def test_pyxlsb_import():
    import pyxlsb
    assert hasattr(pyxlsb, "open_workbook")


def test_python_docx_import():
    import docx
    assert hasattr(docx, "Document")


def test_python_pptx_import():
    import pptx
    assert hasattr(pptx, "Presentation")


def test_pillow_import():
    from PIL import Image
    assert hasattr(Image, "open")


def test_anthropic_import():
    import anthropic
    assert hasattr(anthropic, "Anthropic")


def test_converters_package_import():
    from converters import BaseConverter, ExtractionResult, ConfidenceLevel
    assert ConfidenceLevel.HIGH.value == "high"
    assert ConfidenceLevel.MEDIUM.value == "medium"
    assert ConfidenceLevel.LOW.value == "low"


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
    assert result.confidence_reason == ""


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


def test_extraction_result_is_reliable_medium():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="some text",
        method="pdfplumber",
        success=True,
        confidence=ConfidenceLevel.MEDIUM,
        confidence_reason="low text density, 120 avg chars/page",
    )
    assert result.is_reliable is True
    assert result.is_low_confidence is False


def test_extraction_result_is_not_reliable_low():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="x",
        method="claude_vision",
        success=True,
        confidence=ConfidenceLevel.LOW,
        confidence_reason="very little text found (5 characters)",
    )
    assert result.is_reliable is False
    assert result.is_low_confidence is True


def test_extraction_result_is_not_reliable_failed():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="",
        method="pdfplumber",
        success=False,
        confidence=ConfidenceLevel.LOW,
        confidence_reason="file not found",
        error="File not found: /tmp/test.pdf",
    )
    assert result.is_reliable is False
    assert result.is_low_confidence is True


def test_confidence_summary_success():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="good text",
        method="pdfplumber",
        success=True,
        confidence=ConfidenceLevel.HIGH,
        confidence_reason="strong text density, 450 avg chars/page",
    )
    summary = result.confidence_summary
    assert summary == (
        "high confidence (pdfplumber: "
        "strong text density, 450 avg chars/page)"
    )


def test_confidence_summary_failure():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="",
        method="pdfplumber",
        success=False,
        confidence=ConfidenceLevel.LOW,
        confidence_reason="file not found",
        error="File not found: /tmp/test.pdf",
    )
    summary = result.confidence_summary
    assert summary == (
        "extraction failed (pdfplumber: File not found: /tmp/test.pdf)"
    )


def test_confidence_summary_no_reason_falls_back_to_level():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="some text",
        method="test_method",
        success=True,
        confidence=ConfidenceLevel.MEDIUM,
    )
    assert result.confidence_summary == "medium confidence (test_method: medium)"


def test_base_converter_can_handle():
    from converters import BaseConverter

    class FakeConverter(BaseConverter):
        supported_extensions = [".pdf"]

    converter = FakeConverter()
    assert converter.can_handle(Path("report.pdf")) is True
    assert converter.can_handle(Path("report.PDF")) is True
    assert converter.can_handle(Path("report.xlsx")) is False


def test_base_converter_requires_override():
    from converters import BaseConverter
    import pytest

    converter = BaseConverter()
    with pytest.raises(NotImplementedError):
        converter.convert(Path("/tmp/test.pdf"))


def test_pdf_converter_missing_file_marked_as_failure():
    from converters import PDFConverter, ConfidenceLevel

    converter = PDFConverter(vision_fallback=False)
    result = converter.convert(Path("/tmp/nonexistent_abc123.pdf"))
    assert result.success is False
    assert result.confidence == ConfidenceLevel.LOW
    assert result.confidence_reason == "file not found"
    assert result.error is not None
    assert result.is_reliable is False
    assert "extraction failed" in result.confidence_summary


def test_pdf_converter_wrong_extension_marked_as_failure(tmp_path):
    from converters import PDFConverter, ConfidenceLevel

    # Create a real file with the wrong extension so the file-not-found
    # check passes and the extension check fires.
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("not a pdf")

    converter = PDFConverter(vision_fallback=False)
    result = converter.convert(txt_file)
    assert result.success is False
    assert result.confidence == ConfidenceLevel.LOW
    assert result.confidence_reason == "unsupported file type"
    assert result.is_reliable is False


def test_vision_converter_missing_file_marked_as_failure():
    from converters import VisionConverter, ConfidenceLevel

    converter = VisionConverter()
    result = converter.convert(Path("/tmp/nonexistent_abc123.png"))
    assert result.success is False
    assert result.confidence == ConfidenceLevel.LOW
    assert result.confidence_reason == "file not found"
    assert result.error is not None
    assert result.is_reliable is False


def test_vision_converter_unsupported_type_marked_as_failure(tmp_path):
    from converters import VisionConverter, ConfidenceLevel

    # Create a real file with an unsupported extension.
    xyz_file = tmp_path / "test.xyz"
    xyz_file.write_text("unknown format")

    converter = VisionConverter()
    result = converter.convert(xyz_file)
    assert result.success is False
    assert result.confidence == ConfidenceLevel.LOW
    assert result.confidence_reason == "unsupported file type"
    assert result.is_reliable is False
