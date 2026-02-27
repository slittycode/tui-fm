"""Tests for tab management functionality."""
from pathlib import Path

import pytest

from tab_manager import TabManager, TabState


class TestTabState:
    """Test cases for TabState class."""

    def test_tab_state_initialization(self) -> None:
        """Test TabState initialization."""
        tab = TabState()
        
        assert tab.id is not None
        assert tab.path == Path.home()
        assert tab.filter_query == ""
        assert tab.selected_node is None
        assert tab.scroll_position == 0
        assert not tab.is_locked
        assert tab.title is None

    def test_tab_state_with_path(self) -> None:
        """Test TabState with custom path."""
        test_path = Path("/tmp/test")
        tab = TabState(path=test_path)
        
        assert tab.path == test_path

    def test_tab_state_with_string_path(self) -> None:
        """Test TabState with string path."""
        tab = TabState(path="/tmp/test")
        
        assert tab.path == Path("/tmp/test")

    def test_display_title_home(self) -> None:
        """Test display title for home directory."""
        tab = TabState(path=Path.home())
        assert tab.display_title == "Home"

    def test_display_title_named_directory(self) -> None:
        """Test display title for named directory."""
        tab = TabState(path=Path("/tmp/testdir"))
        assert tab.display_title == "testdir"

    def test_display_title_root(self) -> None:
        """Test display title for root directory."""
        tab = TabState(path=Path("/"))
        assert tab.display_title == "/"

    def test_display_title_custom_title(self) -> None:
        """Test display title with custom title."""
        tab = TabState(title="Custom Title")
        assert tab.display_title == "Custom Title"

    def test_to_dict(self) -> None:
        """Test TabState serialization."""
        tab = TabState(path=Path("/tmp/test"), filter_query="*.py", is_locked=True)
        
        data = tab.to_dict()
        
        assert data["id"] == tab.id
        assert data["path"] == str(tab.path)
        assert data["filter_query"] == "*.py"
        assert data["is_locked"] is True

    def test_from_dict(self) -> None:
        """Test TabState deserialization."""
        data = {
            "id": "test-id",
            "path": "/tmp/test",
            "filter_query": "*.py",
            "is_locked": True,
        }
        
        tab = TabState.from_dict(data)
        
        assert tab.id == "test-id"
        assert tab.path == Path("/tmp/test")
        assert tab.filter_query == "*.py"
        assert tab.is_locked is True


class TestTabManager:
    """Test cases for TabManager class."""

    def test_tab_manager_initialization(self) -> None:
        """Test TabManager initialization."""
        manager = TabManager()
        
        assert len(manager) == 1
        assert manager.active_tab_index == 0
        assert manager.max_tabs == 10
        assert manager.active_tab.path == Path.home()

    def test_tab_manager_custom_max_tabs(self) -> None:
        """Test TabManager with custom max tabs."""
        manager = TabManager(max_tabs=5)
        
        assert manager.max_tabs == 5

    def test_add_tab(self) -> None:
        """Test adding a new tab."""
        manager = TabManager()
        initial_count = len(manager)
        
        new_tab = manager.add_tab(Path("/tmp"))
        
        assert len(manager) == initial_count + 1
        assert manager.active_tab_index == initial_count
        assert new_tab.path == Path("/tmp")

    def test_add_tab_default_path(self) -> None:
        """Test adding tab with default path."""
        manager = TabManager()
        manager.active_tab.path = Path("/tmp")
        
        new_tab = manager.add_tab()
        
        assert new_tab.path == Path("/tmp")

    def test_add_tab_max_tabs(self) -> None:
        """Test adding tab when at maximum."""
        manager = TabManager(max_tabs=2)
        
        # Add tabs to reach maximum
        manager.add_tab()
        
        # Should raise error when trying to add another
        with pytest.raises(RuntimeError, match="Maximum number of tabs"):
            manager.add_tab()

    def test_close_tab(self) -> None:
        """Test closing a tab."""
        manager = TabManager()
        initial_tab_id = manager.active_tab.id
        
        # Add a new tab
        new_tab = manager.add_tab()
        assert len(manager) == 2
        
        # Close the new tab
        success = manager.close_tab(new_tab.id)
        
        assert success is True
        assert len(manager) == 1
        assert manager.active_tab.id == initial_tab_id

    def test_close_tab_not_found(self) -> None:
        """Test closing a tab that doesn't exist."""
        manager = TabManager()
        
        success = manager.close_tab("non-existent-id")
        
        assert success is False

    def test_close_last_tab(self) -> None:
        """Test closing the last tab."""
        manager = TabManager()
        
        with pytest.raises(RuntimeError, match="Cannot close the last tab"):
            manager.close_tab(manager.active_tab.id)

    def test_close_active_tab(self) -> None:
        """Test closing the active tab."""
        manager = TabManager()
        initial_tab_id = manager.active_tab.id
        
        # Add a new tab
        manager.add_tab()
        assert len(manager) == 2
        
        # Close active tab (should close the new tab and switch back)
        success = manager.close_active_tab()
        
        assert success is True
        assert len(manager) == 1
        assert manager.active_tab.id == initial_tab_id

    def test_switch_to_tab(self) -> None:
        """Test switching to tab by index."""
        manager = TabManager()
        initial_tab = manager.active_tab
        
        # Add new tab
        new_tab = manager.add_tab()
        assert manager.active_tab.id == new_tab.id
        
        # Switch back to first tab
        success = manager.switch_to_tab(0)
        
        assert success is True
        assert manager.active_tab.id == initial_tab.id

    def test_switch_to_tab_invalid_index(self) -> None:
        """Test switching to invalid tab index."""
        manager = TabManager()
        
        success = manager.switch_to_tab(99)
        
        assert success is False

    def test_switch_to_tab_by_id(self) -> None:
        """Test switching to tab by ID."""
        manager = TabManager()
        initial_tab = manager.active_tab
        
        # Add new tab
        new_tab = manager.add_tab()
        assert manager.active_tab.id == new_tab.id
        
        # Switch back by ID
        success = manager.switch_to_tab_by_id(initial_tab.id)
        
        assert success is True
        assert manager.active_tab.id == initial_tab.id

    def test_switch_to_tab_by_id_not_found(self) -> None:
        """Test switching to tab by non-existent ID."""
        manager = TabManager()
        
        success = manager.switch_to_tab_by_id("non-existent-id")
        
        assert success is False

    def test_next_tab(self) -> None:
        """Test switching to next tab."""
        manager = TabManager()
        initial_tab = manager.active_tab
        
        # Add new tab
        new_tab = manager.add_tab()
        assert manager.active_tab.id == new_tab.id
        
        # Next tab should wrap to first
        success = manager.next_tab()
        
        assert success is True
        assert manager.active_tab.id == initial_tab.id

    def test_next_tab_single(self) -> None:
        """Test next tab with only one tab."""
        manager = TabManager()
        
        success = manager.next_tab()
        
        assert success is False

    def test_previous_tab(self) -> None:
        """Test switching to previous tab."""
        manager = TabManager()
        initial_tab = manager.active_tab
        
        # Add new tab
        new_tab = manager.add_tab()
        assert manager.active_tab.id == new_tab.id
        
        # Previous tab should wrap to last
        success = manager.previous_tab()
        
        assert success is True
        assert manager.active_tab.id == initial_tab.id

    def test_previous_tab_single(self) -> None:
        """Test previous tab with only one tab."""
        manager = TabManager()
        
        success = manager.previous_tab()
        
        assert success is False

    def test_get_tab_by_index(self) -> None:
        """Test getting tab by index."""
        manager = TabManager()
        
        tab = manager.get_tab_by_index(0)
        
        assert tab is not None
        assert tab.id == manager.active_tab.id

    def test_get_tab_by_index_invalid(self) -> None:
        """Test getting tab by invalid index."""
        manager = TabManager()
        
        tab = manager.get_tab_by_index(99)
        
        assert tab is None

    def test_get_tab_by_id(self) -> None:
        """Test getting tab by ID."""
        manager = TabManager()
        
        tab = manager.get_tab_by_id(manager.active_tab.id)
        
        assert tab is not None
        assert tab.id == manager.active_tab.id

    def test_get_tab_by_id_not_found(self) -> None:
        """Test getting tab by non-existent ID."""
        manager = TabManager()
        
        tab = manager.get_tab_by_id("non-existent-id")
        
        assert tab is None

    def test_update_active_tab(self) -> None:
        """Test updating active tab state."""
        manager = TabManager()
        
        manager.update_active_tab(
            filter_query="*.py",
            selected_node="test.py",
            scroll_position=10
        )
        
        active_tab = manager.active_tab
        assert active_tab.filter_query == "*.py"
        assert active_tab.selected_node == "test.py"
        assert active_tab.scroll_position == 10

    def test_duplicate_active_tab(self) -> None:
        """Test duplicating the active tab."""
        manager = TabManager()
        manager.active_tab.path = Path("/tmp")
        manager.active_tab.filter_query = "*.py"
        
        new_tab = manager.duplicate_active_tab()
        
        assert len(manager) == 2
        assert manager.active_tab.id == new_tab.id
        assert new_tab.path == Path("/tmp")
        assert new_tab.filter_query == "*.py"
        assert new_tab.title == "tmp (copy)"

    def test_duplicate_active_tab_max_tabs(self) -> None:
        """Test duplicating tab when at maximum."""
        manager = TabManager(max_tabs=2)
        
        # Add tabs to reach maximum
        manager.add_tab()
        
        with pytest.raises(RuntimeError, match="Maximum number of tabs"):
            manager.duplicate_active_tab()

    def test_lock_active_tab(self) -> None:
        """Test locking the active tab."""
        manager = TabManager()
        
        manager.lock_active_tab()
        assert manager.active_tab.is_locked is True

    def test_unlock_active_tab(self) -> None:
        """Test unlocking the active tab."""
        manager = TabManager()
        manager.lock_active_tab()
        
        manager.unlock_active_tab()
        assert manager.active_tab.is_locked is False

    def test_toggle_active_tab_lock(self) -> None:
        """Test toggling the active tab lock."""
        manager = TabManager()
        
        # Initially unlocked
        assert manager.active_tab.is_locked is False
        
        # Toggle to locked
        manager.toggle_active_tab_lock()
        assert manager.active_tab.is_locked is True
        
        # Toggle to unlocked
        manager.toggle_active_tab_lock()
        assert manager.active_tab.is_locked is False

    def test_to_dict_list(self) -> None:
        """Test converting tabs to dictionary list."""
        manager = TabManager()
        manager.active_tab.path = Path("/tmp")
        
        data = manager.to_dict_list()
        
        assert len(data) == 1
        assert data[0]["path"] == "/tmp"

    def test_from_dict_list(self) -> None:
        """Test loading tabs from dictionary list."""
        data = [
            {
                "id": "test-id-1",
                "path": "/tmp/test1",
                "filter_query": "*.py",
                "is_locked": False,
            },
            {
                "id": "test-id-2",
                "path": "/tmp/test2",
                "filter_query": "*.txt",
                "is_locked": True,
            }
        ]
        
        manager = TabManager()
        manager.from_dict_list(data)
        
        assert len(manager) == 2
        assert manager.active_tab_index == 0
        assert manager.tabs[0].path == Path("/tmp/test1")
        assert manager.tabs[1].path == Path("/tmp/test2")
        assert manager.tabs[1].is_locked is True

    def test_from_dict_list_empty(self) -> None:
        """Test loading from empty dictionary list."""
        manager = TabManager()
        manager.from_dict_list([])
        
        # Should create initial tab
        assert len(manager) == 1
        assert manager.active_tab_index == 0

    def test_iteration(self) -> None:
        """Test iterating over tabs."""
        manager = TabManager()
        manager.add_tab()
        manager.add_tab()
        
        tab_ids = [tab.id for tab in manager]
        
        assert len(tab_ids) == 3
        assert manager.tabs[0].id in tab_ids
        assert manager.tabs[1].id in tab_ids
        assert manager.tabs[2].id in tab_ids

    def test_repr(self) -> None:
        """Test string representation."""
        manager = TabManager()
        
        repr_str = repr(manager)
        
        assert "TabManager" in repr_str
        assert "tabs=1" in repr_str
        assert "active=0" in repr_str
