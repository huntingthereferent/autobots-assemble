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


if __name__ == "__main__":
    unittest.main()
