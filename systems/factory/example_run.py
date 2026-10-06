from __future__ import annotations

from runtime import HandoffRuntime
from systems.factory import FactorySystem, run_simulated_order


def demo():
    factory = FactorySystem()
    factory.create_order(
        order_id="ORDER-0001",
        product="demo-widget",
        quantity=10,
        material="demo-stock",
    )
    runtime = HandoffRuntime()
    trace = run_simulated_order(factory, runtime, "ORDER-0001")
    return factory, runtime, trace


if __name__ == "__main__":
    factory, runtime, trace = demo()
    print("running factory")
    for line in trace:
        print(" ", line)
    order = factory.order("ORDER-0001")
    print("order:", order.status)
    print("shipment:", order.local_state.get("shipment_state"))
    print("factory events:", len(factory.events()))
    print("runtime events:", len(runtime.event_store.all()))
