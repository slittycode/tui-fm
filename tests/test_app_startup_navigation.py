"""Regression tests for startup tree mounting and path navigation behavior."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from textual.widgets import Input

import app as app_module
from app import FileManagerApp
from tabbed_directory_tree import TabbedDirectoryTree


def _make_app(start_path: Path) -> FileManagerApp:
    """Create an app instance rooted to a controlled test directory."""
    app = FileManagerApp()
    app.current_path = start_path
    return app


@pytest.mark.asyncio
async def test_startup_mounts_active_tree(tmp_path: Path) -> None:
    """Tree widget should be mounted and active at startup."""
    app = _make_app(tmp_path)

    async with app.run_test() as pilot:
        await pilot.pause(0.05)
        tabbed_tree = app.query_one("#tree", TabbedDirectoryTree)
        assert tabbed_tree.get_active_tree() is not None


@pytest.mark.asyncio
async def test_startup_focuses_active_tree(tmp_path: Path) -> None:
    """Initial focus should land on the directory tree, not command input."""
    app = _make_app(tmp_path)

    async with app.run_test() as pilot:
        await pilot.pause(0.05)
        tabbed_tree = app.query_one("#tree", TabbedDirectoryTree)
        assert app.focused is tabbed_tree.get_active_tree()


@pytest.mark.asyncio
async def test_goto_path_changes_active_root(tmp_path: Path) -> None:
    """Go-to-path should switch the active tab root directory."""
    start_root = tmp_path / "start"
    destination = tmp_path / "destination"
    start_root.mkdir()
    destination.mkdir()
    app = _make_app(start_root)

    async with app.run_test() as pilot:
        await pilot.pause(0.05)
        tabbed_tree = app.query_one("#tree", TabbedDirectoryTree)
        command_input = app.query_one("#command-input", Input)

        app.action_goto_path()
        assert app.command_mode == "goto"
        assert command_input.value == str(start_root)

        event = SimpleNamespace(input=command_input, value=str(destination))
        app.on_input_submitted(event)

        assert tabbed_tree.get_active_path() == destination.resolve()


@pytest.mark.asyncio
async def test_quit_shortcut_not_swallowed_by_input(tmp_path: Path) -> None:
    """Pressing q from startup should quit rather than type into command input."""
    app = _make_app(tmp_path)

    async with app.run_test() as pilot:
        await pilot.pause(0.05)
        command_input = app.query_one("#command-input", Input)
        assert command_input.value == ""

        await pilot.press("q")
        await pilot.pause(0.05)
        assert not app.is_running
        assert command_input.value == ""


@pytest.mark.asyncio
async def test_disk_and_git_actions_use_active_root_helper(tmp_path: Path, monkeypatch) -> None:
    """Disk/Git actions should use the active root path source consistently."""
    app = _make_app(tmp_path)
    target_root = tmp_path / "active-root"
    target_root.mkdir()

    summary = SimpleNamespace(
        total_size=0,
        total_files=0,
        total_dirs=0,
        largest_files=[],
        file_type_distribution={},
        subdirectory_sizes={},
    )
    disk_calls: list[Path] = []

    def fake_get_active_root_path() -> Path:
        return target_root

    def fake_analyze_directory(path: Path, max_depth: int = 2):
        disk_calls.append(path)
        return summary

    def fake_get_disk_usage(path: Path) -> tuple[int, int, int]:
        return (0, 0, 0)

    def fake_get_disk_space_percentage(path: Path) -> tuple[float, float]:
        return (0.0, 100.0)

    def fake_format_size(size: int) -> str:
        return "0 B"

    git_init_paths: list[Path] = []

    class FakeEnhancedGitService:
        def __init__(self, path: Path) -> None:
            git_init_paths.append(path)

        def is_git_repository(self) -> bool:
            return False

    monkeypatch.setattr(app, "_get_active_root_path", fake_get_active_root_path)
    monkeypatch.setattr(app.disk_usage_service, "analyze_directory", fake_analyze_directory)
    monkeypatch.setattr(app.disk_usage_service, "get_disk_usage", fake_get_disk_usage)
    monkeypatch.setattr(
        app.disk_usage_service,
        "get_disk_space_percentage",
        fake_get_disk_space_percentage,
    )
    monkeypatch.setattr(app.disk_usage_service, "format_size", fake_format_size)
    monkeypatch.setattr(app_module, "EnhancedGitService", FakeEnhancedGitService)

    async with app.run_test() as pilot:
        await pilot.pause(0.05)
        app.action_disk_usage()
        app.action_git_log()
        app.action_git_branches()
        app.action_git_status()
        await pilot.pause(0.05)

    assert disk_calls == [target_root]
    assert git_init_paths == [target_root, target_root, target_root]
