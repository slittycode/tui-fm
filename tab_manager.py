"""Tab management for the File Manager."""
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class TabState:
    """State for a single directory tab."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    path: Path = field(default_factory=lambda: Path.home())
    filter_query: str = ""
    selected_node: Optional[str] = None
    scroll_position: int = 0
    is_locked: bool = False
    title: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if isinstance(self.path, str):
            self.path = Path(self.path)
    
    @property
    def display_title(self) -> str:
        """Get the display title for the tab."""
        if self.title:
            return self.title
        
        if self.path == Path.home():
            return "Home"
        elif self.path.name:
            return self.path.name
        else:
            return str(self.path)
    
    def to_dict(self) -> dict:
        """Convert tab state to dictionary for serialization."""
        return {
            "id": self.id,
            "path": str(self.path),
            "filter_query": self.filter_query,
            "selected_node": self.selected_node,
            "scroll_position": self.scroll_position,
            "is_locked": self.is_locked,
            "title": self.title,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TabState":
        """Create tab state from dictionary."""
        return cls(
            id=data["id"],
            path=Path(data["path"]),
            filter_query=data.get("filter_query", ""),
            selected_node=data.get("selected_node"),
            scroll_position=data.get("scroll_position", 0),
            is_locked=data.get("is_locked", False),
            title=data.get("title"),
        )


class TabManager:
    """Manage multiple directory tabs."""
    
    def __init__(self, max_tabs: int = 10) -> None:
        """Initialize the tab manager.
        
        Args:
            max_tabs: Maximum number of tabs allowed.
        """
        self.tabs: list[TabState] = []
        self.active_tab_index: int = 0
        self.max_tabs = max_tabs
        
        # Create initial tab
        self._create_initial_tab()
    
    def _create_initial_tab(self) -> None:
        """Create the initial tab."""
        initial_tab = TabState(path=Path.home())
        self.tabs.append(initial_tab)
        self.active_tab_index = 0
    
    @property
    def active_tab(self) -> TabState:
        """Get the currently active tab."""
        if not self.tabs or self.active_tab_index >= len(self.tabs):
            raise RuntimeError("No active tab available")
        return self.tabs[self.active_tab_index]
    
    def add_tab(self, path: Optional[Path] = None) -> TabState:
        """Add a new tab.
        
        Args:
            path: Path for the new tab. Defaults to current tab's path.
            
        Returns:
            The created tab state.
            
        Raises:
            RuntimeError: If maximum number of tabs reached.
        """
        if len(self.tabs) >= self.max_tabs:
            raise RuntimeError(f"Maximum number of tabs ({self.max_tabs}) reached")
        
        if path is None:
            path = self.active_tab.path
        
        new_tab = TabState(path=path)
        self.tabs.append(new_tab)
        self.active_tab_index = len(self.tabs) - 1
        
        return new_tab
    
    def close_tab(self, tab_id: str) -> bool:
        """Close a tab by ID.
        
        Args:
            tab_id: ID of the tab to close.
            
        Returns:
            True if tab was closed, False if not found.
            
        Raises:
            RuntimeError: If trying to close the last tab.
        """
        # Find the tab to close
        tab_index = None
        for i, tab in enumerate(self.tabs):
            if tab.id == tab_id:
                tab_index = i
                break
        
        if tab_index is None:
            return False
        
        # Check if this would close the last tab
        if len(self.tabs) <= 1:
            raise RuntimeError("Cannot close the last tab")
        
        # Remove the tab
        del self.tabs[tab_index]
        
        # Adjust active tab index if necessary
        if self.active_tab_index >= len(self.tabs):
            self.active_tab_index = len(self.tabs) - 1
        elif self.active_tab_index > tab_index:
            self.active_tab_index -= 1
        
        return True
    
    def close_active_tab(self) -> bool:
        """Close the currently active tab.
        
        Returns:
            True if tab was closed, False if not.
        """
        return self.close_tab(self.active_tab.id)
    
    def switch_to_tab(self, index: int) -> bool:
        """Switch to tab by index.
        
        Args:
            index: Index of the tab to switch to.
            
        Returns:
            True if switch was successful, False if index invalid.
        """
        if 0 <= index < len(self.tabs):
            self.active_tab_index = index
            return True
        return False
    
    def switch_to_tab_by_id(self, tab_id: str) -> bool:
        """Switch to tab by ID.
        
        Args:
            tab_id: ID of the tab to switch to.
            
        Returns:
            True if switch was successful, False if not found.
        """
        for i, tab in enumerate(self.tabs):
            if tab.id == tab_id:
                self.active_tab_index = i
                return True
        return False
    
    def next_tab(self) -> bool:
        """Switch to the next tab.
        
        Returns:
            True if switch was successful.
        """
        if len(self.tabs) <= 1:
            return False
        
        self.active_tab_index = (self.active_tab_index + 1) % len(self.tabs)
        return True
    
    def previous_tab(self) -> bool:
        """Switch to the previous tab.
        
        Args:
            True if switch was successful.
        """
        if len(self.tabs) <= 1:
            return False
        
        self.active_tab_index = (self.active_tab_index - 1) % len(self.tabs)
        return True
    
    def get_tab_by_index(self, index: int) -> Optional[TabState]:
        """Get tab by index.
        
        Args:
            index: Index of the tab.
            
        Returns:
            Tab state if found, None otherwise.
        """
        if 0 <= index < len(self.tabs):
            return self.tabs[index]
        return None
    
    def get_tab_by_id(self, tab_id: str) -> Optional[TabState]:
        """Get tab by ID.
        
        Args:
            tab_id: ID of the tab.
            
        Returns:
            Tab state if found, None otherwise.
        """
        for tab in self.tabs:
            if tab.id == tab_id:
                return tab
        return None
    
    def update_active_tab(self, **kwargs) -> None:
        """Update the active tab's state.
        
        Args:
            **kwargs: Tab state fields to update.
        """
        for key, value in kwargs.items():
            if hasattr(self.active_tab, key):
                setattr(self.active_tab, key, value)
    
    def duplicate_active_tab(self) -> TabState:
        """Duplicate the currently active tab.
        
        Returns:
            The newly created tab state.
        """
        if len(self.tabs) >= self.max_tabs:
            raise RuntimeError(f"Maximum number of tabs ({self.max_tabs}) reached")
        
        current_tab = self.active_tab
        new_tab = TabState(
            path=current_tab.path,
            filter_query=current_tab.filter_query,
            title=f"{current_tab.display_title} (copy)"
        )
        
        self.tabs.append(new_tab)
        self.active_tab_index = len(self.tabs) - 1
        
        return new_tab
    
    def lock_active_tab(self) -> None:
        """Lock the currently active tab to prevent accidental closure."""
        self.active_tab.is_locked = True
    
    def unlock_active_tab(self) -> None:
        """Unlock the currently active tab."""
        self.active_tab.is_locked = False
    
    def toggle_active_tab_lock(self) -> None:
        """Toggle the lock state of the currently active tab."""
        self.active_tab.is_locked = not self.active_tab.is_locked
    
    def to_dict_list(self) -> list[dict]:
        """Convert all tabs to a list of dictionaries."""
        return [tab.to_dict() for tab in self.tabs]
    
    def from_dict_list(self, data: list[dict]) -> None:
        """Load tabs from a list of dictionaries.
        
        Args:
            data: List of tab dictionaries.
        """
        self.tabs = [TabState.from_dict(item) for item in data]
        if self.tabs:
            self.active_tab_index = 0
        else:
            self._create_initial_tab()
    
    def __len__(self) -> int:
        """Get the number of tabs."""
        return len(self.tabs)
    
    def __iter__(self):
        """Iterate over tabs."""
        return iter(self.tabs)
    
    def __repr__(self) -> str:
        return f"TabManager(tabs={len(self.tabs)}, active={self.active_tab_index})"
