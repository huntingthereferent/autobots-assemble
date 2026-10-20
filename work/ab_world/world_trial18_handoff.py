"""WORLD18 source conditional second impulses and short finite sample predictions.

No physical contact has been witnessed. The original model and independent
oracle own all mechanics. A/B only records hypothetical impulse proposals and
sampled predictions, preserving the unresolved continuation after the return.
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

SCHEMA = "ab-world-trial18-local-response-hypothesis-handoff/v1"
SOURCE = "world-ab-local-corner-recontact-impulse/v1"
TRIAL17 = "world-ab-rotating-square-first-finite-recontact/v1"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
HORIZON = .016
STEP = .0005
NO_CONTACT = "NO_ADMITTED_RENEWED_CONTACT"
OVERLAP = "LOCAL_OVERLAP_UNRESOLVED"
NO_DETECTED = "NO_OVERLAP_DETECTED_IN_LOCAL_SAMPLES"


def demand(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError("WORLD18 A/B: " + msg)


def number(x: Any) -> bool:
    return type(x) in (float, int) and isfinite(x)


def pair(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(number(v) for v in x)


def carry(native: dict[str, Any], source_commit: str) -> dict[str, Any]:
    demand(type(source_commit) is str and
           re.fullmatch("[a-f0-9]{40}", source_commit) is not None,
           "exact immutable source commit required")
    demand(type(native) is dict and native.get("schema") == SOURCE and
           native.get("angles") == list(ANGLES) and
           native.get("material_contact_response_proven") is False and
           native.get("created_any_new_receiver") is False and
           native.get("general_rotating_contact_solver") is False,
           "source schema, controls or physical boundary changed")
    cases = native.get("cases")
    demand(type(cases) is list and len(cases) == len(ANGLES),
           "all eight source controls required")
    owner = {"kind": "source-execution",
             "source": "original WORLD Trial18 @" + source_commit}
    model = {"kind": "declared",
             "source": "frictionless rotating-square single-normal e=1 model hypothesis"}
    pages = []
    admitted_candidates = 0
    refused = 0
    sampled_overlap = 0
    candidate_samples = 0
    for idx, angle in enumerate(ANGLES):
        case = cases[idx]
        demand(type(case) is dict and case.get("schema") == SOURCE and
               case.get("angle") == angle and
               case.get("source_trial17") == TRIAL17 and
               case.get("source_original_trial04") ==
               "world-ab-oblique-normal-angular-impact/v1" and
               case.get("local_time_horizon") == HORIZON and
               case.get("observation_step") == STEP,
               "original source angle, lineage or sampling bounds changed")
        demand(case.get("second_impulse_is_a_model_hypothesis") is True and
               case.get("physical_second_impact_observed") is False and
               case.get("receiver_constructed") is False and
               case.get("continuous_clearance_certified") is False and
               case.get("further_impacts_solved") is False,
               "proposed second response promoted to material physics")
        first_impact = case.get("source_first_contact")
        first_return = case.get("source_trial17_first_return")
        demand(type(first_impact) is dict and
               first_impact.get("hit") is True and
               first_impact.get("angle_degrees") == angle and
               type(first_impact.get("candidate_receiver")) is dict and
               first_impact["candidate_receiver"].get("surface_built") is False,
               "original first impact or source receiver changed")
        steps = [
            {"op": "introduce", "id": "original-virtual-first-impact",
             "state": {"source_first_contact": deepcopy(first_impact),
                       "real_sensor_evidence": False}, "basis": owner},
            {"op": "introduce", "id": "source-first-return-claim",
             "state": {"numerical_first_return": deepcopy(first_return),
                       "second_impulse": None,
                       "actual_contact_response_selected": False}, "basis": owner},
            {"op": "connect", "id": "source-first-impact-to-return",
             "from": "original-virtual-first-impact",
             "to": "source-first-return-claim",
             "label": "numerical-first-return-conditional-on-initial-impact",
             "state": {"physical_contact_selected": False}, "basis": model},
        ]
        status = case.get("status")
        impulse = case.get("candidate_impulse")
        raw_samples = case.get("post_contact_samples")
        if first_return is None:
            demand(status == NO_CONTACT and impulse is None and raw_samples == [],
                   "absence of renewed contact promoted to an impulse")
            steps.append({
                "op": "observe", "id": "no-admitted-source-recontact",
                "entity": "object", "subject": "source-first-return-claim",
                "reading": {"status": NO_CONTACT, "candidate_impulse": None,
                            "postcontact_model_motion": None,
                            "future_impact_ruled_out": False}, "basis": owner,
            })
            refused += 1
        else:
            demand(type(first_return) is dict and
                   number(first_return.get("dt_after_initial_contact")) and
                   number(first_return.get("absolute_virtual_time")) and
                   type(first_return.get("corner_index")) is int and
                   first_return["corner_index"] in (0,1,2,3) and
                   pair(first_return.get("corner_position")) and
                   first_return.get("second_impulse_selected") is False,
                   "source first-return candidate lost")
            demand(status in (OVERLAP, NO_DETECTED) and
                   case.get("next_movement_admitted_as_verified") is False and
                   type(impulse) is dict and
                   impulse.get("constitutive_hypothesis") ==
                   "single frictionless normal, e=1, rotating rigid square" and
                   impulse.get("selected_as_actual_material_response") is False,
                   "conditional impulse misrepresented as observed dynamics")
            demand(number(impulse.get("normal_impulse")) and
                   impulse["normal_impulse"] > 0 and
                   number(impulse.get("incoming_vertex_normal_rate")) and
                   impulse["incoming_vertex_normal_rate"] < 0 and
                   number(impulse.get("outgoing_vertex_normal_rate")) and
                   impulse["outgoing_vertex_normal_rate"] > 0 and
                   type(impulse.get("contact_vertex_index")) is int and
                   impulse["contact_vertex_index"] == first_return["corner_index"] and
                   number(impulse.get("contact_time_relative")) and
                   abs(impulse["contact_time_relative"] -
                       first_return["dt_after_initial_contact"]) < 2e-9 and
                   pair(impulse.get("contact_point")) and
                   all(abs(x-y)<3e-7 for x,y in
                       zip(impulse["contact_point"],first_return["corner_position"])) and
                   pair(impulse.get("velocity_before")) and
                   pair(impulse.get("velocity_after")) and
                   number(impulse.get("angular_velocity_after")) and
                   number(impulse.get("kinetic_energy_before")) and
                   number(impulse.get("kinetic_energy_after")) and
                   abs(impulse["kinetic_energy_before"] -
                       impulse["kinetic_energy_after"]) < 3e-7,
                   "candidate impulse detached from source geometry or energy")
            demand(type(raw_samples) is list and
                   len(raw_samples) == 1 + round(HORIZON / STEP),
                   "full original 33-sample local horizon required")
            steps.extend([
                {"op": "observe", "id": "source-hypothetical-local-impulse",
                 "entity": "object", "subject": "source-first-return-claim",
                 "reading": {"candidate_impulse": deepcopy(impulse),
                             "second_impulse_measured": False,
                             "continuation_admitted": False}, "basis": owner},
                {"op": "introduce", "id": "candidate-postreturn-sampling",
                 "state": {"second_impulse_hypothesis": deepcopy(impulse),
                           "sample": None, "conditional_only": True,
                           "admitted_continuation": False}, "basis": model},
                {"op": "connect", "id": "return-to-proposed-second-response",
                 "from": "source-first-return-claim",
                 "to": "candidate-postreturn-sampling",
                 "label": "counterfactual-second-impulse",
                 "state": {"real_contact_witnessed": False,
                           "next_receiver_built": False}, "basis": model},
            ])
            first_bad = None
            for j, sample in enumerate(raw_samples):
                demand(type(sample) is dict and
                       number(sample.get("dt_after_candidate")) and
                       abs(sample["dt_after_candidate"] - j*STEP) < 1e-9 and
                       pair(sample.get("center")) and
                       number(sample.get("orientation")),
                       "source virtual post-return sample time/pose changed")
                gap = sample.get("minimum_sampled_signed_face_gap")
                corner = sample.get("worst_finite_face_corner")
                tangent = sample.get("worst_finite_face_tangent")
                demand((gap is None and corner is None and tangent is None) or
                       (number(gap) and type(corner) is int and
                        0 <= corner < 4 and number(tangent)),
                       "source finite-face gap record invalid")
                if number(gap) and gap < -1e-8 and first_bad is None:
                    first_bad = sample["dt_after_candidate"]
                label = ("post-overlap-counterfactual" if
                         first_bad is not None and
                         sample["dt_after_candidate"] > first_bad else
                         "first-sampled-overlap" if first_bad == sample["dt_after_candidate"]
                         else "unvalidated-local-sample")
                state = {
                    "second_impulse_hypothesis": deepcopy(impulse),
                    "sample": deepcopy(sample),
                    "conditional_only": True, "admitted_continuation": False,
                    "sample_class": label,
                }
                steps.extend([
                    {"op": "revise", "entity": "object",
                     "id": "candidate-postreturn-sampling",
                     "after": state, "basis": owner},
                    {"op": "observe", "id": f"source-proposed-step-{j:02d}",
                     "entity": "object", "subject": "candidate-postreturn-sampling",
                     "reading": {"source_virtual_sample": deepcopy(sample),
                                 "sample_class": label,
                                 "measured_material": False,
                                 "continuous_motion_verified": False},
                     "basis": owner},
                ])
            expected = OVERLAP if first_bad is not None else NO_DETECTED
            demand(status == expected and
                   case.get("first_sampled_post_contact_overlap") == first_bad,
                   "source local sampled-overlap conclusion altered")
            steps.append({
                "op": "observe", "id": "source-local-conclusion",
                "entity": "object", "subject": "candidate-postreturn-sampling",
                "reading": {"source_status": status,
                            "source_case_sha256": digest(case),
                            "sampled_first_overlap": first_bad,
                            "continuous_clearance_not_certified": True,
                            "receiver_constructed": False,
                            "actual_material_response": None}, "basis": owner,
            })
            admitted_candidates += 1
            sampled_overlap += int(first_bad is not None)
            candidate_samples += len(raw_samples)
        plan = {"schema": PLAN,
                "referent": f"WORLD18 / bounded second-impulse hypothesis angle {angle}",
                "limits": {"objects": 3, "relations": 2, "steps": len(steps)},
                "steps": steps}
        receipt = run_plan(plan)
        pages.append({"case": idx, "angle": angle, "status": status,
                      "receipt": receipt, "witness": verify_receipt(receipt)})
    demand(native.get("cases_with_candidate_impulse") == admitted_candidates and
           native.get("cases_without_recontact") == refused and
           native.get("cases_with_sampled_post_overlap") == sampled_overlap and
           admitted_candidates == 6 and refused == 2,
           "native model hypothesis/refusal totals changed")
    manifest = {"source_report_sha256": digest(native),
                "ordered_case_heads": [
                    {"case": p["case"], "angle": p["angle"],
                     "status": p["status"], "head_hash": p["receipt"]["head_hash"]}
                    for p in pages]}
    witness = {"valid": all(p["witness"]["valid"] for p in pages),
               "pages_verified": len(pages),
               "steps_verified": sum(p["witness"]["steps_verified"] for p in pages),
               "observations_recorded": sum(
                   p["witness"]["observations_recorded"] for p in pages)}
    return {
        "schema": SCHEMA, "source_commit": source_commit,
        "source_report_sha256": digest(native),
        "candidate_second_impulses": admitted_candidates,
        "absent_first_returns": refused,
        "source_sampled_overlap_cases": sampled_overlap,
        "hypothetical_postreturn_samples": candidate_samples,
        "receivers_constructed": 0, "material_second_impulses_observed": 0,
        "valid_sustained_postcontact_motion_proven": False,
        "source_model_verified_by_adapter": False,
        "ledger_pages": pages, "ledger_witness": witness,
        "page_manifest": manifest,
        "page_manifest_sha256": digest(manifest),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--native", type=Path, required=True)
    p.add_argument("--source-commit", required=True)
    a = p.parse_args()
    print(json.dumps(carry(load_json(a.native), a.source_commit),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
