"""Independent witness for WORLD16 finite source/rotating vertex clearance.

Recomputes the angular projection from the original first-contact record
without calling the generator's sample or rotating_corners functions.
"""
from copy import deepcopy
from math import cos,sin,radians,isclose,isfinite
import unittest

from systems.workspace.world_ab_rotating_square_clearance import (
    run,trial,SCHEMA,HORIZON,OBSERVATION_STEP
)
from network.tests.test_world_ab_oblique_impact import verify_impact
from systems.workspace.world_ab_oblique_impact import HALF,SPAN,WALL_CENTER


def verify(case):
    if case["schema"]!=SCHEMA or case["physical_observation"] is not False:
        raise ValueError("invalid source model/physical origin")
    original=case["first_contact"]
    if not verify_impact(original):
        raise ValueError("unverified original square impact")
    if not original["hit"]:
        if case["status"]!="NO_ADMITTED_FIRST_CONTACT" or case["samples"] or case["next_receiver_built"]:
            raise ValueError("invented no-contact movement")
        return True
    if not isclose(case["angle"],original["angle_degrees"],abs_tol=1e-9):
        raise ValueError("changed source angle")
    if len(case["samples"])!=61 or case["observation_horizon"]!=HORIZON or case["observation_step"]!=OBSERVATION_STEP:
        raise ValueError("missing fixed interval observation")
    if case["next_receiver_built"] is not False or case["second_contact_computed"] is not False:
        raise ValueError("unwitnessed construction or contact")
    if case["next_receiver_candidate_only"]!=original["candidate_receiver"]:
        raise ValueError("candidate mislabeled or substituted")
    if (case["no_overlap_between_samples_proven"] is not False or
        case["continuous_clearance_verified"] is not False or
        case["world_15_fixed_square_source_preserved"] is not True):
        raise ValueError("unverified continuous motion promoted")

    n=(-cos(radians(case["angle"])),-sin(radians(case["angle"])))
    tangent=(-n[1],n[0])
    if any(abs(original["normal"][i]-n[i])>2e-8 for i in range(2)):
        raise ValueError("source normal differs from independently recomputed angle")
    pos=original["first_contact_center"]
    speed=original["velocity_after"]
    angular=original["angular_velocity_after"]
    first_invalid=None
    for index,item in enumerate(case["samples"]):
        dt=index*OBSERVATION_STEP
        center=(pos[0]+speed[0]*dt,pos[1]+speed[1]*dt)
        rotation=angular*dt
        cc=cos(rotation);ss=sin(rotation)
        inside=[]
        for vertex_index,(x,y) in enumerate(((-HALF,-HALF),(-HALF,HALF),
                                              (HALF,-HALF),(HALF,HALF))):
            # Orthogonal rotation of the actual original square vertices.
            v=(center[0]+cc*x-ss*y,center[1]+ss*x+cc*y)
            vec=(v[0]-WALL_CENTER[0],v[1]-WALL_CENTER[1])
            along=vec[0]*tangent[0]+vec[1]*tangent[1]
            if abs(along)<=SPAN/2+1e-8:
                clearance=vec[0]*n[0]+vec[1]*n[1]
                inside.append((clearance,vertex_index,along))
        worst=min(inside) if inside else None
        overlap=bool(worst and worst[0]<-1e-8)
        if overlap and first_invalid is None:
            first_invalid=round(dt,10)
        if abs(item["dt"]-dt)>1e-9 or any(abs(item["center"][i]-center[i])>2e-8 for i in (0,1)):
            raise ValueError("fabricated motion time or center")
        if abs(item["orientation"]-rotation)>2e-8 or item["checked_corners"]!=len(inside):
            raise ValueError("rotating geometry or sampled corner count differs")
        if item["finite_interior_overlap"] != overlap:
            raise ValueError("incorrect sampled finite wall overlap")
        if worst is None:
            if item["minimum_signed_clearance"] is not None or item["worst_corner_index"] is not None:
                raise ValueError("fabricated supported finite projection")
        elif (abs(item["minimum_signed_clearance"]-worst[0])>2e-8 or
              item["worst_corner_index"]!=worst[1]):
            raise ValueError("minimum finite source clearance or vertex forged")

    expected_status=("ROTATING_BODY_OVERLAPS_ORIGINAL_FACE_AT_SAMPLE"
                     if first_invalid is not None else "NO_OVERLAP_DETECTED_IN_SHORT_SAMPLED_WINDOW")
    if case["status"]!=expected_status or case["first_detected_overlap_at"]!=first_invalid:
        raise ValueError("false continuation status / first overlap time")
    if case["unmodeled_recontact_response_refused"] != (first_invalid is not None):
        raise ValueError("unmodeled contact incorrectly continued")
    return True


class WorldRotatingSquareClearanceTests(unittest.TestCase):
    def test_short_window_all_eight_are_independently_replayed(self):
        result=run()
        self.assertEqual(result["schema"],SCHEMA)
        self.assertFalse(result["physical_world_verified"])
        self.assertFalse(result["continuous_rotating_polygon_solver_present"])
        self.assertFalse(result["new_world_or_renderer"])
        self.assertEqual(len(result["cases"]),8)
        for case in result["cases"]:
            with self.subTest(angle=case["angle"]):
                self.assertTrue(verify(case))

    def test_actual_early_rotating_overlap_is_not_a_second_collision_solution(self):
        for angle in (2.5,5.,7.5,10.,12.25,15.):
            with self.subTest(angle=angle):
                record=trial(angle)
                self.assertEqual(record["status"],
                                 "ROTATING_BODY_OVERLAPS_ORIGINAL_FACE_AT_SAMPLE")
                self.assertIsNotNone(record["first_detected_overlap_at"])
                self.assertFalse(record["next_receiver_built"])
                self.assertTrue(record["unmodeled_recontact_response_refused"])
                self.assertTrue(verify(record))

    def test_no_detected_overlap_is_not_continuous_clearance_proof(self):
        for angle in (0.,20.):
            with self.subTest(angle=angle):
                record=trial(angle)
                self.assertEqual(record["status"],"NO_OVERLAP_DETECTED_IN_SHORT_SAMPLED_WINDOW")
                self.assertFalse(record["continuous_clearance_verified"])
                self.assertFalse(record["next_receiver_built"])
                self.assertTrue(verify(record))

    def test_source_contact_still_original_04_impact_not_trial15_reflection(self):
        for angle in (0.,5.,10.,15.,20.):
            c=trial(angle)
            self.assertTrue(verify_impact(c["first_contact"]))
            self.assertFalse(c["first_contact"]["after_look"]["continuous_contact_retested"])
            self.assertEqual(c["first_contact"]["candidate_receiver"]["surface_built"],False)

    def test_forged_rotation_or_clearance_is_caught(self):
        base=trial(10.)
        for field,value in (("orientation",0.),
                            ("minimum_signed_clearance",.999),
                            ("finite_interior_overlap",False),
                            ("checked_corners",0),
                            ("worst_corner_index",99),
                            ("center",[0.,0.]),
                            ("dt",.051)):
            fake=deepcopy(base)
            fake["samples"][50][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):
                verify(fake)

    def test_forged_original_first_impulse_or_promoted_second_face_is_caught(self):
        for field,val in (("angular_velocity_after",0.),
                          ("normal_impulse",0.)):
            fake=deepcopy(trial(20.))
            fake["first_contact"][field]=val
            with self.subTest(field=field),self.assertRaises(ValueError):
                verify(fake)
        for field,val in (("next_receiver_built",True),
                          ("second_contact_computed",True),
                          ("physical_observation",True),
                          ("continuous_clearance_verified",True)):
            fake=deepcopy(trial(10.));fake[field]=val
            with self.subTest(field=field),self.assertRaises(ValueError):verify(fake)

    def test_invalid_source_angles_refuse(self):
        for a in (-1,21,float("nan"),"5",True):
            with self.subTest(angle=a),self.assertRaises(ValueError):
                trial(a)


if __name__=="__main__":
    unittest.main()
