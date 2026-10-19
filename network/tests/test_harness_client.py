"""Real native worker round-trip via an agent-neutral workstation client.

This test runs a registered finite worker and replays its verifier. It does not
execute Harness² itself, claim an LLM performance result, or touch game worlds.
"""
import json
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.branch_help import CAP_FINITE, CAP_GAME
from systems.workspace.coordinator_window import CoordinatorIndex
from systems.workspace.cp_motion import admit_research
from systems.workspace.harness_client import WorkstationClient
from systems.workspace.process_handoff import WORKER_ID
from systems.workspace.workstation import ProcessWorkstation


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work" / "arc_like_maze" / "chatbot"
INPUTS = {
    "old_phi": [0, 0, 1], "new_phi": [0, 0, 0],
    "candidate_words": [["ABAA", "ABBABA"], ["ABAA", "AAABB", "BAAAB"]],
    "required_state": [0, 0, 0], "required_action": "B",
}


class HarnessClientTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.data = self.root / "private"
        admit_research(CoordinatorIndex(self.data / "coordinator-windows.jsonl"))
        src = self.root / "source"
        src.mkdir()
        for name in ("finite_goal_priority.py", "finite_required_edge_guard.py"):
            shutil.copyfile(SOURCE / name, src / name)
        self.desk = ProcessWorkstation(self.data / "workstation")
        self.desk.copy_source(src, worker_id=WORKER_ID, version_id="base")
        self.inputs = self.root / "inputs.json"
        self.inputs.write_text(json.dumps(INPUTS))
        self.client = WorkstationClient(self.data, client_id="harness2")

    def request(self, **kw):
        return self.client.request_worker(
            lane="game", slot="cp-game-w13-worlds",
            capability=CAP_FINITE, opening_key="h2-native-001",
            reason="Run a registered finite source-owned worker",
            parent_version="base", inputs_file=self.inputs,
            admit_registered=True, **kw,
        )

    def runtime(self):
        return HandoffRuntime(event_store=RuntimeJournal(self.data / "runtime.jsonl"))

    def test_external_client_can_admit_execute_verify_existing_worker(self):
        row = self.request()
        self.assertEqual(row["state"], "ASSIGNED_NOT_VERIFIED")
        self.assertFalse(row["executed"])
        job = row["child"]["job_id"]
        self.assertEqual(self.runtime().state(job).status, "READY")
        with self.assertRaises(ValueError):
            self.client.reverify_return(opening_id=row["opening_id"])
        with self.assertRaises(PermissionError):
            self.client.execute_worker(opening_id=row["opening_id"],
                                       expected_job_id=job)
        self.assertEqual(self.runtime().state(job).status, "READY")
        got = self.client.execute_worker(opening_id=row["opening_id"],
                                         expected_job_id=job,
                                         allow_native_execution=True)
        self.assertEqual(got["execution"]["status"], "COMPLETE")
        self.assertEqual(got["return"]["state"],
                         "RETURN_RECORDED_REVERIFY_BEFORE_USE")
        self.assertFalse(got["return"]["parent_cp_witnessed"])
        original_journal = (self.data / "runtime.jsonl").read_bytes()
        verified = self.client.reverify_return(opening_id=row["opening_id"])
        self.assertEqual(verified["state"], got["return"]["state"])
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), original_journal)
        replay = self.client.execute_worker(opening_id=row["opening_id"],
                                            expected_job_id=job,
                                            allow_native_execution=True)
        self.assertEqual(replay["execution"]["status"], "COMPLETE")
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), original_journal)

    def test_other_agent_can_use_same_workstation_without_another_scheduler(self):
        first = self.request()
        other = WorkstationClient(self.data, client_id="codex-client")
        second = other.request_worker(
            lane="game", slot="cp-game-w13-worlds",
            capability=CAP_FINITE, opening_key="h2-native-001",
            reason="Run a registered finite source-owned worker",
            parent_version="base", inputs_file=self.inputs,
            admit_registered=True,
        )
        self.assertEqual(first["child"], second["child"])
        events = self.runtime().event_store.for_handoff(first["opening_id"])
        labels = [e.actor_id for e in events
                  if e.event_type == "WORKSTATION_CLIENT_REQUEST"]
        self.assertEqual(labels, ["harness2", "codex-client"])
        self.assertEqual(len([x for x in self.runtime().snapshot()
                              if x.startswith("help-job-")]), 1)
        again = self.request()
        self.assertEqual(again["child"], first["child"])
        events = self.runtime().event_store.for_handoff(first["opening_id"])
        self.assertEqual(sum(e.event_type == "WORKSTATION_CLIENT_REQUEST"
                             for e in events), 2)

    def test_exact_job_identity_cannot_be_bypassed(self):
        row = self.request()
        with self.assertRaises(PermissionError):
            self.client.execute_worker(
                opening_id=row["opening_id"], expected_job_id="different",
                allow_native_execution=True)
        self.assertEqual(self.runtime().state(row["child"]["job_id"]).status, "READY")

    def test_unknown_capability_is_not_a_worker(self):
        row = self.client.request_worker(
            lane="game", slot="cp-game-w13-worlds",
            capability=CAP_GAME, opening_key="not-registered",
            reason="Do not pretend a generic builder was installed",
            parent_version="base", inputs_file=self.inputs,
            admit_registered=True,
        )
        self.assertEqual(row["state"], "OPEN_UNSTAFFED")
        self.assertFalse(row["registered_capability"])
        with self.assertRaises(ValueError):
            self.client.execute_worker(
                opening_id=row["opening_id"], expected_job_id="fiction",
                allow_native_execution=True)
        self.assertFalse(any(x.startswith("help-job-")
                             for x in self.runtime().snapshot()))


if __name__ == "__main__":
    unittest.main()
