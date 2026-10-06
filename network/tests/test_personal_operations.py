from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime import HandoffRuntime
from runtime.activation import ActivationRegistry, run_activation
from systems.personal_operations import Note, Plan, PersonalOperationsStore, TaskRecord


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "activations" / "registry.json"


class PersonalOperationsTests(unittest.TestCase):
    def test_note_stays_note_and_does_not_emit_handoff(self):
        store = PersonalOperationsStore()
        note = store.add_note(
            Note.create(
                "Printer paper is getting low.",
                referent="household supplies",
                actor_id="james",
            )
        )

        self.assertEqual(store.note(note.note_id), note)
        self.assertEqual(store.tasks(), ())
        self.assertEqual(store.admitted_handoff_id(note.note_id), None)
        self.assertEqual([e["event_type"] for e in store.events()], ["NOTE_ADDED"])

    def test_plan_steps_do_not_become_tasks(self):
        store = PersonalOperationsStore()
        plan = store.add_plan(
            Plan.create(
                "Morning setup",
                referent="James / current day",
                actor_id="james",
                steps=("check school", "review repo", "look at blocked work"),
            )
        )

        self.assertEqual(store.plan(plan.plan_id), plan)
        self.assertEqual(store.tasks(), ())
        self.assertEqual([e["event_type"] for e in store.events()], ["PLAN_ADDED"])

    def test_unadmitted_task_stays_local(self):
        store = PersonalOperationsStore()
        task = store.add_task(
            TaskRecord.create(
                "Review repo movement",
                referent="repo / current movement",
                assignee="james",
            )
        )

        self.assertEqual(store.task(task.task_id), task)
        self.assertIsNone(store.admitted_handoff_id(task.task_id))
        self.assertEqual([e["event_type"] for e in store.events()], ["TASK_ADDED"])

    def test_explicit_task_admission_creates_shared_handoff(self):
        store = PersonalOperationsStore()
        task = store.add_task(
            TaskRecord.create(
                "Review repo movement",
                referent="repo / current movement",
                assignee="james",
                provenance=("conversation:explicit-task",),
            )
        )

        handoff = store.admit_task(task.task_id)

        self.assertEqual(handoff.to_actor, "james")
        self.assertEqual(handoff.metadata["title"], "Review repo movement")
        self.assertEqual(handoff.metadata["source_system"], "personal-operations")
        self.assertIn(f"personal-task:{task.task_id}", handoff.provenance)
        self.assertEqual(store.admitted_handoff_id(task.task_id), handoff.handoff_id)
        self.assertEqual(
            [e["event_type"] for e in store.events()],
            ["TASK_ADDED", "TASK_ADMITTED"],
        )

    def test_task_can_only_be_admitted_once(self):
        store = PersonalOperationsStore()
        task = store.add_task(
            TaskRecord.create(
                "One task",
                referent="James / current day",
                assignee="james",
            )
        )
        store.admit_task(task.task_id)

        with self.assertRaisesRegex(ValueError, "already admitted"):
            store.admit_task(task.task_id)

    def test_admitted_personal_task_flows_to_ohayo(self):
        store = PersonalOperationsStore()
        runtime = HandoffRuntime()

        note = store.add_note(
            Note.create(
                "Maybe inspect school output later.",
                referent="Online School",
                actor_id="james",
            )
        )
        plan = store.add_plan(
            Plan.create(
                "Repo morning",
                referent="James / current day",
                actor_id="james",
                steps=("review runtime",),
            )
        )
        local_only = store.add_task(
            TaskRecord.create(
                "Local but not admitted",
                referent="private local task",
                assignee="james",
            )
        )
        admitted = store.add_task(
            TaskRecord.create(
                "Review handoff runtime",
                referent="runtime / current movement",
                assignee="james",
            )
        )

        handoff = store.admit_task(admitted.task_id)
        runtime.submit(handoff)

        registry = ActivationRegistry.from_json(REGISTRY_PATH)
        route = registry.resolve("ohayo", actor_id="james")
        result = run_activation(
            route,
            surface="ohayo",
            handoffs=[(handoff, runtime.state(handoff.handoff_id))],
        )

        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0]["title"], "Review handoff runtime")
        self.assertNotEqual(local_only.task_id, admitted.task_id)
        self.assertEqual(store.note(note.note_id), note)
        self.assertEqual(store.plan(plan.plan_id), plan)

    def test_jsonl_persistence_replays_distinct_records_and_admission(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "personal-ops.jsonl"
            store = PersonalOperationsStore(path)
            note = store.add_note(
                Note.create("Remember this.", referent="test", actor_id="james")
            )
            plan = store.add_plan(
                Plan.create(
                    "Test plan",
                    referent="test",
                    actor_id="james",
                    steps=("one", "two"),
                )
            )
            task = store.add_task(
                TaskRecord.create(
                    "Test task",
                    referent="test",
                    assignee="james",
                )
            )
            handoff = store.admit_task(task.task_id)

            reloaded = PersonalOperationsStore(path)

            self.assertEqual(reloaded.note(note.note_id).body, "Remember this.")
            self.assertEqual(reloaded.plan(plan.plan_id).steps, ("one", "two"))
            self.assertEqual(reloaded.task(task.task_id).title, "Test task")
            self.assertEqual(
                reloaded.admitted_handoff_id(task.task_id),
                handoff.handoff_id,
            )
            self.assertEqual(len(reloaded.events()), 4)


if __name__ == "__main__":
    unittest.main()
