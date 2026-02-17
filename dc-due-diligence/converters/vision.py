"""
Vision-based text extraction using Claude's vision API.

Handles scanned/image-based PDFs and standalone image files (PNG, JPG, TIFF)
by sending each page or image to Claude vision for text extraction.  When the
PDF text converter detects a scanned document (low text-to-page ratio), the
pipeline routes the file here instead.
"""

from __future__ import annotations

import base64
import io
import os
from pathlib import Path
from typing import Any

import anthropic
import pypdfium2
from PIL import Image

from converters.base import BaseConverter, ConfidenceLevel, ExtractionResult

# Maximum dimension (width or height) for images sent to Claude vision.
# Keeps token costs and latency manageable without losing detail.
_MAX_IMAGE_DIMENSION = 2048

# JPEG quality for compressed images sent to the API.
_JPEG_QUALITY = 85

# Claude model to use for vision extraction.
_VISION_MODEL = "claude-sonnet-4-20250514"

# Maximum tokens per vision request (single page).
_MAX_TOKENS_PER_PAGE = 4096

# The prompt sent along with each page image.
_EXTRACTION_PROMPT = (
    "Extract all text from this image exactly as it appears. "
    "Preserve the original structure including headings, paragraphs, lists, "
    "and tables. Format tables as markdown tables. "
    "If there are handwritten annotations, include them in [brackets]. "
    "If any text is unclear or illegible, mark it as [illegible]. "
    "Return only the extracted text with no commentary."
)


def _image_to_base64_jpeg(img: Image.Image) -> str:
    """Resize an image if needed and return a base64-encoded JPEG string."""
    width, height = img.size

    # Resize if either dimension exceeds the limit.
    if width > _MAX_IMAGE_DIMENSION or height > _MAX_IMAGE_DIMENSION:
        scale = _MAX_IMAGE_DIMENSION / max(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img = img.resize((new_width, new_height), Image.LANCZOS)

    # Convert to RGB if necessary (handles RGBA, palette, etc.)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=_JPEG_QUALITY)
    return base64.standard_b64encode(buf.getvalue()).decode("ascii")


def _pdf_page_to_image(pdf_path: Path, page_index: int) -> Image.Image:
    """Render a single PDF page to a PIL Image using pypdfium2."""
    doc = pypdfium2.PdfDocument(str(pdf_path))
    try:
        page = doc[page_index]
        # Render at 200 DPI -- good balance of quality vs. size.
        bitmap = page.render(scale=200 / 72)
        pil_image = bitmap.to_pil()
        return pil_image
    finally:
        doc.close()


def _get_pdf_page_count(pdf_path: Path) -> int:
    """Return the number of pages in a PDF."""
    doc = pypdfium2.PdfDocument(str(pdf_path))
    try:
        return len(doc)
    finally:
        doc.close()


class VisionConverter(BaseConverter):
    """Extract text from scanned PDFs and images using Claude's vision API.

    For PDFs, each page is rendered to an image and sent individually to avoid
    token limits.  For standalone images, the file is sent directly.

    Requires the ``ANTHROPIC_API_KEY`` environment variable to be set.
    """

    supported_extensions: list[str] = [
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".tiff",
        ".tif",
        ".bmp",
        ".webp",
    ]

    def __init__(self, api_key: str | None = None):
        """Initialize with an optional API key.

        If *api_key* is not provided, the ``ANTHROPIC_API_KEY`` environment
        variable is used (via the anthropic SDK default).
        """
        self._api_key = api_key

    def _get_client(self) -> anthropic.Anthropic:
        """Create an Anthropic client, using the stored key or env default."""
        if self._api_key:
            return anthropic.Anthropic(api_key=self._api_key)
        return anthropic.Anthropic()

    def convert(self, path: Path) -> ExtractionResult:
        """Extract text from a scanned PDF or image file via Claude vision."""
        path = Path(path).resolve()

        if not path.exists():
            return ExtractionResult(
                source_path=path,
                text="",
                method="claude_vision",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="file not found",
                error=f"File not found: {path}",
            )

        suffix = path.suffix.lower()
        if suffix not in self.supported_extensions:
            return ExtractionResult(
                source_path=path,
                text="",
                method="claude_vision",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="unsupported file type",
                error=f"Unsupported file type: {suffix}",
            )

        try:
            if suffix == ".pdf":
                return self._extract_scanned_pdf(path)
            else:
                return self._extract_image(path)
        except anthropic.AuthenticationError as exc:
            return ExtractionResult(
                source_path=path,
                text="",
                method="claude_vision",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="API authentication failed",
                error=f"Authentication failed: {exc}",
            )
        except anthropic.APIError as exc:
            return ExtractionResult(
                source_path=path,
                text="",
                method="claude_vision",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="API request failed",
                error=f"API error: {exc}",
            )
        except Exception as exc:
            return ExtractionResult(
                source_path=path,
                text="",
                method="claude_vision",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="unexpected extraction failure",
                error=f"Vision extraction failed: {exc}",
            )

    # ------------------------------------------------------------------
    # Scanned PDF handling
    # ------------------------------------------------------------------

    def _extract_scanned_pdf(self, path: Path) -> ExtractionResult:
        """Render each page of a scanned PDF to an image and extract text."""
        page_count = _get_pdf_page_count(path)

        if page_count == 0:
            return ExtractionResult(
                source_path=path,
                text="",
                method="claude_vision",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="PDF has no pages",
                error="PDF has no pages",
            )

        page_texts: list[str] = []
        pages_failed: list[int] = []

        client = self._get_client()

        for i in range(page_count):
            page_image = _pdf_page_to_image(path, i)
            b64_jpeg = _image_to_base64_jpeg(page_image)

            page_text = self._call_vision_api(client, b64_jpeg, page_num=i + 1)
            if page_text is not None:
                page_texts.append(page_text)
            else:
                pages_failed.append(i + 1)
                page_texts.append(f"[Page {i + 1}: extraction failed]")

        combined_text = "\n\n---\n\n".join(page_texts)

        total_chars = sum(len(t) for t in page_texts)
        avg_chars = total_chars / max(page_count, 1)

        # Confidence is based on how many pages succeeded.
        failed_count = len(pages_failed)
        failed_ratio = failed_count / page_count
        if failed_ratio == 0:
            confidence = ConfidenceLevel.HIGH
            confidence_reason = (
                f"all {page_count} pages extracted successfully"
            )
        elif failed_ratio < 0.3:
            confidence = ConfidenceLevel.MEDIUM
            confidence_reason = (
                f"{failed_count} of {page_count} pages failed extraction"
            )
        else:
            confidence = ConfidenceLevel.LOW
            confidence_reason = (
                f"{failed_count} of {page_count} pages failed extraction"
            )

        # If all pages failed, mark the entire extraction as a failure.
        all_failed = failed_count == page_count
        if all_failed:
            confidence_reason = "all pages failed vision extraction"

        metadata: dict[str, Any] = {
            "avg_chars_per_page": round(avg_chars, 1),
            "total_chars": total_chars,
            "pages_failed": pages_failed,
            "vision_model": _VISION_MODEL,
        }

        return ExtractionResult(
            source_path=path,
            text=combined_text,
            method="claude_vision",
            success=not all_failed,
            confidence=confidence,
            confidence_reason=confidence_reason,
            page_count=page_count,
            is_scanned=True,
            metadata=metadata,
            error="All pages failed vision extraction" if all_failed else None,
        )

    # ------------------------------------------------------------------
    # Standalone image handling
    # ------------------------------------------------------------------

    def _extract_image(self, path: Path) -> ExtractionResult:
        """Extract text from a standalone image file."""
        img = Image.open(path)
        b64_jpeg = _image_to_base64_jpeg(img)

        client = self._get_client()
        extracted = self._call_vision_api(client, b64_jpeg)

        if extracted is None:
            return ExtractionResult(
                source_path=path,
                text="",
                method="claude_vision",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="vision API returned no text",
                error="Vision API returned no text",
            )

        total_chars = len(extracted)

        # For images, confidence depends on how much text was found.
        if total_chars > 100:
            confidence = ConfidenceLevel.HIGH
            confidence_reason = f"extracted {total_chars} characters"
        elif total_chars > 20:
            confidence = ConfidenceLevel.MEDIUM
            confidence_reason = f"only {total_chars} characters extracted"
        else:
            confidence = ConfidenceLevel.LOW
            confidence_reason = (
                f"very little text found ({total_chars} characters)"
            )

        metadata: dict[str, Any] = {
            "total_chars": total_chars,
            "image_size": list(img.size),
            "vision_model": _VISION_MODEL,
        }

        return ExtractionResult(
            source_path=path,
            text=extracted,
            method="claude_vision",
            success=True,
            confidence=confidence,
            confidence_reason=confidence_reason,
            page_count=1,
            is_scanned=False,
            metadata=metadata,
        )

    # ------------------------------------------------------------------
    # Claude vision API call
    # ------------------------------------------------------------------

    def _call_vision_api(
        self,
        client: anthropic.Anthropic,
        b64_image: str,
        page_num: int | None = None,
    ) -> str | None:
        """Send a single image to Claude vision and return the extracted text.

        Returns None if the API call fails or returns empty content.
        """
        system_msg = "You are a document text extraction assistant."
        if page_num is not None:
            user_text = f"This is page {page_num}. {_EXTRACTION_PROMPT}"
        else:
            user_text = _EXTRACTION_PROMPT

        response = client.messages.create(
            model=_VISION_MODEL,
            max_tokens=_MAX_TOKENS_PER_PAGE,
            system=system_msg,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": b64_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": user_text,
                        },
                    ],
                }
            ],
        )

        # Extract text from the response content blocks.
        text_parts: list[str] = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)

        result = "\n".join(text_parts).strip()
        return result if result else None
