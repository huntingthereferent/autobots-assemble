"""WORLD Trial19: analytic whole-interval separation of Trial18 candidate motion.

No new world, solver, engine, or object type. For the same rotating rigid-square
candidate after the second *hypothetical* frictionless impact, bound the signed
distance of every square vertex to the ORIGINAL source supporting line.

For a body vertex r at second-contact orientation, gap(t) = g0 + vn*t
+ n·Rot(omega*t)r. Taylor's theorem and |gap''(t)| <= omega^2 |r| give

  gap(t) >= gap(0) + gap'(0)*t - 0.5*K*t*t,
  K = omega^2*sqrt(2)*HALF.

For the first touching corner the nominal gap at t=0 is zero within the
recording tolerance; a strictly positive derivative lower bound prevents
later return. Other corners have strictly positive quadratic lower bounds
throughout the tested 0.016 virtual-time window. This proves a stronger
geometric statement *under the declared nominal model and exact real-number
interpretation*: the square remains on the non-penetrating side of the
source's infinite support line. Hence it is clear of the finite source
segment too, including both endpoints.

Ordinary floating arithmetic is NOT a formally outward-rounded interval
certificate. No continuous real-material outcome, contact law selection,
external forces, or further receiver is claimed.
"""
from __future__ import annotations

from math import cos, sin, hypot, isfinite

from systems.workspace.world_ab_local_recontact_impulse import (
    attempt as trial18, ANGLES, POST_HORIZON, VERTICES,
)
from systems.workspace.world_ab_oblique_impact import HALF, WALL_CENTER

SCHEMA="world-ab-conditional-continuous-separation/v1"
EPS=1e-7
MIN_CERTIFIED_MARGIN=1e-5
RADIUS=hypot(HALF,HALF)


def rd(x):
    return round(float(x), 10)


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def cross(a,b):
    return a[0]*b[1]-a[1]*b[0]


def evaluate(angle):
    old=trial18(angle)
    common={
        "schema":SCHEMA,
        "source_trial18_schema":old["schema"],
        "original_source_angle":old["angle"],
        "original_first_contact_source_id":"original WORLD Trial04 rigid square",
        "source_candidate_impulse":old["candidate_impulse"],
        "source_trial18_status":old["status"],
        "half_extent":HALF,
        "window":POST_HORIZON,
        "finite_face_origin":list(WALL_CENTER),
        "conditional_second_impulse_only":True,
        "actual_hardware_behavior_witnessed":False,
        "further_contact_response_solved":False,
        "derived_receiver_constructed":False,
        "formal_floating_point_interval_certificate":False,
    }
    if old["candidate_impulse"] is None:
        if old["status"]!="NO_ADMITTED_RENEWED_CONTACT":
            raise ValueError("unexpected unadmitted source contact")
        return {
            **common,"status":"NO_ADMITTED_SECOND_IMPULSE",
            "per_vertex_bounds":[],"worst_positive_margin":None,
            "all_corner_halfspace_clearance_supported":False,
        }
    first=old["source_trial17_first_return"]
    hypothesis=old["candidate_impulse"]
    if (first is None or first["corner_index"]!=hypothesis["contact_vertex_index"]
            or hypothesis["selected_as_actual_material_response"] is not False):
        raise ValueError("source response/feature identity changed")
    normal=tuple(hypothesis["source_face_normal"])
    center=tuple(hypothesis["contact_center"])
    theta=hypothesis["contact_angle"]
    velocity=tuple(hypothesis["velocity_after"])
    omega=hypothesis["angular_velocity_after"]
    if any(not isfinite(v) for v in (*normal,*center,theta,*velocity,omega)):
        raise ValueError("nonfinite source movement")
    if abs(hypot(*normal)-1)>1e-7:
        raise ValueError("source normal not unit")
    if not (0<POST_HORIZON<=.016):
        raise ValueError("source observation interval changed")
    k=(omega*omega)*RADIUS
    records=[]
    for i,(x,y) in enumerate(VERTICES):
        # Actual original square corner at nominal second-contact orientation.
        rx=x*cos(theta)-y*sin(theta)
        ry=x*sin(theta)+y*cos(theta)
        r=(rx,ry)
        f0=dot((center[0]+rx-WALL_CENTER[0],
                center[1]+ry-WALL_CENTER[1]),normal)
        df0=dot(velocity,normal)+omega*cross(r,normal)
        # The lower polynomial is concave, so its minimum over a closed
        # interval is at an endpoint. Treat the contact corner separately.
        qend=f0+df0*POST_HORIZON-.5*k*POST_HORIZON**2
        if i==first["corner_index"]:
            if abs(f0)>EPS:
                raise ValueError("second contact point left original face")
            rate_floor=df0-k*POST_HORIZON
            accepted=rate_floor>MIN_CERTIFIED_MARGIN
            margin=rate_floor
            condition="touching-corner-derivative-positive-entire-window"
        else:
            rate_floor=df0-k*POST_HORIZON
            margin=min(f0,qend)
            accepted=margin>MIN_CERTIFIED_MARGIN
            condition="noncontact-corner-quadratic-lower-bound-positive"
        records.append({
            "corner_index":i,
            "source_signed_gap_at_contact":rd(f0),
            "outgoing_signed_gap_derivative":rd(df0),
            "absolute_second_derivative_bound":rd(k),
            "quadratic_lower_bound_at_window_end":rd(qend),
            "derivative_lower_bound_at_window_end":rd(rate_floor),
            "admission_condition":condition,
            "conservative_margin":rd(margin),
            "accepted":accepted,
        })
    success=all(r["accepted"] for r in records)
    return {
        **common,
        "status":("CONDITIONAL_CONTINUOUS_HALFSPACE_SEPARATION"
                  if success else "UNRESOLVED_CONTINUOUS_HALFSPACE_SEPARATION"),
        "per_vertex_bounds":records,
        "worst_positive_margin":rd(min(r["conservative_margin"] for r in records)) if success else None,
        "all_corner_halfspace_clearance_supported":success,
        "bounding_method":"four rotated-corner Taylor lower bounds; whole interval",
        "line_clearance_implies_finite_face_clearance":success,
        "nominal_real_arithmetic_only":True,
        "postcontact_motion_assumed_ballistic":True,
        "no_additional_contacts_or_forces_in_assumed_window":True,
    }


def run():
    cases=[evaluate(a) for a in ANGLES]
    return {
        "schema":SCHEMA,
        "source_trial18":"world-ab-local-corner-recontact-impulse/v1",
        "angles":list(ANGLES),
        "cases":cases,
        "conditional_continuous_clearance_count":sum(
            c["status"]=="CONDITIONAL_CONTINUOUS_HALFSPACE_SEPARATION"
            for c in cases),
        "no_second_impulse_count":sum(
            c["status"]=="NO_ADMITTED_SECOND_IMPULSE" for c in cases),
        "inconclusive_count":sum(
            c["status"]=="UNRESOLVED_CONTINUOUS_HALFSPACE_SEPARATION"
            for c in cases),
        "physics_engine_created":False,
        "all_earth_physics_verified":False,
        "new_receiver_created":False,
    }
