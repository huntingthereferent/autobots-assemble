"""WORLD43 — finite-original-segment separation, NOT support-line collision.

Conditional on WORLD42 independently clearing all original supporting
plane normal gaps through t=.25, examine [.25,.50] of the same *unselected*
sixth-response constant-speed rigid-square model. Retain the original
24x6 world, four world perimeter planes, and BOTH original finite segments.

A finite static segment and rigid square are proved apart on a subinterval
only if a single fixed SAT axis (source segment normal or rotating square
axis at either endpoint) supplies a positive full-time Lipschitz certificate.
World perimeter gaps are also individually checked. Bisect the FIRST
uncertified interval, stop there, and never label uncertainty a seventh
material contact or an impulse. This permits testing whether a supporting-
line crossing OUTSIDE a finite source face actually matters.
"""
from __future__ import annotations

from math import cos,sin,hypot,isfinite
from systems.workspace.world_ab_first_post_sixth_guard_limit import (
    attempt as prior42, SCHEMA as SOURCE42
)
from systems.workspace.world_ab_post_sixth_local_clearance import source_model
from systems.workspace.world_ab_sixth_conditional_normal_law import attempt as prior40
from systems.workspace.world_ab_post_fifth_contiguous_prefix import original_planes
from systems.workspace.world_ab_third_contact import ANGLES
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA="world-ab-finite-original-post-sixth-separation/v1"
START=.25
END=.50
BASE_SLABS=64
MAX_REFINE=8
GUARD=1e-7
RADIUS=hypot(HALF,HALF)
CORNERS=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def rd(v):return round(float(v),12)
def dot(v,w):return v[0]*w[0]+v[1]*w[1]


def square(model,t):
    theta=model["theta"]+model["spin"]*t
    c,s=cos(theta),sin(theta)
    center=(model["center"][0]+model["velocity"][0]*t,
            model["center"][1]+model["velocity"][1]*t)
    return [(center[0]+x*c-y*s,center[1]+x*s+y*c) for x,y in CORNERS]


def segments_and_world(planes):
    faces=[]
    world=[]
    for name,n,anchor,span in planes:
        if span is None:
            world.append((name,n,anchor))
            continue
        tangent=(-n[1],n[0])
        faces.append((name,n,(
            (anchor[0]-span*tangent[0]/2,anchor[1]-span*tangent[1]/2),
            (anchor[0]+span*tangent[0]/2,anchor[1]+span*tangent[1]/2))))
    if len(planes)!=6 or len(faces)!=2 or len(world)!=4:
        raise ValueError("original finite surfaces/world perimeter changed")
    return faces,world


def axes(model,normal,a,b):
    original=[("finite_segment_normal",tuple(normal))]
    for label,time in (("square_at_start",a),("square_at_end",b)):
        theta=model["theta"]+model["spin"]*time
        c,s=cos(theta),sin(theta)
        original.extend(((label+"_first",(c,s)),
                         (label+"_second",(-s,c))))
    return original


def signed_separation(box,segment,n,reverse):
    p=[dot(x,n) for x in box]
    q=[dot(x,n) for x in segment]
    return (min(q)-max(p) if reverse else min(p)-max(q))


def face_witness(model,face,qa,qb,a,b,speed):
    name,n,segment=face
    candidates=[]
    for axis_source,axis in axes(model,n,a,b):
        for reverse in (False,True):
            g0=signed_separation(qa,segment,axis,reverse)
            g1=signed_separation(qb,segment,axis,reverse)
            lower=g0+g1-speed*(b-a)-2*GUARD
            qualifies=g0>GUARD and g1>GUARD and lower>0
            candidates.append({
                "original_face":name,
                "axis_source":axis_source,
                "fixed_axis":[rd(v) for v in axis],
                "reverse_segment_square_order":reverse,
                "start_projection_gap":rd(g0),
                "end_projection_gap":rd(g1),
                "endpoint_lipschitz_surplus":rd(lower),
                "separates_entire_subinterval":qualifies,
            })
    # Prefer the strongest full-interval certificate, otherwise the
    # strongest attempted axis. Neither choice can hide failed constraints.
    candidates.sort(key=lambda x:(
        x["separates_entire_subinterval"],
        x["endpoint_lipschitz_surplus"],
        x["axis_source"],x["reverse_segment_square_order"]),reverse=True)
    return candidates[0]


def perimeter_witness(name,n,anchor,qa,qb,dt,speed):
    g0=min(dot((p[0]-anchor[0],p[1]-anchor[1]),n) for p in qa)
    g1=min(dot((p[0]-anchor[0],p[1]-anchor[1]),n) for p in qb)
    lower=g0+g1-speed*dt-2*GUARD
    return {
        "original_world_plane":name,
        "source_corner_count":4,
        "start_minimum_corner_gap":rd(g0),
        "end_minimum_corner_gap":rd(g1),
        "endpoint_lipschitz_surplus":rd(lower),
        "perimeter_clear_entire_subinterval":(
            g0>GUARD and g1>GUARD and lower>0),
    }


def slab(model,faces,world,a,b):
    if not (START-1e-12<=a<b<=END+1e-12):
        raise ValueError("outside source-owned post-sixth finite horizon")
    qa=square(model,a);qb=square(model,b)
    # Every ORIGINAL corner speed is no greater than |center_velocity|+|w|*R.
    speed=hypot(*model["velocity"])+abs(model["spin"])*RADIUS
    if not isfinite(speed):raise ValueError("nonfinite original source speed")
    face_records=[face_witness(model,f,qa,qb,a,b,speed) for f in faces]
    perimeter_records=[
        perimeter_witness(name,n,anchor,qa,qb,b-a,speed)
        for name,n,anchor in world
    ]
    valid=all(x["separates_entire_subinterval"] for x in face_records) and all(
        x["perimeter_clear_entire_subinterval"] for x in perimeter_records)
    return {
        "start":rd(a),"end":rd(b),
        "original_finite_face_count":2,
        "original_world_perimeter_count":4,
        "original_square_corner_count":4,
        "finite_rigid_vertex_speed_bound":rd(speed),
        "original_finite_face_certificates":face_records,
        "original_world_perimeter_certificates":perimeter_records,
        "nominal_separation_supported":valid,
        "uncertified_means_contact":False,
        "formal_outward_rounded_certificate":False,
    }


def refine(model,faces,world,a,b,depth,accepted):
    record=slab(model,faces,world,a,b)
    if record["nominal_separation_supported"]:
        accepted.append(record)
        return None
    if depth==MAX_REFINE:
        return {**record,
                "status":"FIRST_FINITE_ORIGINAL_SEPARATION_UNRESOLVED",
                "seventh_collision_measured":False}
    mid=(a+b)/2
    return refine(model,faces,world,a,mid,depth+1,accepted) or refine(
        model,faces,world,mid,b,depth+1,accepted)


def attempt(angle):
    old=prior42(angle)
    before=prior40(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial42_schema":SOURCE42,
        "source_trial42_status":old["status"],
        "source_trial42_horizon":old["supported_horizon_endpoint"],
        "original_world":[24.,6.],
        "original_finite_face_count":2,
        "original_world_perimeter_count":4,
        "original_corner_count":4,
        "source_window_start":START,"source_window_end":END,
        "base_interval_count":BASE_SLABS,"max_bisection_depth":MAX_REFINE,
        "positive_finite_separation_guard":GUARD,
        "conditional_sixth_response_only":True,
        "physical_sixth_impact_observed":False,
        "physical_seventh_impact_observed":False,
        "seventh_impulse_computed":False,
        "source_continuation_after_first_unknown":False,
        "new_receiver_constructed":False,
        "outward_rounded_interval_certification":False,
    }
    empty={
        "original_conditional_model_at_sixth":None,
        "original_finite_source_segments":[],
        "source_original_perimeter_planes":[],
        "nominally_supported_prefix_end":None,
        "original_accepted_intervals":[],
        "first_finite_original_unknown":None,
        "entire_finite_declared_window_supported":False,
    }
    if before["conditional_sixth_response"] is None:
        if old["status"]!="NO_ADMITTED_SIXTH_SOURCE":
            raise ValueError("WORLD42 inactive original source changed")
        return {**base,**empty,"status":"NO_SOURCE_SIXTH_RESPONSE"}
    if (old["status"]!="POST_SIXTH_ORIGINAL_GUARDS_CLEAR_THROUGH_HORIZON"
        or old["all_original_guards_clear_through_horizon"] is not True
        or abs(old["supported_horizon_endpoint"]-START)>1e-9):
        return {**base,**empty,"status":"SOURCE_T42_FIRST_HORIZON_NOT_SUPPORTED"}
    model,ancestor=source_model(angle,before)
    planes=original_planes(ancestor,angle)
    faces,world=segments_and_world(planes)
    if any(not isfinite(z) for z in (
        *model["center"],model["theta"],*model["velocity"],model["spin"])):
        raise ValueError("source sixth pose nonfinite")
    accepted=[]
    unknown=None
    for i in range(BASE_SLABS):
        a=START+(END-START)*i/BASE_SLABS
        b=START+(END-START)*(i+1)/BASE_SLABS
        unknown=refine(model,faces,world,a,b,0,accepted)
        if unknown is not None:break
    prefix=accepted[-1]["end"] if accepted else START
    if unknown is not None and abs(prefix-unknown["start"])>2e-9:
        raise ValueError("original finite source missing chronological gap")
    return {
        **base,
        "status":("FINITE_ORIGINAL_SEGMENTS_NOMINALLY_SEPARATED_THROUGH_HORIZON"
                  if unknown is None else "FIRST_FINITE_ORIGINAL_SEPARATION_UNRESOLVED"),
        "original_conditional_model_at_sixth":{
            "center":[rd(x) for x in model["center"]],
            "theta":rd(model["theta"]),
            "outgoing_velocity":[rd(x) for x in model["velocity"]],
            "outgoing_spin":rd(model["spin"])},
        "original_finite_source_segments":[
            {"name":name,"endpoints":[[rd(c) for c in p] for p in segment]}
            for name,_,segment in faces],
        "source_original_perimeter_planes":[name for name,_,_ in world],
        "nominally_supported_prefix_end":prefix,
        "original_accepted_intervals":accepted,
        "first_finite_original_unknown":unknown,
        "entire_finite_declared_window_supported":unknown is None,
    }


def run():
    cases=[attempt(a) for a in ANGLES]
    return {"schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
            "admitted_post_sixth_finite_models":sum(
                c["original_conditional_model_at_sixth"] is not None for c in cases),
            "complete_finite_windows":sum(
                c["entire_finite_declared_window_supported"] for c in cases),
            "first_finite_unknown_models":sum(
                c["status"]=="FIRST_FINITE_ORIGINAL_SEPARATION_UNRESOLVED" for c in cases),
            "prior_horizon_unresolved":sum(
                c["status"]=="SOURCE_T42_FIRST_HORIZON_NOT_SUPPORTED" for c in cases),
            "inactive_original_controls":sum(
                c["status"]=="NO_SOURCE_SIXTH_RESPONSE" for c in cases),
            "material_seventh_contacts":0,"seventh_impulses":0,
            "new_receivers":0,"new_world_engines":0}
