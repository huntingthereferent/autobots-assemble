"""Strict source-owner consent tests, without downloading historical evidence."""
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import json
import base64
from hashlib import sha256
from unittest.mock import patch
from contextlib import ExitStack
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


class RetentionHookTests(unittest.TestCase):
    def test_partial_retention_options_fail_before_authentication_or_execution(self):
        from systems.workspace import w13_owner_verifier_execution as impl
        for args in ({"recipient_public_key_b64": "unused"},
                     {"encrypted_output": Path("unused")}):
            with patch.object(impl, "authenticate_owner_request") as old, \
                 patch.object(impl, "authenticate_retention_request") as new:
                with self.assertRaisesRegex(ValueError, "BOTH"):
                    impl.execute_exact_authorized_child(artifact_dir=ROOT,
                        source_binding=ROOT, repo_root=ROOT, owner_merge_sha="a"*40, **args)
                old.assert_not_called()
                new.assert_not_called()

    def test_unusable_recipient_is_rejected_before_git_or_execution(self):
        from systems.workspace import w13_owner_verifier_execution as impl
        for key in ("invalid", base64.b64encode(bytes(32)).decode()):
            with patch.object(impl, "_git") as git:
                with self.assertRaisesRegex(ValueError,"recipient public key"):
                    impl.authenticate_retention_request(ROOT,"a"*40,key)
                git.assert_not_called()

    def test_retention_requires_new_merge_request_and_pins_recipient(self):
        from systems.workspace import w13_owner_verifier_execution as impl
        key=base64.b64encode(bytes(range(32))).decode()
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            def git(*args):
                return subprocess.check_output(["git", "-C", str(root),
                    "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                    *args], text=True).strip()
            git("init", "-q")
            (root/"base").write_text("base")
            for rel in (impl.WORKER_PATH, impl.BRIDGE_PATH, impl.RESEARCH_PATH):
                target=root/rel; target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes((ROOT/rel).read_bytes())
            git("add", "."); git("commit", "-qm", "base")
            base=git("rev-parse", "HEAD")
            git("checkout", "-qb", "retention")
            request={"contract":"owner-w13-future-child-local-encrypted-retention/v1",
                "execution":impl.EXPECTED_REQUEST,
                "recipient_public_key_sha256":sha256(bytes(range(32))).hexdigest(),
                "authorizes_local_encrypted_retention":True,
                "authorizes_artifact_upload":False, "authorizes_raw_journal_export":False}
            path=root/impl.RETENTION_REQUEST
            path.parent.mkdir(parents=True); path.write_text(json.dumps(request))
            git("add", "."); git("commit", "-qm", "request")
            single=git("rev-parse", "HEAD")
            with self.assertRaisesRegex(ValueError,"two-parent"):
                impl.authenticate_retention_request(root,single,key)
            git("checkout", "-q", "--detach", base)
            git("merge", "--no-ff", "-qm", "owner review", "retention")
            merge=git("rev-parse", "HEAD")
            self.assertEqual(impl.authenticate_retention_request(root,merge,key),request)
            with self.assertRaisesRegex(ValueError,"recipient"):
                impl.authenticate_retention_request(root,merge,
                    base64.b64encode(b"z"*32).decode())
            path.write_text(json.dumps({**request,"authorizes_artifact_upload":True}))
            with self.assertRaisesRegex(ValueError,"changed"):
                impl.authenticate_retention_request(root,merge,key)
            git("restore", "--", impl.RETENTION_REQUEST)
            (root/"unrelated").write_text("unrelated")
            git("add", "."); git("commit", "-qm", "later change")
            later=git("rev-parse", "HEAD")
            git("checkout", "-qb", "another")
            (root/"branch").write_text("branch")
            git("add", "."); git("commit", "-qm", "another")
            git("checkout", "-q", "--detach", later)
            git("merge", "--no-ff", "-qm", "later merge", "another")
            with self.assertRaisesRegex(ValueError,"NEW retention"):
                impl.authenticate_retention_request(root,git("rev-parse","HEAD"),key)

    def test_seal_runs_before_temporary_journal_cleanup_and_failure_is_not_success(self):
        from systems.workspace import w13_owner_verifier_execution as impl
        from systems.workspace import owner_native_evidence_vault as vault
        for fail in (False, True):
            with self.subTest(seal_failure=fail), TemporaryDirectory() as tmp, ExitStack() as stack:
                def mock(name, **kwargs):
                    return stack.enter_context(patch.object(impl,name,**kwargs))
                mock("authenticate_retention_request")
                mock("_object", return_value={"repository":"huntingthereferent/autobots-assemble",
                    "workflow":"workstation-w13-owner-merged-one-shot", "run_id":impl.RUN_ID,
                    "artifact_id":impl.ARTIFACT_ID,"attempt":1,"head_sha":impl.ORIGINAL_HEAD,
                    "digest":impl.ORIGINAL_DIGEST})
                mock("validate_archive_metadata")
                mock("unpack_native_runtime", side_effect=lambda artifact,data:data.mkdir())
                mock("verify_local_relation", return_value={"native_verified":True,
                    "relation":"EXACT_COMMITTED_SOURCE_TO_NATIVE_RESULT_MATCH",
                    "result_event_id":impl.OWNER_W13_RESULT_EVENT,
                    "native_source_fingerprint":impl.OWNER_W13_FINGERPRINT})
                runtime=mock("HandoffRuntime").return_value
                runtime.snapshot.return_value={}
                runtime.state.return_value.status="READY"
                index=mock("CoordinatorIndex").return_value
                index.definition.return_value=(None,{"game":[{"slot":impl.SLOT,"source_kind":"planned"}]})
                mock("freshly_reverify_linked_jobs")
                mock("workstation_cp_view")
                def cp(verifier,ready):
                    return {"cp_automation":{"checkpoints":[
                        {"checkpoint":"GAME-W13-WORLDS","state":"WITNESSED"},
                        {"checkpoint":"GAME-NATIVE-VERIFIER","state":verifier},
                        {"checkpoint":"GAME-WORKER-READY","state":ready}]}}
                mock("one_cp_handoff", side_effect=[cp("ADMISSIBLE","WALLED"),cp("WITNESSED","ADMISSIBLE")])
                mock("copy_verifier_source"); mock("ProcessWorkstation")
                bridge=mock("NativeGameVerifierBridge").return_value
                bridge.admit.return_value.dependencies=(impl.OWNER_W13_JOB,)
                mock("run_exact_linked_job",return_value={"status":"COMPLETE"})
                mock("reverify_local",return_value={"recorded_status":"COMPLETE",
                    "verification":"FRESH_NATIVE_REVERIFICATION_LOCAL","source_fingerprint":"test-only",
                    "events":[{"type":"RESULT","result_status":"COMPLETE","event_id":"test-only"}]})
                observed=[]
                def seal(**kwargs):
                    observed.append(kwargs["data_dir"])
                    self.assertTrue(observed[-1].is_dir())
                    if fail:
                        raise ValueError("seal failure")
                    return {"test_only":True}
                stack.enter_context(patch.object(vault,"seal_verified",side_effect=seal))
                args=dict(artifact_dir=ROOT,source_binding=ROOT,repo_root=ROOT,
                    owner_merge_sha="a"*40,recipient_public_key_b64="test-only",
                    encrypted_output=Path(tmp)/"capsule.enc")
                if fail:
                    with self.assertRaisesRegex(ValueError,"seal failure"):
                        impl.execute_exact_authorized_child(**args)
                else:
                    result=impl.execute_exact_authorized_child(**args)
                    self.assertEqual(result["encrypted_retention"],{"test_only":True})
                self.assertEqual(len(observed),1)
                self.assertFalse(observed[0].exists())


if __name__ == "__main__":
    unittest.main()
