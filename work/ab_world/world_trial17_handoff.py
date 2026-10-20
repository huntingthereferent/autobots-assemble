"""Carry WORLD17 finite first-return brackets, not a second collision response.

Original WORLD source and independent fine-step polygon checker own numerical
claims. This records all source-root witnesses as *conditional* mathematical
contact locations. No new physical impulse, receiver, or continued trajectory.
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

SCHEMA = "ab-world-trial17-first-return-source-handoff/v1"
SOURCE = "world-ab-rotating-square-first-finite-recontact/v1"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
HORIZON = .06
RETURN = "FIRST_RENEWED_FINITE_FACE_CONTACT_CANDIDATE"
NONE = "NO_NEW_LINE_CROSSING_IN_WINDOW"


def demand(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("WORLD17 handoff: " + message)


def num(x: Any) -> bool:
    return type(x) in (int, float) and isfinite(x)


def pair(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(num(v) for v in x)


def carry(native: dict[str, Any], source_commit: str) -> dict[str, Any]:
    demand(type(source_commit) is str and
           re.fullmatch("[0-9a-f]{40}", source_commit) is not None,
           "pin exact original source commit")
    demand(type(native) is dict and native.get("schema") == SOURCE and
           native.get("angles") == list(ANGLES) and native.get("horizon") == HORIZON and
           native.get("built_any_new_object") is False and
           native.get("actual_physical_impact_verified") is False,
           "original source roster or physical claim changed")
    cases = native.get("cases")
    demand(type(cases) is list and len(cases) == len(ANGLES),
           "eight source recontact controls required")
    owner = {"kind": "source-execution",
             "source": "pinned original WORLD17 @" + source_commit}
    proposed = {"kind": "declared",
                "source": "bracketed numerical first return, no modeled impulse"}
    pages = []
    candidate_count = 0
    no_return = 0
    root_count = 0
    for index, angle in enumerate(ANGLES):
        case = cases[index]
        demand(type(case) is dict and case.get("schema") == SOURCE and
               case.get("source") == "unchanged original WORLD trial04 first square impact" and
               case.get("source_angle") == angle and case.get("horizon") == HORIZON and
               case.get("method") ==
               "analytical corner gap stationary partitions plus numerical bisection",
               "source experiment control or method changed")
        demand(case.get("source_finite_wall_preserved") is True and
               case.get("recontact_kinematics_only") is True and
               case.get("numerically_bracketed_not_exact_certified") is True and
               case.get("second_impulse_or_further_motion_solved") is False and
               case.get("derived_receiver_built") is False and
               case.get("physical_sensor_evidence") is False,
               "unwitnessed material impulse or next receiver promoted")
        impact = case.get("source_original_first_contact")
        demand(type(impact) is dict and impact.get("hit") is True and
               impact.get("angle_degrees") == angle and
               num(impact.get("first_contact_time")) and
               type(impact.get("candidate_receiver")) is dict and
               impact["candidate_receiver"].get("surface_built") is False,
               "original first impact and not-yet-built receiver lost")
        status = case.get("status")
        first = case.get("first_return")
        roots = case.get("candidate_return_roots")
        demand(type(roots) is list and
               type(case.get("monotonic_segments_checked")) is int and
               case["monotonic_segments_checked"] >= 0,
               "source root or interval evidence missing")
        prev = -1.
        for root in roots:
            demand(type(root) is dict and num(root.get("time")) and
                   0 < root["time"] <= HORIZON and
                   type(root.get("corner_index")) is int and
                   0 <= root["corner_index"] < 4 and
                   root.get("type") in ("TRANSVERSE_SIGN_CROSSING","UNRESOLVED_TOUCH") and
                   root["time"] >= prev,
                   "source bracket root chronology or identity changed")
            prev = root["time"]
        steps = [
            {"op": "introduce", "id": "original-square-first-impact",
             "state": {"original_source_record": deepcopy(impact),
                       "virtual_first_impact": True,
                       "physical_sensor_evidence": False}, "basis": owner},
            {"op": "introduce", "id": "bounded-first-return-investigation",
             "state": {"angle": angle, "horizon": HORIZON,
                       "status": status, "numerically_bracketed_only": True,
                       "second_impulse": None, "receiver_built": False,
                       "valid_postreturn_motion": None}, "basis": proposed},
            {"op": "connect", "id": "original-impact-to-return-search",
             "from": "original-square-first-impact",
             "to": "bounded-first-return-investigation",
             "label": "source-derived-corner-return-search",
             "state": {"no_physical_contact_selected": True}, "basis": proposed},
            {"op": "observe", "id": "source-reported-return-roots",
             "entity": "object", "subject": "bounded-first-return-investigation",
             "reading": {"roots": deepcopy(roots),
                         "checked_monotonic_intervals":
                             case["monotonic_segments_checked"],
                         "numerical_bisection_not_exact_proof": True,
                         "source_case_sha256": digest(case)}, "basis": owner},
        ]
        if status == RETURN:
            demand(type(first) is dict and len(roots) >= 1 and
                   roots[0].get("type") == "TRANSVERSE_SIGN_CROSSING" and
                   num(first.get("dt_after_initial_contact")) and
                   0 < first["dt_after_initial_contact"] < HORIZON and
                   abs(first["dt_after_initial_contact"]-roots[0]["time"]) < 2e-9 and
                   num(first.get("absolute_virtual_time")) and
                   abs(first["absolute_virtual_time"] -
                       (impact["first_contact_time"] +
                        first["dt_after_initial_contact"])) < 2e-9 and
                   type(first.get("corner_index")) is int and
                   first["corner_index"] == roots[0]["corner_index"] and
                   pair(first.get("corner_position")) and
                   num(first.get("source_face_tangent_coordinate")) and
                   abs(first["source_face_tangent_coordinate"]) < .5 and
                   num(first.get("normal_gap_residual")) and
                   abs(first["normal_gap_residual"]) < 2e-7 and
                   num(first.get("incoming_normal_vertex_rate")) and
                   first["incoming_normal_vertex_rate"] < 0 and
                   first.get("contact_feature") ==
                   "square-vertex / original finite face interior" and
                   first.get("second_impulse_selected") is False,
                   "candidate not grounded in original finite-face return")
            steps.extend([
                {"op": "observe", "id": "first-return-source-candidate",
                 "entity": "object", "subject": "bounded-first-return-investigation",
                 "reading": {"mathematical_first_return": deepcopy(first),
                             "model_only": True, "second_impulse": None,
                             "physical_contact_witnessed": False}, "basis": owner},
                {"op": "introduce", "id": "located-corner-return",
                 "state": {"source_corner": first["corner_index"],
                           "virtual_contact_time": first["absolute_virtual_time"],
                           "finite_face_position": deepcopy(first["corner_position"]),
                           "normal_rate": first["incoming_normal_vertex_rate"],
                           "candidate_only": True, "second_impulse": None,
                           "receiver_built": False}, "basis": proposed},
                {"op": "connect", "id": "return-location-from-original-motion",
                 "from": "bounded-first-return-investigation",
                 "to": "located-corner-return",
                 "label": "numerically-bracketed-possible-contact",
                 "state": {"finite_interior_candidate": True,
                           "no_postcontact_trajectory": True}, "basis": proposed},
            ])
            candidate_count += 1
        else:
            demand(status == NONE and first is None and roots == [],
                   "absence of source crossing promoted to solved event")
            steps.append({
                "op": "observe", "id": "source-no-crossing-in-window",
                "entity": "object", "subject": "bounded-first-return-investigation",
                "reading": {"source_status": NONE,
                            "horizon": HORIZON, "receiver_built": False,
                            "continuous_clearance_proven": False,
                            "future_contact_ruled_out": False}, "basis": owner,
            })
            no_return += 1
        root_count += len(roots)
        plan = {"schema": PLAN,
                "referent": f"WORLD17 / first recontact source angle {angle}",
                "limits": {"objects": 3, "relations": 2,
                           "steps": len(steps)},
                "steps": steps}
        receipt = run_plan(plan)
        pages.append({"case": index, "angle": angle, "status": status,
                      "receipt": receipt, "witness": verify_receipt(receipt)})
    demand(native.get("first_return_candidates") == candidate_count and
           native.get("no_return") == no_return and
           candidate_count == 6 and no_return == 2,
           "original source first return counts altered")
    manifest = {"native_report_sha256": digest(native),
                "ordered_case_heads": [
                    {"case": p["case"], "angle": p["angle"],
                     "status": p["status"],
                     "head_hash": p["receipt"]["head_hash"]}
                    for p in pages]}
    witness = {
        "valid": all(p["witness"]["valid"] for p in pages),
        "pages_verified": len(pages),
        "steps_verified": sum(p["witness"]["steps_verified"] for p in pages),
        "observations_recorded": sum(
            p["witness"]["observations_recorded"] for p in pages),
    }
    return {"schema": SCHEMA, "source_commit": source_commit,
            "source_report_sha256": digest(native),
            "first_return_candidates": candidate_count, "no_return": no_return,
            "source_root_records": root_count,
            "original_controls": len(ANGLES),
            "modeled_second_impulses_selected": 0,
            "derived_receivers_built": 0,
            "observed_material_contacts": 0,
            "continuation_after_return_verified": False,
            "source_physics_verified_by_adapter": False,
            "ledgers": pages, "ledger_witness": witness,
            "page_manifest": manifest, "page_manifest_sha256": digest(manifest)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    print(json.dumps(carry(load_json(args.native), args.source_commit),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
