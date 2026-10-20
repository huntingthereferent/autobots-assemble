"""WORLD19: record nominal whole-interval mathematical separation conditionally.

The original unchanged WORLD19 numerical source and independent stationary
extrema oracle own geometry. A/B only carries evidence and comparison, never
promotes the second impulse hypothesis to a realized physical trajectory.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from math import isfinite
from pathlib import Path
from typing import Any

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

PIN = "cd6fba355d82a6af25772bb08b0ce10c2b491d51"
SCHEMA = "ab-world-trial19-conditional-continuous-separation/v1"
SOURCE = "world-ab-conditional-continuous-separation/v1"
TRIAL18 = "world-ab-local-corner-recontact-impulse/v1"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
SEPARATED = "CONDITIONAL_CONTINUOUS_HALFSPACE_SEPARATION"
ABSENT = "NO_ADMITTED_SECOND_IMPULSE"
WINDOW = .016
MIN_MARGIN = 1e-5


def demand(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("A/B WORLD19: " + reason)


def finite(x: Any) -> bool:
    return type(x) in (int, float) and isfinite(x)


def pair(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(finite(v) for v in x)


def inspect_case(case: dict, angle: float) -> bool:
    demand(type(case) is dict and case.get("schema") == SOURCE
           and case.get("source_trial18_schema") == TRIAL18
           and case.get("original_source_angle") == angle
           and case.get("original_first_contact_source_id") ==
           "original WORLD Trial04 rigid square"
           and case.get("window") == WINDOW
           and finite(case.get("half_extent")) and case["half_extent"] > 0
           and pair(case.get("finite_face_origin")),
           "original source identity, geometry or finite window changed")
    demand(case.get("conditional_second_impulse_only") is True
           and case.get("actual_hardware_behavior_witnessed") is False
           and case.get("further_contact_response_solved") is False
           and case.get("derived_receiver_constructed") is False
           and case.get("formal_floating_point_interval_certificate") is False,
           "nominal mathematical result promoted to physical/formal proof")
    impulse = case.get("source_candidate_impulse")
    status = case.get("status")
    rows = case.get("per_vertex_bounds")
    demand(type(rows) is list, "missing per-vertex record list")
    if impulse is None:
        demand(status == ABSENT
               and case.get("source_trial18_status") == "NO_ADMITTED_RENEWED_CONTACT"
               and rows == []
               and case.get("worst_positive_margin") is None
               and case.get("all_corner_halfspace_clearance_supported") is False,
               "nonexistent second impulse became proved clearance")
        return False
    demand(type(impulse) is dict and
           impulse.get("selected_as_actual_material_response") is False
           and finite(impulse.get("normal_impulse"))
           and impulse["normal_impulse"] > 0
           and case.get("bounding_method") ==
           "four rotated-corner Taylor lower bounds; whole interval"
           and case.get("nominal_real_arithmetic_only") is True
           and case.get("postcontact_motion_assumed_ballistic") is True
           and case.get("no_additional_contacts_or_forces_in_assumed_window") is True,
           "undeclared local second impulse or model assumptions")
    demand(status == SEPARATED
           and case.get("all_corner_halfspace_clearance_supported") is True
           and case.get("line_clearance_implies_finite_face_clearance") is True
           and type(rows) is list and len(rows) == 4
           and finite(case.get("worst_positive_margin"))
           and case["worst_positive_margin"] > MIN_MARGIN,
           "unsupported conditional half-space separation claim")
    margins = []
    for i, row in enumerate(rows):
        demand(type(row) is dict and row.get("corner_index") == i
               and row.get("accepted") is True
               and row.get("admission_condition") in (
                   "touching-corner-derivative-positive-entire-window",
                   "noncontact-corner-quadratic-lower-bound-positive")
               and all(finite(row.get(key)) for key in (
                   "source_signed_gap_at_contact",
                   "outgoing_signed_gap_derivative",
                   "absolute_second_derivative_bound",
                   "quadratic_lower_bound_at_window_end",
                   "derivative_lower_bound_at_window_end",
                   "conservative_margin"))
               and row["conservative_margin"] > MIN_MARGIN,
               "source corner bound, order, or margin changed")
        margins.append(row["conservative_margin"])
    demand(abs(case["worst_positive_margin"] - min(margins)) < 1e-8,
           "minimum source margin inconsistent")
    # Mathematical authentication belongs ONLY to the original oracle,
    # not these structurally checked, source-attributed records.
    return True


def carry(native: dict, source_commit: str = PIN) -> dict:
    demand(source_commit == PIN, "immutable original WORLD19 source pin changed")
    demand(type(native) is dict and native.get("schema") == SOURCE
           and native.get("source_trial18") == TRIAL18
           and native.get("angles") == list(ANGLES)
           and native.get("physics_engine_created") is False
           and native.get("all_earth_physics_verified") is False
           and native.get("new_receiver_created") is False,
           "original trial roster or provenance changed")
    cases = native.get("cases")
    demand(type(cases) is list and len(cases) == 8,
           "eight original WORLD19 source controls required")
    owner = {"kind": "source-execution", "source": "WORLD19 @" + PIN}
    declared = {"kind": "declared",
                "source": "hypothesis: conditional separation over finite interval"}
    pages = []
    separated = 0
    missing = 0
    for index, angle in enumerate(ANGLES):
        case = cases[index]
        supported = inspect_case(case, angle)
        separated += int(supported)
        missing += int(not supported)
        steps = [
            {"op": "introduce", "id": "original-finite-source-face",
             "state": {"face_center": deepcopy(case["finite_face_origin"]),
                       "half_extent": case["half_extent"],
                       "source_angle": angle, "mathematical_source_only": True},
             "basis": owner},
            {"op": "introduce", "id": "conditional-rotating-square",
             "state": {"source_second_impulse_hypothesis":
                       deepcopy(case["source_candidate_impulse"]),
                       "physical_response_selected": False,
                       "continued_material_motion": None,
                       "postcontact_window": WINDOW}, "basis": owner},
            {"op": "connect", "id": "source-separation-test",
             "from": "original-finite-source-face",
             "to": "conditional-rotating-square",
             "label": "nominal-ballistic-halfspace-separation-test",
             "state": {"source_angle": angle,
                       "original_impulse_conditional": True,
                       "scope": "original supporting line, 0.016 virtual time"},
             "basis": declared},
            {"op": "observe", "id": "original-trial19-numerical-report",
             "entity": "object", "subject": "original-finite-source-face",
             "reading": {"status": case["status"],
                         "source_case_sha256": digest(case),
                         "source_trial18_status": case["source_trial18_status"],
                         "original_candidate_impulse":
                             deepcopy(case["source_candidate_impulse"]),
                         "reported_corner_bounds":
                             deepcopy(case["per_vertex_bounds"]),
                         "not_outward_rounded_or_physical": True},
             "basis": owner},
            {"op": "observe", "id": "bounded-separation-claim",
             "entity": "object", "subject": "conditional-rotating-square",
             "reading": {"conditional_whole_interval_separation": supported,
                         "nominal_model_only": True,
                         "formal_certificate": False,
                         "second_impulse_is_hypothesis": True,
                         "hardware_measurement": False,
                         "receiver_built": False},
             "basis": owner},
            {"op": "compare", "id": "conditional-separation-versus-no-proof",
             "observation": "bounded-separation-claim",
             "expected": {"conditional_whole_interval_separation": False,
                          "nominal_model_only": True,
                          "formal_certificate": False,
                          "second_impulse_is_hypothesis": True,
                          "hardware_measurement": False,
                          "receiver_built": False},
             "basis": declared},
        ]
        plan = {"schema": PLAN,
                "referent": f"WORLD19 / bounded conditional separation / {angle}deg",
                "limits": {"objects": 2, "relations": 1, "steps": len(steps)},
                "steps": steps}
        receipt = run_plan(plan)
        witness = verify_receipt(receipt)
        demand(witness["valid"] and set(receipt["final"]["objects"]) ==
               {"original-finite-source-face", "conditional-rotating-square"}
               and receipt["final"]["comparisons"]
               ["conditional-separation-versus-no-proof"]["result"]
               == ("DIFFERENT" if supported else "MATCH"),
               "bounded neutral receipt/contrast changed")
        pages.append({"index": index, "angle": angle,
                      "status": case["status"],
                      "conditional_whole_interval_separation": supported,
                      "receipt": receipt, "witness": witness})
    demand(native.get("conditional_continuous_clearance_count") == separated == 6
           and native.get("no_second_impulse_count") == missing == 2
           and native.get("inconclusive_count") == 0,
           "original conditional model case counts changed")
    manifest = {"source_commit": PIN, "source_sha256": digest(native),
                "ordered_pages": [
                    {"index": p["index"], "angle": p["angle"],
                     "head_hash": p["receipt"]["head_hash"]}
                    for p in pages]}
    return {
        "schema": SCHEMA, "source_commit": PIN,
        "source_cases": 8, "conditional_nominal_separation_cases": separated,
        "no_second_impulse_controls": missing,
        "interval_virtual_duration": WINDOW,
        "mathematical_intervals_formally_certified": 0,
        "physical_contacts_measured": 0, "receivers_constructed": 0,
        "postcontact_material_trajectories_verified": 0,
        "ledger_pages": pages,
        "ledger_witness": {
            "valid": all(p["witness"]["valid"] for p in pages),
            "pages_verified": len(pages),
            "steps_verified": sum(p["witness"]["steps_verified"] for p in pages),
            "observations_recorded": sum(
                p["witness"]["observations_recorded"] for p in pages)},
        "manifest": manifest, "manifest_sha256": digest(manifest),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--native", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(carry(load_json(args.native)), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
