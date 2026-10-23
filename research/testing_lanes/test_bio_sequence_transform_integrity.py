"""Offline controls for BIO-SEQUENCE-TRANSFORM-INTEGRITY-001."""
import unittest

from bio_sequence_transform_integrity import build_receipt, parse_fasta, reverse_complement


class BioSequenceTransformTests(unittest.TestCase):
    def test_reverse_complement_is_involution(self):
        for sequence in ("ACGT", "AACCGGTT", "NNACGTN", "GATTACA"):
            self.assertEqual(reverse_complement(reverse_complement(sequence)), sequence)

    def test_length_and_gc_count_are_preserved(self):
        sequence = "AAACCCGGGTTTNN"
        transformed = reverse_complement(sequence)
        self.assertEqual(len(transformed), len(sequence))
        self.assertEqual(transformed.count("G") + transformed.count("C"),
                         sequence.count("G") + sequence.count("C"))

    def test_rejects_unsupported_symbols(self):
        for sequence in ("ACGTX", "ACGU", ""):
            with self.assertRaises(ValueError):
                reverse_complement(sequence)

    def test_rejects_multiple_fasta_records(self):
        with self.assertRaisesRegex(ValueError, "multiple"):
            parse_fasta(">NC_012920.1\nACGT\n>OTHER\nTTAA")

    def test_receipt_pins_accession_and_reports_invariants(self):
        sequence = "ACGT" * 4000
        raw = (">NC_012920.1 synthetic test fixture\n" +
               "\n".join(sequence[i:i + 80] for i in range(0, len(sequence), 80)) +
               "\n").encode("utf-8")
        receipt = build_receipt(raw)
        self.assertEqual(receipt["source"]["accession"], "NC_012920.1")
        self.assertTrue(receipt["measurements"]["reverse_complement_is_involution"])
        self.assertTrue(receipt["measurements"]["length_preserved"])
        self.assertTrue(receipt["measurements"]["gc_count_preserved"])

    def test_receipt_rejects_wrong_accession(self):
        raw = (">WRONG_ACCESSION\n" + "ACGT" * 4000 + "\n").encode("utf-8")
        with self.assertRaisesRegex(ValueError, "does not match"):
            build_receipt(raw)


if __name__ == "__main__":
    unittest.main()
