"""WORLD-CONTROLLED-TRACE-001: deterministic policy trace under controlled reset.

A tiny local grid world verifies reset/seed trace reproducibility. This is a
harness control, not evidence about real game agents or general environments.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from datetime import datetime, timezone
from pathlib import Path

WIDTH = 6
HEIGHT = 6
START = (0, 0)
GOAL = (5, 5)
MAX_STEPS = 40
ACTIONS = ((0, 1, "down"), (1, 0, "right"), (0, -1, "up"), (-1, 0, "left"))


def reset(seed: int) -> dict:
    rng = random.Random(seed)
    obstacles = set()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if (x, y) in (START, GOAL):
                continue
            if rng.random() < 0.18:
                obstacles.add((x, y))
    return {"seed": seed, "obstacles": sorted([list(p) for p in obstacles])}


def run_policy(seed: int) -> dict:
    world = reset(seed)
    obstacles = {tuple(p) for p in world["obstacles"]}
    rng = random.Random(seed ^ 0x5A17)
    position = START
    visited = {position}
    trace = [{"step": 0, "position": list(position), "action": "reset"}]
    for step in range(1, MAX_STEPS + 1):
        valid = []
        for dx, dy, name in ACTIONS:
            candidate = (position[0] + dx, position[1] + dy)
            if (0 <= candidate[0] < WIDTH and 0 <= candidate[1] < HEIGHT
                    and candidate not in obstacles and candidate not in visited):
                valid.append((candidate, name))
        if not valid:
            trace.append({"step": step, "position": list(position), "action": "stuck"})
            break
        # Fixed policy: seeded uniform choice among unvisited valid moves.
        position, action = valid[rng.randrange(len(valid))]
        visited.add(position)
        trace.append({"step": step, "position": list(position), "action": action})
        if position == GOAL:
            break
    encoded = json.dumps(trace, separators=(",", ":"), sort_keys=True).encode()
    return {
        "seed": seed,
        "world_sha256": hashlib.sha256(
            json.dumps(world, separators=(",", ":"), sort_keys=True).encode()
        ).hexdigest(),
        "trace_sha256": hashlib.sha256(encoded).hexdigest(),
        "steps": len(trace) - 1,
        "reached_goal": position == GOAL,
        "trace": trace,
    }


def build_receipt() -> dict:
    seeds = [17, 17, 23]
    runs = [run_policy(seed) for seed in seeds]
    same_seed_same_trace = runs[0]["trace"] == runs[1]["trace"]
    different_seed_different_world = runs[0]["world_sha256"] != runs[2]["world_sha256"]
    return {
        "schema_version": 1,
        "experiment_id": "WORLD-CONTROLLED-TRACE-001",
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "CONTROL_PASS" if same_seed_same_trace and different_seed_different_world else "CONTROL_FAIL",
        "question": "Does a fixed seeded policy reproduce its trace when the world is reset to the same seed?",
        "environment": {"kind": "local_grid_world", "width": WIDTH, "height": HEIGHT,
                        "start": list(START), "goal": list(GOAL), "max_steps": MAX_STEPS,
                        "obstacle_probability": 0.18},
        "policy": "seeded uniform choice among valid unvisited cardinal neighbors",
        "runs": [{"seed": run["seed"], "world_sha256": run["world_sha256"],
                  "trace_sha256": run["trace_sha256"], "steps": run["steps"],
                  "reached_goal": run["reached_goal"], "trace": run["trace"]} for run in runs],
        "controls": {
            "same_seed_same_trace": same_seed_same_trace,
            "different_seed_different_world": different_seed_different_world,
        },
        "limits": [
            "Synthetic local environment only; no real game or external agent tested.",
            "Trace reproducibility does not imply task competence or safety.",
            "A seeded stochastic policy is used so the random stream is part of the controlled reset.",
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = build_receipt()
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if receipt["status"] != "CONTROL_PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
