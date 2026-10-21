"""WORLD33 — finite, source-owned local clearance certificates after first limit.

WORLD32 reported three original first-envelope-limit poses where the two
finite source segments and the square remained separated. The old WORLD30
global Taylor bound had become insufficient, but that is not a fifth contact.

Evaluate the SAME original six supporting halfplanes with freshly computed
world-frame rotating corners at both ends of each short finite interval.
Each fixed-axis signed corner gap has Lipschitz constant at most
abs(center_velocity dot normal) + abs(spin) * square_radius.
Two positive endpoint-gap neighborhoods cover the whole interval when
gap(left)+gap(right) > L*delta+2*guard. This is a sufficient mathematical
clearance condition, NOT collision detection or a fifth impulse.

Refine failed intervals from left to right to a fixed depth, STOP at first
unverified subinterval; never extrapolate beyond that point or authenticate
material motion. No new geometry, receiver, model law or external measurement.
"""
from __future__ import annotations

from math import cos,sin,hypot,isfinite

from systems.workspace.world_ab_geometry_at_first_envelope_limit import (
    attempt as source32, SCHEMA as SOURCE32
)
from systems.workspace.world_ab_first_finite_response_qualification import attempt as source29
from systems.workspace.world_ab_third_contact import attempt as source21,ANGLES
from systems.workspace.world_ab_first_post_third_candidate import surfaces
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA="world-ab-local-recomputed-halfplane-prefix/v1"
HORIZON=.25
MAX_NEW_WINDOW=.05
BASE_INTERVALS=64
REFINEMENT_DEPTH=9
GUARD=1e-7
SQUARE=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
RADIUS=hypot(HALF,HALF)


def rd(x):
    return round(float(x),12)


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def world_corners(model,t):
    theta=model["theta"]+model["spin"]*t
    c,s=cos(theta),sin(theta)
    x=model["center"][0]+model["velocity"][0]*t
    y=model["center"][1]+model["velocity"][1]*t
    return [(x+c*u-s*v,y+s*u+c*v) for u,v in SQUARE]


def source_planes(original,angle):
    src=list(surfaces(original,angle))
    if len(src)!=6 or [x[0] for x in src]!=[
        "original_finite_face","motion_derived_receiver","world_left",
        "world_right","world_bottom","world_top"]:
        raise ValueError("original two source faces/four perimeter planes changed")
    return [(name,tuple(normal),tuple(anchor),span)
            for name,normal,anchor,span in src]


def halfplane_gap(corners,normal,anchor):
    return min(dot((p[0]-anchor[0],p[1]-anchor[1]),normal)
               for p in corners)


def bound_one_interval(model,planes,left,right):
    if not (0<=left<right<=HORIZON and isfinite(left) and isfinite(right)):
        raise ValueError("outside finite original observation horizon")
    a=world_corners(model,left)
    b=world_corners(model,right)
    entries=[]
    for name,n,anchor,span in planes:
        start=halfplane_gap(a,n,anchor)
        end=halfplane_gap(b,n,anchor)
        speed=abs(dot(model["velocity"],n))+abs(model["spin"])*RADIUS
        surplus=start+end-speed*(right-left)-2*GUARD
        good=start>GUARD and end>GUARD and surplus>0
        entries.append({
            "source_plane":name,
            "original_plane_is_finite_segment":span is not None,
            "start_min_signed_gap":rd(start),
            "end_min_signed_gap":rd(end),
            "fixed_axis_speed_upper_bound":rd(speed),
            "endpoint_neighborhood_surplus":rd(surplus),
            "interval_supported":bool(good),
        })
    return {
        "start":rd(left),"end":rd(right),
        "original_constraints_checked":len(entries),
        "source_plane_bounds":entries,
        "nominally_clear_through_interval":all(r["interval_supported"] for r in entries),
        "floating_point_not_formal_certificate":True,
    }


def advance(model,planes,left,right,depth,verified,limit):
    # Chronological DFS: carry only the verified prefix; never record any
    # segment after the first unresolved leaf as supported movement.
    record=bound_one_interval(model,planes,left,right)
    if record["nominally_clear_through_interval"]:
        verified.append(record)
        return True
    if depth>=REFINEMENT_DEPTH:
        limit.append({**record,"status":"FIRST_UNRESOLVED_LOCAL_SUBINTERVAL",
                      "failure_not_a_collision":True})
        return False
    middle=(left+right)/2
    if not advance(model,planes,left,middle,depth+1,verified,limit):
        return False
    return advance(model,planes,middle,right,depth+1,verified,limit)


def attempt(angle):
    before=source32(angle)
    earlier=source29(angle)
    ancestor=source21(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial32_schema":SOURCE32,
        "source_trial32_status":before["status"],
        "source_first_limit_time":before["source_first_nominal_limit"],
        "original_first_limit_geometry":before,
        "source_qualified_fourth_response":earlier["conditional_fourth_response"],
        "original_24_by_6_world":[24.,6.],
        "original_two_static_finite_segments":True,
        "world_perimeter_plane_count":4,
        "declared_original_horizon":HORIZON,
        "maximum_new_window":MAX_NEW_WINDOW,
        "base_intervals":BASE_INTERVALS,
        "max_subdivision_depth":REFINEMENT_DEPTH,
        "positive_clearance_guard":GUARD,
        "conditional_ballistic_pose_only":True,
        "numerical_non_outward_rounded":True,
        "fifth_contact_witnessed":False,
        "fifth_impulse_computed":False,
        "physical_motion_authenticated":False,
        "post_unknown_continuation_permitted":False,
        "new_receiver_created":False,
    }
    if earlier["conditional_fourth_response"] is None:
        return {**base,"status":"NO_QUALIFIED_FOURTH_RESPONSE",
                "source_recomputed_plane_names":[],
                "attempted_end_time":None,
                "supported_prefix_end_time":None,
                "certified_subintervals":[],
                "first_unknown_subinterval":None,
                "new_window_fully_nominally_supported":False}
    if before["status"]!="CONDITIONAL_FINITE_SHAPES_SEPARATED_AT_EVIDENCE_LIMIT":
        return {**base,"status":"FIRST_LIMIT_GEOMETRY_NOT_CONFIRMED_SEPARATED",
                "source_recomputed_plane_names":[],
                "attempted_end_time":None,
                "supported_prefix_end_time":None,
                "certified_subintervals":[],
                "first_unknown_subinterval":None,
                "new_window_fully_nominally_supported":False}
    t0=before["source_first_nominal_limit"]
    t1=min(HORIZON,t0+MAX_NEW_WINDOW)
    if not (isfinite(t0) and .008<=t0<t1<=HORIZON):
        raise ValueError("invalid source first-limit candidate or horizon")
    feature=earlier["qualifying_source_feature"]
    response=earlier["conditional_fourth_response"]
    model={"center":feature["contact_center"],
           "theta":feature["contact_angle"],
           "velocity":response["outgoing_velocity"],
           "spin":response["outgoing_spin"]}
    planes=source_planes(ancestor,angle)
    verified=[]
    limit=[]
    for i in range(BASE_INTERVALS):
        a=t0+(t1-t0)*i/BASE_INTERVALS
        b=t0+(t1-t0)*(i+1)/BASE_INTERVALS
        if not advance(model,planes,a,b,0,verified,limit):
            break
    end=verified[-1]["end"] if verified else rd(t0)
    full=len(limit)==0
    if verified and not full:
        if abs(end-limit[0]["start"])>1e-8:
            raise ValueError("unverified subinterval moved out of chronological prefix")
    state=("FULL_NEW_WINDOW_NOMINALLY_SEPARATED"
           if full else "FIRST_LOCAL_HALFPLANE_BOUND_UNRESOLVED")
    return {**base,"status":state,
            "source_recomputed_plane_names":[z[0] for z in planes],
            "attempted_end_time":rd(t1),
            "supported_prefix_end_time":end,
            "certified_subintervals":verified,
            "first_unknown_subinterval":limit[0] if limit else None,
            "new_window_fully_nominally_supported":full}


def run():
    cases=[attempt(a) for a in ANGLES]
    return {"schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
            "original_first_limit_cases":sum(
                c["source_first_limit_time"] is not None for c in cases),
            "full_new_window_supported_cases":sum(
                c["status"]=="FULL_NEW_WINDOW_NOMINALLY_SEPARATED" for c in cases),
            "locally_unresolved_cases":sum(
                c["status"]=="FIRST_LOCAL_HALFPLANE_BOUND_UNRESOLVED" for c in cases),
            "without_original_response":sum(
                c["status"]=="NO_QUALIFIED_FOURTH_RESPONSE" for c in cases),
            "original_world_faces_added":0,
            "fifth_impulses_selected":0,
            "physical_measurements":0,
            "new_engine_or_world":False}
