"""WORLD26: bounded between-frame nonintersection from a velocity envelope.

Trial25 measured finite segment vs rotating square overlap at 2049 sampled
virtual poses. Where sample configurations are separated, this source tests
whether their *fixed world-axis* separating margins and an upper bound on
square-corner displacement cover the entire intervening time interval.

The original WORLD21 third impulse remains unselected. This is nominal
real-arithmetic, not outward-rounded interval certification, real material
motion, a fourth impulse or a general continuous collision solver. Failure
of a bound means UNKNOWN, not that a collision occurred.
"""
from __future__ import annotations

from math import cos, sin, hypot, sqrt, isfinite

from systems.workspace.world_ab_finite_segment_square_overlap import (
    attempt as source25, static_faces, START, DURATION, SAMPLE_COUNT
)
from systems.workspace.world_ab_third_contact import attempt as source21, ANGLES
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA = "world-ab-between-sample-conditional-finite-clearance/v1"
SOURCE25 = "world-ab-finite-segment-rotating-square-intersection/v1"
GUARD = 1e-7
VERTICES = ((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def rd(v):
    return round(float(v), 10)


def projection(points,axis):
    values=[x*axis[0]+y*axis[1] for x,y in points]
    return min(values),max(values)


def nominal_margin(h,segment,t):
    """Largest SAT separation, negative if projections all overlap.

    Every axis is *frozen at this sample instant* when propagated forward or
    backward with the speed bound. Later axis rotation is not extrapolated.
    """
    theta=h["contact_orientation"]+h["outgoing_spin"]*t
    c,s=cos(theta),sin(theta)
    x=h["contact_center"][0]+h["outgoing_velocity"][0]*t
    y=h["contact_center"][1]+h["outgoing_velocity"][1]*t
    corners=[(x+c*a-s*b,y+s*a+c*b) for a,b in VERTICES]
    line=(segment[1][0]-segment[0][0],segment[1][1]-segment[0][1])
    size=hypot(*line)
    if size<1e-12:
        raise ValueError("the unchanged source finite segment degenerated")
    axes=((c,s),(-s,c),(-line[1]/size,line[0]/size))
    gaps=[]
    for axis in axes:
        smin,smax=projection(corners,axis)
        fmin,fmax=projection(segment,axis)
        gaps.append(max(smin-fmax,fmin-smax))
    return max(gaps)


def source_speed_bound(h):
    """Uniform norm bound of every rigid square vertex speed in WORLD units."""
    v=h["outgoing_velocity"]
    return hypot(*v)+abs(h["outgoing_spin"])*HALF*sqrt(2)


def face_windows(h,name,segment):
    speed=source_speed_bound(h)
    if not isfinite(speed) or speed<0:
        raise ValueError("invalid original source velocity envelope")
    dt=(DURATION-START)/SAMPLE_COUNT
    margins=[nominal_margin(h,segment,START+dt*i)
             for i in range(SAMPLE_COUNT+1)]
    if any(not isfinite(m) for m in margins):
        raise ValueError("source margin nonfinite")
    unknown=[]
    sufficient=[]
    for i,(a,b) in enumerate(zip(margins,margins[1:])):
        surplus=a+b-speed*dt
        covered=a>GUARD and b>GUARD and surplus>2*GUARD
        if covered:
            sufficient.append(surplus)
        else:
            unknown.append({
                "interval_index":i,
                "start":rd(START+i*dt),
                "end":rd(START+(i+1)*dt),
                "sample_start_separating_margin":rd(a),
                "sample_end_separating_margin":rd(b),
                "velocity_envelope_surplus":rd(surplus),
                "classification":"NOT_CERTIFIED_BY_ENDPOINT_MARGIN",
            })
    return {
        "face":name,
        "segment":segment,
        "velocity_norm_upper_bound":rd(speed),
        "sampled_margins_count":len(margins),
        "grid_intervals_checked":SAMPLE_COUNT,
        "endpoint_margin_covered_intervals":len(sufficient),
        "uncovered_intervals":unknown,
        "uncovered_interval_count":len(unknown),
        "minimum_covered_margin_surplus":rd(min(sufficient)) if sufficient else None,
        "all_intervals_nominally_covered":not unknown,
        "formal_outward_rounded_certificate":False,
    }


def attempt(angle):
    earlier=source25(angle)
    original=source21(angle)
    base={
        "schema":SCHEMA,"angle":rd(angle),
        "source_trial25_schema":earlier["schema"],
        "source_trial25_status":earlier["status"],
        "source_trial25_intersecting_grid_samples":sum(
            x["intersecting_grid_samples"] for x in earlier["face_results"]),
        "source_third_impulse":original["third_impulse"],
        "source_receiver":original["source_receiver"],
        "observation_start":START,"observation_end":DURATION,
        "sample_intervals":SAMPLE_COUNT,
        "nominal_velocity_margin_guard":GUARD,
        "unchanged_existing_two_finite_faces":True,
        "model_free_flight_hypothesis_only":True,
        "physical_motion_witnessed":False,
        "selected_fourth_impulse":False,
        "new_receiver_constructed":False,
        "certified_floating_point_interval_arithmetic":False,
        "counterfactual_after_any_earlier_contact":True,
    }
    if original["third_impulse"] is None:
        if earlier["status"]!="NO_ADMITTED_THIRD_IMPULSE":
            raise ValueError("source25/no-third-impulse lineage mismatch")
        return {**base,"status":"NO_ADMITTED_THIRD_IMPULSE",
                "face_clearance_bounds":[],
                "fully_nominally_covered_faces":0,
                "uncovered_total_intervals":0}
    if original["status"]!="CONDITIONAL_LOCAL_SEPARATION":
        raise ValueError("unadmitted third-impulse movement")
    records=[face_windows(original["third_impulse"],name,segment)
             for name,segment in static_faces(original,angle)]
    if len(records)!=2 or len(earlier["face_results"])!=2:
        raise ValueError("existing original finite source faces missing")
    for fresh,prior in zip(records,earlier["face_results"]):
        if fresh["face"]!=prior["face"] or fresh["segment"]!=prior["segment"]:
            raise ValueError("finite segment changed relative to Trial25")
    covered=sum(r["all_intervals_nominally_covered"] for r in records)
    unknown=sum(r["uncovered_interval_count"] for r in records)
    if covered==2:
        status="ALL_FINITE_FACE_INTERVALS_NOMINALLY_SEPARATED"
    elif earlier["faces_with_sampled_intersection"]>0:
        status="SAMPLED_FINITE_INTERSECTION_WITH_UNRESOLVED_BETWEEN_FRAMES"
    else:
        status="SOME_BETWEEN_FRAME_INTERVALS_REMAIN_UNRESOLVED"
    return {**base,"status":status,
            "face_clearance_bounds":records,
            "fully_nominally_covered_faces":covered,
            "uncovered_total_intervals":unknown}


def run():
    cases=[attempt(angle) for angle in ANGLES]
    return {"schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
            "conditional_third_impulse_cases":sum(
                c["source_third_impulse"] is not None for c in cases),
            "no_source_third_impulse_controls":sum(
                c["status"]=="NO_ADMITTED_THIRD_IMPULSE" for c in cases),
            "cases_with_both_faces_nominally_covered":sum(
                c["fully_nominally_covered_faces"]==2 for c in cases),
            "cases_with_unresolved_intervals":sum(
                c["uncovered_total_intervals"]>0 for c in cases),
            "total_uncovered_face_intervals":sum(
                c["uncovered_total_intervals"] for c in cases),
            "actual_hardware_measurements":0,
            "fourth_impulses_selected":0,
            "new_physical_receivers_constructed":0,
            "new_physics_engine":False}
