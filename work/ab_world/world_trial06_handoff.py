"""Carry original WORLD Trial 06 continuous traces into neutral A/B construction.

The original source owns the geometry, contact rules and native trajectory
verifier. This module records source-labelled movements and contrasts only.
A supplied JSON document or SHA label does not independently authenticate a
source or establish measured physical behavior.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from math import isfinite
from pathlib import Path
import re
from typing import Any

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

SCHEMA = "ab-world-trial06-continuous-source-handoff/v1"
SOURCE_SCHEMA = "world-ab-connected-continuous-junction/v1"
SERIES = ("baseline_finite_capsule", "connected_finite_capsule")


def _require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("WORLD Trial06 handoff: " + reason)


def _case(case: Any, level: float) -> None:
    _require(type(case) is dict, "missing original trajectory")
    for key in ("entry_y", "status", "frames", "contacts", "first_contact",
                "exit", "unresolved"):
        _require(key in case, "incomplete original trajectory " + key)
    _require(case["entry_y"] == level, "probe identity changed")
    frames = case["frames"]
    _require(type(frames) is list and len(frames) >= 1, "no returned frames")
    _require(all(type(f) is dict and type(f.get("time")) in (int, float)
                 and isfinite(f["time"]) for f in frames), "invalid frame")
    _require(frames[0]["time"] == 0, "missing native initial state")
    _require(all(a["time"] <= b["time"] for a, b in zip(frames, frames[1:])),
             "source chronology reversed")
    _require(case["exit"] == frames[-1], "exit does not match final frame")
    _require(type(case["contacts"]) is list, "missing source contact events")
    first = case["contacts"][0].get("surface_id") if case["contacts"] else None
    _require(case["first_contact"] == first, "first contact not trace-derived")
    _require(type(case["status"]) is str, "missing terminal status")


def carry(native: dict[str, Any], source_commit: str) -> dict[str, Any]:
    """Record the source's trajectories, not reproduce their contact physics."""
    _require(type(source_commit) is str
             and re.fullmatch(r"[a-f0-9]{40}", source_commit) is not None,
             "pinned source commit SHA required")
    _require(type(native) is dict and native.get("schema") == SOURCE_SCHEMA,
             "not an original WORLD Trial06 result")
    geometry = native.get("geometry")
    _require(type(geometry) is dict
             and type(geometry.get("surfaces")) is list
             and len(geometry["surfaces"]) == 2, "missing original two-face geometry")
    surfaces = geometry["surfaces"]
    _require(all(type(s) is dict and type(s.get("id")) is str and s["id"].strip()
                 for s in surfaces) and surfaces[0]["id"] != surfaces[1]["id"],
             "source surface identities missing or repeated")
    levels = native.get("probe_levels")
    _require(type(levels) is list and 1 <= len(levels) <= 50
             and all(type(y) in (int, float) and isfinite(y) for y in levels),
             "invalid source probe roster")
    _require(len({str(y) for y in levels}) == len(levels), "repeated probe identity")
    a, b = (native.get(key) for key in SERIES)
    _require(type(a) is list and type(b) is list and
             len(a) == len(b) == len(levels), "unaligned source trajectories")
    for level, baseline, connected in zip(levels, a, b):
        _case(baseline, level)
        _case(connected, level)
        _require(baseline["frames"][0] == connected["frames"][0],
                 "different initial state for baseline and connected motion")
    _require(native.get("completed_cases") ==
             sum(c["status"] == "completed" for c in b), "false completed count")
    _require(native.get("unresolved_cases") ==
             [{"entry_y": c["entry_y"], "status": c["status"]} for c in b
              if c["status"] != "completed"], "unresolved contact status hidden")
    basis = {"kind": "source-execution",
             "source": "original WORLD Trial06 native source @" + source_commit}
    expected_basis = {"kind": "declared",
                      "source": "original WORLD Trial06 finite-face baseline @" + source_commit}
    steps = [
        {"op": "introduce", "id": "source-surface-0",
         "state": deepcopy(surfaces[0]), "basis": basis},
        {"op": "introduce", "id": "source-surface-1",
         "state": deepcopy(surfaces[1]), "basis": basis},
        {"op": "connect", "id": "source-finite-intersection",
         "from": "source-surface-0", "to": "source-surface-1",
         "label": "source-reported-junction",
         "state": {"junction": deepcopy(geometry.get("junction")),
                   "topology": deepcopy(geometry.get("topology"))},
         "basis": basis},
    ]
    differences = []
    frame_count = 0
    for i, (level, baseline, connected) in enumerate(zip(levels, a, b), 1):
        for name, trace in (("baseline", baseline), ("connected", connected)):
            ident = f"{name}-probe-{i:03d}"
            def state(frame):
                return {"series": name, "source_probe_level": level,
                        "frame": deepcopy(frame)}
            steps.append({"op": "introduce", "id": ident,
                          "state": state(trace["frames"][0]), "basis": basis})
            frame_count += 1
            for frame in trace["frames"][1:]:
                steps.append({"op": "revise", "id": ident, "entity": "object",
                              "after": state(frame), "basis": basis})
                frame_count += 1
            steps.append({"op": "observe", "id": f"{name}-trace-{i:03d}",
                          "entity": "object", "subject": ident,
                          "reading": {"trajectory": deepcopy(trace)}, "basis": basis})
        if baseline != connected:
            differences.append(level)
        steps.append({"op": "compare", "id": f"source-path-contrast-{i:03d}",
                      "observation": f"connected-trace-{i:03d}",
                      "expected": {"trajectory": deepcopy(baseline)},
                      "basis": expected_basis})
    plan = {
        "schema": PLAN,
        "referent": "original WORLD Trial06 finite-segment continuous trajectories",
        "limits": {"objects": 2 + 2 * len(levels), "relations": 1,
                   "steps": len(steps)},
        "steps": steps,
    }
    receipt = run_plan(plan)
    witness = verify_receipt(receipt)
    return {
        "schema": SCHEMA,
        "source_commit": source_commit,
        "source_report_sha256": digest(native),
        "probes_carried": len(levels),
        "trajectories_carried": 2 * len(levels),
        "sampled_frames_carried": frame_count,
        "difference_probe_levels": differences,
        "connected_completed": native["completed_cases"],
        "connected_unresolved": deepcopy(native["unresolved_cases"]),
        "world_receipt": receipt,
        "ledger_witness": witness,
        "native_dynamics_verified_by_this_adapter": False,
        "source_authenticated_by_this_adapter": False,
        "physical_measurements_verified": False,
        "multicontact_solver_inferred": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    print(json.dumps(carry(load_json(args.native), args.source_commit),
                     sort_keys=True, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
