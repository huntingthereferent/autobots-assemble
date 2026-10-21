"""Neutral A/B WORLD30 source receipts: clearance evidence, not real dynamics.

Original WORLD29/30 numerical source and independent native verifier own the
mechanical response and local gap/rate/curvature math. This carrier records
their conditional observations, refusals, and digests. It NEVER mutates the
real or virtual square according to a source-proposed fourth impulse.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from math import isfinite
from pathlib import Path

from work.ab_world.construction import PLAN,digest,load_json,run_plan
from work.ab_world.verify_construction import verify_receipt

PIN="38461711e48d59c859b855772bf8a33119c45b78"
SCHEMA="ab-world-trial30-conditional-local-clearance-ledger/v1"
SOURCE="world-ab-local-clearance-after-conditional-fourth-response/v1"
PRIOR="world-ab-first-finite-feature-conditional-response/v1"
ANGLES=(0.,2.5,5.,7.5,10.,12.25,15.,20.)
ACCEPTED="CONDITIONAL_LOCAL_OUTGOING_SEPARATION"
NO_RESPONSE="NO_QUALIFIED_SOURCE_FOURTH_RESPONSE"
BOUND_LABELS=("original_finite_face","motion_derived_receiver","world_left",
              "world_right","world_bottom","world_top")


def demand(ok,why):
    if not ok:
        raise ValueError("A/B WORLD30: "+why)


def number(x):
    return type(x) in (int,float) and isfinite(x)


def verify_transport(case,prior,angle):
    demand(type(case) is dict and type(prior) is dict
           and case.get("schema")==SOURCE and prior.get("schema")==PRIOR
           and case.get("angle")==prior.get("angle")==angle
           and case.get("source_trial29_schema")==PRIOR
           and case.get("source_trial29_status")==prior.get("status")
           and case.get("source_candidate_contact")==prior.get("qualifying_source_feature")
           and case.get("source_candidate_response")==prior.get("conditional_fourth_response")
           and case.get("source_original_third_impulse")==prior.get("source_original_third_response")
           and case.get("original_world")==[24.,6.]
           and case.get("original_finite_source_faces")==2
           and case.get("four_original_world_boundaries")==4
           and case.get("post_candidate_horizon")==.008,
           "original source lineage, bounded world or time changed")
    claims={
        "nominal_free_flight_model_only":True,
        "actual_contact_selected":False,
        "real_material_response_witnessed":False,
        "post_candidate_continuous_motion_authenticated":False,
        "formally_outward_rounded_numeric_certificate":False,
        "new_receiver_built":False,
        "fifth_impulse_computed":False,
    }
    demand(all(case.get(key) is value for key,value in claims.items()),
           "conditional numerical source promoted to material event")
    source_proposed=prior.get("conditional_fourth_response")
    bounds=case.get("clearance_bounds")
    demand(type(bounds) is list,"missing source bound/refusal list")
    if source_proposed is None:
        demand(case.get("status")==NO_RESPONSE and bounds==[]
               and case.get("accepted_bounds")==0
               and case.get("unresolved_bounds")==0
               and case.get("nominal_local_clearance_admitted") is False,
               "no original candidate acquired modeled postcontact motion")
        return False
    demand(prior.get("status")=="CONDITIONAL_SINGLE_VERTEX_NORMAL_RESPONSE_CANDIDATE"
           and source_proposed.get("materially_witnessed") is False
           and source_proposed.get("response_selected_as_actual") is False
           and len(bounds)==24,
           "source response not qualified or source constraints lost")
    accepted=0
    touching=0
    for i,r in enumerate(bounds):
        demand(type(r) is dict
               and r.get("surface")==BOUND_LABELS[i//4]
               and r.get("corner_index")==i%4
               and type(r.get("accepted")) is bool
               and type(r.get("starts_at_qualified_contact")) is bool
               and r.get("original_finite_source_not_real_hardware") is True
               and all(number(r.get(key)) for key in (
                   "gap_at_candidate","outgoing_normal_rate",
                   "curvature_upper_bound","end_gap_lower_bound",
                   "normal_rate_lower_bound","conservative_bound")),
               "source plane/corner identities, numerical values or material scope changed")
        accepted+=int(r["accepted"])
        touching+=int(r["starts_at_qualified_contact"])
    demand(touching==1
           and case.get("accepted_bounds")==accepted
           and case.get("unresolved_bounds")==24-accepted
           and case.get("nominal_local_clearance_admitted") is (accepted==24),
           "source 24-constraint decision or unique touch changed")
    expected=ACCEPTED if accepted==24 else "POST_CANDIDATE_LOCAL_GEOMETRY_UNRESOLVED"
    demand(case.get("status")==expected,
           "unknown local interval falsely cleared or real contact promoted")
    # The PINNED original native verifier, not this recorder, adjudicates
    # numerical Taylor lower bounds and mechanics.
    return accepted==24


def carry(native,prior,source_commit=PIN):
    demand(source_commit==PIN,"source commit changed")
    demand(type(native) is dict and native.get("schema")==SOURCE
           and native.get("angles")==list(ANGLES)
           and native.get("real_material_impacts_witnessed")==0
           and native.get("selected_actual_fourth_impulses")==0
           and native.get("fifth_impulses_computed")==0
           and native.get("new_receivers_constructed")==0
           and native.get("new_physics_engine") is False,
           "source WORLD30 report or material claim changed")
    demand(type(prior) is dict and prior.get("schema")==PRIOR
           and prior.get("angles")==list(ANGLES)
           and prior.get("material_impacts_witnessed")==0
           and prior.get("actual_fourth_impulses_selected")==0
           and prior.get("post_response_trajectories_solved")==0,
           "original WORLD29 response ownership changed")
    cases,parents=native.get("cases"),prior.get("cases")
    demand(type(cases) is list and len(cases)==8
           and type(parents) is list and len(parents)==8,
           "eight bounded source angle controls missing")
    origin={"kind":"source-execution","source":"original WORLD30 native @"+PIN}
    declared={"kind":"declared","source":"no conditional local post-response clearance expected"}
    pages=[]
    covered=0
    unresolved=0
    no_source=0
    for index,angle in enumerate(ANGLES):
        a,b=cases[index],parents[index]
        verified=verify_transport(a,b,angle)
        covered+=int(verified)
        unresolved+=int(a["status"]=="POST_CANDIDATE_LOCAL_GEOMETRY_UNRESOLVED")
        no_source+=int(a["status"]==NO_RESPONSE)
        steps=[
            {"op":"introduce","id":"source-bounded-geometry",
             "state":{"angle":angle,"source29_digest":digest(b),
                      "source30_digest":digest(a),"actual_material_contact":False},
             "basis":origin},
            {"op":"introduce","id":"hypothetical-square",
             "state":{"source_original_response":deepcopy(b["conditional_fourth_response"]),
                      "physical_fourth_impulse_selected":False,
                      "later_real_movement_computed":False},"basis":origin},
            {"op":"connect","id":"source-conditional-local-geometry",
             "from":"source-bounded-geometry","to":"hypothetical-square",
             "label":"source-declared-local-conditional-projection",
             "state":{"original_horizon":.008,
                      "source_owns_motion_law":True},"basis":declared},
            {"op":"observe","id":"prior-source-response",
             "entity":"object","subject":"source-bounded-geometry",
             "reading":{"status":b["status"],"source29_digest":digest(b),
                        "conditional_response":deepcopy(b["conditional_fourth_response"]),
                        "actual_response_selected":False},"basis":origin},
            {"op":"observe","id":"source-local-clearance-bounds",
             "entity":"object","subject":"hypothetical-square",
             "reading":{"status":a["status"],"source30_digest":digest(a),
                        "original_plane_bounds":deepcopy(a["clearance_bounds"]),
                        "nominal_local_clearance_admitted":verified,
                        "no_actual_movement_authenticated":True},"basis":origin},
            {"op":"observe","id":"source-physical-refusals",
             "entity":"object","subject":"hypothetical-square",
             "reading":{"conditional_local_clearance":verified,
                        "fourth_impulse_selected":False,
                        "real_material_measurement":False,
                        "fifth_impulse_computed":False,
                        "new_receiver_constructed":False},"basis":origin},
            {"op":"compare","id":"bounded-separation-versus-no-response",
             "observation":"source-physical-refusals",
             "expected":{"conditional_local_clearance":False,
                         "fourth_impulse_selected":False,
                         "real_material_measurement":False,
                         "fifth_impulse_computed":False,
                         "new_receiver_constructed":False},
             "basis":declared},
        ]
        plan={"schema":PLAN,
              "referent":f"WORLD30 / conditional local bounds / {angle}deg",
              "limits":{"objects":2,"relations":1,"steps":len(steps)},
              "steps":steps}
        receipt=run_plan(plan)
        result=verify_receipt(receipt)
        demand(result["valid"] and
               receipt["final"]["comparisons"]
               ["bounded-separation-versus-no-response"]["result"]==
               ("DIFFERENT" if verified else "MATCH"),
               "independent A/B receipt replay/contrast failed")
        pages.append({"index":index,"angle":angle,
                      "source_status":a["status"],
                      "nominal_local_clearance":verified,
                      "receipt":receipt,"witness":result})
    demand(covered==native.get("locally_separated_conditional_candidates")==3
           and unresolved==native.get("post_candidate_geometry_unresolved")==0
           and no_source==native.get("no_qualified_source_response")==5
           and native.get("source_qualified_fourth_candidates")==covered+unresolved,
           "original source case totals differ")
    manifest={"original_source_commit":PIN,"world30_digest":digest(native),
              "world29_digest":digest(prior),
              "ordered_ledger_heads":[{"index":p["index"],"angle":p["angle"],
                                       "head_hash":p["receipt"]["head_hash"]}
                                      for p in pages]}
    return {"schema":SCHEMA,"original_source_commit":PIN,
            "source_cases":8,"qualified_local_clearances":covered,
            "source_unresolved_local_cases":unresolved,
            "without_original_fourth_candidate":no_source,
            "physical_fourth_impacts_selected":0,"fifth_impulses_computed":0,
            "actual_post_contact_motion_authenticated":0,"receivers_created":0,
            "ledger_pages":pages,"ledger_witness":{
                "valid":all(p["witness"]["valid"] for p in pages),
                "pages_verified":len(pages),
                "steps_verified":sum(p["witness"]["steps_verified"] for p in pages),
                "observations_recorded":sum(
                    p["witness"]["observations_recorded"] for p in pages)},
            "manifest":manifest,"manifest_digest":digest(manifest)}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--native",type=Path,required=True)
    parser.add_argument("--prior29",type=Path,required=True)
    a=parser.parse_args()
    print(json.dumps(carry(load_json(a.native),load_json(a.prior29)),sort_keys=True,indent=2))


if __name__=="__main__":
    main()
