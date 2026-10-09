from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

from runtime.ollama_ab import OllamaABDriver
from runtime.pool_evaluator import ContinuityPoolEvaluator
from runtime.continuity_pool import connect_pool, pool_snapshot
from runtime.service import EcosystemService

ROOT = Path(__file__).resolve().parents[2]


class LocalAIEvaluatorTests(unittest.TestCase):
    def test_model_selected_source_is_actually_read(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "native.txt").write_text("Observed real source", encoding="utf-8")
            driver = OllamaABDriver(root)
            proposal = {
                "state": "MOVE", "source": "native.txt",
                "direction": "follow native source", "next_edge": "check witness",
                "reason": "inspect before implementing",
            }
            with patch.object(driver, "_ask", return_value=proposal):
                move, evidence = driver.observe(
                    referent="one actual task", available=("native.txt",),
                )
            self.assertEqual(move["state"], "MOVE")
            self.assertEqual(move["tool"], "read_native_source")
            self.assertEqual(move["excerpt"], "Observed real source")
            self.assertEqual(len(evidence), 1)
            self.assertIn("sha256:", evidence[0].ref)

    def test_unadmitted_path_is_not_executed(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "native.txt").write_text("A", encoding="utf-8")
            driver = OllamaABDriver(root)
            with patch.object(driver, "_ask", return_value={
                "state": "MOVE", "source": "../secret.txt",
                "direction": "escape", "next_edge": "bad",
            }):
                move, evidence = driver.observe(
                    referent="task", available=("native.txt",),
                )
            self.assertEqual(move["state"], "UNKNOWN")
            self.assertEqual(evidence, ())

    def test_ollama_tool_movement_is_inside_existing_agent_lineage(self):
        class FakeDriver:
            model = "local-test-model"
            calls = 0
            def observe(self, *, referent, available, task_context=()):
                self.task_context = task_context
                self.called = True
                self.calls += 1
                return {"state": "MOVE", "source": available[0],
                        "tool": "read_native_source"}, ()
        fake = FakeDriver()
        with TemporaryDirectory() as temp:
            evaluator = ContinuityPoolEvaluator(ROOT, model_driver=fake)
            service = EcosystemService(
                data_dir=temp, repository_work_file=ROOT / "TASKS.md",
                ab_evaluator=evaluator,
            )
            evaluator.bind(service)
            result = connect_pool(service, ROOT)
            self.assertEqual(result["evaluator_run"], "EVALUATED")
            self.assertTrue(fake.called)
            self.assertEqual(len(fake.task_context), 3)
            self.assertEqual(fake.calls, 1)
            self.assertIn("required_witnesses", fake.task_context[0])
            snap = pool_snapshot(service)
            self.assertEqual(snap["last_evaluation"]["model_actor"], "local-test-model")
            self.assertEqual(
                snap["last_evaluation"]["generative_ab_movement"]["state"], "MOVE")
            self.assertTrue(all(t["status"] == "READY" for t in snap["original_tasks"]))
            self.assertFalse(snap["autonomous_site_build_complete"])
            # Reopening the same native state reuses the recorded model witness.
            recovered = EcosystemService(
                data_dir=temp, repository_work_file=ROOT / "TASKS.md",
                ab_evaluator=ContinuityPoolEvaluator(ROOT, model_driver=fake),
            )
            recovered.agent_lineage.evaluate.bind(recovered)
            replay = connect_pool(recovered, ROOT)
            self.assertEqual(replay["evaluator_run"], "REUSED")
            self.assertEqual(fake.calls, 1)

    def test_unavailable_model_preserves_ready_agent_and_unknown(self):
        class OfflineDriver:
            model = "local-offline-test"
            def observe(self, **kwargs):
                raise ConnectionRefusedError("local inference unavailable")
        with TemporaryDirectory() as temp:
            evaluator = ContinuityPoolEvaluator(ROOT, model_driver=OfflineDriver())
            service = EcosystemService(
                data_dir=temp, repository_work_file=ROOT / "TASKS.md",
                ab_evaluator=evaluator,
            )
            evaluator.bind(service)
            connect_pool(service, ROOT)
            snap = pool_snapshot(service)
            self.assertEqual(snap["last_evaluation"]["model_actor"], "UNAVAILABLE")
            self.assertEqual(
                snap["last_evaluation"]["generative_ab_movement"]["state"], "UNKNOWN")
            self.assertTrue(all(row["status"] == "READY"
                                for row in snap["original_tasks"]))


if __name__ == "__main__":
    unittest.main()
