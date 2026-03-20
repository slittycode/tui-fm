"""Tests for go-to-path resolution behavior."""

from pathlib import Path

from app import FileManagerApp


def test_resolve_directory_input_absolute(tmp_path: Path) -> None:
    """Absolute paths should resolve to themselves."""
    target = tmp_path / "target"
    target.mkdir()

    resolved = FileManagerApp._resolve_directory_input(str(target), tmp_path)

    assert resolved == target.resolve()


def test_resolve_directory_input_relative(tmp_path: Path) -> None:
    """Relative paths should resolve from the active tab path."""
    base = tmp_path / "base"
    base.mkdir()

    resolved = FileManagerApp._resolve_directory_input("nested/folder", base)

    assert resolved == (base / "nested/folder").resolve()


def test_resolve_directory_input_tilde_expansion(tmp_path: Path) -> None:
    """Tilde paths should expand to the current user's home directory."""
    resolved = FileManagerApp._resolve_directory_input("~/", tmp_path)

    assert resolved == Path.home().resolve()
