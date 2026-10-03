from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

from .core import EvidenceRef, Relation

ResultState = Literal["MOVE", "WALL", "UNKNOWN", "PARTIAL"]
WitnessState = Literal["SUPPORTED", "MISSING", "UNKNOWN", "PARTIAL"]


@dataclass(frozen=True)
class Witness:
    condition: str
    state: WitnessState
    evidence: tuple[EvidenceRef, ...] = ()
    note: str = ""


@dataclass(frozen=True)
class Protocol:
    protocol_id: str
    purpose: str
    required_witnesses: tuple[str, ...]


@dataclass(frozen=True)
class ProtocolResult:
    protocol_id: str
    referent_before: str
    state: ResultState
    witnesses: tuple[Witness, ...]
    outputs: tuple[Relation, ...]
    next_referent: str
    note: str = ""

    def as_relations(self, source: str = "protocol") -> tuple[Relation, ...]:
        """Encode the result back into generic relations.

        This is the operational closure point: a protocol result becomes valid
        network input without changing the outer evidence contract.
        """
        evidence = tuple(e for witness in self.witnesses for e in witness.evidence)
        parents = tuple(r.relation_id for r in self.outputs)
        return (
            Relation(self.referent_before, "protocol_result", self.state, source, evidence=evidence, parents=parents),
            Relation(self.referent_before, "next_referent", self.next_referent, source, evidence=evidence, parents=parents),
        ) + self.outputs


def apply_protocol(
    protocol: Protocol,
    *,
    referent: str,
    witnesses: Iterable[Witness],
    outputs: Iterable[Relation] = (),
    next_referent: str | None = None,
    note: str = "",
) -> ProtocolResult:
    witness_tuple = tuple(witnesses)
    by_condition = {w.condition: w for w in witness_tuple}

    missing_conditions = [
        condition for condition in protocol.required_witnesses
        if condition not in by_condition or by_condition[condition].state == "MISSING"
    ]
    unknown_conditions = [
        condition for condition in protocol.required_witnesses
        if condition in by_condition and by_condition[condition].state == "UNKNOWN"
    ]
    partial_conditions = [
        condition for condition in protocol.required_witnesses
        if condition in by_condition and by_condition[condition].state == "PARTIAL"
    ]

    output_tuple = tuple(outputs)
    if missing_conditions:
        state: ResultState = "WALL"
        output_tuple = ()
    elif unknown_conditions:
        state = "UNKNOWN"
        output_tuple = ()
    elif partial_conditions:
        state = "PARTIAL"
    else:
        state = "MOVE"

    return ProtocolResult(
        protocol_id=protocol.protocol_id,
        referent_before=referent,
        state=state,
        witnesses=witness_tuple,
        outputs=output_tuple,
        next_referent=next_referent or referent,
        note=note,
    )
