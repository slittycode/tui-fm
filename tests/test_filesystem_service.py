"""Tests for FileSystemService."""
from pathlib import Path

import pytest

from filesystem_service import FileSystemService


class TestApplyNameFilter:
    """Tests for the apply_name_filter method."""

    def test_empty_query_returns_all(self, sample_files: Path) -> None:
        """Empty query should return all items."""
        items = list(sample_files.iterdir())
        result = FileSystemService.apply_name_filter(items, "")
        assert len(result) == len(items)

    def test_whitespace_query_returns_all(self, sample_files: Path) -> None:
        """Whitespace-only query should return all items."""
        items = list(sample_files.iterdir())
        result = FileSystemService.apply_name_filter(items, "   ")
        assert len(result) == len(items)

    def test_case_insensitive_match(self, sample_files: Path) -> None:
        """Filter should be case-insensitive."""
        items = list(sample_files.iterdir())
        result = FileSystemService.apply_name_filter(items, "FILE")
        assert len(result) == 3  # file1.txt, file2.py, file3.json

    def test_partial_match(self, sample_files: Path) -> None:
        """Filter should match partial names."""
        items = list(sample_files.iterdir())
        result = FileSystemService.apply_name_filter(items, "file2")
        assert len(result) == 1
        assert result[0].name == "file2.py"

    def test_extension_match(self, sample_files: Path) -> None:
        """Filter should match extensions."""
        items = list(sample_files.iterdir())
        result = FileSystemService.apply_name_filter(items, ".txt")
        assert len(result) == 1
        assert result[0].name == "file1.txt"

    def test_no_matches(self, sample_files: Path) -> None:
        """Filter with no matches should return empty list."""
        items = list(sample_files.iterdir())
        result = FileSystemService.apply_name_filter(items, "nonexistent")
        assert len(result) == 0


class TestResolveDestinationPath:
    """Tests for the resolve_destination_path method."""

    def test_absolute_path(self, temp_dir: Path) -> None:
        """Should handle absolute paths."""
        source = temp_dir / "source.txt"
        source.write_text("test")
        dest_dir = temp_dir / "dest"
        dest_dir.mkdir()

        result = FileSystemService.resolve_destination_path(source, str(dest_dir))
        assert result == dest_dir / "source.txt"

    def test_relative_path(self, temp_dir: Path) -> None:
        """Should handle relative paths."""
        source = temp_dir / "source.txt"
        source.write_text("test")
        dest_dir = temp_dir / "dest"
        dest_dir.mkdir()

        result = FileSystemService.resolve_destination_path(source, "dest")
        assert result == dest_dir / "source.txt"

    def test_explicit_filename(self, temp_dir: Path) -> None:
        """Should handle explicit destination filename."""
        source = temp_dir / "source.txt"
        source.write_text("test")
        dest = temp_dir / "new_name.txt"

        result = FileSystemService.resolve_destination_path(source, str(dest))
        assert result == dest

    def test_expanded_user(self, temp_dir: Path) -> None:
        """Should expand ~ in paths."""
        source = temp_dir / "source.txt"
        source.write_text("test")

        result = FileSystemService.resolve_destination_path(source, "~/test")
        assert result.home() == Path.home()


class TestCopyPath:
    """Tests for the copy_path method."""

    def test_copy_file(self, temp_dir: Path) -> None:
        """Should copy a file."""
        source = temp_dir / "source.txt"
        source.write_text("test content")
        dest = temp_dir / "dest.txt"

        result = FileSystemService.copy_path(source, dest)
        assert result == dest
        assert dest.exists()
        assert dest.read_text() == "test content"

    def test_copy_directory(self, temp_dir: Path) -> None:
        """Should copy a directory."""
        source = temp_dir / "source_dir"
        source.mkdir()
        (source / "file.txt").write_text("nested")
        dest = temp_dir / "dest_dir"

        result = FileSystemService.copy_path(source, dest)
        assert result == dest
        assert dest.exists()
        assert (dest / "file.txt").read_text() == "nested"

    def test_copy_destination_exists(self, temp_dir: Path) -> None:
        """Should raise error if destination exists."""
        source = temp_dir / "source.txt"
        source.write_text("test")
        dest = temp_dir / "dest.txt"
        dest.write_text("existing")

        with pytest.raises(FileExistsError):
            FileSystemService.copy_path(source, dest)

    def test_copy_parent_not_exists(self, temp_dir: Path) -> None:
        """Should raise error if parent directory doesn't exist."""
        source = temp_dir / "source.txt"
        source.write_text("test")
        dest = temp_dir / "nonexistent" / "dest.txt"

        with pytest.raises(FileNotFoundError):
            FileSystemService.copy_path(source, dest)


class TestMovePath:
    """Tests for the move_path method."""

    def test_move_file(self, temp_dir: Path) -> None:
        """Should move a file."""
        source = temp_dir / "source.txt"
        source.write_text("test content")
        dest = temp_dir / "dest.txt"

        result = FileSystemService.move_path(source, dest)
        assert result == dest
        assert dest.exists()
        assert not source.exists()
        assert dest.read_text() == "test content"

    def test_move_directory(self, temp_dir: Path) -> None:
        """Should move a directory."""
        source = temp_dir / "source_dir"
        source.mkdir()
        (source / "file.txt").write_text("nested")
        dest = temp_dir / "dest_dir"

        result = FileSystemService.move_path(source, dest)
        assert result == dest
        assert dest.exists()
        assert not source.exists()
        assert (dest / "file.txt").read_text() == "nested"

    def test_move_destination_exists(self, temp_dir: Path) -> None:
        """Should raise error if destination exists."""
        source = temp_dir / "source.txt"
        source.write_text("test")
        dest = temp_dir / "dest.txt"
        dest.write_text("existing")

        with pytest.raises(FileExistsError):
            FileSystemService.move_path(source, dest)


class TestRenamePath:
    """Tests for the rename_path method."""

    def test_rename_file(self, temp_dir: Path) -> None:
        """Should rename a file."""
        source = temp_dir / "old_name.txt"
        source.write_text("test")

        result = FileSystemService.rename_path(source, "new_name.txt")
        assert result.name == "new_name.txt"
        assert not source.exists()
        assert result.exists()

    def test_rename_empty_name(self, temp_dir: Path) -> None:
        """Should raise error for empty name."""
        source = temp_dir / "file.txt"
        source.write_text("test")

        with pytest.raises(ValueError):
            FileSystemService.rename_path(source, "")

    def test_rename_path_in_name(self, temp_dir: Path) -> None:
        """Should raise error for path in name."""
        source = temp_dir / "file.txt"
        source.write_text("test")

        with pytest.raises(ValueError):
            FileSystemService.rename_path(source, "subdir/new.txt")

    def test_rename_destination_exists(self, temp_dir: Path) -> None:
        """Should raise error if destination exists."""
        source = temp_dir / "source.txt"
        source.write_text("test")
        existing = temp_dir / "existing.txt"
        existing.write_text("existing")

        with pytest.raises(FileExistsError):
            FileSystemService.rename_path(source, "existing.txt")


class TestDeletePath:
    """Tests for the delete_path method."""

    def test_delete_file(self, temp_dir: Path) -> None:
        """Should delete a file."""
        target = temp_dir / "file.txt"
        target.write_text("test")

        FileSystemService.delete_path(target)
        assert not target.exists()

    def test_delete_directory(self, temp_dir: Path) -> None:
        """Should delete a directory and its contents."""
        target = temp_dir / "dir"
        target.mkdir()
        (target / "file.txt").write_text("nested")

        FileSystemService.delete_path(target)
        assert not target.exists()

    def test_delete_nonexistent(self, temp_dir: Path) -> None:
        """Should raise error for nonexistent path."""
        target = temp_dir / "nonexistent.txt"

        with pytest.raises(FileNotFoundError):
            FileSystemService.delete_path(target)
