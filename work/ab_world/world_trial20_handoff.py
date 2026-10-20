"""Trial20: carry source-derived finite receiver under conditional rotating motion.

Pinned unchanged original WORLD18/20 source and independent numerical oracle
own the geometry. A/B records their reported relationships and candidate
movements, not a material receiver, third impulse, or actual future behavior.
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

PIN = "2a02b76b13dfb779d937e239505bc537e410e13f"
SCHEMA = "ab-world-trial20-conditional-motion-derived-receiver/v1"
SOURCE = "world-ab-rotating-source-derived-receiver/v1"
SOURCE18 = "world-ab-local-corner-recontact-impulse/v1"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
ARRIVED = "CONDITIONAL_DERIVED_RECEIVER_REACHED"
ABSENT = "NO_SOURCE_SECOND_IMPULSE"
DURATION = .25


def demand(ok: bool, explanation: str) -> None:
    if not ok:
        raise ValueError("A/B WORLD20: " + explanation)


def finite(x: Any) -> bool:
    return type(x) in (int, float) and isfinite(x)


def pair(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(finite(v) for v in x)


def check(original: dict, previous: dict, angle: float) -> bool:
    demand(type(original) is dict and original.get("schema") == SOURCE
           and original.get("source_trial18_schema") == SOURCE18
           and original.get("source_angle") == angle
           and original.get("source_first_return") ==
           previous.get("source_trial17_first_return")
           and original.get("original_source_wall_center") == [12., 1.5]
           and original.get("projection_duration") == DURATION
           and original.get("construction_policy") ==
           "normal opposite recorded outgoing centre velocity; pose-supported future face",
           "original WORLD18/20 source relationship changed")
    demand(original.get("model_movement_not_hardware_measurement") is True
           and original.get("third_impulse_calculated") is False
           and original.get("receiver_real_material_built") is False
           and original.get("nominal_floating_point_not_formal_interval") is True
           and original.get("earlier_world_sources_unchanged") is True,
           "modeled relation promoted to material or certified physical law")
    demand(previous.get("schema") == SOURCE18 and previous.get("angle") == angle
           and previous.get("physical_second_impact_observed") is False
           and previous.get("receiver_constructed") is False
           and previous.get("further_impacts_solved") is False,
           "previous conditional source became actual")
    conditional_impulse = previous.get("candidate_impulse")
    receiver = original.get("receiver")
    contact = original.get("next_contact")
    frames = original.get("frames")
    if conditional_impulse is None:
        demand(original.get("status") == ABSENT
               and previous.get("status") == "NO_ADMITTED_RENEWED_CONTACT"
               and receiver is None and contact is None and frames == [],
               "unsupported source produced a receiver or movement")
        return False
    demand(type(conditional_impulse) is dict and
           conditional_impulse.get("selected_as_actual_material_response") is False
           and original.get("status") == ARRIVED
           and original.get("source_clearance_entire_interval_checked") is True
           and original.get("receiver_clearance_entire_interval_checked") is True
           and original.get("world_boundary_clearance_entire_interval_checked") is True
           and original.get("third_collision_outcome_unresolved") is True,
           "source had not supported conditional receiver approach")
    demand(type(receiver) is dict and
           receiver.get("id") == "motion-derived-finite-receiver"
           and receiver.get("constructed_from") ==
           "Trial18 conditional outgoing velocity and square rotation"
           and receiver.get("source_corner") ==
           conditional_impulse.get("contact_vertex_index")
           and receiver.get("activated_at_relative_time") == 0
           and receiver.get("proposed_target_time") == DURATION
           and pair(receiver.get("normal"))
           and pair(receiver.get("anchor"))
           and type(receiver.get("endpoints")) is list
           and len(receiver["endpoints"]) == 2
           and all(pair(p) for p in receiver["endpoints"]),
           "rotation-derived receiver model ancestry missing")
    demand(type(contact) is dict and
           contact.get("at_relative_time") == DURATION
           and contact.get("geometric_touch_only") is True
           and contact.get("third_impulse_assumed") is False
           and type(contact.get("vertex_index")) is int
           and 0 <= contact["vertex_index"] < 4
           and pair(contact.get("point"))
           and finite(contact.get("absolute_virtual_time"))
           and finite(contact.get("incoming_normal_vertex_rate"))
           and contact["incoming_normal_vertex_rate"] < 0,
           "third contact geometry promoted into solved impulse")
    demand(type(frames) is list and len(frames) == 11,
           "original 11 conditional motion poses missing")
    for i, frame in enumerate(frames):
        demand(type(frame) is dict
               and finite(frame.get("time"))
               and abs(frame["time"] - DURATION*i/10) < 1e-9
               and pair(frame.get("center"))
               and finite(frame.get("orientation")),
               "source time-sampled rotation history changed")
    # Source native tests independently verify all geometry and
    # full-interval clearance; this adapter only transports it.
    return True


def carry(native: dict, original18: dict, source_commit: str = PIN) -> dict:
    demand(source_commit == PIN, "immutable original WORLD20 source SHA changed")
    demand(type(native) is dict and native.get("schema") == SOURCE
           and native.get("angles") == list(ANGLES)
           and native.get("real_material_receiver_fabricated") is False
           and native.get("new_engine_or_world_created") is False,
           "original source version/claim changed")
    demand(type(original18) is dict and original18.get("schema") == SOURCE18
           and original18.get("angles") == list(ANGLES)
           and original18.get("material_contact_response_proven") is False
           and original18.get("created_any_new_receiver") is False,
           "original prior source claim changed")
    cases, prior = native.get("cases"), original18.get("cases")
    demand(type(cases) is list and len(cases) == 8
           and type(prior) is list and len(prior) == 8,
           "all eight original source movements required")
    owner = {"kind": "source-execution", "source": "original WORLD20 @" + PIN}
    conditional = {"kind": "declared",
                   "source": "conditional original Trial18 second impulse and rotating-square motion"}
    pages = []
    arrivals = 0
    absent = 0
    frames_count = 0
    for index, angle in enumerate(ANGLES):
        case = cases[index]
        earlier = prior[index]
        reached = check(case, earlier, angle)
        arrivals += int(reached)
        absent += int(not reached)
        steps = [
            {"op": "introduce", "id": "original-square-motion-source",
             "state": {"source_angle": angle,
                       "trial18_source_impulse":
                       deepcopy(earlier["candidate_impulse"]),
                       "source_first_return":
                       deepcopy(case["source_first_return"]),
                       "real_material_measurement": False},
             "basis": owner},
            {"op": "introduce", "id": "candidate-rotating-square",
             "state": {"kind": "virtual-model", "source_angle": angle,
                       "physical_receiver_built": False,
                       "hypothetical_motion_only": True}, "basis": conditional},
            {"op": "connect", "id": "original-motion-hypothesis",
             "from": "original-square-motion-source",
             "to": "candidate-rotating-square",
             "label": "conditional-second-impulse-controls-rotation",
             "state": {"physical_second_impulse_selected": False},
             "basis": conditional},
            {"op": "observe", "id": "source-report-scope",
             "entity": "object", "subject": "candidate-rotating-square",
             "reading": {"source_case_sha256": digest(case),
                         "prior_source_case_sha256": digest(earlier),
                         "source_status": case["status"],
                         "source_scope": "0.25 virtual time after hypothetical impulse",
                         "material_measurement": False,
                         "third_impulse_solved": False},
             "basis": owner},
        ]
        if reached:
            for i,frame in enumerate(case["frames"]):
                steps.append({
                    "op": "observe", "id": f"proposed-model-pose-{i:02d}",
                    "entity": "object", "subject": "candidate-rotating-square",
                    "reading": {"source_frame": deepcopy(frame),
                                "candidate_ballistic_pose_only": True,
                                "physical_motion_verified": False},
                    "basis": owner})
            # Derived geometry enters the *A/B hypothesis* only after the
            # witnessed source-owned conditional path and geometric check.
            steps.extend([
                {"op": "observe", "id": "conditional-source-clearance",
                 "entity": "object", "subject": "candidate-rotating-square",
                 "reading": {"original_source_clearance":
                             case["source_clearance_entire_interval_checked"],
                             "derived_receiver_clearance":
                             case["receiver_clearance_entire_interval_checked"],
                             "world_perimeter_clearance":
                             case["world_boundary_clearance_entire_interval_checked"],
                             "nominal_real_arithmetic_not_formally_certified": True,
                             "source_native_not_ledger_verifies_math": True},
                 "basis": owner},
                {"op": "introduce", "id": "conditional-finite-receiver",
                 "state": {**deepcopy(case["receiver"]),
                           "virtual_model_only": True,
                           "physical_material_constructed": False},
                 "basis": conditional},
                {"op": "connect", "id": "receiver-derived-from-model-motion",
                 "from": "candidate-rotating-square",
                 "to": "conditional-finite-receiver",
                 "label": "pose-supported-movement-derived-finite-face",
                 "state": {"source_motion_only": True,
                           "time_horizon": DURATION,
                           "actual_material_collision": False},
                 "basis": conditional},
                {"op": "observe", "id": "conditional-third-contact-feature",
                 "entity": "object", "subject": "conditional-finite-receiver",
                 "reading": {"modeled_contact_geometry":
                             deepcopy(case["next_contact"]),
                             "third_impulse_calculated": False,
                             "material_collision_measured": False,
                             "future_contact_response_selected": False},
                 "basis": owner},
            ])
            frames_count += len(case["frames"])
        else:
            steps.append({
                "op": "observe", "id": "no-source-second-impulse",
                "entity": "object", "subject": "candidate-rotating-square",
                "reading": {"source_status": ABSENT,
                            "receiver": None,
                            "second_impulse_hypothesis": None,
                            "future_movement_selected": False},
                "basis": owner})
        steps.extend([
            {"op": "observe", "id": "bounded-receiver-presence",
             "entity": "object", "subject": "candidate-rotating-square",
             "reading": {"virtual_receiver_supported": reached,
                         "real_material_receiver_built": False},
             "basis": owner},
            {"op": "compare", "id": "receiver-versus-no-receiver-hypothesis",
             "observation": "bounded-receiver-presence",
             "expected": {"virtual_receiver_supported": False,
                          "real_material_receiver_built": False},
             "basis": conditional},
        ])
        plan = {"schema": PLAN,
                "referent": f"WORLD20 / conditional rotating receiver / {angle}deg",
                "limits": {"objects": 3, "relations": 2,
                           "steps": len(steps)}, "steps": steps}
        receipt = run_plan(plan)
        witness = verify_receipt(receipt)
        demand(witness["valid"] and
               ("conditional-finite-receiver" in receipt["final"]["objects"]) == reached
               and receipt["final"]["comparisons"]
               ["receiver-versus-no-receiver-hypothesis"]["result"]
               == ("DIFFERENT" if reached else "MATCH"),
               "ledger independently witnessed wrong model construction")
        pages.append({"index": index, "angle": angle,
                      "conditional_receiver_reached": reached,
                      "receipt": receipt, "witness": witness})
    demand(native.get("conditional_receiver_arrivals") == arrivals == 6
           and native.get("no_source_second_impulse") == absent == 2,
           "source conditional arrivals/absent-case counts changed")
    manifest = {"pinned_source": PIN,
                "original_world20_sha256": digest(native),
                "original_world18_sha256": digest(original18),
                "ordered_pages": [{"index": p["index"], "angle": p["angle"],
                                   "head_hash": p["receipt"]["head_hash"]}
                                  for p in pages]}
    return {"schema": SCHEMA, "source_commit": PIN,
            "source_controls": 8, "source_conditional_receiver_arrivals": arrivals,
            "no_second_impulse_controls": absent,
            "source_candidate_model_frames": frames_count,
            "real_material_receiver_constructions": 0,
            "third_impulses_calculated_by_adapter": 0,
            "real_physical_measurements": 0,
            "formal_interval_certificates": 0,
            "ledger_pages": pages,
            "ledger_witness": {
                "valid": all(p["witness"]["valid"] for p in pages),
                "pages_verified": len(pages),
                "steps_verified": sum(p["witness"]["steps_verified"] for p in pages),
                "observations_recorded": sum(
                    p["witness"]["observations_recorded"] for p in pages)},
            "manifest": manifest, "manifest_sha256": digest(manifest)}


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--previous",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(carry(load_json(a.native),load_json(a.previous)),
                     sort_keys=True,indent=2))


if __name__=="__main__":
    main()
