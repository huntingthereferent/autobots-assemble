from __future__ import annotations

from pathlib import Path
import importlib.util

from runtime import HandoffRuntime
from runtime.activation import ActivationRegistry, run_activation
from systems.personal_operations import PersonalOperationsStore, TaskRecord


ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "companies" / "online-school" / "app"

engine_spec = importlib.util.spec_from_file_location("school_engine_cross_system", APP / "schedule_engine.py")
engine = importlib.util.module_from_spec(engine_spec)
engine_spec.loader.exec_module(engine)

adapter_spec = importlib.util.spec_from_file_location("school_adapter_cross_system", APP / "handoff_adapter.py")
adapter = importlib.util.module_from_spec(adapter_spec)
adapter_spec.loader.exec_module(adapter)


def demo():
    runtime = HandoffRuntime()

    personal = PersonalOperationsStore()
    personal_task = personal.add_task(
        TaskRecord.create(
            "Review current repo movement",
            referent="Language Network",
            assignee="james",
        )
    )
    runtime.submit(personal.admit_task(personal_task.task_id))

    for school_task in engine.generate_tasks_for_day("2026-10-05"):
        runtime.submit(adapter.task_to_handoff(school_task))

    registry = ActivationRegistry.from_json(ROOT / "activations" / "registry.json")
    route = registry.resolve("ohayo", actor_id="james")
    result = run_activation(
        route,
        surface="ohayo",
        handoffs=[
            (runtime.get(handoff_id), state)
            for handoff_id, state in runtime.snapshot().items()
        ],
    )
    return runtime, result


if __name__ == "__main__":
    runtime, result = demo()
    print(result.route.referent)
    for item in result.items:
        source = runtime.get(item["id"]).metadata.get("source_system")
        print(f"[{item['status']}] {item['title']} <- {source}")
