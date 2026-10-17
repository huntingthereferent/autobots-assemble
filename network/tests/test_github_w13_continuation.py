"""W13 native evidence continuation: actual state-carriage guards, no replay bypass."""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import tarfile
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from systems.workspace import github_w13_continuation as stage


def tar_entry(name: str, body: bytes = b"", *, kind: bytes | None = None):
    info = tarfile.TarInfo(name)
    if kind:
        info.type = kind
        info.linkname = "../escape"
    else:
        info.size = len(body)
    return info, body


class CrossRunnerW13Tests(TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.artifact = self.root / "artifact"
        self.artifact.mkdir()
        self.runtime = self.root / "inherited"
        self.output = self.root / "output"

    def make_archive(self, entries):
        archive = self.artifact / "native-runtime.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            for info, body in entries:
                tar.addfile(info, BytesIO(body))
        digest = sha256(archive.read_bytes()).hexdigest()
        (self.artifact / "native-runtime.sha256").write_text(digest + "  archive\n")
        return digest

    def test_01_original_digest_is_identity_not_generic_green(self):
        self.assertEqual(stage.RUN_ID, 39025574748)
        self.assertEqual(stage.ARTIFACT_ID, 12098716155)
        self.assertIn("sha256:", stage.ORIGINAL_DIGEST)
        self.assertEqual(stage.NEXT, "GAME-NATIVE-VERIFIER")

    def test_02_archived_runtime_requires_sha256(self):
        self.make_archive([
            tar_entry("runtime.jsonl", b"events\n"),
            tar_entry("coordinator-windows.jsonl", b"index\n"),
        ])
        (self.artifact / "native-runtime.sha256").write_text("0" * 64 + " archive\n")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            stage.unpack_native_runtime(self.artifact, self.runtime)

    def test_03_rejects_tar_path_traversal(self):
        self.make_archive([
            tar_entry("runtime.jsonl", b"events\n"),
            tar_entry("coordinator-windows.jsonl", b"index\n"),
            tar_entry("workstation/../../escape", b"forged"),
        ])
        with self.assertRaisesRegex(ValueError, "unsafe archived"):
            stage.unpack_native_runtime(self.artifact, self.runtime)
        self.assertFalse((self.root / "escape").exists())

    def test_04_rejects_tar_symlink(self):
        self.make_archive([
            tar_entry("runtime.jsonl", b"events\n"),
            tar_entry("coordinator-windows.jsonl", b"index\n"),
            tar_entry("workstation/link", kind=tarfile.SYMTYPE),
        ])
        with self.assertRaisesRegex(ValueError, "unsafe archived"):
            stage.unpack_native_runtime(self.artifact, self.runtime)

    def test_05_prevents_reopening_nonempty_workstation(self):
        self.make_archive([
            tar_entry("runtime.jsonl", b"events\n"),
            tar_entry("coordinator-windows.jsonl", b"index\n"),
        ])
        self.runtime.mkdir()
        (self.runtime / "runtime.jsonl").write_text("previous\n")
        with self.assertRaisesRegex(ValueError, "refusing to overlay"):
            stage.unpack_native_runtime(self.artifact, self.runtime)

    def test_06_unwitnessed_parent_never_opens_branch(self):
        prior = {"cp_automation": {
            "witnessed": [],
            "frontier": ["GAME-W13-WORLDS"],
            "checkpoints": [
                {"checkpoint": stage.CHECKPOINT, "state": "ADMISSIBLE"},
                {"checkpoint": stage.NEXT, "state": "BLOCKED"},
            ]
        }}
        with (patch.object(stage, "validate_archive_metadata", return_value={}),
              patch.object(stage, "unpack_native_runtime", return_value="f" * 64),
              patch.object(stage, "CoordinatorIndex"),
              patch.object(stage, "workstation_cp_view", return_value={}),
              patch.object(stage, "freshly_reverify_linked_jobs", return_value={}),
              patch.object(stage, "one_cp_handoff", return_value=prior),
              patch.object(stage, "open_help") as opening):
            with self.assertRaisesRegex(ValueError, "failed fresh native replay"):
                stage.continue_from_artifact(
                    artifact_dir=self.artifact, data_dir=self.runtime,
                    output_dir=self.output, origin={"run_id":stage.RUN_ID,"attempt":1},
                    repo_root=self.root)
            opening.assert_not_called()

    def test_07_verified_parent_creates_one_durable_unstaffed_opening(self):
        packet={"cp_automation":{
            "witnessed":[stage.CHECKPOINT],
            "frontier":[stage.NEXT],
            "checkpoints":[
                {"checkpoint":stage.CHECKPOINT,"state":"WITNESSED"},
                {"checkpoint":stage.NEXT,"state":"ADMISSIBLE"},
            ]}}
        opening={"opening_id":"cp-help-original","state":"OPEN_UNSTAFFED"}
        origin={"run_id":stage.RUN_ID,"attempt":1,
                "artifact_id":stage.ARTIFACT_ID,
                "digest":stage.ORIGINAL_DIGEST,
                "head_sha":stage.ORIGINAL_HEAD}
        with (patch.object(stage,"validate_archive_metadata",return_value={}),
              patch.object(stage,"unpack_native_runtime",return_value="f"*64),
              patch.object(stage,"CoordinatorIndex"),
              patch.object(stage,"workstation_cp_view",return_value={}),
              patch.object(stage,"freshly_reverify_linked_jobs",return_value={}),
              patch.object(stage,"one_cp_handoff",return_value=packet),
              patch.object(stage,"open_help",return_value=opening) as new_branch,
              patch("systems.workspace.branch_help.help_summary",
                    return_value=[opening])):
            result=stage.continue_from_artifact(
                artifact_dir=self.artifact,data_dir=self.runtime,
                output_dir=self.output,origin=origin,repo_root=self.root)
            self.assertEqual(result["next_cp"],stage.NEXT)
            self.assertEqual(result["branch_state"],"OPEN_UNSTAFFED")
            self.assertFalse(result["child_job_admitted"])
            self.assertFalse(result["child_job_executed"])
            new_branch.assert_called_once()
            self.assertEqual(json.loads(
                (self.output/"continuation.json").read_text())["parent_state"],"WITNESSED")

    def test_08_original_archive_must_have_both_journals(self):
        self.make_archive([tar_entry("runtime.jsonl", b"events\n")])
        with self.assertRaisesRegex(ValueError,"journals incomplete"):
            stage.unpack_native_runtime(self.artifact,self.runtime)


if __name__=="__main__":
    import unittest
    unittest.main()
