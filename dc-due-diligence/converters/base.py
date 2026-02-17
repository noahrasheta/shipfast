"""
Base converter interface and shared data models.

All file type converters inherit from BaseConverter and return ExtractionResult
instances so downstream agents receive a consistent structure regardless of
the source file format.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from pathlib import Path


class ConfidenceLevel(enum.Enum):
    """How reliable the extracted text is likely to be."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ExtractionResult:
    """Standard result returned by every converter.

    Attributes:
        source_path: Absolute path to the original file.
        text: The extracted text content (markdown-formatted where possible).
        method: Short label for how the text was extracted
                (e.g. "pdfplumber", "claude_vision", "openpyxl").
        success: Whether the extraction completed without critical errors.
        confidence: Overall confidence in the extracted text quality.
        confidence_reason: Human-readable explanation of why the confidence
            level was assigned (e.g. "high text density" or "30% of pages
            failed vision extraction").
        page_count: Number of pages (for PDFs) or sheets (for spreadsheets).
        is_scanned: True if the document appears to be scanned/image-based.
        metadata: Arbitrary extra info specific to the file type.
        error: Error message if success is False.
    """

    source_path: Path
    text: str
    method: str
    success: bool
    confidence: ConfidenceLevel
    confidence_reason: str = ""
    page_count: int = 0
    is_scanned: bool = False
    metadata: dict = field(default_factory=dict)
    error: str | None = None

    @property
    def is_reliable(self) -> bool:
        """True when the extraction succeeded with high or medium confidence.

        Downstream agents should check this before treating extracted text
        as trustworthy.  When False, consider noting that the source data
        may be incomplete or inaccurate.
        """
        return self.success and self.confidence in (
            ConfidenceLevel.HIGH,
            ConfidenceLevel.MEDIUM,
        )

    @property
    def is_low_confidence(self) -> bool:
        """True when confidence is LOW or the extraction failed entirely."""
        return not self.success or self.confidence == ConfidenceLevel.LOW

    @property
    def confidence_summary(self) -> str:
        """One-line summary suitable for inclusion in agent reports.

        Examples:
            "high confidence (pdfplumber: strong text density, 450 avg chars/page)"
            "low confidence (claude_vision: 2 of 5 pages failed extraction)"
            "extraction failed (pdfplumber: File not found: /tmp/missing.pdf)"
        """
        if not self.success:
            detail = self.error or "unknown error"
            return f"extraction failed ({self.method}: {detail})"

        reason = self.confidence_reason or self.confidence.value
        return f"{self.confidence.value} confidence ({self.method}: {reason})"


class BaseConverter:
    """Interface that every file-type converter implements.

    Subclasses must override ``convert`` to perform the actual extraction.
    The ``supported_extensions`` class attribute declares which file suffixes
    the converter handles (lowercase, with leading dot -- e.g. ``[".pdf"]``).
    """

    supported_extensions: list[str] = []

    def can_handle(self, path: Path) -> bool:
        """Return True if this converter supports the given file."""
        return path.suffix.lower() in self.supported_extensions

    def convert(self, path: Path) -> ExtractionResult:
        """Extract text from the file at *path*.

        Must be overridden by subclasses.  Implementations should never raise
        on expected failures -- instead return an ``ExtractionResult`` with
        ``success=False`` and a description in ``error``.
        """
        raise NotImplementedError(
            f"{type(self).__name__} must implement convert()"
        )
