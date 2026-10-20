"""Trial13: carry rejected and surviving coupled-contact *hypotheses*.

The original native generator and independent Jacobian/geometry verifier own
contact-model admissibility. The general A/B ledger stores source relationships
and finite reported movements, but never chooses actual material impulses.
Each of the 35 predeclared cases is a separately bounded A/B plan.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from math import isfinite
from pathlib import Path
import re
from itertools import product
from typing import Any

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

SCHEMA = "ab-world-trial13-coupled-mode-handoff/v1"
NATIVE = "world-ab-coupled-two-contact-friction-modes/v1"
ANGLES = (-15, -5, 0, 10, 20, 30, 45)
ROTATIONS = (-15., -7.5, 0., 7.5, 15.)
FRICTIONS = (0., .2, .4)
SPINS = (0., 2.)
MODES = ("stick", "slip-positive", "slip-negative")
ACCEPTED = "admissible-coupled-mode"


def require(ok: bool, explanation: str) -> None:
    if not ok:
        raise ValueError("Trial13 A/B handoff: " + explanation)


def number(v: Any) -> bool:
    return type(v) in (int, float) and isfinite(v)


def pair(v: Any) -> bool:
    return type(v) is list and len(v) == 2 and all(number(x) for x in v)


def carry(native: dict[str, Any], source_commit: str) -> dict[str, Any]:
    require(type(source_commit) is str and
            re.fullmatch(r"[a-f0-9]{40}", source_commit) is not None,
            "exact original commit required")
    require(type(native) is dict and native.get("schema") == NATIVE and
            native.get("source_trial09_schema") ==
            "world-ab-two-contact-incidence-stress/v1",
            "original coupled source lineage changed")
    require(native.get("angle_grid") == list(ANGLES) and
            native.get("rotation_grid") == list(ROTATIONS) and
            native.get("friction_grid") == list(FRICTIONS) and
            native.get("starting_spin_grid") == list(SPINS) and
            native.get("hypotheses") == list(MODES),
            "predeclared coupled mode grid changed")
    require(number(native.get("disc_radius")) and
            native["disc_radius"] > 0 and
            number(native.get("disc_inertia")) and
            native["disc_inertia"] > 0 and
            native.get("normal_restitution") == 1. and
            native.get("original_trial06_friction") == .4,
            "source model parameters changed")
    require(native.get("source_original_trial06_simultaneous_stop_preserved") is True,
            "original simultaneous stop overwritten")
    for flag in (
        "general_simultaneous_friction_manifold_solved",
        "actual_joint_contact_impulses_measured",
        "physical_material_law_verified", "real_blueprint_generated",
    ):
        require(native.get(flag) is False, "unsupported physical claim: " + flag)
    geom = native.get("original_source_geometry")
    require(type(geom) is dict and type(geom.get("surfaces")) is list and
            len(geom["surfaces"]) == 2,
            "original source faces missing")
    original_ids = [f.get("id") if type(f) is dict else None
                    for f in geom["surfaces"]]
    require(all(type(v) is str and v.strip() for v in original_ids)
            and original_ids[0] != original_ids[1],
            "original source identity invalid")
    scenarios = native.get("scenarios")
    require(type(scenarios) is list and len(scenarios) == 35,
            "35 declared source cases required")

    basis = {"kind": "source-execution",
             "source": "native WORLD Trial13 @" + source_commit}
    model = {"kind": "declared",
             "source": "conditional frictional coupled-mode Jacobian hypotheses"}
    pages = []
    total = 0
    admitted = 0
    rejected = 0
    frames_carried = 0
    counts = {(omega, mu): {"accepted": 0, "one": 0, "multiple": 0, "none": 0}
              for omega in SPINS for mu in FRICTIONS}
    for index, (rotation, angle) in enumerate(
            (d, a) for d in ROTATIONS for a in ANGLES):
        case = scenarios[index]
        require(type(case) is dict and
                case.get("original_index") == index and
                case.get("incoming_angle_degrees") == angle and
                case.get("surface_B_rotation_degrees") == rotation,
                "original source case order substituted")
        geometry_kind = ("original-source-geometry" if rotation == 0
                         else "controlled-geometry-not-original")
        ids = case.get("source_ids")
        require(case.get("geometry_kind") == geometry_kind and
                type(ids) is list and len(ids) == 2 and
                (ids == original_ids if rotation == 0 else
                 ids[0] == original_ids[0] and ids[1] != original_ids[1]),
                "synthetic geometry presented as original")
        require(case.get("trial09_two_active_status") in (
            "accepted-local-candidate", "rejected-unilateral",
            "rejected-not-incoming", "rejected-constraint"),
            "original two-active source decision missing")
        require(case.get("material_behavior_observed") is False,
                "unsupported real collision observation")
        groups = case.get("groups")
        require(type(groups) is list and len(groups) == 6,
                "six source parameter groups required")
        steps = [
            {"op": "introduce", "id": "original-mu04-contact",
             "state": {"source_case": index, "status": "unresolved-multiple-contacts",
                       "measured_joint_impulse": None}, "basis": basis},
            {"op": "introduce", "id": "conditional-coupled-model",
             "state": {"two-contact_contact_law": "hypothetical",
                       "original_not_solved": True, "real_winner": None},
             "basis": model},
            {"op": "connect", "id": "model-not-observation",
             "from": "original-mu04-contact", "to": "conditional-coupled-model",
             "label": "unobserved-mode-enumeration",
             "state": {"physical_result_selected": False}, "basis": model},
            {"op": "introduce", "id": "source-geometry-case",
             "state": {"angle": angle, "rotation": rotation,
                       "source_ids": deepcopy(ids), "geometry_kind": geometry_kind,
                       "trial09_two_active_status":
                           case["trial09_two_active_status"]},
             "basis": basis},
            {"op": "connect", "id": "model-case-link",
             "from": "conditional-coupled-model", "to": "source-geometry-case",
             "label": "finite-original-case", "state": {"source_index": index},
             "basis": basis},
        ]
        for group_index, (omega, mu) in enumerate(
                (w, m) for w in SPINS for m in FRICTIONS):
            group = groups[group_index]
            require(type(group) is dict and
                    group.get("starting_spin") == omega and
                    group.get("friction") == mu and
                    group.get("physical_outcome_selected") is False,
                    "source coupled-mode parameter or evidence claim changed")
            alternatives = group.get("options")
            modes = ([("frictionless", "frictionless")] if mu == 0.
                     else list(product(MODES, repeat=2)))
            require(type(alternatives) is list and
                    len(alternatives) == len(modes),
                    "original mode enumeration incomplete")
            matching = sum(a.get("status") == ACCEPTED for a in alternatives
                           if type(a) is dict)
            cls = "none" if not matching else "multiple" if matching > 1 else "one"
            require(type(group.get("admissible_count")) is int and
                    group["admissible_count"] == matching and
                    group.get("classification") == cls,
                    "source hypothesis alternatives silently collapsed")
            if mu == 0. and omega == 0.:
                require((matching > 0) ==
                        (case["trial09_two_active_status"] == "accepted-local-candidate"),
                        "original frictionless Trial09 comparison overwritten")
            row = counts[(omega, mu)]
            row["accepted"] += matching
            row[cls] += 1
            gid = f"source-param-{group_index}"
            steps.extend([
                {"op": "introduce", "id": gid,
                 "state": {"starting_spin": omega, "friction": mu,
                           "admissible_count": matching, "classification": cls,
                           "material_response_selected": False},
                 "basis": basis},
                {"op": "connect", "id": f"group-link-{group_index}",
                 "from": "source-geometry-case", "to": gid,
                 "label": "source-parametrized-coupled-model",
                 "state": {"parameter_index": group_index}, "basis": model},
            ])
            for option_index, expected_mode in enumerate(modes):
                option = alternatives[option_index]
                require(type(option) is dict and
                        option.get("mode") == list(expected_mode) and
                        option.get("friction") == mu and
                        option.get("incoming_spin") == omega and
                        option.get("source_ids") == ids,
                        "source coupled mode identity changed")
                status = option.get("status")
                require(type(status) is str and
                        (status == ACCEPTED or status.startswith("rejected-")),
                        "unsupported source outcome")
                key = f"group-{group_index}-mode-{option_index:02d}"
                accepted_candidate = status == ACCEPTED
                frames = option.get("frames")
                initial = {
                    "group": group_index, "mode_index": option_index,
                    "mode": list(expected_mode), "model_only": True,
                    "status": status, "full_source_path": accepted_candidate,
                }
                steps.extend([
                    {"op": "introduce", "id": key, "state": deepcopy(initial),
                     "basis": basis},
                    {"op": "connect", "id": f"hypothesis-{group_index}-{option_index:02d}",
                     "from": gid, "to": key, "label": "tested-not-selected",
                     "state": {"original_contact_unchanged": True}, "basis": model},
                ])
                total += 1
                if accepted_candidate:
                    require(option.get("reason") is None and
                            option.get("continuous_clearance_verified") is True and
                            type(option.get("impulses")) is list and
                            len(option["impulses"]) == 4 and
                            all(number(v) for v in option["impulses"]) and
                            pair(option.get("outgoing_velocity")) and
                            number(option.get("outgoing_spin")) and
                            type(frames) is list and len(frames) == 31,
                            "admissible coupled mode lacks checked complete source movement")
                    admitted += 1
                    frames_carried += len(frames)
                    for clock_index, frame in enumerate(frames):
                        require(type(frame) is dict and
                                number(frame.get("time")) and
                                abs(frame["time"] - clock_index * .05) <= 2e-8 and
                                pair(frame.get("position")) and
                                pair(frame.get("velocity")) and
                                number(frame.get("spin")) and
                                number(frame.get("orientation")),
                                "original coupled spin-motion frame corrupted")
                        steps.append({
                            "op": "revise", "entity": "object", "id": key,
                            "after": {**initial, "source_frame": deepcopy(frame)},
                            "basis": basis,
                        })
                else:
                    require(type(option.get("reason")) is str and
                            status == "rejected-" + option["reason"] and
                            option.get("outgoing_velocity") is None and
                            option.get("outgoing_spin") is None and
                            option.get("continuous_clearance_verified") is False and
                            frames == [],
                            "rejected coupled mode acquired invented motion")
                    rejected += 1
                reported = deepcopy(option)
                del reported["frames"]
                steps.append({
                    "op": "observe", "id": f"source-outcome-{group_index}-{option_index:02d}",
                    "entity": "object", "subject": key,
                    "reading": {"source_candidate": reported,
                                "frames_sha256": digest(frames),
                                "frames_count": len(frames),
                                "physical_material_observation": False},
                    "basis": basis,
                })
        plan = {
            "schema": PLAN,
            "referent": f"WORLD Trial13 / source coupled modes case {index:02d}",
            "limits": {"objects": 2 + 1 + 6 + 38,
                       "relations": 1 + 1 + 6 + 38,
                       "steps": len(steps)},
            "steps": steps,
        }
        receipt = run_plan(plan)
        pages.append({"case": index, "rotation": rotation, "angle": angle,
                      "receipt": receipt, "witness": verify_receipt(receipt)})
    rows = []
    for omega in SPINS:
        for mu in FRICTIONS:
            c = counts[(omega, mu)]
            rows.append({"starting_spin": omega, "friction": mu,
                         "admissible_modes": c["accepted"],
                         "cases_with_one_mode": c["one"],
                         "cases_with_multiple_modes": c["multiple"],
                         "cases_with_no_mode": c["none"]})
    require(native.get("aggregate") == rows,
            "source coupled-mode outcome counts changed")
    require(total == 1330 and admitted + rejected == total and
            frames_carried == admitted * 31,
            "source mode roster or frames incomplete")
    manifest = {
        "source_report_sha256": digest(native),
        "ordered_source_cases": [
            {"case": p["case"], "rotation": p["rotation"], "angle": p["angle"],
             "head_hash": p["receipt"]["head_hash"]} for p in pages
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
        "source_cases": 35, "mode_attempts": total,
        "admissible_modes": admitted, "rejected_modes": rejected,
        "conditional_motion_frames": frames_carried,
        "aggregate": rows, "original_material_contact_solved": False,
        "actual_joint_contact_impulses_measured": False,
        "native_model_verified_by_adapter": False,
        "external_source_authenticated_by_adapter": False,
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
