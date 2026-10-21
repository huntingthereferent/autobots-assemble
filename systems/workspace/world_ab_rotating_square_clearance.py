"""WORLD Trial 16 — observed free-square rotation can invalidate straight travel.

Continue the ORIGINAL oblique-square first-impact source, unchanged. Its
short post-impact ballistic position + orientation is a *hypothesis* until
the finite source-face clearance is checked. Re-evaluate the rotating four
corners against that same finite face at a bounded observation cadence.
A detected overlap REFUSES the projected continuation and any derived
receiver; no second impact or contact response is invented.

This is discrete sampled collision evidence, NOT a continuous rotating-
polygon contact solver or a material/real-world sensor measurement.
"""
from __future__ import annotations

from math import cos, sin, radians, isfinite
from systems.workspace.world_ab_contact_trial import initial
from systems.workspace.world_ab_oblique_impact import (
    strike, HALF, WALL_CENTER, SPAN, INERTIA
)

SCHEMA="world-ab-rotating-square-clearance-check/v1"
OBSERVATION_STEP=.001
HORIZON=.06
EPS=1e-8
ANGLES=(0., 2.5, 5., 7.5, 10., 12.25, 15., 20.)

def rd(v):
    return round(float(v), 10)

def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]

def rotating_corners(center,theta):
    c,s=cos(theta),sin(theta)
    return [(center[0]+x*c-y*s,center[1]+x*s+y*c)
            for x in (-HALF,HALF) for y in (-HALF,HALF)]

def sample(result,dt):
    """Sample all ORIGINAL square corners and the original finite source.

    Penetration candidate = vertex on the wrong one-sided face with tangent
    coordinate inside the actual finite segment. No sampled overlap does
    NOT establish future or intersample nonpenetration.
    """
    if type(dt) not in (float,int) or not isfinite(dt) or not 0<=dt<=HORIZON:
        raise ValueError("invalid bounded observation time")
    if not result["hit"]:
        raise ValueError("no original first-contact source")
    n=tuple(result["normal"])
    tangent=(-n[1],n[0])
    p=tuple(result["first_contact_center"])
    v=tuple(result["velocity_after"])
    center=(p[0]+dt*v[0],p[1]+dt*v[1])
    theta=dt*result["angular_velocity_after"]
    corners=rotating_corners(center,theta)
    tested=[]
    for index,corner in enumerate(corners):
        relative=(corner[0]-WALL_CENTER[0],corner[1]-WALL_CENTER[1])
        along=dot(relative,tangent)
        if -SPAN/2-EPS <= along <= SPAN/2+EPS:
            tested.append({"corner_index":index,
                           "signed_clearance":rd(dot(relative,n)),
                           "tangent_coordinate":rd(along)})
    if not tested:
        return {"dt":rd(dt),"center":[rd(z) for z in center],
                "orientation":rd(theta),"minimum_signed_clearance":None,
                "finite_interior_overlap":False,
                "checked_corners":0,"worst_corner_index":None}
    worst=min(tested,key=lambda d:d["signed_clearance"])
    return {"dt":rd(dt),"center":[rd(z) for z in center],
            "orientation":rd(theta),
            "minimum_signed_clearance":worst["signed_clearance"],
            "finite_interior_overlap":worst["signed_clearance"]<-EPS,
            "checked_corners":len(tested),
            "worst_corner_index":worst["corner_index"]}

def trial(angle=20.):
    original=strike(initial(),angle)
    if not original["hit"]:
        return {"schema":SCHEMA,"angle":rd(angle),
                "status":"NO_ADMITTED_FIRST_CONTACT",
                "first_contact":original,"samples":[],
                "first_detected_overlap_at":None,
                "next_receiver_built":False,
                "physical_observation":False,
                "continuous_clearance_verified":False}
    observations=[sample(original,OBSERVATION_STEP*i)
                  for i in range(round(HORIZON/OBSERVATION_STEP)+1)]
    bad=next((s for s in observations if s["finite_interior_overlap"]),None)
    return {
        "schema":SCHEMA,
        "angle":rd(angle),
        "status":("ROTATING_BODY_OVERLAPS_ORIGINAL_FACE_AT_SAMPLE"
                  if bad else "NO_OVERLAP_DETECTED_IN_SHORT_SAMPLED_WINDOW"),
        "source_model":"unchanged original WORLD trial 04 rigid-square single impact",
        "first_contact":original,
        "samples":observations,
        "observation_step":OBSERVATION_STEP,
        "observation_horizon":HORIZON,
        "first_detected_overlap_at":None if bad is None else bad["dt"],
        # Original 04 first impact proposed a face; NOT a second built face.
        "next_receiver_candidate_only":original["candidate_receiver"],
        "next_receiver_built":False,
        "second_contact_computed":False,
        "unmodeled_recontact_response_refused":bad is not None,
        "no_overlap_between_samples_proven":False,
        "continuous_clearance_verified":False,
        "physical_observation":False,
        "world_15_fixed_square_source_preserved":True,
    }

def run():
    records=[trial(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),
        "cases":records,
        "counts":{
            "sampled-overlap":sum("OVERLAPS" in r["status"] for r in records),
            "sampled-no-overlap":sum(r["status"]=="NO_OVERLAP_DETECTED_IN_SHORT_SAMPLED_WINDOW"
                                      for r in records),
        },
        "physical_world_verified":False,
        "continuous_rotating_polygon_solver_present":False,
        "new_world_or_renderer":False,
    }
