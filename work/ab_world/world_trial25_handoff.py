"""WORLD25: source-owned finite-segment / full rotating-square overlap evidence.

The original WORLD25 Liang–Barsky model and the independently implemented
separating-axis verifier own the geometry. Neutral A/B only keeps source
reports, their Trial23/24 ancestry, finite grid windows and contradictions.
No fourth impact, exact collision-time certificate or material measurement.
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

SCHEMA = "ab-world-trial25-full-finite-overlap-handoff/v1"
SOURCE = "world-ab-finite-segment-rotating-square-intersection/v1"
SRC23 = "world-ab-all-inward-roots-finite-feature-audit/v1"
SRC24 = "world-ab-finite-face-endpoint-rotating-square-edge/v1"
PIN = "c4190eff7d0147b53620322c1900fdb7dfc6b9c3"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
FACES = ("original_finite_face", "motion_derived_receiver")
START, END, INTERVALS = .008, .25, 2048
KIND = "FINITE_SOURCE_SEGMENT_SQUARE_INTERSECTION_CANDIDATE"
NO_SOURCE = "NO_ADMITTED_THIRD_IMPULSE"
BRACKET = "FINITE_MODEL_INTERSECTION_TRANSITION_BRACKET_DETECTED"
START_OVERLAP = "PREEXISTING_FINITE_INTERSECTION_AT_WINDOW_START_UNRESOLVED"
NONE = "NO_FINITE_INTERSECTION_DETECTED_ON_GRID_ONLY"


def demand(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError("WORLD25 A/B: " + msg)


def number(x: Any) -> bool:
    return type(x) in (int, float) and isfinite(x)


def pair(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(number(v) for v in x)


def grid_time(i: int) -> float:
    return round(START + (END - START)*i/INTERVALS, 10)


def validate_face(rec: dict[str, Any], face: str) -> list[dict[str, Any]]:
    demand(type(rec) is dict and rec.get("face") == face and
           type(rec.get("segment")) is list and len(rec["segment"]) == 2 and
           all(pair(p) for p in rec["segment"]) and
           rec.get("samples_checked") == INTERVALS + 1 and
           rec.get("continuous_absence_certified") is False and
           type(rec.get("start_intersected")) is bool,
           "finite source face or bounded-sample identity changed")
    count = rec.get("intersecting_grid_samples")
    demand(type(count) is int and 0 <= count <= INTERVALS + 1,
           "sampled finite intersection count changed")
    windows = rec.get("sampled_intersection_windows")
    demand(type(windows) is list, "finite overlap intervals omitted")
    seen = 0
    previous_last = -2
    for window in windows:
        demand(type(window) is dict and
               type(window.get("first_sample_index")) is int and
               type(window.get("last_sample_index")) is int,
               "finite grid window indices omitted")
        a, b = window["first_sample_index"], window["last_sample_index"]
        demand(0 <= a <= b <= INTERVALS and a > previous_last + 1 and
               window.get("first_sample_time") == grid_time(a) and
               window.get("last_sample_time") == grid_time(b),
               "finite overlap windows: grid order, timing or separation changed")
        previous_last = b
        seen += b-a+1
    demand(seen == count and
           rec.get("start_intersected") is
           (bool(windows) and windows[0]["first_sample_index"] == 0),
           "overlap windows do not agree with sample tally or starting state")
    first = rec.get("first_grid_intersection_at")
    demand(first == (windows[0]["first_sample_time"] if windows else None),
           "first sampled intersection time changed")
    bracket = rec.get("first_transition_bracket")
    if windows and windows[0]["first_sample_index"] > 0:
        i = windows[0]["first_sample_index"]
        demand(type(bracket) is dict and
               bracket.get("last_grid_separated_at") == grid_time(i-1) and
               bracket.get("first_grid_intersection_at") == grid_time(i) and
               number(bracket.get("bisected_transition_time")) and
               grid_time(i-1)-1e-8 <= bracket["bisected_transition_time"] <=
               grid_time(i)+1e-8 and
               number(bracket.get("source_finite_clip_entry_fraction")) and
               number(bracket.get("source_finite_clip_exit_fraction")) and
               bracket.get("numerical_transition_not_exact_certified") is True,
               "finite sampled transition bracket is forged")
    else:
        demand(bracket is None, "bracket invented on already-overlapping or clear source")
    return windows


def expected_comparison(first: dict[str, Any] | None,
                        ancestry23: dict[str, Any]) -> dict[str, Any] | None:
    if first is None:
        return None
    face = first["face"]
    b = first["bracket"]
    roots = ancestry23["eligible_geometry_roots"]
    eligible = [x["dt_after_third_impulse"] for x in roots
                if type(x) is dict and x.get("surface") == face and
                x.get("feature_classification") == "FINITE_FACE_INTERIOR_CANDIDATE"
                and number(x.get("dt_after_third_impulse"))]
    old = min(eligible) if eligible else None
    lo, hi = b["last_grid_separated_at"], b["first_grid_intersection_at"]
    relation = ("NO_PRIOR_VERTEX_CANDIDATE_ON_THIS_FINITE_FACE" if old is None
                else "SOURCE_VERTEX_TIME_INSIDE_FIRST_GRID_BRACKET"
                if lo-3e-7 <= old <= hi+3e-7
                else "SOURCE_VERTEX_TIME_BEFORE_FIRST_GRID_BRACKET"
                if old < lo else "SOURCE_VERTEX_TIME_AFTER_FIRST_GRID_BRACKET")
    return {"face": face, "source_first_finite_vertex_time": old,
            "first_grid_clear_time": lo, "first_grid_overlap_time": hi,
            "relationship": relation, "same_face_only": True,
            "numerical_grid_not_certified_first_contact": True}


def carry(native: dict[str, Any], original23: dict[str, Any],
          original24: dict[str, Any], source_commit: str = PIN) -> dict[str, Any]:
    demand(source_commit == PIN, "original source commit changed")
    demand(type(native) is dict and native.get("schema") == SOURCE and
           native.get("angles") == list(ANGLES) and
           native.get("fourth_impulses_solved") == 0 and
           native.get("material_observations") == 0 and
           native.get("physical_receivers_constructed") == 0 and
           native.get("new_engine_or_world") is False,
           "original WORLD25 source identity or physical boundary changed")
    demand(type(original23) is dict and original23.get("schema") == SRC23 and
           original23.get("angles") == list(ANGLES) and
           original23.get("fourth_impulses_selected") == 0 and
           original23.get("physical_measurements") == 0 and
           type(original24) is dict and original24.get("schema") == SRC24 and
           original24.get("angles") == list(ANGLES) and
           original24.get("fourth_impulses_selected") == 0 and
           original24.get("physical_measurements") == 0,
           "independent original WORLD23/24 ancestry omitted")
    cases, cases23, cases24 = (q.get("cases") for q in (native,original23,original24))
    demand(all(type(q) is list and len(q) == len(ANGLES)
               for q in (cases,cases23,cases24)), "eight original case controls required")
    owner = {"kind":"source-execution",
             "source":"original WORLD25 and original WORLD23/24 @" + PIN}
    hypothesis = {"kind":"declared",
                  "source":"conditional finite-segment vs square intersection on nominal movement"}
    pages = []
    admitted = absent = overlap_cases = no_overlap_cases = total_sampled_intersections = 0
    for index, angle in enumerate(ANGLES):
        c, p23, p24 = cases[index], cases23[index], cases24[index]
        demand(type(c) is dict and type(p23) is dict and type(p24) is dict and
               c.get("schema") == SOURCE and c.get("angle") == angle and
               p23.get("schema") == SRC23 and p23.get("angle") == angle and
               p24.get("schema") == SRC24 and p24.get("angle") == angle,
               "source cases or angle order substituted")
        demand(c.get("source_trial23_schema") == SRC23 and
               c.get("source_trial24_schema") == SRC24 and
               c.get("source_trial23_first_geometry") == p23.get("first_eligible_geometry") and
               c.get("source_trial24_first_edge") == p24.get("first_eligible_edge") and
               c.get("source_trial22_status") == p23.get("source_trial22_status") ==
               p24.get("source_trial22_status") and
               c.get("source_third_impulse") == p23.get("source_third_impulse") ==
               p24.get("source_third_impulse") and
               c.get("source_receiver") == p23.get("source_receiver") ==
               p24.get("source_receiver"),
               "source 23/24 feature or original third-impact relationship lost")
        demand(c.get("window_start") == START and c.get("window_end") == END and
               c.get("sample_intervals_per_face") == INTERVALS and
               c.get("original_24_by_6_world_preserved") is True and
               c.get("conditional_model_only") is True and
               c.get("model_positions_not_hardware") is True and
               c.get("physical_contact_witnessed") is False and
               c.get("fourth_impulse_solved") is False and
               c.get("new_receiver_created") is False and
               c.get("formally_certified_continuous_collision_detection") is False,
               "physical scope / grid bounds or fourth impact misrepresented")
        impulse = c["source_third_impulse"]
        admitted_here = impulse is not None
        steps = [
            {"op":"introduce", "id":"original-conditional-square",
             "state":{"source_angle":angle,"third_impulse_model":deepcopy(impulse),
                      "material_impulse_measured":False,
                      "fourth_impulse":None,"continued_contact_physics":None},
             "basis":owner},
            {"op":"introduce", "id":"finite-feature-investigation",
             "state":{"source_world":[24.,6.],"grid_start":START,
                      "grid_end":END,"grid_intervals_per_face":INTERVALS,
                      "native_stage":"finite-segment-square-intersection",
                      "continuous_collision_certificate":False,
                      "original_case_status":c["status"]}, "basis":hypothesis},
            {"op":"connect", "id":"source-conditional-geometry",
             "from":"original-conditional-square","to":"finite-feature-investigation",
             "label":"finite-source-faces-and-rotating-square",
             "state":{"original_third_impulse_admitted":admitted_here,
                      "new_receiver_built":False}, "basis":hypothesis},
            {"op":"observe","id":"prior-source-feature-alternatives",
             "entity":"object","subject":"finite-feature-investigation",
             "reading":{"original_trial23_first_finite_geometry":
                            deepcopy(p23.get("first_eligible_geometry")),
                        "original_trial24_first_endpoint_edge":
                            deepcopy(p24.get("first_eligible_edge")),
                        "native_trial23_digest":digest(p23),
                        "native_trial24_digest":digest(p24),
                        "source25_original_ancestry":True}, "basis":owner},
        ]
        records=c.get("face_results")
        candidates=c.get("finite_intersection_candidates")
        candidate=c.get("first_detected_bracket")
        comparison=c.get("onset_vs_original_vertex_candidate")
        demand(type(records) is list and type(candidates) is list,
               "original finite-face record or alternatives omitted")
        if not admitted_here:
            demand(c.get("status") == NO_SOURCE and c.get("source_receiver") is None and
                   records == [] and candidates == [] and candidate is None and
                   comparison is None and c.get("faces_with_sampled_intersection") == 0,
                   "no original third impulse has invented finite overlap")
            absent += 1
        else:
            admitted += 1
            demand(type(impulse) is dict and
                   impulse.get("materially_witnessed") is False and
                   type(c.get("source_receiver")) is dict and len(records) == 2 and
                   [rec.get("face") for rec in records if type(rec) is dict] == list(FACES),
                   "original model third impulse or finite source face missing")
            generated = []
            for face_index,(face,record) in enumerate(zip(FACES,records)):
                validate_face(record,face)
                total_sampled_intersections += record["intersecting_grid_samples"]
                if record["first_transition_bracket"] is not None:
                    generated.append({
                        "face":face,
                        "bracket":deepcopy(record["first_transition_bracket"]),
                        "kind":KIND,"hardware_measured":False})
                face_id=f"original-finite-segment-{face_index}"
                steps.extend([
                    {"op":"introduce","id":face_id,
                     "state":{"name":face,"endpoints":deepcopy(record["segment"]),
                              "finite_not_support_line":True,
                              "physical_material":False}, "basis":owner},
                    {"op":"connect","id":f"face-{face_index}-model-intersection",
                     "from":face_id,"to":"original-conditional-square",
                     "label":"tested-finite-square-overlap",
                     "state":{"conditional_grid_only":True,
                              "sampled_intersection_detected":
                                  record["intersecting_grid_samples"]>0},
                     "basis":hypothesis},
                    {"op":"observe","id":f"source-finite-grid-{face_index}",
                     "entity":"object","subject":face_id,
                     "reading":{"native_face":deepcopy(record),
                                "hardware_measured":False,
                                "interval_completeness_certified":False}, "basis":owner},
                ])
            generated.sort(key=lambda x:(x["bracket"]["bisected_transition_time"],x["face"]))
            demand(generated == candidates and
                   candidate == (generated[0] if generated else None),
                   "source finite overlap bracket/alternative classification changed")
            demand(comparison == expected_comparison(candidate,p23),
                   "same-finite-face source23 vertex comparison altered")
            face_overlap = sum(record["intersecting_grid_samples"]>0 for record in records)
            demand(c.get("faces_with_sampled_intersection") == face_overlap,
                   "sampled intersection face count altered")
            expected_status = (START_OVERLAP if any(record["start_intersected"] for record in records)
                               else BRACKET if generated else NONE)
            demand(c.get("status") == expected_status,
                   "finite intersection wrongly called exact contact or clearance")
            overlap_cases += int(face_overlap > 0)
            no_overlap_cases += int(face_overlap == 0)
        steps.extend([
            {"op":"observe","id":"finite-model-source-verdict",
             "entity":"object","subject":"finite-feature-investigation",
             "reading":{"source_status":c["status"],
                        "source25_sha256":digest(c),
                        "finite_first_transition":deepcopy(candidate),
                        "all_onset_alternatives":deepcopy(candidates),
                        "same_finite_face_vertex_comparison":deepcopy(comparison),
                        "actual_material_collision":False,
                        "fourth_impulse_selected":False,
                        "continuous_no-intersection_proven":False},
             "basis":owner},
            {"op":"observe","id":"finite-sample-counterexample",
             "entity":"object","subject":"original-conditional-square",
             "reading":{"original_third_impulse_admitted":admitted_here,
                        "finite_intersection_grid_detected":
                            any(rec.get("intersecting_grid_samples",0)>0 for rec in records),
                        "actual_material_collision":False,"fourth_impulse_selected":False},
             "basis":owner},
            {"op":"compare","id":"no-finite-grid-intersection-hypothesis",
             "observation":"finite-sample-counterexample",
             "expected":{"original_third_impulse_admitted":admitted_here,
                         "finite_intersection_grid_detected":False,
                         "actual_material_collision":False,
                         "fourth_impulse_selected":False}, "basis":hypothesis},
        ])
        plan={"schema":PLAN,"referent":f"WORLD25 / conditional full finite overlap {angle}deg",
              "limits":{"objects":4,"relations":3,"steps":len(steps)}, "steps":steps}
        receipt=run_plan(plan)
        witness=verify_receipt(receipt)
        had_intersection=any(rec.get("intersecting_grid_samples",0)>0 for rec in records)
        demand(witness["valid"] and
               receipt["final"]["comparisons"]
               ["no-finite-grid-intersection-hypothesis"]["result"] ==
               ("DIFFERENT" if had_intersection else "MATCH"),
               "neutral observed finite-intersection contrast diverged")
        pages.append({"index":index,"angle":angle,"status":c["status"],
                      "source_admitted":admitted_here,
                      "sampled_intersection_detected":had_intersection,
                      "receipt":receipt,"witness":witness})
    demand(native.get("source_third_impulse_cases") == admitted == 6 and
           native.get("no_source_third_impulse_controls") == absent == 2 and
           native.get("finite_intersection_grid_cases") == overlap_cases and
           native.get("finite_grid_no_intersection_cases") == no_overlap_cases and
           native.get("total_intersecting_grid_samples") == total_sampled_intersections,
           "original source aggregate counts changed")
    manifest={"pinned_source_commit":PIN,"source25_sha256":digest(native),
              "source23_sha256":digest(original23),"source24_sha256":digest(original24),
              "ordered_receipts":[{"index":p["index"],"angle":p["angle"],
                                   "head_hash":p["receipt"]["head_hash"]} for p in pages]}
    return {"schema":SCHEMA,"source_commit":PIN,
            "original_cases":8,"conditionally_admitted":admitted,"source_refusals":absent,
            "finite_grid_overlap_cases":overlap_cases,
            "finite_grid_no_overlap_cases":no_overlap_cases,
            "source_intersecting_grid_samples":total_sampled_intersections,
            "fourth_impulses_selected":0,"material_impacts_observed":0,
            "new_receivers_constructed":0,
            "finite_intersection_completeness_proven":False,
            "ledger_pages":pages,"ledger_witness":{
                "valid":all(p["witness"]["valid"] for p in pages),
                "pages_verified":len(pages),
                "steps_verified":sum(p["witness"]["steps_verified"] for p in pages),
                "observations_recorded":sum(p["witness"]["observations_recorded"] for p in pages)},
            "manifest":manifest,"manifest_sha256":digest(manifest)}


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--source23",type=Path,required=True)
    p.add_argument("--source24",type=Path,required=True)
    a=p.parse_args()
    print(json.dumps(carry(load_json(a.native),load_json(a.source23),
                           load_json(a.source24)),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
