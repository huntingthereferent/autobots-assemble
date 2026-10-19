"""WORLD A/B trial 03 — sequential relation-driven physical construction.

The generator sees ONLY collision events, source geometry, and a fixed
clearance-aware assembly policy, not target blueprint-shape names. At each
outgoing impact, build a new one-sided straight receiver in the free corridor
when there is physical clearance; otherwise record rejection. A new receiver
is activated AT its originating contact, never retroactively.

A single rigid 2-D translating square, no gravity/friction/spin; one virtual
source wall and dynamically generated collision faces. This cannot prove
spontaneous material assembly, real Earth physics, or emergent curves.
"""
from __future__ import annotations
from math import isfinite
from systems.workspace.world_ab_contact_trial import (
    HALF,WALL,WORLD_WIDTH,WORLD_HEIGHT,initial,trial)

SCHEMA="world-ab-contact-derived-sequential-construction/v1"
DURATION=5.0
MAX_EVENTS=30
MAX_NEW_SURFACES=12
PROJECTION_TIME=0.75
SPAN=1.
TOL=1e-8

def rd(n):
    return round(float(n),9)

def source():
    return {"id":"source-wall","face_x":float(WALL["x"]),
            "y_min":float(WALL["y"]),"y_max":float(WALL["y"]+1),
            "normal":[-1.,0.],"active_at":0.0,"source_contact_index":None}

def _active_hit(x,y,vx,vy,time,surfaces):
    candidates=[]
    for s in surfaces:
        normal=s["normal"][0]
        if vx*normal>=-TOL:continue
        cx=s["face_x"]+normal*HALF
        t=(cx-x)/vx
        if t<=TOL or t>DURATION-time+TOL:continue
        cy=y+vy*t
        if s["y_min"]-HALF-TOL<=cy<=s["y_max"]+HALF+TOL:
            candidates.append((t,s["id"],s))
    if not candidates:return None
    return min(candidates,key=lambda c:(c[0],c[1]))

def _construct(contact,existing):
    """Propose from observed output; projection time and nearest face clearance.

    There is no target-shape name, no desired output graph in this routine.
    A face is vertical because the declared translational source model has
    only x-normal contact response. Reject if a corridor would be narrower
    than the square diameter, or the new face overlaps another one.
    """
    vx,vy=contact["outgoing_velocity"]
    px,py=contact["point"]
    if abs(vx)<=TOL:
        return {"accepted":False,"reason":"NO_REBOUND","candidate":None}
    sign=1 if vx>0 else -1
    ahead=[abs(s["face_x"]-px) for s in existing
           if (s["face_x"]-px)*sign>TOL and s["normal"][0]*vx < -TOL]
    max_distance=PROJECTION_TIME*abs(vx)
    distance=min(max_distance,min(ahead)/2 if ahead else max_distance)
    face=px+sign*distance
    center_y=py+vy*distance/abs(vx)
    proposal={"id":f"generated-face-{len(existing)}",
             "face_x":rd(face),
             "y_min":rd(center_y-SPAN/2),
             "y_max":rd(center_y+SPAN/2),
             "normal":[float(-sign),0.],
             "active_at":contact["time"],
             "source_contact_index":contact["index"]}
    if (distance<=HALF+TOL or
        face<=HALF+TOL or face>=WORLD_WIDTH-HALF-TOL or
        proposal["y_min"]<HALF or proposal["y_max"]>WORLD_HEIGHT-HALF):
        return {"accepted":False,"reason":"NO_ADMISSIBLE_CLEARANCE","candidate":proposal}
    for other in existing:
        overlap_y=(proposal["y_min"]<=other["y_max"]+2*HALF and
                   proposal["y_max"]>=other["y_min"]-2*HALF)
        if overlap_y and abs(face-other["face_x"])<=2*HALF+TOL:
            return {"accepted":False,"reason":"FACES_TOO_CLOSE_FOR_BLOCK","candidate":proposal}
    if len(existing)-1>=MAX_NEW_SURFACES:
        return {"accepted":False,"reason":"BOUNDED_SURFACE_LIMIT","candidate":proposal}
    return {"accepted":True,"reason":"CONTACT_DERIVED_CLEARANCE_ALLOWED","candidate":proposal}

def run(start=None):
    s=initial(**(start or {}))
    original=trial(s)
    x,y,vx,vy=[s[k] for k in ("x","y","vx","vy")]
    t=0.
    objects=[source()]
    events=[]
    proposals=[]
    motions=[{"time":0.,"x":rd(x),"y":rd(y),"vx":rd(vx),"vy":rd(vy),
              "phase":"initial"}]
    for index in range(MAX_EVENTS):
        next_hit=_active_hit(x,y,vx,vy,t,objects)
        if next_hit is None:
            x+=vx*(DURATION-t);y+=vy*(DURATION-t);t=DURATION
            break
        delta,_,surface=next_hit
        hit_t=t+delta
        if hit_t>DURATION+TOL:break
        x+=vx*delta;y+=vy*delta;t=hit_t
        incoming=[vx,vy]
        old_energy=.5*(vx*vx+vy*vy)
        vx=-s["restitution"]*vx
        event={"index":len(events),"time":rd(t),"source_surface_id":surface["id"],
               "point":[rd(x),rd(y)],
               "incoming_velocity":[rd(z) for z in incoming],
               "outgoing_velocity":[rd(vx),rd(vy)],
               "normal":list(surface["normal"]),
               "impulse":rd((1+s["restitution"])*abs(incoming[0])),
               "energy_before":rd(old_energy),
               "energy_after":rd(.5*(vx*vx+vy*vy))}
        events.append(event)
        motions.append({"time":rd(t),"x":rd(x),"y":rd(y),
                        "vx":rd(vx),"vy":rd(vy),"phase":"contact"})
        proposal=_construct(event,objects)
        proposals.append({"contact_index":event["index"],**proposal})
        if proposal["accepted"]:
            objects.append(proposal["candidate"])
        if len(events)>=MAX_EVENTS:raise ValueError("bounded contact-event budget exceeded")
    if t<DURATION-TOL:
        raise ValueError("not enough model time consumed")
    motions.append({"time":rd(t),"x":rd(x),"y":rd(y),
                    "vx":rd(vx),"vy":rd(vy),"phase":"terminal"})
    if any(not (0<=m["x"]<=WORLD_WIDTH and 0<=m["y"]<=WORLD_HEIGHT) for m in motions):
        raise ValueError("sequential relation-derived path exits virtual world")
    if events and (
        abs(events[0]["time"]-original["B_with_wall"]["contacts"][0]["time"])>TOL or
        events[0]["source_surface_id"]!="source-wall" or
        events[0]["point"]!=[original["B_with_wall"]["contacts"][0]["x"],
                             original["B_with_wall"]["contacts"][0]["y"]]):
        raise ValueError("original first contact changed")
    return {"schema":SCHEMA,"input":s,"duration":DURATION,"half_extent":HALF,
            "physics":"2D translational rigid square; event-time x-normal restitution; no Earth-scale calibration",
            "source_world_dimensions":[WORLD_WIDTH,WORLD_HEIGHT],
            "source_original_wall_preserved":True,
            "surfaces":objects,"events":events,"construction_attempts":proposals,
            "motions":motions,"final":motions[-1],
            "generated_surface_count":len(objects)-1,
            "straight_vertical_faces_only":True,
            "spontaneous_material_self_assembly":False,
            "full_original_visual_blueprint_generated":False,
            "original_target_shape_names_used_in_generator":False}
