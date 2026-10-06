from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from runtime import HandoffRuntime
from runtime.journal import RuntimeJournal
from runtime.orchestrator import Orchestrator
from systems.bindings import factory_binding
from systems.factory import FactorySystem, default_simulated_actors


def demo():
    tmp = TemporaryDirectory()
    root = Path(tmp.name)
    factory_path = root / "factory.jsonl"
    runtime_path = root / "runtime.jsonl"

    factory = FactorySystem(factory_path)
    factory.create_order(
        order_id="ORDER-RESTART",
        product="demo-widget",
        quantity=10,
        material="demo-stock",
    )

    actors = default_simulated_actors()
    runtime = HandoffRuntime(
        event_store=RuntimeJournal(runtime_path)
    )

    # Emit + execute supply, but intentionally do not reconcile it to factory.
    supply = factory.next_handoff("ORDER-RESTART")
    runtime.submit(supply)
    runtime.run(supply.handoff_id, actors[supply.to_actor])

    print("crash window:")
    print(" runtime:", runtime.state(supply.handoff_id).status)
    print(" factory pending:", factory.order("ORDER-RESTART").pending_handoff_id)

    # Simulated process restart.
    factory = FactorySystem(factory_path)
    runtime = HandoffRuntime(
        event_store=RuntimeJournal(runtime_path)
    )
    orchestrator = Orchestrator(runtime)
    orchestrator.register_system(
        factory_binding(factory, order_ids=("ORDER-RESTART",))
    )
    for actor in actors.values():
        orchestrator.register_actor(actor)

    recovery = orchestrator.step()
    print("recovered without re-execution:", recovery.reconciled)
    orchestrator.run_until_idle()

    order = factory.order("ORDER-RESTART")
    print("final order:", order.status)
    print("shipment:", order.local_state.get("shipment_state"))
    print("handoffs:", len(runtime.snapshot()))

    return tmp


if __name__ == "__main__":
    _keepalive = demo()
