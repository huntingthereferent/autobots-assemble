"""A/B WORLD21: conditional third impulse at existing modeled receiver.

Original pinned WORLD21 source and independent original numerical oracle own
contact mathematics. This neutral carrier separately records source-reported
relationships, conditional model evidence and eight tamper-witnessed histories.
No material trajectory or fourth interaction is inferred or constructed.
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

PIN = "75a78478b3a437f55e8efc138d746c8096dae8d9"
SCHEMA = "ab-world-trial21-conditional-third-impulse-handoff/v1"
SOURCE = "world-ab-conditional-third-contact/v1"
SOURCE20 = "world-ab-rotating-source-derived-receiver/v1"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
ARRIVED = "CONDITIONAL_DERIVED_RECEIVER_REACHED"
ADMITTED = "CONDITIONAL_LOCAL_SEPARATION"
ABSENT = "NO_QUALIFYING_THIRD_CONTACT"
WINDOW = .008
DURATION = .25
SURFACES = ("receiver", "original_source", "world_left",
            "world_right", "world_bottom", "world_top")


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("A/B WORLD21: " + reason)


def finite(x: Any) -> bool:
    return type(x) in (int, float) and isfinite(x)


def point(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(finite(v) for v in x)


def validate_case(case: dict, previous: dict, angle: float) -> bool:
    require(type(case) is dict and type(previous) is dict
            and case.get("schema") == SOURCE
            and case.get("angle") == angle
            and previous.get("schema") == SOURCE20
            and previous.get("source_angle") == angle
            and case.get("source_trial20_schema") == SOURCE20
            and case.get("source_trial20_status") == previous.get("status")
            and case.get("source_receiver") == previous.get("receiver")
            and case.get("source_third_contact") == previous.get("next_contact")
            and case.get("relative_third_contact_time") == DURATION
            and case.get("local_window") == WINDOW,
            "original source lineage, finite controls, or receiver changed")
    require(case.get("third_impulse_model_hypothesis") is True
            and case.get("measured_material_response") is False
            and case.get("fourth_contact_selected") is False
            and case.get("another_receiver_constructed") is False
            and case.get("formal_interval_certificate") is False
            and case.get("first_second_contact_sources_unchanged") is True
            and previous.get("third_impulse_calculated") is False
            and previous.get("receiver_real_material_built") is False,
            "unwitnessed material outcome or later movement introduced")
    impulse = case.get("third_impulse")
    bounds = case.get("clearance_bounds")
    require(type(bounds) is list, "source 24-corner clearance record missing")
    if previous.get("status") == "NO_SOURCE_SECOND_IMPULSE":
        require(case.get("status") == ABSENT and impulse is None
                and bounds == [] and previous.get("receiver") is None
                and previous.get("next_contact") is None
                and previous.get("frames") == [],
                "source with no second impulse fabricated third response")
        return False
    require(previous.get("status") == ARRIVED
            and previous.get("third_collision_outcome_unresolved") is True
            and type(previous.get("receiver")) is dict
            and type(previous.get("next_contact")) is dict,
            "original virtual receiver was not admitted")
    r = previous["receiver"]
    contact = previous["next_contact"]
    require(r.get("id") == "motion-derived-finite-receiver"
            and contact.get("geometric_touch_only") is True
            and contact.get("third_impulse_assumed") is False
            and case.get("status") == ADMITTED
            and case.get("local_separation_only") is True
            and case.get("source_finite_faces_unchanged") is True
            and case.get("hypothetical_outgoing_motion_only") is True,
            "unsupported conditional third contact or separation")
    require(type(impulse) is dict
            and impulse.get("receiver_id") == r["id"]
            and impulse.get("contact_vertex_index") == contact.get("vertex_index")
            and impulse.get("contact_absolute_virtual_time") ==
            contact.get("absolute_virtual_time")
            and impulse.get("materially_witnessed") is False
            and impulse.get("law") ==
            "original frictionless unit-mass rigid square, restitution 1"
            and point(impulse.get("contact_point"))
            and point(contact.get("point"))
            and all(abs(a-b) < 3e-7 for a,b in
                    zip(impulse["contact_point"], contact["point"]))
            and point(impulse.get("contact_center"))
            and point(impulse.get("source_receiver_normal"))
            and point(r.get("normal"))
            and all(abs(a-b) < 3e-7 for a,b in
                    zip(impulse["source_receiver_normal"],r["normal"]))
            and point(impulse.get("incoming_velocity"))
            and point(impulse.get("outgoing_velocity"))
            and all(finite(impulse.get(key)) for key in
                    ("incoming_spin","outgoing_spin","normal_impulse",
                     "incoming_contact_normal_rate",
                     "outgoing_contact_normal_rate","lever_cross_normal",
                     "kinetic_energy_before","kinetic_energy_after"))
            and impulse["normal_impulse"] > 0
            and impulse["incoming_contact_normal_rate"] < 0
            and impulse["outgoing_contact_normal_rate"] > 0
            and abs(impulse["incoming_contact_normal_rate"] +
                    impulse["outgoing_contact_normal_rate"]) < 3e-7
            and abs(impulse["kinetic_energy_after"] -
                    impulse["kinetic_energy_before"]) < 3e-7,
            "source impulse feature, restitution or energy claim changed")
    require(len(bounds) == 24,
            "all four source corners against six finite planes required")
    for i, record in enumerate(bounds):
        surface = SURFACES[i // 4]
        corner = i % 4
        touching = surface == "receiver" and corner == impulse["contact_vertex_index"]
        require(type(record) is dict
                and record.get("surface") == surface
                and record.get("corner_index") == corner
                and record.get("starts_touching") is touching
                and record.get("accepted") is True
                and all(finite(record.get(field)) for field in (
                    "gap_at_third_contact","outgoing_gap_rate",
                    "curvature_upper_bound","end_gap_lower_bound",
                    "rate_lower_bound","conservative_margin"))
                and record["conservative_margin"] > 1e-5,
                "missing, reordered, or failed local source bound")
    # Independent original native tests, NOT this record transport,
    # rederive impulse and every actual trigonometric corner extremum.
    return True


def carry(native: dict, source20: dict, source_commit: str = PIN) -> dict:
    require(source_commit == PIN, "original pinned source SHA altered")
    require(type(native) is dict and native.get("schema") == SOURCE
            and native.get("source_trial20") == SOURCE20
            and native.get("angles") == list(ANGLES)
            and native.get("real_material_behavior_verified") is False
            and native.get("another_receiver_created") is False
            and native.get("general_multicontact_solver_present") is False,
            "original WORLD21 source schema or claim changed")
    require(type(source20) is dict and source20.get("schema") == SOURCE20
            and source20.get("angles") == list(ANGLES)
            and source20.get("real_material_receiver_fabricated") is False
            and source20.get("new_engine_or_world_created") is False,
            "original WORLD20 source controls changed")
    current = native.get("cases")
    earlier = source20.get("cases")
    require(type(current) is list and len(current) == 8
            and type(earlier) is list and len(earlier) == 8,
            "all eight original source controls required")
    original = {"kind": "source-execution",
                "source": "original WORLD21 numerical model @" + PIN}
    hypothesis = {"kind": "declared",
                  "source": "unselected frictionless third-impulse contact hypothesis"}
    pages = []
    accepted = absent = 0
    for index, angle in enumerate(ANGLES):
        case, previous = current[index], earlier[index]
        admitted = validate_case(case, previous, angle)
        accepted += int(admitted)
        absent += int(not admitted)
        steps = [
            {"op": "introduce", "id": "original-model-source",
             "state": {"angle": angle,
                       "source20_sha256": digest(previous),
                       "conditional_original_motion_only": True,
                       "hardware_source_authenticated": False},
             "basis": original},
            {"op": "introduce", "id": "conditional-moving-square",
             "state": {"angle": angle, "model_object_only": True,
                       "material_response_selected": False,
                       "third_contact_outcome": None},
             "basis": hypothesis},
            {"op": "connect", "id": "conditional-source-square",
             "from": "original-model-source", "to": "conditional-moving-square",
             "label": "trial20-source-conditioned-third-contact-study",
             "state": {"source20_status": previous["status"],
                       "physical_second_impulse_witnessed": False},
             "basis": hypothesis},
            {"op": "observe", "id": "original-source20-receiver-report",
             "entity": "object", "subject": "original-model-source",
             "reading": {"source20_status": previous["status"],
                         "source20_receiver": deepcopy(previous["receiver"]),
                         "source20_contact": deepcopy(previous["next_contact"]),
                         "source_sha256": digest(previous),
                         "material_receiver_constructed": False},
             "basis": original},
        ]
        if admitted:
            steps.extend([
                {"op": "introduce", "id": "existing-virtual-receiver",
                 "state": {**deepcopy(previous["receiver"]),
                           "virtual_source_model_only": True,
                           "actual_material_constructed": False},
                 "basis": original},
                {"op": "connect", "id": "square-to-existing-model-receiver",
                 "from": "conditional-moving-square",
                 "to": "existing-virtual-receiver",
                 "label": "source-supported-conditional-contact-geometry",
                 "state": {"receiver_preexisted_third_model_impulse": True,
                           "physical_contact_witnessed": False},
                 "basis": original},
                {"op": "observe", "id": "source-conditional-third-impulse",
                 "entity": "object", "subject": "existing-virtual-receiver",
                 "reading": {"original_hypothetical_impulse":
                             deepcopy(case["third_impulse"]),
                             "material_contact_selected": False,
                             "source_case_sha256": digest(case)},
                 "basis": original},
                {"op": "observe", "id": "source-local-corner-bounds",
                 "entity": "object", "subject": "existing-virtual-receiver",
                 "reading": {"source_bounds": deepcopy(case["clearance_bounds"]),
                             "local_interval": WINDOW,
                             "nominal_model_separation_only": True,
                             "formally_interval_certified": False,
                             "physical_motion_verified": False},
                 "basis": original},
            ])
        else:
            steps.append({
                "op": "observe", "id": "source-no-third-contact",
                "entity": "object", "subject": "conditional-moving-square",
                "reading": {"source_status": ABSENT, "source_sha256": digest(case),
                            "third_impulse": None, "future_contact_ruled_out": False},
                "basis": original})
        steps.extend([
            {"op": "observe", "id": "source-conditional-third-outcome",
             "entity": "object", "subject": "conditional-moving-square",
             "reading": {"third_impulse_candidate": admitted,
                         "conditional_local_separation": admitted,
                         "actual_material_response_selected": False,
                         "fourth_contact_solved": False,
                         "another_receiver_built": False},
             "basis": original},
            {"op": "compare", "id": "third-candidate-vs-absent-hypothesis",
             "observation": "source-conditional-third-outcome",
             "expected": {"third_impulse_candidate": False,
                          "conditional_local_separation": False,
                          "actual_material_response_selected": False,
                          "fourth_contact_solved": False,
                          "another_receiver_built": False},
             "basis": hypothesis},
        ])
        plan = {"schema": PLAN,
                "referent": f"WORLD21 / third modeled impulse / {angle} degrees",
                "limits": {"objects": 3, "relations": 2, "steps": len(steps)},
                "steps": steps}
        receipt = run_plan(plan)
        witness = verify_receipt(receipt)
        require(witness["valid"]
                and ("existing-virtual-receiver" in
                     receipt["final"]["objects"]) is admitted
                and receipt["final"]["comparisons"]
                ["third-candidate-vs-absent-hypothesis"]["result"]
                == ("DIFFERENT" if admitted else "MATCH"),
                "independent neutral ledger or bounded contrast failed")
        pages.append({"index": index, "angle": angle,
                      "model_third_impulse_candidate": admitted,
                      "source_status": case["status"],
                      "receipt": receipt, "witness": witness})
    require(native.get("candidate_third_impulses") == accepted == 6
            and native.get("local_conditional_separations") == accepted
            and native.get("cases_without_qualifying_third_contact") ==
            absent == 2,
            "original mathematical source counts altered")
    manifest = {
        "source_commit": PIN, "world21_source_sha256": digest(native),
        "world20_source_sha256": digest(source20),
        "ordered_pages": [{"index": p["index"], "angle": p["angle"],
                           "head_hash": p["receipt"]["head_hash"]}
                          for p in pages],
    }
    return {
        "schema": SCHEMA, "source_commit": PIN, "original_cases": 8,
        "conditional_third_impulses": accepted,
        "conditional_full_local_separations": accepted,
        "no_qualifying_third_contact_controls": absent,
        "local_window": WINDOW,
        "receivers_of_new_type_created": 0,
        "real_material_receivers_built": 0,
        "real_impulses_measured": 0,
        "fourth_contacts_solved": 0,
        "formal_interval_certificates": 0,
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--source20", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(carry(load_json(args.native), load_json(args.source20)),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
