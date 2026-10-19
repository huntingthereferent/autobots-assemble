"""WORLD Trial 10 — enumerate, do not choose, local frictionless impact active sets.

Source: complete predeclared Trial 09 7x5 experiment. No original Trial 05–09
physics/geometry source is changed. At each already-observed or explicitly
synthetic simultaneous two-face arrival, inspect {A}, {B}, {A,B} under *one*
specified instantaneous e=1, mu=0 active-set model.

Unilateral, energy, source-normal, full 24x6 bound, and continuous post-contact
separation gates classify candidates. Surviving alternatives are NOT grounds
for choosing which impulse an actual material would take. Rejected Trial 09
two-active candidates stay rejected; admissible single-active candidates do
not repair the old solver or imply real sequential native collisions.
"""
from __future__ import annotations
from math import cos,sin,radians,hypot
from systems.workspace.world_ab_two_contact_stress import run as stress_run, ANGLES,OFFSETS,LEAD,SPEED
from systems.workspace.world_ab_two_contact_candidate import solve_two_normals
from systems.workspace.world_ab_junction_continuous import nearest,dot,add,mul,R,HORIZON,STEP

SCHEMA="world-ab-two-contact-active-set-enumeration/v1"
ACTIVE_SETS=((0,),(1,),(0,1))
IMPACT_RESTITUTION=1.
IMPACT_FRICTION=0.
EPS=1e-8

def rd(q):return round(float(q),9)

def evaluate(case,active):
    angle=case["incoming_angle_degrees"]
    v=(-SPEED*cos(radians(angle)),-SPEED*sin(radians(angle)))
    n=[tuple(x) for x in case["normals"]]
    faces=case["surfaces"]
    center=tuple(case["contact_center"])
    start=tuple(case["start_center"])
    rec={"active_indices":list(active),"active_ids":[faces[i]["id"] for i in active]}
    def reject(code):
        return {**rec,"status":"rejected-"+code,"reason":code,
                "normal_impulses":None,"outgoing_velocity":None,"frames":[]}
    try:
        if len(active)==2:
            impulse=solve_two_normals(v,n)
            js=impulse["normal_impulses"]
            out=tuple(impulse["outgoing_velocity"])
        else:
            k=active[0]
            approach=dot(v,n[k])
            if approach>=-EPS:return reject("nonincoming-active")
            j=-2*approach
            if j<=EPS:return reject("nonpositive-impulse")
            js=[0.,0.];js[k]=j
            out=add(v,mul(j,n[k]))
    except ValueError as e:
        return reject("two-active-"+str(e).replace(" ","-"))
    if min(js[k] for k in active)<=EPS:return reject("nonpositive-impulse")
    if any(js[k]<-EPS for k in range(2)):return reject("negative-inactive")
    if any(dot(out,n[k]) < -EPS for k in range(2)):
        return reject("other-face-inward")
    if any(abs(dot(out,n[k])+dot(v,n[k]))>4e-8 for k in active):
        return reject("active-restitution")
    # Frictionless stationary surfaces imply conservation of kinetic energy
    # for these elastic projected impulses; fail closed on disagreement.
    if abs(dot(v,v)-dot(out,out))>4e-8:return reject("energy")
    # Both faces must be approached before contact and separated from at
    # least tangency after it. This analytic line-sided gate covers every
    # continuous instant, including between sample frames.
    if any(dot(v,ni)>=-EPS or dot(out,ni)<-EPS for ni in n):
        return reject("continuous-separation")
    frames=[]
    for i in range(round(HORIZON/STEP)+1):
        t=i*STEP
        p=add(start,mul(t,v)) if t<=LEAD else add(center,mul(t-LEAD,out))
        if not (R-1e-9<=p[0]<=24-R+1e-9 and R-1e-9<=p[1]<=6-R+1e-9):
            return reject("world-edge")
        if any(nearest(p,f)[0]<R-3e-7 for f in faces):
            return reject("penetration")
        frames.append({"time":rd(t),"position":[rd(z) for z in p],
                       "velocity":[rd(z) for z in (v if t<LEAD else out)]})
    return {**rec,"status":"admissible-local-model","reason":None,
            "normal_impulses":[rd(q) for q in js],
            "outgoing_velocity":[rd(z) for z in out],"frames":frames,
            "energy_before":rd(.5*dot(v,v)),
            "energy_after":rd(.5*dot(out,out))}

def run():
    stress=stress_run()
    cases=[]
    for i,c in enumerate(stress["cases"]):
        alternatives=[evaluate(c,active) for active in ACTIVE_SETS]
        feasible=[z for z in alternatives if z["status"]=="admissible-local-model"]
        pairs=[z for z in alternatives if z["active_indices"]==[0,1]]
        if len(pairs)!=1 or (pairs[0]["status"]=="admissible-local-model")!=(c["status"]=="accepted-local-candidate"):
            raise ValueError("two-active decision disagrees with frozen Trial 09 source")
        cases.append({"original_index":i,"incoming_angle_degrees":c["incoming_angle_degrees"],
          "surface_B_rotation_degrees":c["surface_B_rotation_degrees"],
          "geometry_kind":c["geometry_kind"],"source_ids":[s["id"] for s in c["surfaces"]],
          "trial09_two_active_status":c["status"],
          "alternatives":alternatives,"admissible_count":len(feasible),
          "classification":("no-local-candidate" if not feasible else
              "multiple-admissible" if len(feasible)>1 else "single-admissible"),
          "physical_outcome_independently_observed":False})
    counts={k:sum(z["classification"]==k for z in cases)
        for k in ("no-local-candidate","single-admissible","multiple-admissible")}
    recovered=sum(x["trial09_two_active_status"].startswith("rejected") and x["admissible_count"]>0 for x in cases)
    if len(cases)!=len(ANGLES)*len(OFFSETS) or sum(counts.values())!=len(cases):
        raise ValueError("trial grid incomplete")
    return {"schema":SCHEMA,
      "source_trial09_schema":stress["schema"],
      "original_source_geometry":stress["original_source_geometry"],
      "angle_grid":list(ANGLES),"rotation_grid":list(OFFSETS),
      "active_sets":[list(s) for s in ACTIVE_SETS],
      "original_trial09_two_active_counts":stress["counts"],
      "cases":cases,"counts":counts,
      "trial09_rejected_cases_with_local_alternatives":recovered,
      "original_trial06_friction":.4,"candidate_friction":IMPACT_FRICTION,
      "comparison_restitution":IMPACT_RESTITUTION,
      "simultaneous_multicontact_physics_uniquely_determined":False,
      "physical_active_contacts_observed":False,
      "sequential_impacts_temporally_witnessed":False,
      "original_source_surfaces_modified":False,
      "rotated_faces_are_original_source":False,
      "original_blueprint_generated":False,"earth_material_equivalence":False}
