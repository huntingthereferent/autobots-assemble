from __future__ import annotations

from pathlib import Path
import importlib.util

from runtime import HandoffRuntime
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
    "full_ecosystem_engine",
    APP / "schedule_engine.py",
)
engine = importlib.util.module_from_spec(engine_spec)
engine_spec.loader.exec_module(engine)

adapter_spec = importlib.util.spec_from_file_location(
    "full_ecosystem_adapter",
    APP / "handoff_adapter.py",
)
school_adapter = importlib.util.module_from_spec(adapter_spec)
adapter_spec.loader.exec_module(school_adapter)


def demo():
    runtime = HandoffRuntime()
    orchestrator = Orchestrator(runtime)

    personal = PersonalOperationsStore()
    task = personal.add_task(
        TaskRecord.create(
            "Review current repo movement",
            referent="Language Network",
            assignee="james",
        )
    )
    personal.admit_task(task.task_id)

    school_tasks = {
        task["id"]: dict(task)
        for task in engine.generate_tasks_for_day("2026-10-05")
    }

    def school_provider():
        return tuple(school_tasks.values())

    def school_patch(task_id, state):
        patch = school_adapter.task_patch_from_handoff_state(state)
        school_tasks[task_id] = {**school_tasks[task_id], **patch}

    factory = FactorySystem()
    factory.create_order(
        order_id="ORDER-FULL",
        product="demo-widget",
        quantity=10,
        material="demo-stock",
    )

    orchestrator.register_system(personal_operations_binding(personal))
    orchestrator.register_system(
        online_school_binding(
            task_provider=school_provider,
            task_to_handoff=school_adapter.task_to_handoff,
            apply_patch=school_patch,
        )
    )
    orchestrator.register_system(
        factory_binding(factory, order_ids=("ORDER-FULL",))
    )
    for actor in default_simulated_actors().values():
        orchestrator.register_actor(actor)

    steps = orchestrator.run_until_idle()

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
    return orchestrator, school_tasks, factory, steps, result


if __name__ == "__main__":
    orchestrator, school_tasks, factory, steps, result = demo()

    print("systems: personal-operations + online-school + factory")
    print("factory:", factory.order("ORDER-FULL").status)
    print("school tasks:", len(school_tasks))
    print("runtime handoffs:", len(orchestrator.runtime.snapshot()))
    print("orchestration steps:", len(steps))
    print("ohayo:")
    for item in result.items:
        source = orchestrator.runtime.get(item["id"]).metadata.get("source_system")
        print(f"  [{item['status']}] {item['title']} <- {source}")
