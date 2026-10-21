"""WORLD30: test source-qualified hypothetical response for SHORT local separation.

The original WORLD29 source owns the unique finite contact and a restitution-1
frictionless *candidate* response. WORLD30 changes no contact law, no original
face, and no world. For at most 0.008 virtual-time units after that proposed
response, apply conservative normal-distance Taylor bounds on the same four
corners against the same two static source supporting lines and four WORLD
perimeter planes.

A positive bound suffices for nominal local clearance of those halfplanes;
a failed bound remains UNKNOWN. Source finite-face outside-line cases cannot
be upgraded to physical interpenetration. No response is selected as actual,
no collision later than the candidate is computed, and no receiver is built.
"""
from __future__ import annotations

from math import cos,sin,hypot,isfinite
from systems.workspace.world_ab_first_finite_response_qualification import (
    attempt as prior29,SCHEMA as SOURCE29
)
from systems.workspace.world_ab_third_contact import attempt as prior21,ANGLES
from systems.workspace.world_ab_first_post_third_candidate import surfaces
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA="world-ab-local-clearance-after-conditional-fourth-response/v1"
WINDOW=.008
TOL=3e-6
MARGIN=1e-5
CORNERS=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def rd(x):
    return round(float(x),10)


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def rotate(x,theta):
    co,si=cos(theta),sin(theta)
    return (x[0]*co-x[1]*si,x[0]*si+x[1]*co)


def corner_certificate(center,theta,velocity,spin,corner,normal,anchor,touch):
    r=rotate(CORNERS[corner],theta)
    point=(center[0]+r[0],center[1]+r[1])
    gap=dot((point[0]-anchor[0],point[1]-anchor[1]),normal)
    velocity_at_corner=(velocity[0]-spin*r[1],velocity[1]+spin*r[0])
    rate=dot(velocity_at_corner,normal)
    curvature=spin*spin*hypot(HALF,HALF)
    ending_lower=gap+rate*WINDOW-curvature*WINDOW*WINDOW/2
    rate_lower=rate-curvature*WINDOW
    if touch:
        accepted=abs(gap)<=TOL and rate_lower>MARGIN
        reason=("TOUCHING_VERTEX_DEPARTURE_LOWER_RATE" if accepted
                else "TOUCHING_VERTEX_OUTGOING_SEPARATION_UNRESOLVED")
        conservative=rate_lower
    else:
        conservative=min(gap,ending_lower)
        accepted=conservative>MARGIN
        reason=("OTHER_VERTEX_POSITIVE_GAP_BOUND" if accepted
                else "NONTOUCHING_CORNER_CLEARANCE_UNRESOLVED")
    return {
        "corner_index":corner,
        "gap_at_candidate":rd(gap),
        "outgoing_normal_rate":rd(rate),
        "curvature_upper_bound":rd(curvature),
        "end_gap_lower_bound":rd(ending_lower),
        "normal_rate_lower_bound":rd(rate_lower),
        "conservative_bound":rd(conservative),
        "starts_at_qualified_contact":bool(touch),
        "accepted":bool(accepted),
        "classification":reason,
        "original_finite_source_not_real_hardware":True,
    }


def attempt(angle):
    source=prior29(angle)
    ancestor=prior21(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial29_schema":SOURCE29,
        "source_trial29_status":source["status"],
        "source_original_third_impulse":ancestor["third_impulse"],
        "source_candidate_contact":source["qualifying_source_feature"],
        "source_candidate_response":source["conditional_fourth_response"],
        "original_world":[24.,6.],
        "original_finite_source_faces":2,
        "four_original_world_boundaries":4,
        "post_candidate_horizon":WINDOW,
        "nominal_free_flight_model_only":True,
        "actual_contact_selected":False,
        "real_material_response_witnessed":False,
        "post_candidate_continuous_motion_authenticated":False,
        "formally_outward_rounded_numeric_certificate":False,
        "new_receiver_built":False,
        "fifth_impulse_computed":False,
    }
    if source["conditional_fourth_response"] is None:
        return {**base,
                "status":"NO_QUALIFIED_SOURCE_FOURTH_RESPONSE",
                "clearance_bounds":[],
                "accepted_bounds":0,
                "unresolved_bounds":0,
                "nominal_local_clearance_admitted":False}
    if source["status"]!="CONDITIONAL_SINGLE_VERTEX_NORMAL_RESPONSE_CANDIDATE":
        raise ValueError("source candidate response without accepted contact qualification")
    feature=source["qualifying_source_feature"]
    response=source["conditional_fourth_response"]
    center=feature["contact_center"]
    theta=feature["contact_angle"]
    v=tuple(response["outgoing_velocity"])
    w=response["outgoing_spin"]
    touch_name=feature["source_face"]
    touch_index=feature["source_vertex_index"]
    if (not all(isfinite(x) for x in (*center,theta,*v,w))
        or response["response_selected_as_actual"] is not False
        or response["materially_witnessed"] is not False):
        raise ValueError("source physical contact state promoted")
    all_bounds=[]
    for name,n,anchor,span in surfaces(ancestor,angle):
        normal=tuple(n)
        for i in range(4):
            touch=name==touch_name and i==touch_index
            line=corner_certificate(center,theta,v,w,i,normal,anchor,touch)
            all_bounds.append({"surface":name,**line})
    if len(all_bounds)!=24 or sum(z["starts_at_qualified_contact"] for z in all_bounds)!=1:
        raise ValueError("source finite/contact or WORLD constraints replaced")
    good=sum(c["accepted"] for c in all_bounds)
    status=("CONDITIONAL_LOCAL_OUTGOING_SEPARATION" if good==len(all_bounds)
            else "POST_CANDIDATE_LOCAL_GEOMETRY_UNRESOLVED")
    return {**base,
            "status":status,"clearance_bounds":all_bounds,
            "accepted_bounds":good,
            "unresolved_bounds":len(all_bounds)-good,
            "nominal_local_clearance_admitted":good==len(all_bounds)}


def run():
    cases=[attempt(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "source_qualified_fourth_candidates":sum(
            x["source_candidate_response"] is not None for x in cases),
        "locally_separated_conditional_candidates":sum(
            x["status"]=="CONDITIONAL_LOCAL_OUTGOING_SEPARATION" for x in cases),
        "post_candidate_geometry_unresolved":sum(
            x["status"]=="POST_CANDIDATE_LOCAL_GEOMETRY_UNRESOLVED" for x in cases),
        "no_qualified_source_response":sum(
            x["status"]=="NO_QUALIFIED_SOURCE_FOURTH_RESPONSE" for x in cases),
        "real_material_impacts_witnessed":0,
        "selected_actual_fourth_impulses":0,
        "fifth_impulses_computed":0,
        "new_receivers_constructed":0,
        "new_physics_engine":False,
    }
