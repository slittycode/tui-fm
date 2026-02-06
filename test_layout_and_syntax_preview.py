import unittest
from pathlib import Path

from rich.console import Group
from rich.syntax import Syntax

from app import FileManagerApp


def contains_syntax(renderable) -> bool:
    if isinstance(renderable, Syntax):
        return True
    if isinstance(renderable, Group):
        return any(contains_syntax(item) for item in renderable.renderables)
    return False


class TestLayoutAndSyntaxPreview(unittest.TestCase):
    def test_should_stack_layout_for_narrow_width(self):
        self.assertTrue(FileManagerApp._should_stack_layout(99))

    def test_should_not_stack_layout_for_wide_width(self):
        self.assertFalse(FileManagerApp._should_stack_layout(100))

    def test_code_preview_uses_syntax_highlighting(self):
        app = FileManagerApp()
        sample_path = Path("example.py")
        renderable = app._build_file_content_renderable(
            sample_path,
            "def add(a, b):\n    return a + b\n",
            is_truncated=False,
        )

        self.assertTrue(
            contains_syntax(renderable),
            "Expected a Syntax renderable for Python source previews",
        )


if __name__ == "__main__":
    unittest.main()
