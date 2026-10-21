"""WORLD34: original finite contact geometry inside WORLD33's FIRST unknown.

Only a source-qualified hypothetical fourth-response case with a WORLD33
first-unverified small interval is eligible. Inspect the *finite* original
face against the rotating square at the interval ends and midpoint. If the
source finite clip changes from separated to intersecting, bisect JUST that
interval; attempt to identify a unique incoming corner on the same finite
face. Do not invent an impact for a failed, tangential, simultaneous or
endpoint feature.

The original physical fourth response remains unselected. No fifth impulse,
new receiver or source motion after the first unknown is calculated.
"""
from __future__ import annotations

from math import cos,sin,hypot,isfinite
from systems.workspace.world_ab_local_plane_prefix import attempt as source33,SCHEMA as SOURCE33
from systems.workspace.world_ab_first_finite_response_qualification import attempt as source29
from systems.workspace.world_ab_third_contact import attempt as source21,ANGLES
from systems.workspace.world_ab_finite_segment_square_overlap import static_faces,finite_clip
from systems.workspace.world_ab_first_post_third_candidate import surfaces
from systems.workspace.world_ab_oblique_impact import HALF

SCHEMA="world-ab-first-unknown-finite-contact-feature/v1"
EDGE_EPS=3e-6
RATE_EPS=1e-5
LOCAL_CORNERS=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def rd(x):
    return round(float(x),12)


def dot(a,b):
    return a[0]*b[0]+a[1]*b[1]


def point(model,i,t):
    x,y=LOCAL_CORNERS[i]
    angle=model["contact_orientation"]+model["outgoing_spin"]*t
    co,si=cos(angle),sin(angle)
    lever=(co*x-si*y,si*x+co*y)
    center=(model["contact_center"][0]+model["outgoing_velocity"][0]*t,
            model["contact_center"][1]+model["outgoing_velocity"][1]*t)
    return center,lever,(center[0]+lever[0],center[1]+lever[1])


def investigate_face(model,original,name,segment,lo,hi):
    left=finite_clip(model,segment,lo)
    mid=finite_clip(model,segment,(lo+hi)/2)
    right=finite_clip(model,segment,hi)
    base={
        "source_face":name,
        "original_finite_segment":segment,
        "first_unknown_interval":[lo,hi],
        "sampled_overlap_left":left["overlap"],
        "sampled_overlap_midpoint":mid["overlap"],
        "sampled_overlap_right":right["overlap"],
        "numerical_root_not_formally_certified":True,
        "material_contact_measured":False,
    }
    if left["overlap"] or not right["overlap"]:
        return {**base,"status":"NO_SEPARATED_TO_INTERSECTING_ENDPOINT_BRACKET",
                "refined_model_transition_time":None,
                "candidate_source_corners":[],
                "qualified_unique_incoming_corner":None}
    a,b=lo,hi
    for _ in range(52):
        half=(a+b)/2
        if finite_clip(model,segment,half)["overlap"]:
            b=half
        else:
            a=half
    defs=[(tuple(n),tuple(anchor),span)
          for label,n,anchor,span in surfaces(original,original["angle"])
          if label==name and span is not None]
    if len(defs)!=1:
        raise ValueError("original source finite segment identity changed")
    n,anchor,span=defs[0]
    tangent=(-n[1],n[0])
    candidates=[]
    for i in range(4):
        center,r,p=point(model,i,b)
        d=(p[0]-anchor[0],p[1]-anchor[1])
        gap=dot(d,n)
        along=dot(d,tangent)
        rate=dot((model["outgoing_velocity"][0]-model["outgoing_spin"]*r[1],
                  model["outgoing_velocity"][1]+model["outgoing_spin"]*r[0]),n)
        if abs(gap)<=EDGE_EPS and abs(along)<span/2-EDGE_EPS:
            candidates.append({
                "source_corner_index":i,
                "normal_gap":rd(gap),
                "finite_face_tangent_coordinate":rd(along),
                "incoming_normal_rate":rd(rate),
                "contact_model_position":[rd(z) for z in p],
                "source_face":name,
            })
    incoming=[c for c in candidates if c["incoming_normal_rate"]<-RATE_EPS]
    qualified=incoming[0] if len(candidates)==len(incoming)==1 else None
    status=("UNIQUE_INCOMING_FINITE_CORNER_MODEL_CANDIDATE" if qualified else
            "FINITE_MODEL_TRANSITION_BUT_CONTACT_FEATURE_UNRESOLVED")
    return {**base,"status":status,
            "refined_model_transition_time":rd(b),
            "candidate_source_corners":candidates,
            "qualified_unique_incoming_corner":qualified}


def attempt(angle):
    before=source33(angle)
    prior=source29(angle)
    original=source21(angle)
    base={
        "schema":SCHEMA,"angle":float(angle),
        "source_trial33_schema":SOURCE33,
        "source_trial33_status":before["status"],
        "source_first_unknown_subinterval":before["first_unknown_subinterval"],
        "source_supported_prefix_end":before["supported_prefix_end_time"],
        "source_conditional_fourth_response":prior["conditional_fourth_response"],
        "original_world":[24.,6.],
        "original_static_finite_faces":2,
        "conditional_unselected_response_only":True,
        "material_fifth_impact_witnessed":False,
        "fifth_impulse_selected":False,
        "real_material_trajectory_authenticated":False,
        "new_receiver_constructed":False,
        "continuation_after_first_unknown_solved":False,
    }
    if before["status"]!="FIRST_LOCAL_HALFPLANE_BOUND_UNRESOLVED":
        return {**base,"status":"NO_UNRESOLVED_SOURCE_LOCAL_INTERVAL",
                "source_finite_face_probes":[],
                "earliest_local_model_candidate":None,
                "unique_incoming_source_feature":None}
    interval=before["first_unknown_subinterval"]
    lo,hi=interval["start"],interval["end"]
    feature=prior["qualifying_source_feature"]
    response=prior["conditional_fourth_response"]
    if (feature is None or response is None or
        abs(lo-before["supported_prefix_end_time"])>2e-8 or
        not 0<=lo<hi<=.25):
        raise ValueError("unverified source first-unknown ancestry")
    h={
        "contact_center":list(feature["contact_center"]),
        "contact_orientation":feature["contact_angle"],
        "outgoing_velocity":list(response["outgoing_velocity"]),
        "outgoing_spin":response["outgoing_spin"],
    }
    faces=static_faces(original,angle)
    if len(faces)!=2:
        raise ValueError("original two finite source faces missing")
    probes=[investigate_face(h,original,name,segment,lo,hi)
            for name,segment in faces]
    transitions=[x for x in probes if x["refined_model_transition_time"] is not None]
    transitions.sort(key=lambda x:(x["refined_model_transition_time"],x["source_face"]))
    first=transitions[0] if transitions else None
    if first is None:
        status="FIRST_LOCAL_UNKNOWN_WITH_NO_FINITE_TRANSITION_BRACKET"
    elif (len(transitions)>1 and
          abs(transitions[1]["refined_model_transition_time"]-
              first["refined_model_transition_time"])<3e-7):
        status="SIMULTANEOUS_FINITE_MODEL_FEATURE_UNRESOLVED"
    elif first["qualified_unique_incoming_corner"] is None:
        status="FINITE_OVERLAP_TRANSITION_FEATURE_UNRESOLVED"
    else:
        status="FIRST_FINITE_MODEL_CORNER_TRANSITION_QUALIFIED"
    qualified=(first["qualified_unique_incoming_corner"]
               if status=="FIRST_FINITE_MODEL_CORNER_TRANSITION_QUALIFIED" else None)
    return {**base,"status":status,
            "source_finite_face_probes":probes,
            "earliest_local_model_candidate":first,
            "unique_incoming_source_feature":qualified}


def run():
    cases=[attempt(angle) for angle in ANGLES]
    return {"schema":SCHEMA,"angles":list(ANGLES),"cases":cases,
            "source_first_unknown_cases":sum(c["source_first_unknown_subinterval"] is not None
                                             for c in cases),
            "finite_overlap_transition_cases":sum(
                c["earliest_local_model_candidate"] is not None for c in cases),
            "uniquely_incoming_finite_corner_cases":sum(
                c["unique_incoming_source_feature"] is not None for c in cases),
            "inactive_source_controls":sum(
                c["status"]=="NO_UNRESOLVED_SOURCE_LOCAL_INTERVAL" for c in cases),
            "material_contacts_measured":0,
            "fifth_impulses_selected":0,
            "new_receivers":0,
            "new_engine_or_world":False}
