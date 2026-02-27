# Terminal File Manager (TUI FM) - Quick Start

## ✅ Installation Complete

Your terminal file manager is ready to use!

**Status:**
- ✅ Python virtual environment active
- ✅ Dependencies installed (Textual, Rich)
- ✅ Shell command configured: `tui-fm`
- ✅ 75% complete MVP - fully functional

---

## Launch

Simply type in any terminal:
```bash
tui-fm
```

This opens the dual-pane file manager in your current directory.

---

## Keyboard Shortcuts (The Essentials)

### Navigation
- `↑/↓` - Move up/down in file list
- `←/→` - Collapse/expand folders
- `Enter` - Select file (shows preview)

### File Operations
- `c` - Copy selected file/folder
- `m` - Move selected file/folder
- `n` - Rename selected file/folder
- `d` - Delete (press twice for safety)

### Workflow
- `/` - Start search/filter by filename
- `f` - Clear active filter
- `r` - Refresh directory view
- `h` - Toggle help overlay
- `q` - Quit

---

## Interface Layout

```
┌─────────────────────┬──────────────────────┐
│   Directory Tree    │   File Preview       │
│                     │                      │
│  📁 Projects        │  # README.md         │
│  ├─ 📄 app.py       │                      │
│  ├─ 📄 main.py      │  A terminal file     │
│  └─ 📁 tests        │  manager built with  │
│                     │  Textual...          │
└─────────────────────┴──────────────────────┘
│ Status: file.txt | Size: 1.2KB | Last: ... │
└──────────────────────────────────────────────┘
```

**Left pane:** Navigate your file system  
**Right pane:** Preview selected file with syntax highlighting  
**Bottom bar:** File info and operation feedback

---

## Real-World Usage Examples

### Organizing Downloads
```bash
cd ~/Downloads
tui-fm
# Navigate with arrows
# Press 'm' to move files to organized folders
# Press 'd' twice to delete unwanted files
```

### Quick Code Browsing
```bash
cd ~/code/projects
tui-fm
# Navigate directories on left
# Preview code files on right (syntax highlighted!)
# No need to open full editor just to peek
```

### Batch File Operations
```bash
cd ~/Documents
tui-fm
# Press '/' to filter files
# Type: ".pdf"  (shows only PDFs)
# Use 'c' to copy them to a backup folder
# Press 'f' to clear filter
```

### Project Cleanup
```bash
cd ~/code/old-project
tui-fm
# Visually inspect what's taking space
# Delete node_modules: navigate → 'd' twice
# Clean up temp files quickly
```

---

## 1-Week Trial Challenge

**Test if `tui-fm` fits your workflow:**

### This Week
- [ ] Launch `tui-fm` instead of `ls` at least 3 times
- [ ] Try file operations (copy, move, rename)
- [ ] Use preview pane to check file contents
- [ ] Test search/filter with '/'

### Evaluation Questions (Feb 13)
1. Did you reach for `tui-fm` naturally, or did it feel forced?
2. Was it faster than Finder + terminal combo?
3. Did syntax-highlighted preview save you time?
4. Do you miss features that would make it indispensable?

### Outcomes
- **Feels natural & fast** → Keep using, consider Phase 3 features (bookmarks, tabs)
- **Occasionally useful** → Keep for specific tasks (code browsing, cleanup)
- **Never reached for it** → Archive, stick with `ls` and Finder

---

## Features Already Working

✅ **Phase 1 & 2 Complete (MVP + Core):**
- Dual-pane responsive layout
- Directory tree with expand/collapse
- File preview with syntax highlighting (Python, JS, JSON, etc.)
- Copy, move, rename, delete operations
- Search/filter by filename
- Status bar with file info
- Keyboard shortcuts
- Operation feedback messages

⏳ **Not Yet Built (Phase 3 & 4):**
- Bookmarks/favorites
- Multiple tabs
- Color themes
- Git status indicators
- Image preview
- Archive browsing

---

## Tips for Success

### 1. Start Small
Don't try to replace your entire workflow day 1. Use it for:
- Quick directory browsing
- File cleanup tasks
- Code preview without opening editor

### 2. Muscle Memory
The shortcuts are Vim-inspired but simpler:
- Movement: arrows (everyone knows these)
- Operations: `c`opy, `m`ove, `n`ame, `d`elete (first letters)
- Search: `/` (like Vim and browser find)

### 3. When NOT to Use
- Complex file operations (bulk renames with regex) → use `rename` command
- Heavy text editing → use your editor
- File syncing/backup → use `rsync`, `rclone`

Kiro is for **visual navigation + quick operations**.

---

## Comparison to Alternatives

| Feature | tui-fm | Finder (GUI) | `ls` + bash | ranger | Midnight Commander |
|---------|------|--------------|-------------|--------|-------------------|
| Speed | Fast | Slow | Very Fast | Fast | Medium |
| Preview | Yes | Yes | No | Yes | Limited |
| Syntax highlighting | Yes | No | No | Yes | No |
| Modern UI | Yes | Yes | No | Dated | Dated |
| Mouse support | No | Yes | No | No | Yes |
| Learning curve | Low | None | None | Medium | High |

**tui-fm's sweet spot:** Terminal workflow + modern UX + code preview

---

## Troubleshooting

**"tui-fm command not found"**
```bash
# Restart terminal or:
source ~/.zshrc
```

**"Layout looks broken"**
- Resize your terminal window (minimum 80x24)
- Try full screen

**"Can't see file preview"**
- Navigate to a text file (not binary)
- Supported: .py, .js, .json, .md, .txt, .sh, .yml, .toml, etc.

**"Want to start in a specific directory"**
```bash
cd ~/target/path && tui-fm
# Or just:
(cd ~/target/path && tui-fm)
```

**"Accidentally deleted something"**
Good news: Deletes use OS trash/recycle bin (not permanent).
Check your Trash folder to recover.

---

## Development Status

**Current:** v0.1.0 - MVP with core features working
**Completion:** ~75% (Phases 1 & 2 done)
**Stability:** Stable for daily use
**Maintained:** Active personal project

This is **not** a work-in-progress prototype. It's a working tool ready for real use.

---

## Next Steps

### Today
1. Open a terminal
2. Type `tui-fm`
3. Play around for 5 minutes
4. Try copying a file (`c` key)

### This Week
Use it 3+ times for real tasks (not just testing).

### Feb 13 Decision
- **Keep using:** Add to permanent workflow, maybe request features
- **Occasional tool:** Keep around for specific tasks
- **Doesn't fit:** Archive, no regrets. `ls` is perfectly fine!

---

## Philosophy

Not every tool needs to be perfect or replace everything. Sometimes a tool is useful for **specific contexts**:

- Kiro for: browsing projects, quick file operations, code preview
- Finder for: drag-and-drop, image thumbnails, integrations
- CLI for: scripting, bulk operations, automation

**Use the right tool for the job.**

The goal isn't to force yourself to use tui-fm—it's to see if it **naturally** improves your workflow.

---

## Remember

After 1 week, be honest:
- Are you reaching for it without thinking?
- Or does it feel like homework?

The answer determines if it's worth keeping. Simple as that.

---

**TUI File Manager** - Fast, beautiful, terminal-based file management.

