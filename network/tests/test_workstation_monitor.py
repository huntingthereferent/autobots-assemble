"""Read-only workstation projection against real existing event and edition contracts."""
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff
from runtime.journal import RuntimeJournal
from systems.workspace.monitor import workstation_snapshot
from systems.workspace.store import WorkspaceStore
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.process_handoff import CorrespondenceWorkBridge, WORKER_ID

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "work/arc_like_maze/chatbot"

INPUTS = {"old_phi": [0, 0, 1], "new_phi": [0, 0, 0],
          "candidate_words": [["ABAA", "ABBABA"], ["ABAA", "AAABB", "BAAAB"]],
          "required_state": [0, 0, 0], "required_action": "B"}

def runtime_events(runtime):
    store = runtime.event_store
    return tuple(store.all()) if hasattr(store, "all") else tuple((k, x.event_type) for k in sorted(store.storage) for x in store.storage[k])

class WorkstationMonitorTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.workdir = self.root / "workstation"
        self.journal = self.root / "runtime.jsonl"
        self.lanes_path = self.root / "workspace.jsonl"
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.journal))
        self.workstation = ProcessWorkstation(self.workdir)

    def view(self, *, runtime=None):
        return workstation_snapshot(root=self.workdir, runtime=runtime or self.runtime,
                                    workspace_journal=self.lanes_path)

    def edition(self, *, worker_id=WORKER_ID, version_id="v1"):
        selected = self.root / ("source-" + worker_id)
        selected.mkdir()
        for f in ("finite_goal_priority.py", "finite_required_edge_guard.py"):
            shutil.copyfile(SOURCE / f, selected / f)
        return self.workstation.copy_source(selected, worker_id=worker_id, version_id=version_id)

    def test_empty_read_never_creates_state(self):
        self.assertFalse(self.workdir.exists())
        a = self.view()
        self.assertTrue(a["read_only"])
        self.assertEqual(a["jobs"], [])
        self.assertEqual(a["editions"], [])
        self.assertEqual(a["counts"]["jobs"], 0)
        self.assertFalse(self.workdir.exists())
        self.assertFalse(self.journal.exists())
        self.assertFalse(self.lanes_path.exists())

    def test_version_inventory_is_generic_not_chatbot_owned(self):
        self.edition()
        source = self.root / "sample"
        source.mkdir()
        (source / "make.txt").write_text("worker\n")
        self.workstation.copy_source(source,worker_id="factory-calibration",version_id="test-a")
        v = self.view()
        self.assertEqual(v["counts"]["workers"], 2)
        self.assertEqual(v["counts"]["editions"], 2)
        self.assertEqual({x["worker_id"] for x in v["editions"]},
                         {WORKER_ID, "factory-calibration"})
        self.assertFalse(any("path" in x or "source_locator" in x for x in v["editions"]))
        self.assertTrue(all(x["verified"] is False for x in v["editions"]))

    def test_branch_ancestry_and_change_without_new_job(self):
        first = self.edition()
        p = Path(first["path"]) / "notes.txt"
        p.write_text("experiment\n")
        self.workstation.branch(worker_id=WORKER_ID,parent_version="v1",version_id="v2")
        v = self.view()
        branch = next(e for e in v["editions"] if e["version_id"] == "v2")
        self.assertEqual(branch["parent_version"], "v1")
        self.assertFalse(branch["source_modified"])
        parent = next(e for e in v["editions"] if e["version_id"] == "v1")
        self.assertEqual(parent["added"], ["notes.txt"])
        self.assertEqual(v["counts"]["jobs"], 0)

    def test_admitted_not_executed_remains_ready(self):
        self.edition()
        bridge = CorrespondenceWorkBridge(runtime=self.runtime, workstation=self.workstation)
        handoff = bridge.admit(version_id="v1", inputs=INPUTS,
                               from_actor="james", lane_id="research")
        before = runtime_events(self.runtime)
        payload = self.view()
        job = payload["jobs"][0]
        self.assertEqual(job["job_id"], handoff.handoff_id)
        self.assertEqual(job["source_state"], "MATCHES_ADMISSION")
        self.assertEqual(job["status"], "READY")
        self.assertEqual(job["lane_refs"], ["research"])
        self.assertEqual(job["verification"], "not-complete")
        self.assertEqual(before, runtime_events(self.runtime))

    def test_actual_subprocess_result_and_evidence_not_upgraded(self):
        self.edition()
        bridge = CorrespondenceWorkBridge(runtime=self.runtime, workstation=self.workstation)
        handoff = bridge.admit(version_id="v1", inputs=INPUTS, from_actor="james")
        bridge.execute(handoff.handoff_id, allow_local_execution=True)
        events = runtime_events(self.runtime)
        view = self.view()
        self.assertEqual(view["counts"]["recorded_complete"], 1)
        row = view["jobs"][0]
        self.assertEqual(row["status"], "COMPLETE")
        self.assertEqual(row["verification"], "recorded-not-reverified")
        self.assertEqual([e["event_type"] for e in row["events"]], ["CREATED","STARTED","RESULT"])
        self.assertTrue(row["result"]["verdicts"])
        self.assertEqual(row["evidence"][0]["kind"], "computation")
        self.assertEqual(events, runtime_events(self.runtime))

    def test_restart_preserves_result_without_reexecuting(self):
        self.edition()
        bridge = CorrespondenceWorkBridge(runtime=self.runtime, workstation=self.workstation)
        handoff = bridge.admit(version_id="v1", inputs=INPUTS, from_actor="james")
        bridge.execute(handoff.handoff_id, allow_local_execution=True)
        before = self.view()
        restored = HandoffRuntime(event_store=RuntimeJournal(self.journal))
        after = self.view(runtime=restored)
        self.assertEqual(before["jobs"], after["jobs"])
        self.assertEqual(before["counts"], after["counts"])

    def test_source_changed_warns_without_rewriting_result(self):
        copied = self.edition()
        bridge = CorrespondenceWorkBridge(runtime=self.runtime, workstation=self.workstation)
        h = bridge.admit(version_id="v1", inputs=INPUTS, from_actor="james")
        bridge.execute(h.handoff_id, allow_local_execution=True)
        events = runtime_events(self.runtime)
        (Path(copied["path"]) / "finite_required_edge_guard.py").write_text("# modified\n")
        row = self.view()["jobs"][0]
        self.assertEqual(row["source_state"], "SOURCE_CHANGED")
        self.assertEqual(row["status"], "COMPLETE")
        self.assertEqual(row["verification"], "recorded-not-reverified")
        self.assertEqual(runtime_events(self.runtime), events)

    def test_nonworkstation_handoffs_do_not_leak_into_work_view(self):
        self.runtime.submit(Handoff(handoff_id="personal", referent="private",
                        from_actor="person", to_actor="someone",required_relation="read"))
        self.assertEqual(self.view()["jobs"], [])

    def test_other_worker_and_another_relation_share_projection(self):
        self.edition(worker_id="other-process")
        self.runtime.submit(Handoff(handoff_id="other-job", referent="calibration",
                         from_actor="operator",to_actor="calibrator",required_relation="calibration",
                         metadata={"source_system":"process-workstation","worker_id":"other-process",
                                   "worker_version":"v1"}))
        row=self.view()["jobs"][0]
        self.assertEqual(row["worker_id"],"other-process")
        self.assertEqual(row["source_state"],"NO_PIN")
        self.assertEqual(row["status"],"READY")

    def test_missing_edition_is_not_called_verified(self):
        self.runtime.submit(Handoff(handoff_id="missing-edition", referent="test",
                          from_actor="james",to_actor="worker",required_relation="inspect",
                          metadata={"source_system":"process-workstation","worker_id":"gone",
                                    "worker_version":"v1","edition_fingerprint":"a"*64}))
        row = self.view()["jobs"][0]
        self.assertEqual(row["source_state"],"EDITION_NOT_REGISTERED")

    def test_corrupted_manifest_flagged_not_crashing_dashboard(self):
        path = Path(self.edition()["path"]) / "_worker_version.json"
        path.write_text("{}")
        edition=self.view()["editions"][0]
        self.assertEqual(edition["state"],"UNREADABLE")

    def test_lane_return_points_remain_source_owned(self):
        s=WorkspaceStore(self.lanes_path)
        s.open_lane("research",label="Research",referent="finite proof",actor_id="james")
        s.record_movement("research",preserved="original proof",next_movement="new finite test")
        before=s.events()
        view=self.view()
        self.assertEqual(view["workspace"]["lanes"][0]["next_movement"],"new finite test")
        self.assertEqual(WorkspaceStore(self.lanes_path).events(),before)

if __name__ == "__main__":
    unittest.main()
