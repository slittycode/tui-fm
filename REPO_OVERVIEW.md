# Repo Overview

## Summary
A Python Textual-based TUI file manager with a dual-pane layout. The left pane provides a directory tree. The right pane previews file or directory contents. The project is in an early MVP stage with a roadmap in `TODO.md`.

## Key Files
- `app.py`: Main UI and behavior for navigation, preview, and help.
- `main.py`: Entry point that runs the app.
- `debug_layout.py`: Standalone layout test for left/right pane structure.
- `pyproject.toml`: Canonical project metadata and dependencies.
- `requirements.txt`: Optional pinned dependency workflow.
- `run.sh`: Convenience script to run the app with a venv.
- `README.md`: User-facing description.
- `TODO.md`: Roadmap and prioritization.

## Behavior Snapshot
- Dual-pane layout with a directory tree on the left and preview on the right.
- Preview supports text files up to 1MB.
- Directory preview summarizes contents.
- Help screen lists shortcuts.

## Current Gaps
- Layout issues still noted in `TODO.md`.
- No file operations yet.
- Limited error handling around filesystem edge cases.
- UI can block on slow filesystem operations.
- Tests are minimal.

## Desired Evolution
- Fix layout and usability first.
- Add richer previews (syntax highlighting).
- Add file ops with safe confirmations.
- Add status info, search, bookmarks, and tabs.

## Guardrails For Agents
- Operate only within the repo folder.
- Do not add dependencies or external services without approval.
- Keep changes minimal and aligned to the roadmap.
