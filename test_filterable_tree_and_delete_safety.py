import shutil
import tempfile
import unittest
from pathlib import Path

from app import FileManagerApp
from filterable_tree import FilterableDirectoryTree


class DeleteSafetyApp(FileManagerApp):
    def __init__(self):
        self.current_path = Path("/tmp")
        self.selected_file = None
        self.help_visible = False
        self.filter_query = ""
        self.command_mode = None
        self.delete_confirmation_path = Path("/tmp/armed")
        self.last_action = ""
        self.status_messages = []
        self._tree = FakeTree()

    def _set_status(self, message: str) -> None:
        self.status_messages.append(message)

    def query_one(self, selector, *args, **kwargs):
        if selector == "#tree":
            return self._tree
        raise KeyError(selector)


class FakeTree:
    def __init__(self):
        self.query = ""
        self.reload_count = 0

    def set_filter_query(self, query: str) -> bool:
        changed = query != self.query
        self.query = query
        return changed

    def reload(self):
        self.reload_count += 1


class FilterTreeAndDeleteSafetyTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="fm-filter-tree-"))

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_filter_tree_keeps_matching_paths_and_relevant_dirs(self):
        root = self.tmpdir
        (root / "keep-me.txt").write_text("x", encoding="utf-8")
        (root / "drop-me.txt").write_text("x", encoding="utf-8")

        nested = root / "nested"
        nested.mkdir()
        (nested / "target.log").write_text("x", encoding="utf-8")

        other_dir = root / "other"
        other_dir.mkdir()
        (other_dir / "plain.log").write_text("x", encoding="utf-8")

        tree = FilterableDirectoryTree.__new__(FilterableDirectoryTree)
        tree.filter_query = "target"

        filtered = list(tree.filter_paths([root / "keep-me.txt", nested, other_dir, root / "drop-me.txt"]))

        self.assertIn(nested, filtered)
        self.assertNotIn(other_dir, filtered)
        self.assertNotIn(root / "keep-me.txt", filtered)
        self.assertNotIn(root / "drop-me.txt", filtered)

    def test_non_delete_action_clears_armed_delete_state(self):
        app = DeleteSafetyApp()
        self.assertIsNotNone(app.delete_confirmation_path)

        app._apply_filter_query("abc")

        self.assertIsNone(app.delete_confirmation_path)
        self.assertEqual(app._tree.query, "abc")
        self.assertEqual(app._tree.reload_count, 1)


if __name__ == "__main__":
    unittest.main()
