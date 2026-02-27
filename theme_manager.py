"""Theme management system for the File Manager."""
import json
from pathlib import Path
from typing import Optional

from theme_data import Theme, list_builtin_themes, validate_theme


class ThemeManager:
    """Manage application themes and CSS generation."""
    
    def __init__(self, custom_themes_dir: Optional[Path] = None) -> None:
        """Initialize the theme manager.
        
        Args:
            custom_themes_dir: Directory for custom themes. Defaults to ~/.tui_fm/themes/
        """
        self.themes: dict[str, Theme] = {}
        self.current_theme: str = "dark"
        
        # Set up custom themes directory
        if custom_themes_dir is None:
            custom_themes_dir = Path.home() / ".tui_fm" / "themes"
        self.custom_themes_dir = custom_themes_dir
        self.custom_themes_dir.mkdir(parents=True, exist_ok=True)
        
        # Load built-in themes
        self._load_builtin_themes()
        
        # Load custom themes
        self._load_custom_themes()
    
    def _load_builtin_themes(self) -> None:
        """Load all built-in themes."""
        for theme in list_builtin_themes():
            self.themes[theme.name] = theme
    
    def _load_custom_themes(self) -> None:
        """Load custom themes from the themes directory."""
        if not self.custom_themes_dir.exists():
            return
        
        for theme_file in self.custom_themes_dir.glob("*.json"):
            try:
                with open(theme_file, encoding="utf-8") as f:
                    theme_data = json.load(f)
                
                theme = Theme.from_dict(theme_data)
                theme.is_builtin = False
                
                # Validate theme before loading
                errors = validate_theme(theme)
                if errors:
                    print(f"Warning: Invalid theme {theme.name}: {', '.join(errors)}")
                    continue
                
                self.themes[theme.name] = theme
                
            except (OSError, json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Warning: Failed to load theme {theme_file}: {e}")
    
    def register_theme(self, theme: Theme) -> bool:
        """Register a new theme.
        
        Args:
            theme: Theme to register.
            
        Returns:
            True if registration was successful, False otherwise.
        """
        # Validate theme
        errors = validate_theme(theme)
        if errors:
            print(f"Cannot register theme {theme.name}: {', '.join(errors)}")
            return False
        
        # Check for name conflicts
        existing_theme = self.themes.get(theme.name)
        if existing_theme and existing_theme.is_builtin:
            print(f"Cannot override built-in theme {theme.name}")
            return False
        
        self.themes[theme.name] = theme
        return True
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name.
        
        Args:
            name: Theme name.
            
        Returns:
            Theme if found, None otherwise.
        """
        return self.themes.get(name)
    
    def set_theme(self, name: str) -> bool:
        """Set the current theme.
        
        Args:
            name: Theme name.
            
        Returns:
            True if theme was set successfully, False otherwise.
        """
        if name not in self.themes:
            print(f"Theme {name} not found")
            return False
        
        self.current_theme = name
        return True
    
    def get_current_theme(self) -> Optional[Theme]:
        """Get the currently active theme.
        
        Returns:
            Current theme or None if not found.
        """
        return self.themes.get(self.current_theme)
    
    def list_themes(self) -> list[Theme]:
        """List all available themes.
        
        Returns:
            List of all themes (built-in and custom).
        """
        return list(self.themes.values())
    
    def list_builtin_themes(self) -> list[Theme]:
        """List built-in themes only.
        
        Returns:
            List of built-in themes.
        """
        return [theme for theme in self.themes.values() if theme.is_builtin]
    
    def list_custom_themes(self) -> list[Theme]:
        """List custom themes only.
        
        Returns:
            List of custom themes.
        """
        return [theme for theme in self.themes.values() if not theme.is_builtin]
    
    def generate_css(self, theme: Optional[Theme] = None) -> str:
        """Generate CSS for a theme.
        
        Args:
            theme: Theme to generate CSS for. Uses current theme if None.
            
        Returns:
            CSS string for the theme.
        """
        if theme is None:
            theme = self.get_current_theme()
            if theme is None:
                return ""
        
        colors = theme.colors
        
        css = f"""
/* Theme: {theme.display_name} */
Screen {{
    background: {colors.surface};
}}

Header {{
    background: {colors.primary_darken};
    color: {colors.text};
    text-style: bold;
}}

Footer {{
    background: {colors.panel_darken};
    color: {colors.text_muted};
}}

#main-container {{
    layout: horizontal;
    height: 1fr;
    padding: 0;
    margin: 0;
    background: {colors.surface};
}}

#left-pane {{
    width: 40%;
    height: 100%;
    background: {colors.panel};
    border-right: solid {colors.border};
}}

#right-pane {{
    width: 60%;
    height: 100%;
    background: {colors.surface};
}}

#tree-header, #preview-header {{
    background: {colors.panel_darken};
    color: {colors.text};
    text-style: bold;
    padding: 0 1;
    height: 3;
}}

#tree-footer, #preview-footer {{
    background: {colors.panel_darken};
    color: {colors.text_muted};
    padding: 0 1;
    height: 3;
}}

#preview-content {{
    background: {colors.surface};
    color: {colors.text};
    padding: 1;
}}

#status-bar {{
    background: {colors.panel};
    color: {colors.text_secondary};
    padding: 0 1;
    height: 3;
}}

/* Directory Tree */
DirectoryTree, FilterableDirectoryTree {{
    background: {colors.panel};
    color: {colors.text};
}}

DirectoryTree > .directory-tree--cursor {{
    background: {colors.highlight};
    color: {colors.text_inverse};
}}

DirectoryTree > .directory-tree--cursor:hover {{
    background: {colors.hover};
}}

/* Git Status Colors */
.git-modified {{
    color: {colors.git_modified};
    text-style: bold;
}}

.git-added {{
    color: {colors.git_added};
    text-style: bold;
}}

.git-deleted {{
    color: {colors.git_deleted};
    text-style: bold;
}}

.git-untracked {{
    color: {colors.git_untracked};
    text-style: bold;
}}

.git-clean {{
    color: {colors.text_muted};
}}

/* Tab System */
Tabs {{
    background: {colors.panel_darken};
}}

Tab {{
    background: {colors.panel};
    color: {colors.text};
    border: solid {colors.border};
}}

Tab.--active {{
    background: {colors.primary};
    color: {colors.text_inverse};
}}

Tab:hover {{
    background: {colors.hover};
}}

TabPane {{
    background: {colors.surface};
}}

/* Buttons */
Button {{
    background: {colors.primary};
    color: {colors.text_inverse};
    border: solid {colors.border};
}}

Button:hover {{
    background: {colors.hover};
    color: {colors.text};
}}

Button.--primary {{
    background: {colors.accent};
    color: {colors.text_inverse};
}}

/* Inputs */
Input {{
    background: {colors.surface};
    color: {colors.text};
    border: solid {colors.border};
}}

Input:focus {{
    border: solid {colors.accent};
}}

/* Switches */
Switch {{
    background: {colors.panel};
    color: {colors.text};
}}

Switch.--on {{
    background: {colors.success};
}}

/* Status Colors */
.status-success {{
    color: {colors.success};
}}

.status-warning {{
    color: {colors.warning};
}}

.status-error {{
    color: {colors.error};
}}

.status-info {{
    color: {colors.info};
}}

/* File Preview */
.syntax-highlight {{
    color: {colors.text};
}}

.syntax-comment {{
    color: {colors.text_muted};
    font-style: italic;
}}

.syntax-keyword {{
    color: {colors.accent};
    text-style: bold;
}}

.syntax-string {{
    color: {colors.success};
}}

.syntax-number {{
    color: {colors.warning};
}}

.syntax-function {{
    color: {colors.info};
    text-style: bold;
}}

/* Scrollbar */
::-webkit-scrollbar {{
    background: {colors.panel};
    width: 1;
}}

::-webkit-scrollbar-track {{
    background: {colors.panel};
}}

::-webkit-scrollbar-thumb {{
    background: {colors.border_highlight};
}}

::-webkit-scrollbar-thumb:hover {{
    background: {colors.border};
}}

/* Responsive layout */
@media (max-width: 100) {{
    #main-container {{
        layout: vertical;
    }}
    
    #left-pane {{
        width: 100%;
        height: 50%;
        border-right: none;
        border-bottom: solid {colors.border};
    }}
    
    #right-pane {{
        width: 100%;
        height: 50%;
    }}
}}
"""
        
        return css.strip()
    
    def save_custom_theme(self, theme: Theme) -> bool:
        """Save a custom theme to disk.
        
        Args:
            theme: Theme to save.
            
        Returns:
            True if saved successfully, False otherwise.
        """
        if theme.is_builtin:
            print("Cannot save built-in themes")
            return False
        
        # Validate theme
        errors = validate_theme(theme)
        if errors:
            print(f"Cannot save invalid theme: {', '.join(errors)}")
            return False
        
        theme_file = self.custom_themes_dir / f"{theme.name}.json"
        
        try:
            with open(theme_file, "w", encoding="utf-8") as f:
                json.dump(theme.to_dict(), f, indent=2)
            
            # Register the theme
            self.register_theme(theme)
            return True
            
        except (OSError, TypeError) as e:
            print(f"Failed to save theme {theme.name}: {e}")
            return False
    
    def delete_custom_theme(self, name: str) -> bool:
        """Delete a custom theme.
        
        Args:
            name: Theme name to delete.
            
        Returns:
            True if deleted successfully, False otherwise.
        """
        theme = self.themes.get(name)
        if not theme:
            print(f"Theme {name} not found")
            return False
        
        if theme.is_builtin:
            print("Cannot delete built-in themes")
            return False
        
        # Remove from registry
        del self.themes[name]
        
        # Delete file
        theme_file = self.custom_themes_dir / f"{name}.json"
        try:
            if theme_file.exists():
                theme_file.unlink()
            return True
        except OSError as e:
            print(f"Failed to delete theme file {theme_file}: {e}")
            return False
    
    def export_theme(self, name: str) -> Optional[dict]:
        """Export a theme configuration.
        
        Args:
            name: Theme name to export.
            
        Returns:
            Theme dictionary if found, None otherwise.
        """
        theme = self.get_theme(name)
        if not theme:
            return None
        
        return theme.to_dict()
    
    def import_theme(self, theme_data: dict, overwrite: bool = False) -> bool:
        """Import a theme configuration.
        
        Args:
            theme_data: Theme dictionary to import.
            overwrite: Whether to overwrite existing themes.
            
        Returns:
            True if imported successfully, False otherwise.
        """
        try:
            theme = Theme.from_dict(theme_data)
            
            # Check if theme already exists
            if theme.name in self.themes and not overwrite:
                print(f"Theme {theme.name} already exists. Use overwrite=True to replace.")
                return False
            
            # Validate theme
            errors = validate_theme(theme)
            if errors:
                print(f"Cannot import invalid theme: {', '.join(errors)}")
                return False
            
            # Save custom theme
            return self.save_custom_theme(theme)
            
        except (KeyError, TypeError) as e:
            print(f"Failed to import theme: {e}")
            return False
    
    def get_theme_info(self, name: str) -> Optional[dict]:
        """Get information about a theme.
        
        Args:
            name: Theme name.
            
        Returns:
            Theme information dictionary or None if not found.
        """
        theme = self.get_theme(name)
        if not theme:
            return None
        
        return {
            "name": theme.name,
            "display_name": theme.display_name,
            "description": theme.description,
            "is_builtin": theme.is_builtin,
            "variant": theme.variant,
            "color_count": 24,  # Number of color fields in ThemeColors
        }
    
    def __len__(self) -> int:
        """Get the number of available themes."""
        return len(self.themes)
    
    def __contains__(self, name: str) -> bool:
        """Check if a theme exists."""
        return name in self.themes
    
    def __iter__(self):
        """Iterate over themes."""
        return iter(self.themes.values())
    
    def __repr__(self) -> str:
        return f"ThemeManager(themes={len(self)}, current='{self.current_theme}')"
