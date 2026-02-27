"""Tests for FilterableDirectoryTree."""
from pathlib import Path

from filterable_tree import FilterableDirectoryTree


class TestSetFilterQuery:
    """Tests for the set_filter_query method."""

    def test_set_query(self, sample_files: Path) -> None:
        """Should set filter query."""
        tree = FilterableDirectoryTree(str(sample_files))
        changed = tree.set_filter_query("test")
        assert changed is True
        assert tree.filter_query == "test"

    def test_set_same_query(self, sample_files: Path) -> None:
        """Should return False when setting same query."""
        tree = FilterableDirectoryTree(str(sample_files))
        tree.set_filter_query("test")
        changed = tree.set_filter_query("test")
        assert changed is False

    def test_clear_query(self, sample_files: Path) -> None:
        """Should clear filter query."""
        tree = FilterableDirectoryTree(str(sample_files))
        tree.set_filter_query("test")
        changed = tree.set_filter_query("")
        assert changed is True
        assert tree.filter_query == ""

    def test_case_normalized(self, sample_files: Path) -> None:
        """Should normalize query to lowercase."""
        tree = FilterableDirectoryTree(str(sample_files))
        tree.set_filter_query("TEST")
        assert tree.filter_query == "test"


class TestFilterPaths:
    """Tests for the filter_paths method."""

    def test_no_filter_returns_all(self, sample_files: Path) -> None:
        """Should return all paths when no filter."""
        tree = FilterableDirectoryTree(str(sample_files))
        paths = list(sample_files.iterdir())
        result = tree.filter_paths(paths)
        assert len(result) == len(paths)

    def test_filter_matches_files(self, sample_files: Path) -> None:
        """Should filter files by name."""
        tree = FilterableDirectoryTree(str(sample_files))
        tree.set_filter_query("file1")
        paths = list(sample_files.iterdir())
        result = tree.filter_paths(paths)
        assert len(result) == 1
        assert result[0].name == "file1.txt"

    def test_filter_matches_directories(self, sample_files: Path) -> None:
        """Should filter directories by name."""
        tree = FilterableDirectoryTree(str(sample_files))
        tree.set_filter_query("subdir")
        paths = list(sample_files.iterdir())
        result = tree.filter_paths(paths)
        assert len(result) == 1
        assert result[0].name == "subdir"

    def test_filter_matches_nested(self, sample_files: Path) -> None:
        """Should include directories containing matches."""
        tree = FilterableDirectoryTree(str(sample_files))
        tree.set_filter_query("nested")
        paths = list(sample_files.iterdir())
        result = tree.filter_paths(paths)
        # subdir should be included because it contains nested_file.txt
        assert any(p.name == "subdir" for p in result)

    def test_filter_no_matches(self, sample_files: Path) -> None:
        """Should return empty when no matches."""
        tree = FilterableDirectoryTree(str(sample_files))
        tree.set_filter_query("nonexistent_xyz_123")
        paths = list(sample_files.iterdir())
        result = tree.filter_paths(paths)
        assert len(result) == 0


class TestDirectoryHasMatch:
    """Tests for the _directory_has_match method."""

    def test_match_in_root(self, sample_files: Path) -> None:
        """Should find match in root directory."""
        tree = FilterableDirectoryTree(str(sample_files))
        has_match = tree._directory_has_match(sample_files, "file1")
        assert has_match is True

    def test_match_in_subdirectory(self, sample_files: Path) -> None:
        """Should find match in subdirectory."""
        tree = FilterableDirectoryTree(str(sample_files))
        has_match = tree._directory_has_match(sample_files, "nested")
        assert has_match is True

    def test_no_match(self, sample_files: Path) -> None:
        """Should return False when no match."""
        tree = FilterableDirectoryTree(str(sample_files))
        has_match = tree._directory_has_match(sample_files, "nonexistent_xyz")
        assert has_match is False

    def test_respects_max_entries(self, sample_files: Path) -> None:
        """Should respect max_entries limit."""
        tree = FilterableDirectoryTree(str(sample_files))
        # With max_entries=1, should return True (keeps uncertain directories)
        has_match = tree._directory_has_match(sample_files, "test", max_entries=1)
        assert has_match is True  # Returns True to avoid false negatives
