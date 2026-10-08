"""ARC native observations and original Continuity tasks share ONE lineage callback."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from runtime.arc_native_observer import ARCFrameObservationProvider
from runtime.continuity_pool import connect_pool, pool_snapshot
from runtime.pool_evaluator import ContinuityPoolEvaluator
from runtime.service import EcosystemService

ROOT = Path(__file__).resolve().parents[2]


def frame(color):
    cells = [0] * (64 * 64)
    cells[36 * 64 + 36] = color
    return SimpleNamespace(frame=[cells], levels_completed=0)


class CombinedEvaluatorTests(unittest.TestCase):
    def setup_both(self, folder, *, observer=None):
        observer = observer or ARCFrameObservationProvider("ft09")
        primary = ContinuityPoolEvaluator(ROOT)
        service = EcosystemService(
            data_dir=folder, repository_work_file=ROOT / "TASKS.md",
            ab_evaluator=primary, native_observer=observer,
        )
        primary.bind(service)
        return service, observer

    def test_both_evidence_types_run_via_same_agent_lineage(self):
        with TemporaryDirectory() as temp:
            svc, observer = self.setup_both(Path(temp))
            original = connect_pool(svc, ROOT)
            self.assertEqual(original["evaluator_run"], "EVALUATED")
            pool_root = original["root"]
            pool_events = svc.runtime.event_store.for_handoff(pool_root)
            self.assertEqual(sum(e.event_type == "AGENT_AB_OBSERVED" for e in pool_events), 1)
            self.assertEqual(svc.runtime.state(pool_root).status, "READY")
            self.assertEqual(svc.agent_lineage.step(pool_root).executed, ())
            start = svc.activate_agent({
                "surface": "begin comparison", "actor_id": "james",
                "instance_id": "arc-same-runtime", "referent": "ft09 current board",
            })
            arc_root = start["root"]
            self.assertEqual(svc.agent_lineage.step(arc_root).executed, ())
            observer.record_native_step(
                handoff_id=arc_root, referent="ft09 current board",
                before=frame(9), after=frame(8),
                action="ACTION6 click(36,36)", x=36, y=36,
                predicted_after={"cell_color": 8, "levels_completed": 0},
            )
            result = svc.agent_lineage.step(arc_root)
            self.assertEqual(result.executed, (arc_root,))
            arc_state = svc.runtime.state(arc_root)
            self.assertEqual(arc_state.status, "COMPLETE")
            self.assertEqual(arc_state.output["ab_state"], "MOVE")
            self.assertEqual(arc_state.output["changed"]["cell_color"]["after"], 8)
            self.assertEqual(svc.runtime.state(pool_root).status, "READY")
            self.assertEqual(len(pool_snapshot(svc)["original_tasks"]), 3)
            self.assertEqual(svc.monitor(actor_id="continuity-agent-pool")["counts"]["agents_total"], 1)
            self.assertEqual(svc.monitor(actor_id="james")["counts"]["agents_total"], 1)
            self.assertEqual(svc.agent_lineage.step(pool_root).executed, ())
            self.assertEqual(svc.agent_lineage.step(arc_root).executed, ())

    def test_restart_keeps_native_journal_without_false_replay(self):
        with TemporaryDirectory() as temp:
            folder = Path(temp)
            svc, observer = self.setup_both(folder)
            pool_root = connect_pool(svc, ROOT)["root"]
            arc_root = svc.activate_agent({
                "surface": "begin comparison", "actor_id": "james",
                "instance_id": "arc-restart", "referent": "ft09 current board",
            })["root"]
            observer.record_native_step(
                handoff_id=arc_root, referent="ft09 current board",
                before=frame(9), after=frame(8),
                action="ACTION6", x=36, y=36,
                predicted_after={"cell_color": 8, "levels_completed": 0},
            )
            svc.agent_lineage.step(arc_root)
            before = tuple(svc.runtime.event_store.all())
            recovered, new_observer = self.setup_both(folder)
            self.assertEqual(connect_pool(recovered, ROOT)["evaluator_run"], "REUSED")
            self.assertEqual(recovered.agent_lineage.step(arc_root).executed, ())
            self.assertEqual(recovered.agent_lineage.step(pool_root).executed, ())
            self.assertEqual(tuple(recovered.runtime.event_store.all()), before)
            self.assertEqual(recovered.runtime.state(arc_root).status, "COMPLETE")
            self.assertEqual(recovered.runtime.state(pool_root).status, "READY")

    def test_unscoped_primary_cannot_claim_native_source_actors(self):
        with TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "explicit primary actor scope"):
                EcosystemService(
                    data_dir=temp,
                    ab_evaluator=lambda agent, state: None,
                    native_observer=ARCFrameObservationProvider("ft09"),
                )


if __name__ == "__main__":
    unittest.main()
