"""WORLD Trial 09: predeclared incidence/surface perturbations, not sourced 04B geometry.

The original Trial 07 contact point and source faces are immutable parents. One
branch uses their exact geometry. Other branches deliberately rotate the SECOND
face around its measured contact point (with the necessary normal offset to
keep one shared disc center), and are explicitly synthetic controls. Every
incoming ray is set to hit that point after 0.35 units. The existing Trial 08
frictionless simultaneous impulse is evaluated without modifications; physical
incompatibility is reported as rejection, never converted into acceptance.
"""
from __future__ import annotations
from copy import deepcopy
from math import cos,sin,radians,hypot
from systems.workspace.world_ab_junction_threshold import run as threshold_run,arrival_pair
from systems.workspace.world_ab_two_contact_candidate import run as trial08_run,solve_two_normals
from systems.workspace.world_ab_junction_continuous import nearest,dot,sub,add,mul,R,HORIZON,STEP

SCHEMA="world-ab-two-contact-incidence-stress/v1"
ANGLES=(-15,-5,0,10,20,30,45)
OFFSETS=(-15.,-7.5,0.,7.5,15.)
SPEED=2.
LEAD=.35
EPS=1e-8

def rounded(x):return round(float(x),9)
def rotate(p,angle):
    a=radians(angle);c=cos(a);s=sin(a)
    return (p[0]*c-p[1]*s,p[0]*s+p[1]*c)

def arrangement(faces,contact_center,normals,offset):
    if offset==0:
        return deepcopy(faces),[tuple(z) for z in normals],"original-source-geometry"
    # Purposeful counterfactual. Do not inherit fake Trial04B source IDs or
    # receipt claims on altered face B.
    n0,n1=map(tuple,normals)
    new_n1=rotate(n1,offset)
    q_old=sub(contact_center,mul(R,n1))
    q_new=sub(contact_center,mul(R,new_n1))
    new_endpoints=[]
    for endpoint in faces[1]["endpoints"]:
        shifted=add(q_new,rotate(sub(endpoint,q_old),offset))
        new_endpoints.append([round(x,12) for x in shifted])
    changed={"id":"controlled-face-B-"+str(offset),
             "source_parent_id":faces[1]["id"],
             "geometry_role":"explicit-rotated-counterfactual",
             "rotation_degrees":offset,"endpoints":new_endpoints}
    return [deepcopy(faces[0]),changed],[n0,new_n1],"controlled-geometry-not-original"

def examine(angle,offset,faces,contact_center,normals):
    surfaces,ns,kind=arrangement(faces,contact_center,normals,offset)
    vin=(-SPEED*cos(radians(angle)),-SPEED*sin(radians(angle)))
    start=sub(contact_center,mul(LEAD,vin))
    rec={"incoming_angle_degrees":angle,"surface_B_rotation_degrees":offset,
         "geometry_kind":kind,"surfaces":surfaces,
         "incoming_velocity":[rounded(x) for x in vin],
         "start_center":[rounded(x) for x in start],
         "contact_center":[rounded(x) for x in contact_center],
         "normals":[[rounded(q) for q in n] for n in ns],
         "contact_at":LEAD}
    # Check authentic finite capsule tangency at the constructed comparison
    # center. No new source generation is claimed by this control.
    if any(abs(nearest(contact_center,s)[0]-R)>3e-7 for s in surfaces):
        raise ValueError("controlled source geometry is not tangent at common contact")
    for s,n in zip(surfaces,ns):
        a,b=s["endpoints"];v=sub(b,a);q=sub(contact_center,mul(R,n))
        fraction=dot(sub(q,a),v)/dot(v,v)
        if not 1e-8<fraction<1-1e-8:
            raise ValueError("control contact moved off finite segment interior")
    if not (R<start[0]<24-R and R<start[1]<6-R):
        raise ValueError("controlled initial point outside source world")
    try:
        result=solve_two_normals(vin,ns)
    except ValueError as e:
        if str(e)=="contact requires negative or inactive normal impulse":
            return {**rec,"status":"rejected-unilateral","reason":str(e),"candidate":None,"frames":[]}
        if str(e)=="not a simultaneous incoming pair":
            return {**rec,"status":"rejected-not-incoming","reason":str(e),"candidate":None,"frames":[]}
        return {**rec,"status":"rejected-constraint","reason":str(e),"candidate":None,"frames":[]}
    vout=tuple(result["outgoing_velocity"])
    # Analytic continuous clearance, not a visual/sample-only inference:
    # throughout pre-/post-impact movement, signed distance to EACH line
    # is R+(-vin·n)*(LEAD-t) or R+(vout·n)*(t-LEAD).
    # Distance to a finite segment is >= distance to its supporting line.
    for n in ns:
        if dot(vin,n)>=-EPS or dot(vout,n)<=EPS:
            raise ValueError("candidate had no continuous separation from source line")
    frames=[]
    for i in range(round(HORIZON/STEP)+1):
        t=i*STEP
        p=add(start,mul(t,vin)) if t<=LEAD else add(contact_center,mul(t-LEAD,vout))
        if not (R<=p[0]<=24.-R and R<=p[1]<=6.-R):
            raise ValueError("accepted candidate exited bounded WORLD")
        if any(nearest(p,s)[0]<R-3e-7 for s in surfaces):
            raise ValueError("accepted candidate penetrated finite surface")
        frames.append({"time":rounded(t),"position":[rounded(x) for x in p],
                       "velocity":[rounded(x) for x in (vin if t<LEAD else vout)]})
    reverse=solve_two_normals(vin,list(reversed(ns)))
    if reverse["outgoing_velocity"]!=result["outgoing_velocity"] or reverse["normal_impulses"]!=list(reversed(result["normal_impulses"])):
        raise ValueError("same actual physics depended on surface declaration order")
    return {**rec,"status":"accepted-local-candidate","reason":None,
            "candidate":result,"frames":frames}

def run():
    source=threshold_run()
    prior=trial08_run()
    if prior["baseline_trial06_status"]!="unresolved-multiple-contacts":
        raise ValueError("Trial 08 failed to retain original Trial 06 stop")
    geom=source["source_geometry"];faces=geom["surfaces"]
    y=source["junction_contact"]["entry_y"]
    touches=arrival_pair(y,faces)
    center=tuple(touches[0]["center"])
    normals=[h["normal"] for h in touches]
    if hypot(*sub(center,touches[1]["center"]))>1e-8:
        raise ValueError("original two-contact geometry drifted")
    cases=[examine(angle,offset,faces,center,normals)
           for offset in OFFSETS for angle in ANGLES]
    counts={k:sum(c["status"]==k for c in cases)
            for k in ("accepted-local-candidate","rejected-unilateral",
                      "rejected-not-incoming","rejected-constraint")}
    return {"schema":SCHEMA,"original_source_geometry":geom,
            "original_trial07_contact":source["junction_contact"],
            "original_trial08_outgoing":prior["candidate"]["outgoing_velocity"],
            "incoming_angle_grid":list(ANGLES),"surface_rotation_grid":list(OFFSETS),
            "speed":SPEED,"controlled_contact_lead":LEAD,
            "cases":cases,"counts":counts,
            "original_trial06_friction":.4,"candidate_friction":0.,
            "original_surface_modified":False,
            "rotated_faces_are_original_source":False,
            "general_two_contact_physics_proven":False,
            "frictional_manifold_solved":False,
            "real_material_equivalence":False,
            "original_blueprint_generated":False}
