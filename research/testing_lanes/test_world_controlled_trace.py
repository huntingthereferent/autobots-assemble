"""Offline controls for WORLD-CONTROLLED-TRACE-001."""
import unittest

from world_controlled_trace import build_receipt, run_policy


class WorldTraceTests(unittest.TestCase):
    def test_same_seed_reproduces_world_and_trace(self):
        a = run_policy(17)
        b = run_policy(17)
        self.assertEqual(a["world_sha256"], b["world_sha256"])
        self.assertEqual(a["trace"], b["trace"])
        self.assertEqual(a["trace_sha256"], b["trace_sha256"])

    def test_different_seed_changes_controlled_world(self):
        self.assertNotEqual(run_policy(17)["world_sha256"], run_policy(23)["world_sha256"])

    def test_trace_has_contiguous_step_numbers(self):
        trace = run_policy(17)["trace"]
        self.assertEqual([item["step"] for item in trace], list(range(len(trace))))

    def test_receipt_records_control_outcomes_and_limits(self):
        receipt = build_receipt()
        self.assertEqual(receipt["status"], "CONTROL_PASS")
        self.assertTrue(receipt["controls"]["same_seed_same_trace"])
        self.assertTrue(receipt["controls"]["different_seed_different_world"])
        self.assertTrue(receipt["limits"])


if __name__ == "__main__":
    unittest.main()
