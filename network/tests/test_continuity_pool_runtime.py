"""The ORIGINAL three tasks, durable admission, direct A/B, and no fake closure."""
from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import copy2
import unittest

from runtime.continuity_pool import ACTOR, connect_pool, pool_snapshot, run_pool_ab
from runtime.service import EcosystemService

ROOT = Path(__file__).resolve().parents[2]


class OriginalPoolTests(unittest.TestCase):
    def test_exact_three_tasks_and_separate_james_queue(self):
        with TemporaryDirectory() as tmp:
            svc = EcosystemService(data_dir=Path(tmp), repository_work_file=ROOT/"TASKS.md")
            report = connect_pool(svc, ROOT)
            self.assertEqual(report["assignee"], ACTOR)
            self.assertEqual(report["tasks"], [
                "Finish Continuity site", "Find things to swallow",
                "Visual provenance min/max",
            ])
            self.assertEqual(len(svc.agent_lineage.roots_for_actor(ACTOR)), 1)
            self.assertEqual(len(svc.agent_lineage.roots_for_actor("james")), 0)
            result = pool_snapshot(svc)
            self.assertEqual(len(result["original_tasks"]), 3)
            self.assertTrue(all(t["status"] == "READY" and t["result"] is None
                                for t in result["original_tasks"]))
            self.assertEqual(result["last_native_ab"]["native_reference_moves"], 3)
            self.assertEqual(result["last_native_ab"]["actual_tasks_completed"], 0)
            self.assertEqual(result["last_native_ab"]["ab_states"][:3],
                             ["MOVE", "MOVE", "MOVE"])
            self.assertEqual(result["last_native_ab"]["ab_states"][-1], "UNKNOWN")
            self.assertEqual(result["agent_roots"][0]["status"], "READY")
            self.assertEqual(result["agent_roots"][0]["missing_witnesses"],
                             ["movement witness"])
            self.assertFalse(result["model_backed_worker_running"])
            connected = svc.connections()["continuity_pool"]
            self.assertEqual(connected["original_tasks_admitted"], 3)
            self.assertTrue(connected["native_ab_connected"])
            self.assertFalse(connected["model_backed_worker_running"])

    def test_restart_and_rerun_are_duplicate_safe(self):
        with TemporaryDirectory() as tmp:
            state = Path(tmp)
            svc = EcosystemService(data_dir=state, repository_work_file=ROOT/"TASKS.md")
            first = connect_pool(svc, ROOT)
            before = tuple(svc.runtime.event_store.all())
            again = connect_pool(svc, ROOT)
            self.assertEqual(again["root"], first["root"])
            self.assertEqual(again["native_ab"], "REUSED")
            self.assertEqual(tuple(svc.runtime.event_store.all()), before)
            restarted = EcosystemService(data_dir=state,repository_work_file=ROOT/"TASKS.md")
            third = connect_pool(restarted, ROOT)
            self.assertEqual(third["root"], first["root"])
            self.assertEqual(third["native_ab"], "REUSED")
            self.assertEqual(tuple(restarted.runtime.event_store.all()), before)
            self.assertEqual(len(restarted.personal.tasks()), 3)
            self.assertEqual(restarted.agent_lineage.roots_for_actor(ACTOR),
                             (first["root"],))

    def test_existing_original_task_ids_are_preserved(self):
        old = Path(r"E:\continuity-traversal\runtime\data\personal_operations.jsonl")
        if not old.is_file():
            self.skipTest("original external task journal is not mounted")
        with TemporaryDirectory() as tmp:
            state = Path(tmp)
            copy2(old, state/"personal_operations.jsonl")
            svc = EcosystemService(data_dir=state,repository_work_file=ROOT/"TASKS.md")
            original_ids = [t.task_id for t in svc.personal.tasks()]
            self.assertEqual(len(original_ids), 3)
            connect_pool(svc, ROOT)
            self.assertEqual([t.task_id for t in svc.personal.tasks()], original_ids)
            self.assertEqual(len(pool_snapshot(svc)["original_tasks"]), 3)
            self.assertEqual(len(svc.agent_lineage.roots_for_actor(ACTOR)), 1)

    def test_no_unseeded_agent_and_no_unrelated_james_tasks(self):
        with TemporaryDirectory() as tmp:
            svc = EcosystemService(data_dir=Path(tmp))
            self.assertEqual(run_pool_ab(svc, ROOT)["status"], "NO_AGENT")
            self.assertEqual(svc.runtime.event_store.all(), ())


if __name__ == "__main__":
    unittest.main()
