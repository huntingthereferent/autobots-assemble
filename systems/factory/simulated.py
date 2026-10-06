from __future__ import annotations

from runtime import (
    EvidenceRecord,
    ExecutionResult,
    Handoff,
    HandoffRuntime,
    SimulatedActor,
)

from .system import FactorySystem


def _actor(actor_id: str, relation: str, witness: str, output_fn):
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
                    depth="simulated",
                ),
            ),
        )

    return SimulatedActor(
        actor_id=actor_id,
        capabilities=(relation,),
        handler=handler,
    )


def default_simulated_actors() -> dict[str, SimulatedActor]:
    return {
        "supplier-sim": _actor(
            "supplier-sim",
            "supply material",
            "material supplied",
            lambda x: {
                "material": x["material"],
                "quantity": x["quantity"],
                "material_state": "received",
            },
        ),
        "machine-sim": _actor(
            "machine-sim",
            "machine feature",
            "machining operation completed",
            lambda x: {
                "part": f"{x['product']}-part",
                "quantity": x["quantity"],
                "part_state": "machined",
            },
        ),
        "inspection-sim": _actor(
            "inspection-sim",
            "inspect output",
            "inspection completed",
            lambda x: {
                "quantity": x["quantity"],
                "accepted": x["quantity"],
                "rejected": 0,
                "inspection_state": "inspected",
            },
        ),
        "assembly-sim": _actor(
            "assembly-sim",
            "assemble product",
            "assembly completed",
            lambda x: {
                "product": x["product"],
                "quantity": x["quantity"],
                "product_state": "assembled",
            },
        ),
        "shipping-sim": _actor(
            "shipping-sim",
            "ship product",
            "shipment recorded",
            lambda x: {
                "order": x["order"],
                "product": x["product"],
                "quantity": x["quantity"],
                "shipment_state": "shipped",
            },
        ),
    }


def run_simulated_order(
    factory: FactorySystem,
    runtime: HandoffRuntime,
    order_id: str,
) -> list[str]:
    actors = default_simulated_actors()
    trace: list[str] = []

    while factory.order(order_id).status != "complete":
        handoff = factory.next_handoff(order_id)
        if handoff is None:
            break

        runtime.submit(handoff)
        state = runtime.run(handoff.handoff_id, actors[handoff.to_actor])
        trace.append(f"{handoff.metadata['stage']}:{state.status}")
        factory.reconcile(order_id, handoff=handoff, state=state)

    return trace
