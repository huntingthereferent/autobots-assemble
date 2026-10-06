from pathlib import Path
import importlib.util
import unittest

from runtime import EvidenceRecord, ExecutionResult, HandoffRuntime
from runtime.activation import ActivationRegistry, run_activation
from runtime.orchestrator import Orchestrator
from systems.bindings import (
    factory_binding,
    online_school_binding,
    personal_operations_binding,
)
from systems.factory import FactorySystem, default_simulated_actors
from systems.personal_operations import PersonalOperationsStore, TaskRecord


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "companies" / "online-school" / "app"

engine_spec = importlib.util.spec_from_file_location(
    "full_ecosystem_school_engine",
    APP / "schedule_engine.py",
)
engine = importlib.util.module_from_spec(engine_spec)
engine_spec.loader.exec_module(engine)

adapter_spec = importlib.util.spec_from_file_location(
    "full_ecosystem_school_adapter",
    APP / "handoff_adapter.py",
)
school_adapter = importlib.util.module_from_spec(adapter_spec)
adapter_spec.loader.exec_module(school_adapter)


class EcosystemOrchestratorTests(unittest.TestCase):
    def build(self):
        runtime = HandoffRuntime()
        orchestrator = Orchestrator(runtime)

        personal = PersonalOperationsStore()
        personal_task = personal.add_task(
            TaskRecord.create(
                "Review current repo movement",
                referent="Language Network",
                assignee="james",
            )
        )
        personal.admit_task(personal_task.task_id)

        generated = engine.generate_tasks_for_day("2026-10-05")
        school_tasks = {task["id"]: dict(task) for task in generated}

        def provider():
            return tuple(school_tasks.values())

        def apply_school_patch(task_id, state):
            patch = school_adapter.task_patch_from_handoff_state(state)
            school_tasks[task_id] = {**school_tasks[task_id], **patch}

        factory = FactorySystem()
        factory.create_order(
            order_id="ORDER-ECO",
            product="demo-widget",
            quantity=10,
            material="demo-stock",
        )

        orchestrator.register_system(personal_operations_binding(personal))
        orchestrator.register_system(
            online_school_binding(
                task_provider=provider,
                task_to_handoff=school_adapter.task_to_handoff,
                apply_patch=apply_school_patch,
            )
        )
        orchestrator.register_system(
            factory_binding(factory, order_ids=("ORDER-ECO",))
        )

        for actor in default_simulated_actors().values():
            orchestrator.register_actor(actor)

        return (
            orchestrator,
            personal,
            personal_task,
            school_tasks,
            factory,
        )

    def ohayo(self, orchestrator):
        registry = ActivationRegistry.from_json(ROOT / "activations" / "registry.json")
        route = registry.resolve("ohayo", actor_id="james")
        return run_activation(
            route,
            surface="ohayo",
            handoffs=[
                (orchestrator.runtime.get(handoff_id), state)
                for handoff_id, state in orchestrator.runtime.snapshot().items()
            ],
        )

    def test_three_systems_coexist_without_shared_local_schema(self):
        orchestrator, personal, personal_task, school_tasks, factory = self.build()
        orchestrator.run_until_idle()

        self.assertEqual(factory.order("ORDER-ECO").status, "complete")
        self.assertEqual(len(school_tasks), 11)
        self.assertEqual(len(personal.tasks()), 1)

        source_systems = {
            handoff.metadata.get("source_system")
            for handoff_id in orchestrator.runtime.snapshot()
            for handoff in (orchestrator.runtime.get(handoff_id),)
            if handoff.metadata.get("source_system")
        }
        self.assertIn("personal-operations", source_systems)
        self.assertIn("online-school", source_systems)

    def test_ohayo_compresses_cross_system_state_to_james(self):
        orchestrator, _, _, _, factory = self.build()
        orchestrator.run_until_idle()

        result = self.ohayo(orchestrator)

        self.assertEqual(
            {item["title"] for item in result.items},
            {"Review current repo movement", "guided reading"},
        )
        self.assertEqual(factory.order("ORDER-ECO").status, "complete")

        source_systems = {
            orchestrator.runtime.get(item["id"]).metadata["source_system"]
            for item in result.items
        }
        self.assertEqual(
            source_systems,
            {"personal-operations", "online-school"},
        )

    def test_school_human_return_reconciles_into_school_local_state(self):
        orchestrator, _, _, school_tasks, _ = self.build()
        orchestrator.run_until_idle()

        guided = next(
            task for task in school_tasks.values()
            if task["title"] == "guided reading"
        )
        handoff_id = f"school-{guided['id']}"

        orchestrator.return_result(
            handoff_id,
            actor_id="james",
            result=ExecutionResult(
                status="COMPLETE",
                output={"task_status": "done"},
                evidence=(
                    EvidenceRecord(
                        condition="school task disposition reported",
                        kind="human_report",
                        source="james",
                        depth="reported",
                    ),
                ),
            ),
        )

        self.assertEqual(school_tasks[guided["id"]]["status"], "done")
        result = self.ohayo(orchestrator)
        self.assertEqual(
            [item["title"] for item in result.items],
            ["Review current repo movement"],
        )

    def test_all_james_returns_can_clear_ohayo_without_touching_other_school_work(self):
        orchestrator, personal, personal_task, school_tasks, _ = self.build()
        orchestrator.run_until_idle()

        guided = next(
            task for task in school_tasks.values()
            if task["title"] == "guided reading"
        )
        school_handoff_id = f"school-{guided['id']}"
        personal_handoff_id = personal.admitted_handoff_id(personal_task.task_id)

        orchestrator.return_result(
            school_handoff_id,
            actor_id="james",
            result=ExecutionResult(
                status="COMPLETE",
                evidence=(
                    EvidenceRecord(
                        condition="school task disposition reported",
                        kind="human_report",
                        source="james",
                    ),
                ),
            ),
        )
        orchestrator.return_result(
            personal_handoff_id,
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

        self.assertEqual(self.ohayo(orchestrator).items, ())

        incomplete_school = [
            task for task in school_tasks.values()
            if task["status"] != "done"
        ]
        self.assertEqual(len(incomplete_school), 10)

    def test_factory_does_not_need_school_or_personal_completion_to_run(self):
        orchestrator, _, _, _, factory = self.build()
        orchestrator.run_until_idle()

        self.assertEqual(factory.order("ORDER-ECO").status, "complete")

        human_ready = [
            state
            for handoff_id, state in orchestrator.runtime.snapshot().items()
            if orchestrator.runtime.get(handoff_id).to_actor in {
                "james",
                "track_a",
                "track_b",
                "online-school:shared",
            }
            and state.status == "READY"
        ]
        self.assertGreaterEqual(len(human_ready), 1)


if __name__ == "__main__":
    unittest.main()
