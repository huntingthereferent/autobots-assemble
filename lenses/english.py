from __future__ import annotations

from network import Snapshot


def render_english(snapshot: Snapshot) -> str:
    if not snapshot.relations:
        return "No recorded relations."
    lines = [f"Snapshot {snapshot.seq} contains {len(snapshot.relations)} recorded relation(s):"]
    for r in snapshot.relations:
        lines.append(
            f"- {r.subject} — {r.predicate} → {r.object!r} "
            f"(source: {r.source}; id: {r.relation_id})"
        )
    return "\n".join(lines)
