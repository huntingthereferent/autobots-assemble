"""Independent physics/identity/falsification oracle for Trial 09."""
from copy import deepcopy
from math import cos,sin,radians,hypot
import unittest
from systems.workspace.world_ab_two_contact_stress import (
    SCHEMA,ANGLES,OFFSETS,LEAD,SPEED,run)
from systems.workspace.world_ab_two_contact_candidate import run as trial08_run
from systems.workspace.world_ab_junction_threshold import run as threshold_run,arrival_pair
from systems.workspace.world_ab_junction_continuous import nearest,R,HORIZON,STEP
from network.tests.test_world_ab_junction_continuous import source_equivalent

def check(out):
    source=threshold_run();orig=source["source_geometry"]
    if out["schema"]!=SCHEMA or not source_equivalent(out["original_source_geometry"],orig):
        raise ValueError("original source drifted")
    if out["original_trial07_contact"]!=source["junction_contact"]:
        raise ValueError("prior measured tie replaced")
    if out["original_trial08_outgoing"]!=trial08_run()["candidate"]["outgoing_velocity"]:
        raise ValueError("original Trial 08 observation changed")
    if out["incoming_angle_grid"]!=list(ANGLES) or out["surface_rotation_grid"]!=list(OFFSETS):
        raise ValueError("predeclared stress grid changed")
    if out["controlled_contact_lead"]!=LEAD or out["speed"]!=SPEED:
        raise ValueError("unwitnessed initial conditions")
    if (out["original_trial06_friction"]!=.4 or out["candidate_friction"]!=0. or
        out["original_surface_modified"] is not False or
        out["rotated_faces_are_original_source"] is not False or
        out["general_two_contact_physics_proven"] is not False or
        out["frictional_manifold_solved"] is not False or
        out["real_material_equivalence"] is not False or
        out["original_blueprint_generated"] is not False):
        raise ValueError("unsupported physical claim")
    if len(out["cases"])!=len(ANGLES)*len(OFFSETS):
        raise ValueError("missing predeclared stress controls")
    original_y=source["junction_contact"]["entry_y"]
    hits=arrival_pair(original_y,orig["surfaces"])
    center=hits[0]["center"]
    for i,(offset,angle) in enumerate((d,a) for d in OFFSETS for a in ANGLES):
        c=out["cases"][i]
        if c["incoming_angle_degrees"]!=angle or c["surface_B_rotation_degrees"]!=offset:
            raise ValueError("wrong predeclared case sequence")
        if offset==0:
            if c["geometry_kind"]!="original-source-geometry" or not source_equivalent(c["surfaces"],orig["surfaces"]):
                raise ValueError("original surface replaced")
        else:
            if c["geometry_kind"]!="controlled-geometry-not-original" or not source_equivalent(c["surfaces"][0],orig["surfaces"][0]):
                raise ValueError("original A face changed")
            if (c["surfaces"][1]["source_parent_id"]!=orig["surfaces"][1]["id"] or
                c["surfaces"][1]["geometry_role"]!="explicit-rotated-counterfactual" or
                c["surfaces"][1]["rotation_degrees"]!=offset):
                raise ValueError("controlled face provenance forged")
        vin=(-SPEED*cos(radians(angle)),-SPEED*sin(radians(angle)))
        start=(center[0]-LEAD*vin[0],center[1]-LEAD*vin[1])
        if any(abs(c["incoming_velocity"][axis]-vin[axis])>1e-8 for axis in (0,1)):
            raise ValueError("incident direction changed")
        if any(abs(c["start_center"][axis]-start[axis])>1e-8 or abs(c["contact_center"][axis]-center[axis])>1e-8 for axis in (0,1)):
            raise ValueError("initial path or contact center forged")
        for s in c["surfaces"]:
            if abs(nearest(center,s)[0]-R)>3e-7:
                raise ValueError("measured tie not physically retained")
        normals=[]
        for s,recorded in zip(c["surfaces"],c["normals"]):
            # Independent direction: face tangent gives two possible normals;
            # choose the one pointing from the line toward the disc center.
            a,b=s["endpoints"];t=(b[0]-a[0],b[1]-a[1]);l=hypot(*t)
            u=(-t[1]/l,t[0]/l);d=(center[0]-a[0],center[1]-a[1])
            n=u if sum(u[k]*d[k] for k in (0,1))>0 else (-u[0],-u[1])
            if max(abs(n[k]-recorded[k]) for k in (0,1))>1e-7:
                raise ValueError("contact normal unrelated to finite geometry")
            normals.append(n)
        # Compute unilateral impulses independently from 2x2 matrix geometry.
        g=sum(normals[0][k]*normals[1][k] for k in (0,1))
        det=1-g*g
        if det<=1e-7:raise ValueError("unexpected degenerate predeclared control")
        b0=-2*sum(vin[k]*normals[0][k] for k in (0,1))
        b1=-2*sum(vin[k]*normals[1][k] for k in (0,1))
        impulses=((b0-g*b1)/det,(b1-g*b0)/det)
        expected="accepted-local-candidate" if b0>1e-8 and b1>1e-8 and min(impulses)>1e-9 else (
                 "rejected-not-incoming" if min(b0,b1)<=2e-9 else "rejected-unilateral")
        if c["status"]!=expected:
            raise ValueError("candidate silently promoted/rejected under physical controls")
        if c["status"]!="accepted-local-candidate":
            if c["candidate"] is not None or c["frames"] or not c["reason"]:
                raise ValueError("rejected candidate has invented movement")
            continue
        data=c["candidate"];js=data["normal_impulses"];vout=data["outgoing_velocity"]
        if any(abs(js[j]-impulses[j])>2e-7 for j in (0,1)):
            raise ValueError("reported impulses not independently verified")
        for k in (0,1):
            if abs(vout[k]-(vin[k]+sum(js[j]*normals[j][k] for j in (0,1))))>3e-7:
                raise ValueError("candidate momentum not derived from actual normal impulses")
        if abs(sum(v*v for v in vout)-sum(v*v for v in vin))>3e-7:
            raise ValueError("kinetic energy violation")
        if len(c["frames"])!=round(HORIZON/STEP)+1:
            raise ValueError("31 source observation slots missing")
        for f_idx,frame in enumerate(c["frames"]):
            t=f_idx*STEP
            v=vin if t<LEAD else vout
            p=(start[0]+t*vin[0],start[1]+t*vin[1]) if t<=LEAD else (
                center[0]+(t-LEAD)*vout[0],center[1]+(t-LEAD)*vout[1])
            if abs(frame["time"]-t)>1e-8 or any(abs(frame["position"][k]-p[k])>3e-7 for k in (0,1)):
                raise ValueError("sampled motion not connected to impulse")
            if any(abs(frame["velocity"][k]-v[k])>3e-7 for k in (0,1)):
                raise ValueError("inconsistent recorded velocity")
            if not R<=p[0]<=24-R or not R<=p[1]<=6-R:
                raise ValueError("candidate exited bounded WORLD")
            if any(nearest(p,s)[0]<R-3e-7 for s in c["surfaces"]):
                raise ValueError("candidate penetrated a finite capsule")
        # Analytic line-sided clearance across ALL intermediate times, not
        # just frame samples, given the exact initially tangent construction.
        if any(sum(vin[k]*n[k] for k in (0,1))>=-1e-8 or
               sum(vout[k]*n[k] for k in (0,1))<=1e-8 for n in normals):
            raise ValueError("nonpenetration between observation frames not established")
    counts={k:sum(c["status"]==k for c in out["cases"])
            for k in ("accepted-local-candidate","rejected-unilateral",
                      "rejected-not-incoming","rejected-constraint")}
    if out["counts"]!=counts:raise ValueError("accept/reject counts forged")
    if counts["accepted-local-candidate"]<1 or counts["rejected-unilateral"]<1:
        raise ValueError("failed to expose a real success and a real counterexample")
    return True

class Trial09Tests(unittest.TestCase):
    def test_source_bound_stress_grid(self):
        self.assertTrue(check(run()))
    def test_original_scenario_still_accepted(self):
        out=run();baseline=[c for c in out["cases"] if c["surface_B_rotation_degrees"]==0 and c["incoming_angle_degrees"]==0]
        self.assertEqual(len(baseline),1)
        self.assertEqual(baseline[0]["status"],"accepted-local-candidate")
    def test_physical_rejections_are_not_called_completed(self):
        o=run()
        self.assertGreater(o["counts"]["rejected-unilateral"],0)
        self.assertTrue(all(not x["frames"] and x["candidate"] is None for x in o["cases"] if x["status"].startswith("rejected")))
    def test_rotated_geometry_is_explicit_control_not_original(self):
        o=run();self.assertFalse(o["rotated_faces_are_original_source"])
        self.assertTrue(all(x["geometry_kind"]=="controlled-geometry-not-original" for x in o["cases"] if x["surface_B_rotation_degrees"]!=0))
    def test_mutants_not_promoted(self):
        out=run()
        edits=[
            lambda x:x["cases"][0].update(status="accepted-local-candidate"),
            lambda x:x["cases"][17]["normals"][0].__setitem__(0,0.),
            lambda x:x["cases"][17]["surfaces"][1]["endpoints"][0].__setitem__(0,0.),
            lambda x:x["cases"][17]["candidate"]["normal_impulses"].__setitem__(0,100.),
            lambda x:x["cases"][17]["frames"][20]["position"].__setitem__(0,1.),
            lambda x:x.update(general_two_contact_physics_proven=True),
            lambda x:x["counts"].update({"accepted-local-candidate":35}),
        ]
        for i,edit in enumerate(edits):
            bad=deepcopy(out)
            edit(bad)
            with self.subTest(i=i),self.assertRaises((ValueError,TypeError)):
                check(bad)

if __name__=="__main__":unittest.main()
