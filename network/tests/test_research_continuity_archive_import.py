"""Offline tests for safe, non-destructive Continuity archive intake."""
import tempfile
import unittest
import zipfile
from pathlib import Path

from research.continuity_archive_import import inventory, run, safe_path


class ArchiveImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.destination = self.root / "repo"
        self.destination.mkdir()

    def make(self, files):
        with zipfile.ZipFile(self.source / "experiment.zip", "w") as z:
            for name, blob in files.items():
                z.writestr(name, blob)

    def test_dry_run_then_stage_and_verify(self):
        self.make({"part/a.py": "print(7)", "part/note.md": "note",
                   "__pycache__/junk.pyc": "bytecode"})
        before = run(self.source, self.destination)
        self.assertEqual((before["member_count"], before["pending_files"], before["staged"]),
                         (2, 2, False))
        staged = run(self.source, self.destination, stage=True)
        self.assertEqual(staged["pending_files"], 2)
        self.assertEqual(run(self.source, self.destination)["pending_files"], 0)
        target = self.destination / (
            "research/continuity_engine/collected/archive_sources/experiment/part/a.py")
        self.assertEqual(target.read_text(), "print(7)")

    def test_conflict_never_overwrites(self):
        self.make({"a.txt": "first"})
        run(self.source, self.destination, stage=True)
        target = self.destination / (
            "research/continuity_engine/collected/archive_sources/experiment/a.txt")
        target.write_text("changed")
        with self.assertRaises(FileExistsError):
            run(self.source, self.destination, stage=True)
        self.assertEqual(target.read_text(), "changed")

    def test_traversal_refused(self):
        for name in ("../a.py", "/a.py", "C:/a.py", "x\\y", ""):
            with self.subTest(name=name), self.assertRaises(ValueError):
                safe_path(name)

    def test_archive_member_traversal_refused(self):
        self.make({"../../escape.py": "bad"})
        with self.assertRaises(ValueError):
            run(self.source, self.destination, stage=True)

    def test_duplicate_member_refused(self):
        with zipfile.ZipFile(self.source / "experiment.zip", "w") as z:
            z.writestr("foo.txt", "a")
            z.writestr("foo.txt", "b")
        with self.assertRaises(ValueError):
            run(self.source, self.destination)


if __name__ == "__main__":
    unittest.main()
