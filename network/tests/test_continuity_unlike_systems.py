"""Continuity interoperability across unlike native mathematical and factory systems.

Uses the real native Cyclic Action Engine, persistent shared HandoffRuntime,
and Factory's own event-sourced local order state. No universal world model.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult
from runtime.journal import RuntimeJournal
from runtime.orchestrator import Orchestrator
from systems.bindings import factory_binding
from systems.factory import FactorySystem, default_simulated_actors
from work.arc_like_maze.cyclic_action_continuation import CyclicActionContinuation
from work.arc_like_maze.continuity_handoff import (
    AB_CONJUGATE, B_CONJUGATE, B_DISTINGUISHED, CyclicActionHandoff,
)
from network.tests.test_arc_like_cyclic_action_continuation import negative, positive


ORDER_ID = "ORDER-UNLIKE"


class UnlikeSystemContinuityTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.journal = self.root / "runtime.jsonl"
        self.factory_path = self.root / "factory.jsonl"
        self.witnesses = self.root / "native-witnesses"
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.journal))
        self.math = CyclicActionHandoff(self.runtime, self.witnesses)
        self.factory = FactorySystem(self.factory_path)
        self.factory.create_order(
            order_id=ORDER_ID, product="demo-widget",
            quantity=4, material="demo-stock",
        )
        self._bind_factory()

    def _bind_factory(self):
        self.orchestrator = Orchestrator(self.runtime)
        self.orchestrator.register_system(
            factory_binding(self.factory, order_ids=(ORDER_ID,))
        )
        for actor in default_simulated_actors().values():
            self.orchestrator.register_actor(actor)

    def _restart_both(self):
        self.runtime = HandoffRuntime(event_store=RuntimeJournal(self.journal))
        self.math = CyclicActionHandoff(self.runtime, self.witnesses)
        self.factory = FactorySystem(self.factory_path)
        self._bind_factory()

    @staticmethod
    def negative_at(depth):
        return CyclicActionContinuation.enter(*negative()).advance(depth)

    @staticmethod
    def positive_at(depth):
        return CyclicActionContinuation.enter(*positive()).advance(depth)

    def test_one_runtime_preserves_independent_mathematical_and_factory_results(self):
        self.math.submit(self.positive_at(27), handoff_id="math-positive",
                         claim=B_CONJUGATE)
        self.assertEqual(self.math.conclude("math-positive").status, "COMPLETE")
        self.orchestrator.run_until_idle()

        self.assertEqual(self.factory.order(ORDER_ID).status, "complete")
        self.assertEqual(
            self.factory.order(ORDER_ID).local_state["shipment_state"], "shipped"
        )
        math_state = self.math.recover("math-positive")
        self.assertTrue(math_state.output["bijection_verified"])
        self.assertEqual(math_state.output["watched_scope"], "B_ONLY_ON_x0_EQ_2")

        factory_handoffs = [
            h for h in self.runtime._handoffs.values()
            if h.metadata.get("source_system") == "factory"
        ]
        self.assertEqual(len(factory_handoffs), 5)
        self.assertNotIn("native_evidence_verifier", factory_handoffs[0].metadata)
        self.assertEqual(
            self.runtime.get("math-positive").metadata["native_evidence_verifier"],
            "cyclic-action.restricted-B.v1",
        )
        for h in factory_handoffs:
            state = self.runtime.state(h.handoff_id)
            self.assertEqual(state.status, "COMPLETE")
            self.assertTrue(state.evidence)
            self.assertTrue(all(
                e.kind == "simulation" and e.depth == "simulated"
                for e in state.evidence
            ))
        self.assertEqual(self.runtime.state("math-positive").evidence[0].kind,
                         "native-replay")

    def test_restart_recovers_independent_state_and_continuations(self):
        old = self.negative_at(8)
        self.math.submit(old, handoff_id="math-unknown",
                         claim=B_DISTINGUISHED)
        self.assertEqual(self.math.conclude("math-unknown").status, "UNKNOWN")

        self.assertEqual(len(self.orchestrator.step().executed), 1)
        self.assertEqual(len(self.orchestrator.step().executed), 1)
        self.assertEqual(self.factory.order(ORDER_ID).stage_index, 2)
        recorded = tuple(
            (h.handoff_id, len(self.runtime.event_store.for_handoff(h.handoff_id)))
            for h in self.runtime._handoffs.values()
            if h.metadata.get("source_system") == "factory"
        )
        self._restart_both()
        self.assertEqual(self.factory.order(ORDER_ID).stage_index, 2)
        self.assertEqual(self.math.recover("math-unknown").status, "UNKNOWN")
        self.orchestrator.run_until_idle()
        self.assertEqual(self.factory.order(ORDER_ID).status, "complete")
        self.assertEqual(
            tuple(
                (hid, len(self.runtime.event_store.for_handoff(hid)))
                for hid, _ in recorded
            ),
            recorded,
        )
        new = old.advance(9)
        self.math.submit(new, handoff_id="math-distinguished",
                         claim=B_DISTINGUISHED,
                         previous_handoff_id="math-unknown")
        self.assertEqual(self.math.conclude("math-distinguished").status,
                         "COMPLETE")
        self._restart_both()
        self.assertEqual(self.math.recover("math-unknown").status, "UNKNOWN")
        self.assertEqual(
            self.math.recover("math-distinguished").output["distinguishing_depth"],
            9,
        )
        self.assertEqual(self.factory.order(ORDER_ID).stage_index, 5)

    def test_native_math_evidence_does_not_discharge_factory_stage(self):
        self.math.submit(self.positive_at(27), handoff_id="math-positive",
                         claim=B_CONJUGATE)
        mathematical = self.math.conclude("math-positive")
        handoff = self.factory.next_handoff(ORDER_ID)
        self.runtime.submit(handoff)
        before = len(self.runtime.event_store.all())
        with self.assertRaisesRegex(ValueError, "material supplied"):
            self.runtime.return_result(
                handoff.handoff_id, actor_id=handoff.to_actor,
                result=ExecutionResult(
                    status="COMPLETE",
                    evidence=mathematical.evidence,
                ),
            )
        self.assertEqual(len(self.runtime.event_store.all()), before)
        self.assertEqual(self.factory.order(ORDER_ID).stage_index, 0)

    def test_factory_simulation_cannot_forge_mathematical_proof(self):
        self.math.submit(self.positive_at(26), handoff_id="math-unknown",
                         claim=B_CONJUGATE)
        self.orchestrator.step()
        factory_evidence = self.runtime.state(
            f"factory-{ORDER_ID}-01-supply"
        ).evidence[0]
        before = len(self.runtime.event_store.all())
        with self.assertRaises(ValueError):
            self.runtime.return_result(
                "math-unknown", actor_id="unverified",
                result=ExecutionResult(
                    status="COMPLETE",
                    output={"native_status": "EQUIVALENT_FOR_B_ONLY"},
                    evidence=(EvidenceRecord(
                        condition="native mathematical verification",
                        kind="native-replay",
                        source=factory_evidence.source,
                        ref=factory_evidence.ref,
                        depth=factory_evidence.depth,
                    ),),
                ),
            )
        self.assertEqual(len(self.runtime.event_store.all()), before)
        self.assertEqual(self.math.conclude("math-unknown").status, "UNKNOWN")

    def test_factory_completion_does_not_expand_mathematical_scope(self):
        self.math.submit(self.positive_at(27), handoff_id="overclaimed",
                         claim=AB_CONJUGATE)
        self.orchestrator.run_until_idle()
        self.assertEqual(self.factory.order(ORDER_ID).status, "complete")
        self.assertEqual(self.math.conclude("overclaimed").status, "BLOCKED")
        self.assertEqual(
            self.math.recover("overclaimed").output["native_status"],
            "EQUIVALENT_FOR_B_ONLY",
        )
        self.assertTrue(all(
            e["kind"] == "simulation" and e["depth"] == "simulated"
            for event in self.factory.events()
            if event["event_type"] == "HANDOFF_RECONCILED"
            for e in event["payload"]["evidence"]
        ))


if __name__ == "__main__":
    unittest.main()
