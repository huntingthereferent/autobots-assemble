from pathlib import Path
import unittest

from runtime import (
    EvidenceRecord,
    ExecutionResult,
    HandoffRuntime,
)
from runtime.activation import ActivationRegistry, run_activation
from runtime.orchestrator import Orchestrator
from systems.bindings import factory_binding, personal_operations_binding
from systems.factory import FactorySystem, default_simulated_actors
from systems.personal_operations import PersonalOperationsStore, TaskRecord


ROOT = Path(__file__).resolve().parents[2]


class OrchestratorTests(unittest.TestCase):
    def build_ecosystem(self):
        runtime = HandoffRuntime()
        orchestrator = Orchestrator(runtime)

        personal = PersonalOperationsStore()
        task = personal.add_task(
            TaskRecord.create(
                "Review current repo movement",
                referent="Continuity Layer",
                assignee="james",
            )
        )
        personal.admit_task(task.task_id)

        factory = FactorySystem()
        factory.create_order(
            order_id="ORDER-ORCH",
            product="demo-widget",
            quantity=10,
            material="demo-stock",
        )

        orchestrator.register_system(personal_operations_binding(personal))
        orchestrator.register_system(
            factory_binding(factory, order_ids=("ORDER-ORCH",))
        )
        for actor in default_simulated_actors().values():
            orchestrator.register_actor(actor)

        return orchestrator, personal, task, factory

    def test_orchestrator_runs_machine_work_and_leaves_human_work_ready(self):
        orchestrator, personal, task, factory = self.build_ecosystem()

        steps = orchestrator.run_until_idle()

        self.assertEqual(factory.order("ORDER-ORCH").status, "complete")
        self.assertEqual(
            factory.order("ORDER-ORCH").local_state["shipment_state"],
            "shipped",
        )

        handoff_id = personal.admitted_handoff_id(task.task_id)
        self.assertEqual(orchestrator.runtime.state(handoff_id).status, "READY")
        self.assertIsNone(personal.task_result(task.task_id))

        executed = [
            handoff_id
            for step in steps
            for handoff_id in step.executed
        ]
        self.assertEqual(len(executed), 5)

    def test_ohayo_projects_human_work_while_factory_finishes_in_background(self):
        orchestrator, personal, task, factory = self.build_ecosystem()
        orchestrator.run_until_idle()

        registry = ActivationRegistry.from_json(ROOT / "activations" / "registry.json")
        route = registry.resolve("ohayo", actor_id="james")
        pairs = [
            (orchestrator.runtime.get(handoff_id), state)
            for handoff_id, state in orchestrator.runtime.snapshot().items()
        ]
        result = run_activation(route, surface="ohayo", handoffs=pairs)

        self.assertEqual(
            [item["title"] for item in result.items],
            ["Review current repo movement"],
        )
        self.assertEqual(factory.order("ORDER-ORCH").status, "complete")

    def test_human_result_reconciles_to_origin_system(self):
        orchestrator, personal, task, _ = self.build_ecosystem()
        orchestrator.run_until_idle()

        handoff_id = personal.admitted_handoff_id(task.task_id)
        state = orchestrator.return_result(
            handoff_id,
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

        self.assertEqual(state.status, "COMPLETE")
        reconciled = personal.task_result(task.task_id)
        self.assertEqual(reconciled["status"], "COMPLETE")
        self.assertEqual(reconciled["output"], {"done": True})
        self.assertEqual(
            reconciled["evidence"][0]["kind"],
            "human_report",
        )

    def test_completed_human_task_disappears_from_ohayo(self):
        orchestrator, personal, task, _ = self.build_ecosystem()
        orchestrator.run_until_idle()

        handoff_id = personal.admitted_handoff_id(task.task_id)
        orchestrator.return_result(
            handoff_id,
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

        registry = ActivationRegistry.from_json(ROOT / "activations" / "registry.json")
        route = registry.resolve("ohayo", actor_id="james")
        result = run_activation(
            route,
            surface="ohayo",
            handoffs=[
                (orchestrator.runtime.get(hid), state)
                for hid, state in orchestrator.runtime.snapshot().items()
            ],
        )
        self.assertEqual(result.items, ())

    def test_orchestrator_does_not_duplicate_existing_handoff(self):
        orchestrator, personal, task, _ = self.build_ecosystem()

        first = orchestrator.step()
        handoff_id = personal.admitted_handoff_id(task.task_id)
        before = len(
            orchestrator.runtime.event_store.for_handoff(handoff_id)
        )

        second = orchestrator.step()
        after = len(
            orchestrator.runtime.event_store.for_handoff(handoff_id)
        )

        self.assertIn(handoff_id, first.submitted)
        self.assertNotIn(handoff_id, second.submitted)
        self.assertEqual(before, after)

    def test_system_result_history_replays(self):
        orchestrator, personal, task, factory = self.build_ecosystem()
        orchestrator.run_until_idle()

        # Factory received one create event, then emit+reconcile for each stage.
        self.assertEqual(len(factory.events()), 11)
        self.assertEqual(factory.events()[0]["event_type"], "ORDER_CREATED")
        self.assertEqual(factory.events()[-1]["event_type"], "HANDOFF_RECONCILED")

        # Personal Operations remains unresolved until the human returns.
        self.assertEqual(
            [event["event_type"] for event in personal.events()],
            ["TASK_ADDED", "TASK_ADMITTED"],
        )


if __name__ == "__main__":
    unittest.main()
