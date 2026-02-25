"""
Unified document conversion using Docling.

Replaces the previous per-format converters (PDFConverter, ExcelConverter,
WordConverter, PowerPointConverter, VisionConverter) with a single Docling-based
converter that handles all supported formats entirely offline -- no API calls,
no cloud services.

OCR for scanned PDFs and images runs locally via Apple Vision (macOS) or
RapidOCR (cross-platform).  Table extraction uses Docling's TableFormer model.
"""

from __future__ import annotations

import logging
import platform
from pathlib import Path
from typing import Any

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TableFormerMode,
    TableStructureOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

from converters.base import BaseConverter, ConfidenceLevel, ExtractionResult

logger = logging.getLogger(__name__)

# Map file extensions to Docling InputFormat values.
_EXTENSION_TO_FORMAT: dict[str, InputFormat] = {
    ".pdf": InputFormat.PDF,
    ".docx": InputFormat.DOCX,
    ".dotx": InputFormat.DOCX,
    ".xlsx": InputFormat.XLSX,
    ".xlsm": InputFormat.XLSX,
    ".pptx": InputFormat.PPTX,
    ".potx": InputFormat.PPTX,
    ".ppsx": InputFormat.PPTX,
    ".csv": InputFormat.CSV,
    ".html": InputFormat.HTML,
    ".htm": InputFormat.HTML,
    ".png": InputFormat.IMAGE,
    ".jpg": InputFormat.IMAGE,
    ".jpeg": InputFormat.IMAGE,
    ".tiff": InputFormat.IMAGE,
    ".tif": InputFormat.IMAGE,
    ".bmp": InputFormat.IMAGE,
    ".webp": InputFormat.IMAGE,
}


def _build_pdf_pipeline_options() -> PdfPipelineOptions:
    """Build PDF pipeline options with local-only OCR and table extraction."""
    opts = PdfPipelineOptions()
    opts.do_ocr = True
    opts.do_table_structure = True
    opts.enable_remote_services = False

    # Table extraction: accurate mode for financial/spec documents.
    opts.table_structure_options = TableStructureOptions(
        do_cell_matching=True,
        mode=TableFormerMode.ACCURATE,
    )

    # OCR: prefer macOS Vision on Apple Silicon, fall back to RapidOCR.
    if platform.system() == "Darwin":
        try:
            from docling.datamodel.pipeline_options import OcrMacOptions

            opts.ocr_options = OcrMacOptions(
                lang=["en-US"],
                recognition="accurate",
            )
            logger.info("OCR engine: OcrMac (macOS Vision framework)")
        except ImportError:
            _set_rapidocr(opts)
    else:
        _set_rapidocr(opts)

    return opts


def _set_rapidocr(opts: PdfPipelineOptions) -> None:
    """Configure RapidOCR as the OCR engine."""
    from docling.datamodel.pipeline_options import RapidOcrOptions

    opts.ocr_options = RapidOcrOptions(lang=["english"])
    logger.info("OCR engine: RapidOCR")


def _build_converter() -> DocumentConverter:
    """Create a DocumentConverter configured for offline-only operation."""
    pdf_options = _build_pdf_pipeline_options()

    return DocumentConverter(
        allowed_formats=[
            InputFormat.PDF,
            InputFormat.DOCX,
            InputFormat.PPTX,
            InputFormat.XLSX,
            InputFormat.CSV,
            InputFormat.HTML,
            InputFormat.IMAGE,
        ],
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options),
        },
    )


# Module-level singleton -- reused across calls to avoid re-loading models.
_converter: DocumentConverter | None = None


def _get_converter() -> DocumentConverter:
    """Return (and lazily create) the module-level DocumentConverter."""
    global _converter
    if _converter is None:
        logger.info("Initializing Docling converter (first call, loading models)...")
        _converter = _build_converter()
        logger.info("Docling converter ready.")
    return _converter


class DoclingConverter(BaseConverter):
    """Convert any supported document format to markdown using Docling.

    All processing happens locally -- no API calls, no cloud services.
    Scanned PDFs and images are OCR'd using local engines (Apple Vision
    on macOS, RapidOCR elsewhere).
    """

    supported_extensions: list[str] = list(_EXTENSION_TO_FORMAT.keys())

    def convert(self, path: Path) -> ExtractionResult:
        """Convert a document to markdown text via Docling."""
        path = Path(path).resolve()

        if not path.exists():
            return ExtractionResult(
                source_path=path,
                text="",
                method="docling",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="file not found",
                error=f"File not found: {path}",
            )

        suffix = path.suffix.lower()
        if suffix not in _EXTENSION_TO_FORMAT:
            return ExtractionResult(
                source_path=path,
                text="",
                method="docling",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="unsupported file type",
                error=f"Unsupported file type: {suffix}",
            )

        converter = _get_converter()

        try:
            result = converter.convert(
                source=path,
                raises_on_error=False,
            )
        except Exception as exc:
            logger.error("Docling conversion crashed for %s: %s", path, exc)
            return ExtractionResult(
                source_path=path,
                text="",
                method="docling",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="converter crashed",
                error=f"Docling conversion failed: {exc}",
            )

        return self._to_extraction_result(path, result)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _to_extraction_result(
        self, path: Path, result: Any
    ) -> ExtractionResult:
        """Map a Docling ConversionResult to our ExtractionResult."""
        status = result.status

        if status == ConversionStatus.FAILURE:
            error_msgs = "; ".join(
                e.error_message for e in result.errors
            ) if result.errors else "unknown error"
            return ExtractionResult(
                source_path=path,
                text="",
                method="docling",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="conversion failed",
                error=error_msgs,
            )

        # Extract markdown.
        markdown_text = result.document.export_to_markdown()

        # Page count.
        page_count = len(result.document.pages) if hasattr(result.document, "pages") else 0

        # Determine confidence based on status and content.
        total_chars = len(markdown_text)
        is_partial = status == ConversionStatus.PARTIAL_SUCCESS

        if is_partial:
            error_msgs = "; ".join(
                e.error_message for e in result.errors
            ) if result.errors else ""
            confidence = ConfidenceLevel.MEDIUM
            confidence_reason = f"partial conversion ({error_msgs})" if error_msgs else "partial conversion"
        elif total_chars < 100 and page_count > 0:
            confidence = ConfidenceLevel.LOW
            confidence_reason = f"very little text extracted ({total_chars} chars from {page_count} pages)"
        elif total_chars < 500 and page_count > 2:
            confidence = ConfidenceLevel.MEDIUM
            confidence_reason = f"low text density ({total_chars} chars from {page_count} pages)"
        else:
            confidence = ConfidenceLevel.HIGH
            confidence_reason = f"successful extraction ({total_chars} chars)"
            if page_count > 0:
                confidence_reason = f"successful extraction ({total_chars} chars, {page_count} pages)"

        # Check if this was likely a scanned document.
        # Docling handles OCR transparently, but we note it in metadata.
        is_scanned = False
        suffix = path.suffix.lower()
        if suffix in (".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".webp"):
            is_scanned = True

        metadata: dict[str, Any] = {
            "total_chars": total_chars,
            "conversion_engine": "docling",
            "partial": is_partial,
        }

        return ExtractionResult(
            source_path=path,
            text=markdown_text,
            method="docling",
            success=True,
            confidence=confidence,
            confidence_reason=confidence_reason,
            page_count=page_count,
            is_scanned=is_scanned,
            metadata=metadata,
        )
