from pathlib import Path
from textual.widgets import DirectoryTree


class FilterableDirectoryTree(DirectoryTree):
    """DirectoryTree that filters visible paths by an active query."""

    def __init__(self, path: str, **kwargs):
        super().__init__(path, **kwargs)
        self.filter_query = ""

    def set_filter_query(self, query: str) -> bool:
        normalized = query.strip().lower()
        if normalized == self.filter_query:
            return False
        self.filter_query = normalized
        return True

    def filter_paths(self, paths):
        query = self.filter_query
        if not query:
            return paths

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

    def _directory_has_match(self, directory: Path, query: str, max_entries: int = 500) -> bool:
        stack = [directory]
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
