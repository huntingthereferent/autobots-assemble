from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Literal
import uuid


HandoffStatus = Literal[
    "WAITING",
    "READY",
    "ACTIVE",
    "COMPLETE",
    "PARTIAL",
    "BLOCKED",
    "FAILED",
    "UNKNOWN",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class EvidenceRecord:
    """Evidence returned across a handoff boundary."""

    condition: str
    kind: str
    source: str
    ref: str = ""
    note: str = ""
    depth: str = "reported"

    def __post_init__(self) -> None:
        for name, value in (
            ("condition", self.condition),
            ("kind", self.kind),
            ("source", self.source),
        ):
            if not str(value).strip():
                raise ValueError(f"evidence {name} is required")


@dataclass(frozen=True)
class Handoff:
    """The common carrier between unlike execution layers.

    A handoff describes what must cross a boundary. It does not prescribe how
    the receiver executes it. Human task cards, API jobs, machine commands and
    simulator events are projections/adapters over this same record.
    """

    handoff_id: str
    referent: str
    from_actor: str
    to_actor: str
    required_relation: str
    inputs: dict[str, Any] = field(default_factory=dict)
    expected_output: dict[str, Any] = field(default_factory=dict)
    required_witnesses: tuple[str, ...] = ()
    admissible_evidence: dict[str, tuple[str, ...]] = field(default_factory=dict)
    dependencies: tuple[str, ...] = ()
    boundaries: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name, value in (
            ("handoff_id", self.handoff_id),
            ("referent", self.referent),
            ("from_actor", self.from_actor),
            ("to_actor", self.to_actor),
            ("required_relation", self.required_relation),
        ):
            if not str(value).strip():
                raise ValueError(f"{name} is required")

        unknown = set(self.admissible_evidence) - set(self.required_witnesses)
        if unknown:
            raise ValueError(
                "admissible_evidence keys must name required witnesses: "
                + ", ".join(sorted(unknown))
            )


@dataclass(frozen=True)
class HandoffEvent:
    event_id: str
    handoff_id: str
    event_type: str
    actor_id: str
    occurred_at: str
    data: dict[str, Any] = field(default_factory=dict)
    evidence: tuple[EvidenceRecord, ...] = ()
    parents: tuple[str, ...] = ()

    @classmethod
    def create(
        cls,
        *,
        handoff_id: str,
        event_type: str,
        actor_id: str,
        data: dict[str, Any] | None = None,
        evidence: tuple[EvidenceRecord, ...] = (),
        parents: tuple[str, ...] = (),
    ) -> "HandoffEvent":
        return cls(
            event_id="evt_" + uuid.uuid4().hex,
            handoff_id=handoff_id,
            event_type=event_type,
            actor_id=actor_id,
            occurred_at=utc_now(),
            data=data or {},
            evidence=evidence,
            parents=parents,
        )


@dataclass(frozen=True)
class HandoffState:
    handoff_id: str
    status: HandoffStatus
    output: dict[str, Any] = field(default_factory=dict)
    evidence: tuple[EvidenceRecord, ...] = ()
    missing_witnesses: tuple[str, ...] = ()
    blocked_by: tuple[str, ...] = ()
    last_event_id: str = ""


@dataclass(frozen=True)
class ExecutionResult:
    status: Literal["COMPLETE", "PARTIAL", "BLOCKED", "FAILED", "UNKNOWN"]
    output: dict[str, Any] = field(default_factory=dict)
    evidence: tuple[EvidenceRecord, ...] = ()
    note: str = ""


@dataclass(frozen=True)
class SimulatedActor:
    """Small adapter used to prove that simulated execution fits the carrier."""

    actor_id: str
    capabilities: tuple[str, ...]
    handler: Callable[[Handoff], ExecutionResult]

    def can_execute(self, handoff: Handoff) -> bool:
        return "*" in self.capabilities or handoff.required_relation in self.capabilities

    def execute(self, handoff: Handoff) -> ExecutionResult:
        if not self.can_execute(handoff):
            raise ValueError(
                f"{self.actor_id} cannot execute relation {handoff.required_relation!r}"
            )
        return self.handler(handoff)
