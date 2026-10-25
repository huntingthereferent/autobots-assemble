"""Export an inspectable trace from the existing finite World model.

Run from repository root:
    python -m views.motion.export_world_trace
"""
import json
from pathlib import Path
from work.arc_like_maze.math import World

OUTPUT = Path(__file__).resolve().parents[2] / "docs" / "live" / "finite-world-trace.json"

def build_trace(steps=108):
    world = World(3, (0, 1, 2))
    state = world.origin
    records = [{"index": 0, "state": list(state), "action": None, "verified": True}]
    actions = "AABABB"
    for index in range(1, steps + 1):
        action = actions[(index - 1) % len(actions)]
        before = state
        state = world.step(before, action)
        verified = state in world.reachable() and state == world.step(before, action)
        records.append({"index": index, "before": list(before), "action": action, "state": list(state), "verified": verified})
    return {
        "model": "work.arc_like_maze.math.World",
        "parameters": {"depth": 3, "phi": [0, 1, 2]},
        "actions": actions,
        "geometry": "Finite F_3^3 coordinate projection, not a smooth manifold",
        "reachable_count": len(world.reachable()),
        "records": records,
    }

if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build_trace(), indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)
