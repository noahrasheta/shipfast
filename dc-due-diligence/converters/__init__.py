"""
Document converters for data center due diligence processing.

All conversion is handled by Docling (fully offline) and PII redaction
is handled by GLiNER (fully offline).  No API calls are made during
the conversion or redaction pipeline.

The ``scanner`` module provides folder scanning and automatic file type
detection so the conversion pipeline knows which files to convert.

The ``pipeline`` module ties everything together: it scans a folder,
converts all supported files via Docling, redacts PII via GLiNER,
writes the results to a ``_converted/`` staging subfolder, and produces
a JSON manifest for downstream agents.
"""

from converters.base import BaseConverter, ExtractionResult, ConfidenceLevel
from converters.docling_converter import DoclingConverter
from converters.generate_pdf import (
    PDFResult,
    generate_pdf,
    generate_executive_pdf,
    generate_client_pdf,
    generate_all_pdfs,
)
from converters.pipeline import (
    ConvertedFile,
    PipelineResult,
    convert_folder,
    print_status_report,
    CONVERTED_DIR_NAME,
    MANIFEST_FILENAME,
)
from converters.redactor import (
    RedactedEntity,
    RedactionReport,
    RedactionResult,
    redact_text,
    redact_file,
    redact_converted_folder,
)
from converters.scanner import FileEntry, FileType, ScanResult, scan_folder

__all__ = [
    "BaseConverter",
    "ConfidenceLevel",
    "ConvertedFile",
    "CONVERTED_DIR_NAME",
    "convert_folder",
    "DoclingConverter",
    "ExtractionResult",
    "FileEntry",
    "FileType",
    "generate_all_pdfs",
    "generate_client_pdf",
    "generate_executive_pdf",
    "generate_pdf",
    "MANIFEST_FILENAME",
    "PDFResult",
    "PipelineResult",
    "print_status_report",
    "RedactedEntity",
    "RedactionReport",
    "RedactionResult",
    "redact_converted_folder",
    "redact_file",
    "redact_text",
    "ScanResult",
    "scan_folder",
]
