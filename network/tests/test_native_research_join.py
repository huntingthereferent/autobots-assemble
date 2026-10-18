"""Exact source-to-native-result relationship tests with real finite native replay."""
from __future__ import annotations

from pathlib import Path
import json
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.process_handoff import (
    CorrespondenceWorkBridge, WORKER_ID, VERIFIER,
)
from systems.workspace.native_receipt_projection import recorded_receipt
from systems.workspace.native_research_join import verify_local_relation

SOURCE = Path(__file__).resolve().parents[2] / "work/arc_like_maze/chatbot"
INPUTS = {"old_phi": [0, 0, 1], "new_phi": [0, 0, 0],
          "candidate_words": [["ABAA", "ABBABA"], ["ABAA", "AAABB", "BAAAB"]],
          "required_state": [0, 0, 0], "required_action": "B"}
RELPATH = "state/pins/research-join-fixture.json"


class NativeResearchJoinTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.repo = root / "repo"
        self.repo.mkdir()
        self.data = root / "private-runtime"
        self.path = self.repo / RELPATH
        self.path.parent.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.job = "joined-finite-local-1"
        self.handoff = None
        self.receipt = None

    def commit(self, record):
        self.path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf8")
        subprocess.run(["git", "-C", str(self.repo), "add", RELPATH], check=True)
        subprocess.run([
            "git", "-C", str(self.repo),
            "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-q", "-m", "record fixture"
        ], check=True)
        return subprocess.check_output(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"], text=True).strip()

    def basic(self):
        return {"schema_version": 1, "title": "Synthetic local test movement",
                "result_state": "MOVE", "walls": []}

    def call(self, commit):
        return verify_local_relation(
            data_dir=self.data, job_id=self.job, repo_root=self.repo,
            research_commit=commit, research_path=RELPATH)

    def native_result(self):
        # Actual finite child-process execution and source-native re-verification,
        # not a mocked source verdict or a PR/browser-success surrogate.
        edition = self.data / "finite-source"
        edition.mkdir(parents=True)
        for name in ("finite_goal_priority.py", "finite_required_edge_guard.py"):
            shutil.copyfile(SOURCE / name, edition / name)
        workstation = ProcessWorkstation(self.data / "workstation")
        workstation.copy_source(edition, worker_id=WORKER_ID, version_id="native-v1")
        runtime = HandoffRuntime(event_store=RuntimeJournal(self.data / "runtime.jsonl"))
        bridge = CorrespondenceWorkBridge(runtime=runtime, workstation=workstation)
        self.handoff = bridge.admit(
            version_id="native-v1", inputs=INPUTS, from_actor="local-test",
            job_id=self.job)
        bridge.execute(self.job, allow_local_execution=True)
        bridge.reverify(self.job)
        self.receipt = recorded_receipt(runtime, self.job)
        self.assertEqual(self.receipt["recorded_status"], "COMPLETE")
        self.assertEqual(self.receipt["events"][-1]["type"], "RESULT")

    def declaration(self):
        assert self.receipt is not None
        return {
            "schema": "research-native-receipt-relation/v1",
            "job_id": self.job,
            "result_event_id": self.receipt["events"][-1]["event_id"],
            "worker_id": WORKER_ID,
            "worker_version": "native-v1",
            "native_verifier_id": VERIFIER,
            "source_fingerprint": self.receipt["source_fingerprint"],
        }

    def test_missing_explicit_relation_stays_open_without_native_runtime(self):
        rev = self.commit(self.basic())
        row = self.call(rev)
        self.assertEqual(row["relation"], "OPEN_NO_EXACT_SOURCE_DECLARATION")
        self.assertFalse(row["native_verified"])
        self.assertFalse(row["publicly_published"])
        self.assertEqual(row["research_causality"], "NOT_ESTABLISHED")
        self.assertFalse(self.data.exists())

    def test_real_native_finite_result_and_exact_committed_source_identity(self):
        self.native_result()
        source = self.basic()
        source["native_workstation_receipt"] = self.declaration()
        rev = self.commit(source)
        before = (self.data / "runtime.jsonl").read_bytes()
        row = self.call(rev)
        self.assertEqual(row["relation"], "EXACT_COMMITTED_SOURCE_TO_NATIVE_RESULT_MATCH")
        self.assertTrue(row["native_verified"])
        self.assertEqual(row["result_event_id"], self.receipt["events"][-1]["event_id"])
        self.assertFalse(row["independent_research_owner_attestation"])
        self.assertEqual(row["research_causality"], "NOT_ESTABLISHED")
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_research_revision_tampering_fails_even_when_native_passes(self):
        self.native_result()
        src = self.basic()
        src["native_workstation_receipt"] = self.declaration()
        rev = self.commit(src)
        self.path.write_text(self.path.read_text() + " ", encoding="utf8")
        with self.assertRaisesRegex(ValueError, "differs from pinned Git revision"):
            self.call(rev)

    def test_wrong_result_event_rejected_after_fresh_native_replay(self):
        self.native_result()
        src = self.basic()
        decl = self.declaration()
        decl["result_event_id"] = "evt_" + "9" * 32
        src["native_workstation_receipt"] = decl
        rev = self.commit(src)
        with self.assertRaisesRegex(ValueError, "exact native RESULT"):
            self.call(rev)

    def test_wrong_source_fingerprint_never_accepted(self):
        self.native_result()
        src = self.basic()
        decl = self.declaration()
        decl["source_fingerprint"] = "0" * 64
        src["native_workstation_receipt"] = decl
        rev = self.commit(src)
        with self.assertRaisesRegex(ValueError, "native source identity differs"):
            self.call(rev)

    def test_nonmove_record_cannot_proclaim_verified_movement(self):
        self.native_result()
        src = self.basic()
        src["result_state"] = "BLOCKED"
        src["native_workstation_receipt"] = self.declaration()
        rev = self.commit(src)
        with self.assertRaisesRegex(ValueError, "not a structured original MOVE"):
            self.call(rev)

    def test_invalid_path_and_ancestor_not_matched(self):
        rev = self.commit(self.basic())
        with self.assertRaises(ValueError):
            verify_local_relation(data_dir=self.data, job_id=self.job,
                repo_root=self.repo, research_commit=rev,
                research_path="state/current.json")
        with self.assertRaises(ValueError):
            verify_local_relation(data_dir=self.data, job_id=self.job,
                repo_root=self.repo, research_commit=rev,
                research_path="../runtime/data/runtime.jsonl")

    def test_native_verifier_does_not_get_skipped_by_a_declared_source(self):
        self.native_result()
        src=self.basic()
        src["native_workstation_receipt"]=self.declaration()
        rev=self.commit(src)
        with patch("systems.workspace.native_research_join.reverify_local",
                   side_effect=ValueError("native failed")):
            with self.assertRaisesRegex(ValueError,"native failed"):
                self.call(rev)


if __name__ == "__main__":
    unittest.main()
