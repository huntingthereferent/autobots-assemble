"""Independent finite-motion and impulse conservation oracle for Trial 08."""
import unittest
from copy import deepcopy
from math import hypot
from systems.workspace.world_ab_two_contact_candidate import (
    SCHEMA,run,solve_two_normals,START_V)
from systems.workspace.world_ab_junction_continuous import (
    R,HORIZON,STEP,I,nearest,trace)
from systems.workspace.world_ab_junction_threshold import run as threshold_run,arrival_pair
from network.tests.test_world_ab_junction_continuous import source_equivalent

def verify(out):
    source=threshold_run()
    if out["schema"]!=SCHEMA or not source_equivalent(out["geometry"],source["source_geometry"]):
        raise ValueError("source geometry or schema replaced")
    if (out["original_trial06_friction"]!=.4 or out["candidate_friction"]!=0. or
        out["simultaneous_frictional_manifold_solved"] is not False or
        out["arbitrary_junctions_solved"] is not False or
        out["real_material_behavior_verified"] is not False or
        out["original_blueprint_generated"] is not False or
        out["candidate_is_a_new_comparison_not_original_friction_physics"] is not True):
        raise ValueError("claim or friction boundary falsified")
    c=out["candidate"]
    y=source["junction_contact"]["entry_y"]
    faces=source["source_geometry"]["surfaces"]
    hits=arrival_pair(y,faces)
    t=(hits[0]["time"]+hits[1]["time"])/2
    exact_center=(hits[0]["center"][0],y)
    if abs(c["entry_y"]-y)>1e-11 or abs(c["collision_time"]-t)>2e-9:
        raise ValueError("collision time/height substituted")
    if any(abs(a-b)>3e-8 for a,b in zip(c["collision_center"],exact_center)):
        raise ValueError("collision center substituted")
    if c["source_ids"]!=[s["id"] for s in faces]:
        raise ValueError("source IDs replaced")
    normals=[h["normal"] for h in hits]
    if not source_equivalent(c["normals"],[list(n) for n in normals]):
        raise ValueError("contact normals substituted")
    # Independent impulse check: measured momentum change is exactly the
    # sum of two unilateral source-normal impulses, regardless of solver.
    j=c["normal_impulses"]
    if len(j)!=2 or min(j)<=0:raise ValueError("nonpositive impulse")
    vin=START_V;vout=c["outgoing_velocity"]
    for axis in (0,1):
        expected=vin[axis]+j[0]*normals[0][axis]+j[1]*normals[1][axis]
        if abs(vout[axis]-expected)>2e-7:
            raise ValueError("momentum jump not explained by two measured normals")
    if c["incoming_velocity"]!=[-2.,0.] or c["incoming_spin"]!=0. or c["outgoing_spin"]!=0.:
        raise ValueError("frictionless no-spin source changed")
    for n in normals:
        before=sum(vin[k]*n[k] for k in (0,1))
        after=sum(vout[k]*n[k] for k in (0,1))
        if abs(after+before)>2e-7 or after<=0:
            raise ValueError("candidate did not satisfy unilateral normal restitution")
    eb=.5*sum(z*z for z in vin)
    ea=.5*sum(z*z for z in vout)+.5*I*c["outgoing_spin"]**2
    if abs(ea-eb)>2e-7 or abs(c["kinetic_energy_after"]-ea)>2e-7 or abs(c["kinetic_energy_before"]-eb)>2e-7:
        raise ValueError("invented candidate energy")
    if c["friction"]!=0. or c["normal_restitution"]!=1.:
        raise ValueError("friction or restitution misleading")
    if len(c["frames"])!=round(HORIZON/STEP)+1:
        raise ValueError("missing finite observation frames")
    for i,f in enumerate(c["frames"]):
        clock=i*STEP
        if abs(f["time"]-clock)>1e-8:raise ValueError("frame clock corrupted")
        if clock<=t:
            expected=(12.+vin[0]*clock,y+vin[1]*clock)
        else:
            expected=(exact_center[0]+vout[0]*(clock-t),y+vout[1]*(clock-t))
        if any(abs(q-w)>3e-7 for q,w in zip(f["position"],expected)):
            raise ValueError("reported full-horizon motion not consequence of impact")
        if any(abs(q-w)>3e-7 for q,w in zip(f["velocity"],vin if clock<t else vout)):
            raise ValueError("frame motion inconsistent")
        if f["spin"]!=0 or f["orientation"]!=0:raise ValueError("frictionless spin created")
        for s in faces:
            d,_,_=nearest(f["position"],s)
            if d<R-3e-7:raise ValueError("penetration detected by independent closest-point oracle")
        if not R<=f["position"][0]<=24.-R or not R<=f["position"][1]<=6.-R:
            raise ValueError("frame outside finite WORLD")
    if out["baseline_trial06_status"]!="unresolved-multiple-contacts" or c["original_stop"]!=out["baseline_trial06_status"]:
        raise ValueError("existing Trial 06 fail-closed result overwritten")
    if c["candidate_full_horizon_observed"] is not True:
        raise ValueError("candidate scope falsified")
    if out["nearby_trial07_statuses"]!=[
        {"offset":p["offset"],"status":p["status"],"first_contact":p["first_contact"]}
        for p in source["probes"]]:
        raise ValueError("nearby source-control results substituted")
    return True

class Trial08Tests(unittest.TestCase):
    def test_two_contact_candidate_finite_horizon(self):
        o=run()
        self.assertTrue(verify(o))
        self.assertEqual(o["candidate"]["original_stop"],"unresolved-multiple-contacts")
        self.assertEqual(o["candidate"]["candidate_full_horizon_observed"],True)
    def test_independent_source_normals_have_positive_candidate_impulses(self):
        out=run()
        self.assertTrue(all(j>0 for j in out["candidate"]["normal_impulses"]))
        self.assertEqual(out["candidate"]["outgoing_velocity"],[2.,0.])
    def test_reversing_source_order_is_permutation_invariant(self):
        src=threshold_run();hits=arrival_pair(src["junction_contact"]["entry_y"],src["source_geometry"]["surfaces"])
        a=solve_two_normals(START_V,[hits[0]["normal"],hits[1]["normal"]])
        b=solve_two_normals(START_V,[hits[1]["normal"],hits[0]["normal"]])
        self.assertEqual(a["outgoing_velocity"],b["outgoing_velocity"])
        self.assertEqual(a["normal_impulses"],list(reversed(b["normal_impulses"])))
        self.assertEqual(a["kinetic_energy_after"],b["kinetic_energy_after"])
    def test_degenerate_and_nonincoming_contacts_rejected(self):
        with self.assertRaises(ValueError):solve_two_normals((-2.,0.),[(1.,0.),(1.,0.)])
        with self.assertRaises(ValueError):solve_two_normals((-2.,0.),[(1.,0.),(0.,1.)])
        with self.assertRaises(ValueError):solve_two_normals((-2.,0.),[(1.,0.),(-1.,0.)])
    def test_falsified_receipts_rejected(self):
        o=run()
        mutations=[
            lambda x:x["candidate"]["normal_impulses"].__setitem__(0,0.),
            lambda x:x["candidate"]["outgoing_velocity"].__setitem__(1,1.),
            lambda x:x["candidate"]["frames"][25]["position"].__setitem__(0,0.),
            lambda x:x["candidate"].update(kinetic_energy_after=3.),
            lambda x:x.update(simultaneous_frictional_manifold_solved=True),
            lambda x:x["geometry"]["surfaces"][0]["endpoints"][0].__setitem__(0,1.),
            lambda x:x.update(original_trial06_friction=0.),
        ]
        for i,mut in enumerate(mutations):
            damaged=deepcopy(o);mut(damaged)
            with self.subTest(i=i),self.assertRaises(ValueError):verify(damaged)
    def test_original_single_contact_and_nearby_traces_are_not_promoted(self):
        out=run()
        self.assertTrue(verify(out))
        self.assertFalse(out["simultaneous_frictional_manifold_solved"])
        self.assertFalse(out["arbitrary_junctions_solved"])
        self.assertEqual(len(out["nearby_trial07_statuses"]),9)

if __name__=="__main__":unittest.main()
