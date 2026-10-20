"""A/B-owned rendering scene: projection of a *selected* finite math source.

This module prepares source-derived facts; it is not a visual engine, a
definition of A/B, an agent scheduler, or a WORLD physical solver. It writes
only the public, bounded projection when explicitly invoked.
"""
from __future__ import annotations

import argparse
from collections import deque
from hashlib import sha256
import json
from pathlib import Path

from work.arc_like_maze.math import World
from systems.workspace.ab_relational_cluster import _independent_step

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "live" / "ab-renderer-scene.json"
SOURCE = ROOT / "work" / "arc_like_maze" / "math.py"
SCHEMA = "ab-renderer/native-finite-scene/v1"
MAX_STATES = 128
EXAMPLE_ACTIONS = "ABAABBABA"


def scene() -> dict:
    """Build all actual finite edges and independently replay every step."""
    world = World(3, (0, 1, 2))
    observed = {world.origin: 0}
    queue = deque([world.origin])
    nodes = []
    while queue:
        state = queue.popleft()
        key = ",".join(map(str, state))
        transitions = {}
        for action in "AB":
            destination = world.step(state, action)
            if destination != _independent_step(state, action):
                raise ValueError("independent finite source/step verifier disagrees")
            transitions[action] = ",".join(map(str, destination))
            if destination not in observed:
                observed[destination] = observed[state] + 1
                if len(observed) > MAX_STATES:
                    raise ValueError("native source exceeds bounded renderer capacity")
                queue.append(destination)
        nodes.append({"id": key, "state": list(state),
                      "steps_from_origin": observed[state],
                      "transitions": transitions})
    if set(observed) != world.reachable():
        raise ValueError("native finite reachability mismatch")
    example = [",".join(map(str, world.origin))]
    current = world.origin
    for action in EXAMPLE_ACTIONS:
        current = world.step(current, action)
        if current != _independent_step(tuple(map(int, example[-1].split(","))), action):
            raise ValueError("example path independent replay mismatch")
        example.append(",".join(map(str, current)))
    return {
        "schema": SCHEMA,
        "model": "declared-finite-F3-cubed-phi012",
        "referent_scope": "specific finite model; not the A/B language referent",
        "source": "work/arc_like_maze/math.py::World",
        "source_sha256": sha256(SOURCE.read_bytes()).hexdigest(),
        "independent_verifier": "systems/workspace/ab_relational_cluster.py::_independent_step",
        "phi": [0, 1, 2],
        "origin": "0,0,0",
        "nodes": nodes,
        "node_count": len(nodes),
        "edge_count": len(nodes) * 2,
        "example_actions": EXAMPLE_ACTIONS,
        "example_states": example,
        "presentation_boundary": (
            "pixels, layout, colors, animation and tween are editorial; "
            "only discrete nodes/edges are math"
        ),
        "execution": "read-only projection; no workers or physics",
    }


def encoded() -> str:
    return json.dumps(scene(), sort_keys=True, indent=2, ensure_ascii=True) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Export/check A/B native scene")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    output = scene()
    if args.check:
        if not OUT.is_file() or json.loads(OUT.read_text(encoding="utf-8")) != output:
            raise SystemExit("native A/B renderer scene has changed or is incomplete")
        print("A/B-owned finite renderer scene verifies against native model")
    else:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(encoded(), encoding="utf-8")
        print(f"wrote {output['node_count']} nodes / {output['edge_count']} source edges")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
