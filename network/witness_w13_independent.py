"""WITNESS W13: independent two-room session replay and receipt inspection.

Oracle: WORLD W13 Movement 01 and byte-pinned ORIGINAL W12 transition source.
No import of BUILD's W13 engine, receipt verifier, reference builder, or tests.
Local browser evidence remains unauthenticated as to origin.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from systems.workspace import game_construction as original_w12

W12_SOURCE_SHA256 = "dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1"
W13_VERSION = "game-w13-multiworld-v1"
WORLD_CONTRACT = (
    ("first-room", {"width": 4, "height": 3, "start": [0, 1], "target": [2, 1]}),
    ("second-room", {"width": 3, "height": 3, "start": [0, 0], "target": [1, 1]}),
)
VERBS = frozenset(("up", "down", "left", "right", "interact"))


def strict_json(raw: str) -> Any:
    """Reject duplicate object keys and JSON NaN/Infinity, before verification."""
    def unique(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError(f"duplicate JSON key: {key}")
            obj[key] = value
        return obj
    def reject_constant(value):
        raise ValueError(f"non-JSON numeric constant {value}")
    return json.loads(raw, object_pairs_hook=unique, parse_constant=reject_constant)


def equivalent(a: Any, b: Any) -> bool:
    """Canonical comparison prevents accepting false as zero, 4 as 4.0."""
    return json.dumps(a, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) == json.dumps(
        b, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def shape(obj: Any, keys: set[str], label: str) -> None:
    if type(obj) is not dict or set(obj) != keys:
        raise ValueError(f"incorrect {label} shape")


def independent_w13_replay(receipt: Any) -> dict:
    """Strictly compare *all* recorded session data to a fresh independent run.

    World identity, session step order, cross-world transition and every local
    before/action/after/verdict are reconstructed from the WORLD contract and
    preserved W12 transition source, not BUILD's W13 code or fixtures.
    """
    digest = sha256(Path(original_w12.__file__).read_bytes()).hexdigest()
    if digest != W12_SOURCE_SHA256:
        raise ValueError("original W12 source fingerprint changed")

    shape(receipt, {"version", "worlds", "actions", "boundaries", "final"}, "session")
    if type(receipt["version"]) is not str or receipt["version"] != W13_VERSION:
        raise ValueError("unexpected W13 version")
    if type(receipt["worlds"]) is not list or len(receipt["worlds"]) != 2:
        raise ValueError("WORLD W13 requires exactly two worlds")
    if type(receipt["actions"]) is not list or len(receipt["actions"]) > 150:
        raise ValueError("W13 action count invalid")
    if type(receipt["boundaries"]) is not list:
        raise ValueError("boundary list is missing")

    specs = [
        original_w12.GameSpec(s["width"], s["height"], tuple(s["start"]), tuple(s["target"]))
        for _, s in WORLD_CONTRACT
    ]
    for spec in specs:
        spec.validate()
    states = [original_w12.first_state(spec) for spec in specs]
    actual_actions = [[], []]
    actual_observations = [[], []]
    expected_boundaries = []
    at = 0

    for action_index, action in enumerate(receipt["actions"]):
        if type(action) is not str:
            raise ValueError(f"non-string action at {action_index}")
        if action == "advance":
            if at != 0 or not states[at].collected:
                raise ValueError("advance requires completed first world and unused next world")
            expected_boundaries.append({
                "action": "advance",
                "from_world": WORLD_CONTRACT[0][0],
                "to_world": WORLD_CONTRACT[1][0],
                "before": {"world_id": WORLD_CONTRACT[0][0], "state": asdict(states[0])},
                "after": {"world_id": WORLD_CONTRACT[1][0], "state": asdict(states[1])},
            })
            at = 1
            continue
        if action not in VERBS:
            raise ValueError(f"unrecognized W12 action {action}")
        before = asdict(states[at])
        updated, verdict = original_w12.transition(specs[at], states[at], action)
        states[at] = updated
        actual_actions[at].append(action)
        actual_observations[at].append({
            "action": action, "before": before,
            "after": asdict(updated), "verdict": verdict,
        })

    if not equivalent(receipt["boundaries"], expected_boundaries):
        raise ValueError("W13 boundary does not match independent session replay")

    # Re-run original W12 hash-chained native source separately to confirm
    # per-world trace ancestry; *do not* rely on BUILD's W13 verifier.
    proof = []
    for index, ((world_id, declared), spec) in enumerate(zip(WORLD_CONTRACT, specs)):
        row = receipt["worlds"][index]
        shape(row, {"id", "version", "spec", "actions", "observations", "final"}, f"world {index}")
        if type(row["id"]) is not str or row["id"] != world_id:
            raise ValueError(f"world identity or ordering mismatch at {index}")
        if type(row["version"]) is not str or row["version"] != original_w12.VERSION:
            raise ValueError(f"W12 version mismatch in world {index}")
        shape(row["spec"], {"width", "height", "start", "target"}, f"world {index} spec")
        if not equivalent(row["spec"], declared):
            raise ValueError(f"world {index} spec not declared by WORLD")
        if type(row["actions"]) is not list or not equivalent(row["actions"], actual_actions[index]):
            raise ValueError(f"world {index} actions do not match session")
        if type(row["observations"]) is not list or len(row["observations"]) != len(actual_observations[index]):
            raise ValueError(f"world {index} observations missing")
        for n, (observed, expected) in enumerate(zip(row["observations"], actual_observations[index])):
            shape(observed, {"action", "before", "after", "verdict"}, f"world {index} step {n}")
            shape(observed["before"], {"x", "y", "collected", "turns"}, "before")
            shape(observed["after"], {"x", "y", "collected", "turns"}, "after")
            if not equivalent(observed, expected):
                raise ValueError(f"world {index} observation {n} contradicts W12 transition")
        shape(row["final"], {"x", "y", "collected", "turns"}, f"world {index} final")
        if not equivalent(row["final"], asdict(states[index])):
            raise ValueError(f"world {index} saved final differs from replay")
        trace = original_w12.run_actions(actual_actions[index], spec)
        if not original_w12.verify_trace(trace)["valid"]:
            raise ValueError(f"W12 native trace rejected world {index}")
        if not equivalent(trace["final"], asdict(states[index])):
            raise ValueError(f"world {index} replay/trace discrepancy")
        proof.append({
            "world_id": world_id,
            "actions_verified": len(actual_actions[index]),
            "native_head_hash": trace["head_hash"],
            "solved": states[index].collected,
        })

    solved = at == 1 and all(state.collected for state in states)
    expected_final = {
        "world_id": WORLD_CONTRACT[at][0],
        "state": asdict(states[at]),
        "worlds_completed": sum(int(s.collected) for s in states),
        "solved": solved,
    }
    shape(receipt["final"], {"world_id", "state", "worlds_completed", "solved"}, "session final")
    shape(receipt["final"]["state"], {"x", "y", "collected", "turns"}, "session final state")
    if not equivalent(receipt["final"], expected_final):
        raise ValueError("session final disagrees with independent W12 replay")
    return {
        "witness": "independent-WORLD-W13-plus-original-W12-native-replay",
        "source_sha256": digest,
        "valid": True,
        "solved": solved,
        "worlds_completed": expected_final["worlds_completed"],
        "cursor": expected_final["world_id"],
        "boundaries_checked": len(expected_boundaries),
        "per_world": proof,
        "browser_origin_authenticated": False,
        "w13_checkpoint_promoted": False,
    }
