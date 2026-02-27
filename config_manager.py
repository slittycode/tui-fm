"""Configuration management for the File Manager."""
import json
from pathlib import Path
from typing import Any, Optional


class ConfigManager:
    """Manages user preferences and application settings."""

    DEFAULT_CONFIG = {
        "default_path": "~",
        "theme": "dark",
        "preview_size_limit": 1_000_000,  # 1MB
        "preview_char_limit": 10000,
        "ignored_patterns": [".git", "__pycache__", "node_modules", ".venv", "venv"],
        "show_hidden_files": False,
        "syntax_highlighting": True,
        "line_numbers": True,
        "confirm_delete": True,
        "auto_refresh": True,
    }

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. Defaults to ~/.tui_fm_config.json
        """
        if config_path is None:
            self.config_path = Path.home() / ".tui_fm_config.json"
        else:
            self.config_path = config_path
        self._config: dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, encoding="utf-8") as f:
                    self._config = json.load(f)
            except (OSError, json.JSONDecodeError):
                # If config is corrupted, use defaults
                self._config = {}
        else:
            self._config = {}

    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)
        except OSError as e:
            raise RuntimeError(f"Failed to save configuration: {e}") from e

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: The configuration key.
            default: Default value if key doesn't exist.
            
        Returns:
            The configuration value or default.
        """
        if key in self._config:
            return self._config[key]
        return self.DEFAULT_CONFIG.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: The configuration key.
            value: The value to set.
        """
        self._config[key] = value

    def reset(self, key: Optional[str] = None) -> None:
        """Reset configuration to defaults.
        
        Args:
            key: If provided, reset only this key. Otherwise reset all.
        """
        if key is None:
            self._config = {}
        elif key in self._config:
            del self._config[key]

    @property
    def default_path(self) -> Path:
        """Get the default starting path."""
        path_str = self.get("default_path", "~")
        return Path(path_str).expanduser()

    @default_path.setter
    def default_path(self, path: Path) -> None:
        """Set the default starting path."""
        self.set("default_path", str(path))

    @property
    def theme(self) -> str:
        """Get the current theme."""
        return str(self.get("theme", "dark"))

    @theme.setter
    def theme(self, theme: str) -> None:
        """Set the theme."""
        self.set("theme", theme)

    @property
    def preview_size_limit(self) -> int:
        """Get the preview file size limit in bytes."""
        return int(self.get("preview_size_limit", 1_000_000))

    @preview_size_limit.setter
    def preview_size_limit(self, limit: int) -> None:
        """Set the preview file size limit."""
        self.set("preview_size_limit", limit)

    @property
    def show_hidden_files(self) -> bool:
        """Get whether to show hidden files."""
        return bool(self.get("show_hidden_files", False))

    @show_hidden_files.setter
    def show_hidden_files(self, show: bool) -> None:
        """Set whether to show hidden files."""
        self.set("show_hidden_files", show)

    @property
    def ignored_patterns(self) -> list[str]:
        """Get the list of ignored directory patterns."""
        # type ignore needed for Any return from get() method
        return self.get("ignored_patterns", self.DEFAULT_CONFIG["ignored_patterns"])  # type: ignore[return-value, no-any-return]

    def to_dict(self) -> dict[str, Any]:
        """Get the full configuration as a dictionary."""
        result = self.DEFAULT_CONFIG.copy()
        result.update(self._config)
        return result

    def __repr__(self) -> str:
        return f"ConfigManager(config_path={self.config_path})"
