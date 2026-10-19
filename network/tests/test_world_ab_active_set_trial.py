"""Independent active-set oracle for WORLD Trial 10; do not select a physical branch."""
import unittest
from copy import deepcopy
from math import cos,sin,radians,hypot
from systems.workspace.world_ab_active_set_trial import run,SCHEMA,ACTIVE_SETS
from systems.workspace.world_ab_two_contact_stress import run as prior,ANGLES,OFFSETS,LEAD,SPEED
from systems.workspace.world_ab_junction_continuous import R,HORIZON,STEP
from network.tests.test_world_ab_junction_continuous import source_equivalent

def distance(p,s):
    a,b=s["endpoints"];dx=b[0]-a[0];dy=b[1]-a[1]
    u=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy)))
    return hypot(p[0]-a[0]-u*dx,p[1]-a[1]-u*dy)

def check(out):
    src=prior()
    if out["schema"]!=SCHEMA or out["source_trial09_schema"]!=src["schema"]:
        raise ValueError("source schema switched")
    if not source_equivalent(out["original_source_geometry"],src["original_source_geometry"]):
        raise ValueError("original source changed")
    if out["angle_grid"]!=list(ANGLES) or out["rotation_grid"]!=list(OFFSETS):
        raise ValueError("source test grid substituted")
    if out["active_sets"]!=[list(s) for s in ACTIVE_SETS] or out["original_trial09_two_active_counts"]!=src["counts"]:
        raise ValueError("active-set or prior result substituted")
    if out["original_trial06_friction"]!=.4 or out["candidate_friction"]!=0 or out["comparison_restitution"]!=1:
        raise ValueError("friction and restitution boundary drift")
    for flag in ("simultaneous_multicontact_physics_uniquely_determined",
                 "physical_active_contacts_observed","sequential_impacts_temporally_witnessed",
                 "original_source_surfaces_modified","rotated_faces_are_original_source",
                 "original_blueprint_generated","earth_material_equivalence"):
        if out[flag] is not False:raise ValueError("unobserved real-world claim promoted")
    if len(out["cases"])!=len(src["cases"]):raise ValueError("missing control cases")
    counts={"no-local-candidate":0,"single-admissible":0,"multiple-admissible":0}
    recovered=0
    for i,(case,c) in enumerate(zip(out["cases"],src["cases"])):
        if case["original_index"]!=i or case["incoming_angle_degrees"]!=c["incoming_angle_degrees"] or case["surface_B_rotation_degrees"]!=c["surface_B_rotation_degrees"]:
            raise ValueError("precommitted case order altered")
        if case["geometry_kind"]!=c["geometry_kind"] or case["source_ids"]!=[s["id"] for s in c["surfaces"]]:
            raise ValueError("original/controlled geometry provenance altered")
        if case["trial09_two_active_status"]!=c["status"] or case["physical_outcome_independently_observed"] is not False:
            raise ValueError("invented prior status or material observation")
        if len(case["alternatives"])!=3:raise ValueError("omitted active set")
        vin=(-SPEED*cos(radians(c["incoming_angle_degrees"])),-SPEED*sin(radians(c["incoming_angle_degrees"])))
        ns=[]
        center=c["contact_center"];start=c["start_center"]
        for seg,recorded in zip(c["surfaces"],c["normals"]):
            a,b=seg["endpoints"];t=(b[0]-a[0],b[1]-a[1]);length=hypot(*t)
            normal=(-t[1]/length,t[0]/length)
            signed=sum(normal[k]*(center[k]-a[k]) for k in (0,1))
            if signed<0:normal=(-normal[0],-normal[1])
            if any(abs(normal[k]-recorded[k])>1e-7 for k in (0,1)):
                raise ValueError("contact normals divorced from physical segments")
            if abs(distance(center,seg)-R)>3e-7:
                raise ValueError("contact center not tangent to original/controlled finite face")
            ns.append(normal)
        admissible=0
        for active,answer in zip(ACTIVE_SETS,case["alternatives"]):
            if answer["active_indices"]!=list(active) or answer["active_ids"]!=[c["surfaces"][j]["id"] for j in active]:
                raise ValueError("active set labels switched")
            # Independent small Gram solve without the generator's solver.
            if len(active)==1:
                j=-2*sum(vin[k]*ns[active[0]][k] for k in (0,1))
                J=[0.,0.];J[active[0]]=j
            else:
                g=sum(ns[0][k]*ns[1][k] for k in (0,1))
                det=1-g*g
                b0=-2*sum(vin[k]*ns[0][k] for k in (0,1))
                b1=-2*sum(vin[k]*ns[1][k] for k in (0,1))
                J=[(b0-g*b1)/det,(b1-g*b0)/det]
            outv=[vin[k]+sum(J[j]*ns[j][k] for j in (0,1)) for k in (0,1)]
            positive=all(J[k]>1e-8 for k in active)
            separating=all(sum(outv[k]*n[k] for k in (0,1))>=-1e-8 for n in ns)
            energy=abs(sum(z*z for z in outv)-sum(z*z for z in vin))<=4e-7
            should_accept=positive and separating and energy
            if (answer["status"]=="admissible-local-model")!=should_accept:
                raise ValueError("active-set accept/reject rule inconsistent with independent momentum")
            if not should_accept:
                if answer["outgoing_velocity"] is not None or answer["normal_impulses"] is not None or answer["frames"] or not answer["reason"]:
                    raise ValueError("rejected impulse still has fake completed motion")
                continue
            admissible+=1
            Jactual=answer["normal_impulses"];outactual=answer["outgoing_velocity"]
            if len(Jactual)!=2 or any(abs(Jactual[j]-J[j])>2e-7 for j in (0,1)):
                raise ValueError("normal impulse not source determined")
            if any(abs(outactual[k]-outv[k])>2e-7 for k in (0,1)):
                raise ValueError("outgoing state not original momentum consequence")
            for k in active:
                if abs(sum(outactual[d]*ns[k][d] for d in (0,1))+sum(vin[d]*ns[k][d] for d in (0,1)))>3e-7:
                    raise ValueError("active normal restitution failed")
            if abs(answer["energy_before"]-.5*sum(v*v for v in vin))>2e-7 or abs(answer["energy_after"]-.5*sum(v*v for v in outactual))>2e-7:
                raise ValueError("candidate energy record forged")
            if len(answer["frames"])!=round(HORIZON/STEP)+1:
                raise ValueError("missing finite movement observations")
            for idx,frame in enumerate(answer["frames"]):
                t=idx*STEP
                p=[start[k]+vin[k]*t for k in (0,1)] if t<=LEAD else [
                    center[k]+(t-LEAD)*outactual[k] for k in (0,1)]
                v=vin if t<LEAD else outactual
                if abs(frame["time"]-t)>2e-8 or any(abs(frame["position"][k]-p[k])>3e-7 for k in (0,1)):
                    raise ValueError("frame not reconstructed by active-set motion")
                if any(abs(frame["velocity"][k]-v[k])>3e-7 for k in (0,1)):
                    raise ValueError("frame velocity altered")
                if any(distance(frame["position"],s)<R-3e-7 for s in c["surfaces"]):
                    raise ValueError("penetration of actual finite source")
                if not R<=p[0]<=24-R or not R<=p[1]<=6-R:
                    raise ValueError("virtual world edge escaped")
        if case["admissible_count"]!=admissible:raise ValueError("active-set count forged")
        status="multiple-admissible" if admissible>1 else "single-admissible" if admissible else "no-local-candidate"
        if case["classification"]!=status:raise ValueError("collision uniqueness misrepresented")
        counts[status]+=1
        if c["status"].startswith("rejected") and admissible>0:recovered+=1
        pair=case["alternatives"][2]
        if (pair["status"]=="admissible-local-model")!=(c["status"]=="accepted-local-candidate"):
            raise ValueError("trial09 two-face refusal overwritten")
    if counts!=out["counts"] or out["trial09_rejected_cases_with_local_alternatives"]!=recovered:
        raise ValueError("classification summary not source verified")
    if recovered==0 or counts["multiple-admissible"]==0 or counts["single-admissible"]==0:
        raise ValueError("missing discriminating controls")
    return True

class Trial10Tests(unittest.TestCase):
    def test_all_35_unchanged_source_scenarios(self):self.assertTrue(check(run()))
    def test_original_two_active_result_preserved(self):
        o=run()
        assert all((c["trial09_two_active_status"]=="accepted-local-candidate")==(
            c["alternatives"][2]["status"]=="admissible-local-model") for c in o["cases"])
    def test_rejected_pair_can_have_other_admissible_branches(self):
        o=run()
        self.assertGreater(o["trial09_rejected_cases_with_local_alternatives"],0)
    def test_multiple_possible_results_are_not_selected_as_true_physics(self):
        o=run()
        self.assertGreater(o["counts"]["multiple-admissible"],0)
        self.assertFalse(o["physical_active_contacts_observed"])
    def test_mutated_provenance_impulse_motion_or_claim_rejected(self):
        o=run()
        base=next(i for i,c in enumerate(o["cases"]) if c["alternatives"][0]["status"]=="admissible-local-model")
        edits=[
            lambda x:x["cases"][base]["alternatives"][0]["normal_impulses"].__setitem__(0,99.),
            lambda x:x["cases"][base]["alternatives"][0]["frames"][22]["position"].__setitem__(1,5.),
            lambda x:x["cases"][base].update(admissible_count=0),
            lambda x:x["cases"][base].update(physical_outcome_independently_observed=True),
            lambda x:x.update(sequential_impacts_temporally_witnessed=True),
            lambda x:x["original_source_geometry"]["surfaces"][0]["endpoints"][0].__setitem__(0,0.),
            lambda x:x["counts"].update({"multiple-admissible":35}),
        ]
        for i,edit in enumerate(edits):
            invalid=deepcopy(o);edit(invalid)
            with self.subTest(i=i),self.assertRaises(ValueError):check(invalid)

if __name__=="__main__":unittest.main()
