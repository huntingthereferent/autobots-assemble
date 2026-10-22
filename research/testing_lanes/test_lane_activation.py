"""Verify one lane's source readiness cannot become unearned science evidence."""
import copy
import unittest

from lane_activation import accepted_receipt, all_handoffs, handoff
from source_admission import catalog


class LaneActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = catalog()

    def test_all_21_have_independent_unobserved_handoffs(self):
        result = all_handoffs({})
        self.assertEqual(len(result), 21)
        self.assertEqual(len(set(x["lane_id"] for x in result)), 21)
        self.assertTrue(all(x["source_feed_status"] == "WAITING_FOR_SOURCES" for x in result))
        self.assertTrue(all(x["scientific_status"] == "NOT_TESTED" and x["experiment_runs"] == 0 for x in result))

    def test_valid_single_source_receipt_opens_only_source_feed(self):
        example = self._sample("openalex")
        result = handoff("LIT", {"openalex": example})
        self.assertEqual(result["source_feed_status"], "SOURCE_METADATA_READY")
        self.assertEqual(result["witnessed_source_ids"], ["openalex"])
        self.assertEqual(result["scientific_status"], "NOT_TESTED")
        self.assertEqual(result["experiment_runs"], 0)
        self.assertEqual(handoff("CHEM", {"openalex": example})["source_feed_status"], "WAITING_FOR_SOURCES")

    def test_manual_access_gates_are_kept(self):
        output = handoff("NEURO", {})
        self.assertTrue(any(x["source_state"] == "MANUAL_ACCESS_GATE" for x in output["sources"]))

    def test_mismatched_url_cannot_open_lane(self):
        receipt = self._sample("openalex")
        receipt["source_url"] = "https://other.example/claim"
        self.assertFalse(accepted_receipt("openalex", self.cards, receipt))
        self.assertEqual(handoff("LIT", {"openalex": receipt})["source_feed_status"], "WAITING_FOR_SOURCES")

    def test_malformed_hash_cannot_open_lane(self):
        receipt = self._sample("crossref")
        receipt["body_sha256"] = "abcd"
        self.assertFalse(accepted_receipt("crossref", self.cards, receipt))

    def test_bad_timestamp_cannot_open_lane(self):
        receipt = self._sample("crossref")
        receipt["observed_at_utc"] = "2026-10-22"
        self.assertFalse(accepted_receipt("crossref", self.cards, receipt))

    def test_fake_science_claim_cannot_open_lane(self):
        receipt = self._sample("crossref")
        receipt["scientific_claim_verified"] = True
        self.assertFalse(accepted_receipt("crossref", self.cards, receipt))

    def test_source_unknown_is_not_admitted(self):
        receipt = self._sample("crossref")
        receipt["state"] = "SOURCE_WALL"
        self.assertEqual(handoff("LIT", {"crossref": receipt})["source_feed_status"], "WAITING_FOR_SOURCES")

    def test_wrong_source_id_is_not_admitted(self):
        receipt = self._sample("crossref")
        receipt["source_id"] = "openalex"
        self.assertFalse(accepted_receipt("crossref", self.cards, receipt))

    def test_unknown_lane_is_explicit_wall(self):
        with self.assertRaisesRegex(ValueError, "unknown research test lane"):
            handoff("NO_SUCH_LANE", {})

    def _sample(self, sid):
        return {
            "source_id": sid, "source_url": self.cards[sid]["probe"]["url"],
            "response_status": 200, "state": "METADATA_OBSERVED",
            "scientific_claim_verified": False, "source_data_archived": False,
            "body_sha256": "1" * 64, "observed_at_utc": "2026-10-22T10:00:00+00:00",
            "inspection": {"semantic_record_verified": True, "record_shape": "expected_structure"},
        }


if __name__ == "__main__":
    unittest.main()
