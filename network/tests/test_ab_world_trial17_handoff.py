"""Trial17 negative controls: rooted contact location cannot invent second impact."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial17_handoff import carry, ANGLES, RETURN, NONE
from work.ab_world.verify_construction import verify_receipt

PIN = "02b2f6ca97717eb3bf959d120a2c32a6ae856543"


def sample():
    cases = []
    for angle in ANGLES:
        candidate = angle not in (0.,20.)
        dt = round(.005 + angle*.001, 12)
        impact = {
            "hit": True, "angle_degrees": angle,
            "first_contact_time": 1.25,
            "candidate_receiver": {"surface_built": False},
        }
        root = {"time": dt, "corner_index": 2,
                "type": "TRANSVERSE_SIGN_CROSSING"}
        first = {
            "dt_after_initial_contact": dt,
            "absolute_virtual_time": round(1.25 + dt, 12),
            "corner_index": 2,
            "corner_position": [12.,1.55],
            "source_face_tangent_coordinate": .05,
            "normal_gap_residual": 0.,
            "incoming_normal_vertex_rate": -.15,
            "contact_feature": "square-vertex / original finite face interior",
            "second_impulse_selected": False,
        } if candidate else None
        cases.append({
            "schema": "world-ab-rotating-square-first-finite-recontact/v1",
            "source": "unchanged original WORLD trial04 first square impact",
            "source_angle": angle,
            "source_original_first_contact": impact,
            "horizon": .06,
            "status": RETURN if candidate else NONE,
            "first_return": first,
            "candidate_return_roots": [root] if candidate else [],
            "monotonic_segments_checked": 8,
            "method": "analytical corner gap stationary partitions plus numerical bisection",
            "source_finite_wall_preserved": True,
            "recontact_kinematics_only": True,
            "numerically_bracketed_not_exact_certified": True,
            "second_impulse_or_further_motion_solved": False,
            "derived_receiver_built": False,
            "physical_sensor_evidence": False,
        })
    return {
        "schema": "world-ab-rotating-square-first-finite-recontact/v1",
        "angles": list(ANGLES), "horizon": .06, "cases": cases,
        "first_return_candidates": 6, "no_return": 2,
        "built_any_new_object": False, "actual_physical_impact_verified": False,
    }


class Trial17FirstReturnHandoffTests(unittest.TestCase):
    def test_01_six_source_candidates_two_unresolved_controls(self):
        native=sample()
        copy=deepcopy(native)
        record=carry(native,PIN)
        self.assertEqual(native,copy)
        self.assertEqual(record["first_return_candidates"],6)
        self.assertEqual(record["no_return"],2)
        self.assertEqual(record["source_root_records"],6)
        self.assertEqual(record["modeled_second_impulses_selected"],0)
        self.assertEqual(record["derived_receivers_built"],0)
        self.assertFalse(record["continuation_after_return_verified"])
        self.assertEqual(record["ledger_witness"]["pages_verified"],8)
        self.assertEqual(record["ledger_witness"]["steps_verified"],52)
        self.assertEqual(record["ledger_witness"]["observations_recorded"],16)
        for case in record["ledgers"]:
            self.assertTrue(verify_receipt(case["receipt"])["valid"])
            self.assertNotIn("movement-derived-receiver",case["receipt"]["final"]["objects"])
            self.assertIsNone(case["receipt"]["final"]["objects"][
                "bounded-first-return-investigation"]["second_impulse"])
        self.assertNotIn("located-corner-return",
                         record["ledgers"][0]["receipt"]["final"]["objects"])

    def test_02_return_object_can_only_follow_source_root_witness(self):
        operations=[event["operation"] for event in
                    carry(sample(),PIN)["ledgers"][1]["receipt"]["events"]]
        first=next(i for i,x in enumerate(operations)
                   if x["op"]=="observe" and x["id"]=="first-return-source-candidate")
        created=next(i for i,x in enumerate(operations)
                     if x["op"]=="introduce" and x["id"]=="located-corner-return")
        self.assertEqual(created,first+1)
        self.assertEqual(operations[-1]["label"] if "label" in operations[-1]
                         else operations[-1]["op"],"connect")

    def test_03_no_return_case_not_silently_given_a_contact(self):
        v=sample()
        v["cases"][0]["first_return"]={"dt_after_initial_contact":.01}
        with self.assertRaisesRegex(ValueError,"promoted to solved event"):
            carry(v,PIN)
        v=sample()
        v["cases"][7]["candidate_return_roots"]=[{
            "time":.02,"corner_index":1,"type":"TRANSVERSE_SIGN_CROSSING"}]
        with self.assertRaisesRegex(ValueError,"promoted to solved event"):
            carry(v,PIN)

    def test_04_wrong_time_finite_face_or_root_is_rejected(self):
        for field,value in (
            ("dt_after_initial_contact",-.01),
            ("corner_index",3),
            ("source_face_tangent_coordinate",1.),
            ("incoming_normal_vertex_rate",.3),
            ("second_impulse_selected",True),
        ):
            v=sample()
            v["cases"][1]["first_return"][field]=value
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError,"finite-face return"):
                carry(v,PIN)
        v=sample()
        v["cases"][1]["candidate_return_roots"][0]["time"]=.04
        with self.assertRaisesRegex(ValueError,"finite-face return"):
            carry(v,PIN)

    def test_05_no_unsupported_second_physics_or_forged_source(self):
        for field in (
            "derived_receiver_built","second_impulse_or_further_motion_solved",
            "physical_sensor_evidence",
        ):
            v=sample()
            v["cases"][1][field]=True
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError,"unwitnessed material"):
                carry(v,PIN)
        v=sample()
        v["built_any_new_object"]=True
        with self.assertRaisesRegex(ValueError,"physical claim"):
            carry(v,PIN)
        v=sample()
        v["cases"][1]["source_original_first_contact"]["candidate_receiver"]["surface_built"]=True
        with self.assertRaisesRegex(ValueError,"not-yet-built receiver"):
            carry(v,PIN)
        with self.assertRaisesRegex(ValueError,"exact original source"):
            carry(sample(),"unversioned-original")

    def test_06_independent_replay_rejects_promoted_contact(self):
        receipt=carry(sample(),PIN)["ledgers"][1]["receipt"]
        changed=deepcopy(receipt)
        changed["final"]["objects"]["located-corner-return"]["candidate_only"]=False
        with self.assertRaises(ValueError):
            verify_receipt(changed)
        changed=deepcopy(receipt)
        changed["events"][-1]["effect"]={"status":"contact-response-solved"}
        with self.assertRaises(ValueError):
            verify_receipt(changed)


if __name__=="__main__":
    unittest.main()
