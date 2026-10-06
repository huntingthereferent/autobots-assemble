from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4
import json


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _many(values) -> tuple[str, ...]:
    return tuple(str(x).strip() for x in values or () if str(x).strip())


@dataclass(frozen=True)
class TraversalTouch:
    trace_id: str
    touched_at: str
    surface_kind: str
    locator: str
    referent_before: str
    relation: str
    session_id: str = ""
    parent_trace_id: str = ""
    provider: str = ""
    label: str = ""
    referent_after: str = ""
    what_changed: str = ""
    unresolved: tuple[str, ...] = field(default_factory=tuple)
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)
    artifact_refs: tuple[str, ...] = field(default_factory=tuple)
    next_trace_id: str = ""
    provenance: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def create(cls, payload: dict[str, Any]) -> "TraversalTouch":
        surface_kind = str(payload.get("surface_kind") or "").strip()
        locator = str(payload.get("locator") or "").strip()
        referent_before = str(payload.get("referent_before") or "").strip()
        relation = str(payload.get("relation") or "").strip()

        if not surface_kind:
            raise ValueError("surface_kind is required")
        if not locator:
            raise ValueError("locator is required")
        if not referent_before:
            raise ValueError("referent_before is required")
        if not relation:
            raise ValueError("relation is required")

        return cls(
            trace_id=str(payload.get("trace_id") or uuid4()),
            touched_at=str(payload.get("touched_at") or _now()),
            surface_kind=surface_kind,
            locator=locator,
            referent_before=referent_before,
            relation=relation,
            session_id=str(payload.get("session_id") or "").strip(),
            parent_trace_id=str(payload.get("parent_trace_id") or "").strip(),
            provider=str(payload.get("provider") or "").strip(),
            label=str(payload.get("label") or "").strip(),
            referent_after=str(payload.get("referent_after") or "").strip(),
            what_changed=str(payload.get("what_changed") or "").strip(),
            unresolved=_many(payload.get("unresolved")),
            evidence_refs=_many(payload.get("evidence_refs")),
            artifact_refs=_many(payload.get("artifact_refs")),
            next_trace_id=str(payload.get("next_trace_id") or "").strip(),
            provenance=_many(payload.get("provenance")),
        )


class TraceStore:
    """Append-only relational trace of things Continuity touched.

    The trace stores movement metadata and external locators. It is not an
    ingestion store for the external page/feed/app itself.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def _rows(self) -> list[dict[str, Any]]:
        rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def add(self, touch: TraversalTouch) -> TraversalTouch:
        rows = self._rows()
        ids = {row["trace_id"] for row in rows}
        if touch.trace_id in ids:
            raise ValueError(f"trace already exists: {touch.trace_id}")
        if touch.parent_trace_id and touch.parent_trace_id not in ids:
            raise ValueError(
                f"parent trace does not exist: {touch.parent_trace_id}"
            )
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(touch), ensure_ascii=False) + "\n")
        return touch

    def touches(self, *, session_id: str | None = None) -> list[TraversalTouch]:
        rows = self._rows()
        if session_id:
            rows = [row for row in rows if row.get("session_id") == session_id]
        return [TraversalTouch(**row) for row in rows]

    def get(self, trace_id: str) -> TraversalTouch:
        for touch in self.touches():
            if touch.trace_id == trace_id:
                return touch
        raise KeyError(trace_id)

    def ancestry(self, trace_id: str) -> list[TraversalTouch]:
        by_id = {touch.trace_id: touch for touch in self.touches()}
        if trace_id not in by_id:
            raise KeyError(trace_id)

        chain = []
        current = by_id[trace_id]
        seen = set()
        while current:
            if current.trace_id in seen:
                raise ValueError("trace ancestry contains a cycle")
            seen.add(current.trace_id)
            chain.append(current)
            if not current.parent_trace_id:
                break
            current = by_id.get(current.parent_trace_id)
            if current is None:
                raise ValueError("trace ancestry is missing a parent")
        chain.reverse()
        return chain
