"""Tests for ConfigManager."""
import json
from pathlib import Path

from config_manager import ConfigManager


class TestConfigManager:
    """Tests for the ConfigManager class."""

    def test_default_config(self, temp_dir: Path) -> None:
        """Should use default config when no file exists."""
        config_path = temp_dir / "config.json"
        config = ConfigManager(config_path)

        assert config.theme == "dark"
        assert config.preview_size_limit == 1_000_000
        assert config.show_hidden_files is False

    def test_load_from_file(self, temp_dir: Path) -> None:
        """Should load config from file."""
        config_path = temp_dir / "config.json"
        config_data = {"theme": "light", "show_hidden_files": True}
        config_path.write_text(json.dumps(config_data))

        config = ConfigManager(config_path)
        assert config.theme == "light"
        assert config.show_hidden_files is True

    def test_save_to_file(self, temp_dir: Path) -> None:
        """Should save config to file."""
        config_path = temp_dir / "config.json"
        config = ConfigManager(config_path)

        config.theme = "light"
        config.show_hidden_files = True
        config.save()

        assert config_path.exists()
        loaded = json.loads(config_path.read_text())
        assert loaded["theme"] == "light"
        assert loaded["show_hidden_files"] is True

    def test_get_set(self, temp_dir: Path) -> None:
        """Should get and set values."""
        config_path = temp_dir / "config.json"
        config = ConfigManager(config_path)

        config.set("custom_key", "custom_value")
        assert config.get("custom_key") == "custom_value"

    def test_get_with_default(self, temp_dir: Path) -> None:
        """Should return default for missing keys."""
        config_path = temp_dir / "config.json"
        config = ConfigManager(config_path)

        assert config.get("nonexistent", "default") == "default"

    def test_reset_key(self, temp_dir: Path) -> None:
        """Should reset individual key."""
        config_path = temp_dir / "config.json"
        config_data = {"theme": "light"}
        config_path.write_text(json.dumps(config_data))

        config = ConfigManager(config_path)
        assert config.theme == "light"

        config.reset("theme")
        assert config.theme == "dark"

    def test_reset_all(self, temp_dir: Path) -> None:
        """Should reset all keys."""
        config_path = temp_dir / "config.json"
        config_data = {"theme": "light", "show_hidden_files": True}
        config_path.write_text(json.dumps(config_data))

        config = ConfigManager(config_path)
        config.reset()

        assert config.theme == "dark"
        assert config.show_hidden_files is False

    def test_default_path_property(self, temp_dir: Path) -> None:
        """Should handle default_path property."""
        config_path = temp_dir / "config.json"
        config = ConfigManager(config_path)

        assert config.default_path == Path.home()

        config.default_path = temp_dir / "test"
        assert config.default_path == temp_dir / "test"

    def test_theme_property(self, temp_dir: Path) -> None:
        """Should handle theme property."""
        config_path = temp_dir / "config.json"
        config = ConfigManager(config_path)

        config.theme = "light"
        assert config.theme == "light"
        assert config.get("theme") == "light"

    def test_preview_size_limit_property(self, temp_dir: Path) -> None:
        """Should handle preview_size_limit property."""
        config_path = temp_dir / "config.json"
        config = ConfigManager(config_path)

        config.preview_size_limit = 2_000_000
        assert config.preview_size_limit == 2_000_000

    def test_ignored_patterns(self, temp_dir: Path) -> None:
        """Should handle ignored patterns."""
        config_path = temp_dir / "config.json"
        config = ConfigManager(config_path)

        patterns = config.ignored_patterns
        assert ".git" in patterns
        assert "node_modules" in patterns

    def test_to_dict(self, temp_dir: Path) -> None:
        """Should return merged config dict."""
        config_path = temp_dir / "config.json"
        config_data = {"theme": "light"}
        config_path.write_text(json.dumps(config_data))

        config = ConfigManager(config_path)
        result = config.to_dict()

        assert result["theme"] == "light"
        assert "preview_size_limit" in result  # From defaults

    def test_corrupted_config(self, temp_dir: Path) -> None:
        """Should handle corrupted config file."""
        config_path = temp_dir / "config.json"
        config_path.write_text("not valid json{{{")

        config = ConfigManager(config_path)
        # Should use defaults
        assert config.theme == "dark"
