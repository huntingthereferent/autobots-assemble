"""Independent analytical controls for the minimal A/B physical contact trial.

Tests derive outcomes from time-of-intersection geometry, not from replaying
the generator's per-step event loop. Original blueprint relation labels are
loaded only in the verifier, never in the dynamics module.
"""
from math import isclose
from copy import deepcopy
from pathlib import Path
import json
import unittest

from systems.workspace.world_ab_contact_trial import WALL,HALF,DT,STEPS,initial,trial,integrate

REFERENCE=Path(__file__).resolve().parent/"fixtures/world_ab_original_visual_reference_v1.json"

def analytic(s,wall,t):
    x,y,vx,vy,e=[s[n] for n in ("x","y","vx","vy","restitution")]
    hit=(WALL["x"]-HALF-x)/vx
    in_span=WALL["y"]-HALF<=y+vy*hit<=WALL["y"]+1+HALF
    collided=wall and 0<=hit<=DT*STEPS and in_span
    if collided and t>=hit:
        return WALL["x"]-HALF-e*vx*(t-hit),y+vy*t,-e*vx,vy
    return x+vx*t,y+vy*t,vx,vy

def independently_compare(t):
    s=t["initial"]
    for branch,wall in (("A_without_wall",False),("B_with_wall",True)):
        observed=t[branch]
        for frame in observed["frames"]:
            ref=analytic(s,wall,frame["time"])
            for label,value in zip(("x","y","vx","vy"),ref):
                if not isclose(frame[label],value,rel_tol=0,abs_tol=2e-8):
                    raise ValueError("stepwise simulation disagrees with independent continuous analytic trajectory")
    hit=(WALL["x"]-HALF-s["x"])/s["vx"]
    in_span=WALL["y"]-HALF<=s["y"]+s["vy"]*hit<=WALL["y"]+1+HALF
    expected=1 if 0<=hit<=DT*STEPS and in_span else 0
    if len(t["B_with_wall"]["contacts"])!=expected:
        raise ValueError("actual wall contact disagrees with original geometry")
    if t["A_without_wall"]["contacts"]:
        raise ValueError("control A cannot contact an absent wall")
    if expected:
        c=t["B_with_wall"]["contacts"][0]
        if not (isclose(c["time"],hit,abs_tol=2e-8) and
            isclose(c["normal_impulse"],(1+s["restitution"])*s["vx"],abs_tol=2e-8) and
            isclose(c["energy_before"]-c["energy_after"],
                0.5*s["vx"]**2*(1-s["restitution"]**2),abs_tol=2e-8)):
            raise ValueError("impulse or energy contradicts declared simple restitution model")
    return expected

def contrast(t):
    target=json.loads(REFERENCE.read_text())
    if target["schema"]!="world-ab-original-visual-blueprint-comparison/v1":
        raise ValueError("comparison reference changed")
    b=set(t["B_with_wall"]["relations"])
    supported={k:(v in b) for k,v in target["relation_checks"].items()}
    # Dynamics emits motion traces only: no *constructed structures*. A
    # preplaced object in the larger WORLD is not a generated physical artifact.
    built=set(t.get("generated_geometries",[]))
    missing=[s for s in target["generated_geometries_required"] if s not in built]
    return {"relation_matches":supported,"generated_structures_missing":missing,
        "all_required_physical_blueprint_structures_emerged":not missing,
        "exact_Earth_material_behavior_verified":False}

class ABPhysicalContactTests(unittest.TestCase):
    def test_01_source_wall_geometry_produces_real_block_deflection(self):
        out=trial(initial())
        self.assertEqual(out["physical_world_dimensions"],[24,6])
        self.assertEqual(out["source_boundary"]["face_x"],12)
        self.assertEqual(independently_compare(out),1)
        self.assertEqual(len(out["B_with_wall"]["contacts"]),1)
        self.assertEqual(out["A_without_wall"]["final"]["x"],15)
        self.assertEqual(out["B_with_wall"]["final"]["x"],8.5)
        self.assertIn("movement-redirected",out["B_with_wall"]["relations"])
        self.assertNotIn("movement-redirected",out["A_without_wall"]["relations"])
    def test_02_no_collision_for_block_that_misses_source_wall(self):
        out=trial(initial(y=3.5,vy=0))
        self.assertEqual(independently_compare(out),0)
        self.assertEqual(out["B_with_wall"]["final"],out["A_without_wall"]["final"])
        self.assertFalse(out["B_with_wall"]["contacts"])
        self.assertIn("passed-boundary-coordinate",out["B_with_wall"]["relations"])
    def test_03_restitution_controls_real_energy_movement(self):
        for e in (0.0,0.3,0.6,1.0):
            with self.subTest(e=e):
                out=trial(initial(restitution=e))
                self.assertEqual(independently_compare(out),1)
                c=out["B_with_wall"]["contacts"][0]
                self.assertLessEqual(c["energy_after"],c["energy_before"]+1e-8)
                self.assertAlmostEqual(c["outgoing_velocity"][0],-e*3,places=8)
    def test_04_two_distinct_angles_and_no_preset_result(self):
        for vy in (-0.05,0.0,0.06,0.16):
            with self.subTest(vy=vy):
                out=trial(initial(y=1.35,vy=vy))
                self.assertEqual(independently_compare(out),1)
                self.assertEqual(out["A_without_wall"]["contacts"],[])
                self.assertFalse(out["source_blueprint_structure_generated"])
    def test_05_refuse_unsupported_virtual_scale_or_nan(self):
        for args in ({"x":float("nan")},{"vx":-1},{"x":11.9},
                     {"y":-0.1},{"restitution":1.5},{"vy":float("inf")},
                     {"vx":True}):
            with self.subTest(args=args),self.assertRaises(ValueError):initial(**args)
    def test_06_target_comparison_is_separate_and_can_fail(self):
        out=trial(initial())
        result=contrast(out)
        self.assertTrue(all(result["relation_matches"].values()))
        self.assertEqual(result["generated_structures_missing"],
                         ["guide","funnel","diverter","spiral"])
        self.assertFalse(result["all_required_physical_blueprint_structures_emerged"])
        self.assertFalse(result["exact_Earth_material_behavior_verified"])
        untouched=trial(initial(y=3.5,vy=0))
        different=contrast(untouched)
        self.assertFalse(different["relation_matches"]["boundary_contact"])
        self.assertFalse(different["relation_matches"]["motion_redirected"])
    def test_07_independent_oracle_detects_fabricated_physics(self):
        out=trial(initial())
        mutated=deepcopy(out)
        mutated["B_with_wall"]["frames"][-1]["x"]+=1.0
        with self.assertRaises(ValueError):independently_compare(mutated)
        mutated=deepcopy(out);mutated["B_with_wall"]["contacts"][0]["normal_impulse"]=0.0
        with self.assertRaises(ValueError):independently_compare(mutated)
if __name__=="__main__":unittest.main()
