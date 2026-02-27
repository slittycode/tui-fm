#!/usr/bin/env python3
"""
Rich TUI File Manager
A modern terminal-based file manager with dual-pane layout and preview.
"""
from app import FileManagerApp


def main():
    app = FileManagerApp()
    app.run()

if __name__ == "__main__":
    main()
