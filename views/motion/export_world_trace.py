"""Export an inspectable trace from the existing finite World model.

Run from repository root:
    python -m views.motion.export_world_trace
"""
import json
from pathlib import Path
from work.arc_like_maze.math import World

OUTPUT = Path(__file__).resolve().parents[2] / "docs" / "live" / "finite-world-trace.json"

def build_trace(steps=60):
    world = World(3, (0, 1, 2))
    state = world.origin
    rows = [[0, "", *state]]
    actions = "AABABB"
    for index in range(1, steps + 1):
        action = actions[(index - 1) % len(actions)]
        state = world.step(state, action)
        rows.append([index, action, *state])
    return {
        "source": "work/arc_like_maze/math.py",
        "world": {"depth": 3, "phi": [0, 1, 2]},
        "columns": ["index", "action", "x", "y", "z"],
        "rows": rows,
    }

if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build_trace(), indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)
