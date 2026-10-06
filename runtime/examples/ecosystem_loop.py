from __future__ import annotations

from pathlib import Path

from runtime import HandoffRuntime
from runtime.activation import ActivationRegistry, run_activation
from runtime.orchestrator import Orchestrator
from systems.bindings import factory_binding, personal_operations_binding
from systems.factory import FactorySystem, default_simulated_actors
from systems.personal_operations import PersonalOperationsStore, TaskRecord


ROOT = Path(__file__).resolve().parents[2]


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

    factory = FactorySystem()
    factory.create_order(
        order_id="ORDER-0002",
        product="demo-widget",
        quantity=10,
        material="demo-stock",
    )

    orchestrator.register_system(personal_operations_binding(personal))
    orchestrator.register_system(factory_binding(factory, order_ids=("ORDER-0002",)))
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

    return orchestrator, personal, factory, steps, result


if __name__ == "__main__":
    orchestrator, personal, factory, steps, result = demo()

    print("ecosystem idle")
    print("factory:", factory.order("ORDER-0002").status)
    print("factory shipment:", factory.order("ORDER-0002").local_state.get("shipment_state"))
    print("orchestration steps:", len(steps))
    print("ohayo:")
    for item in result.items:
        source = orchestrator.runtime.get(item["id"]).metadata.get("source_system")
        print(f"  [{item['status']}] {item['title']} <- {source}")
