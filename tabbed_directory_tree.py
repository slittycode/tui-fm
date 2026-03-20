"""Tabbed directory tree widget for the File Manager."""
from pathlib import Path
from typing import Optional

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static, Tab, TabbedContent, TabPane, Tabs

from filterable_tree import FilterableDirectoryTree
from tab_manager import TabManager


class TabbedDirectoryTree(Vertical):
    """A widget that combines tabs with directory trees."""
    
    def __init__(self, initial_path: Path, **kwargs) -> None:
        """Initialize the tabbed directory tree.
        
        Args:
            initial_path: Initial path for the first tab.
            **kwargs: Additional arguments for Vertical.
        """
        super().__init__(**kwargs)
        self.tab_manager = TabManager()
        self._tree_widgets: dict[str, FilterableDirectoryTree] = {}
        
        # Set initial path
        self.tab_manager.active_tab.path = initial_path
    
    def compose(self) -> ComposeResult:
        """Create the tabbed interface."""
        yield Static("📂 File Browser", id="tree-header")
        
        with Tabs(id="directory-tabs"):
            # Initial tab will be added in on_mount
            pass
        
        with TabbedContent(id="directory-content"):
            # Tab panes will be added in on_mount
            pass
        
        yield Static("", id="tree-footer")
    
    def on_mount(self) -> None:
        """Initialize tabs when the widget is mounted."""
        self._rebuild_tabs()
    
    def _rebuild_tabs(self) -> None:
        """Rebuild all tabs and their content."""
        tabs_widget = self.query_one("#directory-tabs", Tabs)
        content_widget = self.query_one("#directory-content", TabbedContent)
        
        # Clear existing tabs and content
        tabs_widget.clear().call_next(self)
        content_widget.clear_panes().call_next(self)
        self._tree_widgets = {}
        
        # Recreate tabs and their panes
        for tab_state in self.tab_manager:
            # Create tab
            tab_title = tab_state.display_title
            if tab_state.is_locked:
                tab_title = f"🔒 {tab_title}"
            
            tab = Tab(tab_title, id=f"tab-{tab_state.id}")
            tabs_widget.add_tab(tab).call_next(self)
            
            # Create tab pane with directory tree
            tree = FilterableDirectoryTree(str(tab_state.path), id=f"tree-{tab_state.id}")
            if tab_state.filter_query:
                tree.set_filter_query(tab_state.filter_query)
            pane = TabPane(tab_state.display_title, tree, id=f"pane-{tab_state.id}")
            content_widget.add_pane(pane).call_next(self)
            self._tree_widgets[tab_state.id] = tree

        self._sync_active_widgets()
        self._update_footer()
        active_tree = self.get_active_tree()
        if active_tree:
            active_tree.focus()

    def _sync_active_widgets(self) -> None:
        """Keep tabs and content panes aligned with the active tab state."""
        if not self.tab_manager.tabs:
            return

        active_tab_id = self.tab_manager.active_tab.id
        tabs_widget = self.query_one("#directory-tabs", Tabs)
        content_widget = self.query_one("#directory-content", TabbedContent)
        tabs_widget.active = f"tab-{active_tab_id}"
        content_widget.active = f"pane-{active_tab_id}"
    
    def add_tab(self, path: Optional[Path] = None) -> str:
        """Add a new tab.
        
        Args:
            path: Path for the new tab. Defaults to current tab's path.
            
        Returns:
            ID of the created tab.
        """
        try:
            new_tab = self.tab_manager.add_tab(path)
            self._rebuild_tabs()
            return new_tab.id
        except RuntimeError as e:
            self._show_error(str(e))
            return ""
    
    def close_tab(self, tab_id: Optional[str] = None) -> bool:
        """Close a tab.
        
        Args:
            tab_id: ID of the tab to close. If None, closes active tab.
            
        Returns:
            True if tab was closed, False otherwise.
        """
        try:
            if tab_id is None:
                tab_id = self.tab_manager.active_tab.id
            
            tab = self.tab_manager.get_tab_by_id(tab_id)
            if tab and tab.is_locked:
                self._show_error("Cannot close locked tab")
                return False
            
            success = self.tab_manager.close_tab(tab_id)
            if success:
                # Clean up tree widget
                if tab_id in self._tree_widgets:
                    del self._tree_widgets[tab_id]
                self._rebuild_tabs()
            return success
        except RuntimeError as e:
            self._show_error(str(e))
            return False
    
    def switch_to_tab(self, index: int) -> bool:
        """Switch to tab by index.
        
        Args:
            index: Index of the tab to switch to.
            
        Returns:
            True if switch was successful.
        """
        success = self.tab_manager.switch_to_tab(index)
        if success:
            self._sync_active_widgets()
            self._update_footer()
            active_tree = self.get_active_tree()
            if active_tree:
                active_tree.focus()
        return success
    
    def switch_to_tab_by_id(self, tab_id: str) -> bool:
        """Switch to tab by ID.
        
        Args:
            tab_id: ID of the tab to switch to.
            
        Returns:
            True if switch was successful.
        """
        success = self.tab_manager.switch_to_tab_by_id(tab_id)
        if success:
            self._sync_active_widgets()
            self._update_footer()
            active_tree = self.get_active_tree()
            if active_tree:
                active_tree.focus()
        return success
    
    def next_tab(self) -> bool:
        """Switch to the next tab.
        
        Returns:
            True if switch was successful.
        """
        success = self.tab_manager.next_tab()
        if success:
            self._sync_active_widgets()
            self._update_footer()
            active_tree = self.get_active_tree()
            if active_tree:
                active_tree.focus()
        return success
    
    def previous_tab(self) -> bool:
        """Switch to the previous tab.
        
        Returns:
            True if switch was successful.
        """
        success = self.tab_manager.previous_tab()
        if success:
            self._sync_active_widgets()
            self._update_footer()
            active_tree = self.get_active_tree()
            if active_tree:
                active_tree.focus()
        return success
    
    def get_active_tree(self) -> Optional[FilterableDirectoryTree]:
        """Get the currently active directory tree.
        
        Returns:
            The active tree widget, or None if no active tab.
        """
        active_tab = self.tab_manager.active_tab
        return self._tree_widgets.get(active_tab.id)
    
    def get_active_path(self) -> Path:
        """Get the path of the currently active tab.
        
        Returns:
            Path of the active tab.
        """
        return self.tab_manager.active_tab.path
    
    def update_active_tab_path(self, path: Path) -> None:
        """Update the path of the currently active tab.
        
        Args:
            path: New path for the active tab.
        """
        self.tab_manager.update_active_tab(path=path)

        active_tree = self.get_active_tree()
        if active_tree:
            # Update path without triggering async reactive watchers directly.
            active_tree.set_reactive(FilterableDirectoryTree.path, path)
            root_data_type = type(active_tree.root.data)
            active_tree.reset_node(
                active_tree.root,
                str(path),
                root_data_type(active_tree.PATH(path)),
            )
            active_tree.reload()
        else:
            self._rebuild_tabs()

        self._update_tab_title(self.tab_manager.active_tab.id)
        self._update_footer()
    
    def update_active_tab_filter(self, filter_query: str) -> None:
        """Update the filter query of the currently active tab.
        
        Args:
            filter_query: New filter query.
        """
        self.tab_manager.update_active_tab(filter_query=filter_query)
        
        # Update the tree widget
        active_tree = self.get_active_tree()
        if active_tree:
            active_tree.set_filter_query(filter_query)
    
    def duplicate_active_tab(self) -> bool:
        """Duplicate the currently active tab.
        
        Returns:
            True if duplication was successful.
        """
        try:
            self.tab_manager.duplicate_active_tab()
            self._rebuild_tabs()
            return True
        except RuntimeError as e:
            self._show_error(str(e))
            return False
    
    def toggle_active_tab_lock(self) -> None:
        """Toggle the lock state of the currently active tab."""
        self.tab_manager.toggle_active_tab_lock()
        self._update_tab_title(self.tab_manager.active_tab.id)
    
    def _update_tab_title(self, tab_id: str) -> None:
        """Update the title of a specific tab.
        
        Args:
            tab_id: ID of the tab to update.
        """
        tab = self.tab_manager.get_tab_by_id(tab_id)
        if not tab:
            return
        
        title = tab.display_title
        if tab.is_locked:
            title = f"🔒 {title}"

        tab_widgets = list(self.query(f"#tab-{tab_id}", Tab))
        if tab_widgets:
            tab_widgets[0].update(title)
    
    def _update_footer(self) -> None:
        """Update the footer with current tab information."""
        footer = self.query_one("#tree-footer", Static)
        active_tab = self.tab_manager.active_tab
        tab_info = f"🏠 {active_tab.path} | Tab {self.tab_manager.active_tab_index + 1}/{len(self.tab_manager)}"
        
        if active_tab.is_locked:
            tab_info += " | 🔒 Locked"
        
        footer.update(tab_info)
    
    def _show_error(self, message: str) -> None:
        """Show an error message in the footer.
        
        Args:
            message: Error message to show.
        """
        footer = self.query_one("#tree-footer", Static)
        footer.update(f"❌ Error: {message}")
    
    def on_tab_activated(self, event: Tabs.TabActivated) -> None:
        """Handle tab activation event.
        
        Args:
            event: The tab activation event.
        """
        # Extract tab ID from the tab widget ID
        tab_id = event.tab.id.replace("tab-", "")
        self.tab_manager.switch_to_tab_by_id(tab_id)
        content_widget = self.query_one("#directory-content", TabbedContent)
        content_widget.active = f"pane-{tab_id}"
        self._update_footer()
        
        # Focus the active tree
        active_tree = self.get_active_tree()
        if active_tree:
            active_tree.focus()
    
    def get_tab_count(self) -> int:
        """Get the number of tabs.
        
        Returns:
            Number of tabs.
        """
        return len(self.tab_manager)
    
    def get_max_tabs(self) -> int:
        """Get the maximum number of tabs.
        
        Returns:
            Maximum number of tabs.
        """
        return self.tab_manager.max_tabs
    
    def is_at_max_tabs(self) -> bool:
        """Check if the maximum number of tabs has been reached.
        
        Returns:
            True if at max tabs, False otherwise.
        """
        return len(self.tab_manager) >= self.tab_manager.max_tabs
