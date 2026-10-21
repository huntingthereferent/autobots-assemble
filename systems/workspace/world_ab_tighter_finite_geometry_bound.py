"""WORLD33: tighter finite geometry bounds, without creating a fifth contact.

Bound the actual conditional rotating-square vs original finite source segments
on the interval immediately AFTER the original WORLD31 conservative-envelope
limit, using interval subdivision and Lipschitz distance enclosures. This is a
finite model-only mathematical check, not a physical trajectory or a contact
solver. No inferred continuation beyond any unresolved interval.
"""
from __future__ import annotations

from math import cos,sin,hypot,isfinite
from systems.workspace.world_ab_geometry_at_first_envelope_limit import attempt as source32
from systems.workspace.world_ab_first_envelope_limit import attempt as source31
from systems.workspace.world_ab_first_finite_response_qualification import attempt as source29
from systems.workspace.world_ab_third_contact import attempt as source21,ANGLES
from systems.workspace.world_ab_finite_segment_square_overlap import static_faces
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA="world-ab-finite-geometry-lipschitz-post-first-limit/v1"
MAX_EXTENSION=.012
SUBDIVISIONS=192
SAFETY_MARGIN=1e-7
SQUARE=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def point_segment_distance(p,a,b):
    dx,dy=b[0]-a[0],b[1]-a[1]
    length=dx*dx+dy*dy
    u=max(0.,min(1.,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/length))
    return hypot(p[0]-a[0]-u*dx,p[1]-a[1]-u*dy)


def orientation(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def intersect(a,b,c,d):
    x1,x2=orientation(a,b,c),orientation(a,b,d)
    y1,y2=orientation(c,d,a),orientation(c,d,b)
    return x1*x2<=0 and y1*y2<=0


def finite_distance(corners,a,b):
    edges=((0,1),(1,3),(3,2),(2,0))
    if any(intersect(corners[i],corners[j],a,b) for i,j in edges):
        return 0.
    return min(
        *(point_segment_distance(p,a,b) for p in corners),
        *(point_segment_distance(p,corners[i],corners[j])
          for p in (a,b) for i,j in edges)
    )


def corners_at(feature,response,t):
    theta=feature["contact_angle"]+response["outgoing_spin"]*t
    co,si=cos(theta),sin(theta)
    cx=feature["contact_center"][0]+response["outgoing_velocity"][0]*t
    cy=feature["contact_center"][1]+response["outgoing_velocity"][1]*t
    return [(cx+co*x-si*y,cy+si*x+co*y) for x,y in SQUARE]


def attempt(angle):
    prior=source31(angle)
    sampled=source32(angle)
    parent=source29(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial31_status":prior["status"],
        "source_trial32_status":sampled["status"],
        "source_first_limit":prior["max_common_nominal_clearance_prefix"],
        "source_limiting_constraints":prior["first_limiting_constraints"],
        "original_24_by_6_world":[24.,6.],
        "model_only":True,
        "real_material_measurements":0,
        "fifth_contact_solved":False,
        "fifth_impulse_solved":False,
        "new_receiver_constructed":False,
        "physical_post_limit_movement_authenticated":False,
    }
    if parent["conditional_fourth_response"] is None:
        return {**base,"status":"NO_QUALIFIED_FOURTH_RESPONSE",
                "finite_face_bounds":[],"supported_extra_time":None}
    if sampled["status"]!="CONDITIONAL_FINITE_SHAPES_SEPARATED_AT_EVIDENCE_LIMIT":
        return {**base,"status":"NO_VERIFIED_FINITE_SEPARATION_AT_SOURCE_LIMIT",
                "finite_face_bounds":[],"supported_extra_time":None}
    t=prior["max_common_nominal_clearance_prefix"]
    feature=parent["qualifying_source_feature"]
    response=parent["conditional_fourth_response"]
    speed=hypot(*response["outgoing_velocity"])+abs(response["outgoing_spin"])*hypot(HALF,HALF)
    faces=static_faces(source21(angle),angle)
    entries=[]
    all_supported=True
    for name,segment in faces:
        a,b=segment
        smallest=float("inf")
        first_unknown=None
        for k in range(SUBDIVISIONS):
            start=t+MAX_EXTENSION*k/SUBDIVISIONS
            stop=t+MAX_EXTENSION*(k+1)/SUBDIVISIONS
            middle=(start+stop)/2
            distance=finite_distance(corners_at(feature,response,middle),a,b)
            lower=max(0.,distance-speed*(stop-start)/2)
            smallest=min(smallest,lower)
            if lower<=SAFETY_MARGIN and first_unknown is None:
                first_unknown=k
        if first_unknown is not None:
            all_supported=False
        entries.append({"source_face":name,
                        "subintervals_checked":SUBDIVISIONS,
                        "minimum_lipschitz_lower_distance":smallest,
                        "first_unresolved_subinterval":first_unknown,
                        "finite_separation_supported":first_unknown is None})
    return {**base,
            "status":("FINITE_FACE_SEPARATION_BOUND_SUPPORTED"
                      if all_supported else "FINITE_FACE_SEPARATION_BOUND_UNRESOLVED"),
            "finite_face_bounds":entries,
            "supported_extra_time":MAX_EXTENSION if all_supported else None,
            "checked_model_interval":[t,t+MAX_EXTENSION],
            "world_perimeter_continuation_certified":False}


def run():
    cases=[attempt(a) for a in ANGLES]
    return {"schema":SCHEMA,"cases":cases,"angles":list(ANGLES),
            "qualified_cases":sum(c["source_first_limit"] is not None for c in cases),
            "finite_face_bound_supported":sum(c["status"]=="FINITE_FACE_SEPARATION_BOUND_SUPPORTED" for c in cases),
            "finite_face_bound_unresolved":sum(c["status"]=="FINITE_FACE_SEPARATION_BOUND_UNRESOLVED" for c in cases),
            "no_response_controls":sum(c["status"]=="NO_QUALIFIED_FOURTH_RESPONSE" for c in cases),
            "fifth_impulses":0,"real_material_measurements":0}
