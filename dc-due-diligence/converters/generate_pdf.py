"""
Markdown-to-PDF conversion for due diligence deliverables.

Converts markdown files (executive summary, client summary) into styled
PDF documents using the markdown-pdf library.  Each document type has its
own CSS stylesheet controlling visual presentation.  The markdown source
files are preserved alongside the generated PDFs.

Uses markdown-pdf (backed by PyMuPDF) which provides pre-built wheels
for all major platforms -- no system-level dependencies like Pango or
wkhtmltopdf are required.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from markdown_pdf import MarkdownPdf, Section

logger = logging.getLogger(__name__)

# Path to the CSS stylesheets relative to the plugin root.
_STYLES_DIR = Path(__file__).resolve().parent.parent / "templates" / "pdf-styles"

# Map document types to their stylesheet filenames.
_STYLESHEETS: dict[str, str] = {
    "executive": "executive-summary.css",
    "client": "client-summary.css",
}

__all__ = [
    "PDFResult",
    "generate_pdf",
    "generate_executive_pdf",
    "generate_client_pdf",
    "generate_all_pdfs",
]


@dataclass
class PDFResult:
    """Result of a markdown-to-PDF conversion.

    Attributes:
        source_path: Absolute path to the source markdown file.
        pdf_path: Absolute path to the generated PDF file, or None if
            conversion failed.
        success: Whether the conversion completed without errors.
        error: Error message if success is False, otherwise None.
        size_bytes: Size of the generated PDF in bytes, or 0 on failure.
    """

    source_path: Path
    pdf_path: Path | None
    success: bool
    error: str | None
    size_bytes: int


def _load_stylesheet(doc_type: str) -> str:
    """Load the CSS stylesheet for the given document type.

    Parameters
    ----------
    doc_type:
        Document type key -- ``"executive"`` or ``"client"``.

    Returns
    -------
    str
        The CSS content, or an empty string if the stylesheet cannot
        be read (a warning is logged but conversion proceeds with
        default styling).
    """
    filename = _STYLESHEETS.get(doc_type)
    if filename is None:
        logger.warning("No stylesheet mapped for document type '%s'", doc_type)
        return ""

    stylesheet_path = _STYLES_DIR / filename
    if not stylesheet_path.exists():
        logger.warning("Stylesheet not found: %s", stylesheet_path)
        return ""

    return stylesheet_path.read_text(encoding="utf-8")


def generate_pdf(
    markdown_path: str | Path,
    output_path: str | Path | None = None,
    doc_type: str = "executive",
) -> PDFResult:
    """Convert a markdown file to a styled PDF document.

    The source markdown file is never modified or removed.  The PDF is
    written alongside it (same directory, same stem, ``.pdf`` extension)
    unless an explicit ``output_path`` is provided.

    Parameters
    ----------
    markdown_path:
        Path to the markdown file to convert.
    output_path:
        Where to write the PDF.  Defaults to the same directory and
        stem as ``markdown_path`` with a ``.pdf`` extension.
    doc_type:
        Document type controlling which CSS stylesheet is applied.
        ``"executive"`` for the scored internal summary, ``"client"``
        for the external-facing client summary.

    Returns
    -------
    PDFResult
        Conversion outcome including the PDF path and any error info.
    """
    markdown_path = Path(markdown_path).resolve()

    if not markdown_path.exists():
        return PDFResult(
            source_path=markdown_path,
            pdf_path=None,
            success=False,
            error=f"Markdown file not found: {markdown_path}",
            size_bytes=0,
        )

    if output_path is None:
        output_path = markdown_path.with_suffix(".pdf")
    else:
        output_path = Path(output_path).resolve()

    # Read the markdown content.
    markdown_text = markdown_path.read_text(encoding="utf-8")

    if not markdown_text.strip():
        return PDFResult(
            source_path=markdown_path,
            pdf_path=None,
            success=False,
            error="Markdown file is empty",
            size_bytes=0,
        )

    # Load the CSS stylesheet for this document type.
    css = _load_stylesheet(doc_type)

    try:
        pdf = MarkdownPdf(toc_level=0)
        section = Section(markdown_text, toc=False, paper_size="Letter")
        pdf.add_section(section, user_css=css if css else None)
        pdf.meta["creator"] = "Data Canopy Due Diligence"

        # Ensure the output directory exists.
        output_path.parent.mkdir(parents=True, exist_ok=True)

        pdf.save(str(output_path))
    except Exception as exc:
        logger.error("PDF generation failed for %s: %s", markdown_path.name, exc)
        return PDFResult(
            source_path=markdown_path,
            pdf_path=None,
            success=False,
            error=f"PDF generation failed: {exc}",
            size_bytes=0,
        )

    size_bytes = output_path.stat().st_size
    logger.info(
        "Generated PDF: %s (%d bytes) from %s",
        output_path.name,
        size_bytes,
        markdown_path.name,
    )

    return PDFResult(
        source_path=markdown_path,
        pdf_path=output_path,
        success=True,
        error=None,
        size_bytes=size_bytes,
    )


def generate_executive_pdf(
    markdown_path: str | Path,
    output_path: str | Path | None = None,
) -> PDFResult:
    """Convert an executive summary markdown file to a styled PDF.

    Convenience wrapper around :func:`generate_pdf` that applies the
    executive summary stylesheet.

    Parameters
    ----------
    markdown_path:
        Path to the ``EXECUTIVE_SUMMARY.md`` file.
    output_path:
        Where to write the PDF.  Defaults to ``EXECUTIVE_SUMMARY.pdf``
        in the same directory.

    Returns
    -------
    PDFResult
        Conversion outcome.
    """
    return generate_pdf(markdown_path, output_path=output_path, doc_type="executive")


def generate_client_pdf(
    markdown_path: str | Path,
    output_path: str | Path | None = None,
) -> PDFResult:
    """Convert a client summary markdown file to a styled PDF.

    Convenience wrapper around :func:`generate_pdf` that applies the
    client summary stylesheet.

    Parameters
    ----------
    markdown_path:
        Path to the ``CLIENT_SUMMARY.md`` file.
    output_path:
        Where to write the PDF.  Defaults to ``CLIENT_SUMMARY.pdf``
        in the same directory.

    Returns
    -------
    PDFResult
        Conversion outcome.
    """
    return generate_pdf(markdown_path, output_path=output_path, doc_type="client")


def generate_all_pdfs(folder_path: str | Path) -> list[PDFResult]:
    """Convert all due diligence summary markdown files in a folder to PDF.

    Looks for ``EXECUTIVE_SUMMARY.md`` and ``CLIENT_SUMMARY.md`` in the
    given folder and converts each one that exists.  Files that do not
    exist are silently skipped.

    Parameters
    ----------
    folder_path:
        Path to the opportunity folder containing the summary markdown
        files.

    Returns
    -------
    list[PDFResult]
        A result for each file that was attempted (skipped files are not
        included).
    """
    folder = Path(folder_path).resolve()
    results: list[PDFResult] = []

    summaries = [
        ("EXECUTIVE_SUMMARY.md", "executive"),
        ("CLIENT_SUMMARY.md", "client"),
    ]

    for filename, doc_type in summaries:
        md_path = folder / filename
        if md_path.exists():
            result = generate_pdf(md_path, doc_type=doc_type)
            results.append(result)
            status = "OK" if result.success else "FAILED"
            print(
                f"{status}: {filename} -> {result.pdf_path.name if result.pdf_path else 'N/A'}"
                + (f" ({result.size_bytes} bytes)" if result.success else f" ({result.error})")
            )
        else:
            print(f"SKIPPED: {filename} not found in {folder}")

    return results


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if len(sys.argv) != 2:
        print("Usage: python -m converters.generate_pdf <opportunity-folder>")
        sys.exit(1)

    folder = sys.argv[1]
    results = generate_all_pdfs(folder)

    success_count = sum(1 for r in results if r.success)
    fail_count = sum(1 for r in results if not r.success)

    if not results:
        print("No summary files found to convert.")
        sys.exit(1)

    print(f"\nPDF generation complete: {success_count} succeeded, {fail_count} failed")
    sys.exit(0 if fail_count == 0 else 1)
