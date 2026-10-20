"""A/B WORLD16: retain finite rotating-square sample refutations as source evidence.

Original Trial04/16 mathematical laws and independent geometry oracle remain in
the pinned source checkout. A/B does not solve physics. It records the sampled
ballistic projection as unverified, stops state revisions *before* a source
overlap, preserves rejected future projections as reports only, and constructs
no receiver.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from math import isfinite
from pathlib import Path
import json
from typing import Any

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

SCHEMA = "ab-world-trial16-sampled-rotation-handoff/v1"
SOURCE = "world-ab-rotating-square-clearance-check/v1"
PIN = "6d22286b1fd129ae4011d1abb55dd4c320d58a5a"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
STEP = .001
HORIZON = .06
OVERLAP = "ROTATING_BODY_OVERLAPS_ORIGINAL_FACE_AT_SAMPLE"
NO_OVERLAP = "NO_OVERLAP_DETECTED_IN_SHORT_SAMPLED_WINDOW"


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise ValueError("A/B WORLD16: " + explanation)


def finite(x: Any) -> bool:
    return type(x) in (int, float) and isfinite(x)


def pair(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(finite(z) for z in x)


def validate(case: dict, angle: float) -> None:
    require(type(case) is dict and case.get("schema") == SOURCE
            and case.get("angle") == angle, "source identity/angle changed")
    require(case.get("status") in (OVERLAP, NO_OVERLAP)
            and case.get("physical_observation") is False
            and case.get("next_receiver_built") is False
            and case.get("second_contact_computed") is False
            and case.get("continuous_clearance_verified") is False
            and case.get("no_overlap_between_samples_proven") is False
            and case.get("world_15_fixed_square_source_preserved") is True,
            "unsupported continuation or physical claim")
    require(case.get("observation_step") == STEP
            and case.get("observation_horizon") == HORIZON,
            "native finite observation window changed")
    first = case.get("first_contact")
    require(type(first) is dict and first.get("hit") is True
            and first.get("reason") == "FIRST_CONTACT_SOLVED"
            and first.get("angle_degrees") == angle
            and pair(first.get("normal"))
            and pair(first.get("first_contact_center"))
            and pair(first.get("velocity_after"))
            and finite(first.get("angular_velocity_after"))
            and finite(first.get("normal_impulse"))
            and type(first.get("candidate_receiver")) is dict
            and first["candidate_receiver"].get("surface_built") is False
            and first["candidate_receiver"].get("second_contact_witnessed") is False
            and first.get("after_look",{}).get("unconstrained_ballistic_projection_only") is True,
            "original first-impact mathematics or candidate status changed")
    require(case.get("next_receiver_candidate_only") == first["candidate_receiver"],
            "source proposed receiver substituted or promoted")
    samples = case.get("samples")
    require(type(samples) is list and len(samples) == 61,
            "61 original time samples are required")
    earliest = None
    for i, item in enumerate(samples):
        require(type(item) is dict and finite(item.get("dt"))
                and abs(item["dt"] - i * STEP) < 1e-9
                and pair(item.get("center")) and finite(item.get("orientation"))
                and type(item.get("finite_interior_overlap")) is bool
                and type(item.get("checked_corners")) is int
                and 0 <= item["checked_corners"] <= 4
                and (item.get("minimum_signed_clearance") is None
                     or finite(item.get("minimum_signed_clearance")))
                and (item.get("worst_corner_index") is None
                     or (type(item["worst_corner_index"]) is int
                         and 0 <= item["worst_corner_index"] <= 3)),
                "source sample clock, geometry or status invalid")
        if item["finite_interior_overlap"] and earliest is None:
            earliest = item["dt"]
    require(case.get("first_detected_overlap_at") == earliest
            and (case["status"] == OVERLAP) == (earliest is not None)
            and case.get("unmodeled_recontact_response_refused") is (earliest is not None),
            "first overlapping sample or refusal changed")
    # This adapter checks chronology and attribution, not original dynamics.
    # Pinned source-independent numerical oracle supplies physics verdict.


def carry(native: dict, source_commit: str = PIN) -> dict:
    require(source_commit == PIN, "source owner pin changed")
    require(type(native) is dict and native.get("schema") == SOURCE
            and native.get("angles") == list(ANGLES)
            and native.get("physical_world_verified") is False
            and native.get("continuous_rotating_polygon_solver_present") is False
            and native.get("new_world_or_renderer") is False,
            "original WORLD16 source controls or scope changed")
    cases = native.get("cases")
    require(type(cases) is list and len(cases) == 8,
            "all original square-angle source cases required")
    source_basis = {"kind": "source-execution",
                    "source": "original WORLD16 @" + source_commit}
    proposal_basis = {"kind": "declared",
                      "source": "unverified post-impact ballistic continuation"}
    pages = []
    overlap_count = 0
    no_overlap_count = 0
    projected_steps = 0
    for index, angle in enumerate(ANGLES):
        case = cases[index]
        validate(case, angle)
        first = case["first_contact"]
        blocked_at = case["first_detected_overlap_at"]
        collided = blocked_at is not None
        overlap_count += int(collided)
        no_overlap_count += int(not collided)
        steps = [
            {"op": "introduce", "id": "original-finite-face",
             "state": {"normal": deepcopy(first["normal"]),
                       "center": deepcopy(first["source_wall_center"]),
                       "span": first["source_wall_span"],
                       "virtual": True}, "basis": source_basis},
            {"op": "introduce", "id": "projected-rotating-square",
             "state": {"center": deepcopy(first["first_contact_center"]),
                       "orientation": 0., "elapsed_after_first_impact": 0.,
                       "velocity": deepcopy(first["velocity_after"]),
                       "angular_velocity": first["angular_velocity_after"],
                       "state_kind": "unverified-ballistic-projection",
                       "hardware_measured": False}, "basis": source_basis},
            {"op": "connect", "id": "sample-original-face",
             "from": "original-finite-face", "to": "projected-rotating-square",
             "label": "declared-short-window-contact-check",
             "state": {"angle": angle, "sample_dt": STEP, "duration": HORIZON},
             "basis": proposal_basis},
            {"op": "observe", "id": "original-first-impact",
             "entity": "object", "subject": "projected-rotating-square",
             "reading": {"first_model_contact": deepcopy(first),
                         "hardware_measured": False}, "basis": source_basis},
        ]
        retained = 0
        for item in case["samples"]:
            # Projections after an observed overlap remain in the full source
            # report, but MUST NOT become continued A/B object state.
            if collided and item["dt"] >= blocked_at - 1e-10:
                break
            steps.append({
                "op": "revise", "entity": "object",
                "id": "projected-rotating-square",
                "after": {"center": deepcopy(item["center"]),
                          "orientation": item["orientation"],
                          "elapsed_after_first_impact": item["dt"],
                          "velocity": deepcopy(first["velocity_after"]),
                          "angular_velocity": first["angular_velocity_after"],
                          "state_kind": "unverified-ballistic-projection",
                          "hardware_measured": False},
                "basis": proposal_basis})
            retained += 1
        projected_steps += retained
        steps.extend([
            {"op": "observe", "id": "complete-source-sampled-evidence",
             "entity": "object", "subject": "original-finite-face",
             "reading": {"samples": deepcopy(case["samples"]),
                         "case_sha256": digest(case),
                         "sampled_source_only": True,
                         "continuous_clearance_verified": False,
                         "hardware_measured": False},
             "basis": source_basis},
            {"op": "observe", "id": "first-sample-contrast",
             "entity": "object", "subject": "projected-rotating-square",
             "reading": {"overlap_detected": collided,
                         "physical_observation": False},
             "basis": source_basis},
            {"op": "compare", "id": "unconstrained-no-overlap-prediction",
             "observation": "first-sample-contrast",
             "expected": {"overlap_detected": False,
                          "physical_observation": False},
             "basis": proposal_basis},
            {"op": "observe", "id": "bounded-continuation-verdict",
             "entity": "object", "subject": "projected-rotating-square",
             "reading": {"source_status": case["status"],
                         "first_detected_overlap_at": blocked_at,
                         "rejected_projection_samples_remain_source_only":
                             61 - retained,
                         "candidate_receiver": deepcopy(case["next_receiver_candidate_only"]),
                         "receiver_built": False, "second_impact_solved": False,
                         "hardware_measured": False,
                         "continuous_clearance_verified": False},
             "basis": source_basis},
        ])
        plan = {"schema": PLAN,
                "referent": f"WORLD16 / rotating-square angle {angle}",
                "limits": {"objects": 2, "relations": 1, "steps": len(steps)},
                "steps": steps}
        receipt = run_plan(plan)
        witnessed = verify_receipt(receipt)
        require(witnessed["valid"], "independent neutral receipt failed")
        require("receiver" not in receipt["final"]["objects"],
                "unverified physical receiver constructed")
        require(receipt["final"]["comparisons"]
                ["unconstrained-no-overlap-prediction"]["result"]
                == ("DIFFERENT" if collided else "MATCH"),
                "source counterexample contrast changed")
        pages.append({"index": index, "angle": angle,
                      "status": case["status"],
                      "first_detected_overlap_at": blocked_at,
                      "projected_revisions_before_refutation": retained,
                      "receipt": receipt, "witness": witnessed})
    counts = native.get("counts")
    require(type(counts) is dict
            and counts.get("sampled-overlap") == overlap_count
            and counts.get("sampled-no-overlap") == no_overlap_count
            and overlap_count == 6 and no_overlap_count == 2,
            "original eight-angle source counts changed")
    manifest = {
        "pinned_source": source_commit,
        "native_sha256": digest(native),
        "ordered_pages": [{"index": p["index"], "angle": p["angle"],
                           "head_hash": p["receipt"]["head_hash"]}
                          for p in pages]
    }
    return {"schema": SCHEMA, "source_commit": source_commit,
            "source_cases": len(cases), "overlaps_refuting_projection": overlap_count,
            "sample_windows_without_detected_overlap": no_overlap_count,
            "sampled_points_retained": sum(len(c["samples"]) for c in cases),
            "projected_state_revisions": projected_steps,
            "receiver_constructions": 0, "second_impulses_solved": 0,
            "real_physical_measurements": 0,
            "continuous_clearance_proven": False,
            "pages": pages,
            "ledger_witness": {
                "valid": all(p["witness"]["valid"] for p in pages),
                "pages_verified": len(pages),
                "steps_verified": sum(p["witness"]["steps_verified"] for p in pages),
                "observations_recorded": sum(
                    p["witness"]["observations_recorded"] for p in pages)},
            "manifest": manifest, "manifest_sha256": digest(manifest)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(carry(load_json(args.native)), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
