from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from runtime.activation import ActivationRegistry, run_activation
from runtime.engine import HandoffRuntime
from runtime.handoff import EvidenceRecord, ExecutionResult
from runtime.journal import RuntimeJournal
from runtime.orchestrator import Orchestrator
from systems.bindings import personal_operations_binding
from systems.personal_operations import (
    Note,
    PersonalOperationsStore,
    Plan,
    TaskRecord,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACTIVATIONS = ROOT / "activations" / "registry.json"


class EcosystemService:
    """Persistent application service over the shared runtime.

    The service owns no new work model. It coordinates the existing
    Personal Operations system, activation registry, durable HandoffRuntime,
    and Orchestrator.
    """

    def __init__(
        self,
        *,
        data_dir: str | Path,
        activation_registry: str | Path = DEFAULT_ACTIVATIONS,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.personal = PersonalOperationsStore(
            self.data_dir / "personal_operations.jsonl"
        )
        self.runtime = HandoffRuntime(
            event_store=RuntimeJournal(
                self.data_dir / "runtime.jsonl"
            )
        )
        self.orchestrator = Orchestrator(self.runtime)
        self.orchestrator.register_system(
            personal_operations_binding(self.personal)
        )
        self.activations = ActivationRegistry.from_json(
            activation_registry
        )

        # Re-bind origins and submit any admitted local tasks that predate
        # runtime persistence. Human tasks remain READY without an actor.
        self.orchestrator.step()

    def status(self) -> dict[str, Any]:
        snapshot = self.runtime.snapshot()
        by_status: dict[str, int] = {}
        for state in snapshot.values():
            by_status[state.status] = by_status.get(state.status, 0) + 1

        return {
            "systems": {
                "personal-operations": {
                    "notes": len(self.personal.notes()),
                    "plans": len(self.personal.plans()),
                    "tasks": len(self.personal.tasks()),
                    "reconciled_results": sum(
                        1
                        for task in self.personal.tasks()
                        if self.personal.task_result(task.task_id) is not None
                    ),
                }
            },
            "runtime": {
                "handoffs": len(snapshot),
                "by_status": by_status,
                "events": len(self.runtime.event_store.all()),
            },
        }

    def add_note(self, payload: dict[str, Any]) -> dict[str, Any]:
        note = self.personal.add_note(
            Note.create(
                str(payload.get("body") or ""),
                referent=str(payload.get("referent") or ""),
                actor_id=str(payload.get("actor_id") or ""),
                tags=tuple(str(x) for x in payload.get("tags") or ()),
                provenance=tuple(
                    str(x) for x in payload.get("provenance") or ()
                ),
            )
        )
        return asdict(note)

    def add_plan(self, payload: dict[str, Any]) -> dict[str, Any]:
        plan = self.personal.add_plan(
            Plan.create(
                str(payload.get("title") or ""),
                referent=str(payload.get("referent") or ""),
                actor_id=str(payload.get("actor_id") or ""),
                steps=tuple(str(x) for x in payload.get("steps") or ()),
                notes=str(payload.get("notes") or ""),
                provenance=tuple(
                    str(x) for x in payload.get("provenance") or ()
                ),
            )
        )
        return asdict(plan)

    def add_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        task = self.personal.add_task(
            TaskRecord.create(
                str(payload.get("title") or ""),
                referent=str(payload.get("referent") or ""),
                assignee=str(payload.get("assignee") or ""),
                required_relation=str(
                    payload.get("required_relation")
                    or "move current task"
                ),
                inputs=dict(payload.get("inputs") or {}),
                expected_output=dict(
                    payload.get("expected_output") or {}
                ),
                boundaries=tuple(
                    str(x) for x in payload.get("boundaries") or ()
                ),
                provenance=tuple(
                    str(x) for x in payload.get("provenance") or ()
                ),
                notes=str(payload.get("notes") or ""),
            )
        )
        return {
            **asdict(task),
            "admitted_handoff_id": None,
            "result": None,
        }

    def admit_task(self, task_id: str) -> dict[str, Any]:
        handoff = self.personal.admit_task(task_id)
        self.orchestrator.step()
        state = self.runtime.state(handoff.handoff_id)
        return self._handoff_view(handoff.handoff_id, state)

    def list_notes(self) -> list[dict[str, Any]]:
        return [asdict(item) for item in self.personal.notes()]

    def list_plans(self) -> list[dict[str, Any]]:
        return [asdict(item) for item in self.personal.plans()]

    def list_tasks(self) -> list[dict[str, Any]]:
        rows = []
        for task in self.personal.tasks():
            rows.append(
                {
                    **asdict(task),
                    "admitted_handoff_id": self.personal.admitted_handoff_id(
                        task.task_id
                    ),
                    "result": self.personal.task_result(task.task_id),
                }
            )
        return rows

    def _handoff_view(self, handoff_id: str, state=None) -> dict[str, Any]:
        handoff = self.runtime.get(handoff_id)
        state = state or self.runtime.state(handoff_id)
        return {
            "handoff_id": handoff.handoff_id,
            "referent": handoff.referent,
            "from_actor": handoff.from_actor,
            "to_actor": handoff.to_actor,
            "required_relation": handoff.required_relation,
            "status": state.status,
            "inputs": handoff.inputs,
            "expected_output": handoff.expected_output,
            "required_witnesses": list(handoff.required_witnesses),
            "blocked_by": list(state.blocked_by),
            "missing_witnesses": list(state.missing_witnesses),
            "output": state.output,
            "evidence": [asdict(item) for item in state.evidence],
            "boundaries": list(handoff.boundaries),
            "provenance": list(handoff.provenance),
            "metadata": handoff.metadata,
        }

    def list_handoffs(
        self,
        *,
        actor_id: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        rows = []
        for handoff_id, state in self.runtime.snapshot().items():
            handoff = self.runtime.get(handoff_id)
            if actor_id and handoff.to_actor != actor_id:
                continue
            if status and state.status != status:
                continue
            rows.append(self._handoff_view(handoff_id, state))
        rows.sort(
            key=lambda row: (
                row["status"],
                str(row["metadata"].get("title") or row["required_relation"]),
            )
        )
        return rows

    def activate(
        self,
        surface: str,
        *,
        actor_id: str,
    ) -> dict[str, Any]:
        route = self.activations.resolve(
            surface,
            actor_id=actor_id,
        )
        if route is None:
            raise KeyError(
                f"no activation for {surface!r} and actor {actor_id!r}"
            )

        result = run_activation(
            route,
            surface=surface,
            handoffs=[
                (self.runtime.get(handoff_id), state)
                for handoff_id, state in self.runtime.snapshot().items()
            ],
        )
        return {
            "activation_id": route.activation_id,
            "referent": route.referent,
            "projection": route.projection,
            "items": list(result.items),
            "note": result.note,
        }

    def return_result(
        self,
        handoff_id: str,
        payload: dict[str, Any],
        *,
        actor_id: str,
    ) -> dict[str, Any]:
        evidence = tuple(
            EvidenceRecord(
                condition=str(item.get("condition") or ""),
                kind=str(item.get("kind") or ""),
                source=str(item.get("source") or actor_id),
                ref=str(item.get("ref") or ""),
                note=str(item.get("note") or ""),
                depth=str(item.get("depth") or "reported"),
            )
            for item in payload.get("evidence") or ()
        )
        result = ExecutionResult(
            status=str(payload.get("status") or "UNKNOWN"),
            output=dict(payload.get("output") or {}),
            evidence=evidence,
            note=str(payload.get("note") or ""),
        )
        state = self.orchestrator.return_result(
            handoff_id,
            actor_id=actor_id,
            result=result,
        )
        return self._handoff_view(handoff_id, state)
