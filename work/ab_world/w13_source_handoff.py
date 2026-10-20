"""Carry genuine existing W13 native source movement into the neutral A/B world.

The source retains authority over game rules; this adapter only maps its
verified native trace to declared world state and attributed observations.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from systems.workspace import game_construction as source
from work.ab_world.construction import PLAN, run_plan
from work.ab_world.verify_construction import verify_receipt

SCHEMA = "ab-world-w13-source-handoff/v1"


def independent_expected(spec: source.GameSpec, actions: list[str]) -> list[dict]:
    """Separate small W12 contract calculation; never calls source.transition."""
    x, y = spec.start
    saved = False
    count = 0
    output = []
    for action in actions:
        before = {"x": x, "y": y, "collected": saved, "turns": count}
        count += 1
        if action == "interact":
            reachable = abs(x - spec.target[0]) + abs(y - spec.target[1]) == 1
            verdict = "already-collected" if saved else ("collected" if reachable else "out-of-reach")
            saved = saved or reachable
        else:
            if action not in {"up", "down", "left", "right"}:
                raise ValueError("unrecognized native movement")
            difference = {"up": (0, -1), "down": (0, 1),
                          "left": (-1, 0), "right": (1, 0)}[action]
            candidate = (x + difference[0], y + difference[1])
            if 0 <= candidate[0] < spec.width and 0 <= candidate[1] < spec.height:
                x, y = candidate
                verdict = "moved"
            else:
                verdict = "blocked-by-boundary"
        output.append({"action": action, "before": before,
                       "after": {"x": x, "y": y, "collected": saved, "turns": count},
                       "verdict": verdict})
    return output


def handoff(actions: list[str] | None = None) -> dict:
    actions = list(actions) if actions is not None else ["left", "right", "interact"]
    if len(actions) > 3000:
        raise ValueError("bounded adapter action limit")
    spec = source.GameSpec()
    native = source.run_actions(actions, spec)
    native_check = source.verify_trace(native)
    if not native_check["valid"]:
        raise ValueError("W13 source replay rejected")
    sha = sha256(Path(source.__file__).read_bytes()).hexdigest()
    owner_ref = "systems/workspace/game_construction.py@sha256:" + sha
    native_basis = {"kind": "source-execution", "source": owner_ref}
    proposed_basis = {"kind": "declared", "source": "w13/independent-movement-contract"}
    independent = independent_expected(spec, actions)
    initial = {"x": spec.start[0], "y": spec.start[1], "collected": False, "turns": 0}
    steps = [{"op": "introduce", "id": "w13-native-state",
              "state": {"native": deepcopy(initial)}, "basis": proposed_basis}]
    for i, (row, expected) in enumerate(zip(native["steps"], independent), 1):
        # Source record and independent candidate remain separately observable.
        reported = {field: deepcopy(row[field]) for field in ("action", "before", "after", "verdict")}
        steps.extend([
            {"op": "revise", "entity": "object", "id": "w13-native-state",
             "after": {"native": deepcopy(row["after"])}, "basis": native_basis},
            {"op": "observe", "id": "w13-native-event-" + str(i),
             "entity": "object", "subject": "w13-native-state",
             "reading": reported, "basis": native_basis},
            {"op": "compare", "id": "w13-independent-contrast-" + str(i),
             "observation": "w13-native-event-" + str(i),
             "expected": expected, "basis": proposed_basis},
        ])
    plan = {
        "schema": PLAN,
        "referent": "original W13 source movement / local game record",
        "limits": {"objects": 1, "relations": 1, "steps": 1 + len(steps)},
        "steps": steps
    }
    receipt = run_plan(plan)
    witness = verify_receipt(receipt)
    differences = [key for key, value in receipt["final"]["comparisons"].items()
                   if value["result"] != "MATCH"]
    return {
        "schema": SCHEMA,
        "source_code_sha256": sha,
        "native_source_version": native["version"],
        "native_trace_head_hash": native["head_hash"],
        "native_source_replay": native_check,
        "source_consistent_with_independent_contract": not differences,
        "differences": differences,
        "world_receipt": receipt,
        "world_ledger_witness": witness,
        "physically_measured": False
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("actions", nargs="*", help="Original W13 local actions")
    args = parser.parse_args()
    result = handoff(args.actions if args.actions else None)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
