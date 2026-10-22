"""Regression checks on first source-run evidence, not scientific results."""
import json
import re
import unittest
from pathlib import Path

from source_admission import catalog

BASE = Path(__file__).resolve().parent
OBS = BASE / "observations" / "2026-10-22-run-39767929086.json"
HANDOFFS = BASE / "observations" / "2026-10-22-source-handoffs.json"


class ArchivedSourceObservationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = catalog()
        cls.observations = json.loads(OBS.read_text(encoding="utf-8"))
        cls.handoffs = json.loads(HANDOFFS.read_text(encoding="utf-8"))

    def test_first_run_references_exact_evidence_source(self):
        doc = self.observations
        self.assertEqual(doc["observed_run_id"], 39767929086)
        self.assertEqual(doc["source_code_commit"], "b0ff39f00a109c2a17d1d2aeace3847ac0b3ffad")
        self.assertFalse(doc["dataset_files_downloaded"])
        self.assertEqual(doc["scientific_experiments_run"], 0)
        self.assertTrue(doc["previous_results_never_overwritten"])

    def test_thirteen_unique_source_receipts(self):
        receipts = self.observations["observations"]
        ids = [r["source_id"] for r in receipts]
        self.assertEqual(len(ids), 13)
        self.assertEqual(len(set(ids)), 13)
        self.assertEqual(set(ids).difference(self.cards), set())

    def test_eleven_exact_public_observations(self):
        successes = [r for r in self.observations["observations"] if r["state"] == "METADATA_OBSERVED"]
        self.assertEqual(len(successes), 11)
        for r in successes:
            with self.subTest(source=r["source_id"]):
                self.assertEqual(r["source_url"], self.cards[r["source_id"]]["probe"]["url"])
                self.assertTrue(re.fullmatch(r"[0-9a-f]{64}", r["body_sha256"]))
                self.assertEqual(r["response_status"], 200)
                self.assertTrue(r["inspection"]["semantic_record_verified"])
                self.assertFalse(r["scientific_claim_verified"])
                self.assertFalse(r["source_data_archived"])

    def test_two_original_access_walls_are_not_erased(self):
        walls = [r for r in self.observations["observations"] if r["state"] == "SOURCE_WALL"]
        self.assertEqual({r["source_id"] for r in walls}, {"zenodo", "gwosc"})
        for r in walls:
            self.assertEqual(r["error_class"], "HTTPError")
            self.assertNotIn("body_sha256", r)
            self.assertFalse(r["scientific_claim_verified"])
            self.assertFalse(r["source_data_archived"])

    def test_manual_access_checks_not_faked(self):
        self.assertEqual(set(self.observations["manual_gates"]),
                         {"physionet", "openneuro", "nist", "noaa", "oecd"})

    def test_all_21_independent_source_handoffs_are_bounded(self):
        d = self.handoffs
        self.assertEqual(len(d["lanes"]), 21)
        self.assertEqual(d["source_feed_ready"], 18)
        self.assertEqual(d["waiting_source_feed"], 3)
        self.assertEqual(d["scientific_experiments_run"], 0)
        self.assertEqual({x["lane_id"] for x in d["lanes"] if x["source_state"] == "WAITING_FOR_SOURCES"},
                         {"PHY", "NEURO", "SPACE"})
        for lane in d["lanes"]:
            self.assertEqual(lane["scientific_status"], "NOT_TESTED")
            self.assertEqual(lane["experiment_runs"], 0)
            self.assertTrue(set(lane["verified_source_ids"]) <=
                            {r["source_id"] for r in self.observations["observations"] if r["state"] == "METADATA_OBSERVED"})
            self.assertEqual(lane["source_state"] == "SOURCE_METADATA_READY",
                             bool(lane["verified_source_ids"]))


    def test_second_pass_is_append_only_and_historical_walls_remain(self):
        second = json.loads((BASE / "observations" /
                             "2026-10-22-run-39771470448.json").read_text(encoding="utf-8"))
        self.assertEqual(second["observed_run_id"], 39771470448)
        self.assertEqual(second["previous_witness"],
                         "research/testing_lanes/observations/2026-10-22-run-39767929086.json")
        self.assertEqual(second["source_status_counts"], {
            "metadata_observed": 12, "source_wall": 1, "manual_not_probed": 5
        })
        by_id = {r["source_id"]: r for r in second["observations"]}
        self.assertEqual(len(by_id), 13)
        self.assertEqual(by_id["zenodo"]["state"], "METADATA_OBSERVED")
        self.assertEqual(by_id["gwosc"]["state"], "SOURCE_WALL")
        old_by_id = {r["source_id"]: r for r in self.observations["observations"]}
        self.assertEqual(old_by_id["zenodo"]["state"], "SOURCE_WALL")
        for row in second["observations"]:
            with self.subTest(source=row["source_id"]):
                self.assertFalse(row["scientific_claim_verified"])
                self.assertFalse(row["source_data_archived"])
                if row["state"] == "METADATA_OBSERVED":
                    self.assertEqual(row["source_url"],
                                     self.cards[row["source_id"]]["probe"]["url"])
                    self.assertRegex(row["body_sha256"], r"^[0-9a-f]{64}$")
                    self.assertEqual(row["response_status"], 200)

    def test_second_pass_source_handoffs_keep_science_not_tested(self):
        doc = json.loads((BASE / "observations" /
                          "2026-10-22-run-39771470448-lanes.json").read_text(encoding="utf-8"))
        self.assertEqual(doc["source_feed_ready"], 20)
        self.assertEqual(doc["waiting_source_feed"], 1)
        self.assertEqual(doc["scientific_experiments_run"], 0)
        self.assertEqual(len(doc["lanes"]), 21)
        self.assertEqual({x["lane_id"] for x in doc["lanes"]}, {
            x["id"] for x in __import__("json").loads((BASE / "registry.json").read_text())["lanes"]
        })
        self.assertEqual({x["lane_id"] for x in doc["lanes"] if x["source_state"] == "WAITING_FOR_SOURCES"},
                         {"NEURO"})
        for lane in doc["lanes"]:
            self.assertEqual(lane["scientific_status"], "NOT_TESTED")
            self.assertEqual(lane["experiment_runs"], 0)



if __name__ == "__main__":
    unittest.main()
