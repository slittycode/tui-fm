"""Disk usage analysis and visualization service."""
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass
from collections import defaultdict
import time


class FileInfo(NamedTuple):
    """Information about a file for disk usage analysis."""
    path: Path
    size: int
    is_dir: bool
    file_type: str


class DirectoryStats(NamedTuple):
    """Statistics for a directory."""
    path: Path
    total_size: int
    file_count: int
    dir_count: int
    largest_file: Optional[Path]
    file_types: Dict[str, int]


@dataclass
class DiskUsageSummary:
    """Summary of disk usage for a path."""
    path: Path
    total_size: int
    total_files: int
    total_dirs: int
    largest_files: List[Tuple[Path, int]]
    file_type_distribution: Dict[str, int]
    subdirectory_sizes: Dict[str, int]
    analyzed_at: float


class DiskUsageService:
    """Service for analyzing and visualizing disk usage."""
    
    def __init__(self, cache_timeout: int = 300) -> None:
        """Initialize disk usage service.
        
        Args:
            cache_timeout: Cache timeout in seconds for directory analysis.
        """
        self.cache_timeout = cache_timeout
        self._cache: Dict[str, Tuple[float, DiskUsageSummary]] = {}
        
    def get_disk_usage(self, path: Path) -> Tuple[int, int, int]:
        """Get disk usage statistics for a path.
        
        Args:
            path: Path to analyze.
            
        Returns:
            Tuple of (total, used, free) bytes.
        """
        try:
            usage = shutil.disk_usage(path)
            return (usage.total, usage.used, usage.free)
        except (OSError, PermissionError):
            return (0, 0, 0)
    
    def analyze_directory(self, path: Path, max_depth: int = 3) -> DiskUsageSummary:
        """Analyze disk usage for a directory.
        
        Args:
            path: Directory path to analyze.
            max_depth: Maximum depth to analyze.
            
        Returns:
            DiskUsageSummary with analysis results.
        """
        # Check cache first
        cache_key = f"{path}:{max_depth}"
        current_time = time.time()
        
        if cache_key in self._cache:
            cached_time, cached_result = self._cache[cache_key]
            if current_time - cached_time < self.cache_timeout:
                return cached_result
        
        if not path.exists() or not path.is_dir():
            return DiskUsageSummary(
                path=path,
                total_size=0,
                total_files=0,
                total_dirs=0,
                largest_files=[],
                file_type_distribution={},
                subdirectory_sizes={},
                analyzed_at=current_time
            )
        
        total_size = 0
        total_files = 0
        total_dirs = 0
        largest_files = []
        file_type_distribution = defaultdict(int)
        subdirectory_sizes = defaultdict(int)
        
        try:
            for item in self._scan_directory(path, max_depth):
                if item.is_dir:
                    total_dirs += 1
                    # For directories, we'll count their contents separately
                    if item.path.parent == path:  # Direct subdirectory
                        subdir_size = self._get_directory_size(item.path, max_depth - 1)
                        subdirectory_sizes[item.path.name] = subdir_size
                        total_size += subdir_size
                else:
                    total_files += 1
                    total_size += item.size
                    file_type = item.file_type.lower()
                    file_type_distribution[file_type] += item.size
                    
                    # Track largest files
                    largest_files.append((item.path, item.size))
                    if len(largest_files) > 10:  # Keep only top 10
                        largest_files.sort(key=lambda x: x[1], reverse=True)
                        largest_files = largest_files[:10]
        
        except (PermissionError, OSError):
            # Handle permission errors gracefully
            pass
        
        # Sort largest files by size
        largest_files.sort(key=lambda x: x[1], reverse=True)
        
        summary = DiskUsageSummary(
            path=path,
            total_size=total_size,
            total_files=total_files,
            total_dirs=total_dirs,
            largest_files=largest_files,
            file_type_distribution=dict(file_type_distribution),
            subdirectory_sizes=dict(subdirectory_sizes),
            analyzed_at=current_time
        )
        
        # Cache the result
        self._cache[cache_key] = (current_time, summary)
        
        return summary
    
    def _scan_directory(self, path: Path, max_depth: int, current_depth: int = 0) -> List[FileInfo]:
        """Scan directory and return file information.
        
        Args:
            path: Directory path to scan.
            max_depth: Maximum depth to scan.
            current_depth: Current scanning depth.
            
        Returns:
            List of FileInfo objects.
        """
        files = []
        
        try:
            for item in path.iterdir():
                try:
                    if item.is_dir():
                        files.append(FileInfo(item, 0, True, "directory"))
                        if current_depth < max_depth:
                            files.extend(self._scan_directory(item, max_depth, current_depth + 1))
                    else:
                        size = item.stat().st_size
                        file_type = item.suffix or "no_extension"
                        files.append(FileInfo(item, size, False, file_type))
                except (OSError, PermissionError):
                    # Skip files we can't access
                    continue
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass
        
        return files
    
    def _get_directory_size(self, path: Path, max_depth: int) -> int:
        """Get total size of a directory.
        
        Args:
            path: Directory path.
            max_depth: Maximum depth to analyze.
            
        Returns:
            Total size in bytes.
        """
        total_size = 0
        
        try:
            for item in path.rglob("*") if max_depth > 0 else path.iterdir():
                if max_depth == 0 and item.is_dir():
                    continue
                    
                try:
                    if item.is_file():
                        total_size += item.stat().st_size
                except (OSError, PermissionError):
                    continue
        except (PermissionError, OSError):
            pass
        
        return total_size
    
    def find_large_files(self, path: Path, min_size_mb: int = 10, max_results: int = 20) -> List[Tuple[Path, int]]:
        """Find large files in a directory tree.
        
        Args:
            path: Directory path to search.
            min_size_mb: Minimum file size in MB.
            max_results: Maximum number of results to return.
            
        Returns:
            List of (path, size) tuples sorted by size.
        """
        min_size_bytes = min_size_mb * 1024 * 1024
        large_files = []
        
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    try:
                        size = item.stat().st_size
                        if size >= min_size_bytes:
                            large_files.append((item, size))
                            
                            # Keep only the largest files
                            if len(large_files) > max_results:
                                large_files.sort(key=lambda x: x[1], reverse=True)
                                large_files = large_files[:max_results]
                    except (OSError, PermissionError):
                        continue
        except (PermissionError, OSError):
            pass
        
        large_files.sort(key=lambda x: x[1], reverse=True)
        return large_files
    
    def get_file_type_breakdown(self, path: Path) -> Dict[str, Tuple[int, int, float]]:
        """Get breakdown of file types in a directory.
        
        Args:
            path: Directory path to analyze.
            
        Returns:
            Dict mapping file types to (count, total_size, percentage).
        """
        summary = self.analyze_directory(path, max_depth=1)
        total_size = summary.total_size
        
        if total_size == 0:
            return {}
        
        breakdown = {}
        file_counts = defaultdict(int)
        
        # Count files by type
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    try:
                        file_type = item.suffix.lower() or "no_extension"
                        file_counts[file_type] += 1
                    except (OSError, PermissionError):
                        continue
        except (PermissionError, OSError):
            pass
        
        # Combine size and count information
        for file_type, size in summary.file_type_distribution.items():
            count = file_counts.get(file_type, 0)
            percentage = (size / total_size) * 100 if total_size > 0 else 0
            breakdown[file_type] = (count, size, percentage)
        
        return breakdown
    
    def format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format.
        
        Args:
            size_bytes: Size in bytes.
            
        Returns:
            Formatted size string.
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    def get_disk_space_percentage(self, path: Path) -> Tuple[float, float]:
        """Get disk space usage percentages.
        
        Args:
            path: Path to check disk usage for.
            
        Returns:
            Tuple of (used_percentage, free_percentage).
        """
        total, used, free = self.get_disk_usage(path)
        
        if total == 0:
            return (0.0, 100.0)
        
        used_percentage = (used / total) * 100
        free_percentage = (free / total) * 100
        
        return (used_percentage, free_percentage)
    
    def clear_cache(self) -> None:
        """Clear the analysis cache."""
        self._cache.clear()
    
    def get_cache_info(self) -> Dict[str, int]:
        """Get information about the cache.
        
        Returns:
            Dictionary with cache statistics.
        """
        return {
            "cached_entries": len(self._cache),
            "cache_timeout": self.cache_timeout
        }
