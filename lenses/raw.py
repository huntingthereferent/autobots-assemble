from __future__ import annotations

from network import Snapshot


def render_raw(snapshot: Snapshot) -> str:
    rows = [f"snapshot {snapshot.seq} @ {snapshot.frozen_at}"]
    for r in snapshot.relations:
        rows.append(
            f"{r.relation_id} | {r.subject} --{r.predicate}--> {r.object!r} | source={r.source}"
        )
    return "\n".join(rows)
