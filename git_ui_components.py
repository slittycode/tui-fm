"""Git-specific UI components for enhanced Git integration."""
from typing import List, Optional, Callable
from datetime import datetime

from rich.console import Console, ConsoleOptions, RenderResult
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual import on
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Footer, Header, Label, Static, ListView, ListItem

from git_enhanced import EnhancedGitService, GitCommit, GitBranch, GitStash, GitDiff


class GitLogViewer(ListView):
    """A widget for viewing Git commit history."""
    
    def __init__(self, commits: List[GitCommit], on_commit_selected: Optional[Callable[[GitCommit], None]] = None):
        """Initialize Git log viewer.
        
        Args:
            commits: List of commits to display.
            on_commit_selected: Callback when a commit is selected.
        """
        self.commits = commits
        self.on_commit_selected = on_commit_selected
        super().__init__()
    
    def compose(self) -> None:
        """Compose the log viewer."""
        for commit in self.commits:
            # Format commit date
            date_str = commit.date.strftime("%Y-%m-%d %H:%M")
            
            # Create commit item
            commit_text = (
                f"[bold]{commit.short_hash}[/bold] "
                f"[cyan]{commit.author}[/cyan] "
                f"[dim]{date_str}[/dim]\n"
                f"{commit.message}"
            )
            
            # Add stats if available
            if commit.files_changed > 0:
                stats = f"[dim]({commit.files_changed} files, {commit.insertions}+, {commit.deletions}-)[/dim]"
                commit_text += f"\n{stats}"
            
            item = ListItem(Static(commit_text))
            item.commit = commit  # Store commit reference
            yield item
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle commit selection."""
        if self.on_commit_selected and hasattr(event.item, 'commit'):
            self.on_commit_selected(event.item.commit)


class GitBranchList(DataTable):
    """A widget for displaying Git branches."""
    
    def __init__(self, branches: List[GitBranch], on_branch_selected: Optional[Callable[[GitBranch], None]] = None):
        """Initialize branch list.
        
        Args:
            branches: List of branches to display.
            on_branch_selected: Callback when a branch is selected.
        """
        self.branches = branches
        self.on_branch_selected = on_branch_selected
        super().__init__()
    
    def compose(self) -> None:
        """Compose the branch list."""
        yield Static("🌿 Git Branches", classes="header")
        yield self
    
    def on_mount(self) -> None:
        """Set up the table when mounted."""
        self.add_column("Branch", key="name")
        self.add_column("Type", key="type")
        self.add_column("Status", key="status")
        self.add_column("Last Commit", key="commit")
        
        for branch in self.branches:
            # Format status
            status_parts = []
            if branch.is_current:
                status_parts.append("[green]✓ CURRENT[/green]")
            if branch.ahead and branch.ahead > 0:
                status_parts.append(f"[cyan]↑{branch.ahead}[/cyan]")
            if branch.behind and branch.behind > 0:
                status_parts.append(f"[yellow]↓{branch.behind}[/yellow]")
            
            status = " ".join(status_parts) if status_parts else ""
            
            # Format type
            branch_type = "[cyan]Remote[/cyan]" if branch.is_remote else "[green]Local[/green]"
            
            # Format commit (shorten if needed)
            commit = branch.last_commit[:8] if branch.last_commit else ""
            
            self.add_row(
                branch.name,
                branch_type,
                status,
                commit,
                key=branch.name
            )
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle branch selection."""
        if self.on_branch_selected and event.row_key.value:
            # Find the branch object
            for branch in self.branches:
                if branch.name == event.row_key.value:
                    self.on_branch_selected(branch)
                    break


class GitStashList(ListView):
    """A widget for displaying Git stashes."""
    
    def __init__(self, stashes: List[GitStash], on_stash_selected: Optional[Callable[[GitStash], None]] = None):
        """Initialize stash list.
        
        Args:
            stashes: List of stashes to display.
            on_stash_selected: Callback when a stash is selected.
        """
        self.stashes = stashes
        self.on_stash_selected = on_stash_selected
        super().__init__()
    
    def compose(self) -> None:
        """Compose the stash list."""
        if not self.stashes:
            yield ListItem(Static("[dim]No stashes found[/dim]"))
            return
        
        for stash in self.stashes:
            stash_text = (
                f"[bold]{stash.ref}[/bold] "
                f"[cyan]{stash.branch or 'unknown'}[/cyan]\n"
                f"{stash.message}"
            )
            
            item = ListItem(Static(stash_text))
            item.stash = stash  # Store stash reference
            yield item
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle stash selection."""
        if self.on_stash_selected and hasattr(event.item, 'stash'):
            self.on_stash_selected(event.item.stash)


class GitDiffViewer(Static):
    """A widget for displaying Git diffs."""
    
    def __init__(self, diffs: List[GitDiff]):
        """Initialize diff viewer.
        
        Args:
            diffs: List of diffs to display.
        """
        self.diffs = diffs
        super().__init__()
    
    def render(self) -> RenderResult:
        """Render the diff content."""
        if not self.diffs:
            return Panel("[dim]No changes to display[/dim]", title="📝 Git Diff")
        
        content = []
        
        for diff in self.diffs:
            # File header
            status_symbol = {
                "A": "[green]✓ ADDED[/green]",
                "D": "[red]✗ DELETED[/red]",
                "M": "[yellow]★ MODIFIED[/yellow]",
            }.get(diff.status, f"[blue]? {diff.status}[/blue]")
            
            content.append(f"{status_symbol} {diff.file_path}")
            
            # Stats
            if diff.additions > 0 or diff.deletions > 0:
                additions = f"[green]+{diff.additions}[/green]" if diff.additions > 0 else ""
                deletions = f"[red]-{diff.deletions}[/red]" if diff.deletions > 0 else ""
                stats = " ".join(filter(None, [additions, deletions]))
                if stats:
                    content.append(f"  [dim]({stats})[/dim]")
            
            # Show diff content if available and not too large
            if diff.content and len(diff.content) < 2000:
                content.append("")
                # Add a few lines of the actual diff
                diff_lines = diff.content.split('\n')[:10]
                for line in diff_lines:
                    if line.startswith('+'):
                        content.append(f"[green]{line}[/green]")
                    elif line.startswith('-'):
                        content.append(f"[red]{line}[/red]")
                    elif line.startswith('@@'):
                        content.append(f"[cyan]{line}[/cyan]")
                    else:
                        content.append(line)
                
                if len(diff.content.split('\n')) > 10:
                    content.append("[dim]... (diff truncated)[/dim]")
            
            content.append("")
        
        return Panel(
            "\n".join(content),
            title=f"📝 Git Diff ({len(self.diffs)} files)",
            border_style="blue"
        )


class GitRepoStatus(Static):
    """A widget for displaying repository status."""
    
    def __init__(self, repo_status):
        """Initialize repository status widget.
        
        Args:
            repo_status: GitRepoStatus object.
        """
        self.repo_status = repo_status
        super().__init__()
    
    def render(self) -> RenderResult:
        """Render the repository status."""
        status = self.repo_status
        
        # Branch info
        branch_info = f"[bold]🌿 {status.branch}[/bold]"
        if status.ahead_by or status.behind_by:
            sync_info = []
            if status.ahead_by:
                sync_info.append(f"[cyan]↑{status.ahead_by}[/cyan]")
            if status.behind_by:
                sync_info.append(f"[yellow]↓{status.behind_by}[/yellow]")
            branch_info += f" {' '.join(sync_info)}"
        
        # Working tree status
        if status.is_clean:
            working_tree = "[green]✓ Working tree clean[/green]"
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
            
            working_tree = f"[yellow]⚠ {' | '.join(parts)}[/yellow]"
        
        # Stash info
        stash_info = ""
        if status.stashes > 0:
            stash_info = f"\n[blue]📦 {status.stashes} stashes[/blue]"
        
        content = f"{branch_info}\n{working_tree}{stash_info}"
        
        return Panel(
            content,
            title="📊 Repository Status",
            border_style="green" if status.is_clean else "yellow"
        )


class GitBranchSwitcher(ModalScreen[str]):
    """Modal screen for switching Git branches."""
    
    BINDINGS = [
        Binding("escape", "dismiss(None)", "Cancel"),
        Binding("enter", "select_branch", "Switch"),
        Binding("up", "cursor_up", "Up"),
        Binding("down", "cursor_down", "Down"),
    ]
    
    def __init__(self, git_service: EnhancedGitService):
        """Initialize branch switcher.
        
        Args:
            git_service: Enhanced Git service instance.
        """
        super().__init__()
        self.git_service = git_service
        self.branches = []
        self.branch_list: Optional[DataTable] = None
    
    def compose(self) -> None:
        """Compose the branch switcher."""
        with Container(id="branch-switcher"):
            yield Static("🌿 Switch Branch", classes="modal-title")
            yield self._create_branch_list()
            with Horizontal(id="branch-actions"):
                yield Button("Switch", variant="primary", id="switch-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")
    
    def _create_branch_list(self) -> DataTable:
        """Create the branch list table."""
        self.branch_list = DataTable()
        self.branch_list.add_column("Branch", key="name")
        self.branch_list.add_column("Type", key="type")
        self.branch_list.add_column("Status", key="status")
        
        # Load branches
        self.branches = self.git_service.get_branches()
        
        for branch in self.branches:
            # Skip current branch for switching
            if branch.is_current:
                continue
            
            # Format status
            status_parts = []
            if branch.ahead and branch.ahead > 0:
                status_parts.append(f"[cyan]↑{branch.ahead}[/cyan]")
            if branch.behind and branch.behind > 0:
                status_parts.append(f"[yellow]↓{branch.behind}[/yellow]")
            
            status = " ".join(status_parts) if status_parts else ""
            
            # Format type
            branch_type = "[cyan]Remote[/cyan]" if branch.is_remote else "[green]Local[/green]"
            
            self.branch_list.add_row(
                branch.name,
                branch_type,
                status,
                key=branch.name
            )
        
        return self.branch_list
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "switch-btn":
            self.action_select_branch()
        elif event.button.id == "cancel-btn":
            self.dismiss(None)
    
    def action_select_branch(self) -> None:
        """Switch to selected branch."""
        if self.branch_list and self.branch_list.cursor_row:
            branch_name = self.branch_list.get_row_key(self.branch_list.cursor_row)
            if branch_name:
                success, message = self.git_service.switch_branch(branch_name)
                if success:
                    self.dismiss(branch_name)
                else:
                    # Show error message
                    self.notify(f"Failed to switch branch: {message}", severity="error")
    
    def action_dismiss(self, result: Optional[str]) -> None:
        """Dismiss the modal."""
        self.dismiss(result)


class GitCommitViewer(ModalScreen[None]):
    """Modal screen for viewing commit details."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("d", "show_diff", "Show Diff"),
    ]
    
    def __init__(self, commit: GitCommit, git_service: EnhancedGitService):
        """Initialize commit viewer.
        
        Args:
            commit: Git commit to view.
            git_service: Enhanced Git service instance.
        """
        super().__init__()
        self.commit = commit
        self.git_service = git_service
    
    def compose(self) -> None:
        """Compose the commit viewer."""
        with Container(id="commit-viewer"):
            yield Static("📝 Commit Details", classes="modal-title")
            yield self._create_commit_info()
            yield Static("Changes:", classes="section-title")
            yield self._create_changes_info()
            with Horizontal(id="commit-actions"):
                yield Button("Show Diff", variant="primary", id="diff-btn")
                yield Button("Close", variant="default", id="close-btn")
    
    def _create_commit_info(self) -> Static:
        """Create commit information display."""
        date_str = self.commit.date.strftime("%Y-%m-%d %H:%M:%S")
        
        info = f"""
[bold]Hash:[/bold] {self.commit.hash}
[bold]Author:[/bold] {self.commit.author} <{self.commit.email}>
[bold]Date:[/bold] {date_str}
[bold]Message:[/bold] {self.commit.message}

[bold]Statistics:[/bold]
  Files changed: {self.commit.files_changed}
  Insertions: [green]+{self.commit.insertions}[/green]
  Deletions: [red]-{self.commit.deletions}[/red]
        """.strip()
        
        return Static(info)
    
    def _create_changes_info(self) -> Static:
        """Create changes information display."""
        # Get diff for this commit
        diffs = self.git_service.get_diff(commit_hash=self.commit.hash + "^")
        
        if not diffs:
            return Static("[dim]No file changes to display[/dim]")
        
        content = []
        for diff in diffs[:10]:  # Limit to 10 files
            status_symbol = {
                "A": "[green]✓[/green]",
                "D": "[red]✗[/red]",
                "M": "[yellow]★[/yellow]",
            }.get(diff.status, "?")
            
            content.append(f"{status_symbol} {diff.file_path}")
            
            if diff.additions > 0 or diff.deletions > 0:
                additions = f"[green]+{diff.additions}[/green]" if diff.additions > 0 else ""
                deletions = f"[red]-{diff.deletions}[/red]" if diff.deletions > 0 else ""
                stats = " ".join(filter(None, [additions, deletions]))
                if stats:
                    content.append(f"  [dim]({stats})[/dim]")
        
        if len(diffs) > 10:
            content.append(f"[dim]... and {len(diffs) - 10} more files[/dim]")
        
        return Static("\n".join(content))
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "diff-btn":
            self.action_show_diff()
        elif event.button.id == "close-btn":
            self.dismiss()
    
    def action_show_diff(self) -> None:
        """Show full diff for this commit."""
        diffs = self.git_service.get_diff(commit_hash=self.commit.hash + "^")
        if diffs:
            # This would open a diff viewer modal
            self.notify("Diff viewer not yet implemented", severity="info")
    
    def action_dismiss(self) -> None:
        """Dismiss the modal."""
        self.dismiss()
