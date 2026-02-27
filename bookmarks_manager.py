"""Bookmarks management for the File Manager."""
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class Bookmark:
    """Represents a bookmarked directory."""
    path: str
    name: str
    created_at: str
    updated_at: str

    @classmethod
    def create(cls, path: Path, name: Optional[str] = None) -> "Bookmark":
        """Create a new bookmark.
        
        Args:
            path: The directory path to bookmark.
            name: Optional display name. Defaults to directory name.
            
        Returns:
            A new Bookmark instance.
        """
        now = datetime.now().isoformat()
        return cls(
            path=str(path.expanduser()),
            name=name or path.name or str(path),
            created_at=now,
            updated_at=now,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Bookmark":
        """Create from dictionary."""
        return cls(**data)


class BookmarksManager:
    """Manages directory bookmarks."""

    def __init__(self, bookmarks_path: Optional[Path] = None) -> None:
        """Initialize the bookmarks manager.
        
        Args:
            bookmarks_path: Path to the bookmarks file. Defaults to ~/.tui_fm_bookmarks.json
        """
        if bookmarks_path is None:
            self.bookmarks_path = Path.home() / ".tui_fm_bookmarks.json"
        else:
            self.bookmarks_path = bookmarks_path
        self._bookmarks: list[Bookmark] = []
        self.load()

    def load(self) -> None:
        """Load bookmarks from file."""
        if self.bookmarks_path.exists():
            try:
                with open(self.bookmarks_path, encoding="utf-8") as f:
                    data = json.load(f)
                    self._bookmarks = [Bookmark.from_dict(b) for b in data]
            except (OSError, json.JSONDecodeError):
                self._bookmarks = []
        else:
            self._bookmarks = []

    def save(self) -> None:
        """Save bookmarks to file."""
        try:
            with open(self.bookmarks_path, "w", encoding="utf-8") as f:
                json.dump([b.to_dict() for b in self._bookmarks], f, indent=2)
        except OSError as e:
            raise RuntimeError(f"Failed to save bookmarks: {e}") from e

    def add(self, path: Path, name: Optional[str] = None) -> Bookmark:
        """Add a bookmark.
        
        Args:
            path: The directory path to bookmark.
            name: Optional display name.
            
        Returns:
            The created bookmark.
            
        Raises:
            ValueError: If path doesn't exist or isn't a directory.
            ValueError: If bookmark already exists.
        """
        path = path.expanduser()

        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        # Check for duplicate
        for bookmark in self._bookmarks:
            if Path(bookmark.path) == path:
                raise ValueError(f"Bookmark already exists: {path}")

        bookmark = Bookmark.create(path, name)
        self._bookmarks.append(bookmark)
        self.save()
        return bookmark

    def remove(self, path: Path) -> bool:
        """Remove a bookmark.
        
        Args:
            path: The directory path to remove.
            
        Returns:
            True if removed, False if not found.
        """
        path = path.expanduser()
        for i, bookmark in enumerate(self._bookmarks):
            if Path(bookmark.path) == path:
                self._bookmarks.pop(i)
                self.save()
                return True
        return False

    def get(self, path: Path) -> Optional[Bookmark]:
        """Get a bookmark by path.
        
        Args:
            path: The directory path to look up.
            
        Returns:
            The bookmark or None if not found.
        """
        path = path.expanduser()
        for bookmark in self._bookmarks:
            if Path(bookmark.path) == path:
                return bookmark
        return None

    def list_all(self) -> list[Bookmark]:
        """List all bookmarks.
        
        Returns:
            List of all bookmarks.
        """
        return self._bookmarks.copy()

    def update_name(self, path: Path, name: str) -> Optional[Bookmark]:
        """Update a bookmark's name.
        
        Args:
            path: The directory path.
            name: The new display name.
            
        Returns:
            The updated bookmark or None if not found.
        """
        path = path.expanduser()
        for bookmark in self._bookmarks:
            if Path(bookmark.path) == path:
                bookmark.name = name
                bookmark.updated_at = datetime.now().isoformat()
                self.save()
                return bookmark
        return None

    def exists(self, path: Path) -> bool:
        """Check if a bookmark exists.
        
        Args:
            path: The directory path to check.
            
        Returns:
            True if bookmarked, False otherwise.
        """
        return self.get(path) is not None

    def count(self) -> int:
        """Get the number of bookmarks."""
        return len(self._bookmarks)

    def clear(self) -> None:
        """Clear all bookmarks."""
        self._bookmarks = []
        self.save()

    def __len__(self) -> int:
        return len(self._bookmarks)

    def __iter__(self):
        return iter(self._bookmarks)

    def __repr__(self) -> str:
        return f"BookmarksManager(count={len(self._bookmarks)}, path={self.bookmarks_path})"
