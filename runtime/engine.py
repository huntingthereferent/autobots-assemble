from __future__ import annotations

from dataclasses import asdict, replace
from pathlib import Path
from typing import Callable, Iterable
from threading import RLock
import json

from .handoff import (
    EvidenceRecord,
    ExecutionResult,
    Handoff,
    HandoffEvent,
    HandoffState,
    SimulatedActor,
)


TERMINAL = {"COMPLETE", "PARTIAL", "BLOCKED", "FAILED", "UNKNOWN"}


class EventStore:
    """Append-only event store with optional JSONL persistence."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self._events: list[HandoffEvent] = []
        if self.path and self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                evidence = tuple(EvidenceRecord(**item) for item in row.pop("evidence", []))
                self._events.append(HandoffEvent(evidence=evidence, **row))

    def append(self, event: HandoffEvent) -> HandoffEvent:
        self._events.append(event)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            row = asdict(event)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
        return event

    def all(self) -> tuple[HandoffEvent, ...]:
        return tuple(self._events)

    def for_handoff(self, handoff_id: str) -> tuple[HandoffEvent, ...]:
        return tuple(e for e in self._events if e.handoff_id == handoff_id)


class HandoffRuntime:
    """Live state derived from immutable handoff specs plus append-only events."""

    def __init__(self, *, event_store: EventStore | None = None) -> None:
        self.event_store = event_store or EventStore()
        # Shared by every authenticated ingress of this runtime (submit/result).
        # The native state is in-memory, so a SQLite transaction alone does
        # not serialize reads of last_event_id against concurrent returns.
        self._authenticated_admission_lock = RLock()
        self._evidence_verifiers: dict[
            str, Callable[[Handoff, ExecutionResult], None]
        ] = {}
        restored = getattr(self.event_store, "handoffs", lambda: ())()
        self._handoffs: dict[str, Handoff] = {
            handoff.handoff_id: handoff
            for handoff in restored
        }

    def register_evidence_verifier(
        self, verifier_id: str, verifier: Callable[[Handoff, ExecutionResult], None]
    ) -> None:
        """Register a native verifier without embedding domain rules in runtime."""
        if not verifier_id.strip() or verifier_id in self._evidence_verifiers:
            raise ValueError("evidence verifier must be named and unique")
        self._evidence_verifiers[verifier_id] = verifier

    def submit(self, handoff: Handoff, *,
               admission: tuple[str, str, str] | None = None) -> HandoffState:
        """Append native CREATED and optional replay admission in one journal commit."""
        if handoff.handoff_id in self._handoffs:
            raise ValueError(f"handoff already exists: {handoff.handoff_id}")
        created = HandoffEvent.create(
            handoff_id=handoff.handoff_id,
            event_type="CREATED",
            actor_id=handoff.from_actor,
            data={
                "referent": handoff.referent,
                "to_actor": handoff.to_actor,
                "required_relation": handoff.required_relation,
            },
        )

        append_submission = getattr(
            self.event_store,
            "append_submission",
            None,
        )
        if append_submission is not None:
            if admission is None:
                append_submission(handoff, created)
            else:
                append_submission(handoff, created, admission=admission)
        else:
            if admission is not None:
                raise ValueError("atomic admission requires sealed native journal")
            self.event_store.append(created)

        self._handoffs[handoff.handoff_id] = handoff
        return self.state(handoff.handoff_id)

    def get(self, handoff_id: str) -> Handoff:
        try:
            return self._handoffs[handoff_id]
        except KeyError as exc:
            raise KeyError(f"unknown handoff: {handoff_id}") from exc

    def state(self, handoff_id: str) -> HandoffState:
        handoff = self.get(handoff_id)
        events = self.event_store.for_handoff(handoff_id)
        blocked_by = tuple(
            dep for dep in handoff.dependencies
            if dep not in self._handoffs or self.state(dep).status != "COMPLETE"
        )

        status = "WAITING" if blocked_by else "READY"
        output = {}
        evidence: list[EvidenceRecord] = []
        last_event_id = events[-1].event_id if events else ""

        for event in events:
            evidence.extend(event.evidence)
            if event.event_type == "STARTED":
                status = "ACTIVE"
            elif event.event_type == "RESULT":
                status = str(event.data["status"])
                output = dict(event.data.get("output") or {})
            elif event.event_type == "REOPENED":
                status = "WAITING" if blocked_by else "READY"
                output = {}

        supported = {item.condition for item in evidence}
        missing = tuple(
            condition for condition in handoff.required_witnesses
            if condition not in supported
        )

        return HandoffState(
            handoff_id=handoff_id,
            status=status,
            output=output,
            evidence=tuple(evidence),
            missing_witnesses=missing,
            blocked_by=blocked_by,
            last_event_id=last_event_id,
        )

    def _validate_complete_evidence(
        self,
        handoff: Handoff,
        evidence: Iterable[EvidenceRecord],
    ) -> None:
        by_condition: dict[str, list[EvidenceRecord]] = {}
        for item in evidence:
            by_condition.setdefault(item.condition, []).append(item)

        missing = [
            condition for condition in handoff.required_witnesses
            if condition not in by_condition
        ]
        if missing:
            raise ValueError(
                "COMPLETE requires evidence for: " + ", ".join(missing)
            )

        for condition, allowed_kinds in handoff.admissible_evidence.items():
            if not allowed_kinds:
                continue
            seen = by_condition.get(condition, [])
            if not any(item.kind in allowed_kinds for item in seen):
                raise ValueError(
                    f"witness {condition!r} requires one of evidence kinds "
                    f"{tuple(allowed_kinds)!r}"
                )

    def return_result(
        self,
        handoff_id: str,
        *,
        actor_id: str,
        result: ExecutionResult,
        admission: tuple[str, str, str] | None = None,
    ) -> HandoffState:
        handoff = self.get(handoff_id)
        current = self.state(handoff_id)
        if current.status == "WAITING":
            raise ValueError(
                f"handoff {handoff_id} is waiting on {current.blocked_by}"
            )
        if result.status == "COMPLETE":
            self._validate_complete_evidence(handoff, result.evidence)

        # A caller-provided evidence label is not itself a native witness.
        # Namespaced claims must be checked by their source adapter, for ALL
        # outcomes (including UNKNOWN/BLOCKED), before an event is persisted.
        verifier_id = handoff.metadata.get("native_evidence_verifier")
        if verifier_id is not None:
            if not isinstance(verifier_id, str) or not verifier_id.strip():
                raise ValueError("invalid native evidence verifier id")
            verifier = self._evidence_verifiers.get(verifier_id)
            if verifier is None:
                raise ValueError("native evidence verifier not registered: " + verifier_id)
            verifier(handoff, result)

        parent = current.last_event_id
        native_event = HandoffEvent.create(
            handoff_id=handoff_id,
            event_type="RESULT",
            actor_id=actor_id,
            data={"status": result.status, "output": result.output, "note": result.note},
            evidence=result.evidence,
            parents=(parent,) if parent else (),
        )
        if admission is None:
            self.event_store.append(native_event)
        else:
            self.event_store.append(native_event, admission=admission)
        return self.state(handoff_id)

    def run(self, handoff_id: str, actor: SimulatedActor) -> HandoffState:
        handoff = self.get(handoff_id)
        current = self.state(handoff_id)
        if current.status != "READY":
            raise ValueError(
                f"handoff {handoff_id} is not READY; current={current.status}"
            )
        if handoff.to_actor != actor.actor_id:
            raise ValueError(
                f"handoff targets {handoff.to_actor}, not {actor.actor_id}"
            )
        if not actor.can_execute(handoff):
            raise ValueError(
                f"{actor.actor_id} cannot execute {handoff.required_relation!r}"
            )

        self.event_store.append(
            HandoffEvent.create(
                handoff_id=handoff_id,
                event_type="STARTED",
                actor_id=actor.actor_id,
                parents=(current.last_event_id,) if current.last_event_id else (),
            )
        )
        return self.return_result(
            handoff_id,
            actor_id=actor.actor_id,
            result=actor.execute(handoff),
        )

    def spawn(self, parent_id: str, child: Handoff) -> HandoffState:
        parent_state = self.state(parent_id)
        if parent_state.status != "COMPLETE":
            raise ValueError(
                f"cannot spawn from {parent_id}: status={parent_state.status}"
            )

        dependencies = tuple(dict.fromkeys((*child.dependencies, parent_id)))
        provenance = tuple(dict.fromkeys((*child.provenance, parent_id)))
        return self.submit(
            replace(child, dependencies=dependencies, provenance=provenance)
        )

    def reopen(self, handoff_id: str, *, actor_id: str, reason: str) -> HandoffState:
        current = self.state(handoff_id)
        self.event_store.append(
            HandoffEvent.create(
                handoff_id=handoff_id,
                event_type="REOPENED",
                actor_id=actor_id,
                data={"reason": reason},
                parents=(current.last_event_id,) if current.last_event_id else (),
            )
        )
        return self.state(handoff_id)

    def snapshot(self) -> dict[str, HandoffState]:
        return {handoff_id: self.state(handoff_id) for handoff_id in self._handoffs}
