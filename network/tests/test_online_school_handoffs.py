from pathlib import Path
import importlib.util
import unittest

from runtime import EvidenceRecord, ExecutionResult, HandoffRuntime
from runtime.activation import ActivationRegistry, run_activation
from systems.personal_operations import PersonalOperationsStore, TaskRecord


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "companies" / "online-school" / "app"

engine_spec = importlib.util.spec_from_file_location(
    "online_school_schedule_engine_handoffs",
    APP / "schedule_engine.py",
)
engine = importlib.util.module_from_spec(engine_spec)
engine_spec.loader.exec_module(engine)

adapter_spec = importlib.util.spec_from_file_location(
    "online_school_handoff_adapter",
    APP / "handoff_adapter.py",
)
adapter = importlib.util.module_from_spec(adapter_spec)
adapter_spec.loader.exec_module(adapter)


class OnlineSchoolHandoffTests(unittest.TestCase):
    def test_schedule_metadata_preserves_responsible_actor(self):
        tasks = engine.generate_tasks_for_day("2026-10-05")
        guided = next(task for task in tasks if task["title"] == "guided reading")
        self.assertEqual(guided["meta"]["responsible_actor"], "james")

    def test_guided_reading_emits_handoff_to_james(self):
        tasks = engine.generate_tasks_for_day("2026-10-05")
        guided = next(task for task in tasks if task["title"] == "guided reading")
        handoff = adapter.task_to_handoff(guided)

        self.assertEqual(handoff.to_actor, "james")
        self.assertEqual(handoff.required_relation, "complete school task")
        self.assertEqual(handoff.metadata["source_system"], "online-school")
        self.assertIn(f"online-school-task:{guided['id']}", handoff.provenance)

    def test_other_school_tasks_keep_school_local_actor_shape(self):
        tasks = engine.generate_tasks_for_day("2026-10-05")

        reading = next(task for task in tasks if task["title"] == "independent reading")
        math = next(task for task in tasks if task["title"] == "mathematics")

        reading_handoff = adapter.task_to_handoff(reading)
        math_handoff = adapter.task_to_handoff(math)

        self.assertEqual(reading_handoff.to_actor, "track_a")
        self.assertEqual(math_handoff.to_actor, "online-school:shared")

    def test_personal_and_school_handoffs_join_under_ohayo(self):
        runtime = HandoffRuntime()

        personal = PersonalOperationsStore()
        task = personal.add_task(
            TaskRecord.create(
                "Review repo movement",
                referent="Language Network",
                assignee="james",
            )
        )
        personal_handoff = personal.admit_task(task.task_id)
        runtime.submit(personal_handoff)

        school_tasks = engine.generate_tasks_for_day("2026-10-05")
        guided = next(task for task in school_tasks if task["title"] == "guided reading")
        school_handoff = adapter.task_to_handoff(guided)
        runtime.submit(school_handoff)

        unrelated = adapter.task_to_handoff(
            next(task for task in school_tasks if task["title"] == "independent reading")
        )
        runtime.submit(unrelated)

        registry = ActivationRegistry.from_json(ROOT / "activations" / "registry.json")
        route = registry.resolve("ohayo", actor_id="james")
        pairs = [
            (runtime.get(handoff_id), state)
            for handoff_id, state in runtime.snapshot().items()
        ]
        result = run_activation(route, surface="ohayo", handoffs=pairs)

        self.assertEqual(
            {item["title"] for item in result.items},
            {"Review repo movement", "guided reading"},
        )
        self.assertEqual(
            {runtime.get(item["id"]).metadata["source_system"] for item in result.items},
            {"personal-operations", "online-school"},
        )

    def test_handoff_completion_translates_back_to_school_patch(self):
        tasks = engine.generate_tasks_for_day("2026-10-05")
        guided = next(task for task in tasks if task["title"] == "guided reading")
        handoff = adapter.task_to_handoff(guided)

        runtime = HandoffRuntime()
        runtime.submit(handoff)
        state = runtime.return_result(
            handoff.handoff_id,
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

        self.assertEqual(adapter.task_patch_from_handoff_state(state), {"status": "done"})

    def test_school_completion_does_not_claim_mastery(self):
        task = next(
            task for task in engine.generate_tasks_for_day("2026-10-05")
            if task["title"] == "guided reading"
        )
        handoff = adapter.task_to_handoff(task)
        boundary = " ".join(handoff.boundaries).lower()
        self.assertIn("does not by itself establish mastery", boundary)


if __name__ == "__main__":
    unittest.main()
