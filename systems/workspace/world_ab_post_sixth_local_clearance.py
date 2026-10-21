"""WORLD41 — first chronological nominal clearance after unselected sixth response.

Original WORLD40 licenses only a *mathematical* sixth elastic normal response,
not a physical sixth event or an accepted seventh contact. Retain the exact
24x6 source world, both finite faces, original four perimeter planes and all
four original square corners. Search a finite .025 virtual-time interval under
the original conditional sixth free-flight model. Certify the selected corner
as strictly outgoing using a curvature-bound on its normal rate from t=0,
and independently bound all 23 other original corner-plane gaps over small
slabs by two endpoint Lipschitz neighborhoods. Refine only the first failed
chronological slab. A bound failure is UNKNOWN, never a seventh impact.
"""
from __future__ import annotations

from math import cos,sin,hypot,isfinite

from systems.workspace.world_ab_sixth_conditional_normal_law import (
    attempt as source40, SCHEMA as SOURCE40
)
from systems.workspace.world_ab_local_zero_gap_after_guard import attempt as source39
from systems.workspace.world_ab_whole_contact_configuration import attempt as source35
from systems.workspace.world_ab_post_fifth_contiguous_prefix import (
    model_at_conditional_fifth,original_planes
)
from systems.workspace.world_ab_third_contact import attempt as source21,ANGLES
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA="world-ab-post-conditional-sixth-first-contiguous-clearance/v1"
WINDOW=.025
BASE_SLABS=32
REFINE_DEPTH=8
POSITIVE_GUARD=1e-7
START_ZERO_TOL=1e-8
DEPART_RATE_GUARD=1e-5
RADIUS=hypot(HALF,HALF)
CORNERS=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def rd(x):
    return round(float(x),12)


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def corner(model,index,t):
    x,y=CORNERS[index]
    a=model["theta"]+model["spin"]*t
    c,s=cos(a),sin(a)
    lever=(x*c-y*s,x*s+y*c)
    return ((model["center"][0]+model["velocity"][0]*t+lever[0],
             model["center"][1]+model["velocity"][1]*t+lever[1]),
            (model["velocity"][0]-model["spin"]*lever[1],
             model["velocity"][1]+model["spin"]*lever[0]))


def source_model(angle,selected):
    fifth=source35(angle)
    world=source21(angle)
    fourth_model=model_at_conditional_fifth(fifth,world)
    t=source39(angle)["bracketed_first_zero_time"]
    sixth=selected["conditional_sixth_response"]
    if (sixth is None or not isfinite(t) or not 0<t<.25
        or sixth["selected_as_physical"] is not False):
        raise ValueError("original sixth source law and root not admitted")
    return ({
        "center":[fourth_model["center"][i]+fourth_model["velocity"][i]*t
                  for i in (0,1)],
        "theta":fourth_model["theta"]+fourth_model["spin"]*t,
        "velocity":list(sixth["outgoing_velocity"]),
        "spin":sixth["outgoing_spin"],
    },world)


def slab(model,planes,chosen,a,b):
    if not (0<=a<b<=WINDOW and isfinite(a) and isfinite(b)):
        raise ValueError("WORLD41 finite source interval violated")
    selected_plane,selected_corner=chosen
    chosen_entry=next(x for x in planes if x[0]==selected_plane)
    _,selected_n,selected_anchor,span=chosen_entry
    if span is None:
        raise ValueError("original selected face must remain finite")
    original_pos,original_vel=corner(model,selected_corner,0.)
    initial_gap=dot((original_pos[0]-selected_anchor[0],
                     original_pos[1]-selected_anchor[1]),selected_n)
    incoming_out=dot(original_vel,selected_n)
    rate_lower=incoming_out-model["spin"]**2*RADIUS*b
    departure_ok=(abs(initial_gap)<=START_ZERO_TOL
                  and rate_lower>DEPART_RATE_GUARD)
    rows=[]
    for name,n,anchor,span in planes:
        speed=abs(dot(model["velocity"],n))+abs(model["spin"])*RADIUS
        for index in range(4):
            pa,_=corner(model,index,a)
            pb,_=corner(model,index,b)
            start=dot((pa[0]-anchor[0],pa[1]-anchor[1]),n)
            end=dot((pb[0]-anchor[0],pb[1]-anchor[1]),n)
            surplus=start+end-speed*(b-a)-2*POSITIVE_GUARD
            chosen_now=name==selected_plane and index==selected_corner
            good=(departure_ok if chosen_now else
                  start>POSITIVE_GUARD and end>POSITIVE_GUARD and surplus>0)
            rows.append({
                "source_plane":name,"source_corner_index":index,
                "original_plane_finite":span is not None,
                "selected_original_sixth_contact":chosen_now,
                "starting_signed_normal_gap":rd(start),
                "ending_signed_normal_gap":rd(end),
                "normal_speed_lipschitz_limit":rd(speed),
                "endpoint_neighborhood_surplus":rd(surplus),
                "selected_contact_global_outward_rate_lower":(
                    rd(rate_lower) if chosen_now else None),
                "nominal_interval_supported":bool(good),
            })
    if len(rows)!=24 or sum(r["selected_original_sixth_contact"] for r in rows)!=1:
        raise ValueError("original source 24 corner-plane relationships changed")
    return {
        "start":rd(a),"end":rd(b),
        "selected_corner_initial_gap":rd(initial_gap),
        "selected_corner_initial_outgoing_normal_rate":rd(incoming_out),
        "selected_corner_global_outgoing_rate_lower":rd(rate_lower),
        "all_original_constraints_checked":24,
        "bounds":rows,
        "interval_nominally_supported":all(x["nominal_interval_supported"] for x in rows),
        "floating_point_not_formal_proof":True,
    }


def advance(model,planes,chosen,a,b,depth,records):
    entry=slab(model,planes,chosen,a,b)
    if entry["interval_nominally_supported"]:
        records.append(entry)
        return None
    if depth==REFINE_DEPTH:
        return {**entry,"status":"FIRST_POST_SIXTH_ORIGINAL_BOUND_UNRESOLVED",
                "failed_bound_is_not_seventh_contact":True}
    m=(a+b)/2
    return advance(model,planes,chosen,a,m,depth+1,records) or advance(
        model,planes,chosen,m,b,depth+1,records)


def attempt(angle):
    old=source40(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial40_schema":SOURCE40,
        "source_trial40_status":old["status"],
        "source_original_sixth_response":old["conditional_sixth_response"],
        "original_24_by_6_world":[24.,6.],
        "source_original_finite_faces":2,
        "source_original_world_perimeter_planes":4,
        "declared_post_sixth_window":WINDOW,
        "base_slab_count":BASE_SLABS,
        "maximum_refinement_depth":REFINE_DEPTH,
        "positive_clearance_guard":POSITIVE_GUARD,
        "selected_zero_gap_tolerance":START_ZERO_TOL,
        "departure_rate_guard":DEPART_RATE_GUARD,
        "model_source_only":True,
        "material_sixth_impact_observed":False,
        "sixth_response_selected_as_physical":False,
        "material_seventh_impact_observed":False,
        "seventh_impulse_computed":False,
        "new_receiver_constructed":False,
        "post_first_unknown_motion_admitted":False,
        "outward_rounded_interval_proof":False,
    }
    empty={
        "original_source_selected_face":None,
        "original_source_selected_corner":None,
        "original_conditional_sixth_pose":None,
        "source_planes":[],
        "supported_contiguous_prefix_end":None,
        "accepted_original_subintervals":[],
        "first_unknown_original_subinterval":None,
        "full_declared_window_supported":False,
    }
    if old["conditional_sixth_response"] is None:
        if old["status"] not in ("NO_SOURCE_SIXTH_CANDIDATE",
                                 "UNQUALIFIED_ORIGINAL_ZERO_GAP_PROBE",
                                 "ORIGINAL_SIXTH_CONFIGURATION_UNRESOLVED"):
            raise ValueError("original sixth response absent despite qualified source")
        return {**base,**empty,"status":"NO_SOURCE_SIXTH_RESPONSE"}
    if old["status"]!="CONDITIONAL_SIXTH_ELASTIC_RESPONSE_MATHEMATICALLY_QUALIFIED":
        raise ValueError("source conditional sixth law not fully qualified")
    model,ancestor=source_model(angle,old)
    if not all(isfinite(v) for v in (
        *model["center"],model["theta"],*model["velocity"],model["spin"])):
        raise ValueError("source sixth model nonfinite")
    planes=original_planes(ancestor,angle)
    chosen=(old["source_face"],old["source_corner"])
    if len(planes)!=6 or sum(z[0]==chosen[0] and z[3] is not None for z in planes)!=1:
        raise ValueError("source selected sixth face changed")
    accepted=[]
    limit=None
    for k in range(BASE_SLABS):
        a=WINDOW*k/BASE_SLABS
        b=WINDOW*(k+1)/BASE_SLABS
        limit=advance(model,planes,chosen,a,b,0,accepted)
        if limit is not None:break
    verified=accepted[-1]["end"] if accepted else 0.
    if limit is not None and abs(verified-limit["start"])>3e-9:
        raise ValueError("unverified original time skipped")
    return {
        **base,
        "status":("CONDITIONAL_SIXTH_FIRST_WINDOW_NOMINALLY_SEPARATED"
                  if limit is None else "FIRST_POST_SIXTH_CLEARANCE_BOUND_UNRESOLVED"),
        "original_source_selected_face":chosen[0],
        "original_source_selected_corner":chosen[1],
        "original_conditional_sixth_pose":{
            "center":[rd(x) for x in model["center"]],
            "theta":rd(model["theta"]),
            "outgoing_velocity":[rd(x) for x in model["velocity"]],
            "outgoing_spin":rd(model["spin"])},
        "source_planes":[x[0] for x in planes],
        "supported_contiguous_prefix_end":verified,
        "accepted_original_subintervals":accepted,
        "first_unknown_original_subinterval":limit,
        "full_declared_window_supported":limit is None,
    }


def run():
    cases=[attempt(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "eligible_conditional_sixth_models":sum(c["original_conditional_sixth_pose"] is not None for c in cases),
        "supported_full_windows":sum(c["full_declared_window_supported"] for c in cases),
        "first_unresolved_windows":sum(c["status"]=="FIRST_POST_SIXTH_CLEARANCE_BOUND_UNRESOLVED" for c in cases),
        "no_source_sixth_response_controls":sum(c["status"]=="NO_SOURCE_SIXTH_RESPONSE" for c in cases),
        "material_sixth_impacts":0,"material_seventh_impacts":0,
        "seventh_impulses":0,"new_receivers":0,"world_engine_constructed":False,
    }
