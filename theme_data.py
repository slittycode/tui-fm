"""Theme data structures and built-in themes for the File Manager."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ThemeColors:
    """Color definitions for a theme."""
    # Background colors
    surface: str
    panel: str
    panel_darken: str
    primary: str
    primary_darken: str
    accent: str
    
    # Text colors
    text: str
    text_muted: str
    text_inverse: str
    text_secondary: str
    
    # Border colors
    border: str
    border_highlight: str
    border_panel: str
    
    # Status colors
    success: str
    warning: str
    error: str
    info: str
    
    # Git status colors
    git_modified: str
    git_added: str
    git_deleted: str
    git_untracked: str
    
    # Additional UI colors
    highlight: str
    hover: str
    active: str
    disabled: str


@dataclass
class Theme:
    """Complete theme definition."""
    name: str
    display_name: str
    description: str
    colors: ThemeColors
    is_builtin: bool = True
    variant: str = "default"  # default, light, dark
    
    def to_dict(self) -> dict:
        """Convert theme to dictionary for serialization."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "colors": {
                "surface": self.colors.surface,
                "panel": self.colors.panel,
                "panel_darken": self.colors.panel_darken,
                "primary": self.colors.primary,
                "primary_darken": self.colors.primary_darken,
                "accent": self.colors.accent,
                "text": self.colors.text,
                "text_muted": self.colors.text_muted,
                "text_inverse": self.colors.text_inverse,
                "text_secondary": self.colors.text_secondary,
                "border": self.colors.border,
                "border_highlight": self.colors.border_highlight,
                "border_panel": self.colors.border_panel,
                "success": self.colors.success,
                "warning": self.colors.warning,
                "error": self.colors.error,
                "info": self.colors.info,
                "git_modified": self.colors.git_modified,
                "git_added": self.colors.git_added,
                "git_deleted": self.colors.git_deleted,
                "git_untracked": self.colors.git_untracked,
                "highlight": self.colors.highlight,
                "hover": self.colors.hover,
                "active": self.colors.active,
                "disabled": self.colors.disabled,
            },
            "is_builtin": self.is_builtin,
            "variant": self.variant,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        """Create theme from dictionary."""
        colors_data = data["colors"]
        colors = ThemeColors(
            surface=colors_data["surface"],
            panel=colors_data["panel"],
            panel_darken=colors_data["panel_darken"],
            primary=colors_data["primary"],
            primary_darken=colors_data["primary_darken"],
            accent=colors_data["accent"],
            text=colors_data["text"],
            text_muted=colors_data["text_muted"],
            text_inverse=colors_data["text_inverse"],
            text_secondary=colors_data["text_secondary"],
            border=colors_data["border"],
            border_highlight=colors_data["border_highlight"],
            border_panel=colors_data["border_panel"],
            success=colors_data["success"],
            warning=colors_data["warning"],
            error=colors_data["error"],
            info=colors_data["info"],
            git_modified=colors_data["git_modified"],
            git_added=colors_data["git_added"],
            git_deleted=colors_data["git_deleted"],
            git_untracked=colors_data["git_untracked"],
            highlight=colors_data["highlight"],
            hover=colors_data["hover"],
            active=colors_data["active"],
            disabled=colors_data["disabled"],
        )
        
        return cls(
            name=data["name"],
            display_name=data["display_name"],
            description=data["description"],
            colors=colors,
            is_builtin=data.get("is_builtin", True),
            variant=data.get("variant", "default"),
        )


# Built-in themes
BUILTIN_THEMES = {
    "dark": Theme(
        name="dark",
        display_name="Dark",
        description="Classic dark theme with high contrast",
        colors=ThemeColors(
            surface="#1a1a1a",
            panel="#2d2d2d",
            panel_darken="#1f1f1f",
            primary="#005f5f",
            primary_darken="#004f4f",
            accent="#87ceeb",
            text="#ffffff",
            text_muted="#999999",
            text_inverse="#000000",
            text_secondary="#cccccc",
            border="#444444",
            border_highlight="#666666",
            border_panel="#333333",
            success="#00ff00",
            warning="#ffff00",
            error="#ff0000",
            info="#00ffff",
            git_modified="#ffff00",
            git_added="#00ff00",
            git_deleted="#ff0000",
            git_untracked="#00ffff",
            highlight="#006666",
            hover="#003333",
            active="#008888",
            disabled="#555555",
        )
    ),
    
    "light": Theme(
        name="light",
        display_name="Light",
        description="Clean light theme optimized for daytime use",
        colors=ThemeColors(
            surface="#ffffff",
            panel="#f5f5f5",
            panel_darken="#e8e8e8",
            primary="#007acc",
            primary_darken="#005a9e",
            accent="#ff6b35",
            text="#333333",
            text_muted="#666666",
            text_inverse="#ffffff",
            text_secondary="#555555",
            border="#cccccc",
            border_highlight="#999999",
            border_panel="#dddddd",
            success="#28a745",
            warning="#ffc107",
            error="#dc3545",
            info="#17a2b8",
            git_modified="#ffc107",
            git_added="#28a745",
            git_deleted="#dc3545",
            git_untracked="#17a2b8",
            highlight="#0066cc",
            hover="#004499",
            active="#0077ff",
            disabled="#cccccc",
        )
    ),
    
    "monochrome": Theme(
        name="monochrome",
        display_name="Monochrome",
        description="Black and white theme for maximum clarity",
        colors=ThemeColors(
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
    ),
    
    "ocean": Theme(
        name="ocean",
        display_name="Ocean",
        description="Blue-based theme inspired by the sea",
        colors=ThemeColors(
            surface="#0f1419",
            panel="#1a2332",
            panel_darken="#0d1117",
            primary="#0969da",
            primary_darken="#0550ae",
            accent="#58a6ff",
            text="#c9d1d9",
            text_muted="#8b949e",
            text_inverse="#0f1419",
            text_secondary="#e6edf3",
            border="#30363d",
            border_highlight="#4a5568",
            border_panel="#21262d",
            success="#3fb950",
            warning="#d29922",
            error="#f85149",
            info="#58a6ff",
            git_modified="#d29922",
            git_added="#3fb950",
            git_deleted="#f85149",
            git_untracked="#58a6ff",
            highlight="#1f6feb",
            hover="#0d419d",
            active="#2f81f7",
            disabled="#484f58",
        )
    ),
    
    "forest": Theme(
        name="forest",
        display_name="Forest",
        description="Green-based theme inspired by nature",
        colors=ThemeColors(
            surface="#1a2f1a",
            panel="#2d4a2d",
            panel_darken="#1f2f1f",
            primary="#228b22",
            primary_darken="#1a6b1a",
            accent="#90ee90",
            text="#e0f0e0",
            text_muted="#a0c0a0",
            text_inverse="#1a2f1a",
            text_secondary="#d0e8d0",
            border="#3d5a3d",
            border_highlight="#5a7a5a",
            border_panel="#2d4a2d",
            success="#32cd32",
            warning="#daa520",
            error="#ff6b6b",
            info="#87ceeb",
            git_modified="#daa520",
            git_added="#32cd32",
            git_deleted="#ff6b6b",
            git_untracked="#87ceeb",
            highlight="#2e8b57",
            hover="#1f5f1f",
            active="#3cb371",
            disabled="#4a5a4a",
        )
    ),
    
    "sunset": Theme(
        name="sunset",
        display_name="Sunset",
        description="Warm orange/red theme inspired by sunset colors",
        colors=ThemeColors(
            surface="#2a1a1a",
            panel="#4a2d2d",
            panel_darken="#3a1f1f",
            primary="#cc5500",
            primary_darken="#aa4400",
            accent="#ff8c69",
            text="#f0e0e0",
            text_muted="#c0a0a0",
            text_inverse="#2a1a1a",
            text_secondary="#e8d0d0",
            border="#5a3d3d",
            border_highlight="#7a5a5a",
            border_panel="#4a2d2d",
            success="#ff8c00",
            warning="#ffd700",
            error="#ff4444",
            info="#87ceeb",
            git_modified="#ffd700",
            git_added="#ff8c00",
            git_deleted="#ff4444",
            git_untracked="#87ceeb",
            highlight="#cc6600",
            hover="#aa4400",
            active="#ff7733",
            disabled="#5a4a4a",
        )
    ),
    
    "cyberpunk": Theme(
        name="cyberpunk",
        display_name="Cyberpunk",
        description="Neon theme with cyberpunk aesthetics",
        colors=ThemeColors(
            surface="#0a0a0a",
            panel="#1a0f1f",
            panel_darken="#0d050d",
            primary="#ff00ff",
            primary_darken="#cc00cc",
            accent="#00ffff",
            text="#ff00ff",
            text_muted="#cc00cc",
            text_inverse="#0a0a0a",
            text_secondary="#ff66ff",
            border="#ff00ff",
            border_highlight="#00ffff",
            border_panel="#1a0f1f",
            success="#00ff00",
            warning="#ffff00",
            error="#ff0066",
            info="#00ffff",
            git_modified="#ffff00",
            git_added="#00ff00",
            git_deleted="#ff0066",
            git_untracked="#00ffff",
            highlight="#ff33ff",
            hover="#cc00cc",
            active="#ff66ff",
            disabled="#4a004a",
        )
    ),
    
    "nord": Theme(
        name="nord",
        display_name="Nord",
        description="Nord-inspired theme with cool, muted colors",
        colors=ThemeColors(
            surface="#2e3440",
            panel="#3b4252",
            panel_darken="#242933",
            primary="#5e81ac",
            primary_darken="#4c566a",
            accent="#88c0d0",
            text="#d8dee9",
            text_muted="#4c566a",
            text_inverse="#2e3440",
            text_secondary="#e5e9f0",
            border="#434c5e",
            border_highlight="#616e88",
            border_panel="#3b4252",
            success="#a3be8c",
            warning="#ebcb8b",
            error="#bf616a",
            info="#88c0d0",
            git_modified="#ebcb8b",
            git_added="#a3be8c",
            git_deleted="#bf616a",
            git_untracked="#88c0d0",
            highlight="#5e81ac",
            hover="#4c566a",
            active="#81a1c1",
            disabled="#4c566a",
        )
    ),
}


def get_builtin_theme(name: str) -> Optional[Theme]:
    """Get a built-in theme by name.
    
    Args:
        name: Theme name.
        
    Returns:
        Theme if found, None otherwise.
    """
    return BUILTIN_THEMES.get(name)


def list_builtin_themes() -> list[Theme]:
    """List all built-in themes.
    
    Returns:
        List of built-in themes.
    """
    return list(BUILTIN_THEMES.values())


def validate_theme(theme: Theme) -> list[str]:
    """Validate a theme for completeness.
    
    Args:
        theme: Theme to validate.
        
    Returns:
        List of validation errors (empty if valid).
    """
    errors = []
    
    # Check required fields
    if not theme.name:
        errors.append("Theme name is required")
    
    if not theme.display_name:
        errors.append("Theme display name is required")
    
    if not theme.description:
        errors.append("Theme description is required")
    
    # Check color values (basic validation)
    color_fields = [
        "surface", "panel", "panel_darken", "primary", "primary_darken", "accent",
        "text", "text_muted", "text_inverse", "text_secondary",
        "border", "border_highlight", "border_panel",
        "success", "warning", "error", "info",
        "git_modified", "git_added", "git_deleted", "git_untracked",
        "highlight", "hover", "active", "disabled"
    ]
    
    for field in color_fields:
        color_value = getattr(theme.colors, field, None)
        if not color_value:
            errors.append(f"Color {field} is required")
        elif not color_value.startswith("#") or len(color_value) != 7:
            errors.append(f"Invalid color format for {field}: {color_value}")
    
    return errors
