"""WORLD37 — first contiguous source clearance prefix after WORLD36.

Only WORLD36's qualified short post-fifth interval authorizes asking whether
the SAME original source's conditional fifth-response free-flight model is
separated after t=.008. Check a further <=.05 virtual units, capped at .25
after fifth. Every original source vertex/plane relationship gets a fixed-
world-axis Lipschitz neighborhood bound over each finite slab. Failed
sufficiency is UNKNOWN, not sixth contact. Stop at the very first unsupported
subinterval; never skip time or propose a sixth impulse.

This is nominal floating-point mathematical counterfactual, not hardware
motion or outward-rounded real-arithmetic certification.
"""
from __future__ import annotations

from math import sin, cos, hypot, isfinite
from systems.workspace.world_ab_post_fifth_local_clearance import (
    attempt as trial36, SCHEMA as SOURCE36, WINDOW as START
)
from systems.workspace.world_ab_whole_contact_configuration import attempt as trial35
from systems.workspace.world_ab_first_finite_response_qualification import attempt as trial29
from systems.workspace.world_ab_third_contact import attempt as trial21, ANGLES
from systems.workspace.world_ab_first_post_third_candidate import surfaces
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA="world-ab-post-fifth-contiguous-recomputed-clearance-prefix/v1"
HORIZON=.25
NEW_WINDOW=.05
BASE_INTERVALS=32
REFINEMENT_DEPTH=8
GUARD=1e-7
RADIUS=hypot(HALF,HALF)
CORNERS=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
PLANE_NAMES=("original_finite_face","motion_derived_receiver",
             "world_left","world_right","world_bottom","world_top")


def rd(x):
    return round(float(x),12)


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def model_at_conditional_fifth(prior,original):
    fourth=trial29(prior["angle"])
    earlier=fourth["qualifying_source_feature"]
    response=fourth["conditional_fourth_response"]
    fifth=prior["conditional_fifth_response"]
    t=prior["candidate_virtual_time"]
    if (earlier is None or response is None or fifth is None
        or not (0<t<HORIZON) or fifth["selected_as_physical"] is not False):
        raise ValueError("WORLD37 source-qualified hypothetical fifth model missing")
    result={
        "center":[earlier["contact_center"][i]+response["outgoing_velocity"][i]*t
                  for i in (0,1)],
        "theta":earlier["contact_angle"]+response["outgoing_spin"]*t,
        "velocity":list(fifth["outgoing_velocity"]),
        "spin":fifth["outgoing_spin"]
    }
    if any(not isfinite(v) for v in (
        *result["center"],result["theta"],*result["velocity"],result["spin"]
    )):
        raise ValueError("original conditional fifth pose not finite")
    return result


def original_planes(ancestor,angle):
    planes=[(name,tuple(n),tuple(anchor),span)
            for name,n,anchor,span in surfaces(ancestor,angle)]
    if ([x[0] for x in planes]!=list(PLANE_NAMES)
        or [x[3] is not None for x in planes] != [True,True,False,False,False,False]):
        raise ValueError("WORLD37 original six planes changed")
    return planes


def positions(model,t):
    theta=model["theta"]+model["spin"]*t
    c,s=cos(theta),sin(theta)
    center=(model["center"][0]+model["velocity"][0]*t,
            model["center"][1]+model["velocity"][1]*t)
    return [(center[0]+c*x-s*y,center[1]+s*x+c*y) for x,y in CORNERS]


def interval(model,planes,a,b):
    if not (isfinite(a) and isfinite(b) and START<=a<b<=HORIZON):
        raise ValueError("nonfinite or out-of-window source interval")
    pa,pb=positions(model,a),positions(model,b)
    rows=[]
    for name,n,anchor,span in planes:
        speed=abs(dot(model["velocity"],n))+abs(model["spin"])*RADIUS
        for i in range(4):
            g0=dot((pa[i][0]-anchor[0],pa[i][1]-anchor[1]),n)
            g1=dot((pb[i][0]-anchor[0],pb[i][1]-anchor[1]),n)
            surplus=g0+g1-speed*(b-a)-2*GUARD
            supported=g0>GUARD and g1>GUARD and surplus>0
            rows.append({
                "source_plane":name, "source_corner_index":i,
                "source_plane_is_finite":span is not None,
                "left_gap":rd(g0),"right_gap":rd(g1),
                "normal_speed_upper_bound":rd(speed),
                "two_endpoint_neighborhood_surplus":rd(surplus),
                "interval_supported":bool(supported),
            })
    return {
        "left":rd(a),"right":rd(b),
        "original_plane_corner_constraints":24,
        "source_bounds":rows,
        "interval_nominally_separated":all(r["interval_supported"] for r in rows),
        "floating_point_not_outward_rounded":True
    }


def advance(model,planes,left,right,depth,accepted):
    record=interval(model,planes,left,right)
    if record["interval_nominally_separated"]:
        accepted.append(record)
        return None
    if depth==REFINEMENT_DEPTH:
        return {**record,"status":"FIRST_SOURCE_CLEARANCE_BOUND_UNRESOLVED",
                "bound_failure_is_not_collision":True}
    m=(left+right)/2
    return (advance(model,planes,left,m,depth+1,accepted)
            or advance(model,planes,m,right,depth+1,accepted))


def attempt(angle):
    prev=trial36(angle)
    source=trial35(angle)
    ancestor=trial21(angle)
    baseline={
        "schema":SCHEMA,"angle":float(angle),
        "original_trial36_schema":SOURCE36,
        "original_trial36_status":prev["status"],
        "original_trial36_case":prev,
        "original_trial35_status":source["status"],
        "original_source_fifth_response":source["conditional_fifth_response"],
        "original_24_by_6_world":[24.,6.],
        "original_finite_source_faces":2,
        "original_perimeter_planes":4,
        "source_original_short_window":START,
        "attempted_additional_window":NEW_WINDOW,
        "declared_max_post_fifth_horizon":HORIZON,
        "base_interval_count":BASE_INTERVALS,
        "maximum_refinement_depth":REFINEMENT_DEPTH,
        "positive_gap_guard":GUARD,
        "source_model_only":True,
        "material_fifth_impact_witnessed":False,
        "physical_fifth_impulse_selected":False,
        "sixth_contact_observed":False,
        "sixth_impulse_computed":False,
        "new_receiver_constructed":False,
        "post_first_unknown_motion_approved":False,
        "exact_interval_arithmetic_certificate":False,
    }
    empty={
        "source_plane_names":[],
        "initial_clearance_time":None,
        "attempted_end_time":None,
        "supported_prefix_end":None,
        "supported_source_subintervals":[],
        "first_unsupported_subinterval":None,
        "full_new_interval_supported":False
    }
    if source["conditional_fifth_response"] is None:
        if prev["nominal_clearance_covered"] is not False:
            raise ValueError("no original fifth response but next interval accepted")
        return {**baseline,**empty,"status":"NO_QUALIFIED_SOURCE_FIFTH_RESPONSE"}
    if (prev["status"]!="CONDITIONAL_FIFTH_LOCAL_CLEARANCE_NOMINALLY_SUPPORTED"
        or prev["supported_original_constraints"]!=24):
        return {**baseline,**empty,"status":"PREVIOUS_SHORT_CLEARANCE_NOT_SUPPORTED"}
    start=START
    end=min(HORIZON,start+NEW_WINDOW)
    model=model_at_conditional_fifth(source,ancestor)
    planes=original_planes(ancestor,angle)
    accepted=[]
    first=None
    for i in range(BASE_INTERVALS):
        a=start+(end-start)*i/BASE_INTERVALS
        b=start+(end-start)*(i+1)/BASE_INTERVALS
        first=advance(model,planes,a,b,0,accepted)
        if first is not None:break
    finish=accepted[-1]["right"] if accepted else rd(start)
    if first is not None and abs(finish-first["left"])>3e-9:
        raise ValueError("noncontiguous original verified source prefix")
    full=first is None
    return {**baseline,
            "status":("EXTENDED_CONDITIONAL_FIFTH_MODEL_CLEARANCE_SUPPORTED"
                      if full else "FIRST_POST_FIFTH_LOCAL_BOUND_UNRESOLVED"),
            "source_plane_names":[p[0] for p in planes],
            "initial_clearance_time":start,
            "attempted_end_time":rd(end),
            "supported_prefix_end":finish,
            "supported_source_subintervals":accepted,
            "first_unsupported_subinterval":first,
            "full_new_interval_supported":full}


def run():
    cases=[attempt(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "source_qualified_post_fifth_cases":sum(c["initial_clearance_time"] is not None for c in cases),
        "complete_new_window_cases":sum(c["status"]=="EXTENDED_CONDITIONAL_FIFTH_MODEL_CLEARANCE_SUPPORTED" for c in cases),
        "first_unknown_window_cases":sum(c["status"]=="FIRST_POST_FIFTH_LOCAL_BOUND_UNRESOLVED" for c in cases),
        "no_original_fifth_response_controls":sum(c["status"]=="NO_QUALIFIED_SOURCE_FIFTH_RESPONSE" for c in cases),
        "material_fifth_impacts":0,"material_sixth_contacts":0,
        "sixth_impulses":0,"new_receivers":0,"general_world_engine":False
    }
