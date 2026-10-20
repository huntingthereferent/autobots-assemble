"""WORLD Trial09 -> A/B: retain finite accepted AND rejected source controls.

Original WORLD source owns incidence geometry, candidate solver, native verifier.
This neutral carrier cannot independently validate those mechanics or authenticate
reported source bytes. Rejected models do not acquire any invented trajectory.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from math import isfinite
import json
from pathlib import Path
import re
from typing import Any

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

SCHEMA = "ab-world-trial09-source-contrast/v1"
NATIVE = "world-ab-two-contact-incidence-stress/v1"
ANGLES = (-15, -5, 0, 10, 20, 30, 45)
OFFSETS = (-15.0, -7.5, 0.0, 7.5, 15.0)
ACCEPTED = "accepted-local-candidate"
REJECTED = ("rejected-unilateral", "rejected-not-incoming", "rejected-constraint")
STATUSES = (ACCEPTED, *REJECTED)


def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError("Trial09 carrier: " + message)


def finite(value: Any) -> bool:
    return type(value) in (float, int) and isfinite(value)


def finite_pair(value: Any) -> bool:
    return type(value) is list and len(value) == 2 and all(finite(v) for v in value)


def carry(native: dict[str, Any], source_commit: str) -> dict[str, Any]:
    require(type(source_commit) is str and
            re.fullmatch("[0-9a-f]{40}", source_commit) is not None,
            "exact source commit required")
    require(type(native) is dict and native.get("schema") == NATIVE,
            "not the original Trial09 observation record")
    require(native.get("incoming_angle_grid") == list(ANGLES) and
            native.get("surface_rotation_grid") == list(OFFSETS),
            "declared finite stress grid changed")
    require(native.get("original_trial06_friction") == .4 and
            native.get("candidate_friction") == 0.,
            "original and counterfactual physics mixed")
    require(native.get("speed") == 2. and
            native.get("controlled_contact_lead") == .35,
            "trial starting conditions changed")
    for flag in ("original_surface_modified", "rotated_faces_are_original_source",
                 "general_two_contact_physics_proven", "frictional_manifold_solved",
                 "real_material_equivalence", "original_blueprint_generated"):
        require(native.get(flag) is False, "unsupported claim: " + flag)
    geo = native.get("original_source_geometry")
    require(type(geo) is dict and type(geo.get("surfaces")) is list
            and len(geo["surfaces"]) == 2, "original finite surfaces absent")
    faces = geo["surfaces"]
    ids = [s.get("id") if type(s) is dict else None for s in faces]
    require(all(type(v) is str and bool(v.strip()) for v in ids)
            and len(set(ids)) == 2, "source identity ambiguity")
    tie = native.get("original_trial07_contact")
    require(type(tie) is dict and tie.get("source_ids") == ids,
            "Trial07 original tie detached from source")
    require(finite_pair(native.get("original_trial08_outgoing")),
            "Trial08 original model's candidate record missing")
    cases = native.get("cases")
    require(type(cases) is list and len(cases) == len(ANGLES) * len(OFFSETS),
            "must retain all 35 source cases")
    owner = {"kind": "source-execution",
             "source": "original WORLD Trial09 nominal source @" + source_commit}
    proposed = {"kind": "declared",
                "source": "original WORLD Trial08 frictionless candidate assumptions"}
    steps = [
        {"op": "introduce", "id": "original-source-face-A",
         "state": deepcopy(faces[0]), "basis": owner},
        {"op": "introduce", "id": "original-source-face-B",
         "state": deepcopy(faces[1]), "basis": owner},
        {"op": "connect", "id": "original-source-junction",
         "from": "original-source-face-A", "to": "original-source-face-B",
         "label": "original-finite-intersection",
         "state": {"junction": deepcopy(geo.get("junction")),
                   "topology": deepcopy(geo.get("topology"))}, "basis": owner},
        {"op": "introduce", "id": "unresolved-original-contact",
         "state": {"source_trial07": deepcopy(tie),
                   "friction": .4, "status": "unresolved-multiple-contacts",
                   "outgoing_impulse": None}, "basis": owner},
        {"op": "introduce", "id": "trial08-model",
         "state": {"source_reported_candidate_outgoing":
                   deepcopy(native["original_trial08_outgoing"]),
                   "friction": 0., "original_response_resolved": False},
         "basis": proposed},
        {"op": "connect", "id": "candidate-not-original",
         "from": "unresolved-original-contact", "to": "trial08-model",
         "label": "separate-frictionless-hypothesis",
         "state": {"original_friction": .4, "candidate_friction": 0.},
         "basis": proposed},
    ]
    counts = dict.fromkeys(STATUSES, 0)
    retained_frames = 0
    for index, (offset, angle) in enumerate(
            (offset, angle) for offset in OFFSETS for angle in ANGLES, 1):
        # The original grid is deliberately ordered: surface rotation outer,
        # incoming incidence inner. Reject any substituted or dropped case.
        case = cases[index - 1]
        require(type(case) is dict and
                case.get("surface_B_rotation_degrees") == offset and
                case.get("incoming_angle_degrees") == angle,
                "predeclared case order changed")
        kind = case.get("geometry_kind")
        surfaces = case.get("surfaces")
        require(type(surfaces) is list and len(surfaces) == 2,
                "case source faces missing")
        if offset == 0:
            require(kind == "original-source-geometry" and surfaces == faces,
                    "original case replaced by a controlled face")
        else:
            face_b = surfaces[1]
            require(kind == "controlled-geometry-not-original" and
                    surfaces[0] == faces[0] and type(face_b) is dict and
                    face_b.get("geometry_role") == "explicit-rotated-counterfactual"
                    and face_b.get("source_parent_id") == ids[1]
                    and face_b.get("rotation_degrees") == offset,
                    "controlled rotated face promoted to original")
        status = case.get("status")
        require(status in STATUSES, "unsupported source outcome")
        counts[status] += 1
        ident = "incidence-control-" + str(index).zfill(2)
        steps.append({
            "op": "introduce", "id": ident,
            "state": {"angle": angle, "rotation": offset,
                      "geometry_kind": kind, "source_surfaces": deepcopy(surfaces),
                      "status": status, "candidate": status == ACCEPTED},
            "basis": owner})
        steps.append({
            "op": "connect", "id": "trial08-control-" + str(index).zfill(2),
            "from": "trial08-model", "to": ident,
            "label": "source-tested-candidate-or-rejection",
            "state": {"geometry_kind": kind, "status": status}, "basis": owner})
        frames = case.get("frames")
        candidate = case.get("candidate")
        if status == ACCEPTED:
            require(candidate is not None and type(candidate) is dict and
                    case.get("reason") is None, "accepted source result incomplete")
            require(type(frames) is list and len(frames) == 31,
                    "accepted source trajectory must have 31 frames")
            for frame_index, frame in enumerate(frames):
                require(type(frame) is dict and finite(frame.get("time")) and
                        abs(frame["time"] - frame_index * .05) < 2e-8 and
                        finite_pair(frame.get("position")) and
                        finite_pair(frame.get("velocity")),
                        "source candidate frame malformed or reordered")
                steps.append({
                    "op": "revise", "entity": "object", "id": ident,
                    "after": {"angle": angle, "rotation": offset,
                              "geometry_kind": kind,
                              "source_surfaces": deepcopy(surfaces),
                              "status": status, "candidate": True,
                              "frame": deepcopy(frame)},
                    "basis": owner})
            retained_frames += len(frames)
        else:
            require(candidate is None and frames == [] and
                    type(case.get("reason")) is str and bool(case["reason"]),
                    "rejected case must have no fabricated motion")
        steps.append({
            "op": "observe", "id": "original-source-control-" + str(index).zfill(2),
            "entity": "object", "subject": ident,
            "reading": {"case": deepcopy(case)}, "basis": owner})
    require(native.get("counts") == counts, "source acceptance counts rewritten")
    require(counts[ACCEPTED] > 0 and
            sum(counts[z] for z in REJECTED) > 0,
            "source did not distinguish acceptance and rejection")
    plan = {
        "schema": PLAN,
        "referent": "WORLD Trial09 / predeclared original and controlled-angle contrasts",
        "limits": {"objects": 4 + len(cases), "relations": 2 + len(cases),
                   "steps": len(steps)},
        "steps": steps}
    receipt = run_plan(plan)
    return {
        "schema": SCHEMA,
        "source_commit": source_commit,
        "source_report_sha256": digest(native),
        "stress_cases": len(cases),
        "outcome_counts": counts,
        "candidate_frames_carried": retained_frames,
        "original_frictional_contact_still_unresolved": True,
        "controlled_faces_are_original_source": False,
        "native_physics_verified_by_adapter": False,
        "external_source_authenticated_by_adapter": False,
        "physical_materials_verified": False,
        "ledger_receipt": receipt,
        "ledger_witness": verify_receipt(receipt),
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
