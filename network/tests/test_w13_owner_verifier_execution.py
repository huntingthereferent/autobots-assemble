"""Strict source-owner consent tests, without downloading historical evidence."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import subprocess
import unittest

from systems.workspace.github_w13_continuation import _git_blob
from systems.workspace.game_native_verifier_bridge import (
    OWNER_W13_JOB, OWNER_W13_RESULT_EVENT, OWNER_W13_FINGERPRINT,
    OWNER_JOB_ID, OWNER_VERSION, WORKER_ID)
from systems.workspace.w13_owner_verifier_execution import (
    REQUEST, EXPECTED_REQUEST, PARENT_RESEARCH_BLOB,
    VERIFIER_BRIDGE_BLOB, VERIFIER_WORKER_BLOB, WORKER_PATH, BRIDGE_PATH,
    RESEARCH_PATH, authenticate_owner_request, execute_exact_authorized_child,
)

ROOT = Path(__file__).resolve().parents[2]


class OriginalW13ConsentGateTests(unittest.TestCase):
    def test_exact_source_and_readonly_predecessor_are_pinned(self):
        self.assertEqual(EXPECTED_REQUEST["original_w13_job_id"], OWNER_W13_JOB)
        self.assertEqual(EXPECTED_REQUEST["original_w13_result_event_id"], OWNER_W13_RESULT_EVENT)
        self.assertEqual(EXPECTED_REQUEST["original_w13_source_fingerprint"], OWNER_W13_FINGERPRINT)
        self.assertEqual(EXPECTED_REQUEST["job_id"], OWNER_JOB_ID)
        self.assertEqual(EXPECTED_REQUEST["source_version"], OWNER_VERSION)
        self.assertEqual(EXPECTED_REQUEST["worker_id"], WORKER_ID)
        for rel, expected in ((WORKER_PATH, VERIFIER_WORKER_BLOB),
                              (BRIDGE_PATH, VERIFIER_BRIDGE_BLOB),
                              (RESEARCH_PATH, PARENT_RESEARCH_BLOB)):
            self.assertEqual(_git_blob(ROOT/rel), expected)
        self.assertTrue(all(EXPECTED_REQUEST[x] for x in (
            "authorizes_source_copy", "authorizes_admission", "authorizes_execution")))

    def test_future_owner_request_requires_the_exact_source_contract(self):
        # The gate PR intentionally has no request. Once the owner separately
        # commits one, the repository-wide suite must verify its bytes rather
        # than unconditionally reject the legitimate next activation step.
        path=ROOT/REQUEST
        if path.exists():
            self.assertTrue(path.is_file())
            self.assertFalse(path.is_symlink())
            self.assertLessEqual(path.stat().st_size,4096)
            self.assertEqual(json.loads(path.read_text(encoding="utf8")),EXPECTED_REQUEST)
        else:
            self.assertFalse(path.is_symlink())

    def test_invalid_revision_refused_before_loading_artifact_or_admitting(self):
        with self.assertRaisesRegex(ValueError, "exact owner-merge SHA"):
            authenticate_owner_request(ROOT, "main")
        with self.assertRaisesRegex(ValueError, "exact owner-merge SHA"):
            execute_exact_authorized_child(artifact_dir=ROOT,
                source_binding=ROOT,repo_root=ROOT,owner_merge_sha="invalid")

    def test_single_parent_or_unreviewed_request_cannot_authorize_native_child(self):
        with TemporaryDirectory() as temp:
            root=Path(temp)
            subprocess.run(["git","init","-q",str(root)],check=True)
            f=root/REQUEST
            f.parent.mkdir(parents=True)
            f.write_text(json.dumps(EXPECTED_REQUEST,sort_keys=True)+"\n")
            subprocess.run(["git","-C",str(root),"add","."],check=True)
            subprocess.run(["git","-C",str(root),"-c","user.name=fixture",
                "-c","user.email=fixture@example.invalid",
                "commit","-qm","unreviewed authorization"],check=True)
            rev=subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],
                                        text=True).strip()
            with self.assertRaisesRegex(ValueError, "two-parent protected-main"):
                authenticate_owner_request(root,rev)
            self.assertEqual(len(list(root.rglob("runtime.jsonl"))),0)

    def test_next_checkpoint_is_source_constrained_but_not_self_executing(self):
        import inspect
        from systems.workspace import w13_owner_verifier_execution as impl
        text=inspect.getsource(impl.execute_exact_authorized_child)
        self.assertLess(text.index("authenticate_owner_request("),
                        text.index("copy_verifier_source("))
        self.assertLess(text.index("verify_local_relation("),
                        text.index("copy_verifier_source("))
        self.assertIn('run_exact_linked_job(',text)
        self.assertIn('child_result_event_id',text)
        workflow=(ROOT/".github/workflows/w13-owner-native-verifier-one-shot.yml").read_text()
        self.assertIn("github.actor == github.repository_owner", workflow)
        self.assertIn("github.event_name == 'push'", workflow)
        self.assertIn('actions/download-artifact@v4', workflow)
        self.assertIn("source-contract-tests", workflow)
        self.assertIn("git", inspect.getsource(impl.authenticate_owner_request))
        self.assertNotIn("actions/upload-artifact@",workflow)


if __name__ == "__main__":
    unittest.main()
