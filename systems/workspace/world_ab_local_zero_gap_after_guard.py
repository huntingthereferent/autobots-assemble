"""WORLD39: source-owned conditional zero-gap probe after WORLD38's first guard.

A Trial38 guard value is *not* contact. Only the one original source
finite-face interior inward-guard case may enter this next bounded
mathematical probe. Look at a tiny local extension of the same hypothetical
fifth-response model, without admitting source continuation or a real sixth
impact. Verify all 24 original supporting gaps over that slab and keep the
other source finite face/perimeter separated. Do NOT calculate an impulse.
"""
from __future__ import annotations

from math import cos,sin,hypot,isfinite
from systems.workspace.world_ab_first_post_fifth_guard_limit import attempt as previous, SCHEMA as SOURCE38
from systems.workspace.world_ab_post_fifth_contiguous_prefix import model_at_conditional_fifth,original_planes
from systems.workspace.world_ab_whole_contact_configuration import attempt as previous35
from systems.workspace.world_ab_third_contact import attempt as original21,ANGLES
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA="world-ab-first-local-original-finite-zero-gap-probe/v1"
PROBE_WIDTH=1e-4
GUARD=1e-7
ROOT_TOL=1e-10
OTHER_GAP_GUARD=1e-6
INWARD_GUARD=1e-5
HORIZON=.25
RADIUS=hypot(HALF,HALF)
CORNERS=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def rd(x):return round(float(x),12)

def dot(a,b):return a[0]*b[0]+a[1]*b[1]

def location(model,index,t):
    x,y=CORNERS[index]
    theta=model["theta"]+model["spin"]*t
    c,s=cos(theta),sin(theta)
    lever=(x*c-y*s,x*s+y*c)
    pos=(model["center"][0]+model["velocity"][0]*t+lever[0],
         model["center"][1]+model["velocity"][1]*t+lever[1])
    vel=(model["velocity"][0]-model["spin"]*lever[1],
         model["velocity"][1]+model["spin"]*lever[0])
    return pos,vel

def plane_gap(model,index,t,normal,anchor):
    p,_=location(model,index,t)
    return dot((p[0]-anchor[0],p[1]-anchor[1]),normal)

def attempt(angle):
    source=previous(angle)
    fifth=previous35(angle)
    ancestor=original21(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),"source_trial38_schema":SOURCE38,
        "source_trial38_status":source["status"],
        "source_original_guard_feature":source["first_source_guard_limit"],
        "source_original_24_by_6_world":[24.,6.],
        "source_original_finite_faces":2,"source_original_perimeter_planes":4,
        "maximum_local_probe_width":PROBE_WIDTH,
        "source_guard_threshold":GUARD,"other_original_gap_guard":OTHER_GAP_GUARD,
        "source_model_counterfactual_only":True,
        "source_clearance_proven_only_to_guard":True,
        "new_interval_not_admitted_continuation":True,
        "real_sixth_contact_observed":False,
        "physical_sixth_impulse_selected":False,
        "hypothetical_sixth_impulse_calculated":False,
        "post_sixth_model_motion_solved":False,
        "new_receiver_constructed":False,
        "formal_interval_arithmetic_proof":False,
    }
    empty={
        "selected_source_face":None,"selected_corner":None,
        "guard_time":None,"local_probe_endpoint":None,
        "bracketed_first_zero_time":None,"first_zero_contact_model_position":None,
        "tangent_inside_finite_face":False,
        "source_normal_rate_at_zero":None,
        "selected_inward_rate_upper_bound":None,
        "source_24_plane_corner_probe_records":[],
        "all_23_other_original_constraints_strictly_separated":False,
        "source_contact_geometry_qualified":False,
    }
    if fifth["conditional_fifth_response"] is None:
        if source["status"]!="NO_SOURCE_FIFTH_RESPONSE":
            raise ValueError("source fifth-response ancestry changed")
        return {**base,**empty,"status":"NO_QUALIFIED_SOURCE_FIFTH_RESPONSE"}
    feature=source["first_source_guard_limit"]
    if feature is None:
        return {**base,**empty,"status":"NO_ADMITTED_FIRST_SOURCE_GUARD_BOUNDARY"}
    if (source["status"]!="FIRST_ORIGINAL_CLEARANCE_GUARD_BOUNDARY"
        or len(source["coearliest_source_guard_features"])!=1
        or not feature["source_plane_is_finite"]
        or feature["finite_face_intersecting_span_at_limit"] is not True
        or feature["normal_rate_at_limit"]>=-INWARD_GUARD):
        return {**base,**empty,"status":"GUARD_SOURCE_FEATURE_UNRESOLVED"}
    model=model_at_conditional_fifth(fifth,ancestor)
    planes=original_planes(ancestor,angle)
    matched=[(name,tuple(n),tuple(anchor),span) for name,n,anchor,span in planes
             if name==feature["source_plane"] and span is not None]
    index=feature["source_corner_index"]
    if len(planes)!=6 or len(matched)!=1 or index not in range(4):
        raise ValueError("original finite face or corner identity changed")
    name,n,anchor,span=matched[0]
    t0=feature["guard_limit_time"]
    t1=min(HORIZON,t0+PROBE_WIDTH)
    if not (isfinite(t0) and 0.058<t0<t1<=HORIZON):
        raise ValueError("original source guard time missing")
    initial=plane_gap(model,index,t0,n,anchor)
    end=plane_gap(model,index,t1,n,anchor)
    initial_rate=dot(location(model,index,t0)[1],n)
    rate_upper=initial_rate+model["spin"]**2*RADIUS*(t1-t0)
    if not (abs(initial-GUARD)<ROOT_TOL
            and rate_upper < -INWARD_GUARD
            and initial > 0 and end < 0):
        return {**base,**empty,"status":"LOCAL_ZERO_GAP_NOT_BRACKETED_OR_INWARD"}
    lo,hi=t0,t1
    for _ in range(70):
        middle=(lo+hi)/2
        if plane_gap(model,index,middle,n,anchor)>0:lo=middle
        else:hi=middle
    zero=(lo+hi)/2
    position,velocity=location(model,index,zero)
    tangent=(-n[1],n[0])
    along=dot((position[0]-anchor[0],position[1]-anchor[1]),tangent)
    within=abs(along)<span/2-1e-6
    all_rows=[]
    for source_plane,normal,origin,length in planes:
        normal,origin=tuple(normal),tuple(origin)
        speed=abs(dot(model["velocity"],normal))+abs(model["spin"])*RADIUS
        for i in range(4):
            selected=source_plane==name and i==index
            gstart=plane_gap(model,i,t0,normal,origin)
            gzero=plane_gap(model,i,zero,normal,origin)
            global_lower=gstart-speed*(zero-t0)
            clear=(None if selected else global_lower>OTHER_GAP_GUARD)
            all_rows.append({
                "source_plane":source_plane,"source_corner_index":i,
                "source_plane_finite":length is not None,
                "selected_guard_feature":selected,
                "source_guard_start_gap":rd(gstart),
                "source_zero_time_gap":rd(gzero),
                "original_normal_speed_upper_bound":rd(speed),
                "conservative_other_gap_lower_bound":rd(global_lower),
                "other_original_relation_separated_through_probe":clear,
            })
    if len(all_rows)!=24 or sum(r["selected_guard_feature"] for r in all_rows)!=1:
        raise ValueError("original 24 source relationships incomplete")
    clear=all(r["other_original_relation_separated_through_probe"] is True
              for r in all_rows if not r["selected_guard_feature"])
    accepted=within and clear and abs(plane_gap(model,index,zero,n,anchor))<=ROOT_TOL
    return {
        **base,
        "status":("LOCAL_ORIGINAL_ZERO_GAP_NUMERICAL_FEATURE_QUALIFIED"
                  if accepted else "LOCAL_FIRST_SOURCE_ZERO_GAP_GEOMETRY_UNRESOLVED"),
        "selected_source_face":name,"selected_corner":index,
        "guard_time":t0,"local_probe_endpoint":rd(t1),
        "bracketed_first_zero_time":rd(zero),
        "first_zero_contact_model_position":[rd(x) for x in position],
        "tangent_inside_finite_face":within,
        "source_normal_rate_at_zero":rd(dot(velocity,n)),
        "selected_inward_rate_upper_bound":rd(rate_upper),
        "source_24_plane_corner_probe_records":all_rows,
        "all_23_other_original_constraints_strictly_separated":clear,
        "source_contact_geometry_qualified":accepted,
    }

def run():
    cases=[attempt(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "qualified_numerical_zero_gap_features":sum(c["source_contact_geometry_qualified"] for c in cases),
        "unresolved_local_zero_gap_features":sum(c["status"] in (
            "GUARD_SOURCE_FEATURE_UNRESOLVED","LOCAL_ZERO_GAP_NOT_BRACKETED_OR_INWARD",
            "LOCAL_FIRST_SOURCE_ZERO_GAP_GEOMETRY_UNRESOLVED") for c in cases),
        "inactive_source_controls":sum(c["status"]=="NO_QUALIFIED_SOURCE_FIFTH_RESPONSE" for c in cases),
        "measured_sixth_contacts":0,"selected_sixth_impulses":0,
        "new_receivers":0,"general_world_engine_built":False,
    }
