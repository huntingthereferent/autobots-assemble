"""Canonical A/B evaluator is connected INSIDE the existing pool agent."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.agent_lineage import AgentMove
from runtime.continuity_pool import connect_pool, pool_snapshot
from runtime.handoff import ExecutionResult
from runtime.pool_evaluator import ContinuityPoolEvaluator
from runtime.service import EcosystemService

ROOT = Path(__file__).resolve().parents[2]


class CanonicalEvaluatorTests(unittest.TestCase):
    def make(self, data):
        worker = ContinuityPoolEvaluator(ROOT)
        service = EcosystemService(data_dir=data, repository_work_file=ROOT / "TASKS.md",
                                   ab_evaluator=worker)
        worker.bind(service)
        return service

    def test_one_live_agent_evaluator_path_not_parallel_ab(self):
        with TemporaryDirectory() as tmp:
            svc = self.make(Path(tmp))
            report = connect_pool(svc, ROOT)
            root = report["root"]
            snap = pool_snapshot(svc)
            self.assertEqual(report["evaluator_run"], "EVALUATED")
            self.assertTrue(svc.agent_lineage.can_evaluate(svc.runtime.get(root)))
            self.assertTrue(snap["evaluator_registered"])
            self.assertEqual(snap["evaluator_observations"], 1)
            event = svc.runtime.event_store.for_handoff(root)[-1]
            self.assertEqual(event.event_type, "AGENT_AB_OBSERVED")
            self.assertEqual(event.data["status"], "UNKNOWN")
            self.assertEqual(event.data["output"]["source_relation_moves"], 3)
            self.assertEqual(event.data["output"]["swallow_attempts"], 1)
            self.assertEqual(event.data["output"]["task_results"], "NOT_EXECUTED")
            self.assertTrue(all(e.condition == "source relation checked"
                                for e in event.evidence))
            self.assertEqual(svc.runtime.state(root).missing_witnesses,
                             ("movement witness",))
            self.assertEqual(svc.runtime.state(root).status, "READY")
            self.assertEqual(len(snap["original_tasks"]), 3)
            self.assertTrue(all(t["status"] == "READY" for t in snap["original_tasks"]))
            self.assertFalse(any(e.event_type in {"RESULT", "CONTINUITY_POOL_AB"}
                                for e in svc.runtime.event_store.for_handoff(root)))

    def test_resumption_is_noop_even_after_restart(self):
        with TemporaryDirectory() as tmp:
            svc = self.make(Path(tmp))
            root = connect_pool(svc, ROOT)["root"]
            before = tuple(svc.runtime.event_store.all())
            self.assertEqual(svc.agent_lineage.run_until_idle(root), ())
            self.assertEqual(tuple(svc.runtime.event_store.all()), before)
            restart = self.make(Path(tmp))
            self.assertEqual(connect_pool(restart, ROOT)["evaluator_run"], "REUSED")
            self.assertEqual(tuple(restart.runtime.event_store.all()), before)

    def test_monitor_is_actor_scoped_and_no_legacy_false_status(self):
        with TemporaryDirectory() as tmp:
            svc = self.make(Path(tmp))
            connect_pool(svc, ROOT)
            pool = svc.monitor(actor_id="continuity-agent-pool")
            james = svc.monitor(actor_id="james")
            self.assertTrue(pool["connections"]["agents"]["ab_evaluator_connected"])
            self.assertFalse(james["connections"]["agents"]["ab_evaluator_connected"])
            self.assertEqual(pool["monitor"]["mode"], "queued_manual")
            self.assertEqual(pool["counts"]["tasks_total"], 3)
            self.assertEqual(james["counts"]["tasks_total"], 0)
            self.assertTrue(any(e["event_type"] == "AGENT_AB_OBSERVED"
                                and e["status"] == "UNKNOWN" for e in pool["events"]))

    def test_observation_cannot_claim_complete_or_birth(self):
        with TemporaryDirectory() as tmp:
            svc = self.make(Path(tmp))
            root = connect_pool(svc, ROOT)["root"]
            agent = svc.runtime.get(root)
            before = tuple(svc.runtime.event_store.all())
            with self.assertRaisesRegex(ValueError, "must remain unresolved"):
                svc.agent_lineage._observe_only(agent, AgentMove(
                    ExecutionResult(status="COMPLETE", output={}),
                    observation_only=True,
                ))
            with self.assertRaisesRegex(ValueError, "cannot request births"):
                svc.agent_lineage._observe_only(agent, AgentMove(
                    ExecutionResult(status="UNKNOWN", output={}),
                    observation_only=True, next_referent="fake next",
                ))
            self.assertEqual(tuple(svc.runtime.event_store.all()), before)


if __name__ == "__main__":
    unittest.main()
