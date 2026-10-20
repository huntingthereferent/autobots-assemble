"""Trial07 source-carrier tests. Native dynamics remain the source's job."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial07_handoff import carry, ORIGINAL_OFFSETS
from work.ab_world.verify_construction import verify_receipt

PIN = "bda4bc271a985965558fc8f0d48e89fee07161d0"


def fixture():
    y = 1.3910443961
    ids = ["source-face-0", "source-face-20"]
    probes = []
    for offset in ORIGINAL_OFFSETS:
        tie = offset == 0
        probes.append({
            "offset": offset,
            "entry_y": round(y + offset, 12),
            "status": "unresolved-multiple-contacts" if tie else "completed",
            "observed_contacts": 0 if tie else 1,
            "first_contact": None if tie else ids[0],
            "end_time": 0.5 if tie else 1.5,
            "surface_order_independent": True,
            "unresolved": {"time": 0.5, "surfaces": ids[:], "center": [8, y]}
                          if tie else None,
        })
    return {
        "schema": "world-ab-junction-arrival-tie/v1",
        "source_geometry": {
            "surfaces": [{"id": ids[0]}, {"id": ids[1]}],
            "junction": [8, y],
            "topology": {"segments": 2, "intersections": 1},
        },
        "bracket": [1.35, 1.4],
        "junction_contact": {
            "entry_y": y, "candidate_gap": 0., "contact_time": 1.,
            "contact_center": [8, y], "source_ids": ids,
            "features": ["interior", "interior"],
            "normals": [[1, 0], [0.9, 0.1]],
        },
        "probes": probes,
        "simultaneous_contact_solver": False,
        "unresolved_contacts_remain_unresolved": True,
        "source_04B_branches_simultaneously_generated": False,
        "earth_material_equivalence": False,
        "full_original_blueprint_generated": False,
    }


class SourceTieTests(unittest.TestCase):
    def test_01_preserves_real_unresolved_label_and_nearby_controls(self):
        native = fixture()
        original = deepcopy(native)
        record = carry(native, PIN)
        self.assertEqual(native, original)
        self.assertEqual(record["control_probes_recorded"], 9)
        self.assertEqual(record["native_tie_status"], "unresolved-multiple-contacts")
        self.assertEqual(record["native_tie_contacts"], 0)
        self.assertFalse(record["outgoing_impulse_decided"])
        self.assertFalse(record["material_world_verified"])
        self.assertEqual(record["ledger_witness"]["steps_verified"], 32)
        self.assertEqual(record["ledger_witness"]["observations_recorded"], 10)
        self.assertEqual(record["ledger_witness"]["comparisons"], {})
        self.assertTrue(verify_receipt(record["world_receipt"])["valid"])
        state = record["world_receipt"]["final"]["objects"]["source-simultaneous-arrival"]
        self.assertEqual(state["resolution"], "UNRESOLVED")
        self.assertIsNone(state["outgoing_impulse"])

    def test_02_cannot_turn_a_tie_into_a_successful_contact(self):
        source = fixture()
        source["probes"][4]["status"] = "completed"
        with self.assertRaisesRegex(ValueError, "silently resolved"):
            carry(source, PIN)
        source = fixture()
        source["probes"][4]["observed_contacts"] = 1
        with self.assertRaisesRegex(ValueError, "fictional impulse"):
            carry(source, PIN)

    def test_03_original_source_ids_and_bracket_must_be_kept(self):
        for change in (
            lambda o: o["junction_contact"]["source_ids"].reverse(),
            lambda o: o["junction_contact"].__setitem__("candidate_gap", .1),
            lambda o: o["bracket"].__setitem__(1, 1.38),
        ):
            obj = fixture()
            change(obj)
            with self.assertRaises(ValueError):
                carry(obj, PIN)

    def test_04_no_reordering_or_implicit_world_laws(self):
        obj = fixture()
        obj["probes"][2], obj["probes"][3] = obj["probes"][3], obj["probes"][2]
        with self.assertRaisesRegex(ValueError, "roster"):
            carry(obj, PIN)
        obj = fixture()
        obj["simultaneous_contact_solver"] = True
        with self.assertRaisesRegex(ValueError, "cannot be promoted"):
            carry(obj, PIN)
        obj = fixture()
        obj["probes"][5]["surface_order_independent"] = False
        with self.assertRaisesRegex(ValueError, "surface ordering"):
            carry(obj, PIN)

    def test_05_source_label_is_not_authentication(self):
        with self.assertRaisesRegex(ValueError, "pin"):
            carry(fixture(), "experiment/world-trial07")
        original = carry(fixture(), PIN)
        self.assertFalse(original["source_authenticated_by_adapter"])
        self.assertFalse(original["native_physics_verified_by_adapter"])

    def test_06_witness_rejects_tampered_or_promoted_ledger(self):
        native = carry(fixture(), PIN)["world_receipt"]
        altered = deepcopy(native)
        altered["events"][-1]["effect"] = {"status": "solved-contact"}
        with self.assertRaises(ValueError):
            verify_receipt(altered)
        altered = deepcopy(native)
        altered["final"]["objects"]["source-simultaneous-arrival"]["resolution"] = "SOLVED"
        with self.assertRaises(ValueError):
            verify_receipt(altered)


if __name__ == "__main__":
    unittest.main()
