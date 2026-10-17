"""Finite source-owned two-room W13 game worker, standalone Python source.

This copied subprocess has no runtime, coordinator, trusted keys, or network
access by contract (no OS sandbox). It only computes one declared game path.
Its JSON is NOT accepted until the host replays original W12 separately.
"""
import json
import os
import sys

VERSION = "game-w13-multiworld-v1"
CP = "GAME-W13-WORLDS"
W12_SHA256 = "dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1"
WORLDS = [
    {"id": "first-room", "spec": {"width": 4, "height": 3, "start": [0, 1], "target": [2, 1]}},
    {"id": "second-room", "spec": {"width": 3, "height": 3, "start": [0, 0], "target": [1, 1]}}
]
ACTIONS = ["right", "interact", "advance", "right", "interact"]
W12_VERSION = "game-construction-v0"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def compute(payload):
    if type(payload) is not dict or set(payload) != {"contract", "worlds", "actions", "w12_sha256"}:
        raise ValueError("incorrect game native request schema")
    if (payload["contract"] != VERSION or payload["w12_sha256"] != W12_SHA256
            or canonical(payload["worlds"]) != canonical(WORLDS)
            or canonical(payload["actions"]) != canonical(ACTIONS)):
        raise ValueError("native request outside WORLD W13 Movement 01")
    states = [
        {"x": w["spec"]["start"][0], "y": w["spec"]["start"][1],
         "collected": False, "turns": 0}
        for w in WORLDS
    ]
    segments = [[], []]
    observations = [[], []]
    boundaries = []
    current = 0
    for action in ACTIONS:
        state = states[current]
        if action == "advance":
            if not state["collected"] or current != 0:
                raise ValueError("advance boundary invalid")
            before = {"world_id": WORLDS[0]["id"], "state": dict(state)}
            current = 1
            after = {"world_id": WORLDS[1]["id"], "state": dict(states[1])}
            boundaries.append({"action": "advance", "from_world": WORLDS[0]["id"],
                               "to_world": WORLDS[1]["id"], "before": before, "after": after})
            continue
        before = dict(state)
        spec = WORLDS[current]["spec"]
        if action == "right":
            if state["x"] + 1 < spec["width"]:
                state["x"] += 1
                verdict = "moved"
            else:
                verdict = "blocked-by-boundary"
        elif action == "interact":
            target = spec["target"]
            adjacent = abs(target[0] - state["x"]) + abs(target[1] - state["y"]) == 1
            if state["collected"]:
                verdict = "already-collected"
            elif adjacent:
                state["collected"] = True
                verdict = "collected"
            else:
                verdict = "out-of-reach"
        else:
            raise ValueError("unknown game source action")
        state["turns"] += 1
        segments[current].append(action)
        observations[current].append({
            "action": action, "before": before, "after": dict(state), "verdict": verdict,
        })
    if not all(s["collected"] for s in states) or len(boundaries) != 1:
        raise ValueError("bounded two-world result is incomplete")
    worlds = []
    for i, world in enumerate(WORLDS):
        worlds.append({"id": world["id"], "version": W12_VERSION,
                       "spec": world["spec"], "actions": segments[i],
                       "observations": observations[i], "final": states[i]})
    receipt = {"version": VERSION, "worlds": worlds, "actions": ACTIONS,
               "boundaries": boundaries,
               "final": {"world_id": WORLDS[1]["id"], "state": states[1],
                         "worlds_completed": 2, "solved": True}}
    return {"receipt": receipt, "pid": os.getpid()}


if __name__ == "__main__":
    try:
        raw = sys.stdin.read(4097)
        if len(raw) > 4096:
            raise ValueError("source input too large")
        print(json.dumps(compute(json.loads(raw)), sort_keys=True, separators=(",", ":")))
    except (ValueError, TypeError, KeyError) as exc:
        print(type(exc).__name__ + ": " + str(exc), file=sys.stderr)
        sys.exit(2)
