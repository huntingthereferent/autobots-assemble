"""Offline controls for COMP-SORT-COMPARISON-001."""
import unittest

from comp_sort_comparison import build_receipt, fixed_cases, merge_sort, compare


class CompSortTests(unittest.TestCase):
    def test_all_fixed_cases_match_baseline_and_preserve_stability(self):
        receipt = build_receipt()
        self.assertTrue(receipt["all_outputs_equal"])
        self.assertTrue(receipt["all_baselines_stable"])
        self.assertEqual(len(receipt["cases"]), 6)
        self.assertTrue(all(row["items"] == 512 for row in receipt["cases"].values()))

    def test_same_seed_produces_same_input_hashes(self):
        first = build_receipt()["cases"]
        second = build_receipt()["cases"]
        self.assertEqual(
            {key: row["input_sha256"] for key, row in first.items()},
            {key: row["input_sha256"] for key, row in second.items()},
        )

    def test_negative_control_detects_dropped_record(self):
        values = [(3, 0), (1, 1), (2, 2)]
        correct = merge_sort(values, compare, [0])
        faulty = correct[:-1]
        self.assertNotEqual(faulty, sorted(values, key=lambda item: item[0]))

    def test_equal_keys_are_stable(self):
        values = [(1, 0), (0, 1), (1, 2), (0, 3), (1, 4)]
        result = merge_sort(values, compare, [0])
        self.assertEqual(result, [(0, 1), (0, 3), (1, 0), (1, 2), (1, 4)])


if __name__ == "__main__":
    unittest.main()
