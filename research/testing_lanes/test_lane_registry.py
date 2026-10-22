"""Offline regression checks for research test-lane admission and promotion."""
import copy
import unittest

from lane_registry import read_registry, make_plan, validate_registry


class ResearchLaneRegistryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = read_registry()

    def test_initial_catalog_has_candidate_lanes_and_no_invented_results(self):
        self.assertGreaterEqual(len(self.data["lanes"]), 20)
        self.assertGreaterEqual(len(self.data["sources"]), 15)
        self.assertTrue(all(l["status"] == "candidate" for l in self.data["lanes"]))
        self.assertTrue(all(not l["witnesses"] and l["last_run"] is None for l in self.data["lanes"]))

    def test_every_lane_can_make_an_unobserved_plan_with_explicit_gates(self):
        for lane in self.data["lanes"]:
            with self.subTest(lane=lane["id"]):
                plan = make_plan(lane["id"], self.data)
                self.assertEqual(plan["status"], "UNOBSERVED")
                self.assertEqual(plan["experimental_witness"]["outcome"], "UNKNOWN")
                self.assertIsNone(plan["source_receipt"]["raw_sha256"])
                self.assertTrue(plan["source_candidates"])
                self.assertTrue(plan["test_contract"]["counterexample"])

    def test_rejects_dangling_source(self):
        bad = copy.deepcopy(self.data)
        bad["lanes"][0]["source_ids"] = ["not-registered"]
        with self.assertRaises(ValueError):
            validate_registry(bad)

    def test_rejects_duplicate_lane_ids(self):
        bad = copy.deepcopy(self.data)
        bad["lanes"].append(copy.deepcopy(bad["lanes"][0]))
        with self.assertRaises(ValueError):
            validate_registry(bad)

    def test_rejects_unearned_test_promotion(self):
        bad = copy.deepcopy(self.data)
        bad["lanes"][0]["status"] = "tested"
        with self.assertRaises(ValueError):
            validate_registry(bad)

    def test_rejects_candidate_with_claimed_results(self):
        bad = copy.deepcopy(self.data)
        bad["lanes"][0]["last_run"] = "2026-10-22"
        with self.assertRaises(ValueError):
            validate_registry(bad)

    def test_rejects_implicit_fetch(self):
        bad = copy.deepcopy(self.data)
        bad["default_fetch"] = "enabled"
        with self.assertRaises(ValueError):
            validate_registry(bad)

    def test_rejects_insecure_source_url(self):
        bad = copy.deepcopy(self.data)
        bad["sources"][0]["doc_url"] = "http://example.net"
        with self.assertRaises(ValueError):
            validate_registry(bad)

    def test_unknown_lane_is_a_wall(self):
        with self.assertRaisesRegex(ValueError, "unknown research test lane"):
            make_plan("../UNREGISTERED", self.data)


if __name__ == "__main__":
    unittest.main()
