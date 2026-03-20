"""Filterable directory tree widget."""
import time
from pathlib import Path
from typing import Iterable, Optional

from rich.text import Text
from textual.widgets import DirectoryTree

from git_service import GitService, GitStatus
from icon_manager import IconManager


class FilterableDirectoryTree(DirectoryTree):
    """DirectoryTree that filters visible paths by an active query."""

    def __init__(self, path: str, **kwargs) -> None:
        """Initialize the filterable directory tree.

        Args:
            path: Root path for the tree.
            **kwargs: Additional arguments for DirectoryTree.
        """
        super().__init__(path, **kwargs)
        self.filter_query = ""
        self.git_service = GitService(Path(path))
        self.icon_manager = IconManager()
        self._git_status_cache = {}
        self._cache_ttl = 5.0  # Cache for 5 seconds

    def set_filter_query(self, query: str) -> bool:
        """Set the filter query.

        Args:
            query: Filter query string.

        Returns:
            True if the query changed, False otherwise.
        """
        normalized = query.strip().lower()
        if normalized == self.filter_query:
            return False
        self.filter_query = normalized
        return True

    def filter_paths(self, paths: Iterable[Path]) -> list[Path]:
        """Filter paths based on the active query.

        Args:
            paths: Iterable of paths to filter.

        Returns:
            Filtered list of paths.
        """
        query = self.filter_query
        if not query:
            return list(paths)

        filtered = []
        for path in paths:
            try:
                if query in path.name.lower():
                    filtered.append(path)
                    continue

                if path.is_dir() and self._directory_has_match(path, query):
                    filtered.append(path)
            except OSError:
                continue
        return filtered

    def _directory_has_match(
        self,
        directory: Path,
        query: str,
        max_entries: int = 500,
    ) -> bool:
        """Check if a directory contains a matching entry.
        
        Args:
            directory: Directory to search.
            query: Filter query string.
            max_entries: Maximum entries to scan before returning True.
            
        Returns:
            True if a match is found or uncertain (due to max_entries).
        """
        stack: list[Path] = [directory]
        seen = 0

        while stack:
            current = stack.pop()
            try:
                for entry in current.iterdir():
                    seen += 1
                    if seen > max_entries:
                        # Keep uncertain directories to avoid false negatives.
                        return True

                    try:
                        name = entry.name.lower()
                        if query in name:
                            return True

                        if entry.is_dir() and not entry.is_symlink():
                            stack.append(entry)
                    except OSError:
                        continue
            except (PermissionError, OSError):
                continue

        return False

    def _get_git_status(self, file_path: str) -> Optional[GitStatus]:
        """Get Git status for a file with caching.
        
        Args:
            file_path: Relative path to the file.
            
        Returns:
            Git status if available, None otherwise.
        """
        current_time = time.time()
        cache_key = file_path
        
        # Check cache
        if cache_key in self._git_status_cache:
            cached_time, cached_status = self._git_status_cache[cache_key]
            if current_time - cached_time < self._cache_ttl:
                return cached_status
        
        # Get fresh status
        status = self.git_service.get_file_status(file_path)
        
        # Cache the result
        self._git_status_cache[cache_key] = (current_time, status)
        
        return status

    def _clear_expired_cache(self) -> None:
        """Clear expired entries from the Git status cache."""
        current_time = time.time()
        expired_keys = []
        
        for cache_key, (cached_time, _) in self._git_status_cache.items():
            if current_time - cached_time >= self._cache_ttl:
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del self._git_status_cache[key]

    def _render_label_with_git_status(self, path: Path) -> Text:
        """Render a label with icon and Git status indicator.
        
        Args:
            path: Path to render label for.
            
        Returns:
            Text object with icon, Git status indicator, and filename.
        """
        # Get the relative path from the tree root
        try:
            relative_path = str(path.relative_to(Path(self.path)))
        except ValueError:
            # Path is not relative to tree root, use name only
            relative_path = path.name
        
        # Get Git status
        git_status = self._get_git_status(relative_path)
        
        # Create the label
        label = Text()
        
        # Add file/directory icon
        if path.is_dir():
            # Check if directory is a Git repository
            is_git_repo = (path / ".git").exists() or git_status is not None
            icon = self.icon_manager.get_directory_icon(path, is_git_repo)
        else:
            icon = self.icon_manager.get_file_icon(path)
        
        if icon:
            label.append(f"{icon} ", style="default")
        
        # Add Git status indicator if available
        if git_status and git_status != GitStatus.CLEAN:
            symbol = self.git_service.get_status_symbol(git_status)
            color = self.git_service.get_status_color(git_status)
            
            if symbol and color:
                label.append(f"{symbol} ", style=color)
        
        # Add the file/directory name
        label.append(path.name)
        
        return label

    def render_label(self, node, base_style, style) -> Text:
        """Render labels with Git status indicators using Textual's current API."""
        # Clear expired cache entries periodically
        if len(self._git_status_cache) > 100:  # Clear cache if it gets too large
            self._clear_expired_cache()

        path = node.data.path
        label = self._render_label_with_git_status(path)
        label.stylize(style)
        return label
