"""WORLD22: locate first possible modeled boundary return after WORLD21 third impulse.

Continue the SAME source-owned finite WORLD, not a new physics engine. Under the
unselected WORLD21 third frictionless impulse, project the rotating square for
at most 0.25 virtual-time units. Partition every vertex-to-plane distance into
monotonic intervals by analytic derivative roots; bisect any positive-to-negative
gap crossing. Retain all co-earliest candidates. Supporting-line crossings
outside the two finite faces are explicitly unresolved, not material impacts.

No fourth impulse, later receiver, real motion, certified interval arithmetic,
or contact/force law is selected.
"""
from __future__ import annotations

from math import acos, atan2, ceil, cos, hypot, isfinite, pi, sin

from systems.workspace.world_ab_third_contact import attempt as trial21, ANGLES
from systems.workspace.world_ab_local_recontact_impulse import attempt as trial18
from systems.workspace.world_ab_oblique_impact import HALF, WALL_CENTER

SCHEMA = "world-ab-first-candidate-after-conditional-third/v1"
DURATION = 0.25
WORLD = (24., 6.)
VERTICES = ((-HALF, -HALF), (-HALF, HALF), (HALF, -HALF), (HALF, HALF))
ROOT_TOL = 3e-7
TIE_TOL = 1e-7


def rd(x):
    return round(float(x), 10)


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def surfaces(source, angle):
    first=trial18(angle)["source_first_contact"]
    receiver=source["source_receiver"]
    n=receiver["normal"]
    return [
        ("original_finite_face",tuple(first["normal"]),tuple(WALL_CENTER),1.0),
        ("motion_derived_receiver",tuple(n),tuple(receiver["anchor"]),1.0),
        ("world_left",(1.,0.),(0.,0.),None),
        ("world_right",(-1.,0.),(WORLD[0],0.),None),
        ("world_bottom",(0.,1.),(0.,0.),None),
        ("world_top",(0.,-1.),(0.,WORLD[1]),None),
    ]


def pose(h,vertex,t):
    angle=h["contact_orientation"]+h["outgoing_spin"]*t
    x,y=vertex
    c,s=cos(angle),sin(angle)
    cx,cy=h["contact_center"]
    vx,vy=h["outgoing_velocity"]
    return (cx+vx*t+x*c-y*s,cy+vy*t+x*s+y*c)


def gap_terms(h,vertex,normal,anchor):
    theta=h["contact_orientation"]
    x,y=vertex
    rotated=(x*cos(theta)-y*sin(theta),x*sin(theta)+y*cos(theta))
    c=(h["contact_center"][0]-anchor[0],h["contact_center"][1]-anchor[1])
    constant=dot(c,normal)
    v=dot(h["outgoing_velocity"],normal)
    a=dot(rotated,normal)
    b=dot((-rotated[1],rotated[0]),normal)
    return constant,v,a,b,h["outgoing_spin"]


def gap_value(q,t):
    c,v,a,b,w=q
    return c+v*t+a*cos(w*t)+b*sin(w*t)


def gap_rate(q,t):
    _,v,a,b,w=q
    return v+w*(-a*sin(w*t)+b*cos(w*t))


def stationary(q):
    """Every analytic derivative root in the declared finite virtual window."""
    _,v,a,b,w=q
    times=[0.,DURATION]
    radius=hypot(a,b)
    if abs(w)>1e-12 and radius>1e-12:
        ratio=-v/(w*radius)
        if -1.<=ratio<=1.:
            offset=atan2(a,b)
            alpha=acos(max(-1.,min(1.,ratio)))
            limit=ceil(abs(w)*DURATION/(2*pi))+4
            for k in range(-limit,limit+1):
                for sign in (-1.,1.):
                    t=(sign*alpha-offset+2*pi*k)/w
                    if 1e-12<t<DURATION-1e-12:
                        times.append(t)
    return sorted(set(times))


def first_inward_crossing(q):
    """Earliest positive-to-negative root; no tangential solution is assumed."""
    times=stationary(q)
    for left,right in zip(times,times[1:]):
        gl=gap_value(q,left)
        gr=gap_value(q,right)
        if gl<=1e-9 or gr>=-1e-9:
            continue
        a,b=left,right
        for _ in range(58):
            mid=(a+b)/2
            if gap_value(q,mid)>0:
                a=mid
            else:
                b=mid
        t=(a+b)/2
        if t>1e-9 and gap_rate(q,t)<-1e-7:
            return t,len(times)-1
    return None,len(times)-1


def classify(name,anchor,normal,span,point):
    if span is None:
        return "WORLD_PERIMETER_CANDIDATE",None
    tangent=(-normal[1],normal[0])
    along=dot((point[0]-anchor[0],point[1]-anchor[1]),tangent)
    if abs(along)>span/2+ROOT_TOL:
        return "SUPPORT_LINE_OUTSIDE_FINITE_FACE_UNRESOLVED",rd(along)
    if abs(along)>=span/2-ROOT_TOL:
        return "ENDPOINT_FEATURE_UNRESOLVED",rd(along)
    return "FINITE_FACE_INTERIOR_CANDIDATE",rd(along)


def attempt(angle):
    ancestor=trial21(angle)
    base={
        "schema":SCHEMA,"source_trial21_schema":ancestor["schema"],
        "angle":rd(angle),"source_trial21_status":ancestor["status"],
        "source_third_impulse":ancestor["third_impulse"],
        "source_receiver":ancestor["source_receiver"],
        "projection_horizon":DURATION,
        "source_trial21_local_window":ancestor["local_window"],
        "source_original_world":[WORLD[0],WORLD[1]],
        "unselected_conditional_model_only":True,
        "model_motion_not_material_measurement":True,
        "fourth_impulse_solved":False,
        "new_receiver_constructed":False,
        "continuous_real_world_motion_verified":False,
        "formally_outward_rounded_certificate":False,
        "later_forces_and_impacts_assumed_absent":True,
    }
    if ancestor["third_impulse"] is None:
        if ancestor["status"]!="NO_QUALIFYING_THIRD_CONTACT":
            raise ValueError("unresolved source cannot be given future motion")
        return {**base,"status":"NO_ADMITTED_THIRD_IMPULSE",
                "first_crossing":None,"coearliest_crossings":[],
                "all_source_line_crossings":[],"monotonic_intervals_checked":0}
    if ancestor["status"]!="CONDITIONAL_LOCAL_SEPARATION":
        return {**base,"status":"SOURCE_LOCAL_GEOMETRY_UNRESOLVED",
                "first_crossing":None,"coearliest_crossings":[],
                "all_source_line_crossings":[],"monotonic_intervals_checked":0}
    h=ancestor["third_impulse"]
    require_fields=("contact_center","contact_orientation","outgoing_velocity",
                    "outgoing_spin","contact_absolute_virtual_time")
    if any(field not in h for field in require_fields):
        raise ValueError("original third-impulse model is incomplete")
    raw=[]
    intervals=0
    for name,normal,anchor,span in surfaces(ancestor,angle):
        for i,vertex in enumerate(VERTICES):
            q=gap_terms(h,vertex,normal,anchor)
            if not all(isfinite(z) for z in q):
                raise ValueError("original motion became nonfinite")
            t,checked=first_inward_crossing(q)
            intervals+=checked
            if t is None:
                continue
            point=pose(h,vertex,t)
            kind,along=classify(name,anchor,normal,span,point)
            raw.append({
                "surface":name,"vertex_index":i,
                "dt_after_third_impulse":rd(t),
                "absolute_virtual_time":rd(h["contact_absolute_virtual_time"]+t),
                "vertex_position":[rd(z) for z in point],
                "source_face_tangent_coordinate":along,
                "incoming_normal_vertex_rate":rd(gap_rate(q,t)),
                "signed_line_gap_residual":rd(gap_value(q,t)),
                "feature_classification":kind,
                "physical_contact_measured":False,
            })
    raw.sort(key=lambda x:(x["dt_after_third_impulse"],x["surface"],x["vertex_index"]))
    if not raw:
        status="NO_INWARD_SOURCE_LINE_CROSSING_IN_BOUNDED_PROJECTION"
        return {**base,"status":status,"first_crossing":None,
                "coearliest_crossings":[],"all_source_line_crossings":[],
                "monotonic_intervals_checked":intervals}
    t0=raw[0]["dt_after_third_impulse"]
    tied=[r for r in raw if abs(r["dt_after_third_impulse"]-t0)<=TIE_TOL]
    if len(tied)>1:
        status="MULTIPLE_FIRST_FEATURES_UNRESOLVED"
    elif tied[0]["feature_classification"] in (
            "WORLD_PERIMETER_CANDIDATE","FINITE_FACE_INTERIOR_CANDIDATE"):
        status="FIRST_MODEL_CONTACT_GEOMETRY_CANDIDATE"
    else:
        status=tied[0]["feature_classification"]
    return {**base,"status":status,"first_crossing":raw[0],
            "coearliest_crossings":tied,"all_source_line_crossings":raw,
            "monotonic_intervals_checked":intervals}


def run():
    cases=[attempt(angle) for angle in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "conditional_third_impulse_inputs":sum(
            c["source_third_impulse"] is not None for c in cases),
        "no_third_impulse_controls":sum(
            c["status"]=="NO_ADMITTED_THIRD_IMPULSE" for c in cases),
        "source_line_crossing_cases":sum(
            c["first_crossing"] is not None for c in cases),
        "source_line_no_crossing_cases":sum(
            c["source_third_impulse"] is not None and
            c["first_crossing"] is None for c in cases),
        "physical_contact_measurements":0,
        "selected_fourth_impulses":0,
        "real_receivers_constructed":0,
        "new_world_or_engine":False,
    }
