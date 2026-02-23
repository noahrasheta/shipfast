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

# If a page yields fewer than this many characters of text on average, the
# document is likely scanned / image-based and should be handled by vision.
_SCANNED_CHARS_PER_PAGE_THRESHOLD = 200

# Minimum average characters per page to consider extraction HIGH confidence.
_HIGH_CONFIDENCE_CHARS_PER_PAGE = 200

# Minimum fraction of characters that must be "readable" (alphanumeric, common
# whitespace, or common punctuation) for extracted text to be considered real
# content rather than font-encoding gibberish from a scanned-as-image PDF.
_MIN_READABLE_CHAR_RATIO = 0.75

# Characters considered "readable" for the gibberish quality check.
_READABLE_CHARS = set(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    " \t\n\r"
    ".,;:!?'\"-()[]{}/@#$%&*+=<>~`^\\_"
)


class PDFConverter(BaseConverter):
    """Extract text and tables from text-based PDFs using pdfplumber.

    When *vision_fallback* is True (the default), scanned PDFs are
    automatically routed to :class:`~converters.vision.VisionConverter`
    for extraction via Claude's vision API.
    """

    supported_extensions: list[str] = [".pdf"]

    def __init__(self, vision_fallback: bool = True, api_key: str | None = None):
        """Initialize the PDF converter.

        Parameters
        ----------
        vision_fallback:
            If True, scanned PDFs (those with very little embedded text)
            are automatically re-processed through Claude vision.
        api_key:
            Optional Anthropic API key passed to the vision fallback
            converter.  If omitted, the ``ANTHROPIC_API_KEY`` environment
            variable is used.
        """
        self._vision_fallback = vision_fallback
        self._api_key = api_key

    def convert(self, path: Path) -> ExtractionResult:
        """Open a PDF with pdfplumber, extract all pages, and return markdown.

        Scanned documents (very little embedded text) are detected and
        automatically routed to Claude vision if *vision_fallback* is enabled.
        """
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

        # Automatic fallback to vision for scanned documents.
        if result.is_scanned and self._vision_fallback:
            from converters.vision import VisionConverter

            vision = VisionConverter(api_key=self._api_key)
            vision_result = vision.convert(path)

            # Preserve the pdfplumber detection context so downstream code
            # knows why vision was used and what the original text density was.
            vision_result.metadata["pdfplumber_fallback"] = True
            vision_result.metadata["pdfplumber_avg_chars_per_page"] = (
                result.metadata.get("avg_chars_per_page", 0)
            )
            return vision_result

        return result

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract(self, path: Path) -> ExtractionResult:
        """Core extraction logic -- opens the PDF, iterates pages, builds
        markdown text, and computes metadata."""
        page_texts: list[str] = []
        total_chars = 0
        tables_found = 0

        with pdfplumber.open(path) as pdf:
            page_count = len(pdf.pages)

            for page in pdf.pages:
                page_md = self._extract_page(page)
                page_texts.append(page_md)
                total_chars += len(page_md)

                tables_found += len(page.find_tables())

        combined_text = "\n\n---\n\n".join(page_texts)

        # Detect scanned/image-based documents.
        avg_chars_per_page = total_chars / max(page_count, 1)
        is_scanned = avg_chars_per_page < _SCANNED_CHARS_PER_PAGE_THRESHOLD

        # Second net: even if text volume looks sufficient, check whether it is
        # actually readable content or font-encoding gibberish from a scanned
        # PDF.  A low ratio of recognizable characters indicates the extracted
        # "text" is noise and vision should be used instead.
        gibberish_detected = False
        readable_ratio = 1.0
        if not is_scanned and total_chars > 0:
            readable_ratio = _compute_readable_ratio(combined_text)
            if readable_ratio < _MIN_READABLE_CHAR_RATIO:
                is_scanned = True
                gibberish_detected = True

        rounded_avg = round(avg_chars_per_page, 1)

        if is_scanned and gibberish_detected:
            confidence = ConfidenceLevel.LOW
            confidence_reason = (
                f"likely scanned, gibberish detected "
                f"({round(readable_ratio * 100, 1)}% readable), "
                f"{rounded_avg} avg chars/page"
            )
        elif is_scanned:
            confidence = ConfidenceLevel.LOW
            confidence_reason = (
                f"likely scanned, only {rounded_avg} avg chars/page"
            )
        elif avg_chars_per_page < _HIGH_CONFIDENCE_CHARS_PER_PAGE:
            confidence = ConfidenceLevel.MEDIUM
            confidence_reason = (
                f"low text density, {rounded_avg} avg chars/page"
            )
        else:
            confidence = ConfidenceLevel.HIGH
            confidence_reason = (
                f"strong text density, {rounded_avg} avg chars/page"
            )

        metadata: dict[str, Any] = {
            "avg_chars_per_page": rounded_avg,
            "total_chars": total_chars,
            "tables_found": tables_found,
        }

        return ExtractionResult(
            source_path=path,
            text=combined_text,
            method="pdfplumber",
            success=True,
            confidence=confidence,
            confidence_reason=confidence_reason,
            page_count=page_count,
            is_scanned=is_scanned,
            metadata=metadata,
        )

    def _extract_page(self, page: pdfplumber.page.Page) -> str:
        """Extract text and tables from a single page, returning markdown.

        Tables are rendered as markdown tables and replaced inline.  Body text
        outside tables is included as plain paragraphs.
        """
        tables = page.find_tables()

        if not tables:
            # No tables -- just return the page text cleaned up.
            raw = page.extract_text() or ""
            return _clean_text(raw)

        # When tables exist we need to stitch together text that sits *between*
        # and *around* the tables.  Strategy:
        # 1. Collect bounding boxes of all tables.
        # 2. Crop the page to regions outside tables for body text.
        # 3. Insert table markdown at the position of each table.

        # Build an ordered list of (top, content) items we'll sort by vertical
        # position so the final output preserves reading order.
        segments: list[tuple[float, str]] = []

        # Gather table regions sorted by vertical position.
        table_bboxes: list[tuple[float, float, float, float]] = []
        for table in tables:
            bbox = table.bbox  # (x0, top, x1, bottom)
            if bbox is None:
                continue
            table_bboxes.append(bbox)
            rows = table.extract()
            if rows:
                md_table = _rows_to_markdown(rows)
                segments.append((bbox[1], md_table))

        # Extract text from regions that are NOT covered by any table.
        non_table_text = self._extract_text_outside_tables(page, table_bboxes)
        if non_table_text.strip():
            # We approximate its position as the top of the page (0) so it
            # appears before tables.  More precise interleaving would require
            # word-level bounding boxes -- this is a pragmatic default.
            segments.append((0.0, non_table_text))

        # Sort by vertical position and join.
        segments.sort(key=lambda s: s[0])
        return "\n\n".join(seg[1] for seg in segments if seg[1].strip())

    def _extract_text_outside_tables(
        self,
        page: pdfplumber.page.Page,
        table_bboxes: list[tuple[float, float, float, float]],
    ) -> str:
        """Return body text from page regions not covered by any table bbox."""
        if not table_bboxes:
            return _clean_text(page.extract_text() or "")

        # Build crop regions that exclude all table areas.  We work in vertical
        # slices above, between, and below the tables.
        page_bbox = (
            float(page.bbox[0]),
            float(page.bbox[1]),
            float(page.bbox[2]),
            float(page.bbox[3]),
        )

        # Sort tables by top coordinate.
        sorted_bboxes = sorted(table_bboxes, key=lambda b: b[1])

        text_parts: list[str] = []
        current_top = page_bbox[1]

        for tbox in sorted_bboxes:
            table_top = tbox[1]
            if table_top > current_top:
                crop = page.crop(
                    (page_bbox[0], current_top, page_bbox[2], table_top)
                )
                raw = crop.extract_text() or ""
                cleaned = _clean_text(raw)
                if cleaned:
                    text_parts.append(cleaned)
            current_top = max(current_top, tbox[3])

        # Region below the last table.
        if current_top < page_bbox[3]:
            crop = page.crop(
                (page_bbox[0], current_top, page_bbox[2], page_bbox[3])
            )
            raw = crop.extract_text() or ""
            cleaned = _clean_text(raw)
            if cleaned:
                text_parts.append(cleaned)

        return "\n\n".join(text_parts)


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _compute_readable_ratio(text: str) -> float:
    """Return the fraction of characters in *text* that are readable.

    Readable characters include ASCII letters, digits, common whitespace, and
    standard punctuation.  A low ratio indicates font-encoding gibberish from
    scanned-as-image PDFs where pdfplumber extracts noise instead of real text.
    """
    if not text:
        return 1.0
    readable_count = sum(1 for ch in text if ch in _READABLE_CHARS)
    return readable_count / len(text)


def _clean_text(raw: str) -> str:
    """Normalize whitespace and strip trailing spaces from extracted text."""
    lines = raw.split("\n")
    cleaned = [line.rstrip() for line in lines]
    # Collapse runs of 3+ blank lines into 2.
    result: list[str] = []
    blank_count = 0
    for line in cleaned:
        if line == "":
            blank_count += 1
            if blank_count <= 2:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)
    return "\n".join(result).strip()


def _rows_to_markdown(rows: list[list[Any]]) -> str:
    """Convert a list of table rows into a markdown table string.

    The first row is treated as the header.  None values are replaced with
    empty strings.
    """
    if not rows:
        return ""

    # Sanitize cells: convert None to empty string, strip whitespace, replace
    # newlines with spaces.
    def _cell(val: Any) -> str:
        if val is None:
            return ""
        text = str(val).strip().replace("\n", " ")
        # Escape pipe characters inside cells so they don't break the table.
        return text.replace("|", "\\|")

    sanitized = [[_cell(c) for c in row] for row in rows]

    # Ensure all rows have the same number of columns.
    max_cols = max(len(r) for r in sanitized)
    for row in sanitized:
        while len(row) < max_cols:
            row.append("")

    header = sanitized[0]
    separator = ["---"] * max_cols
    body = sanitized[1:]

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)
