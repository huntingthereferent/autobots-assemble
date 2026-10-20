"""Retain original WORLD17 numerical first-return candidates in bounded A/B records.

The original WORLD17 source + independent fine-sweep oracle own contact
geometry. This carrier checks provenance, ordering, state/observation boundaries
and digest-linked reports, not physical correctness or root mathematics.
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

SCHEMA = "ab-world-trial17-finite-first-return-handoff/v1"
SOURCE = "world-ab-rotating-square-first-finite-recontact/v1"
PIN = "02b2f6ca97717eb3bf959d120a2c32a6ae856543"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
CANDIDATE = "FIRST_RENEWED_FINITE_FACE_CONTACT_CANDIDATE"
NO_RETURN = "NO_NEW_LINE_CROSSING_IN_WINDOW"
HORIZON = .06
SPAN = 1.0


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("A/B WORLD17: " + reason)


def num(x: Any) -> bool:
    return type(x) in (int, float) and isfinite(x)


def point(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(num(v) for v in x)


def validate_case(case: dict, angle: float) -> None:
    require(type(case) is dict and case.get("schema") == SOURCE
            and case.get("source_angle") == angle
            and case.get("source") == "unchanged original WORLD trial04 first square impact"
            and case.get("horizon") == HORIZON
            and case.get("source_finite_wall_preserved") is True,
            "source identity, control, or finite face changed")
    require(case.get("recontact_kinematics_only") is True
            and case.get("numerically_bracketed_not_exact_certified") is True
            and case.get("second_impulse_or_further_motion_solved") is False
            and case.get("derived_receiver_built") is False
            and case.get("physical_sensor_evidence") is False,
            "unwitnessed physical continuation introduced")
    require(case.get("method") ==
            "analytical corner gap stationary partitions plus numerical bisection",
            "source numerical method changed")
    original = case.get("source_original_first_contact")
    require(type(original) is dict and original.get("hit") is True
            and original.get("reason") == "FIRST_CONTACT_SOLVED"
            and original.get("angle_degrees") == angle
            and point(original.get("normal"))
            and point(original.get("source_wall_center"))
            and num(original.get("source_wall_span"))
            and original["source_wall_span"] == SPAN
            and point(original.get("first_contact_center"))
            and point(original.get("velocity_after"))
            and num(original.get("angular_velocity_after"))
            and num(original.get("normal_impulse"))
            and num(original.get("first_contact_time"))
            and type(original.get("candidate_receiver")) is dict
            and original["candidate_receiver"].get("surface_built") is False
            and original["candidate_receiver"].get("second_contact_witnessed") is False,
            "original first-contact source or receiver proposal substituted")
    require(type(case.get("monotonic_segments_checked")) is int
            and case["monotonic_segments_checked"] > 0,
            "source monotonic interval witness absent")
    roots = case.get("candidate_return_roots")
    require(type(roots) is list
            and all(type(r) is dict
                    and num(r.get("time")) and 0 < r["time"] <= HORIZON
                    and type(r.get("corner_index")) is int
                    and 0 <= r["corner_index"] < 4
                    and r.get("type") in
                    ("TRANSVERSE_SIGN_CROSSING", "UNRESOLVED_TOUCH")
                    for r in roots),
            "source root candidates absent or invalid")
    require(all(roots[i]["time"] <= roots[i + 1]["time"]
                for i in range(len(roots) - 1)),
            "candidate return roots were reordered")
    result = case.get("first_return")
    status = case.get("status")
    if result is None:
        require(status == NO_RETURN and roots == [],
                "no-return control invented a renewed contact")
        return
    require(status == CANDIDATE and type(result) is dict
            and num(result.get("dt_after_initial_contact"))
            and 0 < result["dt_after_initial_contact"] <= HORIZON
            and num(result.get("absolute_virtual_time"))
            and abs(result["absolute_virtual_time"] -
                    (original["first_contact_time"] +
                     result["dt_after_initial_contact"])) <= 1e-7
            and type(result.get("corner_index")) is int
            and 0 <= result["corner_index"] < 4
            and point(result.get("corner_position"))
            and num(result.get("source_face_tangent_coordinate"))
            and abs(result["source_face_tangent_coordinate"]) < SPAN / 2
            and num(result.get("normal_gap_residual"))
            and abs(result["normal_gap_residual"]) < 2e-7
            and num(result.get("incoming_normal_vertex_rate"))
            and result["incoming_normal_vertex_rate"] < 0
            and result.get("contact_feature") ==
            "square-vertex / original finite face interior"
            and result.get("second_impulse_selected") is False,
            "invalid modeled first-return candidate or selected second impulse")
    require(any(r["type"] == "TRANSVERSE_SIGN_CROSSING"
                and r["corner_index"] == result["corner_index"]
                and abs(r["time"] - result["dt_after_initial_contact"]) < 1e-7
                for r in roots),
            "contact candidate not present in original root search")
    require(abs(roots[0]["time"] - result["dt_after_initial_contact"]) < 1e-7,
            "first candidate does not follow source chronological earliest root")


def carry(native: dict, source_commit: str = PIN) -> dict:
    require(source_commit == PIN, "source pin changed")
    require(type(native) is dict and native.get("schema") == SOURCE
            and native.get("angles") == list(ANGLES)
            and native.get("horizon") == HORIZON
            and native.get("built_any_new_object") is False
            and native.get("actual_physical_impact_verified") is False,
            "original WORLD17 experiment identity changed")
    cases = native.get("cases")
    require(type(cases) is list and len(cases) == len(ANGLES),
            "all eight original angles required")
    owner = {"kind": "source-execution",
             "source": "original WORLD17 @" + PIN}
    declared = {"kind": "declared",
                "source": "hypothetical no-renewed-contact continuation"}
    pages = []
    candidate_count = 0
    no_return_count = 0
    for index, angle in enumerate(ANGLES):
        case = cases[index]
        validate_case(case, angle)
        original = case["source_original_first_contact"]
        returned = case["first_return"] is not None
        candidate_count += int(returned)
        no_return_count += int(not returned)
        steps = [
            {"op": "introduce", "id": "original-finite-source-face",
             "state": {"center": deepcopy(original["source_wall_center"]),
                       "span": original["source_wall_span"],
                       "normal": deepcopy(original["normal"]),
                       "virtual": True}, "basis": owner},
            {"op": "introduce", "id": "original-moving-square",
             "state": {"first_contact_center":
                       deepcopy(original["first_contact_center"]),
                       "first_contact_time": original["first_contact_time"],
                       "velocity_after_first": deepcopy(original["velocity_after"]),
                       "angular_velocity_after_first":
                       original["angular_velocity_after"],
                       "candidate_ballistic_projection_only": True,
                       "hardware_measured": False}, "basis": owner},
            {"op": "connect", "id": "source-square-contact-study",
             "from": "original-finite-source-face", "to": "original-moving-square",
             "label": "declared-rotating-square-first-return-study",
             "state": {"angle": angle, "horizon": HORIZON}, "basis": declared},
            {"op": "observe", "id": "original-first-contact",
             "entity": "object", "subject": "original-moving-square",
             "reading": {"source_first_contact": deepcopy(original),
                         "source_sha256": digest(original),
                         "physical_measurement": False}, "basis": owner},
            {"op": "observe", "id": "bounded-numerical-root-search",
             "entity": "object", "subject": "original-finite-source-face",
             "reading": {"roots": deepcopy(case["candidate_return_roots"]),
                         "monotonic_segments_checked":
                         case["monotonic_segments_checked"],
                         "numerically_bracketed_not_exact_certified": True,
                         "source_report_sha256": digest(case)}, "basis": owner},
        ]
        if returned:
            candidate = case["first_return"]
            steps.append({
                "op": "revise", "entity": "object", "id": "original-moving-square",
                "after": {"first_contact_center":
                          deepcopy(original["first_contact_center"]),
                          "first_contact_time": original["first_contact_time"],
                          "velocity_after_first": deepcopy(original["velocity_after"]),
                          "angular_velocity_after_first":
                          original["angular_velocity_after"],
                          "candidate_ballistic_projection_only": True,
                          "candidate_first_return": deepcopy(candidate),
                          "contact_response_not_computed": True,
                          "hardware_measured": False}, "basis": owner})
        steps.extend([
            {"op": "observe", "id": "source-return-verdict",
             "entity": "object", "subject": "original-moving-square",
             "reading": {"first_return_candidate": returned,
                         "first_return": deepcopy(case["first_return"]),
                         "source_status": case["status"],
                         "receiver_built": False,
                         "second_impulse_solved": False,
                         "physical_measurement": False}, "basis": owner},
            {"op": "observe", "id": "candidate-presence-contrast",
             "entity": "object", "subject": "original-finite-source-face",
             "reading": {"renewed_contact_candidate": returned,
                         "physical_event_verified": False}, "basis": owner},
            {"op": "compare", "id": "hypothetical-no-renewed-contact",
             "observation": "candidate-presence-contrast",
             "expected": {"renewed_contact_candidate": False,
                          "physical_event_verified": False},
             "basis": declared},
        ])
        plan = {"schema": PLAN, "referent":
                f"WORLD17 / first renewed finite-face square contact / {angle}deg",
                "limits": {"objects": 2, "relations": 1,
                           "steps": len(steps)}, "steps": steps}
        receipt = run_plan(plan)
        witness = verify_receipt(receipt)
        require(witness["valid"]
                and set(receipt["final"]["objects"]) ==
                {"original-finite-source-face", "original-moving-square"}
                and receipt["final"]["comparisons"]
                ["hypothetical-no-renewed-contact"]["result"]
                == ("DIFFERENT" if returned else "MATCH"),
                "neutral independent witness or candidate contrast changed")
        pages.append({
            "index": index, "angle": angle,
            "source_status": case["status"], "first_return_candidate": returned,
            "source_first_return": deepcopy(case["first_return"]),
            "receipt": receipt, "witness": witness
        })
    require(native.get("first_return_candidates") == candidate_count == 6
            and native.get("no_return") == no_return_count == 2,
            "original source outcome counts changed")
    manifest = {
        "pinned_source_commit": PIN,
        "source_sha256": digest(native),
        "ordered_pages": [
            {"index": page["index"], "angle": page["angle"],
             "source_status": page["source_status"],
             "head_hash": page["receipt"]["head_hash"]}
            for page in pages]
    }
    return {
        "schema": SCHEMA, "source_commit": PIN,
        "source_cases": len(cases), "numerical_first_return_candidates": 6,
        "no_new_line_crossings_in_window": 2,
        "receiver_constructions": 0, "second_impulses_solved": 0,
        "physical_measurements": 0, "continuous_clearance_proven": False,
        "pages": pages,
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
    a = p.parse_args()
    print(json.dumps(carry(load_json(a.native)), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
