#!/usr/bin/env python3
"""Debug script to test layout rendering."""
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Static


class DebugApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #main {
        layout: horizontal;
        height: 1fr;
    }
    
    #left {
        width: 1fr;
        background: blue;
        border: thick white;
    }
    
    #right {
        width: 1fr;
        background: red;
        border: thick white;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal(id="main"):
            with Container(id="left"):
                yield Label("LEFT PANE")
                yield Static("This should be on the left side")

            with Container(id="right"):
                yield Label("RIGHT PANE")
                yield Static("This should be on the right side")

if __name__ == "__main__":
    app = DebugApp()
    app.run()
