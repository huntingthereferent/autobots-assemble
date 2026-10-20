"""WORLD Trial21 — third conditional rigid-square contact at source-derived face.

Use the SAME frictionless e=1 normal impulse rule as original WORLD Trial04
and Trial18. The source-derived receiver, finite vertex, motion and arrival
time come ONLY from the verified Trial20 construction. No predetermined new
geometry, future receiver, real-world material inference, or extra engine.

After proposing the third impulse, use conservative Taylor bounds on the
four rotated vertices against both old and new source supporting lines and
all four original WORLD boundaries. A bounding failure is unresolved, not a
completed continuation. Results are conditional nominal floating-point math;
no formally outward-rounded numeric certificate or hardware measurements.
"""
from __future__ import annotations

from math import cos, sin, hypot, isfinite
from systems.workspace.world_ab_rotating_receiver import (
    trial as former, ANGLES, DURATION,
)
from systems.workspace.world_ab_local_recontact_impulse import attempt as old_impulse
from systems.workspace.world_ab_oblique_impact import HALF, INERTIA, WALL_CENTER

SCHEMA="world-ab-conditional-third-contact/v1"
VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
POST_WINDOW=.008
TOL=3e-7
MIN_MARGIN=1e-5
WORLD_WIDTH=24.
WORLD_HEIGHT=6.


def rd(x):
    return round(float(x), 10)


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def det(a,b):
    return a[0]*b[1]-a[1]*b[0]


def rotate(point, theta):
    c,s=cos(theta),sin(theta)
    x,y=point
    return (x*c-y*s,x*s+y*c)


def one_corner_bound(centre,theta,v,omega,index,n,anchor,touch):
    offset=rotate(VERTICES[index],theta)
    gap=dot((centre[0]+offset[0]-anchor[0],
             centre[1]+offset[1]-anchor[1]),n)
    slope=dot((v[0]-omega*offset[1],v[1]+omega*offset[0]),n)
    curvature=omega*omega*hypot(HALF,HALF)
    end_floor=gap+slope*POST_WINDOW-.5*curvature*POST_WINDOW**2
    derivative_floor=slope-curvature*POST_WINDOW
    if touch:
        accepted=abs(gap)<=TOL and derivative_floor>MIN_MARGIN
        margin=derivative_floor
    else:
        margin=min(gap,end_floor)
        accepted=margin>MIN_MARGIN
    return {
        "corner_index":index,
        "gap_at_third_contact":rd(gap),
        "outgoing_gap_rate":rd(slope),
        "curvature_upper_bound":rd(curvature),
        "end_gap_lower_bound":rd(end_floor),
        "rate_lower_bound":rd(derivative_floor),
        "conservative_margin":rd(margin),
        "starts_touching":bool(touch),
        "accepted":bool(accepted),
    }


def attempt(angle):
    source=former(angle)
    ancestor=old_impulse(angle)
    base={
        "schema":SCHEMA,
        "angle":rd(angle),
        "source_trial20_schema":source["schema"],
        "source_trial20_status":source["status"],
        "source_receiver":source["receiver"],
        "source_third_contact":source["next_contact"],
        "relative_third_contact_time":DURATION,
        "local_window":POST_WINDOW,
        "third_impulse_model_hypothesis":True,
        "measured_material_response":False,
        "fourth_contact_selected":False,
        "another_receiver_constructed":False,
        "formal_interval_certificate":False,
        "first_second_contact_sources_unchanged":True,
    }
    if source["status"]=="NO_SOURCE_SECOND_IMPULSE":
        if ancestor["candidate_impulse"] is not None:
            raise ValueError("source lineage became inconsistent")
        return {**base,"status":"NO_QUALIFYING_THIRD_CONTACT",
                "third_impulse":None,"clearance_bounds":[]}
    if source["status"]!="CONDITIONAL_DERIVED_RECEIVER_REACHED":
        return {**base,"status":"SOURCE_RECEIVER_NOT_ADMITTED",
                "third_impulse":None,"clearance_bounds":[]}
    h=ancestor["candidate_impulse"]
    if h is None:
        raise ValueError("world20 construction had no original second impulse")
    receiver=source["receiver"]
    event=source["next_contact"]
    corner=event["vertex_index"]
    if type(corner) is not int or corner not in range(4):
        raise ValueError("third contact corner was not a unique source vertex")
    normal=tuple(receiver["normal"])
    tangent=(-normal[1],normal[0])
    if abs(hypot(*normal)-1)>TOL:
        raise ValueError("receiver normal no longer unit")
    previous_v=tuple(h["velocity_after"])
    previous_w=h["angular_velocity_after"]
    centre=(h["contact_center"][0]+DURATION*previous_v[0],
            h["contact_center"][1]+DURATION*previous_v[1])
    theta=h["contact_angle"]+DURATION*previous_w
    r=rotate(VERTICES[corner],theta)
    point=(centre[0]+r[0],centre[1]+r[1])
    anchor=tuple(receiver["anchor"])
    vec=(point[0]-anchor[0],point[1]-anchor[1])
    along=dot(vec,tangent)
    before_rate=dot((previous_v[0]-previous_w*r[1],
                     previous_v[1]+previous_w*r[0]),normal)
    if (abs(dot(vec,normal))>TOL or
        abs(along-event["tangent_coordinate"])>TOL or
        not -0.5+TOL<along<0.5-TOL or
        any(abs(x-y)>TOL for x,y in zip(point,event["point"])) or
        abs(before_rate-event["incoming_normal_vertex_rate"])>TOL):
        raise ValueError("third contact moved relative to source-derived receiver")
    if before_rate>=-TOL:
        return {**base,"status":"UNRESOLVED_NONINCOMING_THIRD_CONTACT",
                "third_impulse":None,"clearance_bounds":[]}
    # A single finite corner must be the unique receiver support at arrival.
    gaps=[dot((centre[0]+rotate(v,theta)[0]-anchor[0],
               centre[1]+rotate(v,theta)[1]-anchor[1]),normal)
          for v in VERTICES]
    if (abs(gaps[corner])>TOL or
        any(v<=TOL for i,v in enumerate(gaps) if i!=corner)):
        return {**base,"status":"UNRESOLVED_SIMULTANEOUS_CONTACT",
                "third_impulse":None,"clearance_bounds":[]}
    arm=det(r,normal)
    j=-2*before_rate/(1+arm*arm/INERTIA)
    v=(previous_v[0]+j*normal[0],
       previous_v[1]+j*normal[1])
    w=previous_w+j*arm/INERTIA
    outgoing_rate=dot((v[0]-w*r[1],v[1]+w*r[0]),normal)
    eb=.5*dot(previous_v,previous_v)+.5*INERTIA*previous_w**2
    ea=.5*dot(v,v)+.5*INERTIA*w**2
    if (not all(isfinite(z) for z in (j,*v,w)) or j<=TOL or
        abs(outgoing_rate+before_rate)>TOL or abs(eb-ea)>TOL):
        raise ValueError("unsupported or nonconservative ideal third impulse")

    impulse={
        "receiver_id":receiver["id"],
        "contact_vertex_index":corner,
        "contact_point":[rd(z) for z in point],
        "contact_center":[rd(z) for z in centre],
        "contact_orientation":rd(theta),
        "contact_absolute_virtual_time":event["absolute_virtual_time"],
        "source_receiver_normal":[rd(z) for z in normal],
        "incoming_velocity":[rd(z) for z in previous_v],
        "outgoing_velocity":[rd(z) for z in v],
        "incoming_spin":rd(previous_w),
        "outgoing_spin":rd(w),
        "incoming_contact_normal_rate":rd(before_rate),
        "outgoing_contact_normal_rate":rd(outgoing_rate),
        "normal_impulse":rd(j),
        "lever_cross_normal":rd(arm),
        "kinetic_energy_before":rd(eb),
        "kinetic_energy_after":rd(ea),
        "law":"original frictionless unit-mass rigid square, restitution 1",
        "materially_witnessed":False,
    }
    bounds=[]
    conditions=[
        ("receiver",normal,anchor,corner),
        ("original_source",tuple(ancestor["source_first_contact"]["normal"]),
         tuple(WALL_CENTER),None),
        ("world_left",(1.,0.),(0.,0.),None),
        ("world_right",(-1.,0.),(WORLD_WIDTH,0.),None),
        ("world_bottom",(0.,1.),(0.,0.),None),
        ("world_top",(0.,-1.),(0.,WORLD_HEIGHT),None),
    ]
    for name,n,a,touch in conditions:
        for i in range(4):
            z=one_corner_bound(centre,theta,v,w,i,n,a,touch==i)
            bounds.append({"surface":name,**z})
    admitted=all(z["accepted"] for z in bounds)
    return {
        **base,
        "status":("CONDITIONAL_LOCAL_SEPARATION" if admitted
                  else "UNRESOLVED_POST_THIRD_CONTACT_GEOMETRY"),
        "third_impulse":impulse,
        "clearance_bounds":bounds,
        "local_separation_only":admitted,
        "source_finite_faces_unchanged":True,
        "hypothetical_outgoing_motion_only":True,
    }


def run():
    cases=[attempt(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"source_trial20":"world-ab-rotating-source-derived-receiver/v1",
        "angles":list(ANGLES),"cases":cases,
        "candidate_third_impulses":sum(c["third_impulse"] is not None for c in cases),
        "local_conditional_separations":sum(c["status"]=="CONDITIONAL_LOCAL_SEPARATION" for c in cases),
        "cases_without_qualifying_third_contact":sum(c["status"]=="NO_QUALIFYING_THIRD_CONTACT" for c in cases),
        "real_material_behavior_verified":False,
        "another_receiver_created":False,
        "general_multicontact_solver_present":False,
    }
