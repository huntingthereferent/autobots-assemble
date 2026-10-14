"""Read-only workspace display; never emits work or changes focus."""
from __future__ import annotations

from .store import WorkspaceStore


def workspace_view(store: WorkspaceStore, *, actor_id: str | None = None) -> dict:
    focus = store.focused_lane()
    lanes = []
    for lane in store.lanes():
        if actor_id is not None and lane.actor_id != actor_id:
            continue
        lanes.append({
            "lane_id": lane.lane_id,
            "label": lane.label,
            "referent": lane.referent,
            "sources": list(lane.sources),
            "actor_id": lane.actor_id,
            "changes": lane.changes,
            "preserved": lane.preserved,
            "walls": list(lane.walls),
            "evidence_refs": list(lane.evidence_refs),
            "next_movement": lane.next_movement,
            "return_event_id": lane.latest_event_id,
            "movements": lane.movements,
            "focused": focus == lane.lane_id,
        })
    visible = {lane["lane_id"] for lane in lanes}
    return {"focused_lane": focus if focus in visible else None,
            "lanes": lanes,
            "connections": [
                {"event_id": e.event_id, "from_lane": e.from_lane,
                 "to_lane": e.to_lane, "relation": e.relation,
                 "evidence_refs": list(e.evidence_refs)}
                for e in store.links()
                if e.from_lane in visible and e.to_lane in visible
            ]}
