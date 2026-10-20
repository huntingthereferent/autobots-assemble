"""WORLD Trial 17 — first renewed finite-face contact of the original rotating square.

No physics engine or invented response. Keep the first frictionless off-centre
square impulse from original Trial 04. Its free rigid polygon trajectory is
only a *candidate* before the next contact. For each of four corners, the
signed distance to the original source supporting line is

  f_i(t) = c + (v_after · n)t + (corner_i · n)cos(omega*t)
                         + (J corner_i · n)sin(omega*t),

where t=0 is the *existing* first impact and J(x,y)=(-y,x).
The stationary times of each f_i are found algebraically; bisection between
consecutive stationary times locates the earliest later crossing, if any.
The resulting corner must lie on the ACTUAL finite source segment interior.
No sampled-grid false "exactness", guessed second impulse, fabricated receiver,
or hardware observation. Floating numerical bracketing is not formal proof.
"""
from __future__ import annotations

from math import acos, atan2, ceil, cos, hypot, isfinite, pi, radians, sin

from systems.workspace.world_ab_oblique_impact import (
    HALF, SPAN, WALL_CENTER, strike
)
from systems.workspace.world_ab_contact_trial import initial

SCHEMA = "world-ab-rotating-square-first-finite-recontact/v1"
ANGLES = (0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)
HORIZON = .06
EPS = 1e-9
ZERO_TOL = 2e-8
BISECTION_STEPS = 75
VERTICES = ((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def _round(x):
    return round(float(x), 12)


def _vertex_data(source, vertex):
    n=tuple(source["normal"])
    center=tuple(source["first_contact_center"])
    velocity=tuple(source["velocity_after"])
    omega=source["angular_velocity_after"]
    c=dot((center[0]-WALL_CENTER[0],center[1]-WALL_CENTER[1]),n)
    vn=dot(velocity,n)
    a=dot(vertex,n)
    b=dot((-vertex[1],vertex[0]),n)
    def gap(t):
        return c+vn*t+a*cos(omega*t)+b*sin(omega*t)
    def deriv(t):
        return vn+omega*(-a*sin(omega*t)+b*cos(omega*t))
    return gap,deriv,(a,b,vn)


def _monotonic_breaks(omega,a,b,vn,horizon):
    """All derivative zeros in this bounded interval (numerically computed)."""
    points=[0.,horizon]
    if abs(omega) < EPS:
        return points
    amp=hypot(a,b)
    rhs=-vn/(omega*amp)
    if abs(rhs)>1:
        return points
    phi=atan2(a,b)
    root=acos(max(-1.,min(1.,rhs)))
    cycles=ceil(abs(omega)*horizon/(2*pi))+3
    for k in range(-cycles,cycles+1):
        for sign in (-1,1):
            time=(sign*root-phi+2*k*pi)/omega
            if 1e-12 < time < horizon-1e-12:
                points.append(time)
    return sorted(set(points))


def _corner_at(source,index,t):
    center=tuple(source["first_contact_center"])
    velocity=tuple(source["velocity_after"])
    theta=source["angular_velocity_after"]*t
    c,s=cos(theta),sin(theta)
    x,y=VERTICES[index]
    return (center[0]+velocity[0]*t+c*x-s*y,
            center[1]+velocity[1]*t+s*x+c*y)


def first_recontact(source,horizon=HORIZON):
    if not source.get("hit"):
        raise ValueError("no original source first contact")
    if not (type(horizon) in (int,float) and isfinite(horizon)
            and 0<horizon<=HORIZON):
        raise ValueError("outside admitted finite observation horizon")
    omega=source["angular_velocity_after"]
    n=tuple(source["normal"])
    tangent=(-n[1],n[0])
    records=[]
    candidate_roots=[]
    for index,corner in enumerate(VERTICES):
        f,df,(a,b,vn)=_vertex_data(source,corner)
        times=_monotonic_breaks(omega,a,b,vn,horizon)
        # Source first contact at t=0 must not be reported as another event.
        if f(0)<-ZERO_TOL:
            return {"status":"INVALID_INITIAL_SOURCE_PENETRATION",
                    "first_return":None,"roots":[],"checked_intervals":0}
        if abs(f(0))<=ZERO_TOL and df(0)<-ZERO_TOL:
            return {"status":"IMMEDIATE_POST_IMPACT_OVERLAP",
                    "first_return":None,"roots":[],"checked_intervals":0}
        for lo,hi in zip(times,times[1:]):
            fl,fh=f(lo),f(hi)
            records.append((index,lo,hi))
            if (hi>1e-10 and abs(fh)<=ZERO_TOL and
                    abs(df(hi))<=ZERO_TOL):
                # Tangency at a derivative root is not a signed crossing;
                # it cannot be silently classified as clear.
                candidate_roots.append({"time":hi,"corner_index":index,
                                        "type":"UNRESOLVED_TOUCH"})
            if fl>ZERO_TOL and fh<-ZERO_TOL:
                left,right=lo,hi
                for _ in range(BISECTION_STEPS):
                    mid=(left+right)/2
                    if f(mid)>0:left=mid
                    else:right=mid
                t=(left+right)/2
                pt=_corner_at(source,index,t)
                offset=(pt[0]-WALL_CENTER[0],pt[1]-WALL_CENTER[1])
                along=dot(offset,tangent)
                candidate_roots.append({
                    "time":t,"corner_index":index,
                    "type":"TRANSVERSE_SIGN_CROSSING",
                    "tangent_coordinate":along,
                    "normal_velocity_at_return":df(t),
                    "signed_gap_residual":f(t)})
    roots=sorted(candidate_roots,key=lambda e:(e["time"],e["corner_index"]))
    if not roots:
        return {
            "status":"NO_NEW_LINE_CROSSING_IN_WINDOW",
            "first_return":None,
            "roots":[],
            "checked_intervals":len(records)}
    first=roots[0]
    if first["type"]!="TRANSVERSE_SIGN_CROSSING":
        return {
            "status":"UNRESOLVED_GRAZING_RETURN",
            "first_return":None,
            "roots":[{"time":_round(c["time"]),"corner_index":c["corner_index"],
                      "type":c["type"]} for c in roots],
            "checked_intervals":len(records)}
    if not (-SPAN/2+ZERO_TOL < first["tangent_coordinate"] < SPAN/2-ZERO_TOL):
        return {
            "status":"RETURN_OUTSIDE_FINITE_INTERIOR_UNRESOLVED",
            "first_return":None,
            "roots":[{"time":_round(c["time"]),"corner_index":c["corner_index"],
                      "type":c["type"]} for c in roots],
            "checked_intervals":len(records)}
    t=first["time"]
    point=_corner_at(source,first["corner_index"],t)
    return {
        "status":"FIRST_RENEWED_FINITE_FACE_CONTACT_CANDIDATE",
        "first_return":{
            "dt_after_initial_contact":_round(t),
            "absolute_virtual_time":_round(source["first_contact_time"]+t),
            "corner_index":first["corner_index"],
            "corner_position":[_round(z) for z in point],
            "source_face_tangent_coordinate":_round(first["tangent_coordinate"]),
            "normal_gap_residual":_round(first["signed_gap_residual"]),
            "incoming_normal_vertex_rate":_round(first["normal_velocity_at_return"]),
            "contact_feature":"square-vertex / original finite face interior",
            "second_impulse_selected":False,
        },
        "roots":[{"time":_round(c["time"]),"corner_index":c["corner_index"],
                  "type":c["type"]} for c in roots],
        "checked_intervals":len(records),
    }


def trial(angle=20.):
    original=strike(initial(),angle)
    if not original["hit"]:
        raise ValueError("expected source first contact in admitted angle controls")
    result=first_recontact(original)
    return {
        "schema":SCHEMA,
        "source":"unchanged original WORLD trial04 first square impact",
        "source_angle":_round(angle),
        "source_original_first_contact":original,
        "horizon":HORIZON,
        "status":result["status"],
        "first_return":result["first_return"],
        "candidate_return_roots":result["roots"],
        "monotonic_segments_checked":result["checked_intervals"],
        "method":"analytical corner gap stationary partitions plus numerical bisection",
        "source_finite_wall_preserved":True,
        "recontact_kinematics_only":True,
        "numerically_bracketed_not_exact_certified":True,
        "second_impulse_or_further_motion_solved":False,
        "derived_receiver_built":False,
        "physical_sensor_evidence":False,
    }


def run():
    cases=[trial(angle) for angle in ANGLES]
    return {
        "schema":SCHEMA,
        "angles":list(ANGLES),
        "horizon":HORIZON,
        "cases":cases,
        "first_return_candidates":sum(c["first_return"] is not None for c in cases),
        "no_return":sum(c["status"]=="NO_NEW_LINE_CROSSING_IN_WINDOW" for c in cases),
        "built_any_new_object":False,
        "actual_physical_impact_verified":False,
    }
