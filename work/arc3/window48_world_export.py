"""Playable depth-three WORLD48 export from the existing proved F3 laws.

This is a finite mathematical world, not a native ARC game, a replacement W13
runtime, or an inferred map from SDK controls to F3 letters. All transition
tables and receipt verdicts are derived from the original CombinedWorld.
"""
from __future__ import annotations

import argparse
from itertools import product
import json
from pathlib import Path

from work.arc_like_maze.window_combined import family

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "docs/window48_world_data.json"
SCHEMA = "original-window48-depth3-game-world/v1"
RECEIPT = "original-window48-depth3-browser-receipt/v1"
SCOPE = "finite-mathematical-source-only"
STATES = tuple(product(range(3), repeat=3))


def state_index(s: tuple[int, ...]) -> int:
    if len(s) != 3 or any(type(x) is not int or x not in (0, 1, 2) for x in s):
        raise ValueError("state must be exactly three F3 coordinates")
    return 9 * s[0] + 3 * s[1] + s[2]


def build_manifest() -> dict:
    worlds = family()
    if len(worlds) != 48 or len(set(worlds)) != 48:
        raise AssertionError("original 48-law source changed")
    laws = []
    for n, w in enumerate(worlds):
        laws.append({
            "id": n, "support": w.support, "pulse": w.pulse,
            "balanced": w.balanced, "coefficient": w.coefficient,
            "rooted_class": [w.support, w.pulse, w.balanced],
            "A": [state_index(w.step(s, "A")) for s in STATES],
            "B": [state_index(w.step(s, "B")) for s in STATES],
        })
    return {
        "schema": SCHEMA,
        "source": "work/arc_like_maze/window_combined.py",
        "scope": SCOPE,
        "depth": 3,
        "marked_origin": [0, 0, 0],
        "root_index": 0,
        "concrete_laws": 48,
        "rooted_classes": 16,
        "full_state_classes": 14,
        "laws": laws,
    }


def verify_receipt(record: dict) -> dict:
    """Independent original-source replay of an actual browser export.

    Matching the exported finite actions proves only this mathematical
    representation; it does not authenticate a native ARC observation.
    """
    if type(record) is not dict or set(record) != {
        "schema", "scope", "law_ids", "root_index", "actions", "events", "final"
    } or record["schema"] != RECEIPT or record["scope"] != SCOPE:
        raise ValueError("incorrect or unbounded WORLD48 browser receipt")
    ids = record["law_ids"]
    if (type(ids) is not list or len(ids) != 2 or
            any(type(i) is not int or not 0 <= i < 48 for i in ids)):
        raise ValueError("two original 48-law IDs required")
    if record["root_index"] != 0 or type(record["root_index"]) is not int:
        raise ValueError("marked origin changed")
    actions = record["actions"]
    events = record["events"]
    if (type(actions) is not str or len(actions) > 128 or
            any(a not in "AB" for a in actions) or
            type(events) is not list or len(events) != len(actions)):
        raise ValueError("bounded A/B word and matching native UI events required")
    worlds = family()
    states = [(0, 0, 0), (0, 0, 0)]
    for n, (action, event) in enumerate(zip(actions, events)):
        if type(event) is not dict or set(event) != {"action", "before", "after"}:
            raise ValueError("event shape changed")
        if event["action"] != action:
            raise ValueError("browser action sequence differs")
        before = [state_index(s) for s in states]
        states = [worlds[ids[i]].step(states[i], action) for i in range(2)]
        after = [state_index(s) for s in states]
        if event["before"] != before or event["after"] != after:
            raise ValueError(f"original source transition refuted browser event {n}")
    expected = [state_index(s) for s in states]
    if record["final"] != expected:
        raise ValueError("browser final state differs from original source")
    return {"valid": True, "scope": SCOPE, "steps": len(actions),
            "law_ids": ids, "final": expected}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=DEST)
    args = parser.parse_args()
    generated = build_manifest()
    if args.check:
        if not args.out.is_file() or json.loads(args.out.read_text()) != generated:
            raise SystemExit("WORLD48 manifest differs from the ORIGINAL mathematics")
        print("WORLD48 original-source manifest verified: 48 laws x 27 states x 2 actions")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(generated, indent=2) + "\n", encoding="utf8")
        print(f"Exported {len(generated['laws'])} exact laws to {args.out}")


if __name__ == "__main__":
    main()
