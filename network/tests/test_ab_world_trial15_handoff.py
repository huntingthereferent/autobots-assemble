"""Trial15 source-origin and negative controls; no physical measurement inference."""
from copy import deepcopy
import unittest

from systems.workspace.world_ab_body_support import run, trial
from network.tests.test_world_ab_body_support import independent_witness
from work.ab_world.world_trial15_handoff import carry, PIN
from work.ab_world.verify_construction import verify_receipt


def original():
    return run(), trial("fixed-square", angle=30.)


class Trial15ABSourceTests(unittest.TestCase):
    def test_original_source_witness_and_nine_bounded_carriers(self):
        native, refused = original()
        before = deepcopy(native)
        for case in native["cases"]:
            self.assertTrue(independent_witness(case))
        result = carry(native, refused)
        self.assertEqual(native, before)
        self.assertTrue(result["ledger_witness"]["valid"])
        self.assertEqual(result["ledger_witness"]["pages_verified"], 9)
        self.assertEqual(result["ledger_witness"]["observations_recorded"], 25)
        self.assertEqual(result["modeled_movements"], 8)
        self.assertEqual(result["disc_cases"], 4)
        self.assertEqual(result["constrained_square_cases"], 4)
        self.assertEqual(result["unadmitted_endpoint_cases"], 1)
        self.assertGreaterEqual(result["frames_carried"], 96)
        self.assertEqual(result["real_material_measurements"], 0)
        self.assertFalse(result["free_square_rotation_solved"])
        self.assertFalse(result["contact_law_generalized"])
        for page in result["ledger_pages"]:
            self.assertTrue(verify_receipt(page["receipt"])["valid"])
        refused_final = result["ledger_pages"][-1]["receipt"]["final"]
        self.assertNotIn("movement-derived-receiver", refused_final["objects"])
        self.assertEqual(len(refused_final["observations"]), 1)

    def test_receiver_created_after_modeled_first_contact(self):
        native, refused = original()
        result = carry(native, refused)
        for page in result["ledger_pages"][:8]:
            ops = [e["operation"] for e in page["receipt"]["events"]]
            first = next(i for i, op in enumerate(ops)
                         if op.get("id") == "first-modeled-contact")
            created = next(i for i, op in enumerate(ops)
                           if op.get("id") == "movement-derived-receiver")
            second = next(i for i, op in enumerate(ops)
                          if op.get("id") == "second-modeled-contact")
            self.assertEqual(created, first + 1)
            self.assertGreater(second, created)
            self.assertTrue(all(op.get("id") != "movement-derived-receiver"
                                for op in ops[:created]))

    def test_false_hardware_claim_and_body_relabel_refused(self):
        for key, value in (("measured_earth_material", True),
                           ("actual_hardware_contact_witnessed", True),
                           ("new_physical_law_inferred", True),
                           ("target_receiver_shape_provided", True)):
            native, refused = original()
            native["cases"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                carry(native, refused)
        native, refused = original()
        native["cases"][4]["body"] = "disc"
        with self.assertRaises(ValueError):
            carry(native, refused)

    def test_invalid_source_ancestry_or_order_refused(self):
        native, refused = original()
        native["cases"][2]["receiver"]["activated_at"] = 0.
        with self.assertRaises(ValueError):
            carry(native, refused)
        native, refused = original()
        native["cases"][2]["contacts"][1]["source_id"] = "unseen"
        with self.assertRaises(ValueError):
            carry(native, refused)
        native, refused = original()
        native["cases"][2]["frames"][2]["time"] = -1.
        with self.assertRaises(ValueError):
            carry(native, refused)

    def test_unadmitted_endpoint_does_not_construct_receiver(self):
        native, refused = original()
        self.assertEqual(refused["status"], "NO_ADMITTED_INTERIOR_CONTACT")
        refused["receiver"] = deepcopy(native["cases"][4]["receiver"])
        with self.assertRaises(ValueError):
            carry(native, refused)
        native, refused = original()
        refused["frames"] = deepcopy(native["cases"][4]["frames"])
        with self.assertRaises(ValueError):
            carry(native, refused)

    def test_source_pin_and_ledger_mutation_rejected(self):
        native, refused = original()
        with self.assertRaises(ValueError):
            carry(native, refused, source_commit="0" * 40)
        receipt = carry(native, refused, source_commit=PIN)["ledger_pages"][0]["receipt"]
        damaged = deepcopy(receipt)
        damaged["events"][-1]["effect"] = {"fake": "physical evidence"}
        with self.assertRaises(ValueError):
            verify_receipt(damaged)


if __name__ == "__main__":
    unittest.main()
