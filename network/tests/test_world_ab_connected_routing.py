"""Independent trial-05 topology and continuous first-contact witness.

Derives face intersection independently by implicit line equations, uses
incoming-disc swept-plane intersection + finite segment constraint for each
probe and re-derives frictional impulse and torque directly from constants.
Generated reference shape names are read ONLY after this source test, and
not made available to the geometry constructor.
"""
from copy import deepcopy
from math import isclose,hypot
from pathlib import Path
import json
import unittest

from systems.workspace.world_ab_connected_routing import run,assemble,PROBE_Y,SCHEMA
from systems.workspace.world_ab_oblique_rotation import R,I
EPS=8e-8
def near(a,b,label):
    if not isclose(a,b,rel_tol=0,abs_tol=EPS):
        raise ValueError(f"{label}: {a} != {b}")
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def mul(k,a):return tuple(k*q for q in a)

def verify_source_geometry(g):
    if g["schema"]!=SCHEMA or g["source_experiment_is_separate_cross_run_branches"] is not True:
        raise ValueError("original counterfactual source boundary changed")
    if g["topology"]!={"segments":2,"intersections":1,"connected_components":1,"curved_segments":0}:
        raise ValueError("connected topology misrepresented")
    if g["simultaneous_disc_multicontact_resolved"] is not False:
        raise ValueError("unsafe multi-contact physics promoted to supported")
    faces=g["surfaces"]
    if len(faces)!=2 or {x["source_original_angle"] for x in faces}!={0,20}:
        raise ValueError("source face identities incomplete")
    vertex=g["junction"]
    for i,s in enumerate(faces):
        n=s["normal"]
        near(hypot(*n),1,f"n{i} normalization")
        anchor=s["anchor"]
        # Recalculate the same line as a plane and check intersection point.
        near(dot(sub(vertex,anchor),n),0,f"junction plane {i}")
        tangent=(-n[1],n[0])
        coord=dot(sub(vertex,anchor),tangent)
        near(coord,g["junction_local_coordinates"][i],f"junction local coordinate {i}")
        if not -0.5<=coord<=0.5:raise ValueError("intersection outside measured finite segment")
        ends=[sub(anchor,mul(.5,tangent)),add(anchor,mul(.5,tangent))]
        for j in (0,1):
            for k in (0,1):near(ends[j][k],s["endpoints"][j][k],"source endpoint")
    return True

def independently_verify_route(g,result):
    faces=g["surfaces"]
    if result["schema"]!=SCHEMA or result["geometry"]!=g:
        raise ValueError("substituted source geometry")
    if result["probe_y_levels"]!=list(PROBE_Y):
        raise ValueError("unrecorded probe inputs")
    levels=set()
    hits=set()
    for index,level in enumerate(PROBE_Y):
        for collection,active in (("baseline_first_face_only",faces[:1]),
                                   ("assembled_two_faces",faces)):
            actual=result[collection][index]
            near(actual["initial"][0],12,"probe initial x")
            near(actual["initial"][1],level,"probe initial y")
            candidates=[]
            for s in active:
                n=s["normal"]
                vn=-2*n[0]
                if vn>=0:continue
                distance=dot((12-s["anchor"][0],level-s["anchor"][1]),n)
                t=(.25-distance)/vn
                if t<=0:continue
                cp=(12-2*t,level)
                material=sub(cp,mul(.25,n))
                tangent=(-n[1],n[0])
                u=dot(sub(material,s["anchor"]),tangent)
                if abs(u)<=.5+1e-8:candidates.append((t,s,cp,u))
            candidates.sort(key=lambda q:q[0])
            winner=candidates[0] if candidates else None
            if winner is None:
                if (actual["source_first_contact"] is not None or
                    actual["hit_time"] is not None or actual["contact_impulse"] is not None):
                    raise ValueError("browser reported a phantom source contact")
                continue
            t,s,p,u=winner
            if (actual["source_first_contact"]!=s["id"] or
                actual["contact_impulse"] is None):
                raise ValueError("independently observed first contact disagrees")
            near(actual["hit_time"],t,"first contact time")
            for i in (0,1):near(actual["contact_center"][i],p[i],"contact center")
            near(actual["contact_tangent_coordinate"],u,"finite face span")
            n=s["normal"];tau=(-n[1],n[0])
            jn=4*n[0]
            slip=-2*tau[0]
            jt=max(-.4*jn,min(.4*jn,-slip/(1+(.25**2)/I)))
            outgoing=add((-2,0),add(mul(jn,n),mul(jt,tau)))
            spin=-.25*jt/I
            for i in (0,1):
                near(actual["outgoing_velocity"][i],outgoing[i],"outgoing")
                near(actual["look_after"][i],p[i]+.2*outgoing[i],"look after")
            near(actual["angular_velocity"],spin,"new angular impulse")
            near(actual["contact_impulse"]["normal_impulse"],jn,"normal impulse")
            near(actual["contact_impulse"]["tangential_impulse"],jt,"tangential impulse")
            if collection=="assembled_two_faces":hits.add(s["id"])
        a=result["baseline_first_face_only"][index]
        b=result["assembled_two_faces"][index]
        if a["source_first_contact"]!=b["source_first_contact"] or a["outgoing_velocity"]!=b["outgoing_velocity"]:
            levels.add(level)
    if result["route_changed_probe_levels"]!=list(sorted(levels)):
        raise ValueError("measured changed path levels differ")
    if sorted(hits)!=result["distinct_first_contacts"]:
        raise ValueError("independent contact route identities altered")
    if result["functional_first_contact_splitting_verified"]!=(len(hits)>=2 and bool(levels)):
        raise ValueError("first contact split asserted without real probe distinction")
    if result["continuous_multicontact_navigation_verified"] is not False or result["target_original_blueprint_shapes_generated"] is not False:
        raise ValueError("first contact test misrepresented as complete guide")
    return True

class Trial05ConnectedRoutingTests(unittest.TestCase):
    def test_01_segment_intersection_is_inside_both_original_measured_faces(self):
        assert verify_source_geometry(assemble())
    def test_02_independent_finite_disc_sweep_and_routing(self):
        r=run();self.assertTrue(verify_source_geometry(r["geometry"]))
        self.assertTrue(independently_verify_route(r["geometry"],r))
        self.assertTrue(r["functional_first_contact_splitting_verified"])
        self.assertEqual(len(r["route_changed_probe_levels"]),3)
        self.assertEqual(r["route_changed_probe_levels"],[.9,1.05,1.2])
        self.assertEqual(r["assembled_two_faces"][-1]["source_first_contact"],None)
    def test_03_parallel_wall_baseline_is_not_functional_branch_split(self):
        r=run()
        prior=set(x["source_first_contact"] for x in r["baseline_first_face_only"] if x["source_first_contact"])
        later=set(x["source_first_contact"] for x in r["assembled_two_faces"] if x["source_first_contact"])
        self.assertEqual(len(prior),1);self.assertEqual(len(later),2)
    def test_04_future_sources_and_fake_results_are_rejected(self):
        r=run()
        changes=[
          lambda q:q["geometry"]["junction"].__setitem__(0,8.),
          lambda q:q["geometry"]["surfaces"][0]["endpoints"][0].__setitem__(1,5.),
          lambda q:q["assembled_two_faces"][0].update(source_first_contact=None),
          lambda q:q["assembled_two_faces"][1].update(hit_time=3.5),
          lambda q:q["assembled_two_faces"][3].update(outgoing_velocity=[0,0]),
          lambda q:q.update(functional_first_contact_splitting_verified=False),
        ]
        for i,change in enumerate(changes):
            q=deepcopy(r);change(q)
            with self.subTest(i=i),self.assertRaises(ValueError):
                verify_source_geometry(q["geometry"])
                verify_route_or_fail(q)
    def test_05_no_guide_funnel_spiral_is_promoted_from_crossed_lines(self):
        r=run()
        labels=json.loads((Path(__file__).parent/"fixtures/world_ab_original_visual_reference_v1.json").read_text())
        self.assertEqual(labels["generated_geometries_required"],["guide","funnel","diverter","spiral"])
        self.assertEqual(r["geometry"]["topology"]["curved_segments"],0)
        self.assertFalse(r["target_original_blueprint_shapes_generated"])
        self.assertFalse(r["simultaneous_source_generation_proven"])
def verify_route_or_fail(q):
    return independently_verify_route(q["geometry"],q)
if __name__=="__main__":unittest.main()
