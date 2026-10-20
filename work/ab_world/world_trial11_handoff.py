"""WORLD Trial11 -> A/B: counterfactual sensor discrimination, never measured.

A source-specific adapter to the neutral bounded construction ledger.
The native WORLD source and independent oracle remain responsible for
hypothetical partitions and friction constraints; these are not instruments.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any

from work.ab_world.construction import PLAN, digest, load_json, run_plan
from work.ab_world.verify_construction import verify_receipt

SCHEMA = "ab-world-trial11-counterfactual-evidence-handoff/v1"
NATIVE = "world-ab-contact-discrimination-hypotheses/v1"
ANGLES = (-15, -5, 0, 10, 20, 30, 45)
ROTATIONS = (-15.0, -7.5, 0.0, 7.5, 15.0)
TIMES = (0.40, 0.60, 1.10)
QUANTA = (0.1, 0.01, 0.001)
COUNT_KEYS = (
    "ambiguous_cases", "friction_cone_only_narrowed_cases",
    "all_normals_rest_narrowed_cases", "all_normals_rest_eliminated_cases",
    "ambiguous_cases_with_hypothetical_distinguishing_sensor",
    "ambiguous_cases_not_distinguished_at_tested_sensor_settings",
)


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("WORLD Trial11 handoff: " + reason)


def carry(native: dict[str, Any], source_commit: str) -> dict[str, Any]:
    require(type(source_commit) is str and
            re.fullmatch(r"[a-f0-9]{40}", source_commit) is not None,
            "exact pinned source commit required")
    require(type(native) is dict and native.get("schema") == NATIVE,
            "wrong native Trial11 schema")
    require(native.get("source_trial10_schema") ==
            "world-ab-two-contact-active-set-enumeration/v1" and
            native.get("source_trial09_schema") ==
            "world-ab-two-contact-incidence-stress/v1",
            "original source ancestry missing")
    require(native.get("sensor_times") == list(TIMES) and
            native.get("sensor_position_quanta") == list(QUANTA),
            "predeclared hypothetical sampling grid changed")
    require(native.get("friction_coefficient_hypothesis") == 0.4,
            "original declared Coulomb parameter changed")
    for flag in (
        "friction_cone_check_is_necessary_not_sufficient",
        "all_normals_restitution_is_extra_unobserved_postulate",
        "all_sensor_readings_are_counterfactual",
    ):
        require(native.get(flag) is True, "evidence boundary lost: " + flag)
    for flag in (
        "source_physical_outgoing_velocities_measured",
        "original_trial06_mu_point_four_solver_resolved",
        "actual_outcome_selected",
        "external_physical_blueprint_constructed",
    ):
        require(native.get(flag) is False, "unsupported physical claim: " + flag)
    counts10 = native.get("source_trial10_counts")
    require(type(counts10) is dict and
            counts10.get("multiple-admissible") == 26 and
            counts10.get("single-admissible") == 9 and
            counts10.get("no-local-candidate") == 0,
            "original Trial10 classification changed")
    cases = native.get("cases")
    require(type(cases) is list and len(cases) == 35,
            "missing one of 35 original source cases")
    totals = {key: 0 for key in COUNT_KEYS}
    pages = []
    source = {"kind": "source-execution",
              "source": "native WORLD Trial11 source @" + source_commit}
    hypothetical = {"kind": "declared",
                    "source": "source-proposed sensor readings; no physical sample"}
    for group, rotation in enumerate(ROTATIONS):
        steps = [
            {"op": "introduce", "id": "original-mu04-contact",
             "state": {"status": "unresolved-multiple-contacts",
                       "observed_outgoing_impulse": None,
                       "coefficient_of_friction": 0.4}, "basis": source},
            {"op": "introduce", "id": "candidate-reading-model",
             "state": {"friction_cone_is_necessary_not_sufficient": True,
                       "extra_restitution_is_unobserved": True,
                       "measurements_available": False,
                       "outcome_selected": False}, "basis": hypothetical},
            {"op": "connect", "id": "counterfactual-not-physical-measurement",
             "from": "original-mu04-contact", "to": "candidate-reading-model",
             "label": "proposed-observations-not-actual-readings",
             "state": {"measured_reading": None}, "basis": hypothetical},
        ]
        for local_index, angle in enumerate(ANGLES):
            index = group * len(ANGLES) + local_index
            case = cases[index]
            require(type(case) is dict and
                    case.get("original_index") == index and
                    case.get("incoming_angle_degrees") == angle and
                    case.get("surface_B_rotation_degrees") == rotation,
                    "source case identity or order changed")
            expected_kind = ("original-source-geometry" if rotation == 0
                             else "controlled-geometry-not-original")
            require(case.get("geometry_kind") == expected_kind,
                    "controlled geometry represented as original")
            cls = case.get("source_trial10_classification")
            live = case.get("original_admissible_count")
            require(type(live) is int and 1 <= live <= 3 and
                    cls == ("multiple-admissible" if live > 1
                            else "single-admissible"),
                    "original competing alternatives silently collapsed")
            require(case.get("actual_source_sensor_reading_available") is False and
                    case.get("physical_outcome_selected") is False,
                    "hypothetical reading promoted into physical observation")
            audits = case.get("candidates")
            require(type(audits) is list and len(audits) == live,
                    "original candidate list omitted")
            unique_active = set()
            cone = 0
            restitution = 0
            for audit in audits:
                require(type(audit) is dict and
                        type(audit.get("active_indices")) is list and
                        tuple(audit["active_indices"]) in ((0,), (1,), (0, 1)) and
                        type(audit.get("source_ids")) is list and
                        len(audit["source_ids"]) == len(audit["active_indices"]),
                        "native candidate active-set attribution changed")
                key = tuple(audit["active_indices"])
                require(key not in unique_active, "same active set recorded twice")
                unique_active.add(key)
                require(audit.get("has_actual_outgoing_motion_measurement") is False,
                        "source virtual velocity falsely called measured")
                require(audit.get("necessary_mu_point_four_cone") is True and
                        audit.get("tangent_impulses_under_original_mu_zero_model") ==
                        [0.0] * len(key),
                        "necessary friction cone claimed as frictional law")
                require(type(audit.get("mu_point_four_normal_cone_bounds")) is list and
                        len(audit["mu_point_four_normal_cone_bounds"]) == len(key),
                        "source model normal bounds omitted")
                require(type(audit.get("hypothesis_both_touching_normals_restitute")) is bool,
                        "extra unmeasured restitution not labeled")
                cone += 1
                restitution += int(audit["hypothesis_both_touching_normals_restitute"])
            require(case.get("necessary_friction_cone_retained_count") == cone and
                    case.get("additional_all_normals_restitution_retained_count") ==
                    restitution,
                    "source candidate filtering counts altered")
            caseid = f"source-case-{index:02d}"
            steps.extend([
                {"op": "introduce", "id": caseid,
                 "state": {"source_index": index, "angle": angle,
                           "rotation": rotation, "geometry_kind": expected_kind,
                           "original_candidate_count": live,
                           "no_physical_outcome_selected": True}, "basis": source},
                {"op": "connect", "id": f"hypothesis-for-{index:02d}",
                 "from": "candidate-reading-model", "to": caseid,
                 "label": "unmeasured-source-candidate-comparison",
                 "state": {"candidate_count": live}, "basis": hypothetical},
                {"op": "observe", "id": f"source-audits-{index:02d}",
                 "entity": "object", "subject": caseid,
                 "reading": {"reported_model_audits": deepcopy(audits),
                             "necessary_cone_retained": cone,
                             "extra_unobserved_restitution_retained": restitution,
                             "real_contact_observed": False}, "basis": source},
            ])
            sensors = case.get("sensors")
            require(type(sensors) is list and len(sensors) == len(TIMES) * len(QUANTA),
                    "missing one of the nine hypothetical settings")
            first = None
            for sensor_index, (time, quantum) in enumerate(
                    (t, q) for t in TIMES for q in QUANTA):
                sensor = sensors[sensor_index]
                require(type(sensor) is dict and
                        sensor.get("virtual_time") == time and
                        sensor.get("position_quantum") == quantum,
                        "hypothetical sampling time or precision substituted")
                require(sensor.get("measured_reading") is None,
                        "hypothetical sensor substituted with measured reading")
                parts = sensor.get("hypothetical_reading_partitions")
                require(type(parts) is list and 1 <= len(parts) <= live and
                        all(type(p) is dict and
                            type(p.get("bin_xy")) is list and
                            len(p["bin_xy"]) == 2 and
                            all(type(v) is int for v in p["bin_xy"]) and
                            type(p.get("possible_active_sets")) is list
                            for p in parts),
                        "source quantized partitions missing")
                actual_unique = len(parts) == live
                require(sensor.get("distinguishable_bins") == len(parts) and
                        sensor.get("would_uniquely_discriminate_if_a_matching_reading_were_observed")
                        is actual_unique,
                        "counterfactual discriminating claim changed")
                if live > 1 and actual_unique and first is None:
                    first = {"virtual_time": time, "position_quantum": quantum}
                sensorid = f"hypothetical-{index:02d}-{sensor_index}"
                steps.extend([
                    {"op": "introduce", "id": sensorid,
                     "state": {"virtual_time": time, "position_quantum": quantum,
                               "measured_reading": None,
                               "partitions": deepcopy(parts),
                               "would_distinguish_if_observed": actual_unique},
                     "basis": hypothetical},
                    {"op": "connect", "id": f"possible-reading-{index:02d}-{sensor_index}",
                     "from": caseid, "to": sensorid,
                     "label": "hypothetical-position-bin-not-observation",
                     "state": {"actual_reading_available": False}, "basis": hypothetical},
                    {"op": "observe", "id": f"source-reported-grid-{index:02d}-{sensor_index}",
                     "entity": "object", "subject": sensorid,
                     "reading": {"source_reported_hypothetical_sensor": deepcopy(sensor),
                                 "real_measurement_present": False},
                     "basis": source},
                ])
            require(case.get("first_hypothetical_discriminating_sensor") == first,
                    "first proposed discriminating setting changed")
            totals["ambiguous_cases"] += int(live > 1)
            totals["friction_cone_only_narrowed_cases"] += int(cone < live)
            totals["all_normals_rest_narrowed_cases"] += int(restitution < live)
            totals["all_normals_rest_eliminated_cases"] += int(restitution == 0)
            totals["ambiguous_cases_with_hypothetical_distinguishing_sensor"] += int(
                live > 1 and first is not None)
            totals["ambiguous_cases_not_distinguished_at_tested_sensor_settings"] += int(
                live > 1 and first is None)
        plan = {
            "schema": PLAN,
            "referent": f"WORLD Trial11 / hypothetical readings rotation {rotation}",
            "limits": {"objects": 2 + len(ANGLES) * (1 + 9),
                       "relations": 1 + len(ANGLES) * (1 + 9),
                       "steps": len(steps)},
            "steps": steps,
        }
        receipt = run_plan(plan)
        pages.append({"rotation": rotation, "first_case": group * 7,
                      "last_case": group * 7 + 6,
                      "receipt": receipt, "witness": verify_receipt(receipt)})
    require(native.get("counts") == totals, "original source count summary changed")
    require(totals["ambiguous_cases"] == 26 and
            totals["friction_cone_only_narrowed_cases"] == 0,
            "unsupported source cone interpretation")
    manifest = {
        "source_report_sha256": digest(native),
        "ordered_rotation_pages": [
            {"rotation": p["rotation"], "first_case": p["first_case"],
             "last_case": p["last_case"],
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
        "case_count": len(cases),
        "hypothetical_sensor_settings": 35 * 9,
        "source_counts": totals,
        "physical_sensor_measurements": 0,
        "physical_contact_selected": False,
        "frictional_solver_proven": False,
        "source_physics_verified_by_adapter": False,
        "external_source_authenticated_by_adapter": False,
        "ledger_pages": pages, "ledger_witness": witness,
        "page_manifest": manifest, "page_manifest_sha256": digest(manifest),
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
