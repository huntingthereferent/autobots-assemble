from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, Field


class ChangeKind(StrEnum):
    NEW = "new"
    CHANGED = "changed"
    UNCHANGED = "unchanged"
    DISAPPEARED = "disappeared"
    CONFLICTING = "conflicting"


class ReconciliationStatus(StrEnum):
    SINGLE_SOURCE = "single_source"
    AGREEMENT = "agreement"
    CONFLICT = "conflict"
    REVIEW_REQUIRED = "review_required"


class SourceObservation(BaseModel):
    source: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    observed_at: datetime
    source_updated_at: datetime | None = None
    source_url: str | None = None
    entity_type: str = Field(min_length=1)
    canonical_key: str = Field(min_length=1)
    payload: dict[str, Any]


class SourceAdapter(Protocol):
    name: str

    def fetch(self) -> list[SourceObservation]:
        ...


class ChangeResult(BaseModel):
    kind: ChangeKind
    changed_fields: list[str] = []


class ReconciliationResult(BaseModel):
    canonical_key: str
    status: ReconciliationStatus
    sources: list[str]
    conflicting_fields: list[str] = []
    selected_payload: dict[str, Any] | None = None


def classify_change(
    previous: SourceObservation | None,
    current: SourceObservation | None,
) -> ChangeResult:
    if previous is None and current is not None:
        return ChangeResult(kind=ChangeKind.NEW)
    if previous is not None and current is None:
        return ChangeResult(kind=ChangeKind.DISAPPEARED)
    if previous is None and current is None:
        raise ValueError("at least one observation is required")

    assert previous is not None and current is not None

    keys = sorted(set(previous.payload) | set(current.payload))
    changed = [key for key in keys if previous.payload.get(key) != current.payload.get(key)]
    if not changed:
        return ChangeResult(kind=ChangeKind.UNCHANGED)
    return ChangeResult(kind=ChangeKind.CHANGED, changed_fields=changed)


def reconcile(observations: list[SourceObservation]) -> ReconciliationResult:
    if not observations:
        raise ValueError("at least one observation is required")

    keys = {obs.canonical_key for obs in observations}
    if len(keys) != 1:
        raise ValueError("observations must share one canonical_key")

    canonical_key = observations[0].canonical_key
    sources = sorted({obs.source for obs in observations})

    if len(observations) == 1:
        return ReconciliationResult(
            canonical_key=canonical_key,
            status=ReconciliationStatus.SINGLE_SOURCE,
            sources=sources,
            selected_payload=observations[0].payload,
        )

    fields = sorted(set().union(*(obs.payload.keys() for obs in observations)))
    conflicts = [
        field
        for field in fields
        if len({repr(obs.payload.get(field)) for obs in observations}) > 1
    ]

    if not conflicts:
        return ReconciliationResult(
            canonical_key=canonical_key,
            status=ReconciliationStatus.AGREEMENT,
            sources=sources,
            selected_payload=observations[0].payload,
        )

    return ReconciliationResult(
        canonical_key=canonical_key,
        status=ReconciliationStatus.CONFLICT,
        sources=sources,
        conflicting_fields=conflicts,
        selected_payload=None,
    )
