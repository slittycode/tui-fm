"""Tests for theme data structures and built-in themes."""

from theme_data import (
    BUILTIN_THEMES,
    Theme,
    ThemeColors,
    get_builtin_theme,
    list_builtin_themes,
    validate_theme,
)


class TestThemeColors:
    """Test cases for ThemeColors class."""
    
    def test_theme_colors_initialization(self) -> None:
        """Test ThemeColors initialization."""
        colors = ThemeColors(
            surface="#ffffff",
            panel="#f0f0f0",
            panel_darken="#e0e0e0",
            primary="#333333",
            primary_darken="#000000",
            accent="#666666",
            text="#000000",
            text_muted="#666666",
            text_inverse="#ffffff",
            text_secondary="#333333",
            border="#999999",
            border_highlight="#666666",
            border_panel="#cccccc",
            success="#333333",
            warning="#666666",
            error="#000000",
            info="#666666",
            git_modified="#666666",
            git_added="#333333",
            git_deleted="#000000",
            git_untracked="#999999",
            highlight="#cccccc",
            hover="#e0e0e0",
            active="#666666",
            disabled="#cccccc",
        )
        
        assert colors.surface == "#ffffff"
        assert colors.panel == "#f0f0f0"
        assert colors.text == "#000000"
        assert colors.git_modified == "#666666"


class TestTheme:
    """Test cases for Theme class."""
    
    def test_theme_initialization(self) -> None:
        """Test Theme initialization."""
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
            name="test",
            display_name="Test Theme",
            description="A test theme",
            colors=colors
        )
        
        assert theme.name == "test"
        assert theme.display_name == "Test Theme"
        assert theme.description == "A test theme"
        assert theme.colors is colors
        assert theme.is_builtin is True
        assert theme.variant == "default"
    
    def test_theme_to_dict(self) -> None:
        """Test Theme serialization to dictionary."""
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
            name="test",
            display_name="Test Theme",
            description="A test theme",
            colors=colors,
            is_builtin=False,
            variant="custom"
        )
        
        data = theme.to_dict()
        
        assert data["name"] == "test"
        assert data["display_name"] == "Test Theme"
        assert data["description"] == "A test theme"
        assert data["is_builtin"] is False
        assert data["variant"] == "custom"
        assert "colors" in data
        assert data["colors"]["surface"] == "#ffffff"
    
    def test_theme_from_dict(self) -> None:
        """Test Theme deserialization from dictionary."""
        data = {
            "name": "test",
            "display_name": "Test Theme",
            "description": "A test theme",
            "colors": {
                "surface": "#ffffff",
                "panel": "#f0f0f0",
                "panel_darken": "#e0e0e0",
                "primary": "#333333",
                "primary_darken": "#000000",
                "accent": "#666666",
                "text": "#000000",
                "text_muted": "#666666",
                "text_inverse": "#ffffff",
                "text_secondary": "#333333",
                "border": "#999999",
                "border_highlight": "#666666",
                "border_panel": "#cccccc",
                "success": "#333333",
                "warning": "#666666",
                "error": "#000000",
                "info": "#666666",
                "git_modified": "#666666",
                "git_added": "#333333",
                "git_deleted": "#000000",
                "git_untracked": "#999999",
                "highlight": "#cccccc",
                "hover": "#e0e0e0",
                "active": "#666666",
                "disabled": "#cccccc"
            },
            "is_builtin": False,
            "variant": "custom"
        }
        
        theme = Theme.from_dict(data)
        
        assert theme.name == "test"
        assert theme.display_name == "Test Theme"
        assert theme.description == "A test theme"
        assert theme.is_builtin is False
        assert theme.variant == "custom"
        assert theme.colors.surface == "#ffffff"
        assert theme.colors.text == "#000000"


class TestBuiltinThemes:
    """Test cases for built-in themes."""
    
    def test_builtin_themes_exist(self) -> None:
        """Test that built-in themes are defined."""
        expected_themes = [
            "dark", "light", "monochrome", "ocean",
            "forest", "sunset", "cyberpunk", "nord"
        ]
        
        for theme_name in expected_themes:
            assert theme_name in BUILTIN_THEMES
            theme = BUILTIN_THEMES[theme_name]
            assert isinstance(theme, Theme)
            assert theme.name == theme_name
            assert theme.is_builtin is True
    
    def test_get_builtin_theme(self) -> None:
        """Test getting built-in themes by name."""
        theme = get_builtin_theme("dark")
        assert theme is not None
        assert theme.name == "dark"
        assert theme.display_name == "Dark"
        assert theme.is_builtin is True
        
        # Test non-existent theme
        theme = get_builtin_theme("nonexistent")
        assert theme is None
    
    def test_list_builtin_themes(self) -> None:
        """Test listing all built-in themes."""
        themes = list_builtin_themes()
        
        assert len(themes) == 8
        theme_names = [theme.name for theme in themes]
        expected_names = [
            "dark", "light", "monochrome", "ocean",
            "forest", "sunset", "cyberpunk", "nord"
        ]
        
        for name in expected_names:
            assert name in theme_names
    
    def test_dark_theme_structure(self) -> None:
        """Test dark theme structure."""
        theme = get_builtin_theme("dark")
        assert theme is not None
        
        colors = theme.colors
        assert colors.surface == "#1a1a1a"
        assert colors.panel == "#2d2d2d"
        assert colors.text == "#ffffff"
        assert colors.primary == "#005f5f"
        assert colors.git_modified == "#ffff00"
        assert colors.git_added == "#00ff00"
    
    def test_light_theme_structure(self) -> None:
        """Test light theme structure."""
        theme = get_builtin_theme("light")
        assert theme is not None
        
        colors = theme.colors
        assert colors.surface == "#ffffff"
        assert colors.panel == "#f5f5f5"
        assert colors.text == "#333333"
        assert colors.primary == "#007acc"
        assert colors.git_modified == "#ffc107"
        assert colors.git_added == "#28a745"
    
    def test_monochrome_theme_structure(self) -> None:
        """Test monochrome theme structure."""
        theme = get_builtin_theme("monochrome")
        assert theme is not None
        
        colors = theme.colors
        assert colors.surface == "#ffffff"
        assert colors.panel == "#f0f0f0"
        assert colors.text == "#000000"
        # All colors should be grayscale
        assert all(c.startswith("#") and all(ch in "0123456789abcdef" for ch in c[1:])
                  for c in [colors.surface, colors.panel, colors.text, colors.primary])
    
    def test_ocean_theme_structure(self) -> None:
        """Test ocean theme structure."""
        theme = get_builtin_theme("ocean")
        assert theme is not None
        
        colors = theme.colors
        assert colors.surface == "#0f1419"
        assert colors.primary == "#0969da"
        assert colors.accent == "#58a6ff"
        # Should be blue-based
        assert "blue" in theme.description.lower() or "sea" in theme.description.lower()
    
    def test_forest_theme_structure(self) -> None:
        """Test forest theme structure."""
        theme = get_builtin_theme("forest")
        assert theme is not None
        
        colors = theme.colors
        assert colors.surface == "#1a2f1a"
        assert colors.primary == "#228b22"
        assert colors.git_added == "#32cd32"
        # Should be green-based
        assert "green" in theme.description.lower() or "nature" in theme.description.lower()
    
    def test_sunset_theme_structure(self) -> None:
        """Test sunset theme structure."""
        theme = get_builtin_theme("sunset")
        assert theme is not None
        
        colors = theme.colors
        assert colors.surface == "#2a1a1a"
        assert colors.primary == "#cc5500"
        assert colors.accent == "#ff8c69"
        # Should be warm colors
        assert "warm" in theme.description.lower() or "sunset" in theme.description.lower()
    
    def test_cyberpunk_theme_structure(self) -> None:
        """Test cyberpunk theme structure."""
        theme = get_builtin_theme("cyberpunk")
        assert theme is not None
        
        colors = theme.colors
        assert colors.surface == "#0a0a0a"
        assert colors.primary == "#ff00ff"
        assert colors.accent == "#00ffff"
        # Should be neon colors
        assert "neon" in theme.description.lower() or "cyber" in theme.description.lower()
    
    def test_nord_theme_structure(self) -> None:
        """Test Nord theme structure."""
        theme = get_builtin_theme("nord")
        assert theme is not None
        
        colors = theme.colors
        assert colors.surface == "#2e3440"
        assert colors.primary == "#5e81ac"
        assert colors.accent == "#88c0d0"
        # Should be Nord-inspired
        assert "nord" in theme.description.lower()


class TestThemeValidation:
    """Test cases for theme validation."""
    
    def test_valid_theme_validation(self) -> None:
        """Test validation of a valid theme."""
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
            name="valid",
            display_name="Valid Theme",
            description="A valid theme",
            colors=colors
        )
        
        errors = validate_theme(theme)
        assert errors == []
    
    def test_invalid_theme_missing_name(self) -> None:
        """Test validation of theme with missing name."""
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
            name="",
            display_name="Invalid Theme",
            description="An invalid theme",
            colors=colors
        )
        
        errors = validate_theme(theme)
        assert "Theme name is required" in errors
    
    def test_invalid_theme_missing_display_name(self) -> None:
        """Test validation of theme with missing display name."""
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
            name="invalid",
            display_name="",
            description="An invalid theme",
            colors=colors
        )
        
        errors = validate_theme(theme)
        assert "Theme display name is required" in errors
    
    def test_invalid_theme_missing_description(self) -> None:
        """Test validation of theme with missing description."""
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
            name="invalid",
            display_name="Invalid Theme",
            description="",
            colors=colors
        )
        
        errors = validate_theme(theme)
        assert "Theme description is required" in errors
    
    def test_invalid_theme_missing_color(self) -> None:
        """Test validation of theme with missing color."""
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
            colors=colors
        )
        
        errors = validate_theme(theme)
        assert "Color surface is required" in errors
    
    def test_invalid_theme_wrong_color_format(self) -> None:
        """Test validation of theme with wrong color format."""
        colors = ThemeColors(
            surface="white", panel="#f0f0f0", panel_darken="#e0e0e0",
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
            colors=colors
        )
        
        errors = validate_theme(theme)
        assert "Invalid color format for surface: white" in errors
    
    def test_invalid_theme_wrong_color_length(self) -> None:
        """Test validation of theme with wrong color length."""
        colors = ThemeColors(
            surface="#fff", panel="#f0f0f0", panel_darken="#e0e0e0",
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
            colors=colors
        )
        
        errors = validate_theme(theme)
        assert "Invalid color format for surface: #fff" in errors
    
    def test_validate_builtin_themes(self) -> None:
        """Test that all built-in themes are valid."""
        for theme in list_builtin_themes():
            errors = validate_theme(theme)
            assert errors == [], f"Built-in theme {theme.name} has validation errors: {errors}"
