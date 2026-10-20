from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
import os

from .handoff import EvidenceRecord, Handoff, HandoffEvent


def handoff_to_dict(handoff: Handoff) -> dict:
    return asdict(handoff)


def handoff_from_dict(row: dict) -> Handoff:
    return Handoff(
        handoff_id=row["handoff_id"],
        referent=row["referent"],
        from_actor=row["from_actor"],
        to_actor=row["to_actor"],
        required_relation=row["required_relation"],
        inputs=dict(row.get("inputs") or {}),
        expected_output=dict(row.get("expected_output") or {}),
        required_witnesses=tuple(row.get("required_witnesses") or ()),
        admissible_evidence={
            key: tuple(value)
            for key, value in (row.get("admissible_evidence") or {}).items()
        },
        dependencies=tuple(row.get("dependencies") or ()),
        boundaries=tuple(row.get("boundaries") or ()),
        provenance=tuple(row.get("provenance") or ()),
        metadata=dict(row.get("metadata") or {}),
    )


def event_to_dict(event: HandoffEvent) -> dict:
    return asdict(event)


def event_from_dict(row: dict) -> HandoffEvent:
    return HandoffEvent(
        event_id=row["event_id"],
        handoff_id=row["handoff_id"],
        event_type=row["event_type"],
        actor_id=row["actor_id"],
        occurred_at=row["occurred_at"],
        data=dict(row.get("data") or {}),
        evidence=tuple(
            EvidenceRecord(**item)
            for item in row.get("evidence") or ()
        ),
        parents=tuple(row.get("parents") or ()),
    )


class RuntimeJournal:
    """Append-only durable store for handoff specs + runtime events.

    A SUBMISSION record contains the immutable handoff specification and its
    CREATED event in one JSONL record. This avoids recovering an event stream
    that has lost the contract needed to interpret it.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._handoffs: dict[str, Handoff] = {}
        self._events: list[HandoffEvent] = []

        if self.path.exists():
            for number, line in enumerate(
                self.path.read_text(encoding="utf-8").splitlines(),
                start=1,
            ):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"invalid runtime journal JSON at line {number}"
                    ) from exc
                self._replay(record, line_number=number)

    def _replay(self, record: dict, *, line_number: int) -> None:
        kind = record.get("record_type")
        if kind == "SUBMISSION":
            handoff = handoff_from_dict(record["handoff"])
            event = event_from_dict(record["event"])
            if event.event_type != "CREATED":
                raise ValueError(
                    f"submission line {line_number} must contain CREATED event"
                )
            if event.handoff_id != handoff.handoff_id:
                raise ValueError(
                    f"submission line {line_number} handoff/event mismatch"
                )
            if handoff.handoff_id in self._handoffs:
                raise ValueError(
                    f"duplicate handoff submission: {handoff.handoff_id}"
                )
            self._handoffs[handoff.handoff_id] = handoff
            self._events.append(event)
            return

        if kind == "EVENT":
            event = event_from_dict(record["event"])
            if event.handoff_id not in self._handoffs:
                raise ValueError(
                    f"event line {line_number} references unknown handoff "
                    f"{event.handoff_id}"
                )
            self._events.append(event)
            return

        raise ValueError(
            f"unknown runtime journal record_type at line {line_number}: {kind!r}"
        )

    def _append_record(self, record: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(record, ensure_ascii=False) + "\n"
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())

    def append_submission(
        self,
        handoff: Handoff,
        created_event: HandoffEvent,
        *,
        admission: tuple[str, str, str] | None = None,
    ) -> HandoffEvent:
        if handoff.handoff_id in self._handoffs:
            raise ValueError(f"handoff already exists: {handoff.handoff_id}")
        if created_event.event_type != "CREATED":
            raise ValueError("submission requires a CREATED event")
        if created_event.handoff_id != handoff.handoff_id:
            raise ValueError("handoff/event id mismatch")

        record = {
            "record_type": "SUBMISSION",
            "handoff": handoff_to_dict(handoff),
            "event": event_to_dict(created_event),
        }
        if admission is None:
            self._append_record(record)
        else:
            atomic_append = getattr(self, "_append_admitted_record", None)
            if atomic_append is None:
                raise ValueError("native atomic admission requires sealed SQLite storage")
            atomic_append(record, admission)
        self._handoffs[handoff.handoff_id] = handoff
        self._events.append(created_event)
        return created_event

    def append(self, event: HandoffEvent, *,
               admission: tuple[str, str, str] | None = None) -> HandoffEvent:
        if event.handoff_id not in self._handoffs:
            raise ValueError(
                f"event references unknown handoff: {event.handoff_id}"
            )
        record = {"record_type": "EVENT", "event": event_to_dict(event)}
        if admission is None:
            self._append_record(record)
        else:
            atomic_append = getattr(self, "_append_admitted_record", None)
            if atomic_append is None:
                raise ValueError("native atomic admission requires sealed SQLite storage")
            atomic_append(record, admission)
        self._events.append(event)
        return event

    def handoffs(self) -> tuple[Handoff, ...]:
        return tuple(self._handoffs.values())

    def all(self) -> tuple[HandoffEvent, ...]:
        return tuple(self._events)

    def for_handoff(self, handoff_id: str) -> tuple[HandoffEvent, ...]:
        return tuple(
            event for event in self._events
            if event.handoff_id == handoff_id
        )
