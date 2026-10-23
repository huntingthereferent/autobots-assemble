"""Cross-object lineage checks for source receipt -> lane handoff."""
import copy
import hashlib
import json
import unittest

from lane_activation import handoff
from source_admission import catalog


class CrossObjectSourceLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = catalog()

    def sample_receipt(self):
        return {
            "source_id": "openalex",
            "source_url": self.cards["openalex"]["probe"]["url"],
            "response_status": 200,
            "state": "METADATA_OBSERVED",
            "scientific_claim_verified": False,
            "source_data_archived": False,
            "body_sha256": "a" * 64,
            "observed_at_utc": "2026-10-22T10:00:00+00:00",
            "inspection": {
                "semantic_record_verified": True,
                "record_shape": "expected_structure",
            },
        }

    def test_accepted_receipt_identity_survives_lane_handoff(self):
        receipt = self.sample_receipt()
        result = handoff("LIT", {"openalex": receipt})
        source = next(row for row in result["sources"] if row["source_id"] == "openalex")
        lineage = source["accepted_observation"]
        canonical = json.dumps(
            receipt, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")

        self.assertEqual(source["source_state"], "METADATA_AVAILABLE")
        self.assertEqual(lineage["source_url"], receipt["source_url"])
        self.assertEqual(lineage["observed_at_utc"], receipt["observed_at_utc"])
        self.assertEqual(lineage["response_status"], 200)
        self.assertEqual(lineage["body_sha256"], receipt["body_sha256"])
        self.assertEqual(lineage["receipt_sha256"], hashlib.sha256(canonical).hexdigest())
        self.assertEqual(result["scientific_status"], "NOT_TESTED")
        self.assertEqual(result["experiment_runs"], 0)

    def test_receipt_does_not_transfer_to_unrelated_lane(self):
        receipt = self.sample_receipt()
        result = handoff("CHEM", {"openalex": receipt})
        self.assertEqual(result["source_feed_status"], "WAITING_FOR_SOURCES")
        self.assertEqual(result["scientific_status"], "NOT_TESTED")
        self.assertFalse(any(
            row.get("accepted_observation")
            for row in result["sources"]
        ))

    def test_invalid_receipt_does_not_emit_accepted_lineage(self):
        receipt = self.sample_receipt()
        receipt["source_url"] = "https://example.invalid/wrong-source"
        result = handoff("LIT", {"openalex": receipt})
        source = next(row for row in result["sources"] if row["source_id"] == "openalex")
        self.assertEqual(source["source_state"], "SOURCE_UNVERIFIED")
        self.assertNotIn("accepted_observation", source)
        self.assertEqual(result["scientific_status"], "NOT_TESTED")

    def test_receipt_fingerprint_changes_when_receipt_changes(self):
        first = self.sample_receipt()
        second = copy.deepcopy(first)
        second["observed_at_utc"] = "2026-10-22T10:00:01+00:00"
        output_a = handoff("LIT", {"openalex": first})
        output_b = handoff("LIT", {"openalex": second})
        def fingerprint(output):
            source = next(row for row in output["sources"] if row["source_id"] == "openalex")
            return source["accepted_observation"]["receipt_sha256"]
        self.assertNotEqual(fingerprint(output_a), fingerprint(output_b))


if __name__ == "__main__":
    unittest.main()
