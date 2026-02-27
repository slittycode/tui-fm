"""Tests for theme manager functionality."""
import json
import tempfile
from pathlib import Path

from theme_data import Theme, ThemeColors, get_builtin_theme
from theme_manager import ThemeManager


class TestThemeManager:
    """Test cases for ThemeManager class."""
    
    def test_theme_manager_initialization(self) -> None:
        """Test ThemeManager initialization."""
        manager = ThemeManager()
        
        assert len(manager) > 0
        assert "dark" in manager
        assert "light" in manager
        assert manager.current_theme == "dark"
        assert manager.custom_themes_dir.exists()
    
    def test_theme_manager_custom_directory(self) -> None:
        """Test ThemeManager with custom directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir) / "custom_themes"
            manager = ThemeManager(custom_themes_dir=custom_dir)
            
            assert manager.custom_themes_dir == custom_dir
            assert custom_dir.exists()
    
    def test_get_theme(self) -> None:
        """Test getting themes by name."""
        manager = ThemeManager()
        
        # Test built-in theme
        theme = manager.get_theme("dark")
        assert theme is not None
        assert theme.name == "dark"
        assert theme.is_builtin is True
        
        # Test non-existent theme
        theme = manager.get_theme("nonexistent")
        assert theme is None
    
    def test_set_theme(self) -> None:
        """Test setting current theme."""
        manager = ThemeManager()
        
        # Set to valid theme
        success = manager.set_theme("light")
        assert success is True
        assert manager.current_theme == "light"
        
        # Set to invalid theme
        success = manager.set_theme("nonexistent")
        assert success is False
        assert manager.current_theme == "light"  # Should not change
    
    def test_get_current_theme(self) -> None:
        """Test getting current theme."""
        manager = ThemeManager()
        
        theme = manager.get_current_theme()
        assert theme is not None
        assert theme.name == manager.current_theme
        
        # Change theme and check again
        manager.set_theme("light")
        theme = manager.get_current_theme()
        assert theme is not None
        assert theme.name == "light"
    
    def test_list_themes(self) -> None:
        """Test listing all themes."""
        manager = ThemeManager()
        
        themes = manager.list_themes()
        assert len(themes) >= 8  # At least the built-in themes
        
        theme_names = [theme.name for theme in themes]
        assert "dark" in theme_names
        assert "light" in theme_names
    
    def test_list_builtin_themes(self) -> None:
        """Test listing built-in themes only."""
        manager = ThemeManager()
        
        themes = manager.list_builtin_themes()
        assert len(themes) == 8  # Exactly the built-in themes
        
        theme_names = [theme.name for theme in themes]
        expected_names = ["dark", "light", "monochrome", "ocean", "forest", "sunset", "cyberpunk", "nord"]
        for name in expected_names:
            assert name in theme_names
        
        # All should be built-in
        assert all(theme.is_builtin for theme in themes)
    
    def test_list_custom_themes(self) -> None:
        """Test listing custom themes only."""
        manager = ThemeManager()
        
        # Initially no custom themes
        themes = manager.list_custom_themes()
        assert len(themes) == 0
    
    def test_register_theme(self) -> None:
        """Test registering a new theme."""
        manager = ThemeManager()
        
        colors = ThemeColors(
            surface="#ffffff", panel="#f0f0f0", panel_darken="#e0e0e0",
            primary="#333333", primary_darken="#000000", accent="#666666",
            text="#000000", text_muted="#666666", text_inverse="#ffffff",
            text_secondary="#333333", border="#999999", border_highlight="#666666",
            border_panel="#cccccc", success="#333333", warning="#666666",
            error="#000000", info="#666666", git_modified="#666666",
            git_added="#333333", git_deleted="#000000", git_untracked="#999999",
            highlight="#cccccc", hover="#e0e0e0", active="#666666", disabled="#cccccc"
        )
        
        theme = Theme(
            name="custom",
            display_name="Custom Theme",
            description="A custom theme",
            colors=colors,
            is_builtin=False
        )
        
        # Register valid theme
        success = manager.register_theme(theme)
        assert success is True
        assert "custom" in manager
        assert manager.get_theme("custom") is theme
        
        # Try to register built-in theme name (should fail)
        builtin_theme = get_builtin_theme("dark")
        success = manager.register_theme(builtin_theme)
        assert success is False
    
    def test_register_invalid_theme(self) -> None:
        """Test registering an invalid theme."""
        manager = ThemeManager()
        
        # Create invalid theme (missing required fields)
        colors = ThemeColors(
            surface="", panel="#f0f0f0", panel_darken="#e0e0e0",
            primary="#333333", primary_darken="#000000", accent="#666666",
            text="#000000", text_muted="#666666", text_inverse="#ffffff",
            text_secondary="#333333", border="#999999", border_highlight="#666666",
            border_panel="#cccccc", success="#333333", warning="#666666",
            error="#000000", info="#666666", git_modified="#666666",
            git_added="#333333", git_deleted="#000000", git_untracked="#999999",
            highlight="#cccccc", hover="#e0e0e0", active="#666666", disabled="#cccccc"
        )
        
        theme = Theme(
            name="invalid",
            display_name="Invalid Theme",
            description="An invalid theme",
            colors=colors,
            is_builtin=False
        )
        
        success = manager.register_theme(theme)
        assert success is False
        assert "invalid" not in manager
    
    def test_generate_css(self) -> None:
        """Test CSS generation."""
        manager = ThemeManager()
        
        css = manager.generate_css()
        assert css is not None
        assert len(css) > 0
        assert "Theme:" in css
        assert "Screen {" in css
        assert "background:" in css
        
        # Test with specific theme
        css = manager.generate_css(manager.get_theme("light"))
        assert "#ffffff" in css  # Light theme surface color
        assert "#007acc" in css  # Light theme primary color
    
    def test_generate_css_no_current_theme(self) -> None:
        """Test CSS generation when no current theme is set."""
        manager = ThemeManager()
        manager.current_theme = "nonexistent"
        
        css = manager.generate_css()
        assert css == ""
    
    def test_save_custom_theme(self) -> None:
        """Test saving custom theme to disk."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir) / "themes"
            manager = ThemeManager(custom_themes_dir=custom_dir)
            
            colors = ThemeColors(
                surface="#ffffff", panel="#f0f0f0", panel_darken="#e0e0e0",
                primary="#333333", primary_darken="#000000", accent="#666666",
                text="#000000", text_muted="#666666", text_inverse="#ffffff",
                text_secondary="#333333", border="#999999", border_highlight="#666666",
                border_panel="#cccccc", success="#333333", warning="#666666",
                error="#000000", info="#666666", git_modified="#666666",
                git_added="#333333", git_deleted="#000000", git_untracked="#999999",
                highlight="#cccccc", hover="#e0e0e0", active="#666666", disabled="#cccccc"
            )
            
            theme = Theme(
                name="saved",
                display_name="Saved Theme",
                description="A saved theme",
                colors=colors,
                is_builtin=False
            )
            
            # Save theme
            success = manager.save_custom_theme(theme)
            assert success is True
            
            # Check file was created
            theme_file = custom_dir / "saved.json"
            assert theme_file.exists()
            
            # Check file contents
            with open(theme_file, encoding="utf-8") as f:
                data = json.load(f)
            assert data["name"] == "saved"
            assert data["display_name"] == "Saved Theme"
            
            # Check theme is registered
            assert "saved" in manager
            assert manager.get_theme("saved") is not None
    
    def test_save_builtin_theme(self) -> None:
        """Test that built-in themes cannot be saved."""
        manager = ThemeManager()
        
        theme = get_builtin_theme("dark")
        success = manager.save_custom_theme(theme)
        assert success is False
    
    def test_save_invalid_theme(self) -> None:
        """Test that invalid themes cannot be saved."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir) / "themes"
            manager = ThemeManager(custom_themes_dir=custom_dir)
            
            # Create invalid theme
            colors = ThemeColors(
                surface="", panel="#f0f0f0", panel_darken="#e0e0e0",
                primary="#333333", primary_darken="#000000", accent="#666666",
                text="#000000", text_muted="#666666", text_inverse="#ffffff",
                text_secondary="#333333", border="#999999", border_highlight="#666666",
                border_panel="#cccccc", success="#333333", warning="#666666",
                error="#000000", info="#666666", git_modified="#666666",
                git_added="#333333", git_deleted="#000000", git_untracked="#999999",
                highlight="#cccccc", hover="#e0e0e0", active="#666666", disabled="#cccccc"
            )
            
            theme = Theme(
                name="invalid",
                display_name="Invalid Theme",
                description="An invalid theme",
                colors=colors,
                is_builtin=False
            )
            
            success = manager.save_custom_theme(theme)
            assert success is False
    
    def test_load_custom_themes(self) -> None:
        """Test loading custom themes from directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir) / "themes"
            custom_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a custom theme file
            theme_data = {
                "name": "loaded",
                "display_name": "Loaded Theme",
                "description": "A loaded theme",
                "colors": {
                    "surface": "#ffffff", "panel": "#f0f0f0", "panel_darken": "#e0e0e0",
                    "primary": "#333333", "primary_darken": "#000000", "accent": "#666666",
                    "text": "#000000", "text_muted": "#666666", "text_inverse": "#ffffff",
                    "text_secondary": "#333333", "border": "#999999", "border_highlight": "#666666",
                    "border_panel": "#cccccc", "success": "#333333", "warning": "#666666",
                    "error": "#000000", "info": "#666666", "git_modified": "#666666",
                    "git_added": "#333333", "git_deleted": "#000000", "git_untracked": "#999999",
                    "highlight": "#cccccc", "hover": "#e0e0e0", "active": "#666666", "disabled": "#cccccc"
                },
                "is_builtin": False,
                "variant": "default"
            }
            
            theme_file = custom_dir / "loaded.json"
            with open(theme_file, "w", encoding="utf-8") as f:
                json.dump(theme_data, f)
            
            # Create manager and check theme is loaded
            manager = ThemeManager(custom_themes_dir=custom_dir)
            assert "loaded" in manager
            assert manager.get_theme("loaded") is not None
            assert manager.get_theme("loaded").is_builtin is False
    
    def test_delete_custom_theme(self) -> None:
        """Test deleting custom themes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir) / "themes"
            manager = ThemeManager(custom_themes_dir=custom_dir)
            
            colors = ThemeColors(
                surface="#ffffff", panel="#f0f0f0", panel_darken="#e0e0e0",
                primary="#333333", primary_darken="#000000", accent="#666666",
                text="#000000", text_muted="#666666", text_inverse="#ffffff",
                text_secondary="#333333", border="#999999", border_highlight="#666666",
                border_panel="#cccccc", success="#333333", warning="#666666",
                error="#000000", info="#666666", git_modified="#666666",
                git_added="#333333", git_deleted="#000000", git_untracked="#999999",
                highlight="#cccccc", hover="#e0e0e0", active="#666666", disabled="#cccccc"
            )
            
            theme = Theme(
                name="deletable",
                display_name="Deletable Theme",
                description="A deletable theme",
                colors=colors,
                is_builtin=False
            )
            
            # Save theme first
            manager.save_custom_theme(theme)
            assert "deletable" in manager
            
            # Delete theme
            success = manager.delete_custom_theme("deletable")
            assert success is True
            assert "deletable" not in manager
            
            # Check file is deleted
            theme_file = custom_dir / "deletable.json"
            assert not theme_file.exists()
    
    def test_delete_builtin_theme(self) -> None:
        """Test that built-in themes cannot be deleted."""
        manager = ThemeManager()
        
        success = manager.delete_custom_theme("dark")
        assert success is False
        assert "dark" in manager  # Should still be there
    
    def test_delete_nonexistent_theme(self) -> None:
        """Test deleting non-existent theme."""
        manager = ThemeManager()
        
        success = manager.delete_custom_theme("nonexistent")
        assert success is False
    
    def test_export_theme(self) -> None:
        """Test exporting theme configuration."""
        manager = ThemeManager()
        
        data = manager.export_theme("dark")
        assert data is not None
        assert data["name"] == "dark"
        assert data["display_name"] == "Dark"
        assert "colors" in data
        
        # Test non-existent theme
        data = manager.export_theme("nonexistent")
        assert data is None
    
    def test_import_theme(self) -> None:
        """Test importing theme configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir) / "themes"
            manager = ThemeManager(custom_themes_dir=custom_dir)
            
            theme_data = {
                "name": "imported",
                "display_name": "Imported Theme",
                "description": "An imported theme",
                "colors": {
                    "surface": "#ffffff", "panel": "#f0f0f0", "panel_darken": "#e0e0e0",
                    "primary": "#333333", "primary_darken": "#000000", "accent": "#666666",
                    "text": "#000000", "text_muted": "#666666", "text_inverse": "#ffffff",
                    "text_secondary": "#333333", "border": "#999999", "border_highlight": "#666666",
                    "border_panel": "#cccccc", "success": "#333333", "warning": "#666666",
                    "error": "#000000", "info": "#666666", "git_modified": "#666666",
                    "git_added": "#333333", "git_deleted": "#000000", "git_untracked": "#999999",
                    "highlight": "#cccccc", "hover": "#e0e0e0", "active": "#666666", "disabled": "#cccccc"
                },
                "is_builtin": False,
                "variant": "default"
            }
            
            # Import theme
            success = manager.import_theme(theme_data)
            assert success is True
            assert "imported" in manager
            
            # Try to import again without overwrite
            success = manager.import_theme(theme_data, overwrite=False)
            assert success is False
            
            # Import again with overwrite
            success = manager.import_theme(theme_data, overwrite=True)
            assert success is True
    
    def test_import_invalid_theme(self) -> None:
        """Test importing invalid theme configuration."""
        manager = ThemeManager()
        
        # Invalid theme data (missing required fields)
        invalid_data = {
            "name": "invalid",
            "display_name": "Invalid Theme",
            # Missing colors and other required fields
        }
        
        success = manager.import_theme(invalid_data)
        assert success is False
    
    def test_get_theme_info(self) -> None:
        """Test getting theme information."""
        manager = ThemeManager()
        
        info = manager.get_theme_info("dark")
        assert info is not None
        assert info["name"] == "dark"
        assert info["display_name"] == "Dark"
        assert info["is_builtin"] is True
        assert info["color_count"] == 24
        
        # Test non-existent theme
        info = manager.get_theme_info("nonexistent")
        assert info is None
    
    def test_contains_operator(self) -> None:
        """Test the 'in' operator for themes."""
        manager = ThemeManager()
        
        assert "dark" in manager
        assert "light" in manager
        assert "nonexistent" not in manager
    
    def test_iteration(self) -> None:
        """Test iterating over themes."""
        manager = ThemeManager()
        
        themes = list(manager)
        assert len(themes) >= 8
        
        theme_names = [theme.name for theme in themes]
        assert "dark" in theme_names
        assert "light" in theme_names
    
    def test_repr(self) -> None:
        """Test string representation."""
        manager = ThemeManager()
        
        repr_str = repr(manager)
        assert "ThemeManager" in repr_str
        assert "themes=" in repr_str
        assert "current=" in repr_str
