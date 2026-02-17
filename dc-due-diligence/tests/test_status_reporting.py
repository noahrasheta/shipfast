"""
Tests for document processing status reporting.
"""

import tempfile
from pathlib import Path

import pytest

from converters import (
    ConvertedFile,
    PipelineResult,
    print_status_report,
)


@pytest.fixture
def sample_result():
    """Create a sample PipelineResult with various file states."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "test_opportunity"
        root.mkdir()
        converted = root / "_converted"
        converted.mkdir()
        manifest = converted / "manifest.json"

        files = [
            # Successful high-confidence conversion
            ConvertedFile(
                original_path=str(root / "document1.pdf"),
                relative_path="document1.pdf",
                converted_path=str(converted / "document1.md"),
                converted_filename="document1.md",
                file_type="pdf",
                converter="PDFConverter",
                method="pdfplumber",
                success=True,
                confidence="high",
                confidence_reason="strong text density, 500 avg chars/page",
                error=None,
                size_bytes=10000,
                page_count=3,
                elapsed_seconds=0.5,
            ),
            # Successful medium-confidence conversion
            ConvertedFile(
                original_path=str(root / "spreadsheet.xlsx"),
                relative_path="spreadsheet.xlsx",
                converted_path=str(converted / "spreadsheet.md"),
                converted_filename="spreadsheet.md",
                file_type="xlsx",
                converter="ExcelConverter",
                method="openpyxl",
                success=True,
                confidence="medium",
                confidence_reason="3 of 5 sheets extracted",
                error=None,
                size_bytes=5000,
                page_count=5,
                elapsed_seconds=0.3,
            ),
            # Successful low-confidence conversion
            ConvertedFile(
                original_path=str(root / "scanned.pdf"),
                relative_path="scanned.pdf",
                converted_path=str(converted / "scanned.md"),
                converted_filename="scanned.md",
                file_type="pdf",
                converter="VisionConverter",
                method="claude_vision",
                success=True,
                confidence="low",
                confidence_reason="poor image quality, partial text extracted",
                error=None,
                size_bytes=20000,
                page_count=2,
                elapsed_seconds=5.0,
            ),
            # Failed conversion
            ConvertedFile(
                original_path=str(root / "broken.pdf"),
                relative_path="broken.pdf",
                converted_path=None,
                converted_filename=None,
                file_type="pdf",
                converter="PDFConverter",
                method="pdfplumber",
                success=False,
                confidence="low",
                confidence_reason="extraction failed",
                error="File is corrupted or encrypted",
                size_bytes=3000,
                page_count=0,
                elapsed_seconds=0.1,
            ),
            # Unsupported file (skipped)
            ConvertedFile(
                original_path=str(root / "video.mp4"),
                relative_path="video.mp4",
                converted_path=None,
                converted_filename=None,
                file_type="unknown",
                converter=None,
                method=None,
                success=False,
                confidence="low",
                confidence_reason="unsupported file type",
                error="No converter for file type: unknown",
                size_bytes=50000,
                page_count=0,
                elapsed_seconds=0.0,
            ),
        ]

        result = PipelineResult(
            root=root,
            converted_dir=converted,
            manifest_path=manifest,
            files=files,
            elapsed_seconds=6.0,
        )

        yield result


def test_pipeline_result_counts(sample_result):
    """Test that count properties work correctly."""
    assert sample_result.total_files == 5
    assert sample_result.converted_count == 3
    assert sample_result.failed_count == 1
    assert sample_result.skipped_count == 1
    assert sample_result.low_confidence_count == 1


def test_status_report_verbose(sample_result, capsys):
    """Test verbose status report output."""
    print_status_report(sample_result, verbose=True)
    captured = capsys.readouterr()

    # Check header
    assert "DOCUMENT PROCESSING REPORT" in captured.out
    assert "Total files found: 5" in captured.out
    assert "Successfully converted: 3" in captured.out
    assert "Low confidence extractions: 1" in captured.out
    assert "Failed to convert: 1" in captured.out
    assert "Skipped (unsupported type): 1" in captured.out

    # Check failed conversions section
    assert "FAILED CONVERSIONS" in captured.out
    assert "broken.pdf" in captured.out
    assert "File is corrupted or encrypted" in captured.out

    # Check low confidence section
    assert "LOW CONFIDENCE EXTRACTIONS" in captured.out
    assert "scanned.pdf" in captured.out
    assert "poor image quality, partial text extracted" in captured.out

    # Check unsupported files section
    assert "UNSUPPORTED FILES (SKIPPED)" in captured.out
    assert "video.mp4" in captured.out

    # Check success rate
    assert "Success rate: 60.0% (3/5)" in captured.out


def test_status_report_non_verbose(sample_result, capsys):
    """Test non-verbose status report only shows summary."""
    print_status_report(sample_result, verbose=False)
    captured = capsys.readouterr()

    # Should have summary
    assert "DOCUMENT PROCESSING REPORT" in captured.out
    assert "Total files found: 5" in captured.out

    # Should NOT have detailed sections
    assert "FAILED CONVERSIONS" not in captured.out
    assert "LOW CONFIDENCE EXTRACTIONS" not in captured.out
    assert "UNSUPPORTED FILES" not in captured.out

    # Should have paths
    assert "Results saved to:" in captured.out
    assert "Manifest:" in captured.out


def test_status_report_all_successful(capsys):
    """Test report when all files are successfully converted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "test"
        root.mkdir()
        converted = root / "_converted"
        converted.mkdir()

        files = [
            ConvertedFile(
                original_path=str(root / "doc.pdf"),
                relative_path="doc.pdf",
                converted_path=str(converted / "doc.md"),
                converted_filename="doc.md",
                file_type="pdf",
                converter="PDFConverter",
                method="pdfplumber",
                success=True,
                confidence="high",
                confidence_reason="great extraction",
                error=None,
                size_bytes=1000,
                page_count=1,
                elapsed_seconds=0.1,
            )
        ]

        result = PipelineResult(
            root=root,
            converted_dir=converted,
            manifest_path=converted / "manifest.json",
            files=files,
            elapsed_seconds=0.1,
        )

        print_status_report(result, verbose=True)
        captured = capsys.readouterr()

        # Should have success message but no failure sections
        assert "Successfully converted: 1" in captured.out
        assert "FAILED CONVERSIONS" not in captured.out
        assert "LOW CONFIDENCE" not in captured.out
        assert "Success rate: 100.0% (1/1)" in captured.out


def test_status_report_no_successful_conversions(capsys):
    """Test report when no files were successfully converted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "test"
        root.mkdir()
        converted = root / "_converted"
        converted.mkdir()

        files = [
            ConvertedFile(
                original_path=str(root / "bad.pdf"),
                relative_path="bad.pdf",
                converted_path=None,
                converted_filename=None,
                file_type="pdf",
                converter="PDFConverter",
                method="pdfplumber",
                success=False,
                confidence="low",
                confidence_reason="failed",
                error="Could not read file",
                size_bytes=100,
                page_count=0,
                elapsed_seconds=0.1,
            )
        ]

        result = PipelineResult(
            root=root,
            converted_dir=converted,
            manifest_path=converted / "manifest.json",
            files=files,
            elapsed_seconds=0.1,
        )

        print_status_report(result, verbose=True)
        captured = capsys.readouterr()

        assert "Failed to convert: 1" in captured.out
        assert "No files were successfully converted" in captured.out
        assert "Check the errors above" in captured.out
