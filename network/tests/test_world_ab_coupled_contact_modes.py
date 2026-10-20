"""Independent coupled-Jacobian impulse oracle, negative evidence and lineage."""
from __future__ import annotations
import unittest
from copy import deepcopy
from math import cos,sin,radians,hypot,isfinite
from systems.workspace.world_ab_coupled_contact_modes import run,SCHEMA,MODES
from systems.workspace.world_ab_two_contact_stress import run as source_run,ANGLES,OFFSETS,LEAD,SPEED
from systems.workspace.world_ab_friction_spin_trial import MU_LEVELS,START_SPINS
from systems.workspace.world_ab_junction_continuous import R,I,HORIZON,STEP
from network.tests.test_world_ab_junction_continuous import source_equivalent

def d(a,b):
    return sum(x*y for x,y in zip(a,b))
def distance(p,seg):
    a,b=seg["endpoints"];ab=(b[0]-a[0],b[1]-a[1])
    u=max(0.,min(1.,d((p[0]-a[0],p[1]-a[1]),ab)/d(ab,ab)))
    return hypot(p[0]-a[0]-u*ab[0],p[1]-a[1]-u*ab[1])
def independent_solve(A,b):
    # Left-to-right column elimination, a separately implemented replay
    # rather than calling generator's pivoted linear_solve.
    size=len(b)
    mat=[list(A[i])+[b[i]] for i in range(size)]
    for j in range(size):
        k=max(range(j,size),key=lambda i:abs(mat[i][j]))
        if abs(mat[k][j])<1e-10:return None
        mat[j],mat[k]=mat[k],mat[j]
        pivot=mat[j][j]
        for i in range(j+1,size):
            q=mat[i][j]/pivot
            for c in range(j+1,size+1):
                mat[i][c]-=q*mat[j][c]
            mat[i][j]=0.
    x=[0.]*size
    for i in reversed(range(size)):
        x[i]=(mat[i][-1]-sum(mat[i][j]*x[j] for j in range(i+1,size)))/mat[i][i]
    return x

def classify(src,mu,omega,mode):
    inc=(-SPEED*cos(radians(src["incoming_angle_degrees"])),-SPEED*sin(radians(src["incoming_angle_degrees"])))
    n=[]
    center=src["contact_center"]
    for face,prior in zip(src["surfaces"],src["normals"]):
        a,b=face["endpoints"];v=(b[0]-a[0],b[1]-a[1]);L=hypot(*v)
        normal=(-v[1]/L,v[0]/L)
        if d(normal,(center[0]-a[0],center[1]-a[1]))<0:normal=(-normal[0],-normal[1])
        if max(abs(q-p) for q,p in zip(normal,prior))>2e-7:
            raise ValueError("measured normal not source face normal")
        if abs(distance(center,face)-R)>3e-7:raise ValueError("source contact center drift")
        # Independently verify the measured finite-face normal, but use the
        # exact recorded 9dp input for the impulse algebra. Replacing it with
        # higher precision shifts ill-conditioned impulse magnitudes.
        n.append(tuple(prior))
    tangent=[(-q[1],q[0]) for q in n]
    vectors=[]
    for ni,ti in zip(n,tangent):
        vectors.extend([(ni[0],ni[1],0.),(ti[0],ti[1],-R)])
    mass=(1.,1.,1./I)
    gram=[[sum(vectors[i][k]*vectors[j][k]*mass[k] for k in range(3)) for j in range(4)] for i in range(4)]
    base=(inc[0],inc[1],omega)
    entering=[d(v,base) for v in vectors]
    if entering[0]>=-1e-8 or entering[2]>=-1e-8:return "rejected-nonincoming",None
    if mu==0 and mode!=("frictionless","frictionless"):return "rejected-not-frictionless-mode",None
    A=[list(gram[0]),list(gram[2])]
    rhs=[-2*entering[0],-2*entering[2]]
    for j,m in enumerate(mode):
        if m=="frictionless":
            row=[0.]*4;row[2*j+1]=1;right=0.
        elif m=="stick":
            row=list(gram[2*j+1]);right=-entering[2*j+1]
        else:
            sign=1 if m=="slip-positive" else -1
            row=[0.]*4;row[2*j]=-mu*sign;row[2*j+1]=-1.;right=0.
        A.append(row);rhs.append(right)
    impulses=independent_solve(A,rhs)
    if impulses is None:return "rejected-dependent-mode-equations",None
    if not all(isfinite(z) for z in impulses):return "rejected-nonfinite",None
    if impulses[0]<=1e-8 or impulses[2]<=1e-8:return "rejected-nonpositive-normal",impulses
    if any(abs(impulses[2*j+1])>mu*impulses[2*j]+2e-8 for j in range(2)):
        return "rejected-friction-cone",impulses
    projected=[entering[i]+sum(gram[i][k]*impulses[k] for k in range(4)) for i in range(4)]
    if abs(projected[0]+entering[0])>3e-7 or abs(projected[2]+entering[2])>3e-7:
        return "rejected-normal-restitution",impulses
    for i,m in enumerate(mode):
        slip=projected[2*i+1]
        if m=="stick" and abs(slip)>3e-7:return "rejected-stick-residual",impulses
        if m=="slip-positive" and slip<1e-7:return "rejected-sliding-direction",impulses
        if m=="slip-negative" and slip>-1e-7:return "rejected-sliding-direction",impulses
    final=[base[k]+mass[k]*sum(vectors[j][k]*impulses[j] for j in range(4)) for k in range(3)]
    before=.5*d(inc,inc)+.5*I*omega*omega
    after=.5*d(final[:2],final[:2])+.5*I*final[2]**2
    if after>before+5e-8:return "rejected-energy-increase",impulses
    if any(d(final[:2],q)<-1e-8 for q in n):
        return "rejected-inward-to-other-contact",impulses
    start=src["start_center"]
    for i in range(round(HORIZON/STEP)+1):
        clock=i*STEP
        pos=[start[k]+inc[k]*clock for k in range(2)] if clock<=LEAD else [
            center[k]+final[k]*(clock-LEAD) for k in range(2)]
        if not R-1e-9<=pos[0]<=24-R+1e-9 or not R-1e-9<=pos[1]<=6-R+1e-9:
            return "rejected-world-edge",impulses
        if any(distance(pos,face)<R-3e-7 for face in src["surfaces"]):
            return "rejected-surface-penetration",impulses
    return "admissible-coupled-mode",(impulses,final,entering,projected,before,after)

def check(out):
    src=source_run()
    if out["schema"]!=SCHEMA or out["source_trial09_schema"]!=src["schema"] or not source_equivalent(out["original_source_geometry"],src["original_source_geometry"]):
        raise ValueError("original source geometry or schema changed")
    if out["original_trial09_two_active_counts"]!=src["counts"] or out["angle_grid"]!=list(ANGLES) or out["rotation_grid"]!=list(OFFSETS):
        raise ValueError("original contact classifications or grid mutated")
    if out["friction_grid"]!=list(MU_LEVELS) or out["starting_spin_grid"]!=list(START_SPINS) or out["hypotheses"]!=list(MODES):
        raise ValueError("experiment grid substituted")
    if out["disc_radius"]!=R or out["disc_inertia"]!=I or out["normal_restitution"]!=1. or out["original_trial06_friction"]!=.4:
        raise ValueError("physical assumptions distorted")
    if out["source_original_trial06_simultaneous_stop_preserved"] is not True:
        raise ValueError("source fail-close boundary lost")
    for flag in ("general_simultaneous_friction_manifold_solved","actual_joint_contact_impulses_measured",
                 "physical_material_law_verified","real_blueprint_generated"):
        if out[flag] is not False:raise ValueError("unobserved scientific claim promoted")
    if len(out["scenarios"])!=35:raise ValueError("missing source scenarios")
    summary=[]
    for i,(c,s) in enumerate(zip(out["scenarios"],src["cases"])):
        if c["original_index"]!=i or c["incoming_angle_degrees"]!=s["incoming_angle_degrees"] or c["surface_B_rotation_degrees"]!=s["surface_B_rotation_degrees"]:
            raise ValueError("source motion/control identity changed")
        if c["geometry_kind"]!=s["geometry_kind"] or c["source_ids"]!=[q["id"] for q in s["surfaces"]] or c["trial09_two_active_status"]!=s["status"]:
            raise ValueError("original finite face provenance changed")
        if c["material_behavior_observed"] is not False or len(c["groups"])!=6:
            raise ValueError("fabricated material measurement or omitted parameter")
        for row,(w,mu) in zip(c["groups"],((w,m) for w in START_SPINS for m in MU_LEVELS)):
            if row["starting_spin"]!=w or row["friction"]!=mu or row["physical_outcome_selected"] is not False:
                raise ValueError("hypothesis displayed as observed contact")
            expect_modes=[("frictionless","frictionless")] if mu==0 else list(__import__("itertools").product(MODES,repeat=2))
            if len(row["options"])!=len(expect_modes):raise ValueError("friction candidate missing")
            admitted=0
            for candidate,mode in zip(row["options"],expect_modes):
                if candidate["mode"]!=list(mode) or candidate["friction"]!=mu or candidate["incoming_spin"]!=w or candidate["source_ids"]!=c["source_ids"]:
                    raise ValueError("contact mode or source role switched")
                status,computed=classify(s,mu,w,mode)
                if candidate["status"]!=status:
                    raise ValueError(f"case {i} spin={w} mu={mu} mode={mode}: actual {candidate['status']}, expected {status}")
                if (candidate["reason"] is None)!=(status=="admissible-coupled-mode"):
                    raise ValueError("rejected candidate marked completed")
                if status!="admissible-coupled-mode":
                    if candidate["outgoing_velocity"] is not None or candidate["outgoing_spin"] is not None or candidate["frames"] or candidate["continuous_clearance_verified"] is not False:
                        raise ValueError("rejected mode has fake completed trajectory")
                    if computed is None:
                        if candidate["impulses"] is not None:raise ValueError("invented singular impulses")
                    elif len(computed)==4:
                        if candidate["impulses"] is None or any(abs(x-y)>3e-7 for x,y in zip(candidate["impulses"],computed)):
                            raise ValueError(f"case {i}, w={w}, mu={mu}, mode={mode}: rejected impulses mismatch actual={candidate['impulses']} independent={computed}")
                    continue
                admitted+=1
                impulse,fin,pre,post,energy_pre,energy_post=computed
                if candidate["continuous_clearance_verified"] is not True or len(candidate["frames"])!=round(HORIZON/STEP)+1:
                    raise ValueError("accepted mode missing full continuous source trajectory")
                for name,expected in (("impulses",impulse),("outgoing_velocity",fin[:2]),("incoming_contact_speeds",pre),("outgoing_contact_speeds",post)):
                    if any(abs(x-y)>3e-7 for x,y in zip(candidate[name],expected)):
                        raise ValueError("candidate's source-derived contact impulse or velocity forged")
                if abs(candidate["outgoing_spin"]-fin[2])>3e-7 or abs(candidate["energy_before"]-energy_pre)>3e-7 or abs(candidate["energy_after"]-energy_post)>3e-7:
                    raise ValueError("angular velocity or energy fabricated")
                incoming=(-SPEED*cos(radians(s["incoming_angle_degrees"])),-SPEED*sin(radians(s["incoming_angle_degrees"])))
                for frameidx,f in enumerate(candidate["frames"]):
                    clock=frameidx*STEP
                    pos=[s["start_center"][k]+clock*incoming[k] for k in range(2)] if clock<=LEAD else [
                        s["contact_center"][k]+(clock-LEAD)*fin[k] for k in range(2)]
                    vel=incoming if clock<LEAD else fin[:2]
                    spin=w if clock<LEAD else fin[2]
                    angle=w*clock if clock<=LEAD else w*LEAD+fin[2]*(clock-LEAD)
                    if (abs(f["time"]-clock)>3e-8 or
                        any(abs(f["position"][k]-pos[k])>3e-7 for k in range(2)) or
                        any(abs(f["velocity"][k]-vel[k])>3e-7 for k in range(2)) or
                        abs(f["spin"]-spin)>3e-7 or abs(f["orientation"]-angle)>3e-7):
                        raise ValueError("false coupled full-horizon motion frame")
            if row["admissible_count"]!=admitted or row["classification"]!=("none" if admitted==0 else "multiple" if admitted>1 else "one"):
                raise ValueError("coupled contact ambiguity erased or invented")
        if (c["groups"][0]["admissible_count"]>0) != (s["status"]=="accepted-local-candidate"):
            raise ValueError("frictionless Trial09 outcome changed")
    for j,(w,mu) in enumerate((w,m) for w in START_SPINS for m in MU_LEVELS):
        counts=[c["groups"][j] for c in out["scenarios"]]
        expected={"starting_spin":w,"friction":mu,
           "admissible_modes":sum(y["admissible_count"] for y in counts),
           "cases_with_one_mode":sum(y["classification"]=="one" for y in counts),
           "cases_with_multiple_modes":sum(y["classification"]=="multiple" for y in counts),
           "cases_with_no_mode":sum(y["classification"]=="none" for y in counts)}
        if out["aggregate"][j]!=expected:raise ValueError("aggregate source outcome falsified")
    return True

class Trial13Tests(unittest.TestCase):
    def test_all_1330_mode_attempts_and_full_finite_source(self):self.assertTrue(check(run()))
    def test_original_frictionless_restitution_retained(self):
        original=source_run();out=run()
        for case,src in zip(out["scenarios"],original["cases"]):
            self.assertEqual(case["groups"][0]["admissible_count"]>0,src["status"]=="accepted-local-candidate")
    def test_unobserved_contact_results_not_selected(self):
        out=run()
        self.assertFalse(out["actual_joint_contact_impulses_measured"])
        self.assertTrue(all(group["physical_outcome_selected"] is False for x in out["scenarios"] for group in x["groups"]))
    def test_invalid_physical_postulates_fail_closed(self):
        out=run()
        self.assertGreater(sum(g["classification"]=="none" for c in out["scenarios"] for g in c["groups"]),0)
        self.assertTrue(any(z["status"].startswith("rejected-") for c in out["scenarios"] for g in c["groups"] for z in g["options"]))
    def test_tampered_source_or_contact_claims_rejected(self):
        out=run()
        first=next((i,j,k) for i,c in enumerate(out["scenarios"]) for j,g in enumerate(c["groups"])
                   for k,q in enumerate(g["options"]) if q["status"]=="admissible-coupled-mode")
        i,j,k=first
        mods=[
           lambda x:x["scenarios"][i]["groups"][j]["options"][k]["impulses"].__setitem__(0,999.),
           lambda x:x["scenarios"][i]["groups"][j]["options"][k]["frames"][22]["position"].__setitem__(0,0.),
           lambda x:x["scenarios"][i]["groups"][j].update(admissible_count=5),
           lambda x:x["scenarios"][i]["groups"][j].update(physical_outcome_selected=True),
           lambda x:x.update(actual_joint_contact_impulses_measured=True),
           lambda x:x["aggregate"][0].update(cases_with_one_mode=35),
           lambda x:x["original_source_geometry"]["surfaces"][0]["endpoints"][0].__setitem__(0,0.),
        ]
        for m,mod in enumerate(mods):
            mutant=deepcopy(out);mod(mutant)
            with self.subTest(m=m),self.assertRaises(ValueError):check(mutant)

if __name__=="__main__":unittest.main()
