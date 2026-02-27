import unittest
from pathlib import Path

from app import FileManagerApp


class FakeWidget:
    def __init__(self):
        self.text = None

    def update(self, value):
        self.text = value


class TestableFileManagerApp(FileManagerApp):
    def __init__(self):
        self.current_path = Path("/tmp")
        self.selected_file = None
        self.help_visible = False
        self.filter_query = ""
        self.command_mode = None
        self.delete_confirmation_path = None
        self.last_action = ""
        self._widgets = {
            "#preview-content": FakeWidget(),
            "#preview-header": FakeWidget(),
            "#preview-footer": FakeWidget(),
            "#tree-footer": FakeWidget(),
            "#status-bar": FakeWidget(),
        }

    def query_one(self, selector, *args, **kwargs):
        return self._widgets[selector]


class HelpToggleTest(unittest.TestCase):
    def test_help_toggle_restores_preview_when_no_selection(self):
        app = TestableFileManagerApp()

        app.action_toggle_help()
        self.assertTrue(app.help_visible)
        self.assertIn("HELP & SHORTCUTS", app._widgets["#preview-content"].text)

        app.action_toggle_help()
        self.assertFalse(app.help_visible)
        self.assertEqual(app._widgets["#preview-content"].text, app._get_welcome_text())


if __name__ == "__main__":
    unittest.main()
