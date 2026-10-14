"""Small immutable carriers for independently resumable workspace lanes.

A lane is a current thread of attention, not a fixed discipline or task.
Evidence and source systems retain their native ownership.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Lane:
    lane_id: str
    label: str
    referent: str
    sources: tuple[str, ...]
    actor_id: str
    opened_event_id: str
    latest_event_id: str
    changes: str = ""
    preserved: str = ""
    next_movement: str = ""
    walls: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    movements: int = 0


@dataclass(frozen=True)
class Connection:
    event_id: str
    from_lane: str
    to_lane: str
    relation: str
    evidence_refs: tuple[str, ...] = ()


def required(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be nonempty text")
    return value.strip()


def strings(values: Any, name: str) -> tuple[str, ...]:
    if not isinstance(values, (tuple, list)):
        raise ValueError(f"{name} must be a sequence")
    return tuple(required(v, name) for v in values)
