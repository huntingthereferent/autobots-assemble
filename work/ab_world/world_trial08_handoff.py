"""Preserve original WORLD Trial 08 candidate without overwriting Trial 07 uncertainty.

This module is a domain-specific ledger adapter, not a simultaneous-contact
solver. Original source execution and independent physics verification happen
separately before carrying its reported finite candidate trajectory.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from math import isfinite
from pathlib import Path
import json
import re
from typing import Any

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

SCHEMA = "ab-world-trial08-frictionless-candidate-handoff/v1"
SOURCE_SCHEMA = "world-ab-two-contact-frictionless-candidate/v1"
UNRESOLVED = "unresolved-multiple-contacts"


def require(ok: bool, description: str) -> None:
    if not ok:
        raise ValueError("Trial08 candidate handoff: " + description)


def number(v: Any) -> bool:
    return type(v) in (int, float) and isfinite(v)


def carry(original: dict[str, Any], source_commit: str) -> dict[str, Any]:
    require(type(source_commit) is str and
            re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None,
            "exact source commit required")
    require(type(original) is dict and original.get("schema") == SOURCE_SCHEMA,
            "wrong original Trial08 source format")
    for key in ("simultaneous_frictional_manifold_solved", "arbitrary_junctions_solved",
                "real_material_behavior_verified", "original_blueprint_generated"):
        require(original.get(key) is False, "unsupported source claim " + key)
    require(original.get("candidate_is_a_new_comparison_not_original_friction_physics") is True,
            "candidate must be separate from the original physics")
    require(original.get("original_trial06_friction") == .4 and
            original.get("candidate_friction") == 0.,
            "original and candidate friction regimes have been mixed")
    require(original.get("baseline_trial06_status") == UNRESOLVED,
            "original junction is not unresolved")

    geometry = original.get("geometry")
    require(type(geometry) is dict and type(geometry.get("surfaces")) is list and
            len(geometry["surfaces"]) == 2,
            "source surfaces not present")
    faces = geometry["surfaces"]
    ids = [x.get("id") if type(x) is dict else None for x in faces]
    require(all(type(x) is str and x.strip() for x in ids) and ids[0] != ids[1],
            "distinct original surface identities required")

    candidate = original.get("candidate")
    require(type(candidate) is dict and candidate.get("source_ids") == ids,
            "candidate detached from original source identities")
    require(candidate.get("original_stop") == UNRESOLVED and
            candidate.get("candidate_full_horizon_observed") is True,
            "original stop or candidate scope changed")
    require(candidate.get("friction") == 0. and
            candidate.get("normal_restitution") == 1. and
            candidate.get("outgoing_spin") == 0.,
            "unsupported candidate dynamics labels")
    require(number(candidate.get("collision_time")) and
            number(candidate.get("entry_y")) and
            type(candidate.get("normal_impulses")) is list and
            len(candidate["normal_impulses"]) == 2 and
            all(number(x) and x > 0 for x in candidate["normal_impulses"]),
            "missing two source candidate impulses")
    frames = candidate.get("frames")
    require(type(frames) is list and len(frames) == 31, "original 31 sample frames required")
    for index, frame in enumerate(frames):
        require(type(frame) is dict and number(frame.get("time")) and
                abs(frame["time"] - index * .05) < 1e-8,
                "missing or reordered original candidate frame")
        require(type(frame.get("position")) is list and
                type(frame.get("velocity")) is list and
                len(frame["position"]) == len(frame["velocity"]) == 2 and
                all(number(x) for x in frame["position"] + frame["velocity"]),
                "candidate frame movement missing")
    require(abs(frames[0]["position"][0] - 12.) <= 2e-9 and
            abs(frames[0]["position"][1] - candidate["entry_y"]) <= 2e-9,
            "candidate start differs from original probe beyond source precision")
    controls = original.get("nearby_trial07_statuses")
    require(type(controls) is list and len(controls) == 9,
            "missing original Trial07 controls")
    require(all(type(x) is dict and
                set(("offset", "status", "first_contact")).issubset(x)
                for x in controls), "invalid original control record")

    owner = {"kind": "source-execution",
             "source": "WORLD Trial08 original virtual source @" + source_commit}
    proposal = {"kind": "declared",
                "source": "WORLD Trial08 explicitly hypothetical frictionless model"}
    steps = [
        {"op": "introduce", "id": "original-face-0",
         "state": deepcopy(faces[0]), "basis": owner},
        {"op": "introduce", "id": "original-face-1",
         "state": deepcopy(faces[1]), "basis": owner},
        {"op": "connect", "id": "original-source-junction",
         "from": "original-face-0", "to": "original-face-1",
         "label": "source-reported-finite-geometry",
         "state": {"junction": deepcopy(geometry.get("junction")),
                   "topology": deepcopy(geometry.get("topology"))}, "basis": owner},
        {"op": "introduce", "id": "original-unresolved-contact",
         "state": {"status": UNRESOLVED, "contact_solution": None,
                   "friction": .4, "outgoing_impulse": None}, "basis": owner},
        {"op": "observe", "id": "original-source-stop",
         "entity": "object", "subject": "original-unresolved-contact",
         "reading": {"status": UNRESOLVED, "solved": False,
                     "outgoing_impulse": None}, "basis": owner},
        {"op": "introduce", "id": "original-trial07-controls",
         "state": {"nearby": deepcopy(controls)}, "basis": owner},
        {"op": "introduce", "id": "frictionless-candidate",
         "state": {"hypothetical": True, "friction": 0.,
                   "original_status": UNRESOLVED,
                   "frame": deepcopy(frames[0])}, "basis": proposal},
        {"op": "connect", "id": "counterfactual-not-original-motion",
         "from": "original-unresolved-contact", "to": "frictionless-candidate",
         "label": "separate-conditional-physical-model",
         "state": {"original_friction": .4, "candidate_friction": 0.,
                   "original_remains_unresolved": True}, "basis": proposal},
    ]
    for frame in frames[1:]:
        steps.append({
            "op": "revise", "entity": "object", "id": "frictionless-candidate",
            "after": {"hypothetical": True, "friction": 0.,
                      "original_status": UNRESOLVED, "frame": deepcopy(frame)},
            "basis": owner})
    steps.append({
        "op": "observe", "id": "original-executed-candidate-source",
        "entity": "object", "subject": "frictionless-candidate",
        "reading": {"source_computed_candidate": deepcopy(candidate),
                    "candidate_not_original_observed_motion": True},
        "basis": owner,
    })
    plan = {
        "schema": PLAN,
        "referent": "WORLD Trial08 explicitly conditional frictionless junction response",
        "limits": {"objects": 5, "relations": 2, "steps": len(steps)},
        "steps": steps,
    }
    receipt = run_plan(plan)
    return {
        "schema": SCHEMA,
        "source_commit": source_commit,
        "source_report_sha256": digest(original),
        "ledger_receipt": receipt,
        "ledger_witness": verify_receipt(receipt),
        "original_status": UNRESOLVED,
        "original_response_known": False,
        "candidate_model": "frictionless two-normal e=1",
        "candidate_frames_carried": len(frames),
        "candidate_outgoing_velocity": deepcopy(candidate.get("outgoing_velocity")),
        "candidate_verified_by_adapter_as_physics": False,
        "source_authenticated_by_adapter": False,
        "real_material_behavior_verified": False,
        "frictional_simultaneous_contact_solved": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    print(json.dumps(carry(load_json(args.native), args.source_commit),
                     indent=2, sort_keys=True, ensure_ascii=False))


if __name__ == "__main__":
    main()
