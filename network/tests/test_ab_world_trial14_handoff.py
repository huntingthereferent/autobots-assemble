"""Trial14 controls: source-derived receiver exists only after modeled source impact."""
from copy import deepcopy
import unittest

from work.ab_world.world_trial14_handoff import carry, ANGLES, FRICTIONS, SOURCE
from work.ab_world.verify_construction import verify_receipt

PIN = "344d419be87b737b7cc8af57fb8c680ce492beac"


def fixture(angle=0., friction=.4, anchor=(12., 1.5), status="TWO_CONTACTS_IN_DECLARED_MODEL"):
    source = {
        "id": "finite-input-source", "normal": [-1., 0.],
        "anchor": list(anchor), "endpoints": [[12., 1.], [12., 2.]],
        "span": 1.,
    }
    case = {
        "schema": SOURCE,
        "input_source_angle_degrees": angle,
        "input_source_anchor": list(anchor),
        "friction": friction, "source": source,
        "disc_radius": .25, "disc_inertia": .025,
        "input_origin": [3., 1.35],
        "input_velocity": [3., .12],
        "measured_physical_material": False,
        "source_collision_is_a_declared_model": True,
        "target_shape_supplied": False,
    }
    if status == "NO_FINITE_SEGMENT_CONTACT":
        return {**case, "status": status, "receiver": None,
                "contacts": [], "frames": []}
    receiver = {
        "id": "movement-derived-receiver", "normal": [1., 0.],
        "anchor": [11., 1.6], "endpoints": [[11., 1.1], [11., 2.1]],
        "span": 1., "activated_at": .2,
        "source_contact_index": 0, "constructed_from": "first-outgoing-velocity",
    }
    contact1 = {
        "time": .2, "source_id": source["id"], "center": [11.75, 1.5],
        "incoming_velocity": [3., .12], "outgoing_velocity": [-3., .12],
        "outgoing_spin": 0.2,
        "impulse": {"normal_impulse": 6., "tangential_impulse": .1},
    }
    contact2 = {
        "time": .4, "source_id": receiver["id"], "center": [11.0, 1.6],
        "incoming_velocity": [-3., .12], "outgoing_velocity": [3., .12],
        "outgoing_spin": .1,
        "impulse": {"normal_impulse": 6., "tangential_impulse": .1},
    }
    frames = []
    for t in (0., .1, .2, .3, .4, .5):
        phase = ("before-source-contact" if t < .2 else
                 "source-contact-to-receiver" if t < .4 else
                 "after-derived-contact")
        frames.append({
            "time": t, "phase": phase, "position": [3. + t, 1.35],
            "velocity": [3., .12] if t < .2 or t >= .4 else [-3., .12],
            "spin": 0. if t < .2 else .2 if t < .4 else .1,
        })
    return {**case, "status": status, "receiver": receiver,
            "contacts": [contact1, contact2], "frames": frames,
            "source_model_04B_unchanged": True, "world48_and_nih_unmodified": True,
            "all_physical_interactions_solved": False}


def sample():
    return {
        "schema": SOURCE,
        "source_angle_grid": list(ANGLES),
        "friction_grid": list(FRICTIONS),
        "cases": [fixture(angle, friction) for angle in ANGLES
                  for friction in FRICTIONS],
        "new_receiver_shape_is_source_derived": True,
        "real_earth_physics_verified": False,
        "physical_motor_or_nih_blueprint_tested": False,
    }


class Trial14CausalCarrierTests(unittest.TestCase):
    def test_01_source_movement_creates_receiver_in_causal_event_order(self):
        raw, miss = sample(), fixture(status="NO_FINITE_SEGMENT_CONTACT",
                                     anchor=(12.,4.))
        original = deepcopy(raw)
        result = carry(raw, PIN, miss)
        self.assertEqual(raw, original)
        self.assertEqual(result["completed_causal_movements"], 8)
        self.assertEqual(result["source_misses"], 1)
        self.assertEqual(result["source_frames_carried"], 48)
        self.assertEqual(result["ledger_witness"]["pages_verified"], 9)
        self.assertEqual(result["ledger_witness"]["observations_recorded"], 25)
        self.assertEqual(result["ledger_witness"]["steps_verified"], 115)
        self.assertEqual(result["physical_material_measurements"], 0)
        self.assertFalse(result["real_material_construction_verified"])
        self.assertTrue(result["ledger_witness"]["valid"])
        for page in result["ledger_pages"]:
            self.assertTrue(verify_receipt(page["receipt"])["valid"])
        first = result["ledger_pages"][0]["receipt"]
        ops = [x["operation"] for x in first["events"]]
        observe = next(i for i,step in enumerate(ops)
                       if step["op"] == "observe" and
                       step["id"] == "first-modeled-contact")
        create = next(i for i,step in enumerate(ops)
                      if step["op"] == "introduce" and
                      step["id"] == "derived-receiver-face")
        self.assertEqual(create, observe + 1)
        self.assertTrue(all(step.get("id") != "derived-receiver-face"
                            for step in ops[:create]))
        self.assertNotIn("derived-receiver-face",
                         result["ledger_pages"][-1]["receipt"]["final"]["objects"])

    def test_02_invented_receiver_on_miss_rejected(self):
        raw, miss = sample(), fixture(status="NO_FINITE_SEGMENT_CONTACT",
                                     anchor=(12.,4.))
        miss["receiver"] = raw["cases"][0]["receiver"]
        with self.assertRaisesRegex(ValueError, "source miss converted"):
            carry(raw, PIN, miss)
        miss = fixture(status="NO_FINITE_SEGMENT_CONTACT",anchor=(12.,4.))
        miss["frames"] = raw["cases"][0]["frames"]
        with self.assertRaisesRegex(ValueError, "source miss converted"):
            carry(raw, PIN, miss)

    def test_03_receiver_cannot_exist_before_first_contact(self):
        raw = sample()
        raw["cases"][0]["receiver"]["activated_at"] = 0.
        with self.assertRaisesRegex(ValueError, "receiver existed before"):
            carry(raw, PIN, fixture(status="NO_FINITE_SEGMENT_CONTACT",
                                    anchor=(12.,4.)))
        raw = sample()
        raw["cases"][0]["receiver"]["constructed_from"] = "target-shape"
        with self.assertRaisesRegex(ValueError, "receiver ancestry"):
            carry(raw, PIN, fixture(status="NO_FINITE_SEGMENT_CONTACT",
                                    anchor=(12.,4.)))

    def test_04_falsified_contact_or_out_of_order_frame_rejected(self):
        raw = sample()
        raw["cases"][0]["contacts"][1]["source_id"] = "invented"
        with self.assertRaisesRegex(ValueError, "receiver existed before"):
            carry(raw, PIN, fixture(status="NO_FINITE_SEGMENT_CONTACT",
                                    anchor=(12.,4.)))
        raw = sample()
        raw["cases"][0]["frames"][3]["time"] = .1
        with self.assertRaisesRegex(ValueError, "chronological"):
            carry(raw, PIN, fixture(status="NO_FINITE_SEGMENT_CONTACT",
                                    anchor=(12.,4.)))

    def test_05_no_physical_promotion_or_fake_case_grid(self):
        raw = sample()
        raw["real_earth_physics_verified"] = True
        with self.assertRaisesRegex(ValueError, "physical blueprint"):
            carry(raw, PIN, fixture(status="NO_FINITE_SEGMENT_CONTACT",
                                    anchor=(12.,4.)))
        raw = sample()
        raw["cases"][1]["measured_physical_material"] = True
        with self.assertRaisesRegex(ValueError, "material"):
            carry(raw, PIN, fixture(status="NO_FINITE_SEGMENT_CONTACT",
                                    anchor=(12.,4.)))
        raw = sample()
        raw["cases"][0], raw["cases"][1] = raw["cases"][1], raw["cases"][0]
        with self.assertRaisesRegex(ValueError, "control changed"):
            carry(raw, PIN, fixture(status="NO_FINITE_SEGMENT_CONTACT",
                                    anchor=(12.,4.)))
        with self.assertRaisesRegex(ValueError, "pin exact"):
            carry(sample(), "branch name", fixture(status="NO_FINITE_SEGMENT_CONTACT",
                                                    anchor=(12.,4.)))

    def test_06_independent_replay_detects_receipt_mutation(self):
        receipt = carry(sample(), PIN,
                        fixture(status="NO_FINITE_SEGMENT_CONTACT",
                                anchor=(12.,4.)))["ledger_pages"][0]["receipt"]
        bad = deepcopy(receipt)
        bad["final"]["objects"]["derived-receiver-face"]["activated_at"] = 0.
        with self.assertRaises(ValueError):
            verify_receipt(bad)
        bad = deepcopy(receipt)
        bad["events"][-1]["effect"] = {"status": "real hardware generated"}
        with self.assertRaises(ValueError):
            verify_receipt(bad)


if __name__ == "__main__":
    unittest.main()
