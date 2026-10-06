from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any
import json

from runtime import Handoff, HandoffState

from .model import Note, Plan, TaskRecord, utc_now


class PersonalOperationsStore:
    """Append-only local state for notes, tasks and plans.

    Notes and plans do not automatically become work.
    Tasks do not become runtime handoffs until explicitly admitted.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self._events: list[dict[str, Any]] = []
        self._notes: dict[str, Note] = {}
        self._plans: dict[str, Plan] = {}
        self._tasks: dict[str, TaskRecord] = {}
        self._admitted: dict[str, str] = {}
        self._results: dict[str, dict[str, Any]] = {}

        if self.path and self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    event = json.loads(line)
                    self._events.append(event)
                    self._replay(event)

    def _append(self, event: dict[str, Any]) -> None:
        self._events.append(event)
        self._replay(event)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def _replay(self, event: dict[str, Any]) -> None:
        kind = event["event_type"]
        payload = event["payload"]

        if kind == "NOTE_ADDED":
            self._notes[payload["note_id"]] = Note(
                **{
                    **payload,
                    "tags": tuple(payload.get("tags", ())),
                    "provenance": tuple(payload.get("provenance", ())),
                }
            )
        elif kind == "PLAN_ADDED":
            self._plans[payload["plan_id"]] = Plan(
                **{
                    **payload,
                    "steps": tuple(payload.get("steps", ())),
                    "provenance": tuple(payload.get("provenance", ())),
                }
            )
        elif kind == "TASK_ADDED":
            admissible = {
                key: tuple(value)
                for key, value in payload.get("admissible_evidence", {}).items()
            }
            self._tasks[payload["task_id"]] = TaskRecord(
                **{
                    **payload,
                    "required_witnesses": tuple(
                        payload.get("required_witnesses", ())
                    ),
                    "admissible_evidence": admissible,
                    "boundaries": tuple(payload.get("boundaries", ())),
                    "provenance": tuple(payload.get("provenance", ())),
                }
            )
        elif kind == "TASK_ADMITTED":
            self._admitted[payload["task_id"]] = payload["handoff_id"]
        elif kind == "TASK_RESULT_RECONCILED":
            self._results[payload["task_id"]] = dict(payload)

    def _record(self, event_type: str, payload: dict[str, Any]) -> None:
        self._append(
            {
                "event_type": event_type,
                "occurred_at": utc_now(),
                "payload": payload,
            }
        )

    def add_note(self, note: Note) -> Note:
        self._record("NOTE_ADDED", asdict(note))
        return note

    def add_plan(self, plan: Plan) -> Plan:
        self._record("PLAN_ADDED", asdict(plan))
        return plan

    def add_task(self, task: TaskRecord) -> TaskRecord:
        self._record("TASK_ADDED", asdict(task))
        return task

    def note(self, note_id: str) -> Note:
        return self._notes[note_id]

    def plan(self, plan_id: str) -> Plan:
        return self._plans[plan_id]

    def task(self, task_id: str) -> TaskRecord:
        return self._tasks[task_id]

    def notes(self) -> tuple[Note, ...]:
        return tuple(self._notes.values())

    def plans(self) -> tuple[Plan, ...]:
        return tuple(self._plans.values())

    def tasks(self) -> tuple[TaskRecord, ...]:
        return tuple(self._tasks.values())

    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._events)

    def admitted_handoff_id(self, task_id: str) -> str | None:
        return self._admitted.get(task_id)

    def task_result(self, task_id: str) -> dict[str, Any] | None:
        result = self._results.get(task_id)
        return dict(result) if result is not None else None

    def _handoff_from_task(
        self,
        task: TaskRecord,
        *,
        handoff_id: str,
    ) -> Handoff:
        return Handoff(
            handoff_id=handoff_id,
            referent=task.referent,
            from_actor="personal-operations",
            to_actor=task.assignee,
            required_relation=task.required_relation,
            inputs=task.inputs,
            expected_output=task.expected_output,
            required_witnesses=task.required_witnesses,
            admissible_evidence=task.admissible_evidence,
            boundaries=task.boundaries,
            provenance=tuple(
                dict.fromkeys(
                    (*task.provenance, f"personal-task:{task.task_id}")
                )
            ),
            metadata={
                "title": task.title,
                "notes": task.notes,
                "source_system": "personal-operations",
                "source_task_id": task.task_id,
            },
        )

    def admit_task(self, task_id: str) -> Handoff:
        task = self.task(task_id)
        existing = self._admitted.get(task_id)
        if existing:
            raise ValueError(
                f"task {task_id} already admitted as handoff {existing}"
            )

        handoff_id = f"personal-{task.task_id}"
        handoff = self._handoff_from_task(task, handoff_id=handoff_id)

        self._record(
            "TASK_ADMITTED",
            {"task_id": task.task_id, "handoff_id": handoff.handoff_id},
        )
        return handoff

    def admitted_handoff(self, task_id: str) -> Handoff:
        handoff_id = self._admitted.get(task_id)
        if handoff_id is None:
            raise ValueError(f"task {task_id} has not been admitted")
        return self._handoff_from_task(
            self.task(task_id),
            handoff_id=handoff_id,
        )

    def reconcile_task_result(
        self,
        task_id: str,
        state: HandoffState,
    ) -> dict[str, Any]:
        handoff_id = self._admitted.get(task_id)
        if handoff_id is None:
            raise ValueError(f"task {task_id} has not been admitted")
        if state.handoff_id != handoff_id:
            raise ValueError(
                f"state {state.handoff_id} does not belong to task {task_id}"
            )

        payload = {
            "task_id": task_id,
            "handoff_id": handoff_id,
            "status": state.status,
            "output": dict(state.output),
            "evidence": [
                {
                    "condition": item.condition,
                    "kind": item.kind,
                    "source": item.source,
                    "ref": item.ref,
                    "note": item.note,
                    "depth": item.depth,
                }
                for item in state.evidence
            ],
            "missing_witnesses": list(state.missing_witnesses),
            "blocked_by": list(state.blocked_by),
        }
        self._record("TASK_RESULT_RECONCILED", payload)
        return self.task_result(task_id)
