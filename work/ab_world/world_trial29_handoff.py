"""A/B WORLD29 — neutral original-source contact qualification receipts.

Original WORLD29 numerical source and its independent original verifier own
all contact geometry and hypothetical rigid-body response equations. The
separate general A/B world only observes those source outcomes and refuses
physical selection or a derived receiver. Original WORLD28 ancestry is carried
in parallel; no numerical law is implemented in this adapter.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from math import isfinite
from pathlib import Path
from typing import Any

from work.ab_world.construction import PLAN,digest,load_json,run_plan
from work.ab_world.verify_construction import verify_receipt

PIN="74ecad19a43c6bc093151198fd18cfecf80334cc"
SCHEMA="ab-world-trial29-source-contact-qualification-ledger/v1"
SOURCE="world-ab-first-finite-feature-conditional-response/v1"
PRIOR="world-ab-local-first-finite-onset-refinement/v1"
ANGLES=(0.,2.5,5.,7.5,10.,12.25,15.,20.)
ACCEPTED="CONDITIONAL_SINGLE_VERTEX_NORMAL_RESPONSE_CANDIDATE"


def demand(ok:bool,why:str):
    if not ok:
        raise ValueError("A/B WORLD29: "+why)


def real(x:Any)->bool:
    return type(x) in (int,float) and isfinite(x)


def pair(x:Any)->bool:
    return type(x) is list and len(x)==2 and all(real(y) for y in x)


def source_decision(case:dict,earlier:dict,angle:float)->bool:
    demand(type(case) is dict and type(earlier) is dict
           and case.get("schema")==SOURCE and earlier.get("schema")==PRIOR
           and case.get("angle")==earlier.get("angle")==angle
           and case.get("source_trial28_schema")==PRIOR
           and case.get("source_trial28_status")==earlier.get("status")
           and case.get("source_original_third_response")==
           earlier.get("source_original_third_impulse")
           and case.get("original_world_dimensions")==[24.,6.]
           and case.get("original_mass")==1.
           and real(case.get("original_inertia"))
           and case["original_inertia"]>0,
           "unchanged original finite source, angle, or prior source movement missing")
    claims={
        "source_conditional_free_flight_only":True,
        "physical_fourth_impact_witnessed":False,
        "physical_response_selected":False,
        "post_response_trajectory_solved":False,
        "another_receiver_constructed":False,
        "exact_root_or_material_certification":False,
    }
    demand(all(case.get(k) is v for k,v in claims.items())
           and case.get("assumed_law")==
           "single frictionless normal, restitution 1, unit-mass rotating square",
           "source candidate promoted to actual physical event")
    response=case.get("conditional_fourth_response")
    qualified=case.get("qualifying_source_feature")
    previous_onset=earlier.get("first_eligible_finite_onset")
    if earlier.get("source_original_third_impulse") is None:
        demand(case.get("status")=="NO_ADMITTED_THIRD_IMPULSE"
               and previous_onset is None and qualified is None
               and response is None and case.get("source_contact_rejection") is None,
               "absent source third impulse fabricated finite contact")
        return False
    if previous_onset is None:
        demand(case.get("status")=="NO_ORIGINAL_FIRST_FINITE_ONSET"
               and qualified is None and response is None
               and case.get("source_contact_rejection") is None,
               "absent source first contact fabricated response")
        return False
    if response is None:
        demand(qualified is None
               and case.get("status") in (
                   "UNRESOLVED_OR_COMPETING_FINITE_CONTACT",
                   "UNRESOLVED_FIRST_ONSET_ANCESTRY")
               and case.get("source_contact_rejection") is not None,
               "original refusal suppressed or replaced by hypothetical physical event")
        return False
    demand(case.get("status")==ACCEPTED
           and case.get("source_contact_rejection") is None
           and type(qualified) is dict and type(response) is dict
           and qualified.get("source_face")==previous_onset.get("face")
           and abs(qualified.get("source_onset_refined_at",-1)-
                   previous_onset["refined_sat_bracket"]["first_nominally_intersecting_time"])
           < 3e-7,
           "conditional contact must reference original refined finite source face")
    demand(type(qualified.get("source_vertex_index")) is int
           and 0<=qualified["source_vertex_index"]<4
           and response.get("source_vertex_index")==qualified["source_vertex_index"]
           and response.get("source_face")==qualified["source_face"]
           and pair(qualified.get("contact_point"))
           and pair(qualified.get("contact_center"))
           and pair(qualified.get("contact_normal"))
           and pair(qualified.get("contact_lever"))
           and real(qualified.get("absolute_virtual_time"))
           and real(qualified.get("finite_face_tangent_coordinate"))
           and real(qualified.get("dt_after_original_third_impulse"))
           and qualified.get("independent_finite_geometry_not_material_contact") is True,
           "original finite vertex location and time source not preserved")
    demand(response.get("materially_witnessed") is False
           and response.get("response_selected_as_actual") is False
           and response.get("further_contacts_resolved") is False
           and real(response.get("normal_impulse"))
           and response["normal_impulse"]>0
           and pair(response.get("incoming_velocity"))
           and pair(response.get("outgoing_velocity"))
           and all(real(response.get(k)) for k in (
               "incoming_contact_normal_rate","outgoing_contact_normal_rate",
               "kinetic_energy_before","kinetic_energy_after",
               "incoming_spin","outgoing_spin"))
           and response["incoming_contact_normal_rate"]<0
           and response["outgoing_contact_normal_rate"]>0
           and abs(response["incoming_contact_normal_rate"]+
                   response["outgoing_contact_normal_rate"])<3e-7
           and abs(response["kinetic_energy_before"]-
                   response["kinetic_energy_after"])<3e-7,
           "conditional mathematical response promoted, corrupted or nonconservative")
    # Only the separate, pinned original source's independent numerical
    # verifier adjudicates the normal/contact/impulse law itself.
    return True


def carry(original:dict,previous:dict,source_commit:str=PIN)->dict:
    demand(source_commit==PIN, "immutable original WORLD29 source commit changed")
    demand(type(original) is dict and original.get("schema")==SOURCE
           and original.get("angles")==list(ANGLES)
           and original.get("material_impacts_witnessed")==0
           and original.get("actual_fourth_impulses_selected")==0
           and original.get("post_response_trajectories_solved")==0
           and original.get("receivers_constructed")==0
           and original.get("new_engine_or_world") is False,
           "source WORLD29 report/version/material claim changed")
    demand(type(previous) is dict and previous.get("schema")==PRIOR
           and previous.get("angles")==list(ANGLES)
           and previous.get("actual_material_contacts_measured")==0
           and previous.get("fourth_impulses_solved")==0
           and previous.get("real_receivers_built")==0,
           "source WORLD28 ancestry or physical boundary changed")
    cases,earlier=original.get("cases"),previous.get("cases")
    demand(type(cases) is list and type(earlier) is list
           and len(cases)==len(earlier)==8,
           "all eight unchanged source cases required")
    owner={"kind":"source-execution","source":"original WORLD29 numerical source @"+PIN}
    hypothesis={"kind":"declared","source":"no admitted fourth-contact mathematical response"}
    pages=[]
    accepted=0
    absent=0
    no_onset=0
    refused=0
    for index,angle in enumerate(ANGLES):
        c,p=cases[index],earlier[index]
        admitted=source_decision(c,p,angle)
        accepted+=int(admitted)
        absent+=int(c["status"]=="NO_ADMITTED_THIRD_IMPULSE")
        no_onset+=int(c["status"]=="NO_ORIGINAL_FIRST_FINITE_ONSET")
        refused+=int(c["status"] in (
            "UNRESOLVED_OR_COMPETING_FINITE_CONTACT",
            "UNRESOLVED_FIRST_ONSET_ANCESTRY"))
        steps=[
            {"op":"introduce","id":"original-finite-source-record",
             "state":{"source_angle":angle,"source28_sha256":digest(p),
                      "source29_sha256":digest(c),
                      "material_contact_measured":False},
             "basis":owner},
            {"op":"introduce","id":"conditional-square-model",
             "state":{"hypothetical_original_third_response":
                      deepcopy(p["source_original_third_impulse"]),
                      "actual_fourth_impulse_selected":False,
                      "later_ballistic_movement_admitted":False},
             "basis":hypothesis},
            {"op":"connect","id":"source-to-bounded-square-qualification",
             "from":"original-finite-source-record",
             "to":"conditional-square-model",
             "label":"original-model-qualification-only",
             "state":{"source_owns_contact_law":True,
                      "physical_contact_witnessed":False},
             "basis":hypothesis},
            {"op":"observe","id":"earlier-first-finite-onset",
             "entity":"object","subject":"original-finite-source-record",
             "reading":{"original_source28_status":p["status"],
                        "source28_case_sha256":digest(p),
                        "original_first_finite_onset":
                        deepcopy(p["first_eligible_finite_onset"]),
                        "exact_root_certified":False},
             "basis":owner},
            {"op":"observe","id":"source-qualification-reason",
             "entity":"object","subject":"conditional-square-model",
             "reading":{"original_world29_status":c["status"],
                        "source29_case_sha256":digest(c),
                        "source_contact_feature":
                        deepcopy(c["qualifying_source_feature"]),
                        "source_refusal":
                        deepcopy(c["source_contact_rejection"]),
                        "numerical_source_not_physical_instrument":True},
             "basis":owner},
            {"op":"observe","id":"bounded-conditional-response",
             "entity":"object","subject":"conditional-square-model",
             "reading":{"source_qualified_response_present":admitted,
                        "original_proposed_response":
                        deepcopy(c["conditional_fourth_response"]),
                        "physical_impulse_selected":False,
                        "actual_post_contact_movement_solved":False,
                        "new_receiver_built":False},
             "basis":owner},
            {"op":"compare","id":"source-response-versus-absent",
             "observation":"bounded-conditional-response",
             "expected":{"source_qualified_response_present":False,
                         "original_proposed_response":None,
                         "physical_impulse_selected":False,
                         "actual_post_contact_movement_solved":False,
                         "new_receiver_built":False},
             "basis":hypothesis},
        ]
        plan={"schema":PLAN,
              "referent":f"WORLD29 / original source qualification / {angle}deg",
              "limits":{"objects":2,"relations":1,"steps":len(steps)},
              "steps":steps}
        receipt=run_plan(plan)
        verdict=verify_receipt(receipt)
        demand(verdict["valid"]
               and set(receipt["final"]["objects"])==
               {"original-finite-source-record","conditional-square-model"}
               and receipt["final"]["comparisons"]
               ["source-response-versus-absent"]["result"]==
               ("DIFFERENT" if admitted else "MATCH"),
               "A/B bounded source receipt failed independent reconstruction")
        pages.append({"index":index,"angle":angle,
                      "original_status":c["status"],
                      "conditional_response_present":admitted,
                      "receipt":receipt,"witness":verdict})
    demand(accepted==original.get("conditionally_qualifying_responses")==3
           and absent==original.get("absent_source_impulse_controls")==2
           and original.get("original_finite_first_onset_cases")==3
           and refused==original.get("unresolved_finite_feature_cases")
           and accepted+refused==3 and no_onset==3,
           "original bounded source candidate/refusal counts changed")
    manifest={"original_source_commit":PIN,
              "world29_sha256":digest(original),
              "world28_sha256":digest(previous),
              "ordered_ledger_heads":[{"index":p["index"],"angle":p["angle"],
                                       "head_hash":p["receipt"]["head_hash"]}
                                      for p in pages]}
    return {"schema":SCHEMA,"source_commit":PIN,
            "original_cases":8,"qualified_mathematical_candidates":accepted,
            "no_original_third_impulse_controls":absent,
            "no_first_finite_onset_controls":no_onset,
            "source_contact_refusals":refused,
            "physical_impacts_measured":0,"actual_impulses_selected":0,
            "verified_post_contact_motion":0,"new_receivers_built":0,
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
    parser.add_argument("--prior28",type=Path,required=True)
    a=parser.parse_args()
    print(json.dumps(carry(load_json(a.native),load_json(a.prior28)),
                     sort_keys=True,indent=2))


if __name__=="__main__":
    main()
