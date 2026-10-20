"""A/B WORLD16 source sample controls reject invented square continuation."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial16_handoff import ANGLES, carry
from work.ab_world.verify_construction import verify_receipt

PIN="6d22286b1fd129ae4011d1abb55dd4c320d58a5a"


def sample():
    records=[]
    for angle in ANGLES:
        overlap = angle not in (0.,20.)
        first = .01 if overlap else None
        samples=[]
        for i in range(61):
            t=round(i*.001,10)
            samples.append({
                "dt":t,"center":[10.+t,1.5],"orientation":t*2,
                "minimum_signed_clearance":-.0001 if overlap and i==10 else 0.01,
                "finite_interior_overlap":overlap and i==10,
                "checked_corners":4,"worst_corner_index":0})
        source_impact={"hit":True,"candidate_receiver":{"surface_built":False},
                       "after_look":{"continuous_contact_retested":False}}
        records.append({
            "schema":"world-ab-rotating-square-clearance-check/v1",
            "angle":angle,
            "status":("ROTATING_BODY_OVERLAPS_ORIGINAL_FACE_AT_SAMPLE" if overlap
                      else "NO_OVERLAP_DETECTED_IN_SHORT_SAMPLED_WINDOW"),
            "source_model":"unchanged original WORLD trial 04 rigid-square single impact",
            "first_contact":source_impact,
            "samples":samples,"observation_step":.001,"observation_horizon":.06,
            "first_detected_overlap_at":first,
            "next_receiver_candidate_only":source_impact["candidate_receiver"],
            "next_receiver_built":False,"second_contact_computed":False,
            "unmodeled_recontact_response_refused":overlap,
            "no_overlap_between_samples_proven":False,
            "continuous_clearance_verified":False,
            "physical_observation":False,
            "world_15_fixed_square_source_preserved":True})
    return {"schema":"world-ab-rotating-square-clearance-check/v1",
            "angles":list(ANGLES),"cases":records,
            "counts":{"sampled-overlap":6,"sampled-no-overlap":2},
            "physical_world_verified":False,
            "continuous_rotating_polygon_solver_present":False,
            "new_world_or_renderer":False}


class SampledRotatingSquareHandoffTests(unittest.TestCase):
    def test_01_eight_bounded_worlds_keep_all_488_unvalidated_samples(self):
        original=sample()
        copied=deepcopy(original)
        out=carry(original,PIN)
        self.assertEqual(original,copied)
        self.assertEqual(out["cases"],8)
        self.assertEqual(out["proposed_samples"],488)
        self.assertEqual(out["sampled_overlap_cases"],6)
        self.assertEqual(out["no_sampled_overlap_cases"],2)
        self.assertEqual(out["ledger_witness"]["pages_verified"],8)
        self.assertEqual(out["ledger_witness"]["observations_recorded"],496)
        self.assertEqual(out["ledger_witness"]["steps_verified"],1008)
        self.assertFalse(out["receiver_built"])
        self.assertFalse(out["continuous_clearance_proven"])
        self.assertFalse(out["second_contact_response_solved"])
        self.assertTrue(all(verify_receipt(p["receipt"])["valid"] for p in out["ledger_pages"]))
        for page in out["ledger_pages"]:
            self.assertNotIn("movement-derived-receiver",
                             page["receipt"]["final"]["objects"])
            self.assertFalse(page["receipt"]["final"]["objects"]
                             ["projected-rotating-square"]["admitted_continuation"])

    def test_02_after_overlap_remains_counterfactual_not_completed_path(self):
        first_overlap=carry(sample(),PIN)["ledger_pages"][1]["receipt"]
        obs=first_overlap["final"]["observations"]
        first=obs["source-projected-sample-10"]["reading"]
        after=obs["source-projected-sample-11"]["reading"]
        self.assertEqual(first["proposed_state"],"first-detected-overlap")
        self.assertEqual(after["proposed_state"],"post-sampled-overlap-counterfactual")
        self.assertFalse(after["valid_continued_dynamics"])
        self.assertFalse(after["material_sample_measured"])

    def test_03_invented_receiver_or_continuous_solver_is_rejected(self):
        data=sample()
        data["cases"][0]["next_receiver_built"]=True
        with self.assertRaisesRegex(ValueError,"promoted"):
            carry(data,PIN)
        data=sample()
        data["cases"][1]["second_contact_computed"]=True
        with self.assertRaisesRegex(ValueError,"promoted"):
            carry(data,PIN)
        data=sample()
        data["continuous_rotating_polygon_solver_present"]=True
        with self.assertRaisesRegex(ValueError,"scope changed"):
            carry(data,PIN)
        data=sample()
        data["cases"][7]["continuous_clearance_verified"]=True
        with self.assertRaisesRegex(ValueError,"promoted"):
            carry(data,PIN)

    def test_04_sampled_overlap_mutants_falsify_source_witness(self):
        data=sample()
        data["cases"][1]["samples"][10]["finite_interior_overlap"]=False
        with self.assertRaisesRegex(ValueError,"overlap/refusal"):
            carry(data,PIN)
        data=sample()
        data["cases"][1]["first_detected_overlap_at"]=.02
        with self.assertRaisesRegex(ValueError,"overlap/refusal"):
            carry(data,PIN)
        data=sample()
        data["counts"]["sampled-overlap"]=0
        with self.assertRaisesRegex(ValueError,"counts changed"):
            carry(data,PIN)

    def test_05_angle_order_and_finite_samples_cannot_drift(self):
        data=sample()
        data["cases"][3]["samples"].pop()
        with self.assertRaisesRegex(ValueError,"61 predeclared"):
            carry(data,PIN)
        data=sample()
        data["cases"][0]["samples"][3]["dt"]=.002
        with self.assertRaisesRegex(ValueError,"time"):
            carry(data,PIN)
        data=sample()
        data["cases"][0]["angle"]=99.
        with self.assertRaisesRegex(ValueError,"angle/source"):
            carry(data,PIN)
        with self.assertRaisesRegex(ValueError,"exact source SHA"):
            carry(sample(),"moving-original-branch")

    def test_06_independent_receipt_detects_claimed_physical_continuation(self):
        receipt=carry(sample(),PIN)["ledger_pages"][1]["receipt"]
        bad=deepcopy(receipt)
        bad["final"]["objects"]["projected-rotating-square"]["admitted_continuation"]=True
        with self.assertRaises(ValueError):
            verify_receipt(bad)
        bad=deepcopy(receipt)
        bad["events"][-1]["effect"]={"status":"real-collision-resolved"}
        with self.assertRaises(ValueError):
            verify_receipt(bad)


if __name__=="__main__":
    unittest.main()
