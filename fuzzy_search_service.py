"""Fuzzy search service for fzf-style file searching."""
import os
import time
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

try:
    from rapidfuzz import fuzz, process
except ImportError:
    fuzz = None
    process = None


@dataclass
class SearchResult:
    """Represents a fuzzy search result."""
    path: Path
    score: int
    matched_indices: List[int]
    
    def __str__(self) -> str:
        return str(self.path)


class FuzzySearchService:
    """Service for fuzzy file searching with rapidfuzz."""
    
    def __init__(self, max_results: int = 1000, min_score: int = 30) -> None:
        """Initialize the fuzzy search service.
        
        Args:
            max_results: Maximum number of results to return.
            min_score: Minimum similarity score (0-100) for matches.
        """
        self.max_results = max_results
        self.min_score = min_score
        self.last_search_time = 0
        self.debounce_delay = 0.1  # 100ms debounce
        self.case_sensitive = False
        
    def set_case_sensitive(self, case_sensitive: bool) -> None:
        """Set case sensitivity for searches.
        
        Args:
            case_sensitive: Whether searches should be case sensitive.
        """
        self.case_sensitive = case_sensitive
    
    def is_available(self) -> bool:
        """Check if rapidfuzz is available.
        
        Returns:
            True if rapidfuzz is available, False otherwise.
        """
        return fuzz is not None and process is not None
    
    def search_files(
        self, 
        query: str, 
        search_paths: List[Path], 
        search_depth: int = 3,
        include_hidden: bool = False
    ) -> List[SearchResult]:
        """Perform fuzzy search on files and directories.
        
        Args:
            query: Search query string.
            search_paths: List of paths to search in.
            search_depth: Maximum directory depth to search.
            include_hidden: Whether to include hidden files.
            
        Returns:
            List of search results sorted by relevance.
        """
        if not self.is_available():
            return []
        
        if not query.strip():
            return []
        
        # Debounce rapid searches
        current_time = time.time()
        if current_time - self.last_search_time < self.debounce_delay:
            time.sleep(self.debounce_delay)
        self.last_search_time = current_time
        
        # Collect all files and directories
        all_paths = []
        for search_path in search_paths:
            if search_path.exists():
                all_paths.extend(self._collect_paths(search_path, search_depth, include_hidden))
        
        if not all_paths:
            return []
        
        # Prepare search strings
        path_strings = [str(path) for path in all_paths]
        
        # Perform fuzzy search
        if self.case_sensitive:
            results = process.extract(
                query,
                path_strings,
                scorer=fuzz.WRatio,
                limit=self.max_results,
                score_cutoff=self.min_score
            )
            # Convert to SearchResult objects
            search_results = []
            for match, score, index in results:
                # Use the index from rapidfuzz to get the original path
                original_path = all_paths[index]
                
                search_results.append(SearchResult(
                    path=original_path,
                    score=score,
                    matched_indices=[]  # rapidfuzz doesn't provide matched indices in basic extract
                ))
        else:
            # For case-insensitive search, we need to map back to original strings
            lower_path_strings = [s.lower() for s in path_strings]
            results = process.extract(
                query.lower(),
                lower_path_strings,
                scorer=fuzz.WRatio,
                limit=self.max_results,
                score_cutoff=self.min_score
            )
            
            # Convert to SearchResult objects
            search_results = []
            for match, score, index in results:
                # Use the index from rapidfuzz to get the original path
                original_path = all_paths[index]
                
                search_results.append(SearchResult(
                    path=original_path,
                    score=score,
                    matched_indices=[]  # rapidfuzz doesn't provide matched indices in basic extract
                ))
        
        return search_results
    
    def search_files_debounced(
        self, 
        query: str, 
        search_paths: List[Path], 
        search_depth: int = 3,
        include_hidden: bool = False
    ) -> List[SearchResult]:
        """Perform debounced fuzzy search.
        
        Args:
            query: Search query string.
            search_paths: List of paths to search in.
            search_depth: Maximum directory depth to search.
            include_hidden: Whether to include hidden files.
            
        Returns:
            List of search results sorted by relevance.
        """
        # Simple debounce - only search if query has changed significantly
        if not hasattr(self, '_last_query'):
            self._last_query = ""
        
        # Skip search if query is the same as last time (user is still typing)
        if query == self._last_query:
            return []
        
        self._last_query = query
        return self.search_files(query, search_paths, search_depth, include_hidden)
    
    def _collect_paths(
        self, 
        root_path: Path, 
        max_depth: int, 
        include_hidden: bool,
        current_depth: int = 0
    ) -> List[Path]:
        """Recursively collect all file and directory paths.
        
        Args:
            root_path: Root path to start from.
            max_depth: Maximum depth to search.
            include_hidden: Whether to include hidden files.
            current_depth: Current recursion depth.
            
        Returns:
            List of all found paths.
        """
        paths = []
        
        try:
            for item in root_path.iterdir():
                # Skip hidden files if not requested
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                paths.append(item)
                
                # Recursively search directories within depth limit
                if item.is_dir() and current_depth < max_depth:
                    try:
                        paths.extend(self._collect_paths(
                            item, max_depth, include_hidden, current_depth + 1
                        ))
                    except (PermissionError, OSError):
                        # Skip directories we can't access
                        continue
        except (PermissionError, OSError):
            # Skip directories we can't access
            pass
        
        return paths
    
    def get_best_match(self, query: str, search_paths: List[Path]) -> Optional[SearchResult]:
        """Get the single best match for a query.
        
        Args:
            query: Search query string.
            search_paths: List of paths to search in.
            
        Returns:
            Best match result or None if no good match found.
        """
        results = self.search_files(query, search_paths, search_depth=1)
        return results[0] if results else None
    
    def highlight_match(self, result: SearchResult, query: str) -> str:
        """Create a highlighted version of the matched path.
        
        Args:
            result: Search result to highlight.
            query: Original search query.
            
        Returns:
            String with highlighted matches (using ANSI codes).
        """
        if not result.matched_indices:
            return str(result.path)
        
        path_str = str(result.path)
        highlighted = []
        
        # Add ANSI color codes for matched characters
        for i, char in enumerate(path_str):
            if i in result.matched_indices:
                highlighted.append(f"\033[91m{char}\033[0m")  # Red highlight
            else:
                highlighted.append(char)
        
        return "".join(highlighted)
    
    def get_search_stats(self, results: List[SearchResult]) -> dict:
        """Get statistics about search results.
        
        Args:
            results: List of search results.
            
        Returns:
            Dictionary with search statistics.
        """
        if not results:
            return {
                "total_results": 0,
                "avg_score": 0,
                "best_score": 0,
                "files": 0,
                "directories": 0
            }
        
        files = sum(1 for r in results if r.path.is_file())
        directories = sum(1 for r in results if r.path.is_dir())
        scores = [r.score for r in results]
        
        return {
            "total_results": len(results),
            "avg_score": sum(scores) / len(scores),
            "best_score": max(scores),
            "files": files,
            "directories": directories
        }
    
    def filter_by_type(
        self, 
        results: List[SearchResult], 
        file_type: str = "all"
    ) -> List[SearchResult]:
        """Filter search results by file type.
        
        Args:
            results: List of search results.
            file_type: Type to filter by ("all", "files", "directories").
            
        Returns:
            Filtered list of search results.
        """
        if file_type == "files":
            return [r for r in results if r.path.is_file()]
        elif file_type == "directories":
            return [r for r in results if r.path.is_dir()]
        else:
            return results
    
    def sort_by_score(self, results: List[SearchResult]) -> List[SearchResult]:
        """Sort results by score (highest first).
        
        Args:
            results: List of search results.
            
        Returns:
            Sorted list of search results.
        """
        return sorted(results, key=lambda r: r.score, reverse=True)
    
    def sort_by_name(self, results: List[SearchResult]) -> List[SearchResult]:
        """Sort results by filename.
        
        Args:
            results: List of search results.
            
        Returns:
            Sorted list of search results.
        """
        return sorted(results, key=lambda r: r.path.name.lower())
    
    def sort_by_path(self, results: List[SearchResult]) -> List[SearchResult]:
        """Sort results by full path.
        
        Args:
            results: List of search results.
            
        Returns:
            Sorted list of search results.
        """
        return sorted(results, key=lambda r: str(r.path))
    
    def __repr__(self) -> str:
        return f"FuzzySearchService(max_results={self.max_results}, min_score={self.min_score})"
