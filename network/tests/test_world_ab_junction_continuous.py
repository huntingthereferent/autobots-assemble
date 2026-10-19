"""Independent geometry, energy and event-time checks for Trial 06.

Reconstruct independent source segment distances and impulse invariants from
recorded event/frame history; no use of the generator's swept-contact routine.
"""
from copy import deepcopy
from math import hypot,isclose
import unittest
from systems.workspace.world_ab_junction_continuous import (
    run,trace,nearest,SCHEMA,HORIZON,R,I,STEP)
from systems.workspace.world_ab_connected_routing import assemble,PROBE_Y

def check(out):
    if (out["schema"]!=SCHEMA or out["geometry"]!=assemble() or
        out["physical_world_dimensions"]!=[24,6] or
        out["finite_segment_endpoints_enabled"] is not True or
        out["multi_contact_manifold_solver"] is not False or
        out["full_original_blueprint_generated"] is not False):
        raise ValueError("source or claim boundary changed")
    geo=out["geometry"]
    for key,faces in (("baseline_finite_capsule",geo["surfaces"][:1]),
                      ("connected_finite_capsule",geo["surfaces"])):
        for y,case in zip(out["probe_levels"],out[key]):
            if abs(case["entry_y"]-y)>1e-9:
                raise ValueError("substituted probe source")
            frames=case["frames"]
            if not frames or frames[0]["position"]!=[12.,round(y,9)]:
                raise ValueError("initial state forged")
            if case["status"] not in ("completed","unresolved-multiple-contacts",
                                     "unresolved-event-budget","penetration",
                                     "world-edge-reached-no-boundary-response","outside-world"):
                raise ValueError("unknown settlement state")
            if case["status"]=="completed" and abs(frames[-1]["time"]-HORIZON)>1e-8:
                raise ValueError("simulation ended early")
            if case["exit"]!=frames[-1]:
                raise ValueError("reported exit differs from observation")
            last_time=0.
            for i,ev in enumerate(case["contacts"]):
                t=ev["time"]
                if not last_time<=t<=frames[-1]["time"]+1e-8:
                    raise ValueError("event chronology reversed")
                last_time=t
                material=next((f for f in faces if f["id"]==ev["surface_id"]),None)
                if material is None:raise ValueError("contact with nonexistent face")
                d,_,u=nearest(ev["center"],material)
                if abs(d-R)>1e-7:raise ValueError("contact not on finite surface capsule")
                n=ev["normal"]
                if abs(hypot(*n)-1)>1e-7:raise ValueError("contact normal not unit")
                vn=sum(a*b for a,b in zip(ev["incoming_velocity"],n))
                if vn>=0:raise ValueError("event not incoming")
                tangent=(-n[1],n[0])
                jn=-2*vn
                slip=sum(a*b for a,b in zip(ev["incoming_velocity"],tangent))-ev["incoming_spin"]*R
                jt=max(-.4*jn,min(.4*jn,-slip/(1+R*R/I)))
                want_v=[ev["incoming_velocity"][j]+jn*n[j]+jt*tangent[j] for j in (0,1)]
                want_spin=ev["incoming_spin"]-R*jt/I
                if (any(abs(a-b)>2e-7 for a,b in zip(want_v,ev["outgoing_velocity"])) or
                    abs(want_spin-ev["outgoing_spin"])>2e-7 or
                    abs(ev["normal_impulse"]-jn)>2e-7 or
                    abs(ev["tangential_impulse"]-jt)>2e-7):
                    raise ValueError("recorded physical impulse or spin not independently conserved")
                if ev["energy_after"]>ev["energy_before"]+1e-8:
                    raise ValueError("contact added energy")
            for i,frame in enumerate(frames):
                if abs(frame["time"]-i*STEP)>2e-7 and case["status"]=="completed":
                    raise ValueError("frame observation moved in time")
                if not (R-1e-6<=frame["position"][0]<=24-R+1e-6 and
                        R-1e-6<=frame["position"][1]<=6-R+1e-6):
                    raise ValueError("recorded disc outside virtual WORLD")
                for f in faces:
                    d,_,_=nearest(frame["position"],f)
                    if d<R-3e-7:raise ValueError("recorded penetration")
            # The last sampled state and first-contact relation must be a
            # consequence of actual events, not an authored label.
            expected_first=case["contacts"][0]["surface_id"] if case["contacts"] else None
            if expected_first!=case["first_contact"]:
                raise ValueError("first-contact source label not witnessed")
    completed=sum(x["status"]=="completed" for x in out["connected_finite_capsule"])
    if out["completed_cases"]!=completed:
        raise ValueError("completed-path count changed")
    return True

class Trial06ContinuousJunctionTests(unittest.TestCase):
    def test_01_full_finite_segment_motion_and_source_replay(self):
        data=run()
        self.assertTrue(check(data))
        self.assertEqual(len(data["probe_levels"]),10)
        self.assertEqual(data["completed_cases"],10)
        self.assertEqual(data["unresolved_cases"],[])
    def test_02_endpoints_are_real_not_infinite_planes(self):
        data=run()
        cases=data["baseline_finite_capsule"]
        self.assertIsNone(cases[0]["first_contact"])
        self.assertIsNotNone(cases[1]["first_contact"])
        self.assertIn("endpoint",cases[1]["contacts"][0]["feature"])
        self.assertIsNotNone(cases[6]["first_contact"]) # y=2.25 endpoint
        self.assertEqual(cases[1]["status"],"world-edge-reached-no-boundary-response")
        self.assertAlmostEqual(cases[1]["exit"]["position"][1],R,places=7)
    def test_03_no_unsafe_future_or_missing_geometry_promoted(self):
        data=run()
        self.assertTrue(data["geometry"]["finite_intersection_verified"])
        self.assertFalse(data["multi_contact_manifold_solver"])
        self.assertFalse(data["full_original_blueprint_generated"])
        self.assertFalse(data["source_04B_branches_simultaneously_generated"])
    def test_04_simultaneous_collisions_stop_instead_of_fabricating(self):
        geo=assemble()
        clone=deepcopy(geo["surfaces"][0])
        clone["id"]="distinct-but-coincident-face"
        bad=trace(1.6,[geo["surfaces"][0],clone])
        self.assertEqual(bad["status"],"unresolved-multiple-contacts")
        self.assertIsNotNone(bad["unresolved"])
        self.assertEqual(bad["contacts"],[])
    def test_05_false_source_and_physics_mutants_rejected(self):
        data=run()
        edits=[
            lambda z:z["connected_finite_capsule"][0]["contacts"][0].update(normal_impulse=0.),
            lambda z:z["connected_finite_capsule"][1]["contacts"][0].update(center=[9.,4.]),
            lambda z:z["connected_finite_capsule"][4]["exit"].update(position=[0.,0.]),
            lambda z:z["connected_finite_capsule"][3]["frames"][12].update(position=[10.,1.]),
            lambda z:z["geometry"]["surfaces"][1]["endpoints"][0].__setitem__(0,4.),
            lambda z:z.update(completed_cases=0),
        ]
        for i,edit in enumerate(edits):
            changed=deepcopy(data);edit(changed)
            with self.subTest(i=i),self.assertRaises(ValueError):check(changed)
    def test_06_original_first_contact_is_distinct_from_real_endpoint_physics(self):
        data=run()
        before=data["baseline_finite_capsule"]
        after=data["connected_finite_capsule"]
        self.assertNotEqual(before[0]["first_contact"],after[0]["first_contact"])
        self.assertEqual(set(x["first_contact"] for x in after if x["first_contact"]),set(
            face["id"] for face in data["geometry"]["surfaces"]))
        self.assertTrue(all(len(x["frames"])==31 for x in after))
    def test_07_unbounded_probe_inputs_rejected(self):
        geo=assemble()
        with self.assertRaises(ValueError):trace(-.1,geo["surfaces"])
        with self.assertRaises(ValueError):trace(6.1,geo["surfaces"])

if __name__=="__main__":unittest.main()
