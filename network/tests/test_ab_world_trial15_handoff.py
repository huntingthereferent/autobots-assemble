"""Standalone Trial15 neutral-ledger tests; original native source is NOT in main.

These bounded fixtures test transport invariants. The dedicated GitHub Actions
lane separately runs unchanged pinned original WORLD15 source and independent
numerical witness before carrying its actual JSON into the A/B ledger.
"""
from copy import deepcopy
import unittest

from work.ab_world.world_trial15_handoff import carry, PIN, SOURCE, BODIES, ANGLES
from work.ab_world.verify_construction import verify_receipt


def sample_case(body, angle):
    first = {"time": .2, "source_id": "original-test-source",
             "center": [4., 1.5], "before": [3., 0.], "after": [-3., 0.]}
    second = {"time": .4, "source_id": "movement-derived-receiver",
              "center": [3.4, 1.5], "before": [-3., 0.], "after": [3., 0.]}
    frames = []
    for i in range(12):
        t = round(i * .05, 10)
        frames.append({"time": t,
                       "center": [3. + t, 1.5],
                       "velocity": [3., 0.] if t < .2 or t >= .4 else [-3., 0.]})
    return {
        "schema": SOURCE, "body": body, "source_angle": angle,
        "source_anchor": [12., 1.5],
        "body_support": ("disc radius" if body == "disc" else
                         "axis-aligned square support, orientation fixed by constraint"),
        "half_extent": .25, "initial_center": [3., 1.5],
        "initial_velocity": [3., 0.],
        "source": {"id": "original-test-source",
                   "anchor": [12., 1.5], "normal": [-1., 0.],
                   "endpoints": [[12., 1.], [12., 2.]]},
        "receiver": {"id": "movement-derived-receiver",
                     "anchor": [3.65, 1.5], "normal": [1., 0.],
                     "endpoints": [[3.65, 1.], [3.65, 2.]],
                     "activated_at": .2, "caused_by_contact_index": 0,
                     "constructed_from": "recorded-model-outgoing-velocity"},
        "contacts": [first, second], "frames": frames,
        "status": "TWO_MODELED_CONTACTS",
        "selected_physical_outcome": False,
        "measured_earth_material": False,
        "target_receiver_shape_provided": False,
        "actual_hardware_contact_witnessed": False,
        "new_physical_law_inferred": False,
        "square_rotation_prevented_by_constraint": body == "fixed-square",
    }


def sample():
    native = {
        "schema": SOURCE, "body_types": list(BODIES),
        "angles": list(ANGLES), "no_new_world_or_renderer": True,
        "real_material_behavior_observed": False,
        "shape_independent_contact_law": "frictionless translational normal reflection",
        "cases": [sample_case(body, angle)
                  for body in BODIES for angle in ANGLES],
    }
    refused = {
        "schema": SOURCE, "body": "fixed-square",
        "source_angle": 30., "status": "NO_ADMITTED_INTERIOR_CONTACT",
        "source": native["cases"][4]["source"],
        "receiver": None, "frames": [], "contacts": [],
        "measured_earth_material": False,
    }
    return native, refused


class Trial15ABSourceTests(unittest.TestCase):
    def test_eight_source_fixtures_and_refused_endpoint_carried_separately(self):
        native, refused = sample()
        original = deepcopy(native)
        result = carry(native, refused)
        self.assertEqual(native, original)
        self.assertTrue(result["ledger_witness"]["valid"])
        self.assertEqual(result["ledger_witness"]["pages_verified"], 9)
        self.assertEqual(result["ledger_witness"]["observations_recorded"], 25)
        self.assertEqual(result["modeled_movements"], 8)
        self.assertEqual(result["disc_cases"], 4)
        self.assertEqual(result["constrained_square_cases"], 4)
        self.assertEqual(result["unadmitted_endpoint_cases"], 1)
        self.assertEqual(result["frames_carried"], 96)
        self.assertEqual(result["real_material_measurements"], 0)
        self.assertFalse(result["free_square_rotation_solved"])
        self.assertFalse(result["contact_law_generalized"])
        for page in result["ledger_pages"]:
            self.assertTrue(verify_receipt(page["receipt"])["valid"])
        rejected = result["ledger_pages"][-1]["receipt"]["final"]
        self.assertNotIn("movement-derived-receiver", rejected["objects"])
        self.assertEqual(len(rejected["observations"]), 1)

    def test_receiver_is_not_installed_before_first_source_contact(self):
        native, refused = sample()
        for page in carry(native, refused)["ledger_pages"][:8]:
            ops = [e["operation"] for e in page["receipt"]["events"]]
            first = next(i for i, op in enumerate(ops)
                         if op.get("id") == "first-modeled-contact")
            created = next(i for i, op in enumerate(ops)
                           if op.get("id") == "movement-derived-receiver")
            second = next(i for i, op in enumerate(ops)
                          if op.get("id") == "second-modeled-contact")
            self.assertEqual(created, first + 1)
            self.assertGreater(second, created)

    def test_unobserved_materials_and_relabeling_rejected(self):
        for key in ("measured_earth_material", "actual_hardware_contact_witnessed",
                    "new_physical_law_inferred", "target_receiver_shape_provided"):
            native, refused = sample()
            native["cases"][0][key] = True
            with self.subTest(key=key), self.assertRaises(ValueError):
                carry(native, refused)
        native, refused = sample()
        native["cases"][4]["body"] = "disc"
        with self.assertRaises(ValueError):
            carry(native, refused)

    def test_backdated_receiver_and_malformed_source_frames_rejected(self):
        native, refused = sample()
        native["cases"][2]["receiver"]["activated_at"] = 0.
        with self.assertRaises(ValueError):
            carry(native, refused)
        native, refused = sample()
        native["cases"][2]["contacts"][1]["source_id"] = "unseen"
        with self.assertRaises(ValueError):
            carry(native, refused)
        native, refused = sample()
        native["cases"][2]["frames"][2]["time"] = -1.
        with self.assertRaises(ValueError):
            carry(native, refused)

    def test_refused_source_cannot_acquire_an_invented_receiver(self):
        native, refused = sample()
        refused["receiver"] = deepcopy(native["cases"][4]["receiver"])
        with self.assertRaises(ValueError):
            carry(native, refused)
        native, refused = sample()
        refused["frames"] = deepcopy(native["cases"][4]["frames"])
        with self.assertRaises(ValueError):
            carry(native, refused)

    def test_pinned_source_and_tamper_replay(self):
        native, refused = sample()
        with self.assertRaises(ValueError):
            carry(native, refused, source_commit="0" * 40)
        receipt = carry(native, refused, source_commit=PIN)["ledger_pages"][0]["receipt"]
        bad = deepcopy(receipt)
        bad["events"][-1]["effect"] = {"fake": "physical evidence"}
        with self.assertRaises(ValueError):
            verify_receipt(bad)


if __name__ == "__main__":
    unittest.main()
