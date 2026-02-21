"""
Document converters for data center due diligence processing.

Each converter takes a file path and returns an ExtractionResult containing
the extracted text, metadata about the extraction, and a confidence score.

The ``scanner`` module provides folder scanning and automatic file type
detection so the conversion pipeline knows which converter to use for
each file in an opportunity folder.

The ``pipeline`` module ties everything together: it scans a folder,
converts all supported files, writes the results to a ``_converted/``
staging subfolder, and produces a JSON manifest for downstream agents.
"""

from converters.base import BaseConverter, ExtractionResult, ConfidenceLevel
from converters.excel import ExcelConverter
from converters.generate_pdf import (
    PDFResult,
    generate_pdf,
    generate_executive_pdf,
    generate_client_pdf,
)
from converters.pdf import PDFConverter
from converters.pipeline import (
    ConvertedFile,
    PipelineResult,
    convert_folder,
    print_status_report,
    CONVERTED_DIR_NAME,
    MANIFEST_FILENAME,
)
from converters.powerpoint import PowerPointConverter
from converters.scanner import FileEntry, FileType, ScanResult, scan_folder
from converters.vision import VisionConverter
from converters.word import WordConverter

__all__ = [
    "BaseConverter",
    "ConfidenceLevel",
    "ConvertedFile",
    "CONVERTED_DIR_NAME",
    "convert_folder",
    "ExcelConverter",
    "ExtractionResult",
    "FileEntry",
    "FileType",
    "generate_client_pdf",
    "generate_executive_pdf",
    "generate_pdf",
    "MANIFEST_FILENAME",
    "PDFConverter",
    "PDFResult",
    "PipelineResult",
    "PowerPointConverter",
    "print_status_report",
    "ScanResult",
    "VisionConverter",
    "WordConverter",
    "scan_folder",
]
