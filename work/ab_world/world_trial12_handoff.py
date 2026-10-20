"""Carry WORLD Trial12 nominal friction/spin candidate movements, never material physics.

Original native source and its independent friction/energy/geometry oracle own
candidate validity. This adapter only carries source-reported conditional
movements into independent, bounded A/B event records, one original case each.
No prior frictional two-contact uncertainty can be resolved by this adapter.
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

SCHEMA = "ab-world-trial12-friction-spin-candidate-handoff/v1"
NATIVE = "world-ab-single-active-friction-spin-controls/v1"
ANGLES = (-15, -5, 0, 10, 20, 30, 45)
ROTATIONS = (-15., -7.5, 0., 7.5, 15.)
FRICTIONS = (0., 0.2, 0.4)
SPINS = (0., 2.)
ACCEPTED = "admissible-single-active"


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("Trial12 A/B handoff: " + reason)


def isnum(x: Any) -> bool:
    return type(x) in (int, float) and isfinite(x)


def vector2(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(isnum(v) for v in x)


def carry(native: dict[str, Any], source_commit: str) -> dict[str, Any]:
    require(type(source_commit) is str and
            re.fullmatch("[a-f0-9]{40}", source_commit) is not None,
            "pin exact original source commit")
    require(type(native) is dict and native.get("schema") == NATIVE,
            "original source schema missing")
    require(native.get("source_trial09_schema") ==
            "world-ab-two-contact-incidence-stress/v1" and
            native.get("source_trial10_schema") ==
            "world-ab-two-contact-active-set-enumeration/v1",
            "original source lineage changed")
    require(native.get("incoming_angle_grid") == list(ANGLES) and
            native.get("source_rotation_grid") == list(ROTATIONS) and
            native.get("friction_grid") == list(FRICTIONS) and
            native.get("starting_spin_grid") == list(SPINS),
            "predeclared source experiment grid altered")
    require(native.get("restitution") == 1. and
            isnum(native.get("radius")) and native["radius"] > 0 and
            isnum(native.get("inertia")) and native["inertia"] > 0 and
            native.get("original_trial06_friction") == 0.4,
            "declared source material-model parameters changed")
    require(native.get("original_trial06_two_contact_solver_unchanged") is True,
            "original two-contact source was replaced")
    for flag in (
        "frictional_simultaneous_two_contact_manifold_solved",
        "actual_active_contact_observed", "sequential_real_contacts_measured",
        "real_material_equivalence", "physical_blueprint_generated",
    ):
        require(native.get(flag) is False,
                "unsupported real-world assertion: " + flag)
    geo = native.get("original_source_geometry")
    require(type(geo) is dict and type(geo.get("surfaces")) is list and
            len(geo["surfaces"]) == 2,
            "original source faces missing")
    original_ids = [f.get("id") if type(f) is dict else None
                    for f in geo["surfaces"]]
    require(all(type(s) is str and s.strip() for s in original_ids) and
            original_ids[0] != original_ids[1],
            "source face identity missing")
    source10 = native.get("original_trial10_counts")
    require(type(source10) is dict and
            source10.get("multiple-admissible") == 26 and
            source10.get("single-admissible") == 9 and
            source10.get("no-local-candidate") == 0,
            "frozen Trial10 source counts changed")
    cases = native.get("cases")
    require(type(cases) is list and len(cases) == 35,
            "35 source geometry cases required")
    source = {"kind": "source-execution",
              "source": "native WORLD Trial12 source @" + source_commit}
    model = {"kind": "declared",
             "source": "source conditional single-active friction/spin law"}
    pages = []
    accepted = 0
    rejected = 0
    frame_count = 0
    totals = {(omega, mu): [0, set(), set(), set()]
              for omega in SPINS for mu in FRICTIONS}
    for i, (rotation, angle) in enumerate(
            (d, a) for d in ROTATIONS for a in ANGLES):
        case = cases[i]
        require(type(case) is dict and
                case.get("original_index") == i and
                case.get("incoming_angle_degrees") == angle and
                case.get("surface_B_rotation_degrees") == rotation,
                "original case sequence substituted")
        geometry_kind = ("original-source-geometry" if rotation == 0
                         else "controlled-geometry-not-original")
        ids = case.get("source_ids")
        require(case.get("geometry_kind") == geometry_kind and
                type(ids) is list and len(ids) == 2 and
                (ids == original_ids if rotation == 0 else
                 ids[0] == original_ids[0] and ids[1] != original_ids[1]),
                "controlled geometry promoted to original")
        require(case.get("actual_active_contact_observed") is False and
                case.get("real_collision_outcome_selected") is False,
                "hypothetical contact promoted to observed outcome")
        require(case.get("original_trial10_classification") in (
            "multiple-admissible", "single-admissible"),
            "original Trial10 classification hidden")
        require(case.get("original_trial09_two_active_status") in (
            "accepted-local-candidate", "rejected-unilateral",
            "rejected-not-incoming", "rejected-constraint"),
            "prior Trial09 two-contact source status hidden")
        options = case.get("options")
        require(type(options) is list and len(options) == 12,
                "missing one of twelve source spin/friction/face controls")

        # Bounded source-specific plan for ONE case, not a new global WORLD.
        steps = [
            {"op": "introduce", "id": "original-mu04-junction",
             "state": {"source_case": i, "real_impulse": None,
                       "original_status": "unresolved-multiple-contacts"},
             "basis": source},
            {"op": "introduce", "id": "conditional-single-contact-model",
             "state": {"original_not_resolved": True,
                       "frictional_two_contact_solver": False,
                       "candidate_only": True}, "basis": model},
            {"op": "connect", "id": "original-to-hypotheses",
             "from": "original-mu04-junction",
             "to": "conditional-single-contact-model",
             "label": "conditional-not-observed", "state": {"winner": None},
             "basis": model},
            {"op": "introduce", "id": "source-case",
             "state": {"angle": angle, "rotation": rotation,
                       "geometry_kind": geometry_kind,
                       "source_ids": deepcopy(ids), "physical_winner": None,
                       "original_trial10_classification":
                           case["original_trial10_classification"],
                       "original_trial09_two_active_status":
                           case["original_trial09_two_active_status"]},
             "basis": source},
            {"op": "connect", "id": "hypotheses-for-case",
             "from": "conditional-single-contact-model", "to": "source-case",
             "label": "bounded-source-case", "state": {"case": i},
             "basis": model},
        ]
        for j, (omega, mu, face) in enumerate(
                (w, m, k) for w in SPINS for m in FRICTIONS for k in (0, 1)):
            option = options[j]
            require(type(option) is dict and
                    option.get("incoming_spin") == omega and
                    option.get("friction_coefficient") == mu and
                    option.get("face_index") == face and
                    option.get("face_id") == ids[face],
                    "candidate source active face/friction/spin changed")
            status = option.get("status")
            require(type(status) is str and
                    (status == ACCEPTED or status.startswith("rejected-")),
                    "unsupported source contact classification")
            require(isnum(option.get("normal_impulse")) and
                    option["normal_impulse"] > 0 and
                    isnum(option.get("tangential_impulse")) and
                    vector2(option.get("outgoing_velocity")) and
                    isnum(option.get("outgoing_spin")),
                    "missing conditional source impulse/spin computation")
            require(option.get("friction_cone_satisfied") is True and
                    type(option.get("slip_regime")) is str and
                    option["slip_regime"] in ("stick-candidate", "sliding-cap"),
                    "original single-contact friction assumption changed")
            for val in ("energy_before", "energy_after"):
                require(isnum(option.get(val)), "original candidate energy missing")
            frames = option.get("frames")
            ok = status == ACCEPTED
            if ok:
                require(option.get("reason") is None and
                        option.get("finite_horizon_verified") is True and
                        type(frames) is list and len(frames) == 31,
                        "admissible candidate missing full finite trajectory")
                accepted += 1
                frame_count += len(frames)
                totals[(omega, mu)][0] += 1
                totals[(omega, mu)][1].add(i)
                totals[(omega, mu)][2].add((i, face))
            else:
                require(type(option.get("reason")) is str and
                        option.get("finite_horizon_verified") is False and
                        frames == [] and
                        status == "rejected-" + option["reason"],
                        "rejected candidate given fictional completed motion")
                rejected += 1
                totals[(omega, mu)][3].add((i, face))
            key = f"conditional-{j:02d}"
            initial = {
                "status": status, "model_only": True, "case": i,
                "mu": mu, "incoming_spin": omega, "active_face": face,
                "source_face_id": ids[face], "finite_path_verified": ok,
            }
            steps.extend([
                {"op": "introduce", "id": key,
                 "state": deepcopy(initial), "basis": source},
                {"op": "connect", "id": f"candidate-link-{j:02d}",
                 "from": "source-case", "to": key,
                 "label": "candidate-not-physical-winner",
                 "state": {"completed_source_path": ok}, "basis": model},
            ])
            if ok:
                for index, frame in enumerate(frames):
                    require(type(frame) is dict and
                            isnum(frame.get("time")) and
                            abs(frame["time"] - index * 0.05) < 2e-8 and
                            vector2(frame.get("position")) and
                            vector2(frame.get("velocity")) and
                            isnum(frame.get("spin")) and
                            isnum(frame.get("orientation")),
                            "source spin or motion frame corrupted")
                    steps.append({
                        "op": "revise", "entity": "object", "id": key,
                        "after": {**initial, "source_frame": deepcopy(frame)},
                        "basis": source,
                    })
            # Rejected native options may contain an *attempted* impulse, but
            # have no successful finite trajectory. Preserve precisely that
            # distinction instead of discarding the attempted computation.
            reported = deepcopy(option)
            del reported["frames"]
            steps.append({
                "op": "observe", "id": f"source-candidate-{j:02d}",
                "entity": "object", "subject": key,
                "reading": {"original_model_record": reported,
                            "frames_count": len(frames),
                            "frames_sha256": digest(frames),
                            "real_contact_observed": False},
                "basis": source,
            })
        plan = {
            "schema": PLAN,
            "referent": f"WORLD Trial12 / conditional single-face case {i:02d}",
            "limits": {"objects": 15, "relations": 14,
                       "steps": len(steps)},
            "steps": steps,
        }
        receipt = run_plan(plan)
        pages.append({"case": i, "rotation": rotation, "angle": angle,
                      "receipt": receipt, "witness": verify_receipt(receipt)})
    rows = []
    for omega in SPINS:
        for mu in FRICTIONS:
            n, touched, accepted_faces, _ = totals[(omega, mu)]
            both = sum(sum((i, face) in accepted_faces for face in (0, 1)) == 2
                       for i in range(35))
            rows.append({
                "starting_spin": omega, "friction_coefficient": mu,
                "accepted_single_face_candidates": n,
                "cases_with_any_admissible_single_face": len(touched),
                "cases_with_two_admissible_single_faces": both,
                "cases_with_no_admissible_single_face": 35 - len(touched),
            })
    require(native.get("by_parameter") == rows,
            "original source by-parameter acceptance counts altered")
    require(accepted + rejected == 420 and frame_count == accepted * 31,
            "source candidate/frame roster incomplete")
    manifest = {
        "source_report_sha256": digest(native),
        "ordered_source_cases": [
            {"case": p["case"], "rotation": p["rotation"], "angle": p["angle"],
             "head_hash": p["receipt"]["head_hash"]}
            for p in pages
        ],
    }
    witness = {
        "valid": all(p["witness"]["valid"] for p in pages),
        "pages_verified": len(pages),
        "steps_verified": sum(p["witness"]["steps_verified"] for p in pages),
        "observations_recorded": sum(
            p["witness"]["observations_recorded"] for p in pages),
    }
    return {
        "schema": SCHEMA, "source_commit": source_commit,
        "source_report_sha256": digest(native),
        "cases": 35, "source_candidates": 420,
        "admissible_candidates": accepted, "rejected_candidates": rejected,
        "candidate_frames": frame_count, "by_parameter": rows,
        "physical_winner_selected": False,
        "original_frictional_multicontact_solved": False,
        "external_source_authenticated_by_adapter": False,
        "native_model_verified_by_adapter": False,
        "material_physics_verified": False,
        "ledger_pages": pages, "ledger_witness": witness,
        "page_manifest": manifest,
        "page_manifest_sha256": digest(manifest),
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
