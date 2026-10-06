from __future__ import annotations

from runtime import (
    EvidenceRecord,
    ExecutionResult,
    Handoff,
    HandoffRuntime,
    SimulatedActor,
)


def actor(actor_id: str, relation: str, witness: str, output_fn):
    def handler(handoff: Handoff) -> ExecutionResult:
        return ExecutionResult(
            status="COMPLETE",
            output=output_fn(handoff.inputs),
            evidence=(
                EvidenceRecord(
                    condition=witness,
                    kind="simulation",
                    source=actor_id,
                    ref=f"sim:{handoff.handoff_id}",
                    note="Produced by the tiny-factory simulator.",
                    depth="simulated",
                ),
            ),
        )

    return SimulatedActor(
        actor_id=actor_id,
        capabilities=(relation,),
        handler=handler,
    )


ACTORS = {
    "supplier-sim": actor(
        "supplier-sim",
        "supply material",
        "material supplied",
        lambda inputs: {
            "material": inputs["material"],
            "quantity": inputs["quantity"],
            "state": "received",
        },
    ),
    "machine-sim": actor(
        "machine-sim",
        "machine feature",
        "machining operation completed",
        lambda inputs: {
            "part": inputs["part"],
            "quantity": inputs["quantity"],
            "state": "machined",
        },
    ),
    "inspection-sim": actor(
        "inspection-sim",
        "inspect output",
        "inspection completed",
        lambda inputs: {
            "part": inputs["part"],
            "quantity": inputs["quantity"],
            "accepted": inputs["quantity"],
            "rejected": 0,
            "state": "inspected",
        },
    ),
    "assembly-sim": actor(
        "assembly-sim",
        "assemble product",
        "assembly completed",
        lambda inputs: {
            "product": inputs["product"],
            "quantity": inputs["quantity"],
            "state": "assembled",
        },
    ),
    "shipping-sim": actor(
        "shipping-sim",
        "ship product",
        "shipment recorded",
        lambda inputs: {
            "order": inputs["order"],
            "quantity": inputs["quantity"],
            "state": "shipped",
        },
    ),
}


def spec(
    handoff_id: str,
    referent: str,
    from_actor: str,
    to_actor: str,
    relation: str,
    inputs: dict,
    witness: str,
    *,
    dependency: str | None = None,
) -> Handoff:
    return Handoff(
        handoff_id=handoff_id,
        referent=referent,
        from_actor=from_actor,
        to_actor=to_actor,
        required_relation=relation,
        inputs=inputs,
        expected_output={"state": "changed"},
        required_witnesses=(witness,),
        admissible_evidence={witness: ("simulation",)},
        dependencies=(dependency,) if dependency else (),
        boundaries=(
            "All results in this example are simulated, not physical witnesses.",
        ),
        metadata={"factory_demo": True},
    )


def simulate_order() -> tuple[HandoffRuntime, list[str]]:
    runtime = HandoffRuntime()
    trace: list[str] = []
    referent = "ORDER-0001 / demo-widget"

    supply = spec(
        "factory-001-supply",
        referent,
        "factory-router",
        "supplier-sim",
        "supply material",
        {"material": "demo-stock", "quantity": 10},
        "material supplied",
    )
    runtime.submit(supply)
    state = runtime.run(supply.handoff_id, ACTORS["supplier-sim"])
    trace.append(f"{supply.handoff_id}:{state.status}")
    material = state.output

    machine = spec(
        "factory-002-machine",
        referent,
        "factory-router",
        "machine-sim",
        "machine feature",
        {"part": "demo-part", "quantity": material["quantity"], "material_state": material["state"]},
        "machining operation completed",
        dependency=supply.handoff_id,
    )
    runtime.spawn(supply.handoff_id, machine)
    state = runtime.run(machine.handoff_id, ACTORS["machine-sim"])
    trace.append(f"{machine.handoff_id}:{state.status}")
    machined = state.output

    inspect = spec(
        "factory-003-inspect",
        referent,
        "factory-router",
        "inspection-sim",
        "inspect output",
        {"part": machined["part"], "quantity": machined["quantity"], "part_state": machined["state"]},
        "inspection completed",
        dependency=machine.handoff_id,
    )
    runtime.spawn(machine.handoff_id, inspect)
    state = runtime.run(inspect.handoff_id, ACTORS["inspection-sim"])
    trace.append(f"{inspect.handoff_id}:{state.status}")
    inspected = state.output

    assemble = spec(
        "factory-004-assemble",
        referent,
        "factory-router",
        "assembly-sim",
        "assemble product",
        {"product": "demo-widget", "quantity": inspected["accepted"], "inspection_state": inspected["state"]},
        "assembly completed",
        dependency=inspect.handoff_id,
    )
    runtime.spawn(inspect.handoff_id, assemble)
    state = runtime.run(assemble.handoff_id, ACTORS["assembly-sim"])
    trace.append(f"{assemble.handoff_id}:{state.status}")
    assembled = state.output

    ship = spec(
        "factory-005-ship",
        referent,
        "factory-router",
        "shipping-sim",
        "ship product",
        {"order": "ORDER-0001", "quantity": assembled["quantity"], "product_state": assembled["state"]},
        "shipment recorded",
        dependency=assemble.handoff_id,
    )
    runtime.spawn(assemble.handoff_id, ship)
    state = runtime.run(ship.handoff_id, ACTORS["shipping-sim"])
    trace.append(f"{ship.handoff_id}:{state.status}")

    return runtime, trace


if __name__ == "__main__":
    runtime, trace = simulate_order()
    for line in trace:
        print(line)
    print("events:", len(runtime.event_store.all()))
