"""Phase 1 comparison must never invent a winner from missing receipts."""
import json
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from systems.workspace.nih_phase1_output_compare import compare, CANDIDATES


class OutputComparisonTests(unittest.TestCase):
    def test_no_receipts_no_winner(self):
        with TemporaryDirectory() as directory:
            result = compare(directory)
        self.assertEqual(result["selection"], "UNDETERMINED")
        self.assertEqual(result["shared_capabilities"], [])
        self.assertEqual(result["capability_maximal_candidates_unverified"], [])
        self.assertTrue(all(x["status"] == "UNKNOWN" for x in result["candidates"].values()))

    def test_receipt_is_not_independent_verification(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "frontier" / CANDIDATES["frontier"][0]
            path.parent.mkdir()
            doc = {"schema": CANDIDATES["frontier"][1]}
            doc.update(dict(CANDIDATES["frontier"][2:]))
            path.write_text(json.dumps(doc), encoding="utf-8")
            (path.parent / "exit-code.txt").write_text("0", encoding="utf-8")
            result = compare(directory)
        self.assertEqual(result["candidates"]["frontier"]["status"], "REPORTED_PASS")
        self.assertEqual(result["candidates"]["frontier"]["receipt_sha256"], sha256(json.dumps(doc).encode("utf-8")).hexdigest())
        self.assertEqual(result["selection"], "UNDETERMINED")
        self.assertEqual(result["candidates"]["two_clock"]["status"], "UNKNOWN")
        self.assertEqual(result["shared_capabilities"], ["known-time-frontier"])
        self.assertEqual(result["capability_maximal_candidates_unverified"], ["frontier"])

    def test_nonzero_exit_cannot_become_pass(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "frontier" / CANDIDATES["frontier"][0]
            path.parent.mkdir()
            doc = {"schema": CANDIDATES["frontier"][1]}
            doc.update(dict(CANDIDATES["frontier"][2:]))
            path.write_text(json.dumps(doc), encoding="utf-8")
            (path.parent / "exit-code.txt").write_text("1", encoding="utf-8")
            result = compare(directory)
        self.assertEqual(result["candidates"]["frontier"]["status"], "REPORTED_FAIL")
        self.assertFalse(result["candidates"]["frontier"]["checks"]["process_exit_zero"])

    def test_invalid_claim_is_rejected(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "frontier" / CANDIDATES["frontier"][0]
            path.parent.mkdir()
            path.write_text('{"schema":"not-the-original"}', encoding="utf-8")
            result = compare(directory)
        self.assertEqual(result["candidates"]["frontier"]["status"], "REPORTED_FAIL")


if __name__ == "__main__":
    unittest.main()
