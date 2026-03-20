# Contributing Guide (Non-Kiro Agents)

## Setup
- Create a virtual environment: `python3 -m venv venv`
- Activate it: `source venv/bin/activate`
- Install dependencies (canonical): `pip install -e .[dev]`
- Optional pinned workflow: `pip install -r requirements.txt`

## Run
- Preferred: `python main.py`
- Alternate: `tui-fm` or `./run.sh`

## Tests
- Add automated tests for new behavior and run them with: `python -m pytest tests/ -q`

## Change Guidelines
- Keep changes small and targeted.
- Do not introduce new dependencies without approval.
- Favor readable, defensive error handling.
- Avoid blocking filesystem work on the UI thread when possible.
- Preserve the dual-pane layout and help/shortcut model.

## Feature Priorities
- Fix layout issues first.
- Improve preview readability and add syntax highlighting.
- Implement file operations with safe confirmation flows.
- Add keyboard shortcuts for core operations.
- Add status bar and search features after core ops are stable.

## What Not To Do
- Do not touch files outside the repo directory.
- Do not auto-generate large refactors without explicit approval.
- Do not add network calls or external services.
