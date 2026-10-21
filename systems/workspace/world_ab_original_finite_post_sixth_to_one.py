"""WORLD45 — independent next finite prefix after WORLD44's admitted .75.

Continue ONLY the same unselected sixth elastic response, unchanged two
original finite source segments, four original 24x6 world perimeter planes,
and original square. Try adjacent, bounded original source horizon [.75,1.00].
Each accepted subinterval requires a fixed separating SAT axis for each
finite segment AND a positive normal-gap certificate for each world edge.
Stop at the first unsupported leaf; failure is NOT a seventh collision.
"""
from __future__ import annotations

from functools import lru_cache
from math import hypot,isfinite

from systems.workspace.world_ab_finite_post_sixth_source_separation import (
    square,segments_and_world,face_witness,perimeter_witness,
    RADIUS,GUARD
)
from systems.workspace.world_ab_next_finite_post_sixth_prefix import (
    attempt as trial44, SCHEMA as SOURCE44
)
from systems.workspace.world_ab_post_sixth_local_clearance import source_model
from systems.workspace.world_ab_sixth_conditional_normal_law import attempt as trial40
from systems.workspace.world_ab_post_fifth_contiguous_prefix import original_planes
from systems.workspace.world_ab_third_contact import ANGLES

SCHEMA="world-ab-original-finite-post-sixth-prefix-to-one/v1"
START=.75
END=1.00
BASE=64
REFINE=8


def rd(x):return round(float(x),12)


def checked_slab(h,faces,world,a,b):
    if not (START<=a<b<=END):
        raise ValueError("WORLD45 interval escapes declared finite source horizon")
    p=square(h,a);q=square(h,b)
    speed=hypot(*h["velocity"])+abs(h["spin"])*RADIUS
    if not isfinite(speed):raise ValueError("original source speed nonfinite")
    finite=[face_witness(h,face,p,q,a,b,speed) for face in faces]
    perimeters=[perimeter_witness(name,n,anchor,p,q,b-a,speed)
                for name,n,anchor in world]
    supported=(len(finite)==2 and len(perimeters)==4 and
               all(x["separates_entire_subinterval"] for x in finite) and
               all(x["perimeter_clear_entire_subinterval"] for x in perimeters))
    return {
        "start":rd(a),"end":rd(b),
        "original_square_vertex_count":4,
        "original_finite_faces":[f[0] for f in faces],
        "original_world_perimeters":[w[0] for w in world],
        "vertex_speed_lipschitz_bound":rd(speed),
        "source_finite_segment_SAT_witnesses":finite,
        "source_world_perimeter_witnesses":perimeters,
        "finite_interval_separation_supported":bool(supported),
        "failed_bound_is_seventh_impact":False,
        "numerical_not_outward_rounded":True,
    }


def first_unsupported(h,faces,world,a,b,depth,accepted):
    result=checked_slab(h,faces,world,a,b)
    if result["finite_interval_separation_supported"]:
        accepted.append(result)
        return None
    if depth==REFINE:
        return {**result,
                "status":"FIRST_ORIGINAL_FINITE_SEPARATION_BOUND_UNRESOLVED",
                "physical_seventh_contact_measured":False}
    midpoint=(a+b)/2
    return (first_unsupported(h,faces,world,a,midpoint,depth+1,accepted) or
            first_unsupported(h,faces,world,midpoint,b,depth+1,accepted))


@lru_cache(maxsize=16)
def attempt(angle):
    prior=trial44(angle)
    parent40=trial40(angle)
    common={
        "schema":SCHEMA,
        "angle":float(angle),
        "original_trial44_schema":SOURCE44,
        "original_trial44_status":prior["status"],
        "original_trial44_supported_endpoint":prior["supported_finite_prefix_end"],
        "world_dimensions":[24.,6.],
        "original_static_finite_segment_count":2,
        "original_world_perimeter_count":4,
        "original_rotating_square_corner_count":4,
        "window_start":START,"window_end":END,
        "base_slab_count":BASE,"max_bisection_depth":REFINE,
        "positive_clearance_guard":GUARD,
        "sixth_impulse_unselected_model_only":True,
        "physical_sixth_contact_measured":False,
        "physical_seventh_contact_measured":False,
        "seventh_impulse_selected":False,
        "new_receiver_constructed":False,
        "source_motion_after_first_unknown_admitted":False,
        "formal_outward_rounded_interval_proof":False,
    }
    empty={
        "conditional_sixth_pose":None,
        "source_finite_segments":[],
        "source_world_perimeter_names":[],
        "accepted_original_intervals":[],
        "first_unknown_original_interval":None,
        "supported_finite_prefix_end":None,
        "full_declared_finite_window_supported":False,
    }
    if parent40["conditional_sixth_response"] is None:
        if prior["status"]!="NO_ADMITTED_SIXTH_RESPONSE":
            raise ValueError("original sixth controls changed")
        return {**common,**empty,"status":"NO_ADMITTED_SIXTH_RESPONSE"}
    if (prior["status"]!="ORIGINAL_FINITE_SEPARATION_THROUGH_POST_SIXTH_0_75"
        or prior["full_declared_finite_window_supported"] is not True
        or abs(prior["supported_finite_prefix_end"]-START)>1e-9):
        return {**common,**empty,"status":"SOURCE_T44_FINITE_WINDOW_UNRESOLVED"}
    h,ancestor=source_model(angle,parent40)
    faces,world=segments_and_world(original_planes(ancestor,angle))
    if len(faces)!=2 or len(world)!=4 or any(
        not isfinite(x) for x in (*h["center"],h["theta"],*h["velocity"],h["spin"])):
        raise ValueError("original WORLD finite geometry/movement invalid")
    accepted=[]
    unknown=None
    for i in range(BASE):
        a=START+(END-START)*i/BASE
        b=START+(END-START)*(i+1)/BASE
        unknown=first_unsupported(h,faces,world,a,b,0,accepted)
        if unknown is not None:break
    prefix=accepted[-1]["end"] if accepted else START
    if unknown is not None and abs(prefix-unknown["start"])>3e-9:
        raise ValueError("finite source skipped first unsupported time")
    return {
        **common,
        "status":("ORIGINAL_FINITE_SEPARATION_THROUGH_POST_SIXTH_1_00"
                  if unknown is None else "FIRST_POST_SIXTH_FINITE_UNKNOWN_IN_0_75_TO_1_00"),
        "conditional_sixth_pose":{
            "center":[rd(x) for x in h["center"]],
            "theta":rd(h["theta"]),
            "outgoing_velocity":[rd(x) for x in h["velocity"]],
            "outgoing_spin":rd(h["spin"])},
        "source_finite_segments":[
            {"name":n,"endpoints":[[rd(z) for z in end] for end in ends]}
            for n,_,ends in faces],
        "source_world_perimeter_names":[name for name,_,_ in world],
        "accepted_original_intervals":accepted,
        "first_unknown_original_interval":unknown,
        "supported_finite_prefix_end":prefix,
        "full_declared_finite_window_supported":unknown is None,
    }


def run():
    cases=[attempt(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "admitted_original_finite_sources":sum(
            z["conditional_sixth_pose"] is not None for z in cases),
        "fully_supported_1_00_horizons":sum(
            z["full_declared_finite_window_supported"] for z in cases),
        "first_unknown_0_75_1_00_cases":sum(
            z["status"]=="FIRST_POST_SIXTH_FINITE_UNKNOWN_IN_0_75_TO_1_00" for z in cases),
        "prior_original_source_unresolved":sum(
            z["status"]=="SOURCE_T44_FINITE_WINDOW_UNRESOLVED" for z in cases),
        "inactive_source_controls":sum(
            z["status"]=="NO_ADMITTED_SIXTH_RESPONSE" for z in cases),
        "actual_seventh_impacts":0,
        "calculated_seventh_impulses":0,
        "new_receivers":0,
        "new_engine":False
    }
