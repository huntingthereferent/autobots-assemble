"""WORLD Trial 12: bounded single-active friction/spin comparison, NOT a manifold.

The two finite original Trial04B-derived source faces and all Trial06–11
conclusions are retained. A clearly identified controlled ray enters the
same simultaneous two-face tangent configuration. Enumerate only a local
ONE-active-contact constitutive model, for A or B independently:
normal restitution e=1, Coulomb-cap tangential impulse, disc rotation, and
finite 24×6 motion. Reject the outgoing path if the OTHER measured face
would be penetrated. Never use local success to select the real contact.
"""
from __future__ import annotations
from math import cos,sin,radians,isfinite
from systems.workspace.world_ab_two_contact_stress import run as stress_run,ANGLES,OFFSETS,LEAD,SPEED
from systems.workspace.world_ab_active_set_trial import run as active_run
from systems.workspace.world_ab_junction_continuous import (
    R,I,STEP,HORIZON,nearest,physical_impulse,dot,add,mul)

SCHEMA="world-ab-single-active-friction-spin-controls/v1"
MU_LEVELS=(0.,.2,.4)
START_SPINS=(0.,2.)
RESTITUTION=1.
EPS=1e-8

def rd(x):return round(float(x),9)

def simulate(source,face_index,mu,omega):
    angle=source["incoming_angle_degrees"]
    vin=(-SPEED*cos(radians(angle)),-SPEED*sin(radians(angle)))
    ns=[tuple(n) for n in source["normals"]]
    start=tuple(source["start_center"]);center=tuple(source["contact_center"])
    face=source["surfaces"][face_index]
    n=ns[face_index];t=(-n[1],n[0])
    normal_speed=dot(vin,n)
    slip=dot(vin,t)-R*omega
    rec={"face_index":face_index,"face_id":face["id"],
         "friction_coefficient":mu,"incoming_spin":omega,
         "incoming_velocity":[rd(z) for z in vin],
         "normal":[rd(z) for z in n],
         "incoming_normal_speed":rd(normal_speed),
         "incoming_tangential_slip":rd(slip)}
    if normal_speed>=-EPS:raise ValueError("source case did not approach active face")
    outgoing,outspin,impulse=physical_impulse(vin,omega,n,friction=mu)
    jn=impulse["normal_impulse"];jt=impulse["tangential_impulse"]
    desired=-slip/(1+R*R/I)
    regime="stick-candidate" if abs(desired)<=mu*jn+1e-8 else "sliding-cap"
    slip_after=dot(outgoing,t)-R*outspin
    energy_before=.5*dot(vin,vin)+.5*I*omega*omega
    energy_after=.5*dot(outgoing,outgoing)+.5*I*outspin*outspin
    if (any(not isfinite(q) for q in (*outgoing,outspin,jn,jt))
        or jn<=0 or abs(jt)>mu*jn+2e-8
        or abs(dot(outgoing,n)+dot(vin,n))>3e-8
        or energy_after>energy_before+2e-8):
        raise ValueError("original single-face friction law violated")
    attempted={**rec,"normal_impulse":jn,"tangential_impulse":jt,
       "slip_regime":regime,"outgoing_velocity":[rd(z) for z in outgoing],
       "outgoing_spin":rd(outspin),"outgoing_tangential_slip":rd(slip_after),
       "energy_before":rd(energy_before),"energy_after":rd(energy_after),
       "friction_cone_satisfied":True}
    def reject(reason):
        return {**attempted,"status":"rejected-"+reason,
                "reason":reason,"frames":[],"finite_horizon_verified":False}
    if any(dot(vin,n_i)>=-EPS or dot(outgoing,n_i)<-EPS for n_i in ns):
        return reject("other-face-inward")
    frames=[]
    for i in range(round(HORIZON/STEP)+1):
        clock=i*STEP
        pos=add(start,mul(clock,vin)) if clock<=LEAD else add(center,mul(clock-LEAD,outgoing))
        v=vin if clock<LEAD else outgoing
        w=omega if clock<LEAD else outspin
        orientation=(omega*clock if clock<=LEAD else omega*LEAD+outspin*(clock-LEAD))
        if not (R-1e-9<=pos[0]<=24.-R+1e-9 and R-1e-9<=pos[1]<=6.-R+1e-9):
            return reject("world-edge")
        if any(nearest(pos,seg)[0]<R-3e-7 for seg in source["surfaces"]):
            return reject("penetration")
        frames.append({"time":rd(clock),"position":[rd(z) for z in pos],
            "velocity":[rd(z) for z in v],"spin":rd(w),
            "orientation":rd(orientation)})
    return {**attempted,"status":"admissible-single-active",
       "reason":None,"frames":frames,"finite_horizon_verified":True}

def run():
    src=stress_run()
    active=active_run()
    if len(src["cases"])!=35 or len(active["cases"])!=35:
        raise ValueError("original controlled grid missing")
    cases=[]
    for index,(s,old) in enumerate(zip(src["cases"],active["cases"])):
        if s["incoming_angle_degrees"]!=old["incoming_angle_degrees"] or s["surface_B_rotation_degrees"]!=old["surface_B_rotation_degrees"]:
            raise ValueError("original source case pairing drift")
        options=[simulate(s,face_index,mu,omega)
            for omega in START_SPINS for mu in MU_LEVELS for face_index in (0,1)]
        # Frictionless, zero-initial-spin limit must reproduce exactly the
        # original Trial10 single-active feasibility, not retroactively
        # convert its two-active refusals into successes.
        for index_face in (0,1):
            current=next(x for x in options if x["incoming_spin"]==0 and x["friction_coefficient"]==0 and x["face_index"]==index_face)
            prior=old["alternatives"][index_face]
            if (current["status"]=="admissible-single-active") != (prior["status"]=="admissible-local-model"):
                raise ValueError("original Trial10 frictionless active-set control changed")
        cases.append({"original_index":index,"incoming_angle_degrees":s["incoming_angle_degrees"],
          "surface_B_rotation_degrees":s["surface_B_rotation_degrees"],
          "geometry_kind":s["geometry_kind"],"source_ids":[f["id"] for f in s["surfaces"]],
          "original_trial10_classification":old["classification"],
          "original_trial09_two_active_status":s["status"],
          "options":options,"actual_active_contact_observed":False,
          "real_collision_outcome_selected":False})
    by_parameter=[]
    for omega in START_SPINS:
        for mu in MU_LEVELS:
            selections=[[q for q in case["options"] if q["incoming_spin"]==omega and q["friction_coefficient"]==mu and q["status"]=="admissible-single-active"] for case in cases]
            by_parameter.append({"starting_spin":omega,"friction_coefficient":mu,
               "accepted_single_face_candidates":sum(len(group) for group in selections),
               "cases_with_any_admissible_single_face":sum(bool(group) for group in selections),
               "cases_with_two_admissible_single_faces":sum(len(group)==2 for group in selections),
               "cases_with_no_admissible_single_face":sum(not group for group in selections)})
    return {"schema":SCHEMA,"source_trial09_schema":src["schema"],
       "source_trial10_schema":active["schema"],
       "original_source_geometry":src["original_source_geometry"],
       "original_trial10_counts":active["counts"],
       "original_trial09_two_active_counts":src["counts"],
       "incoming_angle_grid":list(ANGLES),"source_rotation_grid":list(OFFSETS),
       "friction_grid":list(MU_LEVELS),"starting_spin_grid":list(START_SPINS),
       "restitution":RESTITUTION,"radius":R,"inertia":I,
       "cases":cases,"by_parameter":by_parameter,
       "original_trial06_friction":.4,
       "original_trial06_two_contact_solver_unchanged":True,
       "frictional_simultaneous_two_contact_manifold_solved":False,
       "actual_active_contact_observed":False,
       "sequential_real_contacts_measured":False,
       "real_material_equivalence":False,"physical_blueprint_generated":False}
