"""Build Godot's presentation data from the ORIGINAL finite A/B World.

This does not define A/B. The finite F_3^3 model is an explicitly scoped
example, and graph layout/interpolated pixels are not mathematical motion.
Only verified World.step transitions become drawable edges.
"""
from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path
import json

from work.arc_like_maze.math import World

HERE = Path(__file__).resolve().parent
OUT = HERE / "data" / "finite_f3_phi012.json"
SCHEMA = "ab-native-finite-godot/v1"
MODEL = World(3, (0, 1, 2))
DEMO = "ABAABBABA"
MAX_STATES = 128


def manifest() -> dict:
    world = MODEL
    origin = world.origin
    queue = deque([origin])
    depth = {origin: 0}
    states = []
    while queue:
        current = queue.popleft()
        states.append(current)
        for action in "AB":
            dest = world.step(current, action)
            if dest not in depth:
                depth[dest] = depth[current] + 1
                if len(depth) > MAX_STATES:
                    raise ValueError("finite visualization source exceeded bound")
                queue.append(dest)
    if set(states) != set(world.reachable()):
        raise ValueError("breadth-first traversal failed native reachability")
    nodes = [
        {"state": list(current), "depth": depth[current],
         "A": list(world.step(current, "A")),
         "B": list(world.step(current, "B"))}
        for current in states
    ]
    trace = [list(origin)]
    current = origin
    for action in DEMO:
        current = world.step(current, action)
        trace.append(list(current))
    return {
        "schema": SCHEMA,
        "referent": "declared finite F3^3 example, not universal A/B",
        "source": "work.arc_like_maze.math.World",
        "phi": list(world.phi),
        "depth": world.depth,
        "origin": list(origin),
        "state_count": len(states),
        "nodes": nodes,
        "demo_actions": DEMO,
        "demo_states": trace,
        "positions": "editorial BFS-depth projection; no physical distance claim",
        "tween": "visual interpolation only; no intermediate finite state",
        "native_execution": "finite Python model computed, not Godot physics",
    }


def serialized() -> str:
    return json.dumps(manifest(), indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Export/check native finite Godot projection")
    parser.add_argument("--check", action="store_true",
                        help="assert existing dataset is byte-for-byte native-generated")
    args = parser.parse_args(argv)
    text = serialized()
    if args.check:
        if not OUT.is_file() or OUT.read_text(encoding="utf-8") != text:
            raise SystemExit("Godot finite dataset differs from native World; regenerate")
        print("Godot dataset matches native finite World")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"Recorded {manifest()['state_count']} native finite states at {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
