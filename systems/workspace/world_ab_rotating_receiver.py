"""WORLD20: construct one finite receiver from the square's Trial18 movement.

No new engine, laws or object kinds. Under the SAME conditional second impulse,
project the square's moving/rotating geometry 0.25 original virtual-time units.
Construct a finite straight receiver normal to the outgoing centre velocity,
positioned where its actual rotated supporting corner would first touch at
that endpoint. Admit ONLY if the entire intervening path stays outside the
original face, original WORLD perimeter and the proposed receiver itself.

The model predicts geometry; it does not witness spontaneous assembly, choose
a material contact law, solve the resulting third impulse or claim hardware.
All bounds are floating numerical results, not certified interval arithmetic.
"""
from __future__ import annotations

from math import acos, atan2, ceil, cos, hypot, isfinite, pi, sin
from systems.workspace.world_ab_local_recontact_impulse import attempt as prior
from systems.workspace.world_ab_oblique_impact import HALF, WALL_CENTER, SPAN

SCHEMA="world-ab-rotating-source-derived-receiver/v1"
ANGLES=(0.,2.5,5.,7.5,10.,12.25,15.,20.)
DURATION=.25
WORLD=(24.,6.)
VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))
EPS=2e-7

def rd(x):
    return round(float(x),10)

def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]

def rotate(point,theta):
    x,y=point;c=cos(theta);s=sin(theta)
    return (x*c-y*s,x*s+y*c)

def motion(impulse,t):
    v=impulse["velocity_after"];c=impulse["contact_center"]
    angle=impulse["contact_angle"]+impulse["angular_velocity_after"]*t
    center=(c[0]+t*v[0],c[1]+t*v[1])
    return center,angle

def corners(impulse,t):
    center,theta=motion(impulse,t)
    return [(center[0]+r[0],center[1]+r[1])
            for r in (rotate(p,theta) for p in VERTICES)]

def _critical_times(impulse,normal,tmax):
    """Every stationary time for a rotating corner's line-distance."""
    v=tuple(impulse["velocity_after"])
    theta=impulse["contact_angle"]
    w=impulse["angular_velocity_after"]
    times={}
    for i,vertex in enumerate(VERTICES):
        r=rotate(vertex,theta)
        A=dot(r,normal);B=dot((-r[1],r[0]),normal)
        vn=dot(v,normal)
        one=[0.,tmax]
        amplitude=hypot(A,B)
        if abs(w)>1e-12 and amplitude>1e-12:
            q=-vn/(w*amplitude)
            if -1.<=q<=1.:
                alpha=acos(max(-1.,min(1.,q)))
                phi=atan2(A,B)
                limit=ceil(abs(w)*tmax/(2*pi))+3
                for k in range(-limit,limit+1):
                    for sign in (-1,1):
                        t=(sign*alpha-phi+2*pi*k)/w
                        if 1e-12<t<tmax-1e-12:
                            one.append(t)
        times[i]=sorted(set(one))
    return times

def gap(impulse,normal,anchor,index,t):
    p=corners(impulse,t)[index]
    return dot((p[0]-anchor[0],p[1]-anchor[1]),normal)

def gap_rate(impulse,normal,index,t):
    center,theta=motion(impulse,t)
    r=rotate(VERTICES[index],theta)
    v=tuple(impulse["velocity_after"])
    w=impulse["angular_velocity_after"]
    return dot((v[0]-w*r[1],v[1]+w*r[0]),normal)

def _check(impulse,normal,anchor,duration,kind,touch_corner=None):
    """Whole-interval line-sided clearance at all exact stationary times.

    For the source one already-touching corner moves AWAY at start. For the
    receiver one vertex approaches at endpoint. Other corner extrema must
    remain positive. Boundary halfplanes require positive throughout.
    """
    extrema=_critical_times(impulse,normal,duration)
    minimum=float("inf")
    for i,times in extrema.items():
        values=[gap(impulse,normal,anchor,i,t) for t in times]
        if kind=="source" and i==touch_corner:
            if abs(values[0])>EPS or gap_rate(impulse,normal,i,0.)<=EPS:
                return False,"source-corner-not-separating",None
            # t=0 is the original contact; moving away must remain true.
            if any(z<=EPS for z in values[1:]):
                return False,"source-recontact",None
        elif kind=="receiver":
            if values[0]<=EPS:
                return False,"receiver-already-penetrating",None
            if i==touch_corner:
                if abs(values[-1])>EPS or gap_rate(impulse,normal,i,duration)>=-EPS:
                    return False,"receiver-endpoint-not-incoming",None
                if any(z<=EPS for z in values[1:-1]):
                    return False,"receiver-prior-contact",None
            elif any(z<=EPS for z in values):
                return False,"receiver-other-vertex-reaches-early",None
        elif any(z<=EPS for z in values):
            return False,kind+"-halfspace-crossing",None
        minimum=min(minimum,*values)
    return True,"whole-interval-stationary-extrema",minimum

def trial(angle):
    old=prior(angle)
    common={
        "schema":SCHEMA,
        "source_trial18_schema":old["schema"],
        "source_angle":rd(angle),
        "source_first_return":old["source_trial17_first_return"],
        "original_source_wall_center":list(WALL_CENTER),
        "projection_duration":DURATION,
        "construction_policy":"normal opposite recorded outgoing centre velocity; pose-supported future face",
        "model_movement_not_hardware_measurement":True,
        "third_impulse_calculated":False,
        "receiver_real_material_built":False,
        "nominal_floating_point_not_formal_interval":True,
        "earlier_world_sources_unchanged":True,
    }
    h=old["candidate_impulse"]
    if h is None:
        if old["status"]!="NO_ADMITTED_RENEWED_CONTACT":
            raise ValueError("missing source response")
        return {**common,"status":"NO_SOURCE_SECOND_IMPULSE",
                "receiver":None,"next_contact":None,"frames":[]}
    v=tuple(h["velocity_after"])
    length=hypot(*v)
    if length<=EPS:
        return {**common,"status":"NO_OUTGOING_TRANSLATION",
                "receiver":None,"next_contact":None,"frames":[]}
    normal=(-v[0]/length,-v[1]/length)
    tangent=(-normal[1],normal[0])
    target_center,theta=motion(h,DURATION)
    offsets=[rotate(p,theta) for p in VERTICES]
    projections=[dot(r,normal) for r in offsets]
    minimum=min(projections)
    target_vertex=min(range(4),key=lambda i:(projections[i],i))
    # A plane at the *rotated* body's supporting corner at proposed time.
    anchor=(target_center[0]+minimum*normal[0],
            target_center[1]+minimum*normal[1])
    # Using source linear law, a shape-specific contact support determines
    # the receiver location. No visual blueprint is fed to this construction.
    ends=[(anchor[0]+sign*SPAN/2*tangent[0],
           anchor[1]+sign*SPAN/2*tangent[1]) for sign in (-1,1)]
    if any(not (0<=z[0]<=WORLD[0] and 0<=z[1]<=WORLD[1]) for z in ends):
        return {**common,"status":"RECEIVER_OUTSIDE_WORLD",
                "receiver":None,"next_contact":None,"frames":[]}
    source_normal=tuple(old["source_first_contact"]["normal"])
    source_anchor=tuple(WALL_CENTER)
    for index,s in enumerate(((-1.,0.),(1.,0.),(0.,-1.),(0.,1.))):
        a=(0.,0.) if index in (0,2) else (WORLD[0],WORLD[1])
        # For right and top edges use a point with the relevant bound.
        ok,reason,_=_check(h,s,a,DURATION,"world")
        if not ok:
            return {**common,"status":"UNRESOLVED_"+reason,
                    "receiver":None,"next_contact":None,"frames":[]}
    touch=h["contact_vertex_index"]
    ok,reason,_=_check(h,source_normal,source_anchor,DURATION,"source",touch)
    if not ok:
        return {**common,"status":"UNRESOLVED_"+reason,
                "receiver":None,"next_contact":None,"frames":[]}
    ok,reason,_=_check(h,normal,anchor,DURATION,"receiver",target_vertex)
    if not ok:
        return {**common,"status":"UNRESOLVED_"+reason,
                "receiver":None,"next_contact":None,"frames":[]}
    point=corners(h,DURATION)[target_vertex]
    along=dot((point[0]-anchor[0],point[1]-anchor[1]),tangent)
    if abs(along)>=SPAN/2-EPS:
        return {**common,"status":"RECEIVER_FINITE_FACE_MISSED",
                "receiver":None,"next_contact":None,"frames":[]}
    if any(dot((p[0]-source_anchor[0],p[1]-source_anchor[1]),source_normal)<EPS
           for p in ends):
        return {**common,"status":"DERIVED_SURFACE_OVERLAPS_SOURCE_HALFSPACE",
                "receiver":None,"next_contact":None,"frames":[]}
    receiver={
        "id":"motion-derived-finite-receiver",
        "anchor":[rd(z) for z in anchor],
        "normal":[rd(z) for z in normal],
        "endpoints":[[rd(z) for z in p] for p in ends],
        "constructed_from":"Trial18 conditional outgoing velocity and square rotation",
        "source_corner":touch,
        "activated_at_relative_time":0.,
        "proposed_target_time":DURATION,
    }
    next_contact={
        "at_relative_time":DURATION,
        "absolute_virtual_time":rd(h["contact_time_relative"]+old["source_first_contact"]["first_contact_time"]+DURATION),
        "vertex_index":target_vertex,
        "point":[rd(z) for z in point],
        "tangent_coordinate":rd(along),
        "incoming_normal_vertex_rate":rd(gap_rate(h,normal,target_vertex,DURATION)),
        "geometric_touch_only":True,
        "third_impulse_assumed":False,
    }
    times=[DURATION*i/10 for i in range(11)]
    frames=[]
    for t in times:
        center,ang=motion(h,t)
        frames.append({"time":rd(t),"center":[rd(z) for z in center],
                       "orientation":rd(ang)})
    return {
        **common,"status":"CONDITIONAL_DERIVED_RECEIVER_REACHED",
        "receiver":receiver,
        "next_contact":next_contact,
        "frames":frames,
        "source_clearance_entire_interval_checked":True,
        "receiver_clearance_entire_interval_checked":True,
        "world_boundary_clearance_entire_interval_checked":True,
        "third_collision_outcome_unresolved":True,
    }

def run():
    cases=[trial(a) for a in ANGLES]
    return {
        "schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
        "conditional_receiver_arrivals":sum(c["status"]=="CONDITIONAL_DERIVED_RECEIVER_REACHED" for c in cases),
        "no_source_second_impulse":sum(c["status"]=="NO_SOURCE_SECOND_IMPULSE" for c in cases),
        "real_material_receiver_fabricated":False,
        "new_engine_or_world_created":False,
    }
