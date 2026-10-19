"""Independent analytic oracle for source-generated second collision face.

These tests independently calculate two event times and final trajectory from
source wall normal, independently of generator's stepwise contact event loop.
Comparison to original A/B sketch is only after movement evidence is made.
"""
from copy import deepcopy
from math import isclose
from pathlib import Path
import json
import unittest

from systems.workspace.world_ab_contact_trial import HALF,DT,STEPS,WALL,initial
from systems.workspace.world_ab_relation_growth import (
    PROJECTION_DURATION,SCHEMA,experiment,construct,replay)

FIXTURE=Path(__file__).resolve().parent/"fixtures/world_ab_original_visual_reference_v1.json"

def independent_oracle(result):
    if result["schema"]!=SCHEMA or not result["assembly"]["constructed"]:
        raise ValueError("two-contact witness not physically constructed")
    s=result["input"]
    x0,y0,vx0,vy,e=[s[k] for k in ("x","y","vx","vy","restitution")]
    t1=(WALL["x"]-HALF-x0)/vx0
    c1x=WALL["x"]-HALF
    c1y=y0+vy*t1
    v1=-e*vx0
    face=c1x+v1*PROJECTION_DURATION
    center=c1y+vy*PROJECTION_DURATION
    shape=result["assembly"]["surface"]
    if not (isclose(shape["face_x"],face,abs_tol=2e-8) and
            isclose(shape["y_min"],center-.5,abs_tol=2e-8) and
            isclose(shape["y_max"],center+.5,abs_tol=2e-8)):
        raise ValueError("construction did not follow observed rebound")
    t2=t1+((face+HALF)-c1x)/v1
    if not (t1<t2<DT*STEPS):raise ValueError("no predicted second physical contact")
    contacts=result["second_motion"]["contacts"]
    if (len(contacts)!=2 or [c["surface"] for c in contacts]!=[
        "source-wall","relation-surface-1"]):
        raise ValueError("unexpected second relation or missing actual collision")
    if not (isclose(contacts[0]["time"],t1,abs_tol=2e-8) and
            isclose(contacts[1]["time"],t2,abs_tol=2e-8) and
            isclose(contacts[1]["x"],face+HALF,abs_tol=2e-8) and
            isclose(contacts[1]["normal_impulse"],(1+e)*abs(v1),abs_tol=2e-8)):
        raise ValueError("observed event times and impulse do not agree with analytic oracle")
    v2=e*e*vx0
    for f in result["second_motion"]["frames"]:
        t=f["time"]
        if t<t1:
            x=x0+vx0*t;v=vx0
        elif t<t2:
            x=c1x+v1*(t-t1);v=v1
        else:
            x=face+HALF+v2*(t-t2);v=v2
        y=y0+vy*t
        for key,expected in (("x",x),("y",y),("vx",v),("vy",vy)):
            if not isclose(f[key],expected,abs_tol=3e-8):
                raise ValueError(f"frame {f['turn']} diverged on {key}")
    return {"first_contact_time":round(t1,9),
            "second_contact_time":round(t2,9),
            "final_x":round(face+HALF+v2*(DT*STEPS-t2),9)}

def check_original_blueprint_after(source):
    reference=json.loads(FIXTURE.read_text())
    if reference["schema"]!="world-ab-original-visual-blueprint-comparison/v1":
        raise ValueError("original drawing source changed")
    observed=source.get("second_motion") or {}
    two_contacts=observed.get("contacts",[])
    generated=[source["assembly"]["surface"]["id"]] if source["assembly"]["constructed"] else []
    # No categories from the drawing are present in the source generator:
    # a newly assembled *face* is not yet a guide/funnel/diverter/spiral.
    missing=[tag for tag in reference["generated_geometries_required"] if tag not in generated]
    return {"repeated_collisions_observed":len(two_contacts)>=2,
            "new_collision_face_emerged":bool(generated),
            "missing_original_shapes":missing,
            "full_original_blueprint_generated":not missing}

class ReboundCompositionTests(unittest.TestCase):
    def test_01_collision_builds_new_surface_and_second_collision(self):
        out=experiment()
        self.assertEqual(out["schema"],SCHEMA)
        self.assertTrue(out["assembly"]["constructed"])
        self.assertEqual(out["observed_contacts"],["source-wall","relation-surface-1"])
        self.assertTrue(out["new_surface_reused"])
        self.assertEqual(out["assembly"]["surface"]["face_x"],9.5)
        oracle=independent_oracle(out)
        self.assertEqual(oracle["final_x"],11.0)
        self.assertFalse(out["automatically_assembled_without_declared_rule"])
    def test_02_finite_restitution_and_y_variants_independent_analytic_match(self):
        for e in (0.25,0.5,0.75,1.0):
            for vy in (-0.05,0,0.12):
                with self.subTest(e=e,vy=vy):
                    out=experiment(initial(restitution=e,vy=vy))
                    self.assertTrue(out["assembly"]["constructed"])
                    self.assertTrue(out["new_surface_reused"])
                    independent_oracle(out)
    def test_03_no_source_contact_or_no_rebound_cannot_assemble(self):
        miss=experiment(initial(y=3.5,vy=0))
        self.assertFalse(miss["assembly"]["constructed"])
        self.assertIsNone(miss["second_motion"])
        still=experiment(initial(restitution=0))
        self.assertFalse(still["assembly"]["constructed"])
        self.assertEqual(still["assembly"]["reason"],"NO_OUTGOING_REBOUND")
        self.assertIsNone(still["second_motion"])
    def test_04_mutants_falsify_time_impulse_and_constructed_geometry(self):
        out=experiment()
        mutations=[
          ("second_motion","contacts",1,"time",4.0),
          ("second_motion","contacts",1,"normal_impulse",0.0),
          ("second_motion","frames",-1,"x",9.0),
          ("assembly","surface",None,"face_x",8.5),
          ("assembly","surface",None,"y_min",0.3),
        ]
        for outer,middle,index,key,value in mutations:
            d=deepcopy(out)
            node=d[outer][middle]
            if index is not None:node=node[index]
            node[key]=value
            with self.subTest(key=key,middle=middle),self.assertRaises(ValueError):
                independent_oracle(d)
    def test_05_changed_rebound_changes_derived_surface(self):
        full=experiment(initial(restitution=1))
        half=experiment(initial(restitution=.5))
        self.assertNotEqual(full["assembly"]["surface"]["face_x"],
                            half["assembly"]["surface"]["face_x"])
        self.assertNotEqual(full["second_motion"]["final"]["x"],
                            half["second_motion"]["final"]["x"])
        self.assertEqual(full["assembly"]["surface"]["source_boundary_id"],WALL["id"])
    def test_06_original_visual_blueprint_comparison_can_fail(self):
        out=experiment()
        assessed=check_original_blueprint_after(out)
        self.assertTrue(assessed["repeated_collisions_observed"])
        self.assertTrue(assessed["new_collision_face_emerged"])
        self.assertEqual(assessed["missing_original_shapes"],
                         ["guide","funnel","diverter","spiral"])
        self.assertFalse(assessed["full_original_blueprint_generated"])
        no_contact=check_original_blueprint_after(experiment(initial(y=3.5,vy=0)))
        self.assertFalse(no_contact["new_collision_face_emerged"])
        self.assertFalse(no_contact["repeated_collisions_observed"])
if __name__=="__main__":unittest.main()
