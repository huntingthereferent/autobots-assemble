"""Negative controls for independent frozen version-derived public tables.

Mocks cannot satisfy source admission; live CI separately downloads the
published full corpus and verifies its four pinned SHA-256 digests.
"""
from __future__ import annotations
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
import unittest

from systems.workspace.nih_derived_history_receipt import (
    EXPECTED_SHA256, LIMITS, RAW_ROOT, SCHEMA, TARGET,
    execute, parse_rows, source_url, verify_corpus, verify_source,
)


class IndependentDerivedHistoryTests(TestCase):
    def test_00_pinned_source_and_attribution_scope(self):
        self.assertEqual(len(EXPECTED_SHA256), 4)
        self.assertEqual(TARGET, "NCT04153409")
        self.assertIn("65a61a680eaffa8ccd6c9eeae11f1079c8d0e22e", RAW_ROOT)
        self.assertTrue(all(len(value) == 64 for value in EXPECTED_SHA256.values()))
        for name in EXPECTED_SHA256:
            self.assertTrue(source_url(name).startswith(
                "https://raw.githubusercontent.com/ByungwoongYoo/trialtrace/"))
        with self.assertRaises(ValueError):
            source_url("../../secret")

    def test_01_reject_changed_pinned_raw_source(self):
        name = "raw_event_ledger.csv"
        with self.assertRaises(ValueError):
            verify_source(name, b"tampered historical evidence")
        with self.assertRaises(ValueError):
            verify_source(name, b"x" * (LIMITS[name] + 1))
        with self.assertRaises(ValueError):
            verify_source(name, b"")

    def test_02_reject_schema_and_duplicate_headers(self):
        with self.assertRaises(ValueError):
            parse_rows(b"nct_id,nct_id\nNCT00000001,NCT00000002\n", {"nct_id"})
        with self.assertRaises(ValueError):
            parse_rows(b"field\nvalue\n", {"nct_id"})
        with self.assertRaises(ValueError):
            parse_rows(b"\xff", {"nct_id"})

    def test_03_cannot_admit_partial_mock_corpus(self):
        with self.assertRaises(ValueError):
            verify_corpus({"raw_event_ledger.csv": b"nct_id\n"})
        with self.assertRaises(ValueError):
            verify_corpus({}, target="../no")
        with self.assertRaises(ValueError):
            verify_corpus({}, target="NCT123")

    def test_04_no_receipt_on_invalid_source(self):
        with TemporaryDirectory() as td:
            def fake(_):
                return b"fake corpus"
            with self.assertRaises(ValueError):
                execute(output_dir=td, fetch=fake)
            self.assertFalse((Path(td)/"nih-p2-independent-derived-history.json").exists())


if __name__ == "__main__":
    unittest.main()
