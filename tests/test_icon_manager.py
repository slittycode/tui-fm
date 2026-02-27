"""Tests for icon manager functionality."""
import tempfile
from pathlib import Path

import pytest

from icon_manager import IconManager


class TestIconManager:
    """Test cases for IconManager class."""
    
    def test_icon_manager_initialization(self) -> None:
        """Test IconManager initialization."""
        manager = IconManager()
        
        assert isinstance(manager.nerd_font_available, bool)
        assert isinstance(manager.icon_cache, dict)
        assert manager.fallback_enabled is True
        assert len(manager.ICON_MAPPINGS) > 0
        assert len(manager.DIRECTORY_ICONS) > 0
    
    def test_get_file_icon_python(self) -> None:
        """Test getting icon for Python files."""
        manager = IconManager()
        
        # Test various Python file extensions
        python_files = [
            Path("test.py"),
            Path("test.pyw"),
            Path("test.pyi"),
            Path("script.py"),
            Path("module.py"),
        ]
        
        for file_path in python_files:
            icon = manager.get_file_icon(file_path)
            assert icon == "🐍"
    
    def test_get_file_icon_javascript(self) -> None:
        """Test getting icon for JavaScript files."""
        manager = IconManager()
        
        js_files = [
            Path("test.js"),
            Path("test.jsx"),
            Path("app.js"),
            Path("component.jsx"),
        ]
        
        for file_path in js_files:
            icon = manager.get_file_icon(file_path)
            assert icon in ["📜", "📘"]  # JS or TS icon
    
    def test_get_file_icon_typescript(self) -> None:
        """Test getting icon for TypeScript files."""
        manager = IconManager()
        
        ts_files = [
            Path("test.ts"),
            Path("test.tsx"),
            Path("app.ts"),
            Path("component.tsx"),
        ]
        
        for file_path in ts_files:
            icon = manager.get_file_icon(file_path)
            assert icon == "📘"
    
    def test_get_file_icon_java(self) -> None:
        """Test getting icon for Java files."""
        manager = IconManager()
        
        java_files = [
            Path("Test.java"),
            Path("test.class"),
            Path("app.jar"),
        ]
        
        for file_path in java_files:
            icon = manager.get_file_icon(file_path)
            assert icon == "☕"
    
    def test_get_file_icon_cpp(self) -> None:
        """Test getting icon for C/C++ files."""
        manager = IconManager()
        
        cpp_files = [
            Path("test.cpp"),
            Path("test.cxx"),
            Path("test.cc"),
            Path("test.c"),
            Path("test.h"),
            Path("test.hpp"),
        ]
        
        for file_path in cpp_files:
            icon = manager.get_file_icon(file_path)
            assert icon == "⚙️"
    
    def test_get_file_icon_rust(self) -> None:
        """Test getting icon for Rust files."""
        manager = IconManager()
        
        rust_files = [
            Path("main.rs"),
            Path("lib.rs"),
            Path("module.rs"),
        ]
        
        for file_path in rust_files:
            icon = manager.get_file_icon(file_path)
            assert icon == "🦀"
    
    def test_get_file_icon_go(self) -> None:
        """Test getting icon for Go files."""
        manager = IconManager()
        
        go_files = [
            Path("main.go"),
            Path("module.go"),
        ]
        
        for file_path in go_files:
            icon = manager.get_file_icon(file_path)
            assert icon == "🐹"
    
    def test_get_file_icon_web(self) -> None:
        """Test getting icon for web files."""
        manager = IconManager()
        
        web_files = [
            Path("index.html"),
            Path("style.css"),
            Path("script.js"),
            Path("app.vue"),
            Path("component.svelte"),
        ]
        
        for file_path in web_files:
            icon = manager.get_file_icon(file_path)
            assert icon in ["🌐", "🎨", "📜", "💚", "🔥"]
    
    def test_get_file_icon_config(self) -> None:
        """Test getting icon for configuration files."""
        manager = IconManager()
        
        config_files = [
            Path("config.json"),
            Path("settings.yaml"),
            Path("app.toml"),
            Path("config.ini"),
            Path("data.xml"),
        ]
        
        for file_path in config_files:
            icon = manager.get_file_icon(file_path)
            assert icon in ["📋", "📄", "📝", "⚙️", "📰"]
    
    def test_get_file_icon_documents(self) -> None:
        """Test getting icon for document files."""
        manager = IconManager()
        
        doc_files = [
            Path("document.pdf"),
            Path("report.docx"),
            Path("notes.txt"),
            Path("readme.md"),
        ]
        
        for file_path in doc_files:
            icon = manager.get_file_icon(file_path)
            assert icon in ["📕", "📘", "📄", "📝"]
    
    def test_get_file_icon_media(self) -> None:
        """Test getting icon for media files."""
        manager = IconManager()
        
        media_files = [
            Path("image.jpg"),
            Path("photo.png"),
            Path("animation.gif"),
            Path("music.mp3"),
            Path("video.mp4"),
        ]
        
        for file_path in media_files:
            icon = manager.get_file_icon(file_path)
            assert icon in ["🖼️", "🎵", "🎬"]
    
    def test_get_file_icon_archives(self) -> None:
        """Test getting icon for archive files."""
        manager = IconManager()
        
        archive_files = [
            Path("archive.zip"),
            Path("data.tar.gz"),
            Path("package.7z"),
            Path("software.iso"),
        ]
        
        for file_path in archive_files:
            icon = manager.get_file_icon(file_path)
            assert icon in ["📦", "💿"]
    
    def test_get_file_icon_hidden_files(self) -> None:
        """Test getting icon for hidden files."""
        manager = IconManager()
        
        hidden_files = [
            Path(".gitignore"),
            Path(".env"),
            Path(".hidden"),
            Path(".config"),
        ]
        
        for file_path in hidden_files:
            icon = manager.get_file_icon(file_path)
            assert icon in ["📝", "🔐", "👁️", "⚙️"]
    
    def test_get_file_icon_special_names(self) -> None:
        """Test getting icon for files with special names."""
        manager = IconManager()
        
        special_files = [
            Path("Dockerfile"),
            Path("Makefile"),
            Path("README"),
            Path("LICENSE"),
        ]
        
        for file_path in special_files:
            icon = manager.get_file_icon(file_path)
            assert icon in ["🐳", "🔨", "📄"]
    
    def test_get_file_icon_unknown(self) -> None:
        """Test getting icon for unknown file types."""
        manager = IconManager()
        
        unknown_files = [
            Path("unknown.xyz"),
            Path("weird.extension"),
            Path("no_extension"),
        ]
        
        for file_path in unknown_files:
            icon = manager.get_file_icon(file_path)
            assert icon == "📄"  # Default file icon
    
    def test_get_directory_icon_default(self) -> None:
        """Test getting default directory icon."""
        manager = IconManager()
        
        dir_path = Path("random_directory")
        icon = manager.get_directory_icon(dir_path)
        assert icon == "📁"
    
    def test_get_directory_icon_git(self) -> None:
        """Test getting Git repository directory icon."""
        manager = IconManager()
        
        git_dirs = [
            Path(".git"),
            Path("project"),
        ]
        
        for dir_path in git_dirs:
            icon = manager.get_directory_icon(dir_path, is_git_repo=True)
            assert icon == "📂"
    
    def test_get_directory_icon_special_names(self) -> None:
        """Test getting icons for directories with special names."""
        manager = IconManager()
        
        special_dirs = [
            Path("src"),
            Path("lib"),
            Path("docs"),
            Path("test"),
            Path("config"),
            Path("build"),
            Path("node_modules"),
            Path("venv"),
        ]
        
        expected_icons = ["📂", "📚", "🧪", "⚙️", "📦", "🐍", "🔨"]
        
        for dir_path in special_dirs:
            icon = manager.get_directory_icon(dir_path)
            assert icon in expected_icons
    
    def test_get_icon_with_fallback_available(self) -> None:
        """Test getting icon with fallback when Nerd Fonts are available."""
        manager = IconManager()
        
        file_path = Path("test.py")
        
        # Should return the actual icon if available
        icon = manager.get_icon_with_fallback(file_path, "📄")
        if manager.nerd_font_available:
            assert icon == "🐍"
        else:
            assert icon == "📄"
    
    def test_get_icon_with_fallback_unavailable(self) -> None:
        """Test getting icon with fallback when Nerd Fonts are not available."""
        manager = IconManager()
        manager.nerd_font_available = False
        
        file_path = Path("test.py")
        icon = manager.get_icon_with_fallback(file_path, "📄")
        assert icon == "📄"
    
    def test_get_directory_icon_with_fallback(self) -> None:
        """Test getting directory icon with fallback."""
        manager = IconManager()
        
        dir_path = Path("test_dir")
        
        # Should return the actual icon if available
        icon = manager.get_directory_icon_with_fallback(dir_path, False, "📁")
        if manager.nerd_font_available:
            assert icon in ["📁", "📂", "📚", "🧪", "⚙️", "📦", "🐍"]
        else:
            assert icon == "📁"
    
    def test_icon_caching(self) -> None:
        """Test that icons are cached properly."""
        manager = IconManager()
        
        file_path = Path("test.py")
        
        # First call should cache the result
        icon1 = manager.get_file_icon(file_path)
        cache_size_1 = len(manager.icon_cache)
        
        # Second call should use cache
        icon2 = manager.get_file_icon(file_path)
        cache_size_2 = len(manager.icon_cache)
        
        assert icon1 == icon2
        assert cache_size_1 == cache_size_2
        assert cache_size_1 > 0
    
    def test_clear_cache(self) -> None:
        """Test clearing the icon cache."""
        manager = IconManager()
        
        # Add something to cache
        manager.get_file_icon(Path("test.py"))
        assert len(manager.icon_cache) > 0
        
        # Clear cache
        manager.clear_cache()
        assert len(manager.icon_cache) == 0
    
    def test_get_cache_stats(self) -> None:
        """Test getting cache statistics."""
        manager = IconManager()
        
        # Get initial stats
        stats = manager.get_cache_stats()
        assert "cache_size" in stats
        assert "nerd_font_available" in stats
        assert "fallback_enabled" in stats
        assert stats["cache_size"] == 0
        
        # Add something to cache
        manager.get_file_icon(Path("test.py"))
        
        # Get updated stats
        stats = manager.get_cache_stats()
        assert stats["cache_size"] > 0
    
    def test_create_icon_text(self) -> None:
        """Test creating icon text."""
        from rich.text import Text
        
        manager = IconManager()
        
        icon_text = manager.create_icon_text("🐍", "test.py", "bold")
        assert isinstance(icon_text, Text)
        assert "🐍" in str(icon_text)
        assert "test.py" in str(icon_text)
        
        # Test string version
        icon_string = manager.create_icon_text_string("🐍", "test.py", "bold")
        assert isinstance(icon_string, str)
        assert icon_string == "🐍 test.py"
    
    def test_is_available(self) -> None:
        """Test checking if icons are available."""
        manager = IconManager()
        
        available = manager.is_available()
        assert isinstance(available, bool)
    
    def test_enable_fallback(self) -> None:
        """Test enabling/disabling fallback."""
        manager = IconManager()
        
        # Enable fallback
        manager.enable_fallback(True)
        assert manager.fallback_enabled is True
        
        # Disable fallback
        manager.enable_fallback(False)
        assert manager.fallback_enabled is False
    
    def test_repr(self) -> None:
        """Test string representation."""
        manager = IconManager()
        
        repr_str = repr(manager)
        assert "IconManager" in repr_str
        assert "nerd_font" in repr_str
        assert "cache_size" in repr_str
    
    def test_case_insensitive_extensions(self) -> None:
        """Test that file extensions are handled case-insensitively."""
        manager = IconManager()
        
        extensions = [".PY", ".Js", ".TS", ".MD", ".PDF"]
        
        for ext in extensions:
            file_path = Path(f"test{ext}")
            icon = manager.get_file_icon(file_path)
            assert icon != "📄"  # Should not be default icon
    
    def test_comprehensive_icon_coverage(self) -> None:
        """Test that all defined icon mappings work."""
        manager = IconManager()
        
        # Test a sample of each category
        test_cases = [
            # Programming
            (".py", "🐍"),
            (".js", "📜"),
            (".java", "☕"),
            (".cpp", "⚙️"),
            (".rs", "🦀"),
            (".go", "🐹"),
            
            # Config
            (".json", "📋"),
            (".yaml", "📄"),
            (".toml", "📝"),
            (".xml", "📰"),
            
            # Documents
            (".pdf", "📕"),
            (".txt", "📄"),
            (".md", "📝"),
            
            # Media
            (".jpg", "🖼️"),
            (".mp3", "🎵"),
            (".mp4", "🎬"),
            
            # Archives
            (".zip", "📦"),
            (".tar", "📦"),
            (".gz", "📦"),
        ]
        
        for ext, expected_icon in test_cases:
            file_path = Path(f"test{ext}")
            icon = manager.get_file_icon(file_path)
            assert icon == expected_icon, f"Extension {ext} should have icon {expected_icon}, got {icon}"
    
    def test_performance_with_large_cache(self) -> None:
        """Test performance with large icon cache."""
        manager = IconManager()
        
        # Add many entries to cache
        for i in range(1000):
            file_path = Path(f"test_{i}.py")
            manager.get_file_icon(file_path)
        
        # Cache should be reasonably sized
        assert len(manager.icon_cache) == 1000
        
        # Retrieval should still be fast
        import time
        start_time = time.time()
        icon = manager.get_file_icon(Path("test_500.py"))
        end_time = time.time()
        
        assert icon == "🐍"
        assert (end_time - start_time) < 0.001  # Should be very fast from cache
