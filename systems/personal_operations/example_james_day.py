from __future__ import annotations

from pathlib import Path

from runtime import HandoffRuntime
from runtime.activation import ActivationRegistry, run_activation
from systems.personal_operations import Note, Plan, PersonalOperationsStore, TaskRecord


ROOT = Path(__file__).resolve().parents[2]


def demo():
    personal = PersonalOperationsStore()
    runtime = HandoffRuntime()

    # Context can be retained without silently becoming work.
    personal.add_note(
        Note.create(
            "The school monitor is part of the current ecosystem.",
            referent="Online School",
            actor_id="james",
        )
    )
    personal.add_plan(
        Plan.create(
            "Current movement",
            referent="James / current day",
            actor_id="james",
            steps=("school", "runtime", "repo"),
        )
    )

    # Only explicit tasks are admitted to the shared carrier.
    for title, referent in (
        ("Check Online School task monitor", "Online School"),
        ("Review handoff runtime", "Cross-Layer Handoff Runtime"),
        ("Inspect current repo movement", "Continuity Layer"),
    ):
        task = personal.add_task(
            TaskRecord.create(
                title,
                referent=referent,
                assignee="james",
            )
        )
        runtime.submit(personal.admit_task(task.task_id))

    registry = ActivationRegistry.from_json(ROOT / "activations" / "registry.json")
    route = registry.resolve("ohayo", actor_id="james")
    pairs = [
        (runtime.get(handoff_id), state)
        for handoff_id, state in runtime.snapshot().items()
    ]
    return personal, run_activation(route, surface="ohayo", handoffs=pairs)


if __name__ == "__main__":
    personal, result = demo()
    print(result.route.referent)
    print("notes:", len(personal.notes()))
    print("plans:", len(personal.plans()))
    print("tasks:", len(personal.tasks()))
    print("admitted queue:")
    for item in result.items:
        print(f"  [{item['status']}] {item['title']}")
