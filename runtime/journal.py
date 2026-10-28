from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
import os

from .handoff import EvidenceRecord, Handoff, HandoffEvent
from .ab_journal_gate import entry_gate, output_gate


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

    def _validate_event(self, event: HandoffEvent) -> None:
        if any(item.event_id == event.event_id for item in self._events):
            raise ValueError('duplicate runtime event id')
        if event.event_type not in ('CREATED', 'STARTED', 'RESULT', 'REOPENED',
                                    'AGENT_LOOP_CLOSED', 'AGENT_AB_OBSERVED',
                                    'WORKSTATION_MOVEMENT_OBSERVED',
                                    'WORKSTATION_HELP_OPEN',
                                    'WORKSTATION_NATIVE_HELP_ASSIGNED'):
            raise ValueError('invalid runtime event type')
        prior = next((item for item in reversed(self._events)
                      if item.handoff_id == event.handoff_id), None)
        if event.event_type == 'CREATED':
            if prior is not None or event.parents:
                raise ValueError('invalid CREATED event')
        elif event.event_type == 'AGENT_LOOP_CLOSED':
            # The ancestor's last event and the descendant's admitted result
            # are both ancestry, but neither may be invented or reordered.
            if prior is None or not event.data.get('closed_by') or not event.evidence:
                raise ValueError('invalid agent closure event')
            if event.actor_id != event.data['closed_by']:
                raise ValueError('agent closure actor mismatch')
            source = next((item for item in reversed(self._events)
                           if item.handoff_id == event.actor_id), None)
            if source is None or source.event_type != 'RESULT' or source.data.get('status') != 'COMPLETE':
                raise ValueError('agent closure requires completed descendant result')
            if event.parents != (prior.event_id, source.event_id):
                raise ValueError('invalid agent closure ancestry')
        elif prior is None or event.parents != (prior.event_id,):
            raise ValueError('invalid event parent chain')
        if event.event_type == 'RESULT' and event.data.get('status') not in (
            'COMPLETE', 'PARTIAL', 'BLOCKED', 'FAILED', 'UNKNOWN'):
            raise ValueError('invalid RESULT status')
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
            if not entry_gate(self._handoffs, tuple(self._events), event, handoff).admitted:
                raise ValueError("A/entry gate rejected submission replay")
            self._validate_event(event)
            self._handoffs[handoff.handoff_id] = handoff
            self._events.append(event)
            if not output_gate(self._handoffs, tuple(self._events), event).admitted:
                raise ValueError('B/output gate rejected replay')
            return

        if kind == "EVENT":
            event = event_from_dict(record["event"])
            if event.handoff_id not in self._handoffs:
                raise ValueError(
                    f"event line {line_number} references unknown handoff "
                    f"{event.handoff_id}"
                )
            if not entry_gate(self._handoffs, tuple(self._events), event).admitted:
                raise ValueError("A/entry gate rejected event replay")
            self._validate_event(event)
            self._events.append(event)
            if not output_gate(self._handoffs, tuple(self._events), event).admitted:
                raise ValueError('B/output gate rejected event replay')
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
        if not entry_gate(self._handoffs, tuple(self._events), created_event, handoff).admitted:
            raise ValueError('A/entry gate rejected submission')
        self._validate_event(created_event)
        if not output_gate({**self._handoffs, handoff.handoff_id: handoff}, tuple(self._events) + (created_event,), created_event).admitted:
            raise ValueError('B/output gate rejected submission')
        self._append_record(record)
        self._handoffs[handoff.handoff_id] = handoff
        self._events.append(created_event)
        return created_event

    def append(self, event: HandoffEvent) -> HandoffEvent:
        if event.handoff_id not in self._handoffs:
            raise ValueError(
                f"event references unknown handoff: {event.handoff_id}"
            )
        if not entry_gate(self._handoffs, tuple(self._events), event).admitted:
            raise ValueError('A/entry gate rejected event')
        self._validate_event(event)
        if not output_gate(self._handoffs, tuple(self._events) + (event,), event).admitted:
            raise ValueError('B/output gate rejected event')
        self._append_record(
            {
                "record_type": "EVENT",
                "event": event_to_dict(event),
            }
        )
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
