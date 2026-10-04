from __future__ import annotations

from dataclasses import asdict
import json

from network import Snapshot


def render_json(snapshot: Snapshot) -> str:
    return json.dumps(
        {
            "seq": snapshot.seq,
            "frozen_at": snapshot.frozen_at,
            "relations": [
                {"relation_id": r.relation_id, **asdict(r)}
                for r in snapshot.relations
            ],
        },
        indent=2,
        ensure_ascii=False,
        default=str,
    )
