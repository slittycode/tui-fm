# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Configuration system with `ConfigManager` for user preferences
- Bookmarks system with `BookmarksManager` for quick directory access
- Comprehensive test suite with 70+ tests
- pytest configuration with coverage reporting
- ruff linting and mypy type checking configuration
- Pre-commit hooks for code quality
- GitHub Actions CI workflow for automated testing
- Type hints throughout the codebase
- Python packaging support via `pyproject.toml`
- TUI FM branding and naming
- Git status indicators in file tree (M, A, D, ?)
- Git service for file status detection with caching
- Git status legend in help screen
- Configuration UI with modal screen (, key)
- Enhanced ConfigManager with validation and auto-save
- Settings for theme, preview limits, ignored patterns, and more
- Multiple tabs with full keyboard navigation
- Tab management (create, close, switch, duplicate, lock)
- Tab persistence and state management
- Up to 10 configurable tabs with intuitive shortcuts
- Color themes with 8 built-in themes
- Dynamic CSS generation from theme definitions
- Theme switching with keyboard shortcuts
- Enhanced configuration UI with theme selection
- File icons using Nerd Fonts with 50+ file type mappings
- Comprehensive icon support for programming languages, documents, media files
- Integrated icon system with Git status indicators
- Mouse support for intuitive file navigation and selection
- Click, double-click, Ctrl+click, and Shift+click interactions
- Multi-selection support with visual feedback
- Enhanced user experience with both keyboard and mouse interactions

### Changed
- Enhanced error handling in filesystem operations
- Improved documentation with docstrings
- Updated requirements.txt with development dependencies

### Fixed
- Better handling of corrupted configuration files
- Improved edge case handling in filter operations

## [0.1.0] - 2025-02-28

### Added
- Dual-pane responsive layout (horizontal/vertical stacking)
- Directory tree with expand/collapse navigation
- File preview with syntax highlighting for 20+ languages
- File operations: copy, move, rename, delete
- Search/filter by filename with recursive directory matching
- Status bar with file info and operation feedback
- Keyboard shortcuts for all operations
- Help screen with comprehensive shortcut listing
- Async preview loading to prevent UI blocking
- Safe delete confirmation flow (double-press)
- Binary file detection
- Large file handling (>1MB preview limit)
- Permission denied handling
- Responsive layout for narrow terminals

### Technical
- Built with Python Textual framework
- Rich library for syntax highlighting
- pathlib for cross-platform path handling
- shutil for file operations
- asyncio workers for non-blocking UI

### Known Issues
- Dual-pane layout needs verification on all terminal sizes
- Limited testing on Linux and Windows

---

## Version History

- **0.1.0** - Initial MVP release with core features
- **Unreleased** - Foundation improvements, testing, configuration, bookmarks
