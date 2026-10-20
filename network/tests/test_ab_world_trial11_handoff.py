"""Trial11 A/B ledger negative tests: hypothetical bins are not measurements."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial11_handoff import (
    ANGLES, ROTATIONS, TIMES, QUANTA, carry)
from work.ab_world.verify_construction import verify_receipt

PIN = "ec2522164c2dc85f906d211fc780061171fd5e71"


def example():
    cases = []
    for i, (rotation, angle) in enumerate(
            (d, a) for d in ROTATIONS for a in ANGLES):
        live = 2 if i < 26 else 1
        audits = []
        for j in range(live):
            audits.append({
                "active_indices": [j], "source_ids": ["source-face-" + str(j)],
                "outgoing_velocity": [2., float(j)],
                "necessary_mu_point_four_cone": True,
                "tangent_impulses_under_original_mu_zero_model": [0.],
                "mu_point_four_normal_cone_bounds": [1.],
                "hypothesis_both_touching_normals_restitute": False,
                "has_actual_outgoing_motion_measurement": False,
            })
        sensors = []
        for time in TIMES:
            for quantum in QUANTA:
                parts = [
                    {"bin_xy": [1 + j, 2 + j],
                     "possible_active_sets": [[j]]} for j in range(live)
                ]
                sensors.append({
                    "virtual_time": time,
                    "position_quantum": quantum,
                    "hypothetical_reading_partitions": parts,
                    "distinguishable_bins": len(parts),
                    "would_uniquely_discriminate_if_a_matching_reading_were_observed": True,
                    "measured_reading": None,
                })
        cases.append({
            "original_index": i,
            "incoming_angle_degrees": angle,
            "surface_B_rotation_degrees": rotation,
            "geometry_kind": ("original-source-geometry"
                              if rotation == 0 else "controlled-geometry-not-original"),
            "source_trial10_classification": ("multiple-admissible"
                                               if live == 2 else "single-admissible"),
            "original_admissible_count": live,
            "candidates": audits, "sensors": sensors,
            "necessary_friction_cone_retained_count": live,
            "additional_all_normals_restitution_retained_count": 0,
            "first_hypothetical_discriminating_sensor":
                {"virtual_time": TIMES[0], "position_quantum": QUANTA[0]}
                if live > 1 else None,
            "actual_source_sensor_reading_available": False,
            "physical_outcome_selected": False,
        })
    return {
        "schema": "world-ab-contact-discrimination-hypotheses/v1",
        "source_trial10_schema": "world-ab-two-contact-active-set-enumeration/v1",
        "source_trial09_schema": "world-ab-two-contact-incidence-stress/v1",
        "original_source_geometry": {"surfaces": [{"id": "A"}, {"id": "B"}]},
        "source_trial10_counts": {
            "multiple-admissible": 26, "single-admissible": 9,
            "no-local-candidate": 0,
        },
        "source_trial09_two_active_counts": {"accepted-local-candidate": 1},
        "sensor_times": list(TIMES), "sensor_position_quanta": list(QUANTA),
        "friction_coefficient_hypothesis": .4,
        "cases": cases,
        "counts": {
            "ambiguous_cases": 26,
            "friction_cone_only_narrowed_cases": 0,
            "all_normals_rest_narrowed_cases": 35,
            "all_normals_rest_eliminated_cases": 35,
            "ambiguous_cases_with_hypothetical_distinguishing_sensor": 26,
            "ambiguous_cases_not_distinguished_at_tested_sensor_settings": 0,
        },
        "friction_cone_check_is_necessary_not_sufficient": True,
        "all_normals_restitution_is_extra_unobserved_postulate": True,
        "all_sensor_readings_are_counterfactual": True,
        "source_physical_outgoing_velocities_measured": False,
        "original_trial06_mu_point_four_solver_resolved": False,
        "actual_outcome_selected": False,
        "external_physical_blueprint_constructed": False,
    }


class Trial11CounterfactualCarrierTests(unittest.TestCase):
    def test_01_five_finite_hypothetical_pages_not_physical_readings(self):
        source = example()
        unchanged = deepcopy(source)
        result = carry(source, PIN)
        self.assertEqual(source, unchanged)
        self.assertEqual(result["case_count"], 35)
        self.assertEqual(result["hypothetical_sensor_settings"], 315)
        self.assertEqual(result["ledger_witness"]["pages_verified"], 5)
        self.assertEqual(result["ledger_witness"]["observations_recorded"], 350)
        self.assertEqual(result["ledger_witness"]["steps_verified"], 1065)
        self.assertEqual(result["physical_sensor_measurements"], 0)
        self.assertFalse(result["physical_contact_selected"])
        self.assertFalse(result["frictional_solver_proven"])
        for index, page in enumerate(result["ledger_pages"]):
            self.assertTrue(verify_receipt(page["receipt"])["valid"])
            self.assertEqual(page["first_case"], 7 * index)
            self.assertEqual(page["last_case"], 7 * index + 6)
            self.assertEqual(page["rotation"], ROTATIONS[index])
            self.assertIsNone(page["receipt"]["final"]["objects"][
                "hypothetical-" + str(7*index).zfill(2) + "-0"]["measured_reading"])

    def test_02_forged_physical_measurement_never_admitted(self):
        source = example()
        source["cases"][0]["sensors"][0]["measured_reading"] = [1, 2]
        with self.assertRaisesRegex(ValueError, "measured reading"):
            carry(source, PIN)
        source = example()
        source["cases"][0]["candidates"][0]["has_actual_outgoing_motion_measurement"] = True
        with self.assertRaisesRegex(ValueError, "falsely called measured"):
            carry(source, PIN)
        source = example()
        source["actual_outcome_selected"] = True
        with self.assertRaisesRegex(ValueError, "unsupported physical claim"):
            carry(source, PIN)

    def test_03_false_friction_solver_or_new_postulate_rejected(self):
        source = example()
        source["original_trial06_mu_point_four_solver_resolved"] = True
        with self.assertRaisesRegex(ValueError, "unsupported physical claim"):
            carry(source, PIN)
        source = example()
        source["friction_cone_check_is_necessary_not_sufficient"] = False
        with self.assertRaisesRegex(ValueError, "evidence boundary"):
            carry(source, PIN)
        source = example()
        source["cases"][0]["candidates"][0]["tangent_impulses_under_original_mu_zero_model"] = [0.2]
        with self.assertRaisesRegex(ValueError, "frictional law"):
            carry(source, PIN)

    def test_04_sensor_precision_and_partition_falsehoods_rejected(self):
        source = example()
        source["cases"][0]["sensors"][1]["position_quantum"] = 0.3
        with self.assertRaisesRegex(ValueError, "sampling"):
            carry(source, PIN)
        source = example()
        source["cases"][0]["sensors"][0]["distinguishable_bins"] = 77
        with self.assertRaisesRegex(ValueError, "discriminating claim"):
            carry(source, PIN)
        source = example()
        source["cases"][0]["first_hypothetical_discriminating_sensor"] = None
        with self.assertRaisesRegex(ValueError, "first proposed"):
            carry(source, PIN)

    def test_05_original_competing_candidates_and_geometry_kept(self):
        source = example()
        source["cases"][0]["candidates"].pop()
        with self.assertRaisesRegex(ValueError, "candidate list omitted"):
            carry(source, PIN)
        source = example()
        source["cases"][10]["geometry_kind"] = "original-source-geometry"
        with self.assertRaisesRegex(ValueError, "controlled geometry"):
            carry(source, PIN)
        source = example()
        source["cases"][0]["original_admissible_count"] = 1
        with self.assertRaises(ValueError):
            carry(source, PIN)

    def test_06_independent_source_witness_exposes_tampering(self):
        result = carry(example(), PIN)
        changed = deepcopy(result["ledger_pages"][0]["receipt"])
        changed["final"]["objects"]["candidate-reading-model"]["measurements_available"] = True
        with self.assertRaises(ValueError):
            verify_receipt(changed)
        changed = deepcopy(result["ledger_pages"][0]["receipt"])
        changed["events"][-1]["effect"] = {"status": "physically-verified"}
        with self.assertRaises(ValueError):
            verify_receipt(changed)


if __name__ == "__main__":
    unittest.main()
