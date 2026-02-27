"""Mouse event handling system for the TUI File Manager."""
from pathlib import Path
from typing import Optional, Set

from textual.widgets import DirectoryTree


class MouseHandler:
    """Handle mouse events for file navigation and operations."""
    
    def __init__(self, directory_tree: DirectoryTree) -> None:
        """Initialize the mouse handler.
        
        Args:
            directory_tree: The DirectoryTree widget to handle events for.
        """
        self.tree = directory_tree
        self.selected_paths: Set[Path] = set()
        self.last_clicked_path: Optional[Path] = None
        self.click_count = 0
        self.is_ctrl_pressed = False
        self.is_shift_pressed = False
    
    def handle_click(self, event) -> None:
        """Handle single click events.
        
        Args:
            event: The click event.
        """
        # Get the clicked node/path
        clicked_path = self._get_clicked_path(event)
        if clicked_path is None:
            return
        
        # Handle selection based on modifier keys
        if self.is_ctrl_pressed:
            # Ctrl+Click: Toggle selection
            self._toggle_selection(clicked_path)
        elif self.is_shift_pressed and self.last_clicked_path:
            # Shift+Click: Range selection
            self._select_range(self.last_clicked_path, clicked_path)
        else:
            # Normal click: Single selection
            self._select_single(clicked_path)
        
        self.click_count = 1
    
    def handle_double_click(self, event) -> None:
        """Handle double click events.
        
        Args:
            event: The double click event.
        """
        clicked_path = self._get_clicked_path(event)
        if clicked_path is None:
            return
        
        # Double click to navigate or open
        if clicked_path.is_dir():
            self._navigate_to_directory(clicked_path)
        else:
            self._open_file(clicked_path)
    
    def handle_mouse_down(self, event) -> None:
        """Handle mouse down events for modifier key tracking.
        
        Args:
            event: The mouse down event.
        """
        # Update modifier key states
        self.is_ctrl_pressed = getattr(event, 'ctrl', False)
        self.is_shift_pressed = getattr(event, 'shift', False)
    
    def handle_mouse_up(self, event) -> None:
        """Handle mouse up events.
        
        Args:
            event: The mouse up event.
        """
        # Reset modifier key states
        self.is_ctrl_pressed = False
        self.is_shift_pressed = False
    
    # Backward compatibility methods
    def on_click(self, event) -> None:
        """Backward compatibility for on_click."""
        return self.handle_click(event)
    
    def on_double_click(self, event) -> None:
        """Backward compatibility for on_double_click."""
        return self.handle_double_click(event)
    
    def on_mouse_down(self, event) -> None:
        """Backward compatibility for on_mouse_down."""
        return self.handle_mouse_down(event)
    
    def on_mouse_up(self, event) -> None:
        """Backward compatibility for on_mouse_up."""
        return self.handle_mouse_up(event)
    
    def _get_clicked_path(self, event) -> Optional[Path]:
        """Get the path that was clicked.
        
        Args:
            event: The click event.
            
        Returns:
            The clicked path, or None if no valid path was clicked.
        """
        try:
            # Get the node at the click position
            node = self.tree.get_node_at(event.x, event.y)
            if node is None:
                return None
            
            # Convert node to path
            if hasattr(node, 'data') and node.data:
                return Path(node.data)
            
            # Fallback: try to get path from node label
            if hasattr(node, 'label'):
                label_text = str(node.label)
                # Extract filename from label (remove icons and git status)
                filename = self._extract_filename_from_label(label_text)
                if filename:
                    # Try to construct full path
                    current_path = Path(self.tree.path)
                    return current_path / filename
            
            return None
        except Exception:
            return None
    
    def _extract_filename_from_label(self, label: str) -> Optional[str]:
        """Extract filename from a label that may contain icons and status.
        
        Args:
            label: The label text.
            
        Returns:
            The extracted filename, or None if not found.
        """
        # Remove icons (Unicode characters beyond ASCII) and git status symbols
        parts = label.split()
        if not parts:
            return None
        
        # The last part is usually the filename
        filename = parts[-1]
        
        # Validate filename
        if filename and not any(char in filename for char in '📁📂📄📝⚙️🗃️🔐👁️📦🐍🧪🔨🎯📚🎜🎵🎬🖼️📋📘📕📗📙🔧☕🐍🐹🦀💎🍎🎯🔷🌙📊🌐🎨💚🔥📜🐪🐘'):
            return filename
        
        return None
    
    def _select_single(self, path: Path) -> None:
        """Select a single path.
        
        Args:
            path: The path to select.
        """
        self.selected_paths.clear()
        self.selected_paths.add(path)
        self.last_clicked_path = path
        
        # Update the tree selection
        self._update_tree_selection()
    
    def _toggle_selection(self, path: Path) -> None:
        """Toggle selection of a path.
        
        Args:
            path: The path to toggle selection for.
        """
        if path in self.selected_paths:
            self.selected_paths.remove(path)
        else:
            self.selected_paths.add(path)
        
        self._update_tree_selection()
    
    def _select_range(self, start_path: Path, end_path: Path) -> None:
        """Select a range of paths between start and end.
        
        Args:
            start_path: The start of the range.
            end_path: The end of the range.
        """
        # This is a simplified implementation
        # In a real implementation, you'd need to:
        # 1. Get all visible nodes in the tree
        # 2. Find the positions of start and end paths
        # 3. Select all paths between them
        
        # For now, just select both paths
        self.selected_paths.clear()
        self.selected_paths.add(start_path)
        self.selected_paths.add(end_path)
        self.last_clicked_path = end_path
        
        self._update_tree_selection()
    
    def _navigate_to_directory(self, path: Path) -> None:
        """Navigate to a directory.
        
        Args:
            path: The directory path to navigate to.
        """
        if not path.is_dir():
            return
        
        try:
            # Update the tree path
            self.tree.path = str(path)
            self.tree._reload()
            
            # Clear selection when navigating
            self.selected_paths.clear()
            self.last_clicked_path = None
            
            # Post a navigation event if needed
            if hasattr(self.tree.app, '_on_directory_navigate'):
                self.tree.app._on_directory_navigate(path)
                
        except Exception:
            # Handle navigation errors silently
            pass
    
    def _open_file(self, path: Path) -> None:
        """Open a file.
        
        Args:
            path: The file path to open.
        """
        if path.is_dir():
            return
        
        try:
            # Post a file open event if the app supports it
            if hasattr(self.tree.app, '_on_file_open'):
                self.tree.app._on_file_open(path)
            elif hasattr(self.tree.app, '_load_and_render_preview'):
                # Fallback: try to load preview
                self.tree.app._load_and_render_preview(path, 0, "")
                
        except Exception:
            # Handle file open errors silently
            pass
    
    def _update_tree_selection(self) -> None:
        """Update the tree widget to reflect the current selection."""
        try:
            # Clear current tree selection
            if hasattr(self.tree, 'clear_selection'):
                self.tree.clear_selection()
            
            # Select each path in our selection
            for path in self.selected_paths:
                try:
                    # Find and select the node for this path
                    node = self._find_node_for_path(path)
                    if node and hasattr(node, 'select'):
                        node.select()
                except Exception:
                    continue
                    
        except Exception:
            # Handle selection update errors silently
            pass
    
    def _find_node_for_path(self, path: Path) -> Optional:
        """Find the tree node for a given path.
        
        Args:
            path: The path to find.
            
        Returns:
            The tree node, or None if not found.
        """
        try:
            # This is a simplified implementation
            # In a real implementation, you'd traverse the tree
            # to find the node matching the path
            
            # For now, try to get the node by path
            if hasattr(self.tree, '_get_node'):
                return self.tree._get_node(str(path))
            
            return None
        except Exception:
            return None
    
    def get_selected_paths(self) -> Set[Path]:
        """Get the currently selected paths.
        
        Returns:
            Set of selected paths.
        """
        return self.selected_paths.copy()
    
    def clear_selection(self) -> None:
        """Clear all selections."""
        self.selected_paths.clear()
        self.last_clicked_path = None
        self._update_tree_selection()
    
    def select_all(self) -> None:
        """Select all visible items in the tree."""
        try:
            # This is a simplified implementation
            # In a real implementation, you'd iterate through all visible nodes
            # and add them to the selection
            
            # For now, just clear the selection
            self.clear_selection()
            
        except Exception:
            pass
    
    def get_selection_info(self) -> dict:
        """Get information about the current selection.
        
        Returns:
            Dictionary with selection information.
        """
        selected_count = len(self.selected_paths)
        file_count = sum(1 for path in self.selected_paths if path.is_file())
        dir_count = sum(1 for path in self.selected_paths if path.is_dir())
        
        return {
            "total_selected": selected_count,
            "files_selected": file_count,
            "directories_selected": dir_count,
            "selected_paths": list(self.selected_paths),
        }
    
    def __repr__(self) -> str:
        return f"MouseHandler(selected_count={len(self.selected_paths)})"
