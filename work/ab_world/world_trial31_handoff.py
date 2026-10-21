"""A/B WORLD31 — original source's first conservative limit as a bounded ledger.

The original WORLD30/31 numerical source and original independent analytical
witness own the 24 per-corner/plane inequalities and their sufficient prefixes.
This neutral A/B carrier records them, compares them, and expressly refuses
to turn first evidence-bound failure into a fifth material contact or impulse.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from math import isfinite
from pathlib import Path

from work.ab_world.construction import PLAN,digest,load_json,run_plan
from work.ab_world.verify_construction import verify_receipt

PIN="3adab3834913f3b8948a99725e9457c62c2d524b"
SCHEMA="ab-world-trial31-first-source-envelope-limit-ledger/v1"
SOURCE="world-ab-source-first-conservative-envelope-limit/v1"
PRIOR="world-ab-local-clearance-after-conditional-fourth-response/v1"
ANGLES=(0.,2.5,5.,7.5,10.,12.25,15.,20.)
BASELINE=.008
HORIZON=.25
MARGIN=1e-5
KNOWN_PLANES=("original_finite_face","motion_derived_receiver",
              "world_left","world_right","world_bottom","world_top")


def demand(ok,why):
    if not ok:
        raise ValueError("A/B WORLD31: "+why)


def numeric(value):
    return type(value) in (float,int) and isfinite(value)


def verify_case(case,older,angle):
    demand(type(case) is dict and type(older) is dict
           and case.get("schema")==SOURCE and older.get("schema")==PRIOR
           and case.get("angle")==older.get("angle")==angle
           and case.get("source_trial30_schema")==PRIOR
           and case.get("source_trial30_status")==older.get("status")
           and case.get("original_source30_case")==older
           and case.get("source_qualified_fourth_response")==older.get("source_candidate_response")
           and case.get("original_24_by_6_world")==[24.,6.]
           and case.get("source_original_minimum_horizon")==BASELINE
           and case.get("declared_followup_horizon")==HORIZON
           and case.get("positive_separation_margin")==MARGIN
           and case.get("original_24_halfplane_constraints")==24,
           "original WORLD30 ancestry, original world or bounded horizon changed")
    material={
        "same_original_two_finite_source_faces":True,
        "original_model_response_only":True,
        "physical_fourth_impulse_selected":False,
        "fifth_impulse_solved":False,
        "fifth_contact_feature_observed":False,
        "physical_trajectory_recorded":False,
        "exact_interval_arithmetic_certificate":False,
        "post_limit_continuation_admitted":False,
    }
    demand(all(case.get(key) is val for key,val in material.items()),
           "numerical sufficiency limit promoted to physical event")
    limits=case.get("per_original_constraint_limits")
    limiting=case.get("first_limiting_constraints")
    demand(type(limits) is list and type(limiting) is list,
           "original full source uncertainty not recorded")
    if older.get("source_candidate_response") is None:
        demand(case.get("status")=="NO_QUALIFIED_FOURTH_RESPONSE"
               and older.get("clearance_bounds")==[]
               and limits==[] and limiting==[]
               and case.get("max_common_nominal_clearance_prefix") is None
               and case.get("original_constraints_checked")==0,
               "unqualified source response fabricated a later separation or limit")
        return False
    if older.get("status")!="CONDITIONAL_LOCAL_OUTGOING_SEPARATION":
        demand(case.get("status")=="ORIGINAL_SHORT_LOCAL_GEOMETRY_UNRESOLVED"
               and limits==[] and limiting==[]
               and case.get("max_common_nominal_clearance_prefix") is None,
               "unqualified source short-time separation promoted")
        return False
    source_original=older.get("clearance_bounds")
    demand(type(source_original) is list
           and len(source_original)==len(limits)==24
           and case.get("original_constraints_checked")==24,
           "all 24 original bounded corner/plane relationships required")
    times=[]
    for i,(source,record) in enumerate(zip(source_original,limits)):
        demand(type(source) is dict and type(record) is dict
               and record.get("source_plane")==source.get("surface")==KNOWN_PLANES[i//4]
               and record.get("source_corner_index")==source.get("corner_index")==i%4
               and record.get("source_starts_at_qualified_contact")==
               source.get("starts_at_qualified_contact")
               and record.get("original_gap_at_contact")==source.get("gap_at_candidate")
               and record.get("original_outgoing_normal_rate")==source.get("outgoing_normal_rate")
               and record.get("original_curvature_bound")==source.get("curvature_upper_bound")
               and source.get("accepted") is True
               and record.get("at_short_window") is True
               and type(record.get("at_declared_horizon")) is bool
               and type(record.get("constraint_restricts_declared_horizon")) is bool
               and record["at_declared_horizon"] is not record["constraint_restricts_declared_horizon"]
               and numeric(record.get("max_supported_prefix"))
               and BASELINE<=record["max_supported_prefix"]<=HORIZON,
               "original constraint, bounded prefix or model-only status changed")
        times.append(record["max_supported_prefix"])
    minimum=min(times)
    expected=[record for record in limits
              if record["constraint_restricts_declared_horizon"]
              and record["max_supported_prefix"]<=minimum+4e-7]
    demand(numeric(case.get("max_common_nominal_clearance_prefix"))
           and abs(case["max_common_nominal_clearance_prefix"]-minimum)<4e-7
           and case.get("first_limiting_constraints")==expected,
           "original limiting plane(s), source chronology or time changed")
    state=("NOMINAL_CLEARANCE_THROUGH_DECLARED_HORIZON"
           if minimum==HORIZON else
           "FIRST_SUFFICIENT_ENVELOPE_LIMIT_NOT_A_CONTACT")
    demand(case.get("status")==state,
           "loss of a sufficient inequality misreported as actual contact")
    return state=="FIRST_SUFFICIENT_ENVELOPE_LIMIT_NOT_A_CONTACT"


def carry(original,former,source_commit=PIN):
    demand(source_commit==PIN,"immutable original WORLD31 source pin changed")
    demand(type(original) is dict and original.get("schema")==SOURCE
           and original.get("angles")==list(ANGLES)
           and original.get("contact_features_solved")==0
           and original.get("fifth_impulses_computed")==0
           and original.get("real_material_measurements")==0
           and original.get("new_receivers_built")==0
           and original.get("new_engine_or_world") is False,
           "original WORLD31 result or physical boundary changed")
    demand(type(former) is dict and former.get("schema")==PRIOR
           and former.get("angles")==list(ANGLES)
           and former.get("real_material_impacts_witnessed")==0
           and former.get("selected_actual_fourth_impulses")==0
           and former.get("fifth_impulses_computed")==0,
           "original WORLD30 numerical source or material status changed")
    rows=original.get("cases")
    older=former.get("cases")
    demand(type(rows) is list and type(older) is list and len(rows)==len(older)==8,
           "all original source cases and no-response controls required")
    source_basis={"kind":"source-execution","source":"pinned original WORLD31 @"+PIN}
    hypothesis={"kind":"declared","source":"no reported limit of conservative separation evidence"}
    pages=[]
    limiting=0
    full=0
    missing=0
    for index,angle in enumerate(ANGLES):
        case,parent=rows[index],older[index]
        limited=verify_case(case,parent,angle)
        limiting+=int(limited)
        full+=int(case["status"]=="NOMINAL_CLEARANCE_THROUGH_DECLARED_HORIZON")
        missing+=int(case["status"]=="NO_QUALIFIED_FOURTH_RESPONSE")
        ops=[
            {"op":"introduce","id":"source-original-constraint-set",
             "state":{"source_angle":angle,"source30_sha256":digest(parent),
                      "source31_sha256":digest(case),
                      "physical_trajectory_witnessed":False},"basis":source_basis},
            {"op":"introduce","id":"conditional-fourth-response-model",
             "state":{"original_candidate_response":
                      deepcopy(parent["source_candidate_response"]),
                      "actual_fourth_contact_selected":False,
                      "post_limit_motion_permitted":False},"basis":source_basis},
            {"op":"connect","id":"original-envelope-evidence",
             "from":"source-original-constraint-set",
             "to":"conditional-fourth-response-model",
             "label":"original-24-constraint-sufficient-prefix",
             "state":{"declared_max_time":HORIZON,
                      "no_fifth_impulse":True},"basis":hypothesis},
            {"op":"observe","id":"source-short-local-clearance",
             "entity":"object","subject":"source-original-constraint-set",
             "reading":{"original_world30_status":parent["status"],
                        "source30_sha256":digest(parent),
                        "original_short_time_bounds":
                        deepcopy(parent["clearance_bounds"]),
                        "real_material_measurements":0},"basis":source_basis},
            {"op":"observe","id":"source-first-bound-limit",
             "entity":"object","subject":"conditional-fourth-response-model",
             "reading":{"original_world31_status":case["status"],
                        "source31_sha256":digest(case),
                        "individual_constraint_limits":
                        deepcopy(case["per_original_constraint_limits"]),
                        "first_limiting_constraints":
                        deepcopy(case["first_limiting_constraints"]),
                        "max_common_nominal_clearance_prefix":
                        case["max_common_nominal_clearance_prefix"],
                        "limit_is_not_fifth_contact":True},"basis":source_basis},
            {"op":"observe","id":"source-nonmaterial-boundary",
             "entity":"object","subject":"conditional-fourth-response-model",
             "reading":{"first_sufficiency_limit_detected":limited,
                        "real_contact_measured":False,
                        "fifth_impulse_selected":False,
                        "new_receiver_constructed":False,
                        "post_limit_motion_verified":False},"basis":source_basis},
            {"op":"compare","id":"first-source-limit-versus-none",
             "observation":"source-nonmaterial-boundary",
             "expected":{"first_sufficiency_limit_detected":False,
                         "real_contact_measured":False,
                         "fifth_impulse_selected":False,
                         "new_receiver_constructed":False,
                         "post_limit_motion_verified":False},
             "basis":hypothesis},
        ]
        plan={"schema":PLAN,
              "referent":f"WORLD31 / first original source limit / {angle}deg",
              "limits":{"objects":2,"relations":1,"steps":len(ops)},
              "steps":ops}
        receipt=run_plan(plan)
        independent=verify_receipt(receipt)
        demand(independent["valid"] and
               receipt["final"]["comparisons"]
               ["first-source-limit-versus-none"]["result"]==
               ("DIFFERENT" if limited else "MATCH"),
               "bounded A/B observation or independent receipt witness invalid")
        pages.append({"index":index,"angle":angle,
                      "source_status":case["status"],
                      "first_limit_reported":limited,
                      "receipt":receipt,"witness":independent})
    demand(limiting==original.get("cases_with_prior_envelope_limit")==3
           and full==original.get("cases_clear_through_horizon")==0
           and missing==original.get("without_qualified_response")==5
           and original.get("qualified_original_responses")==3,
           "original source outcome census changed")
    manifest={
        "pinned_original_commit":PIN,
        "source31_sha256":digest(original),
        "source30_sha256":digest(former),
        "ordered_receipts":[{"index":p["index"],"angle":p["angle"],
                             "head_hash":p["receipt"]["head_hash"]} for p in pages],
    }
    return {"schema":SCHEMA,"original_source_commit":PIN,
            "source_cases":8,"source_bound_limit_cases":limiting,
            "source_full_horizon_cases":full,
            "without_qualified_fourth_response":missing,
            "real_fifth_contacts":0,"fifth_impulses_selected":0,
            "authenticated_postlimit_movements":0,"new_receivers":0,
            "ledger_pages":pages,
            "ledger_witness":{"valid":all(p["witness"]["valid"] for p in pages),
                              "pages_verified":len(pages),
                              "steps_verified":sum(p["witness"]["steps_verified"] for p in pages),
                              "observations_recorded":sum(
                                  p["witness"]["observations_recorded"] for p in pages)},
            "manifest":manifest,"manifest_sha256":digest(manifest)}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--prior30",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(carry(load_json(args.native),load_json(args.prior30)),
                     sort_keys=True,indent=2))


if __name__=="__main__":
    main()
