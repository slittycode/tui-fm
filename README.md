# TUI File Manager (TUI FM)

A modern terminal-based file manager built with Python and Textual.

[![CI](https://github.com/user/tui-fm/actions/workflows/ci.yml/badge.svg)](https://github.com/user/tui-fm/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-71%20passing-brightgreen.svg)](tests/)
[![Status](https://img.shields.io/badge/status-beta%20ready-green.svg)](AUDIT_REPORT.md)

## Features

- 🎨 Beautiful dual-pane interface
- 📁 Directory tree navigation
- 👁️ File preview pane with syntax highlighting for 50+ languages
- 🛠️ File operations: copy, move, rename, and delete
- 🔎 Search/filter by filename
- 🔖 Bookmarks for quick directory access
- 📁 Git status indicators (M, A, D, ?)
- ⚙️ Configuration UI with validation
- � Multiple tabs with keyboard navigation
- �📊 Status bar with file info and last action
- ⌨️ Keyboard-driven workflow
- 🎨 8 built-in color themes with dynamic switching
- 🖼️ File icons using Nerd Fonts (50+ file types)
- 🖱️ Mouse support for intuitive navigation
- 🧪 Comprehensive test suite (245+ tests)

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/user/tui-fm.git
cd tui-fm

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package (optional)
pip install -e .
```

### From PyPI (Coming Soon)

```bash
pip install tui-fm
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

Or if installed via pip:
```bash
tui-fm
```

## Keyboard Shortcuts

### Navigation
| Key | Action |
|-----|--------|
| `↑/↓` | Navigate files |
| `←/→` | Collapse/expand folders |
| `Enter` | Select file |
| `Home/End` | Jump to top/bottom |
| `Page Up/Down` | Scroll faster |

### File Operations
| Key | Action |
|-----|--------|
| `c` | Copy selected file/folder |
| `m` | Move selected file/folder |
| `n` | Rename selected file/folder |
| `d` | Delete selected file/folder (double press) |

### Workflow
| Key | Action |
|-----|--------|
| `/` | Start search/filter |
| `f` | Clear active filter |
| `b` | Bookmark current directory |
| `B` | Browse bookmarks |
| `r` | Refresh |
| `h` or `?` | Toggle help |
| `q` | Quit |
| `Esc` | Cancel/clear selection |

## Configuration

Create `~/.tui_fm_config.json` to customize:

```json
{
  "default_path": "~/projects",
  "theme": "dark",
  "preview_size_limit": 1000000,
  "show_hidden_files": false,
  "ignored_patterns": [".git", "__pycache__", "node_modules"],
  "syntax_highlighting": true,
  "confirm_delete": true
}
```

## Bookmarks

Bookmarks are stored in `~/.tui_fm_bookmarks.json`.

- Press `b` to bookmark the current directory
- Press `B` to view all bookmarks
- Bookmarks persist across sessions

## Supported File Types

Syntax highlighting for: Python, JavaScript, TypeScript, JSON, Markdown, YAML, TOML, HTML, CSS, SQL, Go, Rust, Java, C/C++, Shell, and more.

## Testing

```bash
# Run all tests (71 tests)
PYTHONPATH=. pytest tests/ -v --override-ini="addopts="

# Run with coverage (requires pytest-cov)
PYTHONPATH=. pytest tests/ -v --cov=filesystem_service --cov=filterable_tree

# View HTML coverage report
open htmlcov/index.html
```

## Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run linting
ruff check .
mypy app.py

# Run tests
pytest
```

## Project Structure

```
tui-fm/
├── app.py                 # Main application UI logic
├── main.py                # Entry point
├── filesystem_service.py  # File operations
├── filterable_tree.py     # Custom directory tree widget
├── config_manager.py      # Configuration management
├── bookmarks_manager.py   # Bookmarks management
├── tests/                 # Test suite
├── requirements.txt       # Dependencies
├── pyproject.toml         # Package configuration
└── README.md              # This file
```

## Status & Roadmap

**Current Status:** ✅ Beta-ready (see [AUDIT_REPORT.md](AUDIT_REPORT.md))
- 71 tests passing (100%)
- 95% code coverage
- Clean linting
- No critical bugs

See [TODO.md](TODO.md) for the complete roadmap.

### Completed
- ✅ Dual-pane responsive layout
- ✅ File preview with syntax highlighting
- ✅ File operations (copy, move, rename, delete)
- ✅ Search/filter functionality
- ✅ Bookmarks system
- ✅ Configuration system
- ✅ Comprehensive testing (70+ tests)
- ✅ CI/CD pipeline

### In Progress
- 🚧 Git status indicators
- 🚧 Enhanced preview (markdown render, hex dump)

### Planned
- Multiple tabs
- Image preview
- Archive browsing
- Disk usage visualization
- Plugin system

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with [Textual](https://textual.textualize.io/)
- Syntax highlighting by [Rich](https://rich.readthedocs.io/)
