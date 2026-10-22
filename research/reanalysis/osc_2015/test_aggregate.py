"""No external requests: independent negative/contract tests for the aggregate."""
import unittest
from aggregate import BYTES, BLOB_SHA, PUBLISHED, inspect_bytes, summarize

HEADER = "Local.ID,T.sign.O.131,T.sign.R.132\n"


class PublishedAggregateTests(unittest.TestCase):
    def test_frozen_published_target(self):
        self.assertEqual(PUBLISHED, {
            "paired": 100, "original": 97, "replication": 36, "both": 35
        })

    def test_pairwise_selection_and_contingency(self):
        rows = HEADER + (
            "row1,1,1\nrow2,1,0\nrow3,0,1\nrow4,0,0\nrow5,NA,0\nrow6,1,NA\n"
        )
        counts = summarize(rows)
        self.assertEqual(counts, {
            "total": 6, "paired": 4, "original": 2, "replication": 2,
            "both": 1, "original_only": 1, "replication_only": 1,
            "neither": 1, "excluded": 2
        })

    def test_reject_duplicate_identifier(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            summarize(HEADER + "a,1,1\na,1,0\n")

    def test_reject_invalid_significance(self):
        with self.assertRaisesRegex(ValueError, "unrecognized"):
            summarize(HEADER + "a,2,0\n")

    def test_reject_missing_column(self):
        with self.assertRaisesRegex(ValueError, "required"):
            summarize("Local.ID,T.sign.O.131\na,1\n")

    def test_reject_duplicate_column(self):
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            summarize("Local.ID,T.sign.O.131,T.sign.R.132,T.sign.R.132\na,1,0,0\n")

    def test_reject_empty_source(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            summarize(HEADER)

    def test_reject_unpinned_data(self):
        with self.assertRaisesRegex(ValueError, "unrecognized source"):
            inspect_bytes((HEADER + "a,1,1\n").encode())

    def test_synthetic_comparison_cannot_claim_real_study(self):
        result = inspect_bytes((HEADER + "a,1,1\n").encode(), check_source=False)
        self.assertEqual(result["status"], "MISMATCH")
        self.assertFalse(result["psychology_experiments_repeated"])
        self.assertFalse(result["source_flags_recomputed_from_raw_observations"])
        self.assertFalse(result["raw_data_archived"])
        self.assertEqual(result["counts"]["paired"], 1)

    def test_original_non_utf8_free_text_does_not_change_numeric_flags(self):
        raw = (HEADER + "row1,1,0,\n").encode("ascii").replace(b",\n", bytes([0x84]) + b"\n")
        # A non-UTF-8 byte in a valid free-text column must not break ASCII flags.
        raw = b"Local.ID,T.sign.O.131,T.sign.R.132,Notes\nrow1,1,0,\x84\n"
        result = inspect_bytes(raw, check_source=False)
        self.assertEqual(result["counts"]["paired"], 1)
        self.assertEqual(result["counts"]["original"], 1)

    def test_pinned_metadata_witness(self):
        self.assertEqual(BYTES, 288855)
        self.assertEqual(BLOB_SHA, "6c8ce0b93b9a83ac42669745bd1054da7c22a687")


if __name__ == "__main__":
    unittest.main()
