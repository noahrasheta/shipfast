"""Tests for vision-based text extraction (scanned PDFs and images)."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import io
import tempfile

import pytest
from PIL import Image

from converters import ConfidenceLevel, ExtractionResult, VisionConverter
from converters.vision import (
    _image_to_base64_jpeg,
    _pdf_page_to_image,
    _get_pdf_page_count,
    _MAX_IMAGE_DIMENSION,
)


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

OPPORTUNITY_DIR = Path(__file__).resolve().parent.parent / "opportunity-example"


@pytest.fixture
def converter():
    return VisionConverter(api_key="test-key")


def _make_test_image(width: int = 100, height: int = 80, color: str = "red") -> Image.Image:
    """Create a small test image in memory."""
    return Image.new("RGB", (width, height), color)


def _make_test_image_file(
    suffix: str = ".png", width: int = 100, height: int = 80
) -> Path:
    """Create a temporary image file and return its path."""
    img = _make_test_image(width, height)
    tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    img.save(tmp.name)
    tmp.close()
    return Path(tmp.name)


def _mock_anthropic_response(text: str) -> MagicMock:
    """Build a mock that mimics anthropic.types.Message."""
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


# ------------------------------------------------------------------
# Helper function tests
# ------------------------------------------------------------------


class TestImageToBase64:
    def test_returns_string(self):
        img = _make_test_image()
        result = _image_to_base64_jpeg(img)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_small_image_not_resized(self):
        img = _make_test_image(50, 50)
        b64 = _image_to_base64_jpeg(img)
        # Should produce valid base64.
        import base64
        decoded = base64.standard_b64decode(b64)
        assert len(decoded) > 0

    def test_large_image_resized(self):
        img = _make_test_image(4000, 3000)
        b64 = _image_to_base64_jpeg(img)
        # Decode and check the resulting image dimensions.
        import base64
        decoded = base64.standard_b64decode(b64)
        result_img = Image.open(io.BytesIO(decoded))
        assert result_img.width <= _MAX_IMAGE_DIMENSION
        assert result_img.height <= _MAX_IMAGE_DIMENSION

    def test_rgba_image_handled(self):
        img = Image.new("RGBA", (100, 100), (255, 0, 0, 128))
        b64 = _image_to_base64_jpeg(img)
        assert isinstance(b64, str)
        assert len(b64) > 0

    def test_palette_image_handled(self):
        img = Image.new("P", (100, 100))
        b64 = _image_to_base64_jpeg(img)
        assert isinstance(b64, str)
        assert len(b64) > 0


# ------------------------------------------------------------------
# VisionConverter basics
# ------------------------------------------------------------------


class TestVisionConverterBasics:
    def test_supported_extensions(self, converter):
        assert ".pdf" in converter.supported_extensions
        assert ".png" in converter.supported_extensions
        assert ".jpg" in converter.supported_extensions
        assert ".jpeg" in converter.supported_extensions
        assert ".tiff" in converter.supported_extensions
        assert ".tif" in converter.supported_extensions
        assert ".bmp" in converter.supported_extensions
        assert ".webp" in converter.supported_extensions

    def test_can_handle_images(self, converter):
        assert converter.can_handle(Path("scan.png")) is True
        assert converter.can_handle(Path("photo.JPG")) is True
        assert converter.can_handle(Path("page.tiff")) is True
        assert converter.can_handle(Path("doc.pdf")) is True

    def test_cannot_handle_non_image(self, converter):
        assert converter.can_handle(Path("data.xlsx")) is False
        assert converter.can_handle(Path("report.docx")) is False

    def test_missing_file_returns_error(self, converter):
        result = converter.convert(Path("/tmp/nonexistent_image_12345.png"))
        assert result.success is False
        assert result.method == "claude_vision"
        assert "not found" in result.error.lower()

    def test_unsupported_extension_returns_error(self, converter):
        tmp = tempfile.NamedTemporaryFile(suffix=".xyz", delete=False)
        tmp.write(b"data")
        tmp.close()
        try:
            result = converter.convert(Path(tmp.name))
            assert result.success is False
            assert "unsupported" in result.error.lower()
        finally:
            Path(tmp.name).unlink()


# ------------------------------------------------------------------
# Image extraction with mocked API
# ------------------------------------------------------------------


class TestImageExtraction:
    @patch("converters.vision.VisionConverter._get_client")
    def test_image_extraction_success(self, mock_get_client, converter):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_anthropic_response(
            "Extracted text from the image."
        )
        mock_get_client.return_value = mock_client

        img_path = _make_test_image_file(".png")
        try:
            result = converter.convert(img_path)

            assert result.success is True
            assert result.method == "claude_vision"
            assert "Extracted text from the image." in result.text
            assert result.page_count == 1
            assert result.is_scanned is False
            assert result.confidence in (
                ConfidenceLevel.HIGH,
                ConfidenceLevel.MEDIUM,
            )
            assert "vision_model" in result.metadata
            assert "total_chars" in result.metadata
            assert "image_size" in result.metadata
        finally:
            img_path.unlink()

    @patch("converters.vision.VisionConverter._get_client")
    def test_image_extraction_empty_response(self, mock_get_client, converter):
        mock_client = MagicMock()
        # Return a response with no text content.
        empty_response = MagicMock()
        empty_response.content = []
        mock_client.messages.create.return_value = empty_response
        mock_get_client.return_value = mock_client

        img_path = _make_test_image_file(".jpg")
        try:
            result = converter.convert(img_path)
            assert result.success is False
            assert "no text" in result.error.lower()
        finally:
            img_path.unlink()

    @patch("converters.vision.VisionConverter._get_client")
    def test_jpeg_file_handled(self, mock_get_client, converter):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_anthropic_response("JPEG text")
        mock_get_client.return_value = mock_client

        img_path = _make_test_image_file(".jpeg")
        try:
            result = converter.convert(img_path)
            assert result.success is True
            assert result.text == "JPEG text"
        finally:
            img_path.unlink()

    @patch("converters.vision.VisionConverter._get_client")
    def test_tiff_file_handled(self, mock_get_client, converter):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_anthropic_response("TIFF text")
        mock_get_client.return_value = mock_client

        img_path = _make_test_image_file(".tiff")
        try:
            result = converter.convert(img_path)
            assert result.success is True
            assert result.text == "TIFF text"
        finally:
            img_path.unlink()

    @patch("converters.vision.VisionConverter._get_client")
    def test_low_confidence_for_little_text(self, mock_get_client, converter):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_anthropic_response("OK")
        mock_get_client.return_value = mock_client

        img_path = _make_test_image_file(".png")
        try:
            result = converter.convert(img_path)
            assert result.success is True
            # Only 2 chars -- should be LOW confidence.
            assert result.confidence == ConfidenceLevel.LOW
        finally:
            img_path.unlink()


# ------------------------------------------------------------------
# Scanned PDF extraction with mocked API
# ------------------------------------------------------------------


class TestScannedPDFExtraction:
    def _make_simple_pdf(self) -> Path:
        """Create a minimal 2-page PDF for testing via pypdfium2."""
        # Use reportlab-free approach: create a PDF with pypdfium2/pdfplumber
        # by writing raw PDF bytes.
        pdf_content = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R 6 0 R]/Count 2>>endobj\n"
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
            b"/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
            b"4 0 obj<</Length 0>>stream\nendstream\nendobj\n"
            b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
            b"6 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
            b"/Contents 7 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
            b"7 0 obj<</Length 0>>stream\nendstream\nendobj\n"
            b"xref\n0 8\n"
            b"0000000000 65535 f \n"
            b"0000000009 00000 n \n"
            b"0000000058 00000 n \n"
            b"0000000115 00000 n \n"
            b"0000000266 00000 n \n"
            b"0000000315 00000 n \n"
            b"0000000392 00000 n \n"
            b"0000000543 00000 n \n"
            b"trailer<</Size 8/Root 1 0 R>>\nstartxref\n592\n%%EOF"
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.write(pdf_content)
        tmp.close()
        return Path(tmp.name)

    @patch("converters.vision.VisionConverter._get_client")
    def test_scanned_pdf_processes_each_page(self, mock_get_client, converter):
        mock_client = MagicMock()
        call_count = 0

        def side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            return _mock_anthropic_response(f"Page {call_count} content here")

        mock_client.messages.create.side_effect = side_effect
        mock_get_client.return_value = mock_client

        pdf_path = self._make_simple_pdf()
        try:
            result = converter.convert(pdf_path)
            assert result.success is True
            assert result.method == "claude_vision"
            assert result.is_scanned is True
            assert result.page_count == 2
            # Both pages should be in the output, separated by ---
            assert "Page 1 content here" in result.text
            assert "Page 2 content here" in result.text
            assert "---" in result.text
            assert call_count == 2
        finally:
            pdf_path.unlink()

    @patch("converters.vision.VisionConverter._get_client")
    def test_scanned_pdf_metadata(self, mock_get_client, converter):
        mock_client = MagicMock()
        mock_client.messages.create.return_value = _mock_anthropic_response(
            "Some extracted text from scanned page"
        )
        mock_get_client.return_value = mock_client

        pdf_path = self._make_simple_pdf()
        try:
            result = converter.convert(pdf_path)
            assert "avg_chars_per_page" in result.metadata
            assert "total_chars" in result.metadata
            assert "pages_failed" in result.metadata
            assert "vision_model" in result.metadata
            assert result.metadata["pages_failed"] == []
        finally:
            pdf_path.unlink()

    @patch("converters.vision.VisionConverter._get_client")
    def test_scanned_pdf_partial_failure(self, mock_get_client, converter):
        """If some pages fail, the result should still succeed with reduced confidence."""
        mock_client = MagicMock()
        call_count = 0

        def side_effect(**kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _mock_anthropic_response("Good page text here")
            else:
                # Return empty response to simulate failure.
                empty = MagicMock()
                empty.content = []
                return empty

        mock_client.messages.create.side_effect = side_effect
        mock_get_client.return_value = mock_client

        pdf_path = self._make_simple_pdf()
        try:
            result = converter.convert(pdf_path)
            assert result.success is True
            assert 1 in result.metadata["pages_failed"] or 2 in result.metadata["pages_failed"]
            # With 1 of 2 pages failed (50%), confidence should be LOW.
            assert result.confidence == ConfidenceLevel.LOW
        finally:
            pdf_path.unlink()


# ------------------------------------------------------------------
# PDFConverter vision fallback integration
# ------------------------------------------------------------------


class TestPDFConverterVisionFallback:
    """Verify that PDFConverter routes scanned PDFs to VisionConverter."""

    @patch("converters.vision.VisionConverter.convert")
    def test_scanned_pdf_triggers_vision_fallback(self, mock_vision_convert):
        """When a PDF is detected as scanned, PDFConverter should delegate
        to VisionConverter."""
        from converters.pdf import PDFConverter

        # Create a minimal blank PDF (no text) that pdfplumber will flag as scanned.
        pdf_content = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
            b"/Contents 4 0 R/Resources<<>>>>endobj\n"
            b"4 0 obj<</Length 0>>stream\nendstream\nendobj\n"
            b"xref\n0 5\n"
            b"0000000000 65535 f \n"
            b"0000000009 00000 n \n"
            b"0000000058 00000 n \n"
            b"0000000107 00000 n \n"
            b"0000000232 00000 n \n"
            b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n281\n%%EOF"
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.write(pdf_content)
        tmp.close()
        pdf_path = Path(tmp.name)

        mock_vision_convert.return_value = ExtractionResult(
            source_path=pdf_path,
            text="Vision extracted text",
            method="claude_vision",
            success=True,
            confidence=ConfidenceLevel.HIGH,
            page_count=1,
            is_scanned=True,
        )

        try:
            converter = PDFConverter(vision_fallback=True, api_key="test-key")
            result = converter.convert(pdf_path)

            # Should have delegated to vision.
            assert mock_vision_convert.called
            assert result.method == "claude_vision"
            assert result.text == "Vision extracted text"
        finally:
            pdf_path.unlink()

    def test_vision_fallback_disabled(self):
        """When vision_fallback is False, scanned PDFs should NOT be routed."""
        from converters.pdf import PDFConverter

        pdf_content = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
            b"/Contents 4 0 R/Resources<<>>>>endobj\n"
            b"4 0 obj<</Length 0>>stream\nendstream\nendobj\n"
            b"xref\n0 5\n"
            b"0000000000 65535 f \n"
            b"0000000009 00000 n \n"
            b"0000000058 00000 n \n"
            b"0000000107 00000 n \n"
            b"0000000232 00000 n \n"
            b"trailer<</Size 5/Root 1 0 R>>\nstartxref\n281\n%%EOF"
        )
        tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        tmp.write(pdf_content)
        tmp.close()
        pdf_path = Path(tmp.name)

        try:
            converter = PDFConverter(vision_fallback=False)
            result = converter.convert(pdf_path)

            # Should have stayed with pdfplumber -- no vision fallback.
            assert result.method == "pdfplumber"
            assert result.is_scanned is True
        finally:
            pdf_path.unlink()


# ------------------------------------------------------------------
# API error handling
# ------------------------------------------------------------------


class TestAPIErrorHandling:
    @patch("converters.vision.VisionConverter._get_client")
    def test_authentication_error(self, mock_get_client, converter):
        import anthropic

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = anthropic.AuthenticationError(
            message="Invalid API key",
            response=MagicMock(status_code=401),
            body={"error": {"type": "authentication_error", "message": "Invalid API key"}},
        )
        mock_get_client.return_value = mock_client

        img_path = _make_test_image_file(".png")
        try:
            result = converter.convert(img_path)
            assert result.success is False
            assert "authentication" in result.error.lower()
        finally:
            img_path.unlink()

    @patch("converters.vision.VisionConverter._get_client")
    def test_generic_api_error(self, mock_get_client, converter):
        import anthropic

        mock_client = MagicMock()
        mock_client.messages.create.side_effect = anthropic.APIError(
            message="Server error",
            request=MagicMock(),
            body=None,
        )
        mock_get_client.return_value = mock_client

        img_path = _make_test_image_file(".png")
        try:
            result = converter.convert(img_path)
            assert result.success is False
            assert "api error" in result.error.lower()
        finally:
            img_path.unlink()


# ------------------------------------------------------------------
# Integration tests against real files (skipped if data missing)
# ------------------------------------------------------------------


class TestRealFiles:
    """Integration tests that use actual example documents.

    These are skipped if the opportunity-example folder or ANTHROPIC_API_KEY
    is not available.
    """

    @pytest.fixture
    def real_converter(self):
        import os
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")
        return VisionConverter()

    def _get_file(self, name: str) -> Path:
        f = OPPORTUNITY_DIR / name
        if not f.exists():
            pytest.skip(f"Example file not found: {name}")
        return f

    def test_scanned_pdf_via_vision(self, real_converter):
        """A known scanned/image-heavy PDF should produce text via vision."""
        # The engineering drawings PDF is mostly images.
        pdf = self._get_file("16g. DN Ext Drawings r.pdf")
        result = real_converter.convert(pdf)

        assert result.success is True
        assert result.method == "claude_vision"
        assert result.page_count > 0
        assert len(result.text) > 0
