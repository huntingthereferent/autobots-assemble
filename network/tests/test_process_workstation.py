"""Source-only workstation copies; no AI agent or runtime execution required."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from systems.workspace.workstation import ProcessWorkstation


class ProcessWorkstationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "original"
        self.source.mkdir()
        (self.source / "worker.py").write_text("VALUE = 1\n")
        (self.source / "configs").mkdir()
        (self.source / "configs" / "scope.json").write_text('{"scope":"finite"}\n')
        self.bench = ProcessWorkstation(self.root / "private")

    def version(self, version_id="one"):
        return self.bench.copy_source(self.source, worker_id="correspondence", version_id=version_id)

    def test_copy_has_provenance_and_original_unchanged(self):
        v = self.version()
        self.assertEqual(v["file_count"], 2)
        self.assertEqual((Path(v["path"]) / "worker.py").read_text(), "VALUE = 1\n")
        self.assertEqual((self.source / "worker.py").read_text(), "VALUE = 1\n")
        self.assertEqual(self.bench.inspect(worker_id="correspondence", version_id="one")["modified"], [])

    def test_modification_isolated_from_original(self):
        v = self.version()
        (Path(v["path"]) / "worker.py").write_text("VALUE = 2\n")
        self.assertEqual((self.source / "worker.py").read_text(), "VALUE = 1\n")
        self.assertEqual(self.bench.inspect(worker_id="correspondence", version_id="one")["modified"], ["worker.py"])

    def test_fork_modified_copy_and_keep_parent_intact(self):
        v = self.version()
        (Path(v["path"]) / "worker.py").write_text("VALUE = 3\n")
        b = self.bench.branch(worker_id="correspondence", parent_version="one", version_id="two")
        self.assertEqual(b["parent_version"], "one")
        self.assertEqual((Path(b["path"]) / "worker.py").read_text(), "VALUE = 3\n")
        (Path(b["path"]) / "worker.py").write_text("VALUE = 4\n")
        self.assertEqual((Path(v["path"]) / "worker.py").read_text(), "VALUE = 3\n")
        self.assertEqual((self.source / "worker.py").read_text(), "VALUE = 1\n")

    def test_parallel_versions_are_independent(self):
        self.version("a")
        self.version("b")
        self.assertNotEqual(self.bench._edition("correspondence", "a"), self.bench._edition("correspondence", "b"))

    def test_detect_new_and_deleted_files(self):
        p = Path(self.version()["path"])
        (p / "added.py").write_text("x = 1\n")
        (p / "configs" / "scope.json").unlink()
        info = self.bench.inspect(worker_id="correspondence", version_id="one")
        self.assertEqual(info["added"], ["added.py"])
        self.assertEqual(info["deleted"], ["configs/scope.json"])

    def test_reject_overwrite_without_mutating_existing(self):
        self.version()
        with self.assertRaises(FileExistsError):
            self.version()
        self.assertEqual(self.bench.inspect(worker_id="correspondence", version_id="one")["added"], [])

    def test_reject_traversal_name(self):
        with self.assertRaises(ValueError):
            self.bench.copy_source(self.source, worker_id="../other", version_id="one")

    def test_reject_empty_source(self):
        (self.source / "worker.py").unlink()
        (self.source / "configs" / "scope.json").unlink()
        with self.assertRaises(ValueError):
            self.version()

    def test_reject_symlink_source(self):
        (self.source / "bad").symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.version()

    def test_reject_secret_name(self):
        (self.source / ".env").write_text("secret\n")
        with self.assertRaises(ValueError):
            self.version()

    def test_fork_does_not_inherit_verification(self):
        self.version()
        info = self.bench.inspect(worker_id="correspondence", version_id="one")
        self.assertFalse(info["verified"])
        self.assertFalse(info["executed"])

    def test_refuse_falsified_identity(self):
        p = Path(self.version()["path"]) / "_worker_version.json"
        doc = json.loads(p.read_text())
        doc["worker_id"] = "other"
        p.write_text(json.dumps(doc))
        with self.assertRaises(ValueError):
            self.bench.inspect(worker_id="correspondence", version_id="one")

    def test_reject_edited_provenance_baseline(self):
        p = Path(self.version()["path"]) / "_worker_version.json"
        doc = json.loads(p.read_text())
        doc["baseline"]["worker.py"] = "0" * 64
        p.write_text(json.dumps(doc))
        with self.assertRaises(ValueError):
            self.bench.branch(worker_id="correspondence", parent_version="one", version_id="two")

    def test_refuse_source_inside_workspace(self):
        self.version()
        with self.assertRaises(ValueError):
            self.bench.copy_source(self.bench._edition("correspondence", "one"), worker_id="other", version_id="v1")

    def test_nested_modules_copied_without_rewriting_names(self):
        self.version()
        self.assertTrue((self.bench._edition("correspondence", "one") / "configs/scope.json").is_file())

    def test_modified_parent_is_snapshot_of_branch_time(self):
        v = self.version()
        p = Path(v["path"])
        (p / "worker.py").write_text("VALUE = 2\n")
        self.bench.branch(worker_id="correspondence", parent_version="one", version_id="two")
        (p / "worker.py").write_text("VALUE = 99\n")
        info = self.bench.inspect(worker_id="correspondence", version_id="two")
        self.assertEqual(info["modified"], [])
        self.assertEqual((self.bench._edition("correspondence", "two") / "worker.py").read_text(), "VALUE = 2\n")


if __name__ == "__main__":
    unittest.main()
