"""BUILD W13 bounded browser-session receipt: native W12 replay and exact join.

The October 15 W13 composition *candidate* is not imported to verify
receipts. This verifier compares browser evidence to the original W12
source and WORLD W13 Movement 01. No browser-origin authentication or
independent WITNESS certification is implied.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from . import game_construction as w12

VERSION = "game-w13-multiworld-v1"
W12_SHA256 = "dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1"
WORLDS = (
    {"id": "first-room", "spec": {"width": 4, "height": 3, "start": [0, 1], "target": [2, 1]}},
    {"id": "second-room", "spec": {"width": 3, "height": 3, "start": [0, 0], "target": [1, 1]}},
)
LOCAL_ACTIONS = frozenset({"up", "down", "left", "right", "interact"})


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _equal(a: Any, b: Any) -> bool:
    # Canonical JSON distinguishes False/0, float/int and nested schema order.
    return canonical(a) == canonical(b)


def _keys(value: Any, expected: set[str], where: str) -> None:
    if type(value) is not dict or set(value) != expected:
        raise ValueError(f"{where} has missing or unexpected fields")


def _spec(data: dict) -> w12.GameSpec:
    _keys(data, {"width", "height", "start", "target"}, "world spec")
    if any(type(data[k]) is not int for k in ("width", "height")):
        raise ValueError("world dimensions must be exact integers")
    for key in ("start", "target"):
        if type(data[key]) is not list or len(data[key]) != 2 or any(type(v) is not int for v in data[key]):
            raise ValueError("world coordinates must be exact integer lists")
    obj = w12.GameSpec(data["width"], data["height"], tuple(data["start"]), tuple(data["target"]))
    obj.validate()
    return obj


def verify_session_receipt(receipt: dict[str, Any]) -> dict[str, Any]:
    """Verify partial or complete W13 receipts without granting W13 CP PASS."""
    source = Path(w12.__file__).read_bytes()
    if sha256(source).hexdigest() != W12_SHA256:
        raise ValueError("original W12 rules changed")

    _keys(receipt, {"version", "worlds", "actions", "boundaries", "final"}, "W13 receipt")
    if receipt["version"] != VERSION:
        raise ValueError("wrong W13 version")
    records, actions, boundaries = receipt["worlds"], receipt["actions"], receipt["boundaries"]
    if type(records) is not list or len(records) != 2:
        raise ValueError("W13 must contain exactly two declared worlds")
    if type(actions) is not list or len(actions) > 150 or any(type(a) is not str or a not in LOCAL_ACTIONS | {"advance"} for a in actions):
        raise ValueError("invalid W13 action sequence")
    if type(boundaries) is not list:
        raise ValueError("invalid W13 boundary records")

    traces = []
    for index, record in enumerate(records):
        _keys(record, {"id", "version", "spec", "actions", "observations", "final"}, f"world {index}")
        expected = WORLDS[index]
        if type(record["id"]) is not str or record["id"] != expected["id"] or record["version"] != w12.VERSION:
            raise ValueError("world identity/version mismatch")
        _spec(record["spec"])
        if not _equal(record["spec"], expected["spec"]):
            raise ValueError("world specification mismatch")
        local_actions = record["actions"]
        observations = record["observations"]
        if type(local_actions) is not list or any(type(a) is not str or a not in LOCAL_ACTIONS for a in local_actions):
            raise ValueError("invalid local actions")
        if type(observations) is not list or len(observations) != len(local_actions):
            raise ValueError("local observation count mismatch")

        trace = w12.run_actions(local_actions, _spec(record["spec"]))
        w12.verify_trace(trace)
        for n, (actual, expected_row) in enumerate(zip(observations, trace["steps"]), 1):
            _keys(actual, {"action", "before", "after", "verdict"}, f"world {index} observation {n}")
            _keys(actual["before"], {"x", "y", "collected", "turns"}, "local before")
            _keys(actual["after"], {"x", "y", "collected", "turns"}, "local after")
            expected_obs = {k: expected_row[k] for k in ("action", "before", "after", "verdict")}
            if not _equal(actual, expected_obs):
                raise ValueError(f"world {index} native observation mismatch at {n}")
        _keys(record["final"], {"x", "y", "collected", "turns"}, "world final")
        if not _equal(record["final"], trace["final"]):
            raise ValueError(f"world {index} final disagrees with W12 native replay")
        traces.append(trace)

    n_advances = actions.count("advance")
    if n_advances not in (0, 1):
        raise ValueError("cannot advance twice")
    if n_advances == 0:
        if records[1]["actions"] or boundaries:
            raise ValueError("second world cannot move before advance")
        current_index = 0
        ordered = records[0]["actions"]
    else:
        if not traces[0]["solved"]:
            raise ValueError("advance requires collected first world")
        current_index = 1
        ordered = records[0]["actions"] + ["advance"] + records[1]["actions"]
        if len(boundaries) != 1:
            raise ValueError("one advance requires exactly one boundary")
        expected_boundary = {
            "action": "advance",
            "from_world": WORLDS[0]["id"],
            "to_world": WORLDS[1]["id"],
            "before": {"world_id": WORLDS[0]["id"], "state": traces[0]["final"]},
            "after": {"world_id": WORLDS[1]["id"], "state": asdict(w12.first_state(_spec(WORLDS[1]["spec"])))},
        }
        _keys(boundaries[0], set(expected_boundary), "advance boundary")
        if not _equal(boundaries[0], expected_boundary):
            raise ValueError("advance boundary disagrees with W12 replay")
    if not _equal(actions, ordered):
        raise ValueError("global/local action sequence mismatch")

    solved = current_index == 1 and all(trace["solved"] for trace in traces)
    finished = {
        "world_id": WORLDS[current_index]["id"],
        "state": traces[current_index]["final"],
        "worlds_completed": sum(int(t["solved"]) for t in traces),
        "solved": solved,
    }
    _keys(receipt["final"], set(finished), "session final")
    if not _equal(receipt["final"], finished):
        raise ValueError("session final disagrees with native replay")
    return {
        "valid": True,
        "version": VERSION,
        "solved": solved,
        "worlds_completed": finished["worlds_completed"],
        "world_proofs": [
            {"world_id": record["id"], "head_hash": trace["head_hash"],
             "steps_verified": len(trace["steps"]), "collected": trace["solved"]}
            for record, trace in zip(records, traces)
        ],
        "boundary_verified": n_advances == 1,
        "evidence_depth": "native-W12-replay-of-untrusted-browser-receipt",
    }


def build_reference_receipt(actions: list[str]) -> dict[str, Any]:
    """BUILD-only deterministic fixture generator; not a browser witness."""
    if type(actions) is not list or any(type(a) is not str or a not in LOCAL_ACTIONS | {"advance"} for a in actions):
        raise ValueError("invalid actions")
    if actions.count("advance") > 1:
        raise ValueError("too many advances")
    crossed = "advance" in actions
    if crossed:
        idx = actions.index("advance")
        segments = (actions[:idx], actions[idx + 1:])
    else:
        segments = (actions, [])
    traces = [w12.run_actions(seq, _spec(world["spec"])) for seq, world in zip(segments, WORLDS)]
    if crossed and not traces[0]["solved"]:
        raise ValueError("advance requires completed first world")
    current = 1 if crossed else 0
    records = []
    for world, seq, trace in zip(WORLDS, segments, traces):
        records.append({
            "id": world["id"], "version": w12.VERSION,
            # Never expose mutable WORLDS source dictionaries to test fixtures.
            "spec": json.loads(canonical(world["spec"])),
            "actions": list(seq),
            "observations": [
                {k: row[k] for k in ("action", "before", "after", "verdict")}
                for row in trace["steps"]
            ], "final": trace["final"],
        })
    boundaries = []
    if crossed:
        boundaries.append({
            "action": "advance",
            "from_world": WORLDS[0]["id"], "to_world": WORLDS[1]["id"],
            "before": {"world_id": WORLDS[0]["id"], "state": traces[0]["final"]},
            "after": {"world_id": WORLDS[1]["id"], "state": asdict(w12.first_state(_spec(WORLDS[1]["spec"])))},
        })
    receipt = {
        "version": VERSION, "worlds": records, "actions": list(actions),
        "boundaries": boundaries,
        "final": {
            "world_id": WORLDS[current]["id"], "state": traces[current]["final"],
            "worlds_completed": sum(int(t["solved"]) for t in traces),
            "solved": current == 1 and all(t["solved"] for t in traces),
        },
    }
    verify_session_receipt(receipt)
    return receipt
