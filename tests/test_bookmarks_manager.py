"""Tests for BookmarksManager."""
from pathlib import Path

import pytest

from bookmarks_manager import Bookmark, BookmarksManager


class TestBookmark:
    """Tests for the Bookmark dataclass."""

    def test_create(self, temp_dir: Path) -> None:
        """Should create a bookmark."""
        bookmark = Bookmark.create(temp_dir)

        assert bookmark.path == str(temp_dir)
        assert bookmark.name == temp_dir.name
        assert bookmark.created_at is not None
        assert bookmark.updated_at is not None

    def test_create_with_name(self, temp_dir: Path) -> None:
        """Should create a bookmark with custom name."""
        bookmark = Bookmark.create(temp_dir, name="My Folder")

        assert bookmark.name == "My Folder"

    def test_to_dict(self, temp_dir: Path) -> None:
        """Should convert to dictionary."""
        bookmark = Bookmark.create(temp_dir, name="Test")
        data = bookmark.to_dict()

        assert data["path"] == str(temp_dir)
        assert data["name"] == "Test"

    def test_from_dict(self, temp_dir: Path) -> None:
        """Should create from dictionary."""
        data = {
            "path": str(temp_dir),
            "name": "Test",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        }
        bookmark = Bookmark.from_dict(data)

        assert bookmark.path == str(temp_dir)
        assert bookmark.name == "Test"


class TestBookmarksManager:
    """Tests for the BookmarksManager class."""

    def test_empty_initialization(self, temp_dir: Path) -> None:
        """Should initialize with empty bookmarks."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        assert len(manager) == 0
        assert manager.list_all() == []

    def test_add_bookmark(self, temp_dir: Path) -> None:
        """Should add a bookmark."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        bookmark = manager.add(temp_dir, name="Test Folder")

        assert len(manager) == 1
        assert bookmark.name == "Test Folder"
        assert manager.exists(temp_dir)

    def test_add_nonexistent_path(self, temp_dir: Path) -> None:
        """Should raise error for nonexistent path."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        nonexistent = temp_dir / "does_not_exist"
        with pytest.raises(ValueError, match="does not exist"):
            manager.add(nonexistent)

    def test_add_file_not_directory(self, temp_dir: Path) -> None:
        """Should raise error for file (not directory)."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        file_path = temp_dir / "file.txt"
        file_path.write_text("test")

        with pytest.raises(ValueError, match="not a directory"):
            manager.add(file_path)

    def test_add_duplicate(self, temp_dir: Path) -> None:
        """Should raise error for duplicate bookmark."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        manager.add(temp_dir)

        with pytest.raises(ValueError, match="already exists"):
            manager.add(temp_dir)

    def test_remove_bookmark(self, temp_dir: Path) -> None:
        """Should remove a bookmark."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        manager.add(temp_dir)
        assert len(manager) == 1

        result = manager.remove(temp_dir)

        assert result is True
        assert len(manager) == 0
        assert not manager.exists(temp_dir)

    def test_remove_nonexistent(self, temp_dir: Path) -> None:
        """Should return False for nonexistent bookmark."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        result = manager.remove(temp_dir)

        assert result is False

    def test_get_bookmark(self, temp_dir: Path) -> None:
        """Should get a bookmark by path."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)
        
        manager.add(temp_dir, name="Test")
        retrieved = manager.get(temp_dir)
        
        assert retrieved is not None
        assert retrieved.name == "Test"

    def test_get_nonexistent(self, temp_dir: Path) -> None:
        """Should return None for nonexistent bookmark."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        result = manager.get(temp_dir)

        assert result is None

    def test_list_all(self, temp_dir: Path) -> None:
        """Should list all bookmarks."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        manager.add(dir1, name="First")
        manager.add(dir2, name="Second")

        bookmarks = manager.list_all()

        assert len(bookmarks) == 2
        names = {b.name for b in bookmarks}
        assert names == {"First", "Second"}

    def test_update_name(self, temp_dir: Path) -> None:
        """Should update bookmark name."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        manager.add(temp_dir, name="Old Name")
        updated = manager.update_name(temp_dir, "New Name")

        assert updated is not None
        assert updated.name == "New Name"

        retrieved = manager.get(temp_dir)
        assert retrieved.name == "New Name"

    def test_update_nonexistent(self, temp_dir: Path) -> None:
        """Should return None when updating nonexistent bookmark."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        result = manager.update_name(temp_dir, "New Name")

        assert result is None

    def test_count(self, temp_dir: Path) -> None:
        """Should return bookmark count."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        assert manager.count() == 0

        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        manager.add(dir1)
        manager.add(dir2)

        assert manager.count() == 2

    def test_clear(self, temp_dir: Path) -> None:
        """Should clear all bookmarks."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        dir1 = temp_dir / "dir1"
        dir1.mkdir()
        manager.add(dir1)

        manager.clear()

        assert len(manager) == 0
        assert manager.list_all() == []

    def test_persistence(self, temp_dir: Path) -> None:
        """Should persist bookmarks to file."""
        bookmarks_path = temp_dir / "bookmarks.json"

        # Create and save
        manager1 = BookmarksManager(bookmarks_path)
        dir1 = temp_dir / "dir1"
        dir1.mkdir()
        manager1.add(dir1, name="Persistent")

        # Load from file
        manager2 = BookmarksManager(bookmarks_path)

        assert len(manager2) == 1
        bookmark = manager2.get(dir1)
        assert bookmark is not None
        assert bookmark.name == "Persistent"

    def test_iteration(self, temp_dir: Path) -> None:
        """Should support iteration."""
        bookmarks_path = temp_dir / "bookmarks.json"
        manager = BookmarksManager(bookmarks_path)

        dir1 = temp_dir / "dir1"
        dir2 = temp_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        manager.add(dir1)
        manager.add(dir2)

        paths = [b.path for b in manager]

        assert len(paths) == 2

    def test_load_corrupted_file(self, temp_dir: Path) -> None:
        """Should handle corrupted bookmarks file."""
        bookmarks_path = temp_dir / "bookmarks.json"
        bookmarks_path.write_text("not valid json{{{")

        manager = BookmarksManager(bookmarks_path)

        assert len(manager) == 0
