"""
Conversion pipeline that processes a full opportunity folder.

Takes the folder scanner's processing plan (``ScanResult``), runs each
supported file through its appropriate converter, writes converted
markdown files to a ``_converted/`` staging subfolder, and produces a
JSON manifest listing every document with its conversion status.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from converters.base import BaseConverter, ConfidenceLevel, ExtractionResult
from converters.excel import ExcelConverter
from converters.pdf import PDFConverter
from converters.powerpoint import PowerPointConverter
from converters.scanner import FileEntry, FileType, ScanResult, scan_folder
from converters.vision import VisionConverter
from converters.word import WordConverter

logger = logging.getLogger(__name__)

# Name of the staging subfolder created inside the opportunity folder.
CONVERTED_DIR_NAME = "_converted"

# Name of the manifest file written inside the staging subfolder.
MANIFEST_FILENAME = "manifest.json"


def print_status_report(result: PipelineResult, verbose: bool = True) -> None:
    """Print a detailed human-readable status report.

    Shows a summary of what was processed, lists all problems that occurred,
    and calls out low-confidence extractions so the user knows what to
    expect when agents start analyzing.

    Parameters
    ----------
    result:
        The pipeline result to report on.
    verbose:
        If True, show individual file details for failed and low-confidence
        conversions. If False, only show summary statistics.
    """
    print()
    print("=" * 70)
    print("DOCUMENT PROCESSING REPORT")
    print("=" * 70)
    print()

    # Overall statistics
    print(f"Folder: {result.root}")
    print(f"Processing time: {result.elapsed_seconds:.1f} seconds")
    print()

    total = result.total_files
    converted = result.converted_count
    failed = result.failed_count
    skipped = result.skipped_count
    low_conf = result.low_confidence_count

    print(f"Total files found: {total}")
    print(f"  ✓ Successfully converted: {converted}")
    if low_conf > 0:
        print(f"  ⚠ Low confidence extractions: {low_conf}")
    if failed > 0:
        print(f"  ✗ Failed to convert: {failed}")
    if skipped > 0:
        print(f"  - Skipped (unsupported type): {skipped}")
    print()

    # Detailed breakdown if verbose
    if not verbose:
        print(f"Results saved to: {result.converted_dir}")
        print(f"Manifest: {result.manifest_path}")
        print("=" * 70)
        print()
        return

    # Failed conversions
    failed_files = [f for f in result.files if not f.success and f.converter is not None]
    if failed_files:
        print("FAILED CONVERSIONS")
        print("-" * 70)
        for f in failed_files:
            print(f"✗ {f.relative_path}")
            print(f"  Type: {f.file_type}")
            print(f"  Reason: {f.error or 'Unknown error'}")
            print()

    # Low confidence extractions
    low_conf_files = [
        f for f in result.files
        if f.success and f.confidence == "low"
    ]
    if low_conf_files:
        print("LOW CONFIDENCE EXTRACTIONS")
        print("-" * 70)
        print("These files were converted but may have incomplete or")
        print("inaccurate text. Agents may not have full information.")
        print()
        for f in low_conf_files:
            print(f"⚠ {f.relative_path}")
            print(f"  Method: {f.method}")
            print(f"  Reason: {f.confidence_reason}")
            if f.page_count > 0:
                print(f"  Pages: {f.page_count}")
            print()

    # Unsupported files
    skipped_files = [f for f in result.files if f.converter is None]
    if skipped_files:
        print("UNSUPPORTED FILES (SKIPPED)")
        print("-" * 70)
        for f in skipped_files:
            print(f"- {f.relative_path} ({f.file_type})")
        print()

    # Summary footer
    if converted > 0:
        success_rate = (converted / total) * 100 if total > 0 else 0
        print(f"Success rate: {success_rate:.1f}% ({converted}/{total})")
        print()
        print(f"Converted files saved to: {result.converted_dir}")
        print(f"Full manifest: {result.manifest_path}")
    else:
        print("No files were successfully converted.")
        print("Check the errors above to understand what went wrong.")

    print("=" * 70)
    print()


def _get_converter(converter_name: str, api_key: str | None = None) -> BaseConverter:
    """Instantiate a converter by its class name.

    Parameters
    ----------
    converter_name:
        The converter class name as stored in ``FileEntry.converter``
        (e.g. ``"PDFConverter"``).
    api_key:
        Optional API key forwarded to converters that need external API
        access (PDFConverter's vision fallback, VisionConverter).
    """
    converters: dict[str, BaseConverter] = {
        "PDFConverter": PDFConverter(vision_fallback=True, api_key=api_key),
        "ExcelConverter": ExcelConverter(),
        "WordConverter": WordConverter(),
        "PowerPointConverter": PowerPointConverter(),
        "VisionConverter": VisionConverter(api_key=api_key),
    }
    if converter_name not in converters:
        raise ValueError(f"Unknown converter: {converter_name}")
    return converters[converter_name]


def _safe_filename(relative_path: Path) -> str:
    """Build a safe, unique markdown filename from the source file's relative path.

    Nested directories are flattened by joining path parts with ``--``.
    The file extension is replaced with ``.md``.  Characters outside
    letters, digits, hyphens, underscores, and dots are replaced with
    underscores.

    Examples
    --------
    >>> _safe_filename(Path("financials/budget.xlsx"))
    'financials--budget.md'
    >>> _safe_filename(Path("site photos/front (1).jpg"))
    'site_photos--front__1_.md'
    """
    parts = list(relative_path.parts)
    # Replace extension on the last part.
    stem = relative_path.stem
    parts[-1] = stem

    joined = "--".join(parts)

    # Replace unsafe characters.
    safe = re.sub(r"[^\w\-.]", "_", joined)
    # Collapse multiple underscores.
    safe = re.sub(r"_+", "_", safe)
    # Strip leading/trailing underscores and dashes.
    safe = safe.strip("_-")

    return f"{safe}.md"


@dataclass
class ConvertedFile:
    """Record of a single file's conversion result.

    Attributes:
        original_path: Absolute path to the source file.
        relative_path: Path relative to the opportunity folder root.
        converted_path: Absolute path to the converted markdown file,
            or None if conversion failed or file was unsupported.
        converted_filename: Name of the markdown file inside _converted/,
            or None if not converted.
        file_type: Detected file type label (e.g. "pdf", "xlsx").
        converter: Name of the converter class used, or None.
        method: Extraction method label from the converter result
            (e.g. "pdfplumber", "openpyxl").
        success: Whether conversion succeeded.
        confidence: Confidence level as a string ("high", "medium", "low").
        confidence_reason: Human-readable explanation of confidence.
        error: Error message if conversion failed, otherwise None.
        size_bytes: Original file size in bytes.
        page_count: Number of pages/sheets extracted, or 0.
        elapsed_seconds: Wall-clock seconds the conversion took.
    """

    original_path: str
    relative_path: str
    converted_path: str | None
    converted_filename: str | None
    file_type: str
    converter: str | None
    method: str | None
    success: bool
    confidence: str
    confidence_reason: str
    error: str | None
    size_bytes: int
    page_count: int
    elapsed_seconds: float


@dataclass
class PipelineResult:
    """Complete result of running the conversion pipeline on a folder.

    Attributes:
        root: The opportunity folder that was processed.
        converted_dir: Path to the ``_converted/`` staging subfolder.
        manifest_path: Path to the JSON manifest file.
        files: Record for every file encountered (supported and unsupported).
        total_files: Total number of files encountered.
        converted_count: Number of files successfully converted.
        failed_count: Number of files where conversion was attempted but failed.
        skipped_count: Number of unsupported files that were skipped.
        elapsed_seconds: Total wall-clock time for the entire pipeline.
    """

    root: Path
    converted_dir: Path
    manifest_path: Path
    files: list[ConvertedFile] = field(default_factory=list)
    elapsed_seconds: float = 0.0

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def converted_count(self) -> int:
        return sum(1 for f in self.files if f.success)

    @property
    def failed_count(self) -> int:
        return sum(
            1 for f in self.files
            if not f.success and f.converter is not None
        )

    @property
    def skipped_count(self) -> int:
        return sum(1 for f in self.files if f.converter is None)

    @property
    def low_confidence_count(self) -> int:
        """Count of successfully converted files with low confidence."""
        return sum(
            1 for f in self.files
            if f.success and f.confidence == "low"
        )

    def summary(self) -> str:
        """Human-readable summary of the pipeline run."""
        lines = [
            f"Pipeline complete: {self.root}",
            f"Total files: {self.total_files}",
            f"Converted: {self.converted_count} | "
            f"Failed: {self.failed_count} | "
            f"Skipped (unsupported): {self.skipped_count}",
            f"Staging folder: {self.converted_dir}",
            f"Manifest: {self.manifest_path}",
            f"Time: {self.elapsed_seconds:.1f}s",
        ]
        return "\n".join(lines)


def convert_folder(
    folder_path: str | Path,
    api_key: str | None = None,
) -> PipelineResult:
    """Scan an opportunity folder and convert all supported files.

    This is the main entry point for the conversion pipeline.  It:

    1. Scans the folder using :func:`~converters.scanner.scan_folder`.
    2. Creates a ``_converted/`` subfolder for staging output.
    3. Runs each supported file through its appropriate converter.
    4. Writes converted text as individual markdown files.
    5. Records unsupported files in the manifest without converting.
    6. Writes a JSON manifest listing every file's status.

    Parameters
    ----------
    folder_path:
        Path to the opportunity folder to process.
    api_key:
        Optional Anthropic API key for vision-based extraction.

    Returns
    -------
    PipelineResult
        Complete record of the pipeline run including paths to all
        converted files and the manifest.
    """
    pipeline_start = time.monotonic()

    scan = scan_folder(folder_path)
    converted_dir = scan.root / CONVERTED_DIR_NAME
    converted_dir.mkdir(exist_ok=True)

    manifest_path = converted_dir / MANIFEST_FILENAME

    result = PipelineResult(
        root=scan.root,
        converted_dir=converted_dir,
        manifest_path=manifest_path,
    )

    # Track filenames to handle duplicates within the staging folder.
    used_filenames: dict[str, int] = {}

    for entry in scan.files:
        file_record = _process_file(entry, converted_dir, used_filenames, api_key)
        result.files.append(file_record)

    result.elapsed_seconds = time.monotonic() - pipeline_start

    # Write the manifest.
    _write_manifest(result)

    logger.info(
        "Pipeline complete: %d converted, %d failed, %d skipped in %.1fs",
        result.converted_count,
        result.failed_count,
        result.skipped_count,
        result.elapsed_seconds,
    )

    # Print the status report for user visibility.
    print_status_report(result)

    return result


def _process_file(
    entry: FileEntry,
    converted_dir: Path,
    used_filenames: dict[str, int],
    api_key: str | None,
) -> ConvertedFile:
    """Convert a single file and write the result to the staging folder.

    Unsupported files are recorded with ``success=False`` and no
    conversion is attempted.  Converter errors are caught and recorded
    without stopping the pipeline.
    """
    # Handle unsupported files.
    if entry.converter is None:
        logger.info("Skipping unsupported file: %s", entry.relative_path)
        return ConvertedFile(
            original_path=str(entry.path),
            relative_path=str(entry.relative_path),
            converted_path=None,
            converted_filename=None,
            file_type=entry.file_type.value,
            converter=None,
            method=None,
            success=False,
            confidence="low",
            confidence_reason="unsupported file type",
            error=f"No converter for file type: {entry.file_type.value}",
            size_bytes=entry.size_bytes,
            page_count=0,
            elapsed_seconds=0.0,
        )

    # Build a unique filename for the converted output.
    base_name = _safe_filename(entry.relative_path)
    unique_name = _unique_filename(base_name, used_filenames)
    output_path = converted_dir / unique_name

    # Run the converter.
    start = time.monotonic()
    try:
        converter = _get_converter(entry.converter, api_key=api_key)
        extraction: ExtractionResult = converter.convert(entry.path)
    except Exception as exc:
        elapsed = time.monotonic() - start
        logger.error(
            "Converter crashed for %s: %s", entry.relative_path, exc
        )
        return ConvertedFile(
            original_path=str(entry.path),
            relative_path=str(entry.relative_path),
            converted_path=None,
            converted_filename=None,
            file_type=entry.file_type.value,
            converter=entry.converter,
            method=None,
            success=False,
            confidence="low",
            confidence_reason="converter crashed",
            error=str(exc),
            size_bytes=entry.size_bytes,
            page_count=0,
            elapsed_seconds=round(elapsed, 3),
        )

    elapsed = time.monotonic() - start

    # If the converter reports failure, record it but don't write an output file.
    if not extraction.success:
        logger.warning(
            "Conversion failed for %s: %s",
            entry.relative_path,
            extraction.error,
        )
        return ConvertedFile(
            original_path=str(entry.path),
            relative_path=str(entry.relative_path),
            converted_path=None,
            converted_filename=None,
            file_type=entry.file_type.value,
            converter=entry.converter,
            method=extraction.method,
            success=False,
            confidence=extraction.confidence.value,
            confidence_reason=extraction.confidence_reason,
            error=extraction.error,
            size_bytes=entry.size_bytes,
            page_count=extraction.page_count,
            elapsed_seconds=round(elapsed, 3),
        )

    # Write the converted markdown file with a metadata header.
    markdown_content = _build_markdown(entry, extraction)
    output_path.write_text(markdown_content, encoding="utf-8")

    logger.info(
        "Converted %s -> %s (%s, %s confidence)",
        entry.relative_path,
        unique_name,
        extraction.method,
        extraction.confidence.value,
    )

    return ConvertedFile(
        original_path=str(entry.path),
        relative_path=str(entry.relative_path),
        converted_path=str(output_path),
        converted_filename=unique_name,
        file_type=entry.file_type.value,
        converter=entry.converter,
        method=extraction.method,
        success=True,
        confidence=extraction.confidence.value,
        confidence_reason=extraction.confidence_reason,
        error=None,
        size_bytes=entry.size_bytes,
        page_count=extraction.page_count,
        elapsed_seconds=round(elapsed, 3),
    )


def _build_markdown(entry: FileEntry, extraction: ExtractionResult) -> str:
    """Build the final markdown content with a metadata header.

    The header gives agents context about the source file without needing
    to read the manifest separately.
    """
    header_lines = [
        f"# {entry.relative_path}",
        "",
        f"- **Source:** `{entry.relative_path}`",
        f"- **Type:** {entry.file_type.value}",
        f"- **Method:** {extraction.method}",
        f"- **Confidence:** {extraction.confidence.value} -- {extraction.confidence_reason}",
    ]
    if extraction.page_count > 0:
        label = "pages" if entry.file_type == FileType.PDF else "sheets/slides"
        header_lines.append(f"- **Pages:** {extraction.page_count} {label}")
    if extraction.is_scanned:
        header_lines.append("- **Note:** Scanned/image-based document (OCR extracted)")

    header_lines.append("")
    header_lines.append("---")
    header_lines.append("")

    return "\n".join(header_lines) + extraction.text + "\n"


def _unique_filename(base_name: str, used: dict[str, int]) -> str:
    """Ensure a filename is unique within the staging folder.

    If ``base_name`` has already been used, a numeric suffix is appended
    (e.g. ``budget.md`` becomes ``budget_2.md``).

    The *used* dict is mutated to track counts.
    """
    if base_name not in used:
        used[base_name] = 1
        return base_name

    used[base_name] += 1
    stem = base_name.rsplit(".", 1)[0]
    return f"{stem}_{used[base_name]}.md"


def _write_manifest(result: PipelineResult) -> None:
    """Write the JSON manifest to the staging folder.

    The manifest is the authoritative record of what was converted and
    what failed.  Agents read this file to know which documents are
    available and how reliable each extraction is.
    """
    manifest: dict[str, Any] = {
        "opportunity_folder": str(result.root),
        "converted_dir": str(result.converted_dir),
        "pipeline_summary": {
            "total_files": result.total_files,
            "converted": result.converted_count,
            "failed": result.failed_count,
            "skipped_unsupported": result.skipped_count,
            "elapsed_seconds": round(result.elapsed_seconds, 3),
        },
        "files": [],
    }

    for f in result.files:
        entry: dict[str, Any] = {
            "original_path": f.original_path,
            "relative_path": f.relative_path,
            "converted_path": f.converted_path,
            "converted_filename": f.converted_filename,
            "file_type": f.file_type,
            "converter": f.converter,
            "method": f.method,
            "success": f.success,
            "confidence": f.confidence,
            "confidence_reason": f.confidence_reason,
            "error": f.error,
            "size_bytes": f.size_bytes,
            "page_count": f.page_count,
            "elapsed_seconds": f.elapsed_seconds,
        }
        manifest["files"].append(entry)

    result.manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    logger.info("Manifest written: %s", result.manifest_path)
