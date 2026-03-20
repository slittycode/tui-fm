"""Regression tests for startup key bindings."""

from app import FileManagerApp


def test_open_config_binding_uses_comma_key_name() -> None:
    """Ensure config shortcut binding uses Textual's normalized comma key token."""
    config_bindings = [
        binding for binding in FileManagerApp.BINDINGS if binding.action == "open_config"
    ]

    assert config_bindings, "Expected an open_config binding to be defined."
    assert config_bindings[0].key == "comma"
    assert config_bindings[0].key_display == ","


def test_goto_path_binding_exists() -> None:
    """Ensure go-to-path shortcut is available from startup."""
    goto_bindings = [
        binding for binding in FileManagerApp.BINDINGS if binding.action == "goto_path"
    ]

    assert goto_bindings, "Expected a goto_path binding to be defined."
    assert goto_bindings[0].key == "g"
