"""
Tests for the folder scanner and file type detection.

Covers recursive scanning, file type detection for all supported formats,
handling of unknown types, special characters in filenames, and the
processing plan structure.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from converters.scanner import (
    FileEntry,
    FileType,
    ScanResult,
    _should_skip,
    detect_file_type,
    scan_folder,
)


# ------------------------------------------------------------------
# detect_file_type
# ------------------------------------------------------------------


class TestDetectFileType:
    """Tests for the file type detection function."""

    @pytest.mark.parametrize(
        "filename, expected",
        [
            ("report.pdf", FileType.PDF),
            ("report.PDF", FileType.PDF),
            ("data.xlsx", FileType.XLSX),
            ("data.XLSX", FileType.XLSX),
            ("pro_forma.xlsb", FileType.XLSB),
            ("pro_forma.XLSB", FileType.XLSB),
            ("contract.docx", FileType.DOCX),
            ("contract.DOCX", FileType.DOCX),
            ("presentation.pptx", FileType.PPTX),
            ("presentation.PPTX", FileType.PPTX),
            ("photo.png", FileType.IMAGE_PNG),
            ("photo.PNG", FileType.IMAGE_PNG),
            ("photo.jpg", FileType.IMAGE_JPG),
            ("photo.JPG", FileType.IMAGE_JPG),
            ("photo.jpeg", FileType.IMAGE_JPG),
            ("photo.JPEG", FileType.IMAGE_JPG),
            ("scan.tiff", FileType.IMAGE_TIFF),
            ("scan.tif", FileType.IMAGE_TIFF),
            ("scan.TIFF", FileType.IMAGE_TIFF),
            ("diagram.bmp", FileType.IMAGE_BMP),
            ("diagram.webp", FileType.IMAGE_WEBP),
        ],
    )
    def test_recognized_extensions(self, filename: str, expected: FileType):
        """All supported extensions are correctly identified."""
        assert detect_file_type(Path(filename)) == expected

    @pytest.mark.parametrize(
        "filename",
        [
            "readme.txt",
            "script.py",
            "archive.zip",
            "database.sqlite",
            "noextension",
            ".hidden_no_ext",
        ],
    )
    def test_unknown_extensions(self, filename: str):
        """Unsupported or missing extensions return UNKNOWN."""
        assert detect_file_type(Path(filename)) == FileType.UNKNOWN

    def test_extension_takes_priority(self):
        """Extension-based detection runs before MIME-type guessing."""
        # A .pdf extension should be detected even if the name is odd.
        assert detect_file_type(Path("weird name (1).pdf")) == FileType.PDF


# ------------------------------------------------------------------
# scan_folder
# ------------------------------------------------------------------


class TestScanFolder:
    """Tests for the folder scanning function."""

    def test_scan_empty_folder(self, tmp_path: Path):
        """Scanning an empty folder returns an empty plan."""
        result = scan_folder(tmp_path)
        assert result.root == tmp_path
        assert result.files == []
        assert len(result.supported) == 0
        assert len(result.unsupported) == 0
        assert result.total_size_bytes == 0

    def test_scan_flat_folder(self, tmp_path: Path):
        """Scanning a folder with files produces entries for each."""
        (tmp_path / "report.pdf").write_bytes(b"%PDF-1.4 fake")
        (tmp_path / "data.xlsx").write_bytes(b"fake xlsx")
        (tmp_path / "photo.jpg").write_bytes(b"\xff\xd8fake")

        result = scan_folder(tmp_path)

        assert len(result.files) == 3
        assert len(result.supported) == 3
        assert len(result.unsupported) == 0

        types = {e.file_type for e in result.files}
        assert types == {FileType.PDF, FileType.XLSX, FileType.IMAGE_JPG}

    def test_scan_recursive(self, tmp_path: Path):
        """Files in subfolders are discovered."""
        sub = tmp_path / "subfolder" / "deep"
        sub.mkdir(parents=True)
        (sub / "nested.pdf").write_bytes(b"fake pdf")
        (tmp_path / "top.docx").write_bytes(b"fake docx")

        result = scan_folder(tmp_path)

        assert len(result.files) == 2
        paths = {str(e.relative_path) for e in result.files}
        assert "subfolder/deep/nested.pdf" in paths
        assert "top.docx" in paths

    def test_unknown_types_flagged(self, tmp_path: Path):
        """Unknown file types appear in the unsupported list."""
        (tmp_path / "readme.txt").write_text("hello")
        (tmp_path / "report.pdf").write_bytes(b"fake")

        result = scan_folder(tmp_path)

        assert len(result.files) == 2
        assert len(result.supported) == 1
        assert len(result.unsupported) == 1
        assert result.unsupported[0].file_type == FileType.UNKNOWN
        assert result.unsupported[0].converter is None

    def test_unknown_types_do_not_stop_processing(self, tmp_path: Path):
        """Unknown files are logged but the scan completes successfully."""
        (tmp_path / "mystery.xyz").write_bytes(b"???")
        (tmp_path / "good.pdf").write_bytes(b"fake")
        (tmp_path / "also_good.xlsx").write_bytes(b"fake")

        result = scan_folder(tmp_path)

        # All three files are present in the plan.
        assert len(result.files) == 3
        # Two are supported, one is not.
        assert len(result.supported) == 2
        assert len(result.unsupported) == 1

    def test_special_characters_in_filenames(self, tmp_path: Path):
        """Files with spaces, parentheses, and unicode are handled."""
        (tmp_path / "0a. Datanovax Teaser (Part I) ext.pdf").write_bytes(
            b"fake"
        )
        (tmp_path / "report #2 [final].xlsx").write_bytes(b"fake")
        (tmp_path / "uber-cool.docx").write_bytes(b"fake")

        result = scan_folder(tmp_path)

        assert len(result.files) == 3
        assert all(e.converter is not None for e in result.files)

        # Verify the paths round-trip correctly.
        for entry in result.files:
            assert entry.path.exists()

    def test_skips_ds_store(self, tmp_path: Path):
        """macOS .DS_Store files are excluded from the scan."""
        (tmp_path / ".DS_Store").write_bytes(b"\x00\x00")
        (tmp_path / "report.pdf").write_bytes(b"fake")

        result = scan_folder(tmp_path)

        assert len(result.files) == 1
        assert result.files[0].file_type == FileType.PDF

    def test_skips_pycache_directory(self, tmp_path: Path):
        """Files inside __pycache__ directories are excluded."""
        cache_dir = tmp_path / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "module.cpython-311.pyc").write_bytes(b"fake")
        (tmp_path / "report.pdf").write_bytes(b"fake")

        result = scan_folder(tmp_path)

        assert len(result.files) == 1

    def test_skips_hidden_files_without_known_extension(self, tmp_path: Path):
        """Hidden files (dotfiles) are skipped unless they have a
        recognized extension."""
        (tmp_path / ".gitignore").write_text("*.pyc")
        (tmp_path / ".env").write_text("SECRET=123")
        (tmp_path / "report.pdf").write_bytes(b"fake")

        result = scan_folder(tmp_path)

        assert len(result.files) == 1
        assert result.files[0].file_type == FileType.PDF

    def test_nonexistent_folder_raises(self):
        """Scanning a path that doesn't exist raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            scan_folder("/nonexistent/path/123456")

    def test_file_not_directory_raises(self, tmp_path: Path):
        """Scanning a file instead of a directory raises NotADirectoryError."""
        file_path = tmp_path / "a_file.txt"
        file_path.write_text("not a directory")

        with pytest.raises(NotADirectoryError):
            scan_folder(file_path)

    def test_file_entry_converter_mapping(self, tmp_path: Path):
        """Each file type maps to the correct converter name."""
        (tmp_path / "a.pdf").write_bytes(b"fake")
        (tmp_path / "b.xlsx").write_bytes(b"fake")
        (tmp_path / "c.xlsb").write_bytes(b"fake")
        (tmp_path / "d.docx").write_bytes(b"fake")
        (tmp_path / "e.pptx").write_bytes(b"fake")
        (tmp_path / "f.png").write_bytes(b"fake")
        (tmp_path / "g.jpg").write_bytes(b"fake")
        (tmp_path / "h.tiff").write_bytes(b"fake")
        (tmp_path / "i.bmp").write_bytes(b"fake")
        (tmp_path / "j.webp").write_bytes(b"fake")

        result = scan_folder(tmp_path)

        converter_map = {e.path.name: e.converter for e in result.files}

        assert converter_map["a.pdf"] == "DoclingConverter"
        assert converter_map["b.xlsx"] == "DoclingConverter"
        assert converter_map["c.xlsb"] == "DoclingConverter"
        assert converter_map["d.docx"] == "DoclingConverter"
        assert converter_map["e.pptx"] == "DoclingConverter"
        assert converter_map["f.png"] == "DoclingConverter"
        assert converter_map["g.jpg"] == "DoclingConverter"
        assert converter_map["h.tiff"] == "DoclingConverter"
        assert converter_map["i.bmp"] == "DoclingConverter"
        assert converter_map["j.webp"] == "DoclingConverter"

    def test_file_sizes_captured(self, tmp_path: Path):
        """File sizes are recorded in the entries."""
        content = b"x" * 1024
        (tmp_path / "big.pdf").write_bytes(content)

        result = scan_folder(tmp_path)

        assert result.files[0].size_bytes == 1024
        assert result.total_size_bytes == 1024

    def test_relative_paths_correct(self, tmp_path: Path):
        """Relative paths are computed from the scan root."""
        sub = tmp_path / "phase1" / "docs"
        sub.mkdir(parents=True)
        (sub / "plan.pdf").write_bytes(b"fake")

        result = scan_folder(tmp_path)

        entry = result.files[0]
        assert entry.relative_path == Path("phase1/docs/plan.pdf")
        assert entry.path.is_absolute()

    def test_accepts_string_path(self, tmp_path: Path):
        """scan_folder accepts both Path objects and plain strings."""
        (tmp_path / "doc.pdf").write_bytes(b"fake")

        result = scan_folder(str(tmp_path))

        assert len(result.files) == 1

    def test_type_counts(self, tmp_path: Path):
        """type_counts property groups files by detected type."""
        (tmp_path / "a.pdf").write_bytes(b"fake")
        (tmp_path / "b.pdf").write_bytes(b"fake")
        (tmp_path / "c.xlsx").write_bytes(b"fake")
        (tmp_path / "d.txt").write_text("hello")

        result = scan_folder(tmp_path)

        counts = result.type_counts
        assert counts[FileType.PDF] == 2
        assert counts[FileType.XLSX] == 1
        assert counts[FileType.UNKNOWN] == 1


# ------------------------------------------------------------------
# ScanResult.summary
# ------------------------------------------------------------------


class TestScanResultSummary:
    """Tests for the human-readable summary output."""

    def test_summary_contains_key_info(self, tmp_path: Path):
        """The summary includes file counts and type breakdown."""
        (tmp_path / "a.pdf").write_bytes(b"fake")
        (tmp_path / "b.xlsx").write_bytes(b"fake")
        (tmp_path / "c.txt").write_text("hello")

        result = scan_folder(tmp_path)
        summary = result.summary()

        assert "Total files: 3" in summary
        assert "Supported: 2" in summary
        assert "Unsupported: 1" in summary
        assert "pdf" in summary
        assert "xlsx" in summary

    def test_summary_empty_folder(self, tmp_path: Path):
        """Summary works for an empty folder."""
        result = scan_folder(tmp_path)
        summary = result.summary()

        assert "Total files: 0" in summary
        assert "Supported: 0" in summary


# ------------------------------------------------------------------
# _should_skip
# ------------------------------------------------------------------


class TestShouldSkip:
    """Tests for the file-skipping logic."""

    def test_skip_ds_store(self, tmp_path: Path):
        """macOS .DS_Store files are always skipped."""
        path = tmp_path / ".DS_Store"
        path.touch()
        assert _should_skip(path, tmp_path) is True

    def test_skip_thumbs_db(self, tmp_path: Path):
        """Windows Thumbs.db files are always skipped."""
        path = tmp_path / "Thumbs.db"
        path.touch()
        assert _should_skip(path, tmp_path) is True

    def test_skip_files_in_pycache(self, tmp_path: Path):
        """Files inside __pycache__ are skipped."""
        cache = tmp_path / "__pycache__"
        cache.mkdir()
        path = cache / "something.pyc"
        path.touch()
        assert _should_skip(path, tmp_path) is True

    def test_skip_files_in_git_dir(self, tmp_path: Path):
        """Files inside .git are skipped."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        path = git_dir / "HEAD"
        path.touch()
        assert _should_skip(path, tmp_path) is True

    def test_normal_file_not_skipped(self, tmp_path: Path):
        """Regular files are not skipped."""
        path = tmp_path / "report.pdf"
        path.touch()
        assert _should_skip(path, tmp_path) is False

    def test_hidden_file_with_known_extension_not_skipped(
        self, tmp_path: Path
    ):
        """Hidden files with recognized extensions are kept."""
        path = tmp_path / ".hidden_report.pdf"
        path.touch()
        assert _should_skip(path, tmp_path) is False

    def test_hidden_file_unknown_extension_skipped(self, tmp_path: Path):
        """Hidden files with unknown extensions are skipped."""
        path = tmp_path / ".env"
        path.touch()
        assert _should_skip(path, tmp_path) is True


# ------------------------------------------------------------------
# Integration test with the example opportunity folder structure
# ------------------------------------------------------------------


class TestRealWorldStructure:
    """Tests that mimic the structure of a real broker package."""

    def test_mixed_file_types(self, tmp_path: Path):
        """A folder mimicking a real broker package is scanned correctly."""
        # Create files matching the Pioneer Park example structure.
        (tmp_path / "0a. Datanovax Teaser Part I ext.pdf").write_bytes(
            b"fake"
        )
        (tmp_path / "0b. Datanovax Teaser part II.pdf").write_bytes(b"fake")
        (tmp_path / "0c. DN Pic.jpg").write_bytes(b"fake")
        (tmp_path / "0d. DN Carrier Matrix.xlsx").write_bytes(b"fake")
        (tmp_path / "17. DataNovaX Pioneer Park  Pro Forma.xlsb").write_bytes(
            b"fake"
        )
        (tmp_path / ".DS_Store").write_bytes(b"\x00")

        result = scan_folder(tmp_path)

        # .DS_Store should be excluded.
        assert len(result.files) == 5
        assert all(e.converter is not None for e in result.files)

        counts = result.type_counts
        assert counts.get(FileType.PDF, 0) == 2
        assert counts.get(FileType.IMAGE_JPG, 0) == 1
        assert counts.get(FileType.XLSX, 0) == 1
        assert counts.get(FileType.XLSB, 0) == 1

    def test_nested_subfolders(self, tmp_path: Path):
        """Broker packages with subdirectories are fully scanned."""
        phase1 = tmp_path / "Phase 1 Docs"
        phase1.mkdir()
        (phase1 / "connectivity.pdf").write_bytes(b"fake")
        (phase1 / "power.pdf").write_bytes(b"fake")

        phase2 = tmp_path / "Phase 2 (Expansion)"
        phase2.mkdir()
        (phase2 / "layout.pptx").write_bytes(b"fake")

        result = scan_folder(tmp_path)

        assert len(result.files) == 3
        assert len(result.supported) == 3
