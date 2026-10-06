from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


@dataclass(frozen=True)
class Note:
    note_id: str
    body: str
    referent: str = ""
    actor_id: str = ""
    tags: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def create(
        cls,
        body: str,
        *,
        referent: str = "",
        actor_id: str = "",
        tags: tuple[str, ...] = (),
        provenance: tuple[str, ...] = (),
    ) -> "Note":
        if not body.strip():
            raise ValueError("note body is required")
        return cls(
            note_id=new_id("note"),
            body=body.strip(),
            referent=referent.strip(),
            actor_id=actor_id.strip(),
            tags=tags,
            provenance=provenance,
        )


@dataclass(frozen=True)
class Plan:
    plan_id: str
    title: str
    referent: str
    actor_id: str
    steps: tuple[str, ...] = ()
    notes: str = ""
    provenance: tuple[str, ...] = ()
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def create(
        cls,
        title: str,
        *,
        referent: str,
        actor_id: str,
        steps: tuple[str, ...] = (),
        notes: str = "",
        provenance: tuple[str, ...] = (),
    ) -> "Plan":
        if not title.strip():
            raise ValueError("plan title is required")
        if not referent.strip():
            raise ValueError("plan referent is required")
        if not actor_id.strip():
            raise ValueError("plan actor_id is required")
        return cls(
            plan_id=new_id("plan"),
            title=title.strip(),
            referent=referent.strip(),
            actor_id=actor_id.strip(),
            steps=tuple(step.strip() for step in steps if step.strip()),
            notes=notes.strip(),
            provenance=provenance,
        )


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    title: str
    referent: str
    assignee: str
    required_relation: str
    inputs: dict[str, Any] = field(default_factory=dict)
    expected_output: dict[str, Any] = field(default_factory=dict)
    required_witnesses: tuple[str, ...] = ("task disposition reported",)
    admissible_evidence: dict[str, tuple[str, ...]] = field(
        default_factory=lambda: {
            "task disposition reported": ("human_report",)
        }
    )
    boundaries: tuple[str, ...] = ()
    provenance: tuple[str, ...] = ()
    notes: str = ""
    created_at: str = field(default_factory=utc_now)

    @classmethod
    def create(
        cls,
        title: str,
        *,
        referent: str,
        assignee: str,
        required_relation: str = "move current task",
        inputs: dict[str, Any] | None = None,
        expected_output: dict[str, Any] | None = None,
        required_witnesses: tuple[str, ...] = ("task disposition reported",),
        admissible_evidence: dict[str, tuple[str, ...]] | None = None,
        boundaries: tuple[str, ...] = (),
        provenance: tuple[str, ...] = (),
        notes: str = "",
    ) -> "TaskRecord":
        for name, value in (
            ("title", title),
            ("referent", referent),
            ("assignee", assignee),
            ("required_relation", required_relation),
        ):
            if not value.strip():
                raise ValueError(f"task {name} is required")

        return cls(
            task_id=new_id("task"),
            title=title.strip(),
            referent=referent.strip(),
            assignee=assignee.strip(),
            required_relation=required_relation.strip(),
            inputs=dict(inputs or {}),
            expected_output=dict(expected_output or {}),
            required_witnesses=required_witnesses,
            admissible_evidence=dict(
                admissible_evidence
                or {"task disposition reported": ("human_report",)}
            ),
            boundaries=boundaries,
            provenance=provenance,
            notes=notes.strip(),
        )
