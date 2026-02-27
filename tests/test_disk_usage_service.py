"""Tests for disk usage service functionality."""
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from disk_usage_service import (
    DiskUsageService,
    DiskUsageSummary,
    FileInfo,
    DirectoryStats
)


class TestDiskUsageService:
    """Test cases for DiskUsageService class."""
    
    def test_service_initialization(self) -> None:
        """Test DiskUsageService initialization."""
        service = DiskUsageService()
        
        assert service.cache_timeout == 300
        assert service._cache == {}
        
        # Test custom cache timeout
        service_custom = DiskUsageService(cache_timeout=600)
        assert service_custom.cache_timeout == 600
    
    def test_get_disk_usage(self) -> None:
        """Test getting disk usage statistics."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            
            total, used, free = service.get_disk_usage(path)
            
            assert isinstance(total, int)
            assert isinstance(used, int)
            assert isinstance(free, int)
            assert total > 0
            assert used >= 0
            assert free >= 0
            assert total >= used + free
    
    def test_get_disk_usage_nonexistent_path(self) -> None:
        """Test disk usage with nonexistent path."""
        service = DiskUsageService()
        
        nonexistent = Path("/nonexistent/path/that/should/not/exist")
        total, used, free = service.get_disk_usage(nonexistent)
        
        assert total == 0
        assert used == 0
        assert free == 0
    
    @patch('shutil.disk_usage')
    def test_get_disk_usage_permission_error(self, mock_disk_usage: Mock) -> None:
        """Test disk usage with permission error."""
        service = DiskUsageService()
        
        mock_disk_usage.side_effect = PermissionError("Access denied")
        
        total, used, free = service.get_disk_usage(Path("/tmp"))
        
        assert total == 0
        assert used == 0
        assert free == 0
    
    def test_analyze_directory_basic(self) -> None:
        """Test basic directory analysis."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            
            # Create test files
            (path / "file1.txt").write_text("Hello World")
            (path / "file2.py").write_text("print('Hello')")
            
            # Create subdirectory
            subdir = path / "subdir"
            subdir.mkdir()
            (subdir / "file3.md").write_text("# Title")
            
            summary = service.analyze_directory(path, max_depth=2)
            
            assert isinstance(summary, DiskUsageSummary)
            assert summary.path == path
            assert summary.total_files == 3
            assert summary.total_dirs >= 1
            assert summary.total_size > 0
            assert len(summary.largest_files) > 0
            assert len(summary.file_type_distribution) > 0
            assert isinstance(summary.analyzed_at, float)
    
    def test_analyze_directory_nonexistent(self) -> None:
        """Test analyzing nonexistent directory."""
        service = DiskUsageService()
        
        nonexistent = Path("/nonexistent/directory")
        summary = service.analyze_directory(nonexistent)
        
        assert summary.path == nonexistent
        assert summary.total_size == 0
        assert summary.total_files == 0
        assert summary.total_dirs == 0
        assert summary.largest_files == []
        assert summary.file_type_distribution == {}
        assert summary.subdirectory_sizes == {}
    
    def test_analyze_directory_file(self) -> None:
        """Test analyzing a file instead of directory."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.txt"
            file_path.write_text("Hello")
            
            summary = service.analyze_directory(file_path)
            
            assert summary.total_size == 0
            assert summary.total_files == 0
            assert summary.total_dirs == 0
    
    def test_analyze_directory_caching(self) -> None:
        """Test directory analysis caching."""
        service = DiskUsageService(cache_timeout=1)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            (path / "test.txt").write_text("Hello")
            
            # First analysis
            summary1 = service.analyze_directory(path)
            first_time = summary1.analyzed_at
            
            # Second analysis should use cache
            summary2 = service.analyze_directory(path)
            assert summary2.analyzed_at == first_time
            
            # Wait for cache to expire
            time.sleep(1.1)
            
            # Third analysis should recompute
            summary3 = service.analyze_directory(path)
            assert summary3.analyzed_at > first_time
    
    def test_find_large_files(self) -> None:
        """Test finding large files."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            
            # Create files of different sizes
            (path / "small.txt").write_text("small")
            (path / "medium.txt").write_text("x" * 1000)  # ~1KB
            (path / "large.txt").write_text("x" * 10000)  # ~10KB
            
            # Find files larger than 500 bytes
            large_files = service.find_large_files(path, min_size_mb=0.0005)  # ~512B
            
            assert len(large_files) >= 2  # medium and large files
            assert all(size >= 1000 for _, size in large_files)
            
            # Should be sorted by size (largest first)
            assert large_files[0][1] >= large_files[1][1]
    
    def test_find_large_files_max_results(self) -> None:
        """Test finding large files with result limit."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            
            # Create many files
            for i in range(25):
                (path / f"file{i}.txt").write_text("x" * 1000)
            
            large_files = service.find_large_files(path, min_size_mb=0.001, max_results=10)
            
            assert len(large_files) <= 10
    
    def test_get_file_type_breakdown(self) -> None:
        """Test file type breakdown analysis."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            
            # Create different file types
            (path / "test.txt").write_text("Hello")
            (path / "script.py").write_text("print('Hello')")
            (path / "data.json").write_text('{}')
            (path / "readme").write_text("README")  # No extension
            
            breakdown = service.get_file_type_breakdown(path)
            
            assert ".txt" in breakdown
            assert ".py" in breakdown
            assert ".json" in breakdown
            assert "no_extension" in breakdown
            
            # Check breakdown structure: (count, size, percentage)
            for file_type, (count, size, percentage) in breakdown.items():
                assert isinstance(count, int)
                assert isinstance(size, int)
                assert isinstance(percentage, float)
                assert count > 0
                assert size > 0
                assert 0 <= percentage <= 100
    
    def test_get_file_type_breakdown_empty(self) -> None:
        """Test file type breakdown with empty directory."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            breakdown = service.get_file_type_breakdown(Path(temp_dir))
            
            assert breakdown == {}
    
    def test_format_size(self) -> None:
        """Test size formatting."""
        service = DiskUsageService()
        
        assert service.format_size(0) == "0 B"
        assert service.format_size(500) == "500.0 B"
        assert service.format_size(1024) == "1.0 KB"
        assert service.format_size(1536) == "1.5 KB"
        assert service.format_size(1048576) == "1.0 MB"
        assert service.format_size(1073741824) == "1.0 GB"
        assert service.format_size(1099511627776) == "1.0 TB"
    
    def test_get_disk_space_percentage(self) -> None:
        """Test disk space percentage calculation."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            
            used_pct, free_pct = service.get_disk_space_percentage(path)
            
            assert isinstance(used_pct, float)
            assert isinstance(free_pct, float)
            assert 0 <= used_pct <= 100
            assert 0 <= free_pct <= 100
            assert abs((used_pct + free_pct) - 100.0) < 0.1  # Should sum to ~100%
    
    def test_get_disk_space_percentage_zero_total(self) -> None:
        """Test disk space percentage with zero total space."""
        service = DiskUsageService()
        
        with patch.object(service, 'get_disk_usage', return_value=(0, 0, 0)):
            used_pct, free_pct = service.get_disk_space_percentage(Path("/tmp"))
            
            assert used_pct == 0.0
            assert free_pct == 100.0
    
    def test_clear_cache(self) -> None:
        """Test cache clearing."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            (path / "test.txt").write_text("Hello")
            
            # Populate cache
            service.analyze_directory(path)
            assert len(service._cache) > 0
            
            # Clear cache
            service.clear_cache()
            assert len(service._cache) == 0
    
    def test_get_cache_info(self) -> None:
        """Test cache information retrieval."""
        service = DiskUsageService(cache_timeout=600)
        
        info = service.get_cache_info()
        
        assert info["cached_entries"] == 0
        assert info["cache_timeout"] == 600
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            (path / "test.txt").write_text("Hello")
            
            # Populate cache
            service.analyze_directory(path)
            
            info = service.get_cache_info()
            assert info["cached_entries"] == 1
    
    def test_scan_directory_permission_error(self) -> None:
        """Test directory scanning with permission errors."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            (path / "accessible.txt").write_text("Hello")
            
            # Mock iterdir to raise permission error
            with patch.object(Path, 'iterdir', side_effect=PermissionError):
                files = service._scan_directory(path, max_depth=1)
                assert files == []
    
    def test_get_directory_size_permission_error(self) -> None:
        """Test directory size calculation with permission error."""
        service = DiskUsageService()
        
        with patch.object(Path, 'rglob', side_effect=PermissionError):
            size = service._get_directory_size(Path("/tmp"), max_depth=1)
            assert size == 0
    
    def test_analyze_directory_with_subdirectories(self) -> None:
        """Test analyzing directory with subdirectories."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            
            # Create nested structure
            subdir1 = path / "subdir1"
            subdir1.mkdir()
            (subdir1 / "file1.txt").write_text("x" * 100)
            
            subdir2 = path / "subdir2"
            subdir2.mkdir()
            (subdir2 / "file2.txt").write_text("x" * 200)
            
            summary = service.analyze_directory(path, max_depth=2)
            
            assert "subdir1" in summary.subdirectory_sizes
            assert "subdir2" in summary.subdirectory_sizes
            assert summary.subdirectory_sizes["subdir2"] > summary.subdirectory_sizes["subdir1"]
    
    def test_largest_files_sorting(self) -> None:
        """Test that largest files are properly sorted."""
        service = DiskUsageService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir)
            
            # Create files with different sizes
            sizes = [100, 500, 200, 1000, 50]
            for i, size in enumerate(sizes):
                (path / f"file{i}.txt").write_text("x" * size)
            
            summary = service.analyze_directory(path, max_depth=1)
            
            # Check that files are sorted by size (largest first)
            if len(summary.largest_files) > 1:
                for i in range(len(summary.largest_files) - 1):
                    assert summary.largest_files[i][1] >= summary.largest_files[i + 1][1]
    
    def test_file_info_dataclass(self) -> None:
        """Test FileInfo dataclass."""
        path = Path("/test/file.txt")
        info = FileInfo(path, 1024, False, ".txt")
        
        assert info.path == path
        assert info.size == 1024
        assert info.is_dir is False
        assert info.file_type == ".txt"
    
    def test_directory_stats_namedtuple(self) -> None:
        """Test DirectoryStats namedtuple."""
        path = Path("/test/dir")
        stats = DirectoryStats(path, 2048, 10, 2, Path("/test/large.txt"), {".txt": 1024})
        
        assert stats.path == path
        assert stats.total_size == 2048
        assert stats.file_count == 10
        assert stats.dir_count == 2
        assert stats.largest_file == Path("/test/large.txt")
        assert stats.file_types == {".txt": 1024}
    
    def test_disk_usage_summary_dataclass(self) -> None:
        """Test DiskUsageSummary dataclass."""
        path = Path("/test")
        summary = DiskUsageSummary(
            path=path,
            total_size=4096,
            total_files=5,
            total_dirs=2,
            largest_files=[],
            file_type_distribution={".txt": 2048},
            subdirectory_sizes={"subdir": 2048},
            analyzed_at=time.time()
        )
        
        assert summary.path == path
        assert summary.total_size == 4096
        assert summary.total_files == 5
        assert summary.total_dirs == 2
        assert summary.largest_files == []
        assert summary.file_type_distribution == {".txt": 2048}
        assert summary.subdirectory_sizes == {"subdir": 2048}
