from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime import (
    EvidenceRecord,
    ExecutionResult,
    HandoffRuntime,
)
from runtime.activation import ActivationRegistry, run_activation
from runtime.journal import RuntimeJournal
from runtime.orchestrator import Orchestrator
from systems.bindings import factory_binding, personal_operations_binding
from systems.factory import FactorySystem, default_simulated_actors
from systems.personal_operations import PersonalOperationsStore, TaskRecord


ROOT = Path(__file__).resolve().parents[2]


class RecoveryTests(unittest.TestCase):
    def test_runtime_journal_restores_handoff_contract_and_state(self):
        with TemporaryDirectory() as tmp:
            journal_path = Path(tmp) / "runtime.jsonl"

            from runtime import Handoff
            handoff = Handoff(
                handoff_id="recover-one",
                referent="recoverable work",
                from_actor="source",
                to_actor="james",
                required_relation="move task",
                required_witnesses=("task disposition reported",),
                admissible_evidence={
                    "task disposition reported": ("human_report",),
                },
                provenance=("source:test",),
                metadata={"title": "Recover me"},
            )

            runtime = HandoffRuntime(
                event_store=RuntimeJournal(journal_path)
            )
            runtime.submit(handoff)
            runtime.return_result(
                handoff.handoff_id,
                actor_id="james",
                result=ExecutionResult(
                    status="COMPLETE",
                    output={"done": True},
                    evidence=(
                        EvidenceRecord(
                            condition="task disposition reported",
                            kind="human_report",
                            source="james",
                            depth="reported",
                        ),
                    ),
                ),
            )

            restored = HandoffRuntime(
                event_store=RuntimeJournal(journal_path)
            )

            self.assertEqual(
                restored.get("recover-one").required_relation,
                "move task",
            )
            self.assertEqual(
                restored.get("recover-one").provenance,
                ("source:test",),
            )
            self.assertEqual(
                restored.state("recover-one").status,
                "COMPLETE",
            )
            self.assertEqual(
                restored.state("recover-one").output,
                {"done": True},
            )

    def test_ready_human_handoff_survives_restart_and_ohayo(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            personal_path = root / "personal.jsonl"
            runtime_path = root / "runtime.jsonl"

            personal = PersonalOperationsStore(personal_path)
            task = personal.add_task(
                TaskRecord.create(
                    "Restart-safe James task",
                    referent="James / current day",
                    assignee="james",
                )
            )
            personal.admit_task(task.task_id)

            runtime = HandoffRuntime(
                event_store=RuntimeJournal(runtime_path)
            )
            first = Orchestrator(runtime)
            first.register_system(personal_operations_binding(personal))
            first.step()

            handoff_id = personal.admitted_handoff_id(task.task_id)
            self.assertEqual(runtime.state(handoff_id).status, "READY")

            # New process objects.
            personal2 = PersonalOperationsStore(personal_path)
            runtime2 = HandoffRuntime(
                event_store=RuntimeJournal(runtime_path)
            )
            second = Orchestrator(runtime2)
            second.register_system(personal_operations_binding(personal2))
            step = second.step()

            self.assertIn(handoff_id, step.waiting_for_actor)
            self.assertNotIn(handoff_id, step.submitted)

            registry = ActivationRegistry.from_json(
                ROOT / "activations" / "registry.json"
            )
            route = registry.resolve("ohayo", actor_id="james")
            result = run_activation(
                route,
                surface="ohayo",
                handoffs=[
                    (runtime2.get(hid), state)
                    for hid, state in runtime2.snapshot().items()
                ],
            )
            self.assertEqual(
                [item["title"] for item in result.items],
                ["Restart-safe James task"],
            )

    def test_human_result_before_origin_reconcile_is_recovered(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            personal_path = root / "personal.jsonl"
            runtime_path = root / "runtime.jsonl"

            personal = PersonalOperationsStore(personal_path)
            task = personal.add_task(
                TaskRecord.create(
                    "Crash-window human task",
                    referent="James / current day",
                    assignee="james",
                )
            )
            handoff = personal.admit_task(task.task_id)

            runtime = HandoffRuntime(
                event_store=RuntimeJournal(runtime_path)
            )
            runtime.submit(handoff)

            # Result reaches durable runtime, then process dies before the
            # origin system receives reconcile_task_result().
            runtime.return_result(
                handoff.handoff_id,
                actor_id="james",
                result=ExecutionResult(
                    status="COMPLETE",
                    evidence=(
                        EvidenceRecord(
                            condition="task disposition reported",
                            kind="human_report",
                            source="james",
                        ),
                    ),
                ),
            )
            self.assertIsNone(personal.task_result(task.task_id))

            personal2 = PersonalOperationsStore(personal_path)
            runtime2 = HandoffRuntime(
                event_store=RuntimeJournal(runtime_path)
            )
            second = Orchestrator(runtime2)
            second.register_system(personal_operations_binding(personal2))
            step = second.step()

            self.assertIn(handoff.handoff_id, step.reconciled)
            self.assertEqual(
                personal2.task_result(task.task_id)["status"],
                "COMPLETE",
            )

    def test_factory_result_before_reconcile_is_not_executed_twice(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            factory_path = root / "factory.jsonl"
            runtime_path = root / "runtime.jsonl"

            factory = FactorySystem(factory_path)
            factory.create_order(
                order_id="ORDER-RECOVER",
                product="demo-widget",
                quantity=10,
                material="demo-stock",
            )

            runtime = HandoffRuntime(
                event_store=RuntimeJournal(runtime_path)
            )
            actors = default_simulated_actors()

            supply = factory.next_handoff("ORDER-RECOVER")
            runtime.submit(supply)
            supply_state = runtime.run(
                supply.handoff_id,
                actors[supply.to_actor],
            )
            self.assertEqual(supply_state.status, "COMPLETE")

            # Crash before factory.reconcile(...).
            factory2 = FactorySystem(factory_path)
            runtime2 = HandoffRuntime(
                event_store=RuntimeJournal(runtime_path)
            )
            before_supply_events = len(
                runtime2.event_store.for_handoff(supply.handoff_id)
            )

            orchestrator = Orchestrator(runtime2)
            orchestrator.register_system(
                factory_binding(
                    factory2,
                    order_ids=("ORDER-RECOVER",),
                )
            )
            for actor in actors.values():
                orchestrator.register_actor(actor)

            recovered = orchestrator.step()

            self.assertIn(supply.handoff_id, recovered.reconciled)
            self.assertNotIn(supply.handoff_id, recovered.executed)
            self.assertEqual(
                len(runtime2.event_store.for_handoff(supply.handoff_id)),
                before_supply_events,
            )
            self.assertEqual(
                factory2.order("ORDER-RECOVER").stage_index,
                1,
            )

            orchestrator.run_until_idle()
            final = factory2.order("ORDER-RECOVER")
            self.assertEqual(final.status, "complete")
            self.assertEqual(
                final.local_state["shipment_state"],
                "shipped",
            )

            supply_emissions = [
                event for event in factory2.events()
                if event["event_type"] == "HANDOFF_EMITTED"
                and event["payload"]["handoff_id"] == supply.handoff_id
            ]
            self.assertEqual(len(supply_emissions), 1)

    def test_mid_factory_restart_continues_from_correct_stage(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            factory_path = root / "factory.jsonl"
            runtime_path = root / "runtime.jsonl"

            factory = FactorySystem(factory_path)
            factory.create_order(
                order_id="ORDER-MID",
                product="demo-widget",
                quantity=4,
                material="demo-stock",
            )
            runtime = HandoffRuntime(
                event_store=RuntimeJournal(runtime_path)
            )
            orchestrator = Orchestrator(runtime)
            orchestrator.register_system(
                factory_binding(factory, order_ids=("ORDER-MID",))
            )
            actors = default_simulated_actors()
            for actor in actors.values():
                orchestrator.register_actor(actor)

            # One step executes supply and reconciles it. Next stage has not
            # yet been emitted.
            first = orchestrator.step()
            self.assertEqual(len(first.executed), 1)
            self.assertEqual(
                factory.order("ORDER-MID").stage_index,
                1,
            )

            factory2 = FactorySystem(factory_path)
            runtime2 = HandoffRuntime(
                event_store=RuntimeJournal(runtime_path)
            )
            second = Orchestrator(runtime2)
            second.register_system(
                factory_binding(factory2, order_ids=("ORDER-MID",))
            )
            for actor in actors.values():
                second.register_actor(actor)

            second.run_until_idle()

            self.assertEqual(
                factory2.order("ORDER-MID").status,
                "complete",
            )
            handoff_ids = list(runtime2.snapshot())
            self.assertEqual(len(handoff_ids), 5)
            self.assertEqual(len(set(handoff_ids)), 5)


if __name__ == "__main__":
    unittest.main()
