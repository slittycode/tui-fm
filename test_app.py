#!/usr/bin/env python3
"""Quick test to verify the app loads without errors."""
import sys

from app import FileManagerApp

try:
    app = FileManagerApp()
    print("✓ App initialized successfully")
    print(f"✓ Starting path: {app.current_path}")
    print(f"✓ Bindings: {len(app.BINDINGS)} configured")
    print("\nApp structure looks good! Run 'python main.py' to launch.")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
