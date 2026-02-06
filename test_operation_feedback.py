import unittest
from pathlib import Path

from app import FileManagerApp


class FakeWidget:
    def __init__(self):
        self.text = None

    def update(self, value):
        self.text = value


class FeedbackTestApp(FileManagerApp):
    def __init__(self):
        self.current_path = Path("/tmp")
        self.selected_file = None
        self.help_visible = False
        self.filter_query = ""
        self.command_mode = None
        self.delete_confirmation_path = None
        self.last_action = ""
        self._preview_request_id = 0
        self._widgets = {
            "#preview-content": FakeWidget(),
            "#preview-header": FakeWidget(),
            "#preview-footer": FakeWidget(),
            "#tree-footer": FakeWidget(),
            "#status-bar": FakeWidget(),
        }

    def query_one(self, selector, *args, **kwargs):
        return self._widgets[selector]


class OperationFeedbackTest(unittest.TestCase):
    def test_success_feedback_updates_preview_pane(self):
        app = FeedbackTestApp()

        app._show_operation_result(
            operation="Copy",
            success=True,
            details={
                "Source": "/tmp/a.txt",
                "Destination": "/tmp/b.txt",
            },
        )

        self.assertEqual(app._widgets["#preview-header"].text, "✅ Copy Complete")
        self.assertIn("Copy succeeded.", app._widgets["#preview-content"].text)
        self.assertIn("Source:", app._widgets["#preview-content"].text)
        self.assertIn("Destination:", app._widgets["#preview-content"].text)

    def test_failure_feedback_updates_preview_pane(self):
        app = FeedbackTestApp()

        app._show_operation_result(
            operation="Rename",
            success=False,
            details={
                "Target": "/tmp/demo.txt",
                "Error": "Destination already exists",
            },
        )

        self.assertEqual(app._widgets["#preview-header"].text, "❌ Rename Failed")
        self.assertIn("Rename failed.", app._widgets["#preview-content"].text)
        self.assertIn("Destination already exists", app._widgets["#preview-content"].text)


if __name__ == "__main__":
    unittest.main()
