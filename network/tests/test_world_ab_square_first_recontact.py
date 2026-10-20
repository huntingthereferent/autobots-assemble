"""WORLD17 independent first-return witness and finite-segment refutations.

Separate oracle: directly rotate four square vertices and uniformly bracket
first positive-to-negative gap in fine steps, not via the generator's
analytical stationary-time partition or its geometry functions.
"""
from copy import deepcopy
from math import cos, sin, radians, hypot
import unittest

from systems.workspace.world_ab_square_first_recontact import trial,run,SCHEMA,ANGLES,HORIZON
from systems.workspace.world_ab_rotating_square_clearance import trial as source_trial16
from network.tests.test_world_ab_oblique_impact import verify_impact
from systems.workspace.world_ab_oblique_impact import HALF, WALL_CENTER, SPAN

STEP=0.000025
EXPECTED={2.5:0.00529625936,5.:0.01090371075,
          7.5:0.01704778822,10.:0.02410833063,
          12.25:0.03185108083,15.:0.04532136324}
VERTICES=((-HALF,-HALF),(-HALF,HALF),(HALF,-HALF),(HALF,HALF))


def projected_vertices(source,time):
    first=source["first_contact_center"]
    v=source["velocity_after"]
    theta=source["angular_velocity_after"]*time
    c,s=cos(theta),sin(theta)
    center=(first[0]+v[0]*time,first[1]+v[1]*time)
    return [(center[0]+c*x-s*y,center[1]+s*x+c*y)
            for x,y in VERTICES]


def finite_reading(source,time):
    normal=(-cos(radians(source["angle_degrees"])),
            -sin(radians(source["angle_degrees"])))
    tangent=(-normal[1],normal[0])
    observations=[]
    for i,v in enumerate(projected_vertices(source,time)):
        r=(v[0]-WALL_CENTER[0],v[1]-WALL_CENTER[1])
        observations.append((r[0]*normal[0]+r[1]*normal[1],
                             r[0]*tangent[0]+r[1]*tangent[1],i,v))
    return min(observations)


def independent_first_recontact(source):
    """Compute earliest recontact by an independent fine motion sweep."""
    first=finite_reading(source,0)[0]
    if abs(first)>2e-8:
        raise ValueError("original first contact shifted")
    prev=finite_reading(source,0)[0]
    for index in range(1,round(HORIZON/STEP)+1):
        now=finite_reading(source,index*STEP)[0]
        if prev>0 and now<0:
            lo=(index-1)*STEP
            hi=index*STEP
            for _ in range(65):
                mid=(lo+hi)/2
                if finite_reading(source,mid)[0]>0:lo=mid
                else:hi=mid
            time=(hi+lo)/2
            reading=finite_reading(source,time)
            return time,reading
        prev=now
    return None


def independent_check(case):
    if case["schema"]!=SCHEMA or case["source"]!="unchanged original WORLD trial04 first square impact":
        raise ValueError("changed original experiment source")
    if case["horizon"]!=HORIZON or case["source_finite_wall_preserved"] is not True:
        raise ValueError("finite source/horizon changed")
    source=case["source_original_first_contact"]
    verify_impact(source)
    if not abs(case["source_angle"]-source["angle_degrees"])<1e-9:
        raise ValueError("source angle changed")
    if case["recontact_kinematics_only"] is not True or case["numerically_bracketed_not_exact_certified"] is not True:
        raise ValueError("unverified math promoted to exact physical result")
    if case["second_impulse_or_further_motion_solved"] is not False or case["derived_receiver_built"] is not False or case["physical_sensor_evidence"] is not False:
        raise ValueError("invented later material evidence")
    event=independent_first_recontact(source)
    if event is None:
        if case["status"]!="NO_NEW_LINE_CROSSING_IN_WINDOW" or case["first_return"] is not None:
            raise ValueError("first return added without a source return")
        return True
    time,reading=event
    if case["status"]!="FIRST_RENEWED_FINITE_FACE_CONTACT_CANDIDATE" or case["first_return"] is None:
        raise ValueError("actual modeled return missing")
    claimed=case["first_return"]
    if abs(claimed["dt_after_initial_contact"]-time)>STEP:
        raise ValueError("not earliest source recontact")
    if abs(claimed["absolute_virtual_time"]-(source["first_contact_time"]+time))>STEP:
        raise ValueError("incorrect event time")
    if claimed["corner_index"]!=reading[2]:
        raise ValueError("changed source corner")
    if any(abs(p-q)>1e-6 for p,q in zip(claimed["corner_position"],reading[3])):
        raise ValueError("wrong first renewed polygon contact point")
    if abs(claimed["source_face_tangent_coordinate"]-reading[1])>1e-6:
        raise ValueError("false finite source tangent point")
    if not (-SPAN/2<reading[1]<SPAN/2):
        raise ValueError("return outside finite source")
    if abs(claimed["normal_gap_residual"])>2e-7 or abs(reading[0])>2e-7:
        raise ValueError("candidate is not on source face")
    if claimed["incoming_normal_vertex_rate"]>=0 or claimed["second_impulse_selected"] is not False:
        raise ValueError("unobserved contact response chosen")
    if not any(abs(r["time"]-time)<STEP and r["corner_index"]==reading[2]
               and r["type"]=="TRANSVERSE_SIGN_CROSSING"
               for r in case["candidate_return_roots"]):
        raise ValueError("source root receipts missing")
    return True


class SquareFirstRecontactTests(unittest.TestCase):
    def test_eight_original_source_angles_independently_reproduced(self):
        results=run()
        self.assertEqual(results["schema"],SCHEMA)
        self.assertEqual(results["angles"],list(ANGLES))
        self.assertEqual(len(results["cases"]),8)
        self.assertEqual(results["first_return_candidates"],6)
        self.assertEqual(results["no_return"],2)
        self.assertFalse(results["built_any_new_object"])
        self.assertFalse(results["actual_physical_impact_verified"])
        for case in results["cases"]:
            with self.subTest(angle=case["source_angle"]):
                self.assertTrue(independent_check(case))

    def test_six_renewed_contact_times_and_finite_features(self):
        for angle,expected in EXPECTED.items():
            with self.subTest(angle=angle):
                case=trial(angle)
                e=case["first_return"]
                self.assertIsNotNone(e)
                self.assertAlmostEqual(e["dt_after_initial_contact"],expected,delta=3e-6)
                self.assertGreater(e["incoming_normal_vertex_rate"]*-1,0)
                self.assertLess(abs(e["source_face_tangent_coordinate"]),SPAN/2)
                self.assertTrue(independent_check(case))

    def test_recontact_occurs_before_trial16_sampled_penetration(self):
        for angle in EXPECTED:
            with self.subTest(angle=angle):
                first=trial(angle)["first_return"]["dt_after_initial_contact"]
                old=source_trial16(angle)
                self.assertEqual(old["status"],"ROTATING_BODY_OVERLAPS_ORIGINAL_FACE_AT_SAMPLE")
                self.assertLess(first,old["first_detected_overlap_at"])
                self.assertGreaterEqual(old["first_detected_overlap_at"]-first,0)

    def test_vertical_and_twenty_degree_controls_stay_unresolved_not_claimed_clear(self):
        for angle in (0.,20.):
            case=trial(angle)
            self.assertIsNone(case["first_return"])
            self.assertEqual(case["status"],"NO_NEW_LINE_CROSSING_IN_WINDOW")
            self.assertTrue(independent_check(case))

    def test_forged_time_location_and_corner_are_refused(self):
        good=trial(12.25)
        for name,change in (
            ("dt_after_initial_contact",.006),
            ("absolute_virtual_time",.006),
            ("corner_index",1),
            ("corner_position",[.15,.15]),
            ("source_face_tangent_coordinate",.4),
            ("incoming_normal_vertex_rate",99),
            ("normal_gap_residual",.1),
        ):
            fake=deepcopy(good)
            if isinstance(change,list):fake["first_return"][name]=change
            else:fake["first_return"][name]+=change
            with self.subTest(field=name),self.assertRaises(ValueError):
                independent_check(fake)

    def test_original_impulse_and_next_face_claims_cannot_be_forged(self):
        base=trial(10.)
        for key,val in (("physical_sensor_evidence",True),
                        ("derived_receiver_built",True),
                        ("second_impulse_or_further_motion_solved",True),
                        ("numerically_bracketed_not_exact_certified",False)):
            changed=deepcopy(base);changed[key]=val
            with self.subTest(field=key),self.assertRaises(ValueError):
                independent_check(changed)
        for key,val in (("normal_impulse",0),
                        ("angular_velocity_after",0)):
            changed=deepcopy(base);changed["source_original_first_contact"][key]=val
            with self.subTest(field=key),self.assertRaises(ValueError):
                independent_check(changed)

    def test_refuses_invalid_source_control(self):
        for angle in (-1,21,True,"20",float("nan")):
            with self.subTest(angle=angle),self.assertRaises(ValueError):
                trial(angle)


if __name__=="__main__":
    unittest.main()
