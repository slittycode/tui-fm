import asyncio
from pathlib import Path

from rich.console import Group
from rich.syntax import Syntax
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.events import Resize
from textual.widgets import Footer, Header, Input, Static

from archive_service import ArchiveService
from bookmarks_manager import BookmarksManager
from config_manager import ConfigManager
from config_ui import ConfigScreen
from disk_usage_service import DiskUsageService
from filesystem_service import FileSystemService
from filterable_tree import FilterableDirectoryTree
from git_enhanced import EnhancedGitService
from image_preview_service import ImagePreviewService
from tabbed_directory_tree import TabbedDirectoryTree
from theme_manager import ThemeManager


class FileManagerApp(App):
    """A Textual file manager application."""

    TITLE = "⚡ File Manager"
    STACK_LAYOUT_WIDTH = 100

    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: $primary-darken-2;
        color: $text;
        text-style: bold;
    }

    Footer {
        background: $panel-darken-1;
        color: $text-muted;
    }

    #main-container {
        layout: horizontal;
        height: 1fr;
        padding: 0;
        margin: 0;
        background: $surface;
    }

    #left-pane {
        width: 40%;
        height: 100%;
        background: $panel;
        border-right: vkey $primary;
        padding: 0;
    }

    #right-pane {
        width: 60%;
        height: 100%;
        background: $surface;
        padding: 0;
    }

    #tree-header {
        height: 3;
        background: $primary-darken-1;
        color: $text;
        padding: 1 2;
        text-style: bold;
        content-align: center middle;
    }

    #tree-container {
        height: 1fr;
        background: $panel;
        padding: 1 2;
        border-bottom: solid $primary-darken-2;
    }

    DirectoryTree, FilterableDirectoryTree {
        height: 100%;
        background: $panel;
        scrollbar-gutter: stable;
        scrollbar-size: 1 1;
    }

    DirectoryTree > .directory-tree--folder, FilterableDirectoryTree > .directory-tree--folder {
        color: $accent;
        text-style: bold;
    }

    DirectoryTree > .directory-tree--file, FilterableDirectoryTree > .directory-tree--file {
        color: $text;
    }

    DirectoryTree:focus, FilterableDirectoryTree:focus {
        border: none;
    }

    /* Git status indicator colors */
    .git-status-modified {
        color: $warning;
        text-style: bold;
    }

    .git-status-staged {
        color: $success;
        text-style: bold;
    }

    .git-status-deleted {
        color: $error;
        text-style: bold;
    }

    .git-status-untracked {
        color: $accent;
        text-style: italic;
    }

    #tree-footer {
        height: 3;
        background: $panel-darken-1;
        color: $text-muted;
        padding: 1 2;
        text-style: italic;
    }

    #preview-container {
        height: 100%;
        padding: 0;
        layout: vertical;
    }

    #preview-header {
        height: 3;
        background: $primary-darken-1;
        color: $text;
        padding: 1 2;
        text-style: bold;
        content-align: left middle;
    }

    #preview-content {
        height: 1fr;
        background: $surface;
        padding: 2 3;
        overflow-y: auto;
        color: $text;
        scrollbar-size: 1 1;
    }

    #preview-footer {
        height: 3;
        background: $panel-darken-1;
        color: $text-muted;
        padding: 1 2;
    }

    #status-bar {
        height: 1;
        background: $panel;
        color: $text;
        padding: 0 2;
    }

    #command-input {
        height: 3;
        background: $surface;
        color: $text;
        border-top: solid $primary-darken-2;
        padding: 0 1;
    }

    .file-icon {
        color: $success;
    }

    .dir-icon {
        color: $warning;
    }

    .info-label {
        color: $text-muted;
        text-style: italic;
    }

    .error-text {
        color: $error;
        text-style: bold;
    }

    .success-text {
        color: $success;
    }

    .warning-text {
        color: $warning;
    }

    .image-preview {
        color: $text;
    }

    .image-info {
        color: $text-muted;
        text-style: italic;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", key_display="q"),
        Binding("r", "refresh", "Refresh", key_display="r"),
        Binding("h", "toggle_help", "Help", key_display="h"),
        Binding("c", "copy_selected", "Copy", key_display="c"),
        Binding("m", "move_selected", "Move", key_display="m"),
        Binding("n", "rename_selected", "Rename", key_display="n"),
        Binding("d", "delete_selected", "Delete", key_display="d"),
        Binding("/", "start_search", "Search", key_display="/"),
        Binding("f", "clear_filter", "Clear Filter", key_display="f"),
        Binding("ctrl+f", "start_search", "Search", show=False),
        Binding("?", "toggle_help", "Help", show=False),
        Binding("ctrl+c", "quit", "Quit", show=False),
        Binding("escape", "clear_selection", "Clear", show=False),
        Binding("b", "bookmark_current", "Bookmark", key_display="b"),
        Binding("B", "browse_bookmarks", "Bookmarks", key_display="B"),
        Binding("comma", "open_config", "Config", key_display=","),
        Binding("ctrl+t", "new_tab", "New Tab", show=False),
        Binding("ctrl+w", "close_tab", "Close Tab", show=False),
        Binding("ctrl+tab", "next_tab", "Next Tab", show=False),
        Binding("ctrl+shift+tab", "prev_tab", "Prev Tab", show=False),
        Binding("ctrl+d", "duplicate_tab", "Duplicate Tab", show=False),
        Binding("ctrl+l", "toggle_tab_lock", "Lock Tab", show=False),
        Binding("1", "goto_tab_1", "Tab 1", show=False),
        Binding("2", "goto_tab_2", "Tab 2", show=False),
        Binding("3", "goto_tab_3", "Tab 3", show=False),
        Binding("4", "goto_tab_4", "Tab 4", show=False),
        Binding("5", "goto_tab_5", "Tab 5", show=False),
        Binding("6", "goto_tab_6", "Tab 6", show=False),
        Binding("7", "goto_tab_7", "Tab 7", show=False),
        Binding("8", "goto_tab_8", "Tab 8", show=False),
        Binding("9", "goto_tab_9", "Tab 9", show=False),
        Binding("ctrl+right", "next_theme", "Next Theme", show=False),
        Binding("ctrl+left", "prev_theme", "Prev Theme", show=False),
        Binding("ctrl+i", "theme_info", "Theme Info", show=False),
        Binding("ctrl+u", "disk_usage", "Disk Usage", show=False),
        Binding("ctrl+g", "git_log", "Git Log", show=False),
        Binding("ctrl+b", "git_branches", "Git Branches", show=False),
        Binding("ctrl+s", "git_status", "Git Status", show=False),
    ]

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.bookmarks = BookmarksManager()
        self.theme_manager = ThemeManager()
        self.image_preview_service = ImagePreviewService()
        self.disk_usage_service = DiskUsageService()
        self.archive_service = ArchiveService()
        self.enhanced_git_service = EnhancedGitService(self.config.default_path)
        self.current_path = self.config.default_path
        self.selected_file = None
        self.help_visible = False
        self.filter_query = ""
        self.command_mode = None
        self.delete_confirmation_path = None
        self.last_action = ""
        self._preview_request_id = 0

    @staticmethod
    def _should_stack_layout(width: int) -> bool:
        """Switch to stacked panes for narrow terminal widths."""
        return width < FileManagerApp.STACK_LAYOUT_WIDTH

    def _apply_layout_mode(self, width: int) -> None:
        """Apply responsive pane layout based on terminal width."""
        main = self.query_one("#main-container", Horizontal)
        left = self.query_one("#left-pane", Vertical)
        right = self.query_one("#right-pane", Vertical)

        if self._should_stack_layout(width):
            main.styles.layout = "vertical"
            left.styles.width = "100%"
            right.styles.width = "100%"
            left.styles.height = "1fr"
            right.styles.height = "1fr"
        else:
            main.styles.layout = "horizontal"
            left.styles.width = "40%"
            right.styles.width = "60%"
            left.styles.height = "100%"
            right.styles.height = "100%"

    def on_mount(self) -> None:
        """Initialize responsive layout on first render."""
        # Initialize theme system
        self._initialize_theme()
        
        self._apply_layout_mode(self.size.width)
        self._set_status(f"Ready | Root: {self.current_path}")
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        active_tree = tabbed_tree.get_active_tree()
        if active_tree:
            active_tree.focus()

    def on_resize(self, event: Resize) -> None:
        """Re-evaluate layout when the terminal size changes."""
        self._apply_layout_mode(event.size.width)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        with Horizontal(id="main-container"):
            # Left pane - Directory Tree
            with Vertical(id="left-pane"):
                yield TabbedDirectoryTree(self.current_path, id="tree")

            # Right pane - Preview
            with Vertical(id="right-pane"):
                with Container(id="preview-container"):
                    yield Static("👁️  Preview", id="preview-header")
                    yield Static(
                        self._get_welcome_text(),
                        id="preview-content"
                    )
                    yield Static("Ready", id="preview-footer")
        yield Static("Ready", id="status-bar")
        yield Input(
            placeholder="Command: / search | c copy | m move | n rename | d delete",
            id="command-input",
        )
        yield Footer()

    def _get_welcome_text(self) -> str:
        """Get welcome text for preview pane."""
        return """[bold cyan]Welcome to File Manager![/bold cyan]

[dim]Navigate the file tree on the left to preview files and folders.[/dim]

[bold yellow]Quick Start:[/bold yellow]
  • Use [green]↑/↓[/green] to navigate
  • Press [green]Enter[/green] to select
  • Press [green]h[/green] for help
  • Press [green]q[/green] to quit

[dim]Select a file or folder to see its contents here.[/dim]
        """

    def on_directory_tree_file_selected(self, event: FilterableDirectoryTree.FileSelected) -> None:
        """Handle file selection."""
        file_path = Path(event.path)
        self.selected_file = file_path
        self._clear_delete_confirmation()
        self.last_action = ""
        self.update_preview(file_path)

    def _set_status(self, message: str) -> None:
        """Update the status bar message."""
        self.query_one("#status-bar", Static).update(message)

    def _show_operation_result(self, operation: str, success: bool, details: dict) -> None:
        """Render operation success/failure details in the preview pane."""
        self._preview_request_id += 1
        header = self.query_one("#preview-header", Static)
        preview = self.query_one("#preview-content", Static)
        footer = self.query_one("#preview-footer", Static)

        icon = "✅" if success else "❌"
        state = "Complete" if success else "Failed"
        verb = "succeeded" if success else "failed"
        header.update(f"{icon} {operation} {state}")

        lines = [f"[bold]{operation} {verb}.[/bold]", ""]
        for label, value in details.items():
            lines.append(f"[dim]{label}:[/dim] {value}")
        lines.extend(
            [
                "",
                "[dim]Continue browsing, select another entry, or press Esc to reset the preview.[/dim]",
            ]
        )
        preview.update("\n".join(lines))
        footer.update(f"{operation} {state.lower()}")

    def _build_file_status(self, file_path: Path, detail: str) -> str:
        """Build the status text for a selected path."""
        status = f"Selected: {file_path} ({detail})"
        if self.filter_query:
            status += f" | Filter: {self.filter_query}"
        if self.last_action:
            status += f" | Last: {self.last_action}"
        return status

    @staticmethod
    def _apply_name_filter(items, query: str):
        """Return items filtered by a case-insensitive name match."""
        return FileSystemService.apply_name_filter(items, query)

    def _resolve_destination_path(self, source: Path, target_text: str) -> Path:
        """Resolve a destination path from user-provided text."""
        return FileSystemService.resolve_destination_path(source, target_text)

    def _copy_path(self, source: Path, destination: Path) -> Path:
        """Copy a file or directory to a destination path."""
        return FileSystemService.copy_path(source, destination)

    def _move_path(self, source: Path, destination: Path) -> Path:
        """Move a file or directory to a destination path."""
        return FileSystemService.move_path(source, destination)

    def _rename_path(self, source: Path, new_name: str) -> Path:
        """Rename a file or directory in place."""
        return FileSystemService.rename_path(source, new_name)

    def _delete_path(self, target: Path) -> None:
        """Delete a file or directory."""
        FileSystemService.delete_path(target)

    def _clear_delete_confirmation(self) -> None:
        """Reset delete confirmation state for non-delete workflows."""
        self.delete_confirmation_path = None

    def _enter_command_mode(self, mode: str, prompt: str, initial_value: str = "") -> None:
        """Start text input mode for search and file operations."""
        self._clear_delete_confirmation()
        self.command_mode = mode
        input_widget = self.query_one("#command-input", Input)
        input_widget.placeholder = prompt
        input_widget.value = initial_value
        input_widget.focus()
        self._set_status(prompt)

    def _exit_command_mode(self) -> None:
        """Return to normal tree navigation mode."""
        self.command_mode = None
        input_widget = self.query_one("#command-input", Input)
        input_widget.value = ""
        input_widget.placeholder = "Command: / search | c copy | m move | n rename | d delete"
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        active_tree = tabbed_tree.get_active_tree()
        if active_tree:
            active_tree.focus()

    def _refresh_after_operation(self) -> None:
        """Refresh tree after a state change without replacing result feedback."""
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        active_tree = tabbed_tree.get_active_tree()
        if active_tree:
            active_tree.reload()
        if self.last_action:
            self._set_status(self.last_action)
        if self.selected_file and not self.selected_file.exists():
            self.selected_file = None
            self.action_clear_selection()

    def _get_selected_path(self):
        """Return selected path when available and still valid."""
        if self.selected_file is None:
            self._set_status("Select a file or folder first.")
            return None
        if not self.selected_file.exists():
            self.selected_file = None
            self._set_status("Selected path no longer exists.")
            return None
        return self.selected_file

    def _apply_filter_query(self, query: str) -> None:
        """Apply or clear filter and refresh current preview."""
        self.filter_query = query.strip()
        self._clear_delete_confirmation()
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        active_tree = tabbed_tree.get_active_tree()
        if active_tree:
            changed = active_tree.set_filter_query(self.filter_query)
            if changed:
                active_tree.reload()
            # Update tab state
            tabbed_tree.update_active_tab_filter(self.filter_query)

        if self.selected_file and self.selected_file.exists():
            self.update_preview(self.selected_file)
        elif self.filter_query:
            self._set_status(f"Filter active: {self.filter_query}")
        else:
            self._set_status("Filter cleared.")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command input submissions."""
        if event.input.id != "command-input":
            return

        mode = self.command_mode
        value = event.value.strip()
        self._exit_command_mode()

        if mode == "search":
            self._apply_filter_query(value)
            return

        if mode is None:
            if value:
                self._set_status("No pending command. Use /, c, m, n, or d.")
            return

        source = self._get_selected_path()
        if source is None:
            return

        try:
            if mode == "copy":
                if not value:
                    raise ValueError("Copy destination is required.")
                destination = self._resolve_destination_path(source, value)
                self._copy_path(source, destination)
                self.last_action = f"Copied to {destination}"
            elif mode == "move":
                if not value:
                    raise ValueError("Move destination is required.")
                destination = self._resolve_destination_path(source, value)
                moved = self._move_path(source, destination)
                self.selected_file = moved
                self.last_action = f"Moved to {moved}"
            elif mode == "rename":
                renamed = self._rename_path(source, value)
                self.selected_file = renamed
                self.last_action = f"Renamed to {renamed.name}"
            else:
                self._set_status("Unknown command mode.")
                return

            self.delete_confirmation_path = None
            self._refresh_after_operation()
            if mode == "copy":
                self._show_operation_result(
                    operation="Copy",
                    success=True,
                    details={
                        "Source": str(source),
                        "Destination": str(destination),
                    },
                )
            elif mode == "move":
                self._show_operation_result(
                    operation="Move",
                    success=True,
                    details={
                        "Source": str(source),
                        "Destination": str(moved),
                    },
                )
            elif mode == "rename":
                self._show_operation_result(
                    operation="Rename",
                    success=True,
                    details={
                        "Path": str(renamed),
                        "New Name": renamed.name,
                    },
                )
        except Exception as error:
            self._set_status(f"Operation failed: {error}")
            self._show_operation_result(
                operation=mode.capitalize(),
                success=False,
                details={
                    "Target": str(source),
                    "Error": str(error),
                },
            )

    def _build_file_content_renderable(
        self,
        file_path: Path,
        content: str,
        is_truncated: bool,
    ):
        """Build file content renderable with optional syntax highlighting."""
        extension_to_lexer = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "tsx",
            ".jsx": "jsx",
            ".json": "json",
            ".md": "markdown",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".sh": "bash",
            ".zsh": "bash",
            ".toml": "toml",
            ".ini": "ini",
            ".css": "css",
            ".html": "html",
            ".xml": "xml",
            ".sql": "sql",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".c": "c",
            ".cpp": "cpp",
        }
        lexer = extension_to_lexer.get(file_path.suffix.lower())

        renderables: list = [
            Text("Content:", style="bold"),
            Text(""),
        ]

        if lexer:
            renderables.append(
                Syntax(
                    content,
                    lexer,
                    line_numbers=True,
                    word_wrap=False,
                    background_color="default",
                )
            )
        else:
            renderables.append(Text(content))

        if is_truncated:
            renderables.extend(
                [
                    Text(""),
                    Text("... (preview truncated)", style="dim italic"),
                ]
            )

        return Group(*renderables)

    def update_preview(self, file_path: Path) -> None:
        """Update preview and footer asynchronously for the selected path."""
        self._preview_request_id += 1
        request_id = self._preview_request_id

        header = self.query_one("#preview-header", Static)
        preview = self.query_one("#preview-content", Static)
        footer = self.query_one("#preview-footer", Static)
        header.update("⏳ Loading")
        preview.update("[dim]Loading preview...[/dim]")
        footer.update("Loading...")

        self.run_worker(
            self._load_and_render_preview(file_path, request_id, self.filter_query),
            group="preview",
            exclusive=True,
        )

    async def _load_and_render_preview(self, file_path: Path, request_id: int, filter_query: str) -> None:
        """Load preview data in a worker thread, then render on the UI thread."""
        snapshot = await asyncio.to_thread(
            self._build_preview_snapshot,
            file_path,
            filter_query,
        )

        if request_id != self._preview_request_id:
            return
        if self.selected_file is not None and self.selected_file != file_path:
            return

        self._render_preview_snapshot(file_path, snapshot)

    def _build_preview_snapshot(self, file_path: Path, filter_query: str) -> dict:
        """Collect preview and footer data from the filesystem."""
        if not file_path.exists():
            return {"kind": "missing"}

        try:
            is_directory = file_path.is_dir()
        except OSError as error:
            return {"kind": "error", "error": str(error)}

        if is_directory:
            try:
                items = list(file_path.iterdir())
            except (PermissionError, OSError):
                return {"kind": "directory_denied"}

            directories = []
            files = []
            for item in items:
                try:
                    if item.is_dir():
                        directories.append(item)
                    elif item.is_file():
                        files.append(item)
                except OSError:
                    continue

            directories = sorted(directories, key=lambda entry: entry.name.lower())
            files = sorted(files, key=lambda entry: entry.name.lower())
            filtered_dirs = FileSystemService.apply_name_filter(directories, filter_query)
            filtered_files = FileSystemService.apply_name_filter(files, filter_query)

            file_rows = []
            for item in filtered_files[:20]:
                try:
                    size_str = self._format_size(item.stat().st_size)
                except OSError:
                    size_str = "unavailable"
                file_rows.append((item.name, size_str))

            return {
                "kind": "directory",
                "path": str(file_path),
                "name": file_path.name or str(file_path),
                "total_items": len(items),
                "all_dir_count": len(directories),
                "all_file_count": len(files),
                "filtered_dirs": [entry.name for entry in filtered_dirs[:20]],
                "filtered_files": file_rows,
                "filtered_dir_count": len(filtered_dirs),
                "filtered_file_count": len(filtered_files),
            }

        try:
            size = file_path.stat().st_size
        except OSError as error:
            return {"kind": "error", "error": str(error)}

        if size > 1_000_000:
            return {"kind": "large_file", "size": self._format_size(size)}

        # Check if it's an archive file first
        if self.archive_service.is_archive(file_path):
            return {"kind": "archive_file", "size": self._format_size(size)}
        
        # Check if it's an image file
        if self.image_preview_service.can_render_image(file_path):
            return {"kind": "image_file", "size": self._format_size(size)}
        
        try:
            with open(file_path, encoding="utf-8") as handle:
                raw_content = handle.read(10001)
        except UnicodeDecodeError:
            return {"kind": "binary_file", "size": self._format_size(size)}
        except OSError as error:
            return {"kind": "error", "error": str(error)}

        is_truncated = len(raw_content) > 10000
        return {
            "kind": "text_file",
            "size": self._format_size(size),
            "content": raw_content[:10000],
            "is_truncated": is_truncated,
            "suffix": file_path.suffix or "no extension",
        }

    def _render_preview_snapshot(self, file_path: Path, snapshot: dict) -> None:
        """Render previously collected preview data."""
        header = self.query_one("#preview-header", Static)
        preview = self.query_one("#preview-content", Static)
        footer = self.query_one("#preview-footer", Static)
        tree_footer = self.query_one("#tree-footer", Static)

        kind = snapshot["kind"]

        if kind == "missing":
            header.update("❌ Error")
            preview.update("[red bold]File not found[/red bold]")
            footer.update("Not found")
            self._set_status(f"Selected path missing: {file_path}")
            return

        if kind == "directory_denied":
            header.update("🔒 Permission Denied")
            preview.update("[red bold]Permission denied[/red bold]\n\n[dim]You don't have access to this directory[/dim]")
            footer.update("🔒 Access denied")
            tree_footer.update(f"📂 {file_path}")
            self._set_status(f"Selected: {file_path} (access denied)")
            return

        if kind == "error":
            header.update("❌ Error")
            preview.update(f"[red bold]Error reading path[/red bold]\n\n{snapshot['error']}")
            footer.update("Error")
            self._set_status(f"Selected: {file_path} (error)")
            return

        if kind == "directory":
            header.update(f"📁 {snapshot['name']}/")
            content = "[bold cyan]═══ Directory Contents ═══[/bold cyan]\n\n"
            content += f"[dim]Path:[/dim] [italic]{snapshot['path']}[/italic]\n"

            displayed_count = snapshot["filtered_dir_count"] + snapshot["filtered_file_count"]
            if self.filter_query:
                content += (
                    f"[dim]Filter:[/dim] [bold]{self.filter_query}[/bold]\n"
                    f"[dim]Showing:[/dim] {displayed_count} of {snapshot['total_items']} items "
                    f"([yellow]{snapshot['filtered_dir_count']}[/yellow] folders, "
                    f"[green]{snapshot['filtered_file_count']}[/green] files)\n\n"
                )
            else:
                content += (
                    f"[dim]Total:[/dim] {snapshot['total_items']} items "
                    f"([yellow]{snapshot['all_dir_count']}[/yellow] folders, "
                    f"[green]{snapshot['all_file_count']}[/green] files)\n\n"
                )

            if snapshot["filtered_dirs"]:
                content += "[bold yellow]📁 Folders[/bold yellow]\n"
                for name in snapshot["filtered_dirs"]:
                    content += f"  [yellow]▸[/yellow] {name}\n"
                if snapshot["filtered_dir_count"] > len(snapshot["filtered_dirs"]):
                    content += f"  [dim]... and {snapshot['filtered_dir_count'] - len(snapshot['filtered_dirs'])} more[/dim]\n"
                content += "\n"

            if snapshot["filtered_files"]:
                content += "[bold green]📄 Files[/bold green]\n"
                for name, size_str in snapshot["filtered_files"]:
                    content += f"  [green]•[/green] {name} [dim]({size_str})[/dim]\n"
                if snapshot["filtered_file_count"] > len(snapshot["filtered_files"]):
                    content += f"  [dim]... and {snapshot['filtered_file_count'] - len(snapshot['filtered_files'])} more[/dim]\n"

            if displayed_count == 0:
                content += "[dim italic]No entries match the active filter.[/dim italic]\n"

            preview.update(content)
            detail = f"{snapshot['total_items']} items"
            if self.filter_query:
                detail = f"{displayed_count}/{snapshot['total_items']} items"
            footer.update(f"📁 {detail}")
            tree_footer.update(f"📂 {file_path}")
            self._set_status(self._build_file_status(file_path, detail))
            return

        if kind == "large_file":
            header.update(f"📄 {file_path.name}")
            preview.update(
                f"[yellow bold]⚠️  File too large to preview[/yellow bold]\n\n"
                f"[dim]Size:[/dim] {snapshot['size']}\n"
                f"[dim]Path:[/dim] [italic]{file_path}[/italic]\n\n"
                f"[dim]Files larger than 1MB are not previewed for performance reasons.[/dim]"
            )
            footer.update(f"📄 {snapshot['size']}")
            tree_footer.update(f"📂 {file_path.parent}")
            self._set_status(self._build_file_status(file_path, snapshot["size"]))
            return

        if kind == "archive_file":
            # Render archive preview
            try:
                archive_info = self.archive_service.list_archive_contents(file_path)
                archive_stats = self.archive_service.get_archive_stats(file_path)
                
                header.update(f"📦 {file_path.name}")
                
                content = []
                content.append("═══ Archive Contents ═══")
                content.append("")
                content.append(f"📦 Type: {archive_stats.get('type', 'unknown')}")
                content.append(f"📊 Size: {snapshot['size']}")
                content.append(f"📁 Entries: {archive_stats.get('total_entries', 0)}")
                content.append(f"📄 Files: {archive_stats.get('file_count', 0)}")
                content.append(f"📂 Directories: {archive_stats.get('dir_count', 0)}")
                
                if archive_stats.get('compression_ratio'):
                    ratio = archive_stats['compression_ratio']
                    reduction = archive_stats.get('size_reduction', 0)
                    content.append(f"🗜️  Compression: {ratio:.2f}x ({reduction:.1f}% smaller)")
                
                content.append("")
                
                # Show first few entries
                if archive_info.entries:
                    content.append("📋 Contents (first 20):")
                    file_entries = [e for e in archive_info.entries if e.is_file][:15]
                    dir_entries = [e for e in archive_info.entries if e.is_dir][:5]
                    
                    if dir_entries:
                        content.append("")
                        content.append("📂 Directories:")
                        for entry in dir_entries:
                            size_str = self._format_size(entry.size) if entry.size > 0 else "—"
                            content.append(f"  📁 {entry.name} ({size_str})")
                    
                    if file_entries:
                        content.append("")
                        content.append("📄 Files:")
                        for entry in file_entries:
                            size_str = self._format_size(entry.size)
                            content.append(f"  📄 {entry.name} ({size_str})")
                    
                    if archive_info.total_entries > 20:
                        content.append("")
                        content.append(f"[dim]... and {archive_info.total_entries - 20} more entries[/dim]")
                else:
                    content.append("[dim italic]Archive appears to be empty[/dim italic]")
                
                preview.update("\n".join(content))
                footer.update(f"📦 {archive_stats.get('total_entries', 0)} entries")
                tree_footer.update(f"📂 {file_path.parent}")
                self._set_status(f"Archive: {file_path.name} ({archive_stats.get('total_entries', 0)} entries)")
                
            except Exception as e:
                header.update(f"📦 {file_path.name}")
                preview.update(
                    f"[yellow bold]📦 Archive file[/yellow bold]\n\n"
                    f"[dim]Size:[/dim] {snapshot['size']}\n"
                    f"[dim]Path:[/dim] [italic]{file_path}[/italic]\n\n"
                    f"[red]Error reading archive:[/red] {str(e)}"
                )
                footer.update(f"📦 {snapshot['size']}")
                tree_footer.update(f"📂 {file_path.parent}")
                self._set_status(f"Archive error: {file_path.name}")
            return

        if kind == "image_file":
            # Render image preview
            image_content = self.image_preview_service.render_image(file_path)
            image_info = self.image_preview_service.get_image_info(file_path)
            
            header.update(f"🖼️ {file_path.name}")
            
            if image_content:
                preview.update(
                    Group(
                        Text("═══ Image Preview ═══", style="bold cyan"),
                        Text(""),
                        Text.assemble(("Size: ", "dim"), snapshot["size"]),
                        Text.assemble(("Path: ", "dim"), (str(file_path), "italic")),
                        Text.assemble(("Format: ", "dim"), (image_info.get("format", "unknown") if image_info else "unknown")),
                        Text.assemble(("Dimensions: ", "dim"), (f"{image_info.get('width', '?')}x{image_info.get('height', '?')}" if image_info else "unknown")),
                        Text(""),
                        Text(image_content, style="default"),
                    )
                )
            else:
                preview.update(
                    f"[yellow bold]🖼️  Image file[/yellow bold]\n\n"
                    f"[dim]Size:[/dim] {snapshot['size']}\n"
                    f"[dim]Path:[/dim] [italic]{file_path}[/italic]\n"
                    f"[dim]Format:[/dim] {image_info.get('format', 'unknown') if image_info else 'unknown'}\n\n"
                    f"[dim]Unable to render image (PIL not available or unsupported format).[/dim]"
                )
            
            footer.update(f"🖼️ {snapshot['size']}")
            tree_footer.update(f"📂 {file_path.parent}")
            self._set_status(self._build_file_status(file_path, snapshot["size"]))
            return

        if kind == "binary_file":
            header.update(f"📄 {file_path.name}")
            preview.update(
                f"[yellow bold]📦 Binary file[/yellow bold]\n\n"
                f"[dim]Size:[/dim] {snapshot['size']}\n"
                f"[dim]Path:[/dim] [italic]{file_path}[/italic]\n"
                f"[dim]Type:[/dim] {file_path.suffix or 'unknown'}\n\n"
                f"[dim]Cannot preview binary files in text mode.[/dim]"
            )
            footer.update(f"📄 {snapshot['size']}")
            tree_footer.update(f"📂 {file_path.parent}")
            self._set_status(self._build_file_status(file_path, snapshot["size"]))
            return

        header.update(f"📄 {file_path.name}")
        preview.update(
            Group(
                Text("═══ File Preview ═══", style="bold cyan"),
                Text(""),
                Text.assemble(("Size: ", "dim"), snapshot["size"]),
                Text.assemble(("Path: ", "dim"), (str(file_path), "italic")),
                Text.assemble(("Type: ", "dim"), snapshot["suffix"]),
                Text(""),
                self._build_file_content_renderable(
                    file_path,
                    snapshot["content"],
                    snapshot["is_truncated"],
                ),
            )
        )
        footer.update(f"📄 {snapshot['size']}")
        tree_footer.update(f"📂 {file_path.parent}")
        self._set_status(self._build_file_status(file_path, snapshot["size"]))

    def update_footer(self, file_path: Path) -> None:
        """Backward-compatible wrapper that refreshes the full preview."""
        self.update_preview(file_path)

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        size_float: float = float(size)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_float < 1024.0:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024.0
        return f"{size_float:.1f} TB"

    def action_refresh(self) -> None:
        """Refresh the directory tree."""
        self._clear_delete_confirmation()
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        active_tree = tabbed_tree.get_active_tree()
        if active_tree:
            active_tree.reload()
            current_path = tabbed_tree.get_active_path()
        else:
            current_path = self.current_path
        
        if self.selected_file and self.selected_file.exists():
            self.update_preview(self.selected_file)
        else:
            self._set_status(f"Refreshed | Root: {current_path}")

    def action_start_search(self) -> None:
        """Start search/filter input mode."""
        self._enter_command_mode(
            "search",
            "Filter names (empty clears filter):",
            self.filter_query,
        )

    def action_clear_filter(self) -> None:
        """Clear active filter query."""
        self._clear_delete_confirmation()
        if not self.filter_query:
            self._set_status("No active filter.")
            return
        self._apply_filter_query("")

    def action_copy_selected(self) -> None:
        """Prompt for copy destination path."""
        source = self._get_selected_path()
        if source is None:
            return
        self._enter_command_mode(
            "copy",
            "Copy destination (absolute or relative path):",
        )

    def action_move_selected(self) -> None:
        """Prompt for move destination path."""
        source = self._get_selected_path()
        if source is None:
            return
        self._enter_command_mode(
            "move",
            "Move destination (absolute or relative path):",
        )

    def action_rename_selected(self) -> None:
        """Prompt for new name."""
        source = self._get_selected_path()
        if source is None:
            return
        self._enter_command_mode(
            "rename",
            f"New name for {source.name}:",
        )

    def action_delete_selected(self) -> None:
        """Delete selected path with a two-step confirmation."""
        source = self._get_selected_path()
        if source is None:
            return

        if self.delete_confirmation_path != source:
            self.delete_confirmation_path = source
            self._set_status(f"Press d again to delete: {source}")
            return

        try:
            self._delete_path(source)
            self.last_action = f"Deleted {source.name}"
            self.selected_file = None
            self.delete_confirmation_path = None
            self.query_one(FilterableDirectoryTree).reload()
            self.action_clear_selection()
        except Exception as error:
            self._set_status(f"Delete failed: {error}")

    def action_toggle_help(self) -> None:
        """Show help information."""
        self._clear_delete_confirmation()
        if self.help_visible:
            self.help_visible = False
            if self.selected_file is not None:
                self.update_preview(self.selected_file)
            else:
                self.action_clear_selection()
            return

        self.help_visible = True
        preview = self.query_one("#preview-content", Static)
        header = self.query_one("#preview-header", Static)
        footer = self.query_one("#preview-footer", Static)

        header.update("❓ Help & Keyboard Shortcuts")
        footer.update("Press h again to close help")

        help_text = """[bold cyan]╔═══════════════════════════════════════════════════════╗[/bold cyan]
[bold cyan]║          FILE MANAGER - HELP & SHORTCUTS          ║[/bold cyan]
[bold cyan]╚═══════════════════════════════════════════════════════╝[/bold cyan]

[bold yellow]🎯 Navigation[/bold yellow]
  [green]↑ / ↓[/green]         Move up/down in file tree
  [green]← / →[/green]         Collapse/expand folders
  [green]Enter[/green]         Select file or folder
  [green]Home[/green]          Jump to top of list
  [green]End[/green]           Jump to bottom of list
  [green]Page Up/Down[/green]  Scroll faster

[bold yellow]⚡ Commands[/bold yellow]
  [green]q[/green]             Quit application
  [green]r[/green]             Refresh directory tree
  [green]/[/green]             Start search/filter
  [green]f[/green]             Clear active filter
  [green]c[/green]             Copy selected file/folder
  [green]m[/green]             Move selected file/folder
  [green]n[/green]             Rename selected file/folder
  [green]d[/green]             Delete selected file/folder (double press)
  [green]h[/green] or [green]?[/green]       Toggle this help screen
  [green]Ctrl+C[/green]        Force quit
  [green]Esc[/green]           Cancel command or clear selection

[bold yellow]👁️  Preview Pane[/bold yellow]
  • Displays file contents (text files)
  • Shows directory contents (folders)
  • File size and path information
  • Automatic text/binary detection
  • 1MB file size limit for performance

[bold yellow]📊 Status Information[/bold yellow]
  • Top bar: Current file/folder name
  • Bottom bar: File size or item count
  • Tree footer: Current directory path

[bold yellow]🎨 Features[/bold yellow]
  • Dual-pane layout for easy navigation
  • Syntax highlighting for common code/config files
  • File operations: copy, move, rename, delete
  • Search and filter by filename
  • Bookmarks for quick directory access
  • Git status indicators in file tree

[bold yellow]💡 Tips[/bold yellow]
  • Use keyboard for fastest navigation
  • Preview updates automatically on selection
  • Large files show size instead of content
  • Binary files are detected automatically

[bold yellow]🔖 Bookmarks[/bold yellow]
  [green]b[/green]             Bookmark current directory
  [green]B[/green]             Browse all bookmarks

[bold yellow]⚙️ Configuration[/bold yellow]
  [green],[/green]             Open configuration screen

[bold yellow]� Tabs[/bold yellow]
  [green]Ctrl+T[/green]        New tab
  [green]Ctrl+W[/green]        Close tab
  [green]Ctrl+Tab[/green]      Next tab
  [green]Ctrl+Shift+Tab[/green] Previous tab
  [green]Ctrl+D[/green]        Duplicate tab
  [green]Ctrl+L[/green]        Lock/unlock tab
  [green]1-9[/green]           Jump to tab

[bold yellow]🎨 Themes[/bold yellow]
  [green]Ctrl+→[/green]         Next theme
  [green]Ctrl+←[/green]         Previous theme
  [green]Ctrl+I[/green]         Theme info
  [green],[/green]             Theme settings (in config)

[bold yellow]�📁 Git Status[/bold yellow]
  [yellow]M[/yellow]             Modified file
  [green]A[/green]              Staged file
  [red]D[/red]                Deleted file
  [cyan]?[/cyan]               Untracked file

[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]
[dim]Press [bold]h[/bold] to close this help screen[/dim]
        """
        preview.update(help_text)

    def action_bookmark_current(self) -> None:
        """Bookmark the current directory."""
        try:
            tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
            current_path = tabbed_tree.get_active_path()
            self.bookmarks.add(current_path)
            self._set_status(f"Bookmarked: {current_path}")
        except ValueError as e:
            self._set_status(f"Bookmark error: {e}")

    def action_browse_bookmarks(self) -> None:
        """Show bookmarks list in preview pane."""
        self.help_visible = False
        preview = self.query_one("#preview-content", Static)
        header = self.query_one("#preview-header", Static)
        footer = self.query_one("#preview-footer", Static)

        header.update("🔖 Bookmarks")
        footer.update(f"{self.bookmarks.count()} bookmark(s)")

        bookmarks = self.bookmarks.list_all()
        if not bookmarks:
            content = "[dim italic]No bookmarks yet.[/dim italic]\n\n"
            content += "[dim]Press [bold]b[/bold] in any directory to add a bookmark.[/dim]"
        else:
            content = "[bold cyan]═══ Your Bookmarks ═══[/bold cyan]\n\n"
            for i, bookmark in enumerate(bookmarks, 1):
                content += f"[green]{i}.[/green] [bold]{bookmark.name}[/bold]\n"
                content += f"   [dim]{bookmark.path}[/dim]\n"
                if i < len(bookmarks):
                    content += "\n"
            content += "\n[dim]Navigate to a bookmarked path to quick-access it.[/dim]"

        preview.update(content)

    def action_open_config(self) -> None:
        """Open configuration screen."""
        self._clear_delete_confirmation()
        self.help_visible = False
        
        def handle_config_result(saved: bool) -> None:
            """Handle configuration screen result."""
            if saved:
                self._set_status("Configuration saved")
                # Refresh the directory tree to apply any changes
                self.action_refresh()
            else:
                self._set_status("Configuration cancelled")
        
        config_screen = ConfigScreen(self.config)
        self.push_screen(config_screen, handle_config_result)

    def action_clear_selection(self) -> None:
        """Clear current selection."""
        self._clear_delete_confirmation()
        if self.command_mode is not None:
            self._exit_command_mode()
            self._set_status("Command cancelled.")
            return

        preview = self.query_one("#preview-content", Static)
        header = self.query_one("#preview-header", Static)
        footer = self.query_one("#preview-footer", Static)
        tree_footer = self.query_one("#tree-footer", Static)

        header.update("👁️  Preview")
        footer.update("Ready")
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        current_path = tabbed_tree.get_active_path()
        tree_footer.update(f"🏠 {current_path}")
        preview.update(self._get_welcome_text())
        self.selected_file = None
        ready = f"Ready | Root: {current_path}"
        if self.filter_query:
            ready += f" | Filter: {self.filter_query}"
        if self.last_action:
            ready += f" | Last: {self.last_action}"
        self._set_status(ready)

    def action_new_tab(self) -> None:
        """Create a new tab."""
        self._clear_delete_confirmation()
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        
        if tabbed_tree.is_at_max_tabs():
            self._set_status("Maximum number of tabs reached")
            return
        
        tabbed_tree.add_tab()
        self._set_status("New tab created")

    def action_close_tab(self) -> None:
        """Close the current tab."""
        self._clear_delete_confirmation()
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        
        if tabbed_tree.get_tab_count() <= 1:
            self._set_status("Cannot close the last tab")
            return
        
        success = tabbed_tree.close_tab()
        if success:
            self._set_status("Tab closed")
        else:
            self._set_status("Failed to close tab")

    def action_next_tab(self) -> None:
        """Switch to the next tab."""
        self._clear_delete_confirmation()
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        
        if tabbed_tree.next_tab():
            self._set_status("Next tab")
        else:
            self._set_status("No other tabs")

    def action_prev_tab(self) -> None:
        """Switch to the previous tab."""
        self._clear_delete_confirmation()
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        
        if tabbed_tree.previous_tab():
            self._set_status("Previous tab")
        else:
            self._set_status("No other tabs")

    def action_duplicate_tab(self) -> None:
        """Duplicate the current tab."""
        self._clear_delete_confirmation()
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        
        if tabbed_tree.duplicate_active_tab():
            self._set_status("Tab duplicated")
        else:
            self._set_status("Failed to duplicate tab")

    def action_toggle_tab_lock(self) -> None:
        """Toggle the lock state of the current tab."""
        self._clear_delete_confirmation()
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        tabbed_tree.toggle_active_tab_lock()
        
        active_tab = tabbed_tree.tab_manager.active_tab
        if active_tab.is_locked:
            self._set_status("Tab locked")
        else:
            self._set_status("Tab unlocked")

    def action_goto_tab_1(self) -> None:
        """Switch to tab 1."""
        self._goto_tab_number(0)

    def action_goto_tab_2(self) -> None:
        """Switch to tab 2."""
        self._goto_tab_number(1)

    def action_goto_tab_3(self) -> None:
        """Switch to tab 3."""
        self._goto_tab_number(2)

    def action_goto_tab_4(self) -> None:
        """Switch to tab 4."""
        self._goto_tab_number(3)

    def action_goto_tab_5(self) -> None:
        """Switch to tab 5."""
        self._goto_tab_number(4)

    def action_goto_tab_6(self) -> None:
        """Switch to tab 6."""
        self._goto_tab_number(5)

    def action_goto_tab_7(self) -> None:
        """Switch to tab 7."""
        self._goto_tab_number(6)

    def action_goto_tab_8(self) -> None:
        """Switch to tab 8."""
        self._goto_tab_number(7)

    def action_goto_tab_9(self) -> None:
        """Switch to tab 9."""
        self._goto_tab_number(8)

    def _goto_tab_number(self, index: int) -> None:
        """Switch to tab by number.
        
        Args:
            index: Zero-based tab index.
        """
        self._clear_delete_confirmation()
        tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
        
        if tabbed_tree.switch_to_tab(index):
            self._set_status(f"Switched to tab {index + 1}")
        else:
            self._set_status(f"Tab {index + 1} not found")

    def _initialize_theme(self) -> None:
        """Initialize the theme system and apply the current theme."""
        # Set theme from configuration
        theme_name = self.config.theme
        if self.theme_manager.set_theme(theme_name):
            self._apply_theme_css()
        else:
            # Fallback to dark theme if configured theme not found
            self.theme_manager.set_theme("dark")
            self.config.set("theme", "dark")
            self._apply_theme_css()

    def _apply_theme_css(self) -> None:
        """Apply CSS for the current theme."""
        current_theme = self.theme_manager.get_current_theme()
        if current_theme:
            css = self.theme_manager.generate_css(current_theme)
            # Textual 8 removed RenderStyles.css assignment; update via stylesheet source.
            self.stylesheet.add_source(
                css,
                read_from=("runtime-theme.tcss", ""),
                tie_breaker=1000,
            )
            self.stylesheet.update(self)

    def action_next_theme(self) -> None:
        """Switch to the next theme."""
        self._clear_delete_confirmation()
        themes = self.theme_manager.list_themes()
        if len(themes) <= 1:
            self._set_status("No other themes available")
            return
        
        current_index = -1
        for i, theme in enumerate(themes):
            if theme.name == self.theme_manager.current_theme:
                current_index = i
                break
        
        next_index = (current_index + 1) % len(themes)
        next_theme = themes[next_index]
        
        if self.theme_manager.set_theme(next_theme.name):
            self.config.set("theme", next_theme.name)
            self._apply_theme_css()
            self._set_status(f"Theme: {next_theme.display_name}")

    def action_prev_theme(self) -> None:
        """Switch to the previous theme."""
        self._clear_delete_confirmation()
        themes = self.theme_manager.list_themes()
        if len(themes) <= 1:
            self._set_status("No other themes available")
            return
        
        current_index = -1
        for i, theme in enumerate(themes):
            if theme.name == self.theme_manager.current_theme:
                current_index = i
                break
        
        prev_index = (current_index - 1) % len(themes)
        prev_theme = themes[prev_index]
        
        if self.theme_manager.set_theme(prev_theme.name):
            self.config.set("theme", prev_theme.name)
            self._apply_theme_css()
            self._set_status(f"Theme: {prev_theme.display_name}")

    def action_theme_info(self) -> None:
        """Show information about the current theme."""
        self._clear_delete_confirmation()
        current_theme = self.theme_manager.get_current_theme()
        if not current_theme:
            self._set_status("No theme selected")
            return
        
        theme_info = (
            f"Theme: {current_theme.display_name} "
            f"({current_theme.name}) - {current_theme.description}"
        )
        self._set_status(theme_info)

    def action_disk_usage(self) -> None:
        """Show disk usage analysis for current directory."""
        self._clear_delete_confirmation()
        self.help_visible = False
        
        try:
            tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
            current_path = Path(tabbed_tree.current_path)
        except (AttributeError, ValueError):
            current_path = self.current_path
        
        if not current_path.exists():
            self._set_status("Path does not exist")
            return
        
        # Get disk usage analysis
        summary = self.disk_usage_service.analyze_directory(current_path, max_depth=2)
        
        # Format disk usage information
        total_size = self.disk_usage_service.format_size(summary.total_size)
        file_count = summary.total_files
        dir_count = summary.total_dirs
        
        # Get disk space information
        total_disk, used_disk, free_disk = self.disk_usage_service.get_disk_usage(current_path)
        used_pct, free_pct = self.disk_usage_service.get_disk_space_percentage(current_path)
        
        # Build disk usage report
        content = []
        content.append("═══ Disk Usage Analysis ═══")
        content.append("")
        content.append(f"📁 Directory: {current_path}")
        content.append(f"📊 Total Size: {total_size}")
        content.append(f"📄 Files: {file_count}")
        content.append(f"📂 Directories: {dir_count}")
        content.append("")
        
        # Disk space information
        content.append("💾 Disk Space:")
        content.append(f"   Total: {self.disk_usage_service.format_size(total_disk)}")
        content.append(f"   Used: {self.disk_usage_service.format_size(used_disk)} ({used_pct:.1f}%)")
        content.append(f"   Free: {self.disk_usage_service.format_size(free_disk)} ({free_pct:.1f}%)")
        content.append("")
        
        # Largest files
        if summary.largest_files:
            content.append("🔝 Largest Files:")
            for file_path, size in summary.largest_files[:5]:
                size_str = self.disk_usage_service.format_size(size)
                relative_path = file_path.relative_to(current_path)
                content.append(f"   {size_str:8} {relative_path}")
            content.append("")
        
        # File type distribution
        if summary.file_type_distribution:
            content.append("📋 File Types:")
            # Sort by size
            sorted_types = sorted(summary.file_type_distribution.items(), key=lambda x: x[1], reverse=True)
            for file_type, size in sorted_types[:8]:
                size_str = self.disk_usage_service.format_size(size)
                percentage = (size / summary.total_size) * 100 if summary.total_size > 0 else 0
                content.append(f"   {size_str:8} {file_type or 'no_ext'} ({percentage:.1f}%)")
            content.append("")
        
        # Subdirectory sizes
        if summary.subdirectory_sizes:
            content.append("📂 Subdirectories:")
            sorted_dirs = sorted(summary.subdirectory_sizes.items(), key=lambda x: x[1], reverse=True)
            for dir_name, size in sorted_dirs[:5]:
                size_str = self.disk_usage_service.format_size(size)
                content.append(f"   {size_str:8} {dir_name}/")
        
        # Display in preview pane
        preview = self.query_one("#preview-content", Static)
        preview.update("\n".join(content))
        
        self._set_status(f"Disk usage analysis for {current_path.name}")

    def action_git_log(self) -> None:
        """Show Git commit history."""
        self._clear_delete_confirmation()
        self.help_visible = False
        
        try:
            tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
            current_path = Path(tabbed_tree.current_path)
        except (AttributeError, ValueError):
            current_path = self.current_path
        
        # Update Git service path
        self.enhanced_git_service = EnhancedGitService(current_path)
        
        if not self.enhanced_git_service.is_git_repository():
            self._set_status("Not a Git repository")
            return
        
        # Get commit history
        commits = self.enhanced_git_service.get_commit_history(limit=15)
        
        content = []
        content.append("═══ Git Commit History ═══")
        content.append("")
        
        if not commits:
            content.append("[dim italic]No commits found[/dim italic]")
        else:
            for commit in commits:
                date_str = commit.date.strftime("%Y-%m-%d %H:%M")
                content.append(f"[bold]{commit.short_hash}[/bold] [cyan]{commit.author}[/cyan] [dim]{date_str}[/dim]")
                content.append(f"  {commit.message}")
                
                if commit.files_changed > 0:
                    stats = f"[dim]({commit.files_changed} files, {commit.insertions}+, {commit.deletions}-)[/dim]"
                    content.append(f"  {stats}")
                content.append("")
        
        preview = self.query_one("#preview-content", Static)
        preview.update("\n".join(content))
        
        self._set_status(f"Git log: {len(commits)} commits")

    def action_git_branches(self) -> None:
        """Show Git branches."""
        self._clear_delete_confirmation()
        self.help_visible = False
        
        try:
            tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
            current_path = Path(tabbed_tree.current_path)
        except (AttributeError, ValueError):
            current_path = self.current_path
        
        # Update Git service path
        self.enhanced_git_service = EnhancedGitService(current_path)
        
        if not self.enhanced_git_service.is_git_repository():
            self._set_status("Not a Git repository")
            return
        
        # Get branches
        branches = self.enhanced_git_service.get_branches(include_remote=True)
        
        content = []
        content.append("═══ Git Branches ═══")
        content.append("")
        
        if not branches:
            content.append("[dim italic]No branches found[/dim italic]")
        else:
            current_branch = self.enhanced_git_service.get_current_branch()
            
            # Local branches
            local_branches = [b for b in branches if not b.is_remote]
            if local_branches:
                content.append("📁 Local Branches:")
                for branch in local_branches:
                    status = ""
                    if branch.is_current:
                        status = " [green]✓ CURRENT[/green]"
                    elif branch.ahead and branch.ahead > 0:
                        status = f" [cyan]↑{branch.ahead}[/cyan]"
                    elif branch.behind and branch.behind > 0:
                        status = f" [yellow]↓{branch.behind}[/yellow]"
                    
                    commit = branch.last_commit[:8] if branch.last_commit else ""
                    content.append(f"  {branch.name} {status} [dim]{commit}[/dim]")
                content.append("")
            
            # Remote branches
            remote_branches = [b for b in branches if b.is_remote]
            if remote_branches:
                content.append("🌐 Remote Branches:")
                for branch in remote_branches[:10]:  # Limit to 10 remotes
                    commit = branch.last_commit[:8] if branch.last_commit else ""
                    content.append(f"  {branch.name} [dim]{commit}[/dim]")
                
                if len(remote_branches) > 10:
                    content.append(f"  [dim]... and {len(remote_branches) - 10} more[/dim]")
        
        preview = self.query_one("#preview-content", Static)
        preview.update("\n".join(content))
        
        self._set_status(f"Git branches: {len(branches)} total")

    def action_git_status(self) -> None:
        """Show Git repository status."""
        self._clear_delete_confirmation()
        self.help_visible = False
        
        try:
            tabbed_tree = self.query_one("#tree", TabbedDirectoryTree)
            current_path = Path(tabbed_tree.current_path)
        except (AttributeError, ValueError):
            current_path = self.current_path
        
        # Update Git service path
        self.enhanced_git_service = EnhancedGitService(current_path)
        
        if not self.enhanced_git_service.is_git_repository():
            self._set_status("Not a Git repository")
            return
        
        # Get repository status
        status = self.enhanced_git_service.get_repo_status()
        
        content = []
        content.append("═══ Git Repository Status ═══")
        content.append("")
        
        # Branch info
        branch_info = f"[bold]🌿 {status.branch}[/bold]"
        if status.ahead_by or status.behind_by:
            sync_info = []
            if status.ahead_by:
                sync_info.append(f"[cyan]↑{status.ahead_by}[/cyan]")
            if status.behind_by:
                sync_info.append(f"[yellow]↓{status.behind_by}[/yellow]")
            branch_info += f" {' '.join(sync_info)}"
        
        content.append(branch_info)
        
        # Working tree status
        if status.is_clean:
            content.append("[green]✓ Working tree clean[/green]")
        else:
            parts = []
            if status.staged_files:
                parts.append(f"[yellow]{len(status.staged_files)} staged[/yellow]")
            if status.modified_files:
                parts.append(f"[cyan]{len(status.modified_files)} modified[/cyan]")
            if status.untracked_files:
                parts.append(f"[blue]{len(status.untracked_files)} untracked[/blue]")
            if status.deleted_files:
                parts.append(f"[red]{len(status.deleted_files)} deleted[/red]")
            
            content.append(f"[yellow]⚠ {' | '.join(parts)}[/yellow]")
        
        # Stash info
        if status.stashes > 0:
            content.append(f"[blue]📦 {status.stashes} stashes[/blue]")
        
        content.append("")
        
        # Show files by category
        if status.staged_files:
            content.append("[yellow]📋 Staged files:[/yellow]")
            for file in status.staged_files[:10]:
                content.append(f"  [green]A[/green] {file}")
            if len(status.staged_files) > 10:
                content.append(f"  [dim]... and {len(status.staged_files) - 10} more[/dim]")
            content.append("")
        
        if status.modified_files:
            content.append("[cyan]📝 Modified files:[/cyan]")
            for file in status.modified_files[:10]:
                content.append(f"  [yellow]M[/yellow] {file}")
            if len(status.modified_files) > 10:
                content.append(f"  [dim]... and {len(status.modified_files) - 10} more[/dim]")
            content.append("")
        
        if status.untracked_files:
            content.append("[blue]❓ Untracked files:[/blue]")
            for file in status.untracked_files[:10]:
                content.append(f"  [blue]?[/blue] {file}")
            if len(status.untracked_files) > 10:
                content.append(f"  [dim]... and {len(status.untracked_files) - 10} more[/dim]")
            content.append("")
        
        if status.deleted_files:
            content.append("[red]🗑️  Deleted files:[/red]")
            for file in status.deleted_files[:10]:
                content.append(f"  [red]D[/red] {file}")
            if len(status.deleted_files) > 10:
                content.append(f"  [dim]... and {len(status.deleted_files) - 10} more[/dim]")
        
        preview = self.query_one("#preview-content", Static)
        preview.update("\n".join(content))
        
        total_changes = (len(status.staged_files) + len(status.modified_files) + 
                        len(status.untracked_files) + len(status.deleted_files))
        self._set_status(f"Git status: {status.branch} ({total_changes} changes)")
