"""Historical source copy is not proof of a runnable owner-backed process."""
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.integrated_source import (WORKER_ID, copy_integrated_source,
                                                 verify_archive_source)
from systems.workspace.workstation import ProcessWorkstation


class IntegratedSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo"
        self.private = self.root / "private"
        self.integrated = self.repo / "work/arc_like_maze/chatbot/research/integrated"
        self.integrated.mkdir(parents=True)
        self.manifest = {"schema_version": 1, "original_file_count": 281,
                         "stages": [{"cumulative_file_count": 201+8*i} for i in range(11)],
                         "files": {}}
        for n in range(281):
            stage = 20 if n < 201 else 21+(n-201)//8
            name = f"source_{n:03d}.py"
            content = f"# CP{stage} original file {n}\n".encode()
            origin = ("baseline" if stage == 20 else f"deltas/{stage}") + "/" + name
            target = self.integrated / origin
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            self.manifest["files"][name] = {"stage":stage,"path":origin,"size":len(content),
                                            "sha256":sha256(content).hexdigest()}
        self.write_manifest()

    def write_manifest(self):
        (self.integrated / "MANIFEST.json").write_text(json.dumps(self.manifest))

    def copy(self, stage=30, version="cp30", allow=True):
        return copy_integrated_source(repo_root=self.repo,data_dir=self.private,
                                      stage=stage,version_id=version,allow_copy=allow)

    def test_full_cp30_copy_preserves_exact_hashes_but_not_execution_claims(self):
        result = self.copy()
        self.assertEqual(result["file_count"],281)
        self.assertTrue(result["source_verified"])
        self.assertFalse(result["capability_verified"])
        self.assertFalse(result["executed"])
        self.assertFalse(result["job_admitted"])
        desk=ProcessWorkstation(self.private / "workstation")
        edition=desk.inspect(worker_id=WORKER_ID,version_id="cp30")
        self.assertEqual(edition["current_fingerprint"],result["source_fingerprint"])
        self.assertEqual(edition["modified"],[])
        provenance=json.loads((self.private / "workstation" / WORKER_ID / "cp30/_worker_version.json").read_text())
        self.assertEqual(provenance["source_locator"],
                         "repo:work/arc_like_maze/chatbot/research/integrated/MANIFEST.json#CP-30")
        self.assertFalse((self.private / "runtime.jsonl").exists())
        self.assertEqual((self.integrated / "baseline/source_000.py").read_bytes(),
                         (self.private / "workstation" / WORKER_ID / "cp30/source_000.py").read_bytes())

    def test_copy_cp20_contains_only_original_201_files(self):
        result=self.copy(stage=20,version="cp20")
        self.assertEqual(result["file_count"],201)
        self.assertFalse((self.private / "workstation" / WORKER_ID / "cp20/source_201.py").exists())
        self.assertTrue((self.private / "workstation" / WORKER_ID / "cp20/source_200.py").exists())

    def test_refuses_implicit_copy_and_overwrite(self):
        with self.assertRaises(PermissionError):self.copy(allow=False)
        self.assertFalse(self.private.exists())
        self.copy()
        with self.assertRaises(FileExistsError):self.copy()

    def test_incorrect_historical_bytes_fail_closed_before_private_copy(self):
        (self.integrated / "baseline/source_000.py").write_text("tampered")
        with self.assertRaisesRegex(ValueError,"integrity failure"):
            self.copy()
        self.assertFalse(self.private.exists())

    def test_path_traversal_manifest_refused(self):
        self.manifest["files"]["source_000.py"]["path"]="../../../../../../etc/hosts"
        self.write_manifest()
        with self.assertRaises((ValueError,FileNotFoundError)):
            verify_archive_source(self.repo)

    def test_reject_stage_and_private_repo_collision(self):
        with self.assertRaises(ValueError):verify_archive_source(self.repo,31)
        with self.assertRaises(ValueError):
            copy_integrated_source(repo_root=self.repo,data_dir=self.repo,stage=30,
                                   version_id="unsafe",allow_copy=True)

    def test_branch_is_independent_of_recovered_original(self):
        self.copy()
        desk=ProcessWorkstation(self.private / "workstation")
        desk.branch(worker_id=WORKER_ID,parent_version="cp30",version_id="experiment")
        patch=self.private / "workstation" / WORKER_ID / "experiment/source_280.py"
        patch.write_text("# edited in isolated branch\n")
        self.assertTrue(desk.inspect(worker_id=WORKER_ID,version_id="experiment")["modified"])
        self.assertFalse(desk.inspect(worker_id=WORKER_ID,version_id="cp30")["modified"])
        self.assertEqual((self.integrated / "deltas/30/source_280.py").read_text(),"# CP30 original file 280\n")


if __name__ == "__main__":unittest.main()
