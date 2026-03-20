"""Tests for fuzzy search service functionality."""
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from fuzzy_search_service import FuzzySearchService, SearchResult


class TestFuzzySearchService:
    """Test cases for FuzzySearchService class."""
    
    def test_service_initialization(self) -> None:
        """Test FuzzySearchService initialization."""
        service = FuzzySearchService()
        
        assert service.max_results == 1000
        assert service.min_score == 30
        assert service.debounce_delay == 0.1
        assert service.case_sensitive is False
    
    def test_service_custom_initialization(self) -> None:
        """Test FuzzySearchService initialization with custom parameters."""
        service = FuzzySearchService(max_results=500, min_score=50)
        
        assert service.max_results == 500
        assert service.min_score == 50
    
    def test_set_case_sensitive(self) -> None:
        """Test setting case sensitivity."""
        service = FuzzySearchService()
        
        service.set_case_sensitive(True)
        assert service.case_sensitive is True
        
        service.set_case_sensitive(False)
        assert service.case_sensitive is False
    
    def test_is_available_with_rapidfuzz(self) -> None:
        """Test availability check when rapidfuzz is available."""
        service = FuzzySearchService()
        
        # Check if rapidfuzz is available by importing the modules
        try:
            import rapidfuzz
            expected = True
        except ImportError:
            expected = False
        
        assert service.is_available() == expected
    
    def test_is_available_without_rapidfuzz(self) -> None:
        """Test availability check when rapidfuzz is not available."""
        with patch('fuzzy_search_service.fuzz', None):
            with patch('fuzzy_search_service.process', None):
                service = FuzzySearchService()
                assert not service.is_available()
    
    def test_search_files_no_rapidfuzz(self) -> None:
        """Test search when rapidfuzz is not available."""
        with patch('fuzzy_search_service.fuzz', None):
            with patch('fuzzy_search_service.process', None):
                service = FuzzySearchService()
                results = service.search_files("test", [Path("/tmp")])
                assert results == []
    
    def test_search_files_empty_query(self) -> None:
        """Test search with empty query."""
        service = FuzzySearchService()
        
        with patch.object(service, 'is_available', return_value=True):
            results = service.search_files("", [Path("/tmp")])
            assert results == []
            
            results = service.search_files("   ", [Path("/tmp")])
            assert results == []
    
    @patch('fuzzy_search_service.fuzz')
    @patch('fuzzy_search_service.process')
    def test_search_files_success(self, mock_process: Mock, mock_fuzz: Mock) -> None:
        """Test successful file search."""
        service = FuzzySearchService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = ["test.txt", "example.py", "sample.md"]
            for filename in test_files:
                Path(temp_dir).joinpath(filename).touch()
            
            # Mock rapidfuzz results - actual format is (match, score, index)
            # The index should correspond to the actual file order
            mock_process.extract.return_value = [
                ("test.txt", 95, 0),  # index 0 = test.txt
                ("example.py", 80, 1),  # index 1 = example.py
            ]
            
            with patch.object(service, 'is_available', return_value=True):
                # Mock the collect_paths to return files in a predictable order
                with patch.object(service, '_collect_paths') as mock_collect:
                    collected_files = [
                        Path(temp_dir) / "test.txt",
                        Path(temp_dir) / "example.py", 
                        Path(temp_dir) / "sample.md"
                    ]
                    mock_collect.return_value = collected_files
                    
                    results = service.search_files("test", [Path(temp_dir)])
                    
                    assert len(results) == 2
                    assert all(isinstance(r, SearchResult) for r in results)
                    assert results[0].score == 95
                    assert results[1].score == 80
                    assert results[0].path.name == "test.txt"
                    assert results[1].path.name == "example.py"
    
    @patch('fuzzy_search_service.fuzz')
    @patch('fuzzy_search_service.process')
    def test_search_files_case_sensitive(self, mock_process: Mock, mock_fuzz: Mock) -> None:
        """Test case-sensitive search."""
        service = FuzzySearchService()
        service.set_case_sensitive(True)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            Path(temp_dir).joinpath("Test.txt").touch()
            Path(temp_dir).joinpath("test.txt").touch()
            
            # Mock rapidfuzz results for case-sensitive search
            mock_process.extract.return_value = [
                ("Test.txt", 90, 0),
            ]
            
            with patch.object(service, 'is_available', return_value=True):
                with patch.object(service, '_collect_paths') as mock_collect:
                    collected_files = [
                        Path(temp_dir) / "Test.txt",
                        Path(temp_dir) / "test.txt",
                    ]
                    mock_collect.return_value = collected_files
                    
                    results = service.search_files("Test", [Path(temp_dir)])
                    
                    assert len(results) == 1
                    assert results[0].path.name == "Test.txt"
    
    @patch('fuzzy_search_service.fuzz')
    @patch('fuzzy_search_service.process')
    def test_search_files_case_insensitive(self, mock_process: Mock, mock_fuzz: Mock) -> None:
        """Test case-insensitive search."""
        service = FuzzySearchService()
        service.set_case_sensitive(False)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            Path(temp_dir).joinpath("Test.txt").touch()
            Path(temp_dir).joinpath("test.txt").touch()
            
            # Mock rapidfuzz results for case-insensitive search
            mock_process.extract.return_value = [
                ("test.txt", 90, 0),
            ]
            
            with patch.object(service, 'is_available', return_value=True):
                with patch.object(service, '_collect_paths') as mock_collect:
                    collected_files = [
                        Path(temp_dir) / "Test.txt",
                        Path(temp_dir) / "test.txt",
                    ]
                    mock_collect.return_value = collected_files
                    
                    results = service.search_files("TEST", [Path(temp_dir)])
                    
                    assert len(results) == 1
                    assert results[0].path.name in ["Test.txt", "test.txt"]
    
    def test_collect_paths_basic(self) -> None:
        """Test basic path collection."""
        service = FuzzySearchService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test structure
            Path(temp_dir).joinpath("file1.txt").touch()
            Path(temp_dir).joinpath("file2.py").touch()
            subdir = Path(temp_dir).joinpath("subdir")
            subdir.mkdir()
            subdir.joinpath("file3.md").touch()
            
            paths = service._collect_paths(Path(temp_dir), max_depth=2, include_hidden=False)
            
            assert len(paths) >= 3
            assert any(p.name == "file1.txt" for p in paths)
            assert any(p.name == "file2.py" for p in paths)
            assert any(p.name == "file3.md" for p in paths)
    
    def test_collect_paths_depth_limit(self) -> None:
        """Test path collection with depth limit."""
        service = FuzzySearchService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested structure
            level1 = Path(temp_dir).joinpath("level1")
            level1.mkdir()
            level2 = level1.joinpath("level2")
            level2.mkdir()
            
            level1.joinpath("file1.txt").touch()
            level2.joinpath("file2.txt").touch()
            
            # Test that path collection works
            paths = service._collect_paths(Path(temp_dir), max_depth=2, include_hidden=False)
            assert len(paths) >= 2  # Should at least have level1 and level2
            assert any(p.name == "level1" for p in paths)
            assert any(p.name == "level2" for p in paths)
    
    def test_collect_paths_hidden_files(self) -> None:
        """Test path collection with hidden files."""
        service = FuzzySearchService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create normal and hidden files
            Path(temp_dir).joinpath("normal.txt").touch()
            Path(temp_dir).joinpath(".hidden.txt").touch()
            Path(temp_dir).joinpath(".hidden_dir").mkdir()
            Path(temp_dir).joinpath(".hidden_dir").joinpath("inside.txt").touch()
            
            # Without hidden files
            paths = service._collect_paths(Path(temp_dir), max_depth=2, include_hidden=False)
            assert any(p.name == "normal.txt" for p in paths)
            assert not any(p.name.startswith('.') for p in paths)
            
            # With hidden files
            paths = service._collect_paths(Path(temp_dir), max_depth=2, include_hidden=True)
            assert any(p.name == "normal.txt" for p in paths)
            assert any(p.name == ".hidden.txt" for p in paths)
            assert any(p.name == ".hidden_dir" for p in paths)
    
    def test_collect_paths_permission_error(self) -> None:
        """Test path collection with permission errors."""
        service = FuzzySearchService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file
            Path(temp_dir).joinpath("accessible.txt").touch()
            
            # Mock permission error
            with patch.object(Path, 'iterdir', side_effect=PermissionError("Access denied")):
                paths = service._collect_paths(Path(temp_dir), max_depth=2, include_hidden=False)
                assert paths == []  # Should handle gracefully
    
    @patch('fuzzy_search_service.fuzz')
    @patch('fuzzy_search_service.process')
    def test_get_best_match(self, mock_process: Mock, mock_fuzz: Mock) -> None:
        """Test getting the best match."""
        service = FuzzySearchService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir).joinpath("best_match.txt").touch()
            
            # Mock search results
            mock_process.extract.return_value = [
                ("best_match.txt", 95, 0),
                ("other_match.txt", 80, 1),
            ]
            
            with patch.object(service, 'is_available', return_value=True):
                with patch.object(service, '_collect_paths') as mock_collect:
                    collected_files = [
                        Path(temp_dir) / "best_match.txt",
                        Path(temp_dir) / "other_match.txt",
                    ]
                    mock_collect.return_value = collected_files
                    
                    best_match = service.get_best_match("best", [Path(temp_dir)])
                    
                    assert best_match is not None
                    assert best_match.score == 95
                    assert best_match.path.name == "best_match.txt"
    
    def test_get_best_match_no_results(self) -> None:
        """Test getting best match with no results."""
        service = FuzzySearchService()
        
        with patch.object(service, 'search_files', return_value=[]):
            best_match = service.get_best_match("nonexistent", [Path("/tmp")])
            assert best_match is None
    
    def test_highlight_match(self) -> None:
        """Test match highlighting."""
        service = FuzzySearchService()
        
        result = SearchResult(
            path=Path("test_file.txt"),
            score=90,
            matched_indices=[0, 1, 2, 3]
        )
        
        highlighted = service.highlight_match(result, "test")
        assert "\033[91m" in highlighted  # Should contain ANSI color codes
        assert "\033[0m" in highlighted   # Should contain reset codes
    
    def test_highlight_match_no_indices(self) -> None:
        """Test highlighting with no matched indices."""
        service = FuzzySearchService()
        
        result = SearchResult(
            path=Path("test_file.txt"),
            score=90,
            matched_indices=[]
        )
        
        highlighted = service.highlight_match(result, "test")
        assert highlighted == "test_file.txt"  # Should return plain string
    
    def test_get_search_stats_empty(self) -> None:
        """Test search statistics with empty results."""
        service = FuzzySearchService()
        
        stats = service.get_search_stats([])
        
        assert stats["total_results"] == 0
        assert stats["avg_score"] == 0
        assert stats["best_score"] == 0
        assert stats["files"] == 0
        assert stats["directories"] == 0
    
    def test_get_search_stats_with_results(self) -> None:
        """Test search statistics with results."""
        service = FuzzySearchService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files and directories
            file_path = Path(temp_dir).joinpath("test.txt")
            file_path.touch()
            dir_path = Path(temp_dir).joinpath("test_dir")
            dir_path.mkdir()
            
            results = [
                SearchResult(file_path, 90, []),
                SearchResult(dir_path, 80, []),
                SearchResult(file_path, 70, [])
            ]
            
            stats = service.get_search_stats(results)
            
            assert stats["total_results"] == 3
            assert stats["avg_score"] == 80.0  # (90 + 80 + 70) / 3
            assert stats["best_score"] == 90
            assert stats["files"] == 2
            assert stats["directories"] == 1
    
    def test_filter_by_type(self) -> None:
        """Test filtering results by type."""
        service = FuzzySearchService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir).joinpath("test.txt")
            file_path.touch()
            dir_path = Path(temp_dir).joinpath("test_dir")
            dir_path.mkdir()
            
            results = [
                SearchResult(file_path, 90, []),
                SearchResult(dir_path, 80, [])
            ]
            
            # Filter files only
            files = service.filter_by_type(results, "files")
            assert len(files) == 1
            assert files[0].path.is_file()
            
            # Filter directories only
            dirs = service.filter_by_type(results, "directories")
            assert len(dirs) == 1
            assert dirs[0].path.is_dir()
            
            # No filtering
            all_results = service.filter_by_type(results, "all")
            assert len(all_results) == 2
    
    def test_sort_by_score(self) -> None:
        """Test sorting results by score."""
        service = FuzzySearchService()
        
        results = [
            SearchResult(Path("low.txt"), 70, []),
            SearchResult(Path("high.txt"), 95, []),
            SearchResult(Path("medium.txt"), 80, [])
        ]
        
        sorted_results = service.sort_by_score(results)
        
        assert sorted_results[0].score == 95
        assert sorted_results[1].score == 80
        assert sorted_results[2].score == 70
    
    def test_sort_by_name(self) -> None:
        """Test sorting results by name."""
        service = FuzzySearchService()
        
        results = [
            SearchResult(Path("zebra.txt"), 90, []),
            SearchResult(Path("apple.txt"), 80, []),
            SearchResult(Path("banana.txt"), 70, [])
        ]
        
        sorted_results = service.sort_by_name(results)
        
        assert sorted_results[0].path.name == "apple.txt"
        assert sorted_results[1].path.name == "banana.txt"
        assert sorted_results[2].path.name == "zebra.txt"
    
    def test_sort_by_path(self) -> None:
        """Test sorting results by full path."""
        service = FuzzySearchService()
        
        results = [
            SearchResult(Path("/tmp/zebra.txt"), 90, []),
            SearchResult(Path("/tmp/apple.txt"), 80, []),
            SearchResult(Path("/tmp/banana.txt"), 70, [])
        ]
        
        sorted_results = service.sort_by_path(results)
        
        assert "apple" in str(sorted_results[0].path)
        assert "banana" in str(sorted_results[1].path)
        assert "zebra" in str(sorted_results[2].path)
    
    def test_search_debounced(self) -> None:
        """Test debounced search functionality."""
        service = FuzzySearchService()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir).joinpath("test.txt").touch()
            
            with patch.object(service, 'search_files', return_value=[]) as mock_search:
                # First search should work
                results1 = service.search_files_debounced("test", [Path(temp_dir)])
                mock_search.assert_called_once()
                
                # Second search with same query should be skipped
                results2 = service.search_files_debounced("test", [Path(temp_dir)])
                assert mock_search.call_count == 1  # Should not be called again
                
                # Different query should work
                results3 = service.search_files_debounced("different", [Path(temp_dir)])
                assert mock_search.call_count == 2
    
    def test_repr(self) -> None:
        """Test string representation."""
        service = FuzzySearchService(max_results=500, min_score=60)
        
        repr_str = repr(service)
        assert "FuzzySearchService" in repr_str
        assert "500" in repr_str
        assert "60" in repr_str
    
    def test_search_result_dataclass(self) -> None:
        """Test SearchResult dataclass."""
        path = Path("test.txt")
        result = SearchResult(path, 90, [0, 1, 2])
        
        assert result.path == path
        assert result.score == 90
        assert result.matched_indices == [0, 1, 2]
        assert str(result) == "test.txt"
    
    @patch('fuzzy_search_service.fuzz')
    @patch('fuzzy_search_service.process')
    def test_search_files_no_paths(self, mock_process: Mock, mock_fuzz: Mock) -> None:
        """Test search with no valid paths."""
        service = FuzzySearchService()
        
        with patch.object(service, 'is_available', return_value=True):
            results = service.search_files("test", [Path("/nonexistent")])
            assert results == []
    
    def test_debounce_timing(self) -> None:
        """Test debounce logic triggers a sleep for rapid consecutive searches."""
        service = FuzzySearchService()
        service.debounce_delay = 0.01  # 10ms debounce
        
        # Skip if rapidfuzz is not available
        if not service.is_available():
            pytest.skip("rapidfuzz not available")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir).joinpath("test.txt").touch()

            # Simulate a recent prior search so debounce should sleep.
            service.last_search_time = time.time()

            with patch("fuzzy_search_service.time.sleep") as mock_sleep:
                service.search_files("test", [Path(temp_dir)])
                mock_sleep.assert_called_once_with(service.debounce_delay)
