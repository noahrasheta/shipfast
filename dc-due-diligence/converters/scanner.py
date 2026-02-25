"""
Folder scanner with automatic file type detection.

Walks an opportunity folder recursively, identifies every file's type using
both extension matching and MIME-type detection, and produces a processing
plan that maps each file to the converter that will handle it.  Unknown or
unsupported file types are flagged in the plan but never stop processing.
"""

from __future__ import annotations

import logging
import mimetypes
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class FileType(Enum):
    """Recognized file types that the conversion pipeline can handle."""

    PDF = "pdf"
    XLSX = "xlsx"
    XLSB = "xlsb"
    DOCX = "docx"
    PPTX = "pptx"
    CSV = "csv"
    HTML = "html"
    IMAGE_PNG = "png"
    IMAGE_JPG = "jpg"
    IMAGE_TIFF = "tiff"
    IMAGE_BMP = "bmp"
    IMAGE_WEBP = "webp"
    UNKNOWN = "unknown"


# Maps lowercase file extensions (with leading dot) to their FileType.
_EXTENSION_TO_TYPE: dict[str, FileType] = {
    ".pdf": FileType.PDF,
    ".xlsx": FileType.XLSX,
    ".xlsm": FileType.XLSX,
    ".xlsb": FileType.XLSB,
    ".docx": FileType.DOCX,
    ".dotx": FileType.DOCX,
    ".pptx": FileType.PPTX,
    ".potx": FileType.PPTX,
    ".ppsx": FileType.PPTX,
    ".csv": FileType.CSV,
    ".html": FileType.HTML,
    ".htm": FileType.HTML,
    ".png": FileType.IMAGE_PNG,
    ".jpg": FileType.IMAGE_JPG,
    ".jpeg": FileType.IMAGE_JPG,
    ".tiff": FileType.IMAGE_TIFF,
    ".tif": FileType.IMAGE_TIFF,
    ".bmp": FileType.IMAGE_BMP,
    ".webp": FileType.IMAGE_WEBP,
}

# MIME types that confirm a file type when the extension is ambiguous
# or missing.  Used as a secondary check.
_MIME_TO_TYPE: dict[str, FileType] = {
    "application/pdf": FileType.PDF,
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": FileType.XLSX,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": FileType.DOCX,
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": FileType.PPTX,
    "text/csv": FileType.CSV,
    "text/html": FileType.HTML,
    "image/png": FileType.IMAGE_PNG,
    "image/jpeg": FileType.IMAGE_JPG,
    "image/tiff": FileType.IMAGE_TIFF,
    "image/bmp": FileType.IMAGE_BMP,
    "image/webp": FileType.IMAGE_WEBP,
}

# Maps FileType values to the converter class name that handles them.
# All supported types route to DoclingConverter (fully offline).
_TYPE_TO_CONVERTER: dict[FileType, str] = {
    FileType.PDF: "DoclingConverter",
    FileType.XLSX: "DoclingConverter",
    FileType.XLSB: "DoclingConverter",
    FileType.DOCX: "DoclingConverter",
    FileType.PPTX: "DoclingConverter",
    FileType.CSV: "DoclingConverter",
    FileType.HTML: "DoclingConverter",
    FileType.IMAGE_PNG: "DoclingConverter",
    FileType.IMAGE_JPG: "DoclingConverter",
    FileType.IMAGE_TIFF: "DoclingConverter",
    FileType.IMAGE_BMP: "DoclingConverter",
    FileType.IMAGE_WEBP: "DoclingConverter",
}

# Files and directories that should be skipped during scanning.
_SKIP_NAMES: set[str] = {
    ".DS_Store",
    "Thumbs.db",
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "_converted",
}


@dataclass
class FileEntry:
    """A single file discovered during scanning.

    Attributes:
        path: Absolute path to the file.
        relative_path: Path relative to the scanned root folder.
        file_type: Detected file type (or UNKNOWN).
        converter: Name of the converter class that handles this type,
                   or None if the type is unknown/unsupported.
        size_bytes: File size in bytes.
    """

    path: Path
    relative_path: Path
    file_type: FileType
    converter: str | None
    size_bytes: int


@dataclass
class ScanResult:
    """The complete result of scanning an opportunity folder.

    Attributes:
        root: The folder that was scanned.
        files: All discovered files, in the order they were found.
        supported: Files that have a known converter.
        unsupported: Files with unknown or unsupported types.
        total_size_bytes: Combined size of all discovered files.
        type_counts: Count of files per FileType.
    """

    root: Path
    files: list[FileEntry] = field(default_factory=list)

    @property
    def supported(self) -> list[FileEntry]:
        """Files that have a matching converter."""
        return [f for f in self.files if f.converter is not None]

    @property
    def unsupported(self) -> list[FileEntry]:
        """Files with no matching converter."""
        return [f for f in self.files if f.converter is None]

    @property
    def total_size_bytes(self) -> int:
        """Combined size of all discovered files."""
        return sum(f.size_bytes for f in self.files)

    @property
    def type_counts(self) -> dict[FileType, int]:
        """Count of files grouped by detected type."""
        counts: dict[FileType, int] = {}
        for entry in self.files:
            counts[entry.file_type] = counts.get(entry.file_type, 0) + 1
        return counts

    def summary(self) -> str:
        """Human-readable summary of the scan results."""
        lines = [f"Scanned: {self.root}"]
        lines.append(f"Total files: {len(self.files)}")
        lines.append(
            f"Supported: {len(self.supported)} | "
            f"Unsupported: {len(self.unsupported)}"
        )

        counts = self.type_counts
        if counts:
            lines.append("File types:")
            for file_type, count in sorted(
                counts.items(), key=lambda x: x[1], reverse=True
            ):
                label = file_type.value
                converter = _TYPE_TO_CONVERTER.get(file_type, "none")
                lines.append(f"  {label}: {count} -> {converter}")

        return "\n".join(lines)


def detect_file_type(path: Path) -> FileType:
    """Determine the file type using extension and MIME type detection.

    Extension matching is tried first since it is fast and reliable for
    the file types we support.  MIME-type guessing (via Python's built-in
    ``mimetypes`` module) is used as a fallback when the extension is not
    recognized or absent.

    Returns :attr:`FileType.UNKNOWN` if neither approach produces a match.
    """
    suffix = path.suffix.lower()

    # Primary: match on extension.
    if suffix in _EXTENSION_TO_TYPE:
        return _EXTENSION_TO_TYPE[suffix]

    # Fallback: try MIME-type guessing.
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type and mime_type in _MIME_TO_TYPE:
        return _MIME_TO_TYPE[mime_type]

    return FileType.UNKNOWN


def scan_folder(folder_path: str | Path) -> ScanResult:
    """Recursively scan a folder and produce a processing plan.

    Parameters
    ----------
    folder_path:
        Path to the opportunity folder to scan.

    Returns
    -------
    ScanResult
        A processing plan listing every file with its detected type and
        the converter that will handle it.

    Raises
    ------
    FileNotFoundError
        If *folder_path* does not exist.
    NotADirectoryError
        If *folder_path* exists but is not a directory.
    """
    root = Path(folder_path).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Folder not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    result = ScanResult(root=root)

    for item in sorted(root.rglob("*")):
        # Skip directories themselves -- we only care about files.
        if item.is_dir():
            continue

        # Skip well-known junk files and hidden system directories.
        if _should_skip(item, root):
            logger.debug("Skipping: %s", item)
            continue

        file_type = detect_file_type(item)
        converter = _TYPE_TO_CONVERTER.get(file_type)

        try:
            size_bytes = item.stat().st_size
        except OSError:
            size_bytes = 0

        entry = FileEntry(
            path=item,
            relative_path=item.relative_to(root),
            file_type=file_type,
            converter=converter,
            size_bytes=size_bytes,
        )

        result.files.append(entry)

        if file_type == FileType.UNKNOWN:
            logger.warning(
                "Unknown file type: %s (extension: %s)",
                item.relative_to(root),
                item.suffix or "(none)",
            )

    logger.info(
        "Scan complete: %d files found (%d supported, %d unsupported)",
        len(result.files),
        len(result.supported),
        len(result.unsupported),
    )

    return result


def _should_skip(path: Path, root: Path) -> bool:
    """Determine whether a file should be excluded from the scan.

    Skips:
    - Files whose name is in the junk-file list (e.g. .DS_Store).
    - Files inside directories whose name is in the skip list.
    - Hidden files (names starting with a dot) that are not in a
      recognized format.
    """
    # Check if the file name itself should be skipped.
    if path.name in _SKIP_NAMES:
        return True

    # Check if any parent directory between root and this file should
    # be skipped (e.g. __pycache__, .git).
    relative = path.relative_to(root)
    for part in relative.parts[:-1]:  # Exclude the filename itself
        if part in _SKIP_NAMES:
            return True

    # Skip hidden files (starting with .) unless they have a recognized
    # extension.  This avoids things like .gitignore, .env, etc.
    if path.name.startswith("."):
        detected = detect_file_type(path)
        if detected == FileType.UNKNOWN:
            return True

    return False
