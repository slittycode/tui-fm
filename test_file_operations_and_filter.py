import shutil
import tempfile
import unittest
from pathlib import Path

from app import FileManagerApp


class FileOpsAndFilterTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp(prefix="fm-test-"))
        self.app = FileManagerApp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_copy_path_copies_file_contents(self):
        source = self.tmpdir / "source.txt"
        source.write_text("hello", encoding="utf-8")
        destination = self.tmpdir / "copy.txt"

        self.app._copy_path(source, destination)

        self.assertTrue(destination.exists())
        self.assertEqual(destination.read_text(encoding="utf-8"), "hello")

    def test_move_path_moves_file(self):
        source = self.tmpdir / "move_me.txt"
        source.write_text("move", encoding="utf-8")
        destination = self.tmpdir / "moved.txt"

        self.app._move_path(source, destination)

        self.assertFalse(source.exists())
        self.assertTrue(destination.exists())

    def test_rename_path_keeps_parent_directory(self):
        source = self.tmpdir / "old_name.txt"
        source.write_text("rename", encoding="utf-8")

        renamed = self.app._rename_path(source, "new_name.txt")

        self.assertEqual(renamed, self.tmpdir / "new_name.txt")
        self.assertFalse(source.exists())
        self.assertTrue(renamed.exists())

    def test_delete_path_removes_directory_tree(self):
        target_dir = self.tmpdir / "to_delete"
        target_dir.mkdir()
        (target_dir / "nested.txt").write_text("bye", encoding="utf-8")

        self.app._delete_path(target_dir)

        self.assertFalse(target_dir.exists())

    def test_apply_name_filter_is_case_insensitive(self):
        items = [
            Path("alpha.txt"),
            Path("BETA.py"),
            Path("alpaca.md"),
        ]

        filtered = self.app._apply_name_filter(items, "alp")

        self.assertEqual(filtered, [Path("alpha.txt"), Path("alpaca.md")])

    def test_build_file_status_includes_filter_when_active(self):
        self.app.filter_query = "todo"

        status = self.app._build_file_status(Path("/tmp/demo.txt"), "1.2 KB")

        self.assertIn("Selected: /tmp/demo.txt (1.2 KB)", status)
        self.assertIn("Filter: todo", status)


if __name__ == "__main__":
    unittest.main()
