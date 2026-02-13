"""
Word document conversion for .docx files.

Extracts text, headings, tables, and notes the presence of embedded images
from Word documents using python-docx.  Output is clean markdown with
headings mapped to their corresponding markdown levels and tables rendered
as markdown tables.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import docx
from docx.document import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from converters.base import BaseConverter, ConfidenceLevel, ExtractionResult


class WordConverter(BaseConverter):
    """Extract text from Word documents (.docx) using python-docx.

    Headings are mapped to markdown heading levels (# through ######).
    Tables are rendered as markdown tables.  Embedded images are noted
    with a placeholder indicating their presence.
    """

    supported_extensions: list[str] = [".docx"]

    def convert(self, path: Path) -> ExtractionResult:
        """Open a .docx file, extract all content, and return markdown."""
        path = Path(path).resolve()

        if not path.exists():
            return ExtractionResult(
                source_path=path,
                text="",
                method="python-docx",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="file not found",
                error=f"File not found: {path}",
            )

        if path.suffix.lower() not in self.supported_extensions:
            return ExtractionResult(
                source_path=path,
                text="",
                method="python-docx",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="unsupported file type",
                error=f"Not a Word document: {path.suffix}",
            )

        try:
            return self._extract(path)
        except Exception as exc:
            return ExtractionResult(
                source_path=path,
                text="",
                method="python-docx",
                success=False,
                confidence=ConfidenceLevel.LOW,
                confidence_reason="extraction crashed",
                error=f"Extraction failed: {exc}",
            )

    # ------------------------------------------------------------------
    # Internal extraction
    # ------------------------------------------------------------------

    def _extract(self, path: Path) -> ExtractionResult:
        """Core extraction logic -- iterates document body elements in order."""
        document = docx.Document(str(path))

        sections: list[str] = []
        total_chars = 0
        paragraph_count = 0
        table_count = 0
        heading_count = 0
        image_count = _count_images(document)

        # Iterate through body elements in document order so that tables
        # and paragraphs appear in their original sequence.
        for element in document.element.body:
            tag = element.tag

            if tag.endswith("}p"):
                # It's a paragraph (w:p element).
                para = Paragraph(element, document)
                md = _paragraph_to_markdown(para)
                if md:
                    sections.append(md)
                    total_chars += len(md)
                    paragraph_count += 1
                    if para.style and para.style.name and para.style.name.startswith("Heading"):
                        heading_count += 1

            elif tag.endswith("}tbl"):
                # It's a table (w:tbl element).
                table = Table(element, document)
                md_table = _table_to_markdown(table)
                if md_table:
                    sections.append(md_table)
                    total_chars += len(md_table)
                    table_count += 1

        # Add image presence note at the end if images were found.
        if image_count > 0:
            img_note = (
                f"\n\n*[Document contains {image_count} embedded "
                f"image{'s' if image_count != 1 else ''} "
                f"(not extracted as text)]*"
            )
            sections.append(img_note)

        combined_text = "\n\n".join(sections)

        # Confidence scoring.
        confidence, confidence_reason = _score_confidence(
            total_chars=total_chars,
            paragraph_count=paragraph_count,
            table_count=table_count,
            heading_count=heading_count,
        )

        metadata: dict[str, Any] = {
            "paragraph_count": paragraph_count,
            "table_count": table_count,
            "heading_count": heading_count,
            "image_count": image_count,
            "total_chars": total_chars,
        }

        return ExtractionResult(
            source_path=path,
            text=combined_text,
            method="python-docx",
            success=True,
            confidence=confidence,
            confidence_reason=confidence_reason,
            page_count=1,  # Word docs don't have a fixed page count in the XML
            metadata=metadata,
        )


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------


def _paragraph_to_markdown(para: Paragraph) -> str:
    """Convert a single paragraph to markdown text.

    Headings are converted to the appropriate markdown heading level.
    Regular paragraphs are returned as plain text.  Empty paragraphs
    are returned as empty strings.
    """
    text = para.text.strip()
    if not text:
        return ""

    style_name = para.style.name if para.style else ""

    # Map Word heading styles to markdown heading levels.
    if style_name.startswith("Heading"):
        level = _heading_level(style_name)
        prefix = "#" * level
        return f"{prefix} {text}"

    # Title style gets h1.
    if style_name == "Title":
        return f"# {text}"

    # Subtitle style gets h2.
    if style_name == "Subtitle":
        return f"## {text}"

    # List items: detect bullet and numbered styles.
    if "List Bullet" in style_name or "List" in style_name and "Number" not in style_name:
        return f"- {text}"
    if "List Number" in style_name:
        return f"1. {text}"

    return text


def _heading_level(style_name: str) -> int:
    """Extract the numeric heading level from a Word style name.

    Examples: 'Heading 1' -> 1, 'Heading 3' -> 3.  Defaults to 1 if
    the number cannot be parsed.  Clamps to the range 1-6 for valid
    markdown heading levels.
    """
    parts = style_name.split()
    for part in parts:
        if part.isdigit():
            level = int(part)
            return max(1, min(6, level))
    return 1


def _table_to_markdown(table: Table) -> str:
    """Convert a python-docx Table to a markdown table string.

    The first row is treated as the header.  Empty tables return
    an empty string.
    """
    rows: list[list[str]] = []
    for row in table.rows:
        cells = [_clean_cell(cell.text) for cell in row.cells]
        rows.append(cells)

    if not rows:
        return ""

    # Skip tables where every cell is empty.
    if not any(cell for row in rows for cell in row):
        return ""

    # Normalize column count across all rows.
    max_cols = max(len(r) for r in rows)
    if max_cols == 0:
        return ""

    normalized: list[list[str]] = []
    for row in rows:
        padded = list(row)
        while len(padded) < max_cols:
            padded.append("")
        normalized.append(padded[:max_cols])

    # Escape pipe characters in cells.
    escaped: list[list[str]] = []
    for row in normalized:
        escaped.append([cell.replace("|", "\\|") for cell in row])

    header = escaped[0]
    separator = ["---"] * max_cols
    body = escaped[1:]

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)


def _clean_cell(text: str) -> str:
    """Clean a table cell's text for markdown display."""
    cleaned = text.strip()
    # Replace newlines with spaces to keep table structure intact.
    cleaned = cleaned.replace("\n", " ").replace("\r", " ")
    return cleaned


def _count_images(document: Document) -> int:
    """Count embedded images (blip elements) in the document body.

    This looks for drawing elements that contain image references
    (a:blip tags) in the document XML.
    """
    count = 0
    blip_tag = qn("a:blip")
    for blip in document.element.body.iter(blip_tag):
        count += 1
    return count


def _score_confidence(
    total_chars: int,
    paragraph_count: int,
    table_count: int,
    heading_count: int,
) -> tuple[ConfidenceLevel, str]:
    """Determine confidence level based on extraction metrics.

    Returns a (confidence, reason) tuple.
    """
    if total_chars == 0 and paragraph_count == 0 and table_count == 0:
        return (
            ConfidenceLevel.LOW,
            "no content extracted from document",
        )

    if total_chars < 20:
        return (
            ConfidenceLevel.LOW,
            f"very little content, only {total_chars} characters extracted",
        )

    if total_chars < 100:
        return (
            ConfidenceLevel.MEDIUM,
            f"sparse content, {total_chars} characters "
            f"across {paragraph_count} paragraph(s)",
        )

    parts = []
    parts.append(f"{paragraph_count} paragraph(s)")
    if table_count:
        parts.append(f"{table_count} table(s)")
    if heading_count:
        parts.append(f"{heading_count} heading(s)")

    return (
        ConfidenceLevel.HIGH,
        f"well-structured content with {', '.join(parts)}",
    )
