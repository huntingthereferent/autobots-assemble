"""Regression checks on first source-run evidence, not scientific results."""
import json
import re
import unittest
from pathlib import Path

from source_admission import catalog

BASE = Path(__file__).resolve().parent
OBS = BASE / "observations" / "2026-10-22-run-39767929086.json"
HANDOFFS = BASE / "observations" / "2026-10-22-source-handoffs.json"
SECOND_OBS = BASE / "observations" / "2026-10-22-run-39771470448.json"
SECOND_HANDOFFS = BASE / "observations" / "2026-10-22-source-handoffs-run-39771470448.json"


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


class SecondSourceObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = json.loads(OBS.read_text(encoding="utf-8"))
        cls.second = json.loads(SECOND_OBS.read_text(encoding="utf-8"))
        cls.handoff = json.loads(SECOND_HANDOFFS.read_text(encoding="utf-8"))

    def test_first_run_is_preserved_not_relabelled(self):
        self.assertEqual(self.old["observed_run_id"], 39767929086)
        self.assertEqual(self.old["source_status_counts"]["metadata_observed"], 11)
        self.assertEqual(self.old["source_status_counts"]["source_wall"], 2)

    def test_second_run_exact_source_count_and_hash_receipts(self):
        d = self.second
        self.assertEqual(d["observed_run_id"], 39771470448)
        self.assertEqual(d["source_code_commit"], "8fa80de0dbf3f4aaa55d74d2390e45c1b0192a59")
        self.assertEqual(len(d["observations"]), 13)
        self.assertEqual(d["source_status_counts"], {
            "metadata_observed": 12, "source_wall": 1, "manual_not_probed": 5
        })
        successes = [r for r in d["observations"] if r["state"] == "METADATA_OBSERVED"]
        self.assertEqual(len(successes), 12)
        for record in successes:
            self.assertRegex(record["body_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(record["response_status"], 200)
            self.assertFalse(record["scientific_claim_verified"])
            self.assertFalse(record["source_data_archived"])

    def test_original_gwosc_format_wall_retained(self):
        gwosc = next(r for r in self.second["observations"] if r["source_id"] == "gwosc")
        self.assertEqual(gwosc["state"], "SOURCE_WALL")
        self.assertEqual(gwosc["error_class"], "JSONDecodeError")
        self.assertIn("format=api", gwosc["source_url"])
        self.assertNotIn("body_sha256", gwosc)
        self.assertFalse(gwosc["scientific_claim_verified"])

    def test_zenodo_source_admitted_only_as_metadata(self):
        zenodo = next(r for r in self.second["observations"] if r["source_id"] == "zenodo")
        self.assertEqual(zenodo["state"], "METADATA_OBSERVED")
        self.assertIn("zenodo.org", zenodo["source_url"])
        self.assertFalse(zenodo["scientific_claim_verified"])

    def test_21_actual_lane_preflights_and_neuroscience_wall(self):
        d = self.handoff
        self.assertEqual(d["source_feed_ready"], 20)
        self.assertEqual(d["waiting_source_feed"], 1)
        self.assertEqual(d["individual_lane_ci_jobs_passed"], 21)
        self.assertEqual(d["scientific_experiments_run"], 0)
        self.assertEqual(len(d["lanes"]), 21)
        self.assertEqual(len({x["lane_id"] for x in d["lanes"]}), 21)
        waiting = [x for x in d["lanes"] if x["source_feed_status"] == "WAITING_FOR_SOURCES"]
        self.assertEqual([x["lane_id"] for x in waiting], ["NEURO"])
        self.assertEqual({x["source_id"] for x in waiting[0]["source_dependencies"]},
                         {"openneuro", "physionet"})
        for row in d["lanes"]:
            self.assertEqual(row["scientific_status"], "NOT_TESTED")
            self.assertEqual(row["experiment_runs"], 0)

    def test_physics_and_space_source_ready_without_gwosc_success(self):
        rows = {x["lane_id"]: x for x in self.handoff["lanes"]}
        for lane_id in ("PHY", "SPACE"):
            self.assertEqual(rows[lane_id]["source_feed_status"], "SOURCE_METADATA_READY")
            self.assertIn("zenodo", rows[lane_id]["verified_source_ids"])
            self.assertNotIn("gwosc", rows[lane_id]["verified_source_ids"])


if __name__ == "__main__":
    unittest.main()
