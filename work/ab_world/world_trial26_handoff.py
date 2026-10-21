"""WORLD26 bounded, nominal between-sample clearance / unknown evidence.

No dynamics or geometry solver is embedded here: immutable native WORLD26
and its independent separating-axis/speed-envelope verifier own the model.
Neutral A/B keeps each original finite face and all unknown sub-grid
intervals in separately bounded, source-digest-linked ledgers.
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

SCHEMA = "ab-world-trial26-between-grid-uncertainty-handoff/v1"
SRC26 = "world-ab-between-sample-conditional-finite-clearance/v1"
SRC25 = "world-ab-finite-segment-rotating-square-intersection/v1"
PIN = "d9a735b1a5473c0f2646778996c89e70af0d28fd"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
FACES = ("original_finite_face","motion_derived_receiver")
START,END,INTERVALS,GUARD = .008,.25,2048,1e-7
CHUNK = 128
NO_SOURCE = "NO_ADMITTED_THIRD_IMPULSE"
COVERED = "ALL_FINITE_FACE_INTERVALS_NOMINALLY_SEPARATED"
SAMPLED = "SAMPLED_FINITE_INTERSECTION_WITH_UNRESOLVED_BETWEEN_FRAMES"
UNKNOWN = "SOME_BETWEEN_FRAME_INTERVALS_REMAIN_UNRESOLVED"


def require(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError("WORLD26 A/B: " + why)


def finite(x: Any) -> bool:
    return type(x) in (int, float) and isfinite(x)


def point(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(finite(z) for z in x)


def time_at(i: int) -> float:
    return round(START+(END-START)*i/INTERVALS,10)


def face_proof(record: dict, old: dict, face: str) -> int:
    require(type(record) is dict and type(old) is dict and
            record.get("face") == old.get("face") == face and
            record.get("segment") == old.get("segment") and
            type(record.get("segment")) is list and
            len(record["segment"]) == 2 and
            all(point(p) for p in record["segment"]),
            "original finite source segment changed")
    require(finite(record.get("velocity_norm_upper_bound")) and
            record["velocity_norm_upper_bound"] >= 0 and
            record.get("sampled_margins_count") == INTERVALS+1 and
            record.get("grid_intervals_checked") == INTERVALS and
            record.get("formal_outward_rounded_certificate") is False,
            "source velocity envelope, count or floating certificate changed")
    unknown = record.get("uncovered_intervals")
    n = record.get("uncovered_interval_count")
    covered = record.get("endpoint_margin_covered_intervals")
    require(type(unknown) is list and type(n) is int and
            type(covered) is int and n == len(unknown) and
            0 <= n <= INTERVALS and n+covered == INTERVALS and
            record.get("all_intervals_nominally_covered") is (n == 0),
            "uncovered/covered interval count silently changed")
    previous=-1
    for item in unknown:
        require(type(item) is dict and
                type(item.get("interval_index")) is int,
                "source uncertainty interval missing identity")
        idx=item["interval_index"]
        require(previous < idx < INTERVALS and idx >= 0 and
                item.get("start") == time_at(idx) and
                item.get("end") == time_at(idx+1) and
                finite(item.get("sample_start_separating_margin")) and
                finite(item.get("sample_end_separating_margin")) and
                finite(item.get("velocity_envelope_surplus")) and
                item.get("classification") == "NOT_CERTIFIED_BY_ENDPOINT_MARGIN",
                "original uncovered intervals reordered, omitted or promoted to collisions")
        previous=idx
    margin=record.get("minimum_covered_margin_surplus")
    require((margin is None) == (covered == 0) and
            (margin is None or finite(margin)),
            "nominal covered margin incorrectly claimed")
    return n


def carry(native26: dict[str,Any], native25: dict[str,Any],
          source_commit: str = PIN) -> dict[str,Any]:
    require(source_commit == PIN,"original source pin changed")
    require(type(native26) is dict and native26.get("schema") == SRC26 and
            native26.get("angles") == list(ANGLES) and
            native26.get("actual_hardware_measurements") == 0 and
            native26.get("fourth_impulses_selected") == 0 and
            native26.get("new_physical_receivers_constructed") == 0 and
            native26.get("new_physics_engine") is False and
            type(native25) is dict and native25.get("schema") == SRC25 and
            native25.get("angles") == list(ANGLES) and
            native25.get("fourth_impulses_solved") == 0,
            "original WORLD25/26 source scope or physical claims changed")
    cases= native26.get("cases")
    earlier=native25.get("cases")
    require(type(cases) is list and type(earlier) is list and
            len(cases) == len(earlier) == 8,"all eight original controls required")
    basis={"kind":"source-execution",
           "source":"pinned original WORLD25/26 @" + PIN}
    model={"kind":"declared",
           "source":"nominal SAT margins and square corner speed envelope, not measured"}
    summaries=[]
    chunks=[]
    admitted=refused=fully=with_unknown=unknown_total=0
    for i,angle in enumerate(ANGLES):
        case,prior=cases[i],earlier[i]
        require(type(case) is dict and type(prior) is dict and
                case.get("schema") == SRC26 and case.get("angle") == angle and
                prior.get("schema") == SRC25 and prior.get("angle") == angle and
                case.get("source_trial25_schema") == SRC25 and
                case.get("source_trial25_status") == prior.get("status") and
                case.get("source_trial25_intersecting_grid_samples") ==
                sum(q["intersecting_grid_samples"] for q in prior["face_results"]) and
                case.get("source_third_impulse") == prior.get("source_third_impulse") and
                case.get("source_receiver") == prior.get("source_receiver"),
                "Trial25 source ancestry or previous finite samples changed")
        for field,value in (
            ("observation_start",START),("observation_end",END),
            ("sample_intervals",INTERVALS),("nominal_velocity_margin_guard",GUARD),
            ("unchanged_existing_two_finite_faces",True),
            ("model_free_flight_hypothesis_only",True),
            ("physical_motion_witnessed",False),
            ("selected_fourth_impulse",False),
            ("new_receiver_constructed",False),
            ("certified_floating_point_interval_arithmetic",False),
            ("counterfactual_after_any_earlier_contact",True),
        ):
            require(case.get(field) == value,
                    "original model conditions or physical boundary lost: " + field)
        raw=case.get("face_clearance_bounds")
        source_on=case["source_third_impulse"] is not None
        require(type(raw) is list,"source face uncertainty results omitted")
        face_states=[]
        if not source_on:
            require(case.get("status") == NO_SOURCE and raw == [] and
                    prior.get("status") == NO_SOURCE and
                    case.get("fully_nominally_covered_faces") == 0 and
                    case.get("uncovered_total_intervals") == 0,
                    "no original third impulse acquired fake between-frame certificate")
            refused+=1
        else:
            admitted+=1
            require(type(case["source_third_impulse"]) is dict and
                    case["source_third_impulse"].get("materially_witnessed") is False and
                    type(prior.get("face_results")) is list and
                    len(prior["face_results"]) == len(raw) == 2,
                    "conditionally admitted model or original two finite faces missing")
            for j,(face,rec,old) in enumerate(zip(FACES,raw,prior["face_results"])):
                n=face_proof(rec,old,face)
                face_states.append({
                    "face":face, "segment":deepcopy(rec["segment"]),
                    "source25_grid_intersections":old["intersecting_grid_samples"],
                    "covered_intervals":rec["endpoint_margin_covered_intervals"],
                    "uncovered_intervals":n,
                    "all_nominally_covered":n==0,
                    "reported_speed_bound":rec["velocity_norm_upper_bound"],
                    "minimum_covered_margin_surplus":rec["minimum_covered_margin_surplus"],
                    "source26_full_face_sha256":digest(rec),
                    "outward_rounded_certificate":False,
                })
                unknown=rec["uncovered_intervals"]
                for start in range(0,len(unknown),CHUNK):
                    excerpt=deepcopy(unknown[start:start+CHUNK])
                    chunk_index=start//CHUNK
                    # A standalone bounded ledger; never a mutation of a case
                    # or face object belonging to a different plan.
                    steps=[
                        {"op":"introduce","id":"source-uncertain-interval-chunk",
                         "state":{"case_index":i,"face_index":j,"face":face,
                                  "chunk_index":chunk_index,
                                  "source_face_sha256":digest(rec),
                                  "source_case_sha256":digest(case),
                                  "covered_by_model":False,
                                  "hardware_collision_observed":False}, "basis":basis},
                        {"op":"observe","id":"native-unknown-intervals",
                         "entity":"object","subject":"source-uncertain-interval-chunk",
                         "reading":{"original_uncovered_intervals":excerpt,
                                    "reported_uncertainties":len(excerpt),
                                    "not_certified_not_a_collision":True,
                                    "further_contact_solved":False}, "basis":basis},
                    ]
                    receipt=run_plan({"schema":PLAN,
                        "referent":f"WORLD26 / source unknown {i}/{j}/{chunk_index}",
                        "limits":{"objects":1,"relations":1,"steps":len(steps)},
                        "steps":steps})
                    chunk_witness=verify_receipt(receipt)
                    chunks.append({
                        "case":i,"face":face,"face_index":j,
                        "chunk":chunk_index,"source_start":start,"count":len(excerpt),
                        "original_interval_sha256":digest(excerpt),
                        "receipt":receipt,"witness":chunk_witness,
                    })
            count=sum(x["uncovered_intervals"] for x in face_states)
            covered=sum(x["all_nominally_covered"] for x in face_states)
            require(case.get("fully_nominally_covered_faces") == covered and
                    case.get("uncovered_total_intervals") == count,
                    "native whole-face certainty and unknown totals changed")
            expected=(COVERED if covered==2 else SAMPLED
                      if prior.get("faces_with_sampled_intersection",0)>0 else UNKNOWN)
            require(case.get("status") == expected,
                    "uncovered interval promoted to actual impact or physical clearance")
            fully+=int(covered==2)
            with_unknown+=int(count>0)
            unknown_total+=count
        steps=[
            {"op":"introduce","id":"conditional-square",
             "state":{"source_angle":angle,
                      "third_impulse_model":deepcopy(case["source_third_impulse"]),
                      "actual_third_contact_measured":False,
                      "actual_fourth_impulse":None}, "basis":basis},
            {"op":"introduce","id":"bounded-nominal-margin-investigation",
             "state":{"original_world":[24.,6.],
                      "sample_interval":[START,END],
                      "intervals_per_face":INTERVALS,"guard":GUARD,
                      "model_only":True,
                      "outward_rounded_proof":False}, "basis":model},
            {"op":"connect","id":"source-conditional-margin-study",
             "from":"conditional-square","to":"bounded-nominal-margin-investigation",
             "label":"nominal-face-by-face-between-frame-check",
             "state":{"source_third_impulse_admitted":source_on}, "basis":model},
            {"op":"observe","id":"original-source25-grid-comparison",
             "entity":"object","subject":"bounded-nominal-margin-investigation",
             "reading":{"source25_sha256":digest(prior),
                        "source25_grid_intersecting_samples":
                            case["source_trial25_intersecting_grid_samples"],
                        "sampling_is_not_continuous_clearance":True},
             "basis":basis},
        ]
        for j,state in enumerate(face_states):
            face_id=f"source-finite-face-{j}"
            steps.extend([
                {"op":"introduce","id":face_id,"state":deepcopy(state),"basis":basis},
                {"op":"connect","id":f"nominal-margin-study-{j}",
                 "from":face_id,"to":"conditional-square",
                 "label":"existing-finite-face-speed-envelope",
                 "state":{"conditional_model_only":True,
                          "actual_contact_selected":False},"basis":model},
                {"op":"observe","id":f"native-face-bounds-{j}",
                 "entity":"object","subject":face_id,
                 "reading":{"source26_face_sha256":state["source26_full_face_sha256"],
                            "unknown_interval_count":state["uncovered_intervals"],
                            "source_uncertainty_batches":
                                (state["uncovered_intervals"]+CHUNK-1)//CHUNK,
                            "outward_rounded_certificate":False,
                            "material_contact_observed":False},"basis":basis},
            ])
        steps.extend([
            {"op":"observe","id":"source-interval-bound-verdict",
             "entity":"object","subject":"bounded-nominal-margin-investigation",
             "reading":{"source26_sha256":digest(case),"source_status":case["status"],
                        "uncovered_total_intervals":case["uncovered_total_intervals"],
                        "fully_nominally_covered_faces":
                            case["fully_nominally_covered_faces"],
                        "unknown_does_not_mean_collision":True,
                        "continuous_material_clearance_proven":False},
             "basis":basis},
            {"op":"observe","id":"source-coverage-contrast",
             "entity":"object","subject":"conditional-square",
             "reading":{"source_third_impulse_admitted":source_on,
                        "uncovered_intervals_found":
                            case["uncovered_total_intervals"]>0,
                        "material_contact_witnessed":False},"basis":basis},
            {"op":"compare","id":"no-source-uncovered-interval-hypothesis",
             "observation":"source-coverage-contrast",
             "expected":{"source_third_impulse_admitted":source_on,
                         "uncovered_intervals_found":False,
                         "material_contact_witnessed":False}, "basis":model},
        ])
        receipt=run_plan({"schema":PLAN,
             "referent":f"WORLD26 / finite between-grid source angle {angle}",
             "limits":{"objects":4,"relations":3,"steps":len(steps)},
             "steps":steps})
        witness=verify_receipt(receipt)
        require(witness["valid"] and
                receipt["final"]["comparisons"]
                ["no-source-uncovered-interval-hypothesis"]["result"] ==
                ("DIFFERENT" if case["uncovered_total_intervals"]>0 else "MATCH"),
                "independent finite uncertainty contrast changed")
        summaries.append({"case":i,"angle":angle,"source_on":source_on,
                          "native_status":case["status"],
                          "receipt":receipt,"witness":witness})
    require(native26.get("conditional_third_impulse_cases") == admitted == 6 and
            native26.get("no_source_third_impulse_controls") == refused == 2 and
            native26.get("cases_with_both_faces_nominally_covered") == fully and
            native26.get("cases_with_unresolved_intervals") == with_unknown and
            native26.get("total_uncovered_face_intervals") == unknown_total,
            "source-native nominal margin aggregate changed")
    manifest={"source26_sha256":digest(native26),
              "source25_sha256":digest(native25),"source_commit":PIN,
              "case_heads":[{"case":p["case"],"head_hash":p["receipt"]["head_hash"]}
                            for p in summaries],
              "uncertainty_heads":[{"case":p["case"],"face":p["face"],
                                    "chunk":p["chunk"],"count":p["count"],
                                    "source_interval_digest":p["original_interval_sha256"],
                                    "head_hash":p["receipt"]["head_hash"]}
                                   for p in chunks]}
    pages=summaries+chunks
    return {"schema":SCHEMA,"source_commit":PIN,
            "original_cases":8,"source_conditional_cases":admitted,
            "source_absent_controls":refused,
            "nominally_covered_both_faces_cases":fully,
            "cases_with_unknown_intervals":with_unknown,
            "uncovered_source_intervals":unknown_total,
            "uncertainty_chunk_size":CHUNK,"uncertainty_chunks":len(chunks),
            "fourth_impulses_selected":0,"actual_physical_impacts":0,
            "continuous_material_clearance_proven":False,
            "formal_outward_interval_proof":False,
            "ledger_summaries":summaries,"ledger_uncertainty_chunks":chunks,
            "ledger_witness":{"valid":all(p["witness"]["valid"] for p in pages),
                              "pages_verified":len(pages),
                              "steps_verified":sum(p["witness"]["steps_verified"] for p in pages),
                              "observations_recorded":sum(
                                  p["witness"]["observations_recorded"] for p in pages)},
            "manifest":manifest,"manifest_sha256":digest(manifest)}


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--source25",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(carry(load_json(a.native),load_json(a.source25)),
                     sort_keys=True,indent=2))


if __name__=="__main__":
    main()
