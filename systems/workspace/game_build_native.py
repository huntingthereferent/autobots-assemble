"""Independent WORLD->BUILD verifier over preserved W12 native movement rules."""
from __future__ import annotations

from collections import deque
from hashlib import sha256
import json
import re
from pathlib import Path

from . import game_construction as w12

VERSION = "game-built-room-v1"
WORKER_ID = "game-room-builder"
VERIFIER = "game-built-room-w12-independent-v1"
W12_SHA256 = "dcf457efd0bf9bd93823ad862e8f1f315b20f46334dd323a1d467a820c3f5ac1"
STEP_ORDER = ("right", "down", "left", "up", "interact")


def check_world(world):
    if type(world) is not dict or set(world) != {"contract", "world_id", "spec"}:
        raise ValueError("WORLD contract fields differ")
    name = world["world_id"]
    if world["contract"] != VERSION or type(name) is not str or not re.fullmatch(r"[a-z][a-z0-9-]{0,25}", name):
        raise ValueError("invalid WORLD room identity")
    data = world["spec"]
    if type(data) is not dict or set(data) != {"width", "height", "start", "target"}:
        raise ValueError("WORLD spec fields differ")
    if any(type(data[k]) is not int or not 3 <= data[k] <= 9 for k in ("width", "height")):
        raise ValueError("WORLD dimensions outside scope")
    for name in ("start", "target"):
        value = data[name]
        if type(value) is not list or len(value) != 2 or any(type(x) is not int for x in value):
            raise ValueError("WORLD coordinates must be integer pairs")
    spec = w12.GameSpec(data["width"], data["height"], tuple(data["start"]), tuple(data["target"]))
    spec.validate()
    if sha256(Path(w12.__file__).read_bytes()).hexdigest() != W12_SHA256:
        raise ValueError("original W12 game rules have changed")
    return world


def shortest_steps(spec):
    """Host independently explores original W12 transitions, not worker solver."""
    first = w12.first_state(spec)
    queue = deque([(first, 0)])
    seen = {(first.x, first.y, first.collected)}
    while queue:
        state, depth = queue.popleft()
        if state.collected:
            return depth
        for action in STEP_ORDER:
            nxt, _ = w12.transition(spec, state, action)
            key = (nxt.x, nxt.y, nxt.collected)
            if key not in seen:
                seen.add(key)
                queue.append((nxt, depth + 1))
    raise ValueError("WORLD has no reachable collectible")


def verify_build(world, result):
    """Worker output must be a NEW playable artifact plus checked solution."""
    check_world(world)
    if type(result) is not dict or set(result) != {"world", "plan", "html", "build_contract", "built_playable"}:
        raise ValueError("BUILD response fields differ")
    if (result["world"] != world or result["build_contract"] != VERSION
            or result["built_playable"] is not True):
        raise ValueError("BUILD modified WORLD request")
    actions, html = result["plan"], result["html"]
    if (type(actions) is not list or len(actions) > 30 or
            any(type(x) is not str or x not in STEP_ORDER for x in actions)):
        raise ValueError("BUILD plan is not a bounded W12 action sequence")
    specdata = world["spec"]
    spec = w12.GameSpec(specdata["width"], specdata["height"],
                        tuple(specdata["start"]), tuple(specdata["target"]))
    # Each transition is re-run against original W12, not the builder's output.
    state = w12.first_state(spec)
    for action in actions:
        if state.collected:
            raise ValueError("BUILD continued after completion")
        state, _ = w12.transition(spec, state, action)
    if not state.collected or len(actions) != shortest_steps(spec):
        raise ValueError("BUILD does not solve WORLD with a shortest W12-native path")
    if type(html) is not str or not 1000 < len(html) < 14500:
        raise ValueError("BUILD playable HTML absent or oversized")
    found = re.findall(r'<script id="world-config" type="application/json">([^<]+)</script>', html)
    if len(found) != 1:
        raise ValueError("BUILD playable room has no unique WORLD source")
    try:
        data = json.loads(found[0])
    except ValueError as exc:
        raise ValueError("BUILD browser data malformed") from exc
    if data != world:
        raise ValueError("BUILD playable room disagrees with WORLD source")
    for marker in ('id="grid"', 'id="status"', 'id="reset"', 'id="interact"',
                   'id="up"', 'id="down"', 'id="left"', 'id="right"',
                   'data-solved', "WORLD COMPLETE"):
        if marker not in html:
            raise ValueError("BUILD is missing essential playable interactions")
    return {"contract": VERSION, "world_id": world["world_id"],
            "w12_native_replay": "PASS",
            "shortest_solve_actions": len(actions),
            "html_sha256": sha256(html.encode("utf8")).hexdigest(),
            "world_sha256": sha256(json.dumps(world, sort_keys=True,
                                            separators=(",", ":")).encode()).hexdigest()}
