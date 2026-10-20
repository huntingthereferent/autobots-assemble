"""WORLD16 sampled angular/clearance evidence, not validated body continuation.

Original source dynamics and independent rotating-vertex source verifier own
all proposed square geometry. The A/B carrier records each finite sample as
a source-owned *hypothetical projection*, including samples after refusal;
it does not animate them as a supported physical trajectory or build a face.
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

SCHEMA = "ab-world-trial16-sampled-square-refusal-handoff/v1"
NATIVE = "world-ab-rotating-square-clearance-check/v1"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
OVERLAP = "ROTATING_BODY_OVERLAPS_ORIGINAL_FACE_AT_SAMPLE"
CLEAR = "NO_OVERLAP_DETECTED_IN_SHORT_SAMPLED_WINDOW"
DT = .001
HORIZON = .06


def demand(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("WORLD16 A/B: " + reason)


def finite(v: Any) -> bool:
    return type(v) in (int, float) and isfinite(v)


def pair(v: Any) -> bool:
    return type(v) is list and len(v) == 2 and all(finite(t) for t in v)


def carry(native: dict[str, Any], source_commit: str) -> dict[str, Any]:
    demand(type(source_commit) is str and
           re.fullmatch(r"[a-f0-9]{40}", source_commit) is not None,
           "exact source SHA required")
    demand(type(native) is dict and native.get("schema") == NATIVE and
           native.get("angles") == list(ANGLES) and
           native.get("physical_world_verified") is False and
           native.get("continuous_rotating_polygon_solver_present") is False and
           native.get("new_world_or_renderer") is False,
           "original bounded source scope changed")
    cases = native.get("cases")
    demand(type(cases) is list and len(cases) == len(ANGLES),
           "eight source incidence angles required")
    basis = {"kind": "source-execution",
             "source": "pinned WORLD Trial16 @" + source_commit}
    model = {"kind": "declared",
             "source": "source-proposed 0.001s sampled square ballistic projection"}
    pages = []
    overlaps = 0
    undetected = 0
    samples_total = 0
    first_overlap_times = []
    for case_idx, angle in enumerate(ANGLES):
        case = cases[case_idx]
        demand(type(case) is dict and case.get("schema") == NATIVE and
               case.get("angle") == angle and
               case.get("physical_observation") is False,
               "original angle/source material label substituted")
        original = case.get("first_contact")
        demand(type(original) is dict and original.get("hit") is True and
               type(original.get("candidate_receiver")) is dict and
               original["candidate_receiver"].get("surface_built") is False and
               type(original.get("after_look")) is dict and
               original["after_look"].get("continuous_contact_retested") is False,
               "original first collision/receiver provenance changed")
        demand(case.get("source_model") ==
               "unchanged original WORLD trial 04 rigid-square single impact" and
               case.get("next_receiver_candidate_only") ==
               original["candidate_receiver"] and
               case.get("next_receiver_built") is False and
               case.get("second_contact_computed") is False and
               case.get("no_overlap_between_samples_proven") is False and
               case.get("continuous_clearance_verified") is False and
               case.get("world_15_fixed_square_source_preserved") is True,
               "sampled square result promoted to constructed receiver/physics")
        demand(case.get("observation_step") == DT and
               case.get("observation_horizon") == HORIZON,
               "original source observation bounds changed")
        raw = case.get("samples")
        demand(type(raw) is list and len(raw) == 61,
               "all 61 predeclared finite sample positions required")
        steps = [
            {"op": "introduce", "id": "original-first-impact",
             "state": {"original_virtual_first_contact": deepcopy(original),
                       "physical_instrument_reading": False}, "basis": basis},
            {"op": "introduce", "id": "projected-rotating-square",
             "state": {"angle": angle,
                       "hypothetical_ballistic_projection": True,
                       "admitted_continuation": False,
                       "square_angular_motion_modelled": True,
                       "sample": None}, "basis": model},
            {"op": "connect", "id": "candidate-not-continued-contact",
             "from": "original-first-impact", "to": "projected-rotating-square",
             "label": "source-proposed-post-impact-projection",
             "state": {"receiver_built": False,
                       "continuous_clearance_proven": False}, "basis": model},
        ]
        first_bad = None
        for n, sample in enumerate(raw):
            demand(type(sample) is dict and finite(sample.get("dt")) and
                   abs(sample["dt"] - n * DT) < 1e-9 and
                   pair(sample.get("center")) and
                   finite(sample.get("orientation")) and
                   type(sample.get("checked_corners")) is int and
                   0 <= sample["checked_corners"] <= 4 and
                   type(sample.get("finite_interior_overlap")) is bool,
                   "source angular-sample time or finite geometry invalid")
            clearance = sample.get("minimum_signed_clearance")
            worst = sample.get("worst_corner_index")
            demand((clearance is None and worst is None and
                    sample["checked_corners"] == 0) or
                   (finite(clearance) and type(worst) is int and
                    0 <= worst <= 3 and sample["checked_corners"] > 0),
                   "source finite-face corner projection missing")
            if sample["finite_interior_overlap"] and first_bad is None:
                first_bad = sample["dt"]
            status = ("post-sampled-overlap-counterfactual" if
                      first_bad is not None and sample["dt"] > first_bad else
                      "first-detected-overlap" if first_bad == sample["dt"] else
                      "pre-refusal-hypothetical-projection")
            state = {"angle": angle,
                     "hypothetical_ballistic_projection": True,
                     "admitted_continuation": False,
                     "square_angular_motion_modelled": True,
                     "sample": deepcopy(sample),
                     "sample_status": status}
            steps.extend([
                {"op": "revise", "id": "projected-rotating-square",
                 "entity": "object", "after": state, "basis": basis},
                {"op": "observe", "id": f"source-projected-sample-{n:02d}",
                 "entity": "object", "subject": "projected-rotating-square",
                 "reading": {"native_proposed_sample": deepcopy(sample),
                             "proposed_state": status,
                             "material_sample_measured": False,
                             "valid_continued_dynamics": False},
                 "basis": basis},
            ])
        expected = OVERLAP if first_bad is not None else CLEAR
        demand(case.get("status") == expected and
               case.get("first_detected_overlap_at") == first_bad and
               case.get("unmodeled_recontact_response_refused") is
               (first_bad is not None),
               "source overlap/refusal conclusion altered")
        overlaps += int(first_bad is not None)
        undetected += int(first_bad is None)
        first_overlap_times.append(first_bad)
        samples_total += len(raw)
        steps.append({
            "op": "observe", "id": "source-sampled-window-conclusion",
            "entity": "object", "subject": "projected-rotating-square",
            "reading": {"source_status": expected,
                        "first_detected_overlap_at": first_bad,
                        "continued_collision_physics_solved": False,
                        "receiver_constructed": False,
                        "real_world_clearance_proven": False,
                        "original_case_sha256": digest(case)}, "basis": basis,
        })
        plan = {"schema": PLAN,
                "referent": f"WORLD16 / sampled angular projection at angle {angle}",
                "limits": {"objects": 2, "relations": 1,
                           "steps": len(steps)},
                "steps": steps}
        receipt = run_plan(plan)
        pages.append({
            "case": case_idx, "angle": angle, "first_overlap": first_bad,
            "source_status": expected, "receipt": receipt,
            "witness": verify_receipt(receipt)})
    demand(native.get("counts") ==
           {"sampled-overlap": overlaps, "sampled-no-overlap": undetected} and
           overlaps == 6 and undetected == 2,
           "source sampled-overlap counts changed")
    manifest = {"source_report_sha256": digest(native),
                "ordered_source_pages": [
                    {"case": p["case"], "angle": p["angle"],
                     "status": p["source_status"],
                     "head_hash": p["receipt"]["head_hash"]}
                    for p in pages]}
    witness = {"valid": all(p["witness"]["valid"] for p in pages),
               "pages_verified": len(pages),
               "steps_verified": sum(p["witness"]["steps_verified"] for p in pages),
               "observations_recorded": sum(
                   p["witness"]["observations_recorded"] for p in pages)}
    return {"schema": SCHEMA, "source_commit": source_commit,
            "source_sha256": digest(native),
            "cases": 8, "proposed_samples": samples_total,
            "sampled_overlap_cases": overlaps,
            "no_sampled_overlap_cases": undetected,
            "source_first_overlap_times": first_overlap_times,
            "completed_rotating_square_continuations": 0,
            "real_physical_samples_measured": 0,
            "second_contact_response_solved": False,
            "continuous_clearance_proven": False,
            "receiver_built": False,
            "source_physics_verified_by_adapter": False,
            "ledger_pages": pages, "ledger_witness": witness,
            "page_manifest": manifest,
            "page_manifest_sha256": digest(manifest)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    print(json.dumps(carry(load_json(args.native), args.source_commit),
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
