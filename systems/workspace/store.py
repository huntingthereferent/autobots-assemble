"""Append-only, local workspace continuity; no task admission or execution.

The journal is not the source of truth for any originating project.
It holds lane return points and explicitly witnessed cross-lane references.
"""
from __future__ import annotations

from dataclasses import asdict, replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from .model import Connection, Lane, required, strings

EVENTS = frozenset({"LANE_OPENED", "LANE_MOVED", "LANES_CONNECTED", "FOCUS_SET"})
FIELDS = frozenset({"event_id", "event_type", "occurred_at", "data"})


class WorkspaceStore:
    """Mutable journal, computed immutable lane snapshots; no scheduler."""

    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else None
        self._events: list[dict[str, Any]] = []
        if self.path is not None and self.path.exists():
            for number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    raise ValueError(f"blank workspace journal line {number}")
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid workspace journal line {number}") from exc
                # Validate the entire replay prefix before accepting the next row.
                self._fold([*self._events, record])
                self._events.append(record)

    @staticmethod
    def _fold(events: list[dict[str, Any]]) -> tuple[dict[str, Lane], list[Connection], str | None]:
        lanes: dict[str, Lane] = {}
        links: list[Connection] = []
        focus: str | None = None
        seen: set[str] = set()
        for event in events:
            if not isinstance(event, dict) or set(event) != FIELDS:
                raise ValueError("invalid workspace event envelope")
            event_id = required(event["event_id"], "event_id")
            event_type = event["event_type"]
            required(event["occurred_at"], "occurred_at")
            data = event["data"]
            if event_id in seen or event_type not in EVENTS or not isinstance(data, dict):
                raise ValueError("duplicate event id, unknown type, or invalid data")
            seen.add(event_id)
            if event_type == "LANE_OPENED":
                if set(data) != {"lane_id", "label", "referent", "sources", "actor_id"}:
                    raise ValueError("invalid lane opening")
                lane_id = required(data["lane_id"], "lane_id")
                if lane_id in lanes:
                    raise ValueError("lane already exists")
                lanes[lane_id] = Lane(
                    lane_id, required(data["label"], "label"),
                    required(data["referent"], "referent"), strings(data["sources"], "sources"),
                    required(data["actor_id"], "actor_id"), event_id, event_id,
                )
            elif event_type == "LANE_MOVED":
                if set(data) != {"lane_id", "prior_event_id", "referent", "changes", "preserved", "next_movement", "walls", "evidence_refs"}:
                    raise ValueError("invalid lane movement")
                lane_id = required(data["lane_id"], "lane_id")
                if lane_id not in lanes:
                    raise ValueError("movement references unknown lane")
                prior = lanes[lane_id]
                if data["prior_event_id"] != prior.latest_event_id:
                    raise ValueError("movement parent does not match current lane")
                if not any([data["changes"], data["preserved"], data["next_movement"], data["walls"], data["evidence_refs"]]):
                    raise ValueError("movement has no recorded information")
                for field in ("changes", "preserved", "next_movement"):
                    if not isinstance(data[field], str):
                        raise ValueError(f"invalid {field}")
                lanes[lane_id] = replace(
                    prior,referent=required(data["referent"], "referent"),
                    latest_event_id=event_id,changes=data["changes"].strip(),
                    preserved=data["preserved"].strip(),
                    next_movement=data["next_movement"].strip(),
                    walls=strings(data["walls"], "walls"),
                    evidence_refs=strings(data["evidence_refs"], "evidence_refs"),
                    movements=prior.movements + 1,
                )
            elif event_type == "LANES_CONNECTED":
                if set(data) != {"from_lane", "to_lane", "relation", "evidence_refs"}:
                    raise ValueError("invalid lane connection")
                a, b = required(data["from_lane"], "from_lane"), required(data["to_lane"], "to_lane")
                if a == b or a not in lanes or b not in lanes:
                    raise ValueError("connection requires distinct existing lanes")
                links.append(Connection(event_id, a, b, required(data["relation"], "relation"), strings(data["evidence_refs"], "evidence_refs")))
            else:
                if set(data) != {"lane_id"}:
                    raise ValueError("invalid focus event")
                candidate = data["lane_id"]
                if candidate is not None and (not isinstance(candidate, str) or candidate not in lanes):
                    raise ValueError("focus references unknown lane")
                focus = candidate
        return lanes, links, focus

    def _append(self, kind: str, data: dict[str, Any]) -> str:
        record = {"event_id": f"ws_{uuid4().hex}", "event_type": kind,
                  "occurred_at": datetime.now(timezone.utc).isoformat(), "data": data}
        self._fold([*self._events, record])
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        self._events.append(record)
        return record["event_id"]

    def open_lane(self, lane_id: str, *, label: str, referent: str,
                  actor_id: str, sources: tuple[str, ...] = ()) -> Lane:
        self._append("LANE_OPENED", {"lane_id": lane_id, "label": label,
                                   "referent": referent, "actor_id": actor_id,
                                   "sources": list(sources)})
        return self.get_lane(lane_id)

    def record_movement(self, lane_id: str, *, referent: str | None = None,
                        changes: str = "", preserved: str = "", next_movement: str = "",
                        walls: tuple[str, ...] = (), evidence_refs: tuple[str, ...] = ()) -> Lane:
        lane = self.get_lane(lane_id)
        self._append("LANE_MOVED", {"lane_id": lane_id, "prior_event_id": lane.latest_event_id,
                                    "referent": lane.referent if referent is None else referent,
                                    "changes": changes, "preserved": preserved,
                                    "next_movement": next_movement,
                                    "walls": list(walls), "evidence_refs": list(evidence_refs)})
        return self.get_lane(lane_id)

    def connect(self, from_lane: str, to_lane: str, *, relation: str,
                evidence_refs: tuple[str, ...] = ()) -> Connection:
        eid = self._append("LANES_CONNECTED", {"from_lane": from_lane, "to_lane": to_lane,
                                              "relation": relation, "evidence_refs": list(evidence_refs)})
        return next(link for link in self.links() if link.event_id == eid)

    def set_focus(self, lane_id: str | None) -> None:
        self._append("FOCUS_SET", {"lane_id": lane_id})

    def lanes(self) -> tuple[Lane, ...]:
        return tuple(self._fold(self._events)[0].values())

    def get_lane(self, lane_id: str) -> Lane:
        lanes = self._fold(self._events)[0]
        return lanes[lane_id]

    def links(self) -> tuple[Connection, ...]:
        return tuple(self._fold(self._events)[1])

    def focused_lane(self) -> str | None:
        return self._fold(self._events)[2]

    def history(self, lane_id: str) -> tuple[dict[str, Any], ...]:
        self.get_lane(lane_id)
        return tuple(json.loads(json.dumps(e)) for e in self._events
                     if e["data"].get("lane_id") == lane_id or
                     (e["event_type"] == "LANES_CONNECTED" and lane_id in (e["data"]["from_lane"], e["data"]["to_lane"])))

    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(json.loads(json.dumps(e)) for e in self._events)
