"""A source-first fail-closed contract, not fabricated ARC native tests."""
import unittest
from work.arc3.arc4_intervention_gate import make_plan

def fixture():
    obs = {
        "first_new6_outside_cups": {
            "row5": {"frame": 19, "x": [14, 15]},
            "row8": None,
        },
    }
    record = {
        "case": "positive",
        "original_native_action_word": "6@34,21 3 5",
        "source_observations": obs,
        "original_sdk_action_receipts": [{
            "genuine_original_action": 6,
            "real_native_click_xy": [34, 21],
            "original_source_pixel_before_click": 8,
        }],
    }
    a = dict(record, native_witness="A")
    b = dict(record, native_witness="B")
    proposal = {
        "case": "positive", "source_contact_row": "row5",
        "contact_frame": 19, "contact_x": 14,
        "source_click_xy": [34, 21], "native_action": 3,
    }
    return {"kind": "ARC4_SOURCE_OWNED_EVENT_ORDER_AUDIT",
            "original_native_records": [a, b]}, proposal

class GateTests(unittest.TestCase):
    def test_admits_exact_dual_source_receipts(self):
        audit, proposal = fixture()
        plan = make_plan(audit, proposal)
        self.assertEqual(plan["intervention_native_action_word"], "6@34,21 3 6@34,21 3 5")
    def test_rejects_fabricated_contact(self):
        audit, proposal = fixture()
        proposal["contact_x"] = 16
        with self.assertRaises(ValueError):
            make_plan(audit, proposal)
    def test_rejects_unattested_click(self):
        audit, proposal = fixture()
        proposal["source_click_xy"] = [33, 21]
        with self.assertRaises(ValueError):
            make_plan(audit, proposal)
    def test_rejects_single_witness(self):
        audit, proposal = fixture()
        audit["original_native_records"].pop()
        with self.assertRaises(ValueError):
            make_plan(audit, proposal)
    def test_rejects_color_as_action(self):
        audit, proposal = fixture()
        proposal["native_action"] = 5
        with self.assertRaises(ValueError):
            make_plan(audit, proposal)
    def test_rejects_witness_disagreement(self):
        audit, proposal = fixture()
        audit["original_native_records"][1]["source_observations"] = {"first_new6_outside_cups": {"row5": None}}
        with self.assertRaises(ValueError):
            make_plan(audit, proposal)

if __name__ == "__main__":
    unittest.main()
