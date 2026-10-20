"""A/B WORLD22 — source-attributed bounded post-third movement possibilities.

The original WORLD22 source and independent numerical oracle own all rotating
corner and boundary mathematics. This neutral carrier records the reported
first crossing, alternatives, no-crossing windows and refused source controls;
it does not admit any fourth impact, actual hardware contact or later motion.
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

SCHEMA = "ab-world-trial22-first-post-third-source-evidence/v1"
SOURCE = "world-ab-first-candidate-after-conditional-third/v1"
SOURCE21 = "world-ab-conditional-third-contact/v1"
PIN = "84e9bc9a51e813cfcac3146ab49e153cdb02d47b"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
HORIZON = .25
FACES = ("original_finite_face", "motion_derived_receiver")
PLANES = FACES + ("world_left", "world_right", "world_bottom", "world_top")
KINDS = ("WORLD_PERIMETER_CANDIDATE", "FINITE_FACE_INTERIOR_CANDIDATE",
         "SUPPORT_LINE_OUTSIDE_FINITE_FACE_UNRESOLVED",
         "ENDPOINT_FEATURE_UNRESOLVED")
NO_SOURCE = "NO_ADMITTED_THIRD_IMPULSE"
NO_CROSSING = "NO_INWARD_SOURCE_LINE_CROSSING_IN_BOUNDED_PROJECTION"


def demand(ok: bool, description: str) -> None:
    if not ok:
        raise ValueError("A/B WORLD22: " + description)


def number(x: Any) -> bool:
    return type(x) in (float, int) and isfinite(x)


def point(x: Any) -> bool:
    return type(x) is list and len(x) == 2 and all(number(z) for z in x)


def validate_record(case: dict, previous: dict, angle: float) -> bool:
    demand(type(case) is dict and type(previous) is dict
           and case.get("schema") == SOURCE and case.get("angle") == angle
           and case.get("source_trial21_schema") == SOURCE21
           and previous.get("schema") == SOURCE21 and previous.get("angle") == angle
           and case.get("source_trial21_status") == previous.get("status")
           and case.get("source_third_impulse") == previous.get("third_impulse")
           and case.get("source_receiver") == previous.get("source_receiver")
           and case.get("projection_horizon") == HORIZON
           and case.get("source_trial21_local_window") == .008
           and case.get("source_original_world") == [24., 6.],
           "original WORLD21 ancestry, original world, or time bound changed")
    for flag, value in (
        ("unselected_conditional_model_only", True),
        ("model_motion_not_material_measurement", True),
        ("fourth_impulse_solved", False),
        ("new_receiver_constructed", False),
        ("continuous_real_world_motion_verified", False),
        ("formally_outward_rounded_certificate", False),
        ("later_forces_and_impacts_assumed_absent", True),
    ):
        demand(case.get(flag) is value, "source projection promoted to material world: " + flag)
    records = case.get("all_source_line_crossings")
    tied = case.get("coearliest_crossings")
    demand(type(records) is list and type(tied) is list,
           "candidate alternatives or source-root list missing")
    first = case.get("first_crossing")
    admitted = previous.get("third_impulse") is not None
    if not admitted:
        demand(case.get("status") == NO_SOURCE and first is None
               and records == [] and tied == []
               and case.get("monotonic_intervals_checked") == 0,
               "no source third impulse may not acquire later contact")
        return False
    demand(previous.get("status") == "CONDITIONAL_LOCAL_SEPARATION"
           and type(previous.get("third_impulse")) is dict
           and previous.get("third_impulse").get("materially_witnessed") is False
           and type(case.get("monotonic_intervals_checked")) is int
           and case["monotonic_intervals_checked"] > 0,
           "source third impulse not admitted or its numerical interval checks omitted")
    impulse_time=previous["third_impulse"].get("contact_absolute_virtual_time")
    demand(number(impulse_time),"original third impulse time missing")
    time_prior=-1.
    for r in records:
        demand(type(r) is dict
               and r.get("surface") in PLANES
               and type(r.get("vertex_index")) is int
               and 0 <= r["vertex_index"] < 4
               and number(r.get("dt_after_third_impulse"))
               and 0 < r["dt_after_third_impulse"] <= HORIZON
               and r["dt_after_third_impulse"] >= time_prior
               and number(r.get("absolute_virtual_time"))
               and abs(r["absolute_virtual_time"] -
                       (impulse_time + r["dt_after_third_impulse"])) < 3e-7
               and point(r.get("vertex_position"))
               and number(r.get("incoming_normal_vertex_rate"))
               and r["incoming_normal_vertex_rate"] < 0
               and number(r.get("signed_line_gap_residual"))
               and abs(r["signed_line_gap_residual"]) < 3e-7
               and r.get("feature_classification") in KINDS
               and r.get("physical_contact_measured") is False,
               "source root chronology, vertex geometry, or real-world claim changed")
        if r["surface"] in FACES:
            demand(number(r.get("source_face_tangent_coordinate")),
                   "finite source face tangent coordinate missing")
        else:
            demand(r.get("source_face_tangent_coordinate") is None,
                   "unfounded tangent coordinate on world perimeter")
        time_prior=r["dt_after_third_impulse"]
    if first is None:
        demand(case.get("status") == NO_CROSSING and records == [] and tied == [],
               "no-crossing result invented an event or concealed records")
        return False
    demand(first == records[0] and len(tied) >= 1
           and tied == records[:len(tied)]
           and all(abs(x["dt_after_third_impulse"] -
                       first["dt_after_third_impulse"]) <= 1e-7 for x in tied),
           "first candidate or coearliest alternatives changed")
    expected=("MULTIPLE_FIRST_FEATURES_UNRESOLVED" if len(tied)>1 else
              "FIRST_MODEL_CONTACT_GEOMETRY_CANDIDATE"
              if first["feature_classification"] in KINDS[:2]
              else first["feature_classification"])
    demand(case.get("status") == expected,
           "unsupported first contact or outside-segment result promoted")
    return True


def carry(source22: dict, source21: dict, source_commit: str=PIN) -> dict:
    demand(source_commit == PIN, "original immutable WORLD22 source pin changed")
    demand(type(source22) is dict and source22.get("schema") == SOURCE
           and source22.get("angles") == list(ANGLES)
           and source22.get("new_world_or_engine") is False
           and source22.get("physical_contact_measurements") == 0
           and source22.get("selected_fourth_impulses") == 0
           and source22.get("real_receivers_constructed") == 0,
           "original bounded source identity or physical claim changed")
    demand(type(source21) is dict and source21.get("schema") == SOURCE21
           and source21.get("angles") == list(ANGLES)
           and source21.get("real_material_behavior_verified") is False
           and source21.get("another_receiver_created") is False,
           "original WORLD21 source owner or physical scope changed")
    cases=source22.get("cases")
    prior=source21.get("cases")
    demand(type(cases) is list and len(cases) == 8
           and type(prior) is list and len(prior) == 8,
           "eight original angle controls required")
    basis={"kind":"source-execution","source":"original WORLD22 @" + PIN}
    hypothetical={"kind":"declared","source":"conditional post-third no-crossing hypothesis"}
    pages=[]
    crossed=0
    no_crossing=0
    refused=0
    retained_roots=0
    for index,angle in enumerate(ANGLES):
        c,previous=cases[index],prior[index]
        has_root=validate_record(c,previous,angle)
        admitted=previous["third_impulse"] is not None
        crossed+=int(has_root)
        no_crossing+=int(admitted and not has_root)
        refused+=int(not admitted)
        retained_roots+=len(c["all_source_line_crossings"])
        steps=[
            {"op":"introduce","id":"original-source-geometry",
             "state":{"angle":angle,"original_world":[24.,6.],
                      "source21_sha256":digest(previous),
                      "physical_geometry_measured":False},"basis":basis},
            {"op":"introduce","id":"conditional-rotating-square",
             "state":{"original_third_impulse":deepcopy(previous["third_impulse"]),
                      "unselected_hypothetical_motion":True,
                      "material_contact_response_selected":False},"basis":basis},
            {"op":"connect","id":"source-bounded-projection",
             "from":"original-source-geometry","to":"conditional-rotating-square",
             "label":"source-conditioned-post-third-projection",
             "state":{"horizon":HORIZON,"no_fourth_impulse_selected":True},
             "basis":hypothetical},
            {"op":"observe","id":"source-owned-crossing-search",
             "entity":"object","subject":"original-source-geometry",
             "reading":{"source_status":c["status"],
                        "source22_sha256":digest(c),
                        "source21_sha256":digest(previous),
                        "monotonic_intervals_checked":
                        c["monotonic_intervals_checked"],
                        "all_inward_line_crossings":
                        deepcopy(c["all_source_line_crossings"]),
                        "coearliest_alternatives":
                        deepcopy(c["coearliest_crossings"]),
                        "source_first_crossing":deepcopy(c["first_crossing"]),
                        "numerical_source_not_material_sensor":True},
             "basis":basis},
            {"op":"observe","id":"first-bounded-contrast",
             "entity":"object","subject":"conditional-rotating-square",
             "reading":{"original_third_impulse_admitted":admitted,
                        "line_crossing_in_window":has_root,
                        "physical_contact_measured":False,
                        "fourth_impulse_selected":False,
                        "new_receiver_built":False},
             "basis":basis},
            {"op":"compare","id":"no-further-line-crossing-hypothesis",
             "observation":"first-bounded-contrast",
             "expected":{"original_third_impulse_admitted":admitted,
                         "line_crossing_in_window":False,
                         "physical_contact_measured":False,
                         "fourth_impulse_selected":False,
                         "new_receiver_built":False},
             "basis":hypothetical},
        ]
        plan={"schema":PLAN,
              "referent":f"WORLD22 / source-first-post-third / {angle}deg",
              "limits":{"objects":2,"relations":1,"steps":len(steps)},
              "steps":steps}
        receipt=run_plan(plan)
        witness=verify_receipt(receipt)
        demand(witness["valid"] and
               set(receipt["final"]["objects"]) ==
               {"original-source-geometry","conditional-rotating-square"} and
               receipt["final"]["comparisons"]
               ["no-further-line-crossing-hypothesis"]["result"] ==
               ("DIFFERENT" if has_root else "MATCH"),
               "A/B witness or comparison state altered")
        pages.append({"index":index,"angle":angle,"source_status":c["status"],
                      "crossing_reported":has_root,
                      "source_third_impulse_admitted":admitted,
                      "receipt":receipt,"witness":witness})
    demand(source22.get("conditional_third_impulse_inputs") == crossed + no_crossing == 6
           and source22.get("no_third_impulse_controls") == refused == 2
           and source22.get("source_line_crossing_cases") == crossed == 3
           and source22.get("source_line_no_crossing_cases") == no_crossing == 3,
           "original source case counts changed")
    manifest={"pinned_source_commit":PIN,
              "source22_sha256":digest(source22),
              "source21_sha256":digest(source21),
              "ordered_receipts":[{"index":p["index"],"angle":p["angle"],
                                   "head_hash":p["receipt"]["head_hash"]}
                                  for p in pages]}
    return {"schema":SCHEMA,"source_commit":PIN,
            "source_cases":8,"line_crossing_cases":crossed,
            "bounded_no_crossing_cases":no_crossing,
            "without_source_third_impulse":refused,
            "all_source_candidates_retained":retained_roots,
            "real_fourth_impulses":0,"real_material_measurements":0,
            "constructed_new_receivers":0,
            "post_crossing_trajectories_admitted":0,
            "ledger_pages":pages,"ledger_witness":{
                "valid":all(p["witness"]["valid"] for p in pages),
                "pages_verified":len(pages),
                "steps_verified":sum(p["witness"]["steps_verified"] for p in pages),
                "observations_recorded":sum(
                    p["witness"]["observations_recorded"] for p in pages)},
            "manifest":manifest,"manifest_sha256":digest(manifest)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--native",type=Path,required=True)
    parser.add_argument("--source21",type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(carry(load_json(args.native),load_json(args.source21)),
                     sort_keys=True,indent=2))


if __name__=="__main__":
    main()
