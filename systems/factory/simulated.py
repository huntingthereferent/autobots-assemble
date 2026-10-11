from __future__ import annotations

from dataclasses import replace

from runtime import (
    EvidenceRecord,
    ExecutionResult,
    Handoff,
    HandoffRuntime,
    SimulatedActor,
)

from .system import FactorySystem, STAGES


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


FACTORY_SIMULATION_VERIFIER = "factory.simulation.native.v1"


class FactorySimulationAdmission:
    """Source-owned verification for deterministic *simulated* Factory stages.

    Recompute the original native simulator's output from the submitted
    handoff and reject any different claimed success. This checks consistency
    and provenance within the simulation, NOT actual physical performance.
    A live supplier/machine/inspector/carrier needs its own source admission.
    """

    def __init__(self, runtime: HandoffRuntime):
        self.runtime = runtime
        runtime.register_evidence_verifier(
            FACTORY_SIMULATION_VERIFIER, self._verify
        )

    @staticmethod
    def _check_handoff(handoff: Handoff) -> None:
        stage = next(
            (stage for stage in STAGES
             if stage["name"] == handoff.metadata.get("stage")),
            None,
        )
        if (stage is None
                or handoff.metadata.get("source_system") != "factory"
                or handoff.from_actor != "factory-system"
                or handoff.to_actor != stage["actor"]
                or handoff.required_relation != stage["relation"]
                or handoff.required_witnesses != (stage["witness"],)
                or handoff.admissible_evidence != {stage["witness"]: ("simulation",)}):
            raise ValueError("handoff is not a native simulated Factory stage")

    def admit(self, handoff: Handoff) -> Handoff:
        """Mark a real Factory handoff for native simulation verification."""
        self._check_handoff(handoff)
        return replace(
            handoff,
            metadata={
                **handoff.metadata,
                "native_evidence_verifier": FACTORY_SIMULATION_VERIFIER,
            },
            boundaries=(*handoff.boundaries,
                "Native simulation replay does not witness a physical event.",
            ),
        )

    def _verify(self, handoff: Handoff, result: ExecutionResult) -> None:
        self._check_handoff(handoff)
        if handoff.metadata.get("native_evidence_verifier") != FACTORY_SIMULATION_VERIFIER:
            raise ValueError("native Factory verifier metadata mismatch")
        if result.status != "COMPLETE":
            # A non-complete investigation cannot silently carry an asserted
            # physical witness across this simulation-specific admission.
            if result.evidence:
                raise ValueError("non-complete simulated stages must not report evidence")
            return

        # The exact native simulator is the authority for simulated output
        # shape and witness source/depth, not a user-supplied evidence label.
        expected = default_simulated_actors()[handoff.to_actor].execute(handoff)
        if result != expected:
            raise ValueError("claimed Factory result differs from native simulator")

    def reverify(self, handoff_id: str):
        """Recheck persisted simulation COMPLETE results after journal reload."""
        handoff = self.runtime.get(handoff_id)
        if handoff.metadata.get("native_evidence_verifier") != FACTORY_SIMULATION_VERIFIER:
            raise ValueError("handoff was not admitted for native simulation replay")
        state = self.runtime.state(handoff_id)
        if state.status == "COMPLETE":
            self._verify(handoff, ExecutionResult(
                status="COMPLETE",
                output=state.output,
                evidence=state.evidence,
            ))
        return state
