"""WORLD Trial 13: bounded coupled simultaneous friction/spin *mode hypotheses*.

No existing source physics is replaced. Original source-owned two finite
surfaces plus explicit controlled Trial09 rotations are treated as contact
candidates at a virtual simultaneous touching state. Enumerate frictionless
and frictional Coulomb stick/slip modes, solve coupled contact Jacobians,
check unilateral normal impulses, normal restitution, tangential slip law,
passivity, continuous line-sided nonpenetration and full 31-frame horizon.
The available assumptions may yield zero or multiple possible outcomes.
No result counts as physical observation of contact order, real friction,
compliance or Earth matter.
"""
from __future__ import annotations
from itertools import product
from math import cos,sin,radians,isfinite
from systems.workspace.world_ab_two_contact_stress import run as stress_run,ANGLES,OFFSETS,LEAD,SPEED
from systems.workspace.world_ab_two_contact_candidate import solve_two_normals
from systems.workspace.world_ab_friction_spin_trial import MU_LEVELS,START_SPINS
from systems.workspace.world_ab_junction_continuous import R,I,HORIZON,STEP,nearest,dot,add,mul

SCHEMA="world-ab-coupled-two-contact-friction-modes/v1"
MODES=("stick","slip-positive","slip-negative")
REST=1.
EPS=1e-8
# Four generalized unknown impulses: normal0, tangent0, normal1, tangent1.
# Velocities are projected by same source normals and linear disc angular
# Jacobians. Exactly four candidate modes per two-contact source are NOT
# guaranteed to identify actual contact physics.
def rd(x):return round(float(x),9)
def cross_row(n,mode):
    return [n[0],n[1],(-R if mode=="tangent" else 0.)]

def linear_solve(mat,rhs):
    """Pivoted square linear solve; no zero-regularization or fake result."""
    n=len(rhs)
    if len(mat)!=n or any(len(row)!=n for row in mat):
        return None
    a=[[float(y) for y in row]+[float(rhs[i])] for i,row in enumerate(mat)]
    for col in range(n):
        piv=max(range(col,n),key=lambda i:abs(a[i][col]))
        if abs(a[piv][col])<1e-10:return None
        a[col],a[piv]=a[piv],a[col]
        inv=1/a[col][col]
        for j in range(col,n+1):a[col][j]*=inv
        for i in range(n):
            if i==col:continue
            scale=a[i][col]
            for j in range(col,n+1):a[i][j]-=scale*a[col][j]
    return [a[i][-1] for i in range(n)]

def impulse_attempt(source,mu,omega,mode):
    ns=[tuple(z) for z in source["normals"]]
    ts=[(-n[1],n[0]) for n in ns]
    inc=(-SPEED*cos(radians(source["incoming_angle_degrees"])),
         -SPEED*sin(radians(source["incoming_angle_degrees"])))
    base=[inc[0],inc[1],omega]
    J=[]
    for n,t in zip(ns,ts):
        J.extend(((n[0],n[1],0.),(t[0],t[1],-R)))
    inv_mass=(1.,1.,1./I)
    K=[[sum(J[i][k]*inv_mass[k]*J[j][k] for k in range(3)) for j in range(4)] for i in range(4)]
    pre=[sum(J[i][k]*base[k] for k in range(3)) for i in range(4)]
    hypothesis={"mode":list(mode),"friction":mu,"incoming_spin":omega,
      "source_ids":[s["id"] for s in source["surfaces"]]}
    def reject(why,imp=None):
        return {**hypothesis,"status":"rejected-"+why,"reason":why,
            "impulses":None if imp is None else [rd(z) for z in imp],
            "outgoing_velocity":None,"outgoing_spin":None,
            "frames":[],"continuous_clearance_verified":False}
    if pre[0]>=-EPS or pre[2]>=-EPS:
        return reject("nonincoming")
    if mu==0 and mode!=("frictionless","frictionless"):
        return reject("not-frictionless-mode")
    # Rows in A lambda=b: two normal restitution constraints, and a
    # stick=zero final tangential velocity or sliding=friction-cone boundary.
    matrix=[K[0][:],K[2][:]]
    rhs=[-2*pre[0],-2*pre[2]]
    for i,label in enumerate(mode):
        if label=="frictionless":
            row=[0.,0.,0.,0.];row[2*i+1]=1.
            b=0.
        elif label=="stick":
            row=K[2*i+1][:]
            b=-pre[2*i+1]
        else:
            sign=(1 if label=="slip-positive" else -1)
            row=[0.,0.,0.,0.]
            row[2*i]=-mu*sign
            row[2*i+1]=-1.  # jt=-mu*sign*jn
            b=0.
        matrix.append(row);rhs.append(b)
    lam=linear_solve(matrix,rhs)
    if lam is None:return reject("dependent-mode-equations")
    if any(not isfinite(x) for x in lam):return reject("nonfinite")
    normal=[lam[0],lam[2]];tang=[lam[1],lam[3]]
    if any(x<=EPS for x in normal):return reject("nonpositive-normal",lam)
    if any(abs(tang[i])>mu*normal[i]+2e-8 for i in (0,1)):
        return reject("friction-cone",lam)
    post=[pre[i]+sum(K[i][j]*lam[j] for j in range(4)) for i in range(4)]
    if abs(post[0]+pre[0])>3e-7 or abs(post[2]+pre[2])>3e-7:
        return reject("normal-restitution",lam)
    for i,label in enumerate(mode):
        slip=post[2*i+1]
        if label=="stick" and abs(slip)>3e-7:
            return reject("stick-residual",lam)
        if label=="slip-positive" and slip<1e-7:
            return reject("sliding-direction",lam)
        if label=="slip-negative" and slip>-1e-7:
            return reject("sliding-direction",lam)
    new=[base[k]+inv_mass[k]*sum(J[j][k]*lam[j] for j in range(4)) for k in range(3)]
    vout=(new[0],new[1]);wout=new[2]
    before=.5*dot(inc,inc)+.5*I*omega**2
    after=.5*dot(vout,vout)+.5*I*wout*wout
    if after>before+5e-8:return reject("energy-increase",lam)
    if any(dot(vout,n)<-1e-8 for n in ns):
        return reject("inward-to-other-contact",lam)
    start=tuple(source["start_center"]);center=tuple(source["contact_center"])
    frames=[]
    for q in range(round(HORIZON/STEP)+1):
        t=q*STEP
        pos=add(start,mul(t,inc)) if t<=LEAD else add(center,mul(t-LEAD,vout))
        if not (R-1e-9<=pos[0]<=24-R+1e-9 and R-1e-9<=pos[1]<=6-R+1e-9):
            return reject("world-edge",lam)
        if any(nearest(pos,s)[0]<R-3e-7 for s in source["surfaces"]):
            return reject("surface-penetration",lam)
        frames.append({"time":rd(t),"position":[rd(z) for z in pos],
                       "velocity":[rd(z) for z in (inc if t<LEAD else vout)],
                       "spin":rd(omega if t<LEAD else wout),
                       "orientation":rd(omega*t if t<=LEAD else omega*LEAD+wout*(t-LEAD))})
    return {**hypothesis,"status":"admissible-coupled-mode","reason":None,
        "impulses":[rd(z) for z in lam],"outgoing_velocity":[rd(z) for z in vout],
        "outgoing_spin":rd(wout),
        "incoming_contact_speeds":[rd(z) for z in pre],
        "outgoing_contact_speeds":[rd(z) for z in post],
        "energy_before":rd(before),"energy_after":rd(after),
        "frames":frames,"continuous_clearance_verified":True}

def run():
    stress=stress_run()
    if len(stress["cases"])!=35:raise ValueError("source grid changed")
    scenarios=[]
    for i,s in enumerate(stress["cases"]):
        groups=[]
        for omega in START_SPINS:
            for mu in MU_LEVELS:
                options=[impulse_attempt(s,mu,omega,mode) for mode in
                     ((("frictionless","frictionless"),) if mu==0 else product(MODES,repeat=2))]
                admissible=[x for x in options if x["status"]=="admissible-coupled-mode"]
                if mu==0 and omega==0:
                    expected=s["status"]=="accepted-local-candidate"
                    if bool(admissible)!=expected:
                        raise ValueError("Trial09 frictionless simultaneous source drifted")
                groups.append({"starting_spin":omega,"friction":mu,
                  "options":options,"admissible_count":len(admissible),
                  "classification":("none" if not admissible else "multiple" if len(admissible)>1 else "one"),
                  "physical_outcome_selected":False})
        scenarios.append({"original_index":i,"incoming_angle_degrees":s["incoming_angle_degrees"],
             "surface_B_rotation_degrees":s["surface_B_rotation_degrees"],
             "geometry_kind":s["geometry_kind"],"source_ids":[f["id"] for f in s["surfaces"]],
             "trial09_two_active_status":s["status"],"groups":groups,
             "material_behavior_observed":False})
    aggregate=[]
    for j,(omega,mu) in enumerate((w,m) for w in START_SPINS for m in MU_LEVELS):
        vals=[c["groups"][j] for c in scenarios]
        aggregate.append({"starting_spin":omega,"friction":mu,
             "admissible_modes":sum(c["admissible_count"] for c in vals),
             "cases_with_one_mode":sum(c["classification"]=="one" for c in vals),
             "cases_with_multiple_modes":sum(c["classification"]=="multiple" for c in vals),
             "cases_with_no_mode":sum(c["classification"]=="none" for c in vals)})
    return {"schema":SCHEMA,"original_source_geometry":stress["original_source_geometry"],
       "source_trial09_schema":stress["schema"],
       "original_trial09_two_active_counts":stress["counts"],
       "angle_grid":list(ANGLES),"rotation_grid":list(OFFSETS),
       "friction_grid":list(MU_LEVELS),"starting_spin_grid":list(START_SPINS),
       "hypotheses":list(MODES),"disc_radius":R,"disc_inertia":I,
       "normal_restitution":REST,"scenarios":scenarios,"aggregate":aggregate,
       "original_trial06_friction":.4,
       "source_original_trial06_simultaneous_stop_preserved":True,
       "general_simultaneous_friction_manifold_solved":False,
       "actual_joint_contact_impulses_measured":False,
       "physical_material_law_verified":False,
       "real_blueprint_generated":False}
