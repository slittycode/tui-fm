# Development Roadmap

## ✅ Phase 0: Foundation (DONE)
- [x] Testing infrastructure (pytest, coverage)
- [x] Type hints throughout codebase
- [x] Linting configuration (ruff, mypy)
- [x] Pre-commit hooks
- [x] Configuration system (ConfigManager)
- [x] Bookmarks system (BookmarksManager)
- [x] Python packaging (pyproject.toml)
- [x] CI/CD workflow (GitHub Actions)
- [x] CHANGELOG.md

## ✅ Phase 1: MVP (DONE)
- [x] Basic dual-pane layout
- [x] Directory tree navigation
- [x] File preview
- [x] Virtual environment setup
- [x] Launch script
- [x] Bookmarks integration (b/B shortcuts)

## 🚧 Phase 2: Core Features (NEXT)
- [x] Fix layout issues (responsive split/stack behavior)
- [x] Better file preview (syntax highlighting)
- [x] File operations (copy, move, delete, rename)
- [x] Keyboard shortcuts for operations
- [x] Status bar with file info
- [ ] Git status indicators
- [ ] Configuration UI

## 📋 Phase 3: Enhanced UX
- [x] Search/filter functionality (MVP)
- [x] Bookmarks/favorites
- [ ] Multiple tabs
- [ ] Color themes
- [ ] File icons (using Nerd Fonts)
- [ ] Mouse support

## 🎨 Phase 4: Advanced Features
- [ ] Image preview (terminal graphics)
- [ ] Git status indicators (deep integration)
- [ ] Archive browsing (zip/tar)
- [ ] Disk usage visualization
- [ ] Plugin system
- [ ] Fuzzy search (fzf-style)

## 🐛 Known Issues
- [ ] Dual pane layout needs verification on all terminals
- [ ] Need to test on Linux and Windows
- [ ] Large directory loading can still block UI

## 💡 Ideas
- Quick preview toggle (space bar)
- Vim-style navigation (hjkl)
- Fuzzy file finder (Ctrl+P)
- Bulk operations with visual mode
- SSH/remote filesystem support
