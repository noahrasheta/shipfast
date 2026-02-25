"""Verify that all document processing libraries import successfully."""

from pathlib import Path


def test_docling_import():
    from docling.document_converter import DocumentConverter
    assert DocumentConverter is not None


def test_gliner_import():
    from gliner import GLiNER
    assert GLiNER is not None


def test_pillow_import():
    from PIL import Image
    assert hasattr(Image, "open")


def test_converters_package_import():
    from converters import BaseConverter, ExtractionResult, ConfidenceLevel
    assert ConfidenceLevel.HIGH.value == "high"
    assert ConfidenceLevel.MEDIUM.value == "medium"
    assert ConfidenceLevel.LOW.value == "low"


def test_docling_converter_import():
    from converters import DoclingConverter
    converter = DoclingConverter()
    assert ".pdf" in converter.supported_extensions
    assert ".docx" in converter.supported_extensions
    assert ".xlsx" in converter.supported_extensions
    assert ".pptx" in converter.supported_extensions
    assert ".png" in converter.supported_extensions


def test_redactor_import():
    from converters.redactor import redact_text, redact_file, redact_converted_folder
    assert callable(redact_text)
    assert callable(redact_file)
    assert callable(redact_converted_folder)


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
        method="docling",
        success=True,
        confidence=ConfidenceLevel.HIGH,
        confidence_reason="successful extraction (5000 chars, 3 pages)",
    )
    assert result.is_reliable is True
    assert result.is_low_confidence is False


def test_extraction_result_is_reliable_medium():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="some text",
        method="docling",
        success=True,
        confidence=ConfidenceLevel.MEDIUM,
        confidence_reason="partial conversion",
    )
    assert result.is_reliable is True
    assert result.is_low_confidence is False


def test_extraction_result_is_not_reliable_low():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="x",
        method="docling",
        success=True,
        confidence=ConfidenceLevel.LOW,
        confidence_reason="very little text extracted (5 chars from 3 pages)",
    )
    assert result.is_reliable is False
    assert result.is_low_confidence is True


def test_extraction_result_is_not_reliable_failed():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="",
        method="docling",
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
        method="docling",
        success=True,
        confidence=ConfidenceLevel.HIGH,
        confidence_reason="successful extraction (5000 chars)",
    )
    summary = result.confidence_summary
    assert summary == (
        "high confidence (docling: "
        "successful extraction (5000 chars))"
    )


def test_confidence_summary_failure():
    from converters import ExtractionResult, ConfidenceLevel

    result = ExtractionResult(
        source_path=Path("/tmp/test.pdf"),
        text="",
        method="docling",
        success=False,
        confidence=ConfidenceLevel.LOW,
        confidence_reason="file not found",
        error="File not found: /tmp/test.pdf",
    )
    summary = result.confidence_summary
    assert summary == (
        "extraction failed (docling: File not found: /tmp/test.pdf)"
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


def test_docling_converter_missing_file_marked_as_failure():
    from converters import DoclingConverter, ConfidenceLevel

    converter = DoclingConverter()
    result = converter.convert(Path("/tmp/nonexistent_abc123.pdf"))
    assert result.success is False
    assert result.confidence == ConfidenceLevel.LOW
    assert result.confidence_reason == "file not found"
    assert result.error is not None
    assert result.is_reliable is False
    assert "extraction failed" in result.confidence_summary


def test_docling_converter_unsupported_type_marked_as_failure(tmp_path):
    from converters import DoclingConverter, ConfidenceLevel

    # Create a real file with an unsupported extension.
    xyz_file = tmp_path / "test.xyz"
    xyz_file.write_text("unknown format")

    converter = DoclingConverter()
    result = converter.convert(xyz_file)
    assert result.success is False
    assert result.confidence == ConfidenceLevel.LOW
    assert result.confidence_reason == "unsupported file type"
    assert result.is_reliable is False
