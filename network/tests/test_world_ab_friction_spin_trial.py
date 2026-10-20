"""Independent material-law math and finite geometry falsification for Trial 12."""
import unittest
from math import cos,sin,radians,hypot
from copy import deepcopy
from systems.workspace.world_ab_friction_spin_trial import run,SCHEMA,MU_LEVELS,START_SPINS
from systems.workspace.world_ab_two_contact_stress import run as source_run,ANGLES,OFFSETS,LEAD,SPEED
from systems.workspace.world_ab_active_set_trial import run as active_run
from systems.workspace.world_ab_junction_continuous import R,I,STEP,HORIZON
from network.tests.test_world_ab_junction_continuous import source_equivalent

def geometry_distance(center,segment):
    a,b=segment["endpoints"];ab=(b[0]-a[0],b[1]-a[1])
    t=max(0.,min(1.,((center[0]-a[0])*ab[0]+(center[1]-a[1])*ab[1])/(ab[0]*ab[0]+ab[1]*ab[1])))
    return hypot(center[0]-a[0]-t*ab[0],center[1]-a[1]-t*ab[1])

def oracle(out):
    original=source_run()
    source_active=active_run()
    if out["schema"]!=SCHEMA or out["source_trial09_schema"]!=original["schema"] or out["source_trial10_schema"]!=source_active["schema"]:
        raise ValueError("source lineage substituted")
    if not source_equivalent(out["original_source_geometry"],original["original_source_geometry"]):
        raise ValueError("finite source changed")
    if out["original_trial10_counts"]!=source_active["counts"] or out["original_trial09_two_active_counts"]!=original["counts"]:
        raise ValueError("previous test result overwritten")
    if out["incoming_angle_grid"]!=list(ANGLES) or out["source_rotation_grid"]!=list(OFFSETS) or out["friction_grid"]!=list(MU_LEVELS) or out["starting_spin_grid"]!=list(START_SPINS):
        raise ValueError("test grid changed")
    if out["radius"]!=R or out["inertia"]!=I or out["restitution"]!=1. or out["original_trial06_friction"]!=.4:
        raise ValueError("constitutive parameters changed")
    for field,flag in (("original_trial06_two_contact_solver_unchanged",True),
        ("frictional_simultaneous_two_contact_manifold_solved",False),
        ("actual_active_contact_observed",False),
        ("sequential_real_contacts_measured",False),
        ("real_material_equivalence",False),("physical_blueprint_generated",False)):
        if out[field] is not flag:raise ValueError("promoted unobserved claim")
    if len(out["cases"])!=35:raise ValueError("source case omitted")
    stats={}
    for index,(case,src,old) in enumerate(zip(out["cases"],original["cases"],source_active["cases"])):
        if case["original_index"]!=index or case["incoming_angle_degrees"]!=src["incoming_angle_degrees"] or case["surface_B_rotation_degrees"]!=src["surface_B_rotation_degrees"] or case["geometry_kind"]!=src["geometry_kind"]:
            raise ValueError("case provenance altered")
        if case["source_ids"]!=[s["id"] for s in src["surfaces"]] or case["original_trial10_classification"]!=old["classification"] or case["original_trial09_two_active_status"]!=src["status"]:
            raise ValueError("previous tested classifications overwritten")
        if case["actual_active_contact_observed"] is not False or case["real_collision_outcome_selected"] is not False:
            raise ValueError("made up physical measurement")
        if len(case["options"])!=len(MU_LEVELS)*len(START_SPINS)*2:raise ValueError("missing friction/spin candidate")
        rad=radians(src["incoming_angle_degrees"]);vin=(-SPEED*cos(rad),-SPEED*sin(rad))
        normals=[];center=src["contact_center"];start=src["start_center"]
        for seg in src["surfaces"]:
            a,b=seg["endpoints"];t=(b[0]-a[0],b[1]-a[1]);L=hypot(*t);n=(-t[1]/L,t[0]/L)
            if (center[0]-a[0])*n[0]+(center[1]-a[1])*n[1]<0:n=(-n[0],-n[1])
            if abs(geometry_distance(center,seg)-R)>3e-7:raise ValueError("source face not tangent")
            normals.append(n)
        for candidate,(omega,mu,index_face) in zip(case["options"],((w,m,f) for w in START_SPINS for m in MU_LEVELS for f in (0,1))):
            if candidate["face_index"]!=index_face or candidate["face_id"]!=src["surfaces"][index_face]["id"] or candidate["friction_coefficient"]!=mu or candidate["incoming_spin"]!=omega:
                raise ValueError("candidate provenance switched")
            n=normals[index_face];t=(-n[1],n[0])
            vn=sum(vin[k]*n[k] for k in (0,1));slip=sum(vin[k]*t[k] for k in (0,1))-R*omega
            jn=-2*vn;jt=max(-mu*jn,min(mu*jn,-slip/(1+R*R/I)))
            vout=tuple(vin[k]+jn*n[k]+jt*t[k] for k in (0,1))
            wout=omega-R*jt/I
            before=.5*sum(v*v for v in vin)+.5*I*omega**2
            after=.5*sum(v*v for v in vout)+.5*I*wout*wout
            regime="stick-candidate" if abs(-slip/(1+R*R/I))<=mu*jn+1e-8 else "sliding-cap"
            if (candidate["slip_regime"]!=regime or
                abs(candidate["normal_impulse"]-jn)>3e-7 or abs(candidate["tangential_impulse"]-jt)>3e-7 or
                abs(candidate["incoming_normal_speed"]-vn)>3e-7 or abs(candidate["incoming_tangential_slip"]-slip)>3e-7 or
                abs(candidate["outgoing_tangential_slip"]-(sum(vout[k]*t[k] for k in (0,1))-R*wout))>3e-7 or
                any(abs(candidate["normal"][k]-n[k])>3e-7 for k in (0,1)) or
                any(abs(candidate["incoming_velocity"][k]-vin[k])>3e-7 for k in (0,1)) or
                any(abs(candidate["outgoing_velocity"][k]-vout[k])>3e-7 for k in (0,1)) or
                abs(candidate["outgoing_spin"]-wout)>3e-7 or
                abs(candidate["energy_before"]-before)>3e-7 or abs(candidate["energy_after"]-after)>3e-7):
                raise ValueError("friction/spin momentum or energy receipt forged")
            if after>before+3e-8 or abs(jt)>mu*jn+3e-8 or candidate["friction_cone_satisfied"] is not True:
                raise ValueError("energy generation or violated impulse cap")
            expected_reason=None
            if any(sum(vout[k]*ns[k] for k in (0,1)) < -1e-8 for ns in normals):
                expected_reason="other-face-inward"
            if expected_reason is None:
                for i in range(round(HORIZON/STEP)+1):
                    clock=i*STEP
                    pos=(start[0]+vin[0]*clock,start[1]+vin[1]*clock) if clock<=LEAD else (
                        center[0]+vout[0]*(clock-LEAD),center[1]+vout[1]*(clock-LEAD))
                    if not R-1e-9<=pos[0]<=24-R+1e-9 or not R-1e-9<=pos[1]<=6-R+1e-9:
                        expected_reason="world-edge";break
                    if any(geometry_distance(pos,s)<R-3e-7 for s in src["surfaces"]):
                        expected_reason="penetration";break
            status="rejected-"+expected_reason if expected_reason else "admissible-single-active"
            if candidate["status"]!=status or candidate["reason"]!=expected_reason:
                raise ValueError("candidate acceptance inconsistent with finite source")
            if (candidate["finite_horizon_verified"] is True)!= (expected_reason is None):
                raise ValueError("unwitnessed complete path marked verified")
            if expected_reason:
                if candidate["frames"]:raise ValueError("invented completed trajectory on rejected candidate")
            else:
                frames=candidate["frames"]
                if len(frames)!=round(HORIZON/STEP)+1:raise ValueError("missing continuous frames")
                for i,frame in enumerate(frames):
                    clock=i*STEP
                    pos=(start[0]+vin[0]*clock,start[1]+vin[1]*clock) if clock<=LEAD else (
                        center[0]+vout[0]*(clock-LEAD),center[1]+vout[1]*(clock-LEAD))
                    fvel=vin if clock<LEAD else vout
                    fw=omega if clock<LEAD else wout
                    theta=omega*clock if clock<=LEAD else omega*LEAD+wout*(clock-LEAD)
                    if (abs(frame["time"]-clock)>3e-8 or
                        any(abs(frame["position"][k]-pos[k])>3e-7 for k in (0,1)) or
                        any(abs(frame["velocity"][k]-fvel[k])>3e-7 for k in (0,1)) or
                        abs(frame["spin"]-fw)>3e-7 or abs(frame["orientation"]-theta)>3e-7):
                        raise ValueError("disconnected/false finite spin-motion frame")
            if omega==0 and mu==0:
                prior=old["alternatives"][index_face]
                if (candidate["status"]=="admissible-single-active")!=(prior["status"]=="admissible-local-model"):
                    raise ValueError("Trial10 single-active comparison changed")
            stats.setdefault((omega,mu),[]).append((index,index_face,status=="admissible-single-active"))
    if len(out["by_parameter"])!=len(START_SPINS)*len(MU_LEVELS):
        raise ValueError("missing complete parameter count")
    for row,(omega,mu) in zip(out["by_parameter"],((w,m) for w in START_SPINS for m in MU_LEVELS)):
        vals=stats[(omega,mu)]
        possible={i:sum(ok for x,_,ok in vals if x==i) for i in range(35)}
        expected={"starting_spin":omega,"friction_coefficient":mu,
          "accepted_single_face_candidates":sum(possible.values()),
          "cases_with_any_admissible_single_face":sum(n>0 for n in possible.values()),
          "cases_with_two_admissible_single_faces":sum(n==2 for n in possible.values()),
          "cases_with_no_admissible_single_face":sum(n==0 for n in possible.values())}
        if row!=expected:raise ValueError("comparison count forged")
    return True

class Trial12Tests(unittest.TestCase):
    def test_full_420_candidate_source_and_oracle(self):self.assertTrue(oracle(run()))
    def test_original_frictionless_limit_retained(self):
        o=run()
        src=active_run()
        for c,prior in zip(o["cases"],src["cases"]):
            for j in (0,1):
                x=next(x for x in c["options"] if x["friction_coefficient"]==0 and x["incoming_spin"]==0 and x["face_index"]==j)
                self.assertEqual(x["status"]=="admissible-single-active",prior["alternatives"][j]["status"]=="admissible-local-model")
    def test_finite_energy_and_spin_change_witnessed_in_model_only(self):
        o=run()
        accepted=[q for c in o["cases"] for q in c["options"] if q["status"]=="admissible-single-active"]
        self.assertGreater(len(accepted),0)
        self.assertTrue(any(abs(q["tangential_impulse"])>1e-7 and abs(q["outgoing_spin"]-q["incoming_spin"])>1e-7 for q in accepted))
        self.assertTrue(any(q["energy_after"]<q["energy_before"]-1e-7 for q in accepted))
    def test_rejected_cases_are_not_completed(self):
        o=run()
        self.assertTrue(any(q["status"].startswith("rejected") for c in o["cases"] for q in c["options"]))
        self.assertTrue(all(not q["frames"] for c in o["cases"] for q in c["options"] if q["status"].startswith("rejected")))
    def test_preserve_original_contact_evidence_boundary(self):
        o=run()
        self.assertFalse(o["frictional_simultaneous_two_contact_manifold_solved"])
        self.assertFalse(o["actual_active_contact_observed"])
        self.assertFalse(o["sequential_real_contacts_measured"])
    def test_corrupted_spin_motion_source_and_claims_rejected(self):
        o=run()
        case_i=next(i for i,c in enumerate(o["cases"]) if any(q["status"]=="admissible-single-active" for q in c["options"]))
        opt_i=next(i for i,q in enumerate(o["cases"][case_i]["options"]) if q["status"]=="admissible-single-active")
        mods=[
            lambda x:x["cases"][case_i]["options"][opt_i].update(tangential_impulse=123.),
            lambda x:x["cases"][case_i]["options"][opt_i].update(outgoing_spin=-11.),
            lambda x:x["cases"][case_i]["options"][opt_i]["frames"][25].update(orientation=7.),
            lambda x:x["cases"][case_i]["options"][opt_i].update(energy_after=10.),
            lambda x:x["cases"][case_i]["options"][opt_i].update(status="rejected-penetration"),
            lambda x:x["cases"][case_i].update(actual_active_contact_observed=True),
            lambda x:x.update(frictional_simultaneous_two_contact_manifold_solved=True),
            lambda x:x["by_parameter"][0].update(accepted_single_face_candidates=900),
            lambda x:x["original_source_geometry"]["surfaces"][0]["endpoints"][0].__setitem__(0,0.)
        ]
        for index,mod in enumerate(mods):
            candidate=deepcopy(o);mod(candidate)
            with self.subTest(index=index),self.assertRaises(ValueError):oracle(candidate)

if __name__=="__main__":unittest.main()
