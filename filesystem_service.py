"""Filesystem service for file operations."""
import shutil
from pathlib import Path
from typing import TypeVar

T = TypeVar("T")


class FileSystemService:
    """Pure filesystem and filtering helpers for the TUI app."""

    @staticmethod
    def apply_name_filter(items: list[T], query: str) -> list[T]:
        """Filter items by name (case-insensitive).
        
        Args:
            items: List of path-like items to filter.
            query: Search query string.
            
        Returns:
            Filtered list of items matching the query.
        """
        normalized = query.strip().lower()
        if not normalized:
            return list(items)
        return [item for item in items if normalized in item.name.lower()]  # type: ignore[attr-defined]

    @staticmethod
    def resolve_destination_path(source: Path, target_text: str) -> Path:
        """Resolve a destination path from user-provided text.
        
        Args:
            source: Source path for relative resolution.
            target_text: User-provided destination path text.
            
        Returns:
            Resolved destination Path.
        """
        target = Path(target_text.strip()).expanduser()
        if not target.is_absolute():
            target = source.parent / target
        if target.exists() and target.is_dir():
            target = target / source.name
        return target

    @staticmethod
    def copy_path(source: Path, destination: Path) -> Path:
        """Copy a file or directory to a destination.
        
        Args:
            source: Source path to copy.
            destination: Destination path.
            
        Returns:
            Destination path.
            
        Raises:
            FileExistsError: If destination already exists.
            FileNotFoundError: If destination parent doesn't exist.
        """
        if destination.exists():
            raise FileExistsError(f"Destination already exists: {destination}")
        if not destination.parent.exists():
            raise FileNotFoundError(f"Destination directory not found: {destination.parent}")

        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
        return destination

    @staticmethod
    def move_path(source: Path, destination: Path) -> Path:
        """Move a file or directory to a destination.
        
        Args:
            source: Source path to move.
            destination: Destination path.
            
        Returns:
            Destination path.
            
        Raises:
            FileExistsError: If destination already exists.
            FileNotFoundError: If destination parent doesn't exist.
        """
        if destination.exists():
            raise FileExistsError(f"Destination already exists: {destination}")
        if not destination.parent.exists():
            raise FileNotFoundError(f"Destination directory not found: {destination.parent}")

        moved = shutil.move(str(source), str(destination))
        return Path(moved)

    @staticmethod
    def rename_path(source: Path, new_name: str) -> Path:
        """Rename a file or directory in place.
        
        Args:
            source: Source path to rename.
            new_name: New name for the path.
            
        Returns:
            New path after rename.
            
        Raises:
            ValueError: If new name is empty or contains path separators.
            FileExistsError: If destination already exists.
        """
        normalized_name = new_name.strip()
        if not normalized_name:
            raise ValueError("New name cannot be empty.")
        if "/" in normalized_name or "\\" in normalized_name:
            raise ValueError("Rename expects a name, not a path.")

        destination = source.parent / normalized_name
        if destination.exists():
            raise FileExistsError(f"Destination already exists: {destination}")

        source.rename(destination)
        return destination

    @staticmethod
    def delete_path(target: Path) -> None:
        """Delete a file or directory.
        
        Args:
            target: Path to delete.
            
        Raises:
            FileNotFoundError: If target doesn't exist.
        """
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
