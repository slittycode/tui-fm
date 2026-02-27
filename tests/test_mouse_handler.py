"""Tests for mouse handler functionality."""
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock

import pytest

from filterable_tree import FilterableDirectoryTree
from mouse_handler import MouseHandler


class TestMouseHandler:
    """Test cases for MouseHandler class."""
    
    def test_mouse_handler_initialization(self) -> None:
        """Test MouseHandler initialization."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        assert handler.tree == mock_tree
        assert isinstance(handler.selected_paths, set)
        assert len(handler.selected_paths) == 0
        assert handler.last_clicked_path is None
        assert handler.click_count == 0
        assert handler.is_ctrl_pressed is False
        assert handler.is_shift_pressed is False
    
    def test_select_single_path(self) -> None:
        """Test selecting a single path."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        test_path = Path("/test/file.py")
        handler._select_single(test_path)
        
        assert len(handler.selected_paths) == 1
        assert test_path in handler.selected_paths
        assert handler.last_clicked_path == test_path
    
    def test_toggle_selection(self) -> None:
        """Test toggling selection of a path."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        test_path = Path("/test/file.py")
        
        # First toggle should select
        handler._toggle_selection(test_path)
        assert test_path in handler.selected_paths
        
        # Second toggle should deselect
        handler._toggle_selection(test_path)
        assert test_path not in handler.selected_paths
    
    def test_select_range(self) -> None:
        """Test selecting a range of paths."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        start_path = Path("/test/file1.py")
        end_path = Path("/test/file2.py")
        
        handler._select_range(start_path, end_path)
        
        # Should select both paths (simplified implementation)
        assert len(handler.selected_paths) == 2
        assert start_path in handler.selected_paths
        assert end_path in handler.selected_paths
    
    def test_clear_selection(self) -> None:
        """Test clearing selection."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        # Add some selections
        handler.selected_paths.add(Path("/test/file1.py"))
        handler.selected_paths.add(Path("/test/file2.py"))
        handler.last_clicked_path = Path("/test/file1.py")
        
        # Clear selection
        handler.clear_selection()
        
        assert len(handler.selected_paths) == 0
        assert handler.last_clicked_path is None
    
    def test_get_selected_paths(self) -> None:
        """Test getting selected paths."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        # Add selections
        test_paths = [
            Path("/test/file1.py"),
            Path("/test/file2.py"),
        ]
        
        for path in test_paths:
            handler.selected_paths.add(path)
        
        selected = handler.get_selected_paths()
        
        assert len(selected) == 2
        assert all(path in selected for path in test_paths)
        
        # Verify it returns a copy (modifying shouldn't affect original)
        selected.add(Path("/test/file3.py"))
        assert len(handler.selected_paths) == 2
    
    def test_get_selection_info(self) -> None:
        """Test getting selection information."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        # Add mixed selections
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test.py"
            file_path.write_text("test")
            
            dir_path = Path(temp_dir) / "test_dir"
            dir_path.mkdir()
            
            handler.selected_paths.add(file_path)
            handler.selected_paths.add(dir_path)
            
            info = handler.get_selection_info()
            
            assert info["total_selected"] == 2
            assert info["files_selected"] == 1
            assert info["directories_selected"] == 1
            assert len(info["selected_paths"]) == 2
            assert file_path in info["selected_paths"]
            assert dir_path in info["selected_paths"]
    
    def test_extract_filename_from_label(self) -> None:
        """Test extracting filename from label with icons."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        # Test labels with icons
        test_cases = [
            ("🐍 test.py", "test.py"),
            ("📋 config.json", "config.json"),
            ("📁 src", "src"),
            ("📂 .git", ".git"),
            ("🖼️ image.jpg", "image.jpg"),
            ("📄 README.md", "README.md"),
        ]
        
        for label, expected_filename in test_cases:
            filename = handler._extract_filename_from_label(label)
            assert filename == expected_filename
    
    def test_extract_filename_from_label_invalid(self) -> None:
        """Test extracting filename from invalid labels."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        # Test invalid labels
        invalid_labels = [
            "",
            "   ",
            "🐍",  # Only icon
            "📁 📂 📄",  # Only icons
        ]
        
        for label in invalid_labels:
            filename = handler._extract_filename_from_label(label)
            assert filename is None
    
    def test_navigate_to_directory(self) -> None:
        """Test navigating to a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()
            
            # Create mock tree
            mock_tree = Mock()
            mock_tree.path = temp_dir
            mock_tree._reload = Mock()
            
            handler = MouseHandler(mock_tree)
            handler._navigate_to_directory(subdir)
            
            # Should update tree path and reload
            assert mock_tree.path == str(subdir)
            mock_tree._reload.assert_called_once()
            
            # Should clear selection
            assert len(handler.selected_paths) == 0
            assert handler.last_clicked_path is None
    
    def test_navigate_to_file(self) -> None:
        """Test navigating to a file (should not navigate)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file
            file_path = Path(temp_dir) / "test.py"
            file_path.write_text("test")
            
            mock_tree = Mock()
            mock_tree._reload = Mock()
            
            handler = MouseHandler(mock_tree)
            handler._navigate_to_directory(file_path)
            
            # Should not navigate or reload
            mock_tree._reload.assert_not_called()
    
    def test_open_file(self) -> None:
        """Test opening a file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file
            file_path = Path(temp_dir) / "test.py"
            file_path.write_text("test")
            
            # Create mock tree with app
            mock_app = Mock()
            mock_app._on_file_open = Mock()
            
            mock_tree = Mock()
            mock_tree.app = mock_app
            
            handler = MouseHandler(mock_tree)
            handler._open_file(file_path)
            
            # Should call app's file open method
            mock_app._on_file_open.assert_called_once_with(file_path)
    
    def test_open_directory(self) -> None:
        """Test opening a directory (should not open)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a directory
            dir_path = Path(temp_dir) / "test_dir"
            dir_path.mkdir()
            
            mock_app = Mock()
            mock_app._on_file_open = Mock()
            
            mock_tree = Mock()
            mock_tree.app = mock_app
            
            handler = MouseHandler(mock_tree)
            handler._open_file(dir_path)
            
            # Should not call app's file open method
            mock_app._on_file_open.assert_not_called()
    
    def test_mouse_down_modifier_tracking(self) -> None:
        """Test mouse down event tracks modifier keys."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        # Mock mouse down event with Ctrl
        mock_event = Mock()
        mock_event.ctrl = True
        mock_event.shift = False
        
        handler.on_mouse_down(mock_event)
        
        assert handler.is_ctrl_pressed is True
        assert handler.is_shift_pressed is False
    
    def test_mouse_up_modifier_reset(self) -> None:
        """Test mouse up event resets modifier keys."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        # Set modifier keys
        handler.is_ctrl_pressed = True
        handler.is_shift_pressed = True
        
        # Mock mouse up event
        mock_event = Mock()
        handler.on_mouse_up(mock_event)
        
        assert handler.is_ctrl_pressed is False
        assert handler.is_shift_pressed is False
    
    def test_click_with_ctrl_modifier(self) -> None:
        """Test click with Ctrl modifier toggles selection."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        test_path = Path("/test/file.py")
        
        # Mock click event
        mock_event = Mock()
        mock_event.ctrl = True
        mock_event.shift = False
        
        # Mock _get_clicked_path to return our test path
        handler._get_clicked_path = Mock(return_value=test_path)
        
        handler.on_click(mock_event)
        
        # Should toggle selection and path should be selected
        assert test_path in handler.selected_paths
        assert handler.click_count == 1
    
    def test_click_with_shift_modifier(self) -> None:
        """Test click with Shift modifier selects range."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        start_path = Path("/test/file1.py")
        end_path = Path("/test/file2.py")
        
        # Set up initial state
        handler.last_clicked_path = start_path
        
        # Set modifier key state
        handler.is_shift_pressed = True
        
        # Mock click event
        mock_event = Mock()
        mock_event.ctrl = False
        mock_event.shift = True
        
        # Mock _get_clicked_path to return end path
        handler._get_clicked_path = Mock(return_value=end_path)
        
        handler.on_click(mock_event)
        
        # Should select range (both paths should be selected)
        assert start_path in handler.selected_paths
        assert end_path in handler.selected_paths
        assert handler.last_clicked_path == end_path
    
    def test_double_click_navigation(self) -> None:
        """Test double click navigates directories and opens files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file and directory
            file_path = Path(temp_dir) / "test.py"
            file_path.write_text("test")
            
            dir_path = Path(temp_dir) / "test_dir"
            dir_path.mkdir()
            
            mock_tree = Mock()
            handler = MouseHandler(mock_tree)
            
            # Mock methods
            handler._get_clicked_path = Mock()
            handler._navigate_to_directory = Mock()
            handler._open_file = Mock()
            
            # Test double click on directory
            handler._get_clicked_path.return_value = dir_path
            mock_event = Mock()
            
            handler.on_double_click(mock_event)
            
            handler._navigate_to_directory.assert_called_once_with(dir_path)
            handler._open_file.assert_not_called()
            
            # Reset mocks
            handler._navigate_to_directory.reset_mock()
            handler._open_file.reset_mock()
            
            # Test double click on file
            handler._get_clicked_path.return_value = file_path
            
            handler.on_double_click(mock_event)
            
            handler._open_file.assert_called_once_with(file_path)
            handler._navigate_to_directory.assert_not_called()
    
    def test_get_clicked_path_none(self) -> None:
        """Test handling when no valid path is clicked."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        # Mock click event that returns None
        mock_event = Mock()
        handler._get_clicked_path = Mock(return_value=None)
        
        # Should not raise exception
        handler.on_click(mock_event)
        
        # Should not update selection
        assert len(handler.selected_paths) == 0
    
    def test_repr(self) -> None:
        """Test string representation."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        # Add some selections
        handler.selected_paths.add(Path("/test/file1.py"))
        handler.selected_paths.add(Path("/test/file2.py"))
        
        repr_str = repr(handler)
        assert "MouseHandler" in repr_str
        assert "selected_count=2" in repr_str
    
    def test_select_all(self) -> None:
        """Test select all functionality."""
        mock_tree = Mock()
        handler = MouseHandler(mock_tree)
        
        # Add some selections first
        handler.selected_paths.add(Path("/test/file1.py"))
        
        # Select all should clear current selections
        handler.select_all()
        
        # Should be empty (simplified implementation)
        assert len(handler.selected_paths) == 0
