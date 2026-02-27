"""Tests for icon integration with FilterableDirectoryTree."""
import tempfile
from pathlib import Path

from filterable_tree import FilterableDirectoryTree


class TestIconIntegration:
    """Test cases for icon integration in FilterableDirectoryTree."""
    
    def test_filterable_tree_has_icon_manager(self) -> None:
        """Test that FilterableDirectoryTree has an icon manager."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tree = FilterableDirectoryTree(temp_dir)
            
            assert hasattr(tree, 'icon_manager')
            assert tree.icon_manager is not None
    
    def test_render_label_with_icon(self) -> None:
        """Test that render_label includes icons."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tree = FilterableDirectoryTree(temp_dir)
            
            # Create test files
            test_files = [
                "test.py",
                "config.json", 
                "document.pdf",
                "image.jpg",
            ]
            
            for filename in test_files:
                file_path = Path(temp_dir) / filename
                file_path.write_text("test content")
            
            # Test file icons
            for filename in test_files:
                file_path = Path(temp_dir) / filename
                label = tree._render_label_with_git_status(file_path)
                
                # Should contain icon and filename
                label_str = str(label)
                assert filename in label_str
                
                # Should contain an icon (non-empty character at start)
                if label_str:
                    first_char = label_str[0]
                    # Check if it's a valid emoji/icon character
                    assert ord(first_char) > 127  # Should be Unicode beyond ASCII
    
    def test_render_directory_with_icon(self) -> None:
        """Test that render_label includes directory icons."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tree = FilterableDirectoryTree(temp_dir)
            
            # Create test directories
            test_dirs = [
                "src",
                "docs", 
                "tests",
                "build",
            ]
            
            for dirname in test_dirs:
                dir_path = Path(temp_dir) / dirname
                dir_path.mkdir()
            
            # Test directory icons
            for dirname in test_dirs:
                dir_path = Path(temp_dir) / dirname
                label = tree._render_label_with_git_status(dir_path)
                
                # Should contain icon and directory name
                label_str = str(label)
                assert dirname in label_str
                
                # Should contain an icon
                if label_str:
                    first_char = label_str[0]
                    assert ord(first_char) > 127  # Should be Unicode beyond ASCII
    
    def test_render_label_git_repo_directory(self) -> None:
        """Test that Git repository directories get special icons."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tree = FilterableDirectoryTree(temp_dir)
            
            # Create a directory with .git (Git repository)
            git_dir = Path(temp_dir) / "my_project"
            git_dir.mkdir()
            (git_dir / ".git").mkdir()
            
            label = tree._render_label_with_git_status(git_dir)
            label_str = str(label)
            
            # Should contain directory name
            assert "my_project" in label_str
            
            # Should contain an icon (likely Git folder icon)
            if label_str:
                first_char = label_str[0]
                assert ord(first_char) > 127
    
    def test_icon_caching_performance(self) -> None:
        """Test that icon caching improves performance."""
        import time
        
        with tempfile.TemporaryDirectory() as temp_dir:
            tree = FilterableDirectoryTree(temp_dir)
            
            # Create test files
            for i in range(100):
                file_path = Path(temp_dir) / f"test_{i}.py"
                file_path.write_text("test content")
            
            # First render (cache miss)
            start_time = time.time()
            for i in range(100):
                file_path = Path(temp_dir) / f"test_{i}.py"
                tree._render_label_with_git_status(file_path)
            first_time = time.time() - start_time
            
            # Second render (cache hit)
            start_time = time.time()
            for i in range(100):
                file_path = Path(temp_dir) / f"test_{i}.py"
                tree._render_label_with_git_status(file_path)
            second_time = time.time() - start_time
            
            # Second time should be faster (cached)
            assert second_time <= first_time
    
    def test_icon_fallback_disabled(self) -> None:
        """Test behavior when icon fallback is disabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tree = FilterableDirectoryTree(temp_dir)
            
            # Disable fallback
            tree.icon_manager.enable_fallback(False)
            tree.icon_manager.nerd_font_available = False
            
            # Create test file
            file_path = Path(temp_dir) / "test.py"
            file_path.write_text("test content")
            
            label = tree._render_label_with_git_status(file_path)
            label_str = str(label)
            
            # Should still contain filename
            assert "test.py" in label_str
            
            # Should not contain icon when fallback disabled and no Nerd Font
            # (just filename, no icon prefix)
            assert label_str.startswith("test.py")
    
    def test_icon_fallback_enabled(self) -> None:
        """Test behavior when icon fallback is enabled."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tree = FilterableDirectoryTree(temp_dir)
            
            # Enable fallback but no Nerd Font
            tree.icon_manager.enable_fallback(True)
            tree.icon_manager.nerd_font_available = False
            
            # Create test file
            file_path = Path(temp_dir) / "test.py"
            file_path.write_text("test content")
            
            label = tree._render_label_with_git_status(file_path)
            label_str = str(label)
            
            # Should contain filename
            assert "test.py" in label_str
            
            # Should contain fallback icon when enabled
            assert len(label_str) > len("test.py")
    
    def test_mixed_file_types_icons(self) -> None:
        """Test that different file types get different icons."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tree = FilterableDirectoryTree(temp_dir)
            
            # Create files with different extensions
            test_files = {
                "script.py": "🐍",      # Python
                "config.json": "📋",   # JSON
                "image.jpg": "🖼️",     # Image
                "archive.zip": "📦",   # Archive
            }
            
            for filename, expected_icon in test_files.items():
                file_path = Path(temp_dir) / filename
                file_path.write_text("test content")
                
                label = tree._render_label_with_git_status(file_path)
                label_str = str(label)
                
                if tree.icon_manager.nerd_font_available:
                    # Should contain expected icon
                    assert expected_icon in label_str
                    assert filename in label_str
                else:
                    # Should contain fallback icon or just filename
                    assert filename in label_str
    
    def test_special_directory_names(self) -> None:
        """Test that special directory names get appropriate icons."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tree = FilterableDirectoryTree(temp_dir)
            
            # Create special directories
            special_dirs = {
                "src": "📂",
                "docs": "📚", 
                "tests": "🧪",
                "build": "🔨",
                "node_modules": "📦",
                "venv": "🐍",
            }
            
            for dirname, expected_icon in special_dirs.items():
                dir_path = Path(temp_dir) / dirname
                dir_path.mkdir()
                
                label = tree._render_label_with_git_status(dir_path)
                label_str = str(label)
                
                if tree.icon_manager.nerd_font_available:
                    # Should contain expected icon
                    assert expected_icon in label_str
                    assert dirname in label_str
                else:
                    # Should contain fallback icon or just dirname
                    assert dirname in label_str
    
    def test_hidden_files_icons(self) -> None:
        """Test that hidden files get appropriate icons."""
        with tempfile.TemporaryDirectory() as temp_dir:
            tree = FilterableDirectoryTree(temp_dir)
            
            # Create hidden files
            hidden_files = {
                ".gitignore": "📝",
                ".env": "🔐",
                ".hidden": "👁️",
                ".config": "👁️",  # Hidden files get the eye icon
            }
            
            for filename, expected_icon in hidden_files.items():
                file_path = Path(temp_dir) / filename
                file_path.write_text("test content")
                
                label = tree._render_label_with_git_status(file_path)
                label_str = str(label)
                
                if tree.icon_manager.nerd_font_available:
                    # Should contain expected icon
                    assert expected_icon in label_str
                    assert filename in label_str
                else:
                    # Should contain fallback icon or just filename
                    assert filename in label_str
