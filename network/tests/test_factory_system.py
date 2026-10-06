from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime import EvidenceRecord, ExecutionResult, HandoffRuntime
from systems.factory import FactorySystem, default_simulated_actors, run_simulated_order


class FactorySystemTests(unittest.TestCase):
    def make_factory(self):
        factory = FactorySystem()
        factory.create_order(
            order_id="ORDER-TEST",
            product="demo-widget",
            quantity=10,
            material="demo-stock",
        )
        return factory

    def test_first_handoff_is_generated_from_order_state(self):
        factory = self.make_factory()
        handoff = factory.next_handoff("ORDER-TEST")

        self.assertEqual(handoff.metadata["stage"], "supply")
        self.assertEqual(handoff.required_relation, "supply material")
        self.assertEqual(handoff.inputs["quantity"], 10)
        self.assertEqual(handoff.inputs["material"], "demo-stock")
        self.assertEqual(
            factory.order("ORDER-TEST").pending_handoff_id,
            handoff.handoff_id,
        )

    def test_factory_cannot_emit_next_stage_before_reconciliation(self):
        factory = self.make_factory()
        first = factory.next_handoff("ORDER-TEST")

        with self.assertRaisesRegex(ValueError, "awaiting"):
            factory.next_handoff("ORDER-TEST")

        self.assertEqual(factory.order("ORDER-TEST").stage_index, 0)
        self.assertEqual(factory.order("ORDER-TEST").pending_handoff_id, first.handoff_id)

    def test_reconciled_output_becomes_next_stage_input(self):
        factory = self.make_factory()
        runtime = HandoffRuntime()
        actors = default_simulated_actors()

        supply = factory.next_handoff("ORDER-TEST")
        runtime.submit(supply)
        supply_state = runtime.run(supply.handoff_id, actors[supply.to_actor])
        factory.reconcile("ORDER-TEST", handoff=supply, state=supply_state)

        machine = factory.next_handoff("ORDER-TEST")

        self.assertEqual(machine.metadata["stage"], "machine")
        self.assertEqual(machine.inputs["material_state"], "received")
        self.assertEqual(machine.inputs["quantity"], 10)

    def test_noncomplete_result_does_not_advance_stage(self):
        factory = self.make_factory()
        runtime = HandoffRuntime()

        supply = factory.next_handoff("ORDER-TEST")
        runtime.submit(supply)
        state = runtime.return_result(
            supply.handoff_id,
            actor_id=supply.to_actor,
            result=ExecutionResult(
                status="BLOCKED",
                output={},
                note="supplier unavailable",
            ),
        )
        order = factory.reconcile("ORDER-TEST", handoff=supply, state=state)

        self.assertEqual(order.stage_index, 0)
        self.assertEqual(order.status, "blocked")
        self.assertEqual(order.pending_handoff_id, "")

        retry = factory.next_handoff("ORDER-TEST")
        self.assertEqual(retry.metadata["stage"], "supply")

    def test_running_factory_reaches_shipping_from_changed_state(self):
        factory = self.make_factory()
        runtime = HandoffRuntime()

        trace = run_simulated_order(factory, runtime, "ORDER-TEST")
        order = factory.order("ORDER-TEST")

        self.assertEqual(
            trace,
            [
                "supply:COMPLETE",
                "machine:COMPLETE",
                "inspect:COMPLETE",
                "assemble:COMPLETE",
                "ship:COMPLETE",
            ],
        )
        self.assertEqual(order.status, "complete")
        self.assertEqual(order.stage_index, 5)
        self.assertEqual(order.local_state["shipment_state"], "shipped")
        self.assertEqual(order.local_state["quantity"], 10)

    def test_factory_reconciliation_preserves_simulation_evidence(self):
        factory = self.make_factory()
        runtime = HandoffRuntime()

        run_simulated_order(factory, runtime, "ORDER-TEST")

        reconciled = [
            event for event in factory.events()
            if event["event_type"] == "HANDOFF_RECONCILED"
        ]
        self.assertEqual(len(reconciled), 5)
        self.assertTrue(
            all(
                evidence["kind"] == "simulation"
                and evidence["depth"] == "simulated"
                for event in reconciled
                for evidence in event["payload"]["evidence"]
            )
        )

    def test_factory_event_history_is_append_only_and_replayable(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "factory.jsonl"
            factory = FactorySystem(path)
            factory.create_order(
                order_id="ORDER-PERSIST",
                product="demo-widget",
                quantity=3,
                material="stock",
            )
            runtime = HandoffRuntime()
            actors = default_simulated_actors()

            first = factory.next_handoff("ORDER-PERSIST")
            runtime.submit(first)
            state = runtime.run(first.handoff_id, actors[first.to_actor])
            factory.reconcile("ORDER-PERSIST", handoff=first, state=state)

            before = factory.events()
            reloaded = FactorySystem(path)

            self.assertEqual(reloaded.events(), before)
            order = reloaded.order("ORDER-PERSIST")
            self.assertEqual(order.stage_index, 1)
            self.assertEqual(order.local_state["material_state"], "received")

    def test_simulation_boundary_survives_every_emitted_handoff(self):
        factory = self.make_factory()
        runtime = HandoffRuntime()
        actors = default_simulated_actors()

        seen = []
        while factory.order("ORDER-TEST").status != "complete":
            handoff = factory.next_handoff("ORDER-TEST")
            seen.append(handoff)
            runtime.submit(handoff)
            state = runtime.run(handoff.handoff_id, actors[handoff.to_actor])
            factory.reconcile("ORDER-TEST", handoff=handoff, state=state)

        self.assertEqual(len(seen), 5)
        for handoff in seen:
            self.assertIn(
                "Simulation evidence must remain marked simulated.",
                handoff.boundaries,
            )


if __name__ == "__main__":
    unittest.main()
