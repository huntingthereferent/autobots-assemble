"""The ORIGINAL three tasks, durable admission, direct A/B, and no fake closure."""
from pathlib import Path
from tempfile import TemporaryDirectory
from shutil import copy2
import unittest

from runtime.continuity_pool import ACTOR, connect_pool, pool_snapshot, run_pool_ab
from runtime.service import EcosystemService
from runtime.pool_evaluator import ContinuityPoolEvaluator

ROOT = Path(__file__).resolve().parents[2]


class OriginalPoolTests(unittest.TestCase):
    def new_service(self, state, repo=ROOT):
        evaluator = ContinuityPoolEvaluator(repo)
        service = EcosystemService(data_dir=state,
            repository_work_file=repo / "TASKS.md", ab_evaluator=evaluator)
        evaluator.bind(service)
        return service

    def test_exact_three_tasks_and_separate_james_queue(self):
        with TemporaryDirectory() as tmp:
            svc = self.new_service(Path(tmp))
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
            self.assertEqual(result["last_evaluation"]["source_relation_moves"], 3)
            self.assertEqual(result["last_evaluation"]["task_results"], "NOT_EXECUTED")
            self.assertEqual(result["last_evaluation"]["ab_states"][:3],
                             ["MOVE", "MOVE", "MOVE"])
            self.assertIn("UNKNOWN", result["last_evaluation"]["ab_states"])
            self.assertEqual(result["last_evaluation"]["swallow_attempts"], 1)
            self.assertEqual(result["agent_roots"][0]["status"], "READY")
            self.assertEqual(result["agent_roots"][0]["missing_witnesses"],
                             ["movement witness"])
            self.assertFalse(result["model_backed_worker_running"])
            connected = svc.connections()["continuity_pool"]
            self.assertEqual(connected["original_tasks_admitted"], 3)
            self.assertTrue(connected["registered_evaluator"])
            self.assertFalse(connected["model_backed_worker_running"])

    def test_restart_and_rerun_are_duplicate_safe(self):
        with TemporaryDirectory() as tmp:
            state = Path(tmp)
            svc = self.new_service(state)
            first = connect_pool(svc, ROOT)
            before = tuple(svc.runtime.event_store.all())
            again = connect_pool(svc, ROOT)
            self.assertEqual(again["root"], first["root"])
            self.assertEqual(again["evaluator_run"], "REUSED")
            self.assertEqual(tuple(svc.runtime.event_store.all()), before)
            restarted = self.new_service(state)
            third = connect_pool(restarted, ROOT)
            self.assertEqual(third["root"], first["root"])
            self.assertEqual(third["evaluator_run"], "REUSED")
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
            svc = self.new_service(state)
            original_ids = [t.task_id for t in svc.personal.tasks()]
            self.assertEqual(len(original_ids), 3)
            connect_pool(svc, ROOT)
            self.assertEqual([t.task_id for t in svc.personal.tasks()], original_ids)
            self.assertEqual(len(pool_snapshot(svc)["original_tasks"]), 3)
            self.assertEqual(len(svc.agent_lineage.roots_for_actor(ACTOR)), 1)

    def test_no_unseeded_agent_and_no_unrelated_james_tasks(self):
        with TemporaryDirectory() as tmp:
            svc = self.new_service(Path(tmp))
            self.assertEqual(run_pool_ab(svc, ROOT)["status"], "NO_AGENT")
            self.assertEqual(svc.runtime.event_store.all(), ())


if __name__ == "__main__":
    unittest.main()
