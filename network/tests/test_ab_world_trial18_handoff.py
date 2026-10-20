"""WORLD18 candidate impulse controls, no physical postreturn motion selected."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial18_handoff import ANGLES, carry
from work.ab_world.verify_construction import verify_receipt

PIN = "8f9600adcee76f830ac7eb769603e615f14179c9"


def sample():
    cases=[]
    for angle in ANGLES:
        good=angle not in (0.,20.)
        dt=round(.005+.001*angle,12)
        first_return={
            "dt_after_initial_contact":dt,"absolute_virtual_time":1.25+dt,
            "corner_index":2,"corner_position":[12.,1.5],
            "second_impulse_selected":False,
        } if good else None
        impulse={
            "normal_impulse":1.2,
            "incoming_vertex_normal_rate":-1.,
            "outgoing_vertex_normal_rate":1.,
            "contact_vertex_index":2,
            "contact_time_relative":dt,
            "contact_point":[12.,1.5],
            "velocity_before":[-2.,0.],
            "velocity_after":[2.,0.],
            "angular_velocity_after":3.,
            "kinetic_energy_before":2.,
            "kinetic_energy_after":2.,
            "constitutive_hypothesis":
                "single frictionless normal, e=1, rotating rigid square",
            "selected_as_actual_material_response":False,
        } if good else None
        frames=[{
            "dt_after_candidate":round(j*.0005,10),
            "center":[12.+.01*j,1.5],
            "orientation":j*.001,
            "minimum_sampled_signed_face_gap":.01,
            "worst_finite_face_corner":0,
            "worst_finite_face_tangent":.02
        } for j in range(33)] if good else []
        cases.append({
            "schema":"world-ab-local-corner-recontact-impulse/v1",
            "source_trial17":"world-ab-rotating-square-first-finite-recontact/v1",
            "source_original_trial04":"world-ab-oblique-normal-angular-impact/v1",
            "angle":angle,
            "source_first_contact":{
                "hit":True,"angle_degrees":angle,
                "candidate_receiver":{"surface_built":False}},
            "source_trial17_first_return":first_return,
            "local_time_horizon":.016,"observation_step":.0005,
            "second_impulse_is_a_model_hypothesis":True,
            "physical_second_impact_observed":False,
            "receiver_constructed":False,
            "continuous_clearance_certified":False,
            "further_impacts_solved":False,
            "status": "NO_OVERLAP_DETECTED_IN_LOCAL_SAMPLES" if good else
                      "NO_ADMITTED_RENEWED_CONTACT",
            "candidate_impulse":impulse,
            "post_contact_samples":frames,
            **({"first_sampled_post_contact_overlap":None,
                "next_movement_admitted_as_verified":False} if good else {}),
        })
    return {
        "schema":"world-ab-local-corner-recontact-impulse/v1",
        "angles":list(ANGLES),"cases":cases,
        "cases_with_candidate_impulse":6,
        "cases_without_recontact":2,
        "cases_with_sampled_post_overlap":0,
        "material_contact_response_proven":False,
        "created_any_new_receiver":False,
        "general_rotating_contact_solver":False,
    }


class Trial18ImpulseCarrierTests(unittest.TestCase):
    def test_01_retains_all_conditional_impulses_without_completed_dynamics(self):
        source=sample()
        copy=deepcopy(source)
        carried=carry(source,PIN)
        self.assertEqual(source,copy)
        self.assertEqual(carried["candidate_second_impulses"],6)
        self.assertEqual(carried["absent_first_returns"],2)
        self.assertEqual(carried["hypothetical_postreturn_samples"],198)
        self.assertEqual(carried["ledger_witness"]["pages_verified"],8)
        self.assertEqual(carried["ledger_witness"]["steps_verified"],446)
        self.assertEqual(carried["ledger_witness"]["observations_recorded"],212)
        self.assertTrue(carried["ledger_witness"]["valid"])
        self.assertEqual(carried["receivers_constructed"],0)
        self.assertFalse(carried["valid_sustained_postcontact_motion_proven"])
        for page in carried["ledger_pages"]:
            self.assertTrue(verify_receipt(page["receipt"])["valid"])
            self.assertNotIn("movement-derived-receiver",
                             page["receipt"]["final"]["objects"])
        self.assertNotIn("candidate-postreturn-sampling",
                         carried["ledger_pages"][0]["receipt"]["final"]["objects"])

    def test_02_candidate_only_introduced_after_attributed_impulse(self):
        operations=[e["operation"] for e in
                    carry(sample(),PIN)["ledger_pages"][1]["receipt"]["events"]]
        before=next(i for i,step in enumerate(operations)
                    if step["op"]=="observe" and
                    step["id"]=="source-hypothetical-local-impulse")
        created=next(i for i,step in enumerate(operations)
                     if step["op"]=="introduce" and
                     step["id"]=="candidate-postreturn-sampling")
        self.assertEqual(created,before+1)

    def test_03_missing_source_first_return_does_not_generate_an_impulse(self):
        data=sample()
        data["cases"][0]["candidate_impulse"]={"normal_impulse":2.}
        with self.assertRaisesRegex(ValueError,"promoted to an impulse"):
            carry(data,PIN)
        data=sample()
        data["cases"][0]["post_contact_samples"]=[{"dt_after_candidate":0.}]
        with self.assertRaisesRegex(ValueError,"promoted to an impulse"):
            carry(data,PIN)

    def test_04_forged_material_witness_rejected(self):
        for field in ("physical_second_impact_observed","receiver_constructed",
                      "continuous_clearance_certified","further_impacts_solved"):
            data=sample()
            data["cases"][1][field]=True
            with self.subTest(field=field),self.assertRaisesRegex(
                    ValueError,"material physics"):
                carry(data,PIN)
        data=sample()
        data["cases"][1]["next_movement_admitted_as_verified"]=True
        with self.assertRaisesRegex(ValueError,"observed dynamics"):
            carry(data,PIN)
        data=sample()
        data["cases"][1]["candidate_impulse"]["selected_as_actual_material_response"]=True
        with self.assertRaisesRegex(ValueError,"observed dynamics"):
            carry(data,PIN)

    def test_05_sampled_geometry_and_energy_are_bounded(self):
        data=sample()
        data["cases"][1]["candidate_impulse"]["kinetic_energy_after"]=10.
        with self.assertRaisesRegex(ValueError,"energy"):
            carry(data,PIN)
        data=sample()
        data["cases"][1]["post_contact_samples"][2]["dt_after_candidate"]=.005
        with self.assertRaisesRegex(ValueError,"sample time"):
            carry(data,PIN)
        data=sample()
        data["cases"][1]["post_contact_samples"].pop()
        with self.assertRaisesRegex(ValueError,"33-sample"):
            carry(data,PIN)
        data=sample()
        data["cases"][1]["candidate_impulse"]["contact_vertex_index"]=1
        with self.assertRaisesRegex(ValueError,"source geometry"):
            carry(data,PIN)

    def test_06_independent_replay_detects_fake_second_impulse(self):
        record=carry(sample(),PIN)["ledger_pages"][1]["receipt"]
        mutated=deepcopy(record)
        mutated["final"]["objects"]["candidate-postreturn-sampling"]["admitted_continuation"]=True
        with self.assertRaises(ValueError):
            verify_receipt(mutated)
        mutated=deepcopy(record)
        mutated["events"][-1]["effect"]={"status":"real-second-impact"}
        with self.assertRaises(ValueError):
            verify_receipt(mutated)
        with self.assertRaisesRegex(ValueError,"exact immutable"):
            carry(sample(),"unversioned")


if __name__=="__main__":
    unittest.main()
