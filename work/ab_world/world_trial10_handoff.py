"""Record original WORLD Trial10 active-set alternatives without selecting physics.

Original WORLD source and its independent native verification own geometry,
frictionless contact evaluation and admissibility. The general A/B record
carries their outputs and keeps the actual frictional contact unresolved.
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

SCHEMA = "ab-world-trial10-active-set-handoff/v1"
NATIVE = "world-ab-two-contact-active-set-enumeration/v1"
ANGLES = (-15, -5, 0, 10, 20, 30, 45)
ROTATIONS = (-15.0, -7.5, 0.0, 7.5, 15.0)
ACTIVE = ((0,), (1,), (0, 1))
CLASSIFICATIONS = ("no-local-candidate", "single-admissible", "multiple-admissible")
ADMISSIBLE = "admissible-local-model"


def demand(test: bool, reason: str) -> None:
    if not test:
        raise ValueError("Trial10 A/B carrier: " + reason)


def finite(value: Any) -> bool:
    return type(value) in (int, float) and isfinite(value)


def vector2(value: Any) -> bool:
    return type(value) is list and len(value) == 2 and all(finite(x) for x in value)


def carry(native: dict[str, Any], source_commit: str) -> dict[str, Any]:
    demand(type(source_commit) is str and
           re.fullmatch(r"[0-9a-f]{40}", source_commit) is not None,
           "exact original source commit required")
    demand(type(native) is dict and native.get("schema") == NATIVE,
           "wrong original native Trial10 schema")
    demand(native.get("angle_grid") == list(ANGLES) and
           native.get("rotation_grid") == list(ROTATIONS) and
           native.get("active_sets") == [list(x) for x in ACTIVE],
           "original finite case or contact-set roster changed")
    demand(native.get("original_trial06_friction") == 0.4 and
           native.get("candidate_friction") == 0.0 and
           native.get("comparison_restitution") == 1.0,
           "candidate assumptions conflated with original friction")
    for flag in ("simultaneous_multicontact_physics_uniquely_determined",
                 "physical_active_contacts_observed",
                 "sequential_impacts_temporally_witnessed",
                 "original_source_surfaces_modified",
                 "rotated_faces_are_original_source",
                 "original_blueprint_generated", "earth_material_equivalence"):
        demand(native.get(flag) is False, "unsupported physical claim: " + flag)
    geom = native.get("original_source_geometry")
    demand(type(geom) is dict and type(geom.get("surfaces")) is list and
           len(geom["surfaces"]) == 2,
           "original finite geometry missing")
    ids = [x.get("id") if type(x) is dict else None for x in geom["surfaces"]]
    demand(all(type(x) is str and x.strip() for x in ids) and ids[0] != ids[1],
           "original source identities missing")
    cases = native.get("cases")
    demand(type(cases) is list and len(cases) == 35,
           "35 original predeclared cases required")
    prev_counts = native.get("original_trial09_two_active_counts")
    demand(type(prev_counts) is dict and
           set(prev_counts) == {"accepted-local-candidate",
                                "rejected-unilateral",
                                "rejected-not-incoming",
                                "rejected-constraint"} and
           all(type(n) is int and n >= 0 for n in prev_counts.values()) and
           sum(prev_counts.values()) == 35,
           "original Trial09 source counts invalid")

    owner = {"kind": "source-execution",
             "source": "WORLD Trial10 pinned native source @" + source_commit}
    model = {"kind": "declared",
             "source": "original WORLD Trial10 elastic frictionless active-set test"}
    steps = [
        {"op": "introduce", "id": "original-frictional-contact",
         "state": {"status": "unresolved-multiple-contacts",
                   "outgoing_impulse": None, "original_friction": 0.4},
         "basis": owner},
        {"op": "introduce", "id": "frictionless-candidate-model",
         "state": {"friction": 0.0, "restitution": 1.0,
                   "real_outcome_selected": False}, "basis": model},
        {"op": "connect", "id": "counterfactual-not-original",
         "from": "original-frictional-contact",
         "to": "frictionless-candidate-model",
         "label": "not-a-physical-outcome",
         "state": {"original_still_unresolved": True}, "basis": model},
    ]
    counts = {x: 0 for x in CLASSIFICATIONS}
    alternative_count = 0
    admitted = 0
    rejected = 0
    frames = 0
    recovered = 0
    page_ranges = []
    page_start = len(steps)
    for i, (angle, rotation) in enumerate(
            ((a, d) for d in ROTATIONS for a in ANGLES)):
        case = cases[i]
        demand(type(case) is dict and
               case.get("original_index") == i and
               case.get("incoming_angle_degrees") == angle and
               case.get("surface_B_rotation_degrees") == rotation,
               "predeclared original case order changed")
        kind = ("original-source-geometry" if rotation == 0
                else "controlled-geometry-not-original")
        demand(case.get("geometry_kind") == kind and
               type(case.get("source_ids")) is list and
               len(case["source_ids"]) == 2 and
               (case["source_ids"] == ids if rotation == 0
                else case["source_ids"][0] == ids[0] and
                     case["source_ids"][1] != ids[1]),
               "original and controlled surface provenance mixed")
        demand(case.get("physical_outcome_independently_observed") is False,
               "candidate promoted to actual observed material motion")
        original_status = case.get("trial09_two_active_status")
        demand(original_status in prev_counts, "original Trial09 result missing")
        alternatives = case.get("alternatives")
        demand(type(alternatives) is list and len(alternatives) == 3,
               "three source-tested alternatives required per case")
        observed_admitted = sum(alt.get("status") == ADMISSIBLE
                                for alt in alternatives if type(alt) is dict)
        demand(type(case.get("admissible_count")) is int and
               case["admissible_count"] == observed_admitted,
               "source admissibility count falsified")
        classification = ("no-local-candidate" if observed_admitted == 0
                          else "single-admissible" if observed_admitted == 1
                          else "multiple-admissible")
        demand(case.get("classification") == classification,
               "multiple physical candidates silently collapsed")
        counts[classification] += 1
        if original_status.startswith("rejected") and observed_admitted:
            recovered += 1
        cid = f"source-case-{i:02d}"
        steps.extend([
            {"op": "introduce", "id": cid,
             "state": {"angle": angle, "rotation": rotation, "geometry_kind": kind,
                       "source_ids": deepcopy(case["source_ids"]),
                       "classification": classification,
                       "original_two_active_status": original_status,
                       "physical_winner_observed": False}, "basis": owner},
            {"op": "connect", "id": f"candidate-question-{i:02d}",
             "from": "frictionless-candidate-model", "to": cid,
             "label": "original-source-finite-test",
             "state": {"classification": classification}, "basis": model},
        ])
        for j, active in enumerate(ACTIVE):
            result = alternatives[j]
            demand(type(result) is dict and
                   result.get("active_indices") == list(active) and
                   result.get("active_ids") == [case["source_ids"][k] for k in active],
                   "candidate source active-set identity altered")
            status = result.get("status")
            demand(type(status) is str and
                   (status == ADMISSIBLE or status.startswith("rejected-")),
                   "unknown active-set outcome")
            if j == 2:
                demand((status == ADMISSIBLE) ==
                       (original_status == "accepted-local-candidate"),
                       "original Trial09 two-contact rejection overwritten")
            aid = f"case-{i:02d}-active-{j}"
            initial = {"active_indices": list(active), "status": status,
                       "conditional_model_only": True, "reason": result.get("reason")}
            observed = {"status": status, "active": list(active),
                        "reason": result.get("reason"), "source_case": i}
            steps.extend([
                {"op": "introduce", "id": aid,
                 "state": deepcopy(initial), "basis": owner},
                {"op": "connect", "id": f"tested-active-{i:02d}-{j}",
                 "from": cid, "to": aid, "label": "candidate-not-selected",
                 "state": {"model_only": True, "status": status}, "basis": model},
            ])
            alternative_count += 1
            motion = result.get("frames")
            if status == ADMISSIBLE:
                demand(result.get("reason") is None and
                       type(result.get("normal_impulses")) is list and
                       len(result["normal_impulses"]) == 2 and
                       all(finite(n) and n >= 0 for n in result["normal_impulses"]) and
                       vector2(result.get("outgoing_velocity")),
                       "admissible outcome lacks model-specific impulse")
                demand(type(motion) is list and len(motion) == 31,
                       "admissible candidate must retain full finite trajectory")
                for k, frame in enumerate(motion):
                    demand(type(frame) is dict and finite(frame.get("time")) and
                           abs(frame["time"] - k * 0.05) <= 2e-8 and
                           vector2(frame.get("position")) and
                           vector2(frame.get("velocity")),
                           "admissible native frame missing or out of sequence")
                    steps.append({
                        "op": "revise", "entity": "object", "id": aid,
                        "after": {**initial, "frame": deepcopy(frame)},
                        "basis": owner,
                    })
                observed["outgoing_velocity"] = deepcopy(result["outgoing_velocity"])
                observed["normal_impulses"] = deepcopy(result["normal_impulses"])
                frames += len(motion)
                admitted += 1
            else:
                demand(result.get("normal_impulses") is None and
                       result.get("outgoing_velocity") is None and
                       motion == [] and type(result.get("reason")) is str and
                       bool(result["reason"]),
                       "rejected source model supplied invented movement")
                rejected += 1
            steps.append({
                "op": "observe", "id": f"native-alternative-{i:02d}-{j}",
                "entity": "object", "subject": aid,
                "reading": observed, "basis": owner,
            })
        if (i + 1) % len(ANGLES) == 0:
            page_ranges.append((i // len(ANGLES), i - len(ANGLES) + 1,
                                i, page_start, len(steps)))
            page_start = len(steps)
    demand(native.get("counts") == counts, "source classification totals altered")
    demand(native.get("trial09_rejected_cases_with_local_alternatives") == recovered,
           "earlier rejection recovery summary altered")
    demand(admitted + rejected == 105, "original tested active sets missing")
    # The general A/B carrier has a strict 1 MB per-plan bound. Five native
    # surface-rotation groups remain independently witnessed finite worlds,
    # connected by an ordered manifest. Do not alter the global storage bound.
    demand(len(page_ranges) == len(ROTATIONS) and
           page_start == len(steps), "finite source pages were not complete")
    pages = []
    base_steps = steps[:3]
    for rotation_index, first_case, last_case, start, stop in page_ranges:
        operations = deepcopy(base_steps) + deepcopy(steps[start:stop])
        plan = {
            "schema": PLAN,
            "referent": ("WORLD Trial10 / active-set source, rotation " +
                         str(ROTATIONS[rotation_index])),
            "limits": {"objects": 2 + len(ANGLES) * 4,
                       "relations": 1 + len(ANGLES) * 4,
                       "steps": len(operations)},
            "steps": operations,
        }
        receipt = run_plan(plan)
        witness = verify_receipt(receipt)
        pages.append({
            "rotation": ROTATIONS[rotation_index],
            "first_case": first_case, "last_case": last_case,
            "receipt": receipt, "witness": witness,
        })
    combined = {
        "valid": all(page["witness"]["valid"] for page in pages),
        "pages_verified": len(pages),
        "steps_verified": sum(p["witness"]["steps_verified"] for p in pages),
        "objects_live": sum(p["witness"]["objects_live"] for p in pages),
        "relations_live": sum(p["witness"]["relations_live"] for p in pages),
        "observations_recorded": sum(
            p["witness"]["observations_recorded"] for p in pages),
    }
    manifest = {
        "source_report_sha256": digest(native),
        "ordered_rotation_pages": [
            {"rotation": p["rotation"], "first_case": p["first_case"],
             "last_case": p["last_case"],
             "head_hash": p["receipt"]["head_hash"]}
            for p in pages
        ],
    }
    return {
        "schema": SCHEMA, "source_commit": source_commit,
        "source_report_sha256": digest(native),
        "cases": 35, "alternatives": alternative_count,
        "admissible_alternatives": admitted, "rejected_alternatives": rejected,
        "candidate_frames_carried": frames, "classifications": counts,
        "source_trial09_rejections_with_alternatives": recovered,
        "physical_outcome_chosen": False, "original_frictional_contact_solved": False,
        "original_source_authenticated_by_adapter": False,
        "source_dynamics_verified_by_adapter": False,
        "material_physics_verified": False,
        "ledger_pages": pages, "ledger_witness": combined,
        "page_manifest": manifest, "page_manifest_sha256": digest(manifest),
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
