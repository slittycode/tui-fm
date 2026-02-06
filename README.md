# Rich TUI File Manager

A modern terminal-based file manager built with Python and Textual.

## Features

- 🎨 Beautiful dual-pane interface
- 📁 Directory tree navigation
- 👁️ File preview pane with syntax highlighting for common code files
- 🛠️ File operations: copy, move, rename, and delete
- 🔎 Search/filter by filename
- 📊 Status bar with file info and last action
- ⌨️ Keyboard-driven workflow

## Installation

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Make sure venv is activated
source venv/bin/activate

# Run the app
python main.py
```

Or use the launch script:
```bash
./run.sh
```

## Keyboard Shortcuts

- `↑/↓` - Navigate files
- `←/→` - Collapse/expand folders
- `Enter` - Select file
- `/` - Start search/filter
- `f` - Clear active filter
- `c` - Copy selected file/folder
- `m` - Move selected file/folder
- `n` - Rename selected file/folder
- `d` - Delete selected file/folder (double press)
- `q` - Quit
- `r` - Refresh
- `h` - Help

## Roadmap

- [x] File operations (copy, move, delete, rename)
- [x] Search and filter (MVP)
- [x] Syntax highlighting for code
- [ ] Image preview support
- [ ] Bookmarks/favorites
- [ ] Multiple tabs
- [ ] Git status indicators
- [ ] Archive browsing
