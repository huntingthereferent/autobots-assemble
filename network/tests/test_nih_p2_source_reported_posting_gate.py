"""Falsify promoted known_at, altered original receipts and fake posting semantics."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from unittest import TestCase
from unittest.mock import patch

from systems.workspace import nih_p2_source_reported_posting_gate as gate

# Synthetic offline response for *negative* tests only. Never external evidence.
DEFINITION = b"""<html><body>Changes to Record Date Fields.
The Last Update Posted field is defined as the most recent date on which
changes to a study record were posted on ClinicalTrials.gov - that is,
when updated study information is publicly available.
However, delays sometimes occur between submission and public posting;
delays sometimes occur for updates to a study record.</body></html>"""
STAMP = "2026-10-20T13:00:00+00:00"


def semantic_fixture():
    return gate.inspect_nlm_html(DEFINITION, observed_utc=STAMP)


class SourcePostingBoundaryTests(TestCase):
    def test_01_actual_original_minimal_receipt_has_exact_artifact_digest(self):
        raw = gate.EVIDENCE.read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), gate.PINNED_RECEIPT_SHA256)
        pair = gate.authenticate_receipt(raw)
        self.assertEqual([r["version"] for r in pair], [259, 260])
        self.assertEqual([r["observed_overall_status"] for r in pair],
                         ["Recruiting", "Completed"])
        self.assertEqual([r["observed_version_local_last_update_posted"] for r in pair],
                         ["2022-10-27", "2022-11-07"])
        self.assertFalse(any(r["first_public_version_timestamp_independently_authenticated"]
                             for r in pair))

    def test_02_any_change_to_original_source_receipt_fails_closed(self):
        original = gate.EVIDENCE.read_bytes()
        self.assertRaises(ValueError, gate.authenticate_receipt,
                          original.replace(b"Recruiting", b"Completed "))
        self.assertRaises(ValueError, gate.authenticate_receipt,
                          original.replace(b"2022-11-07", b"2022-11-06"))
        self.assertRaises(ValueError, gate.authenticate_receipt, original + b" ")

    def test_03_only_real_official_definition_semantics_is_admissible(self):
        witness = semantic_fixture()
        self.assertTrue(witness["source_defines_last_update_posted_as_public_availability"])
        self.assertEqual(witness["source_url"], gate.NLM_URL)
        self.assertFalse(witness["original_version_first_public_observed_from_this_source"])
        self.assertEqual(len(witness["response_sha256"]), 64)
        for bad in (b"", b"<html>Last Update Posted</html>",
                    b"Last Update Posted public availability; delays sometimes occur"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                gate.inspect_nlm_html(bad, observed_utc=STAMP)

    def test_04_conditional_source_posting_as_of_cutoffs(self):
        results = gate.movement(gate.authenticate_receipt(gate.EVIDENCE.read_bytes()),
                                semantic_fixture())
        got = [(r["cutoff"], r["selected_version_if_source_reported_posting_is_used"],
                r["selected_status_if_source_reported_posting_is_used"],
                r["future_version_ids_withheld_under_this_assumption"])
               for r in results["conditional_comparisons"]]
        self.assertEqual(got, [
            ("2022-10-26", None, "UNAVAILABLE", [259, 260]),
            ("2022-10-27", 259, "Recruiting", [260]),
            ("2022-11-06", 259, "Recruiting", [260]),
            ("2022-11-07", 260, "Completed", []),
            ("2022-11-08", 260, "Completed", []),
        ])
        self.assertEqual(results["interpretation"],
                         "source-reported-posting-date-conditional-only")
        for negative in ("original_version_first_public_independently_authenticated",
                         "known_at_admitted_to_original_W13",
                         "clinical_fact_valid_at_authenticated",
                         "NIH_phase2_real_temporal_benchmark_completed",
                         "original_W13_journal_modified",
                         "source_original_bodies_copied"):
            self.assertFalse(results[negative])

    def test_05_forged_external_semantics_or_claim_promotions_rejected(self):
        pair = gate.authenticate_receipt(gate.EVIDENCE.read_bytes())
        sem = semantic_fixture()
        for mutate in (
            {"source_url": "https://example.org/forged"},
            {"source_defines_last_update_posted_as_public_availability": False},
            {"original_version_first_public_observed_from_this_source": True},
            {"response_sha256": "not-a-hash"},
        ):
            changed = {**sem, **mutate}
            with self.subTest(changed=mutate), self.assertRaises(ValueError):
                gate.movement(pair, changed)

    def test_06_missing_official_network_witness_cannot_claim_success(self):
        with self.assertRaises(ValueError):
            gate.run(live=False)
        with patch.object(gate, "live_nlm", side_effect=ValueError("NLM offline")):
            with self.assertRaises(ValueError):
                gate.run(live=True)

    def test_07_scope_cannot_claim_clinical_event_when_registry_record_changes(self):
        result = gate.movement(gate.authenticate_receipt(gate.EVIDENCE.read_bytes()),
                               semantic_fixture())
        self.assertEqual([e["historical_record_valid_at"]
                          for e in result["source_version_events"]], ["UNAVAILABLE"] * 2)
        self.assertEqual([e["independent_version_first_public_timestamp"]
                          for e in result["source_version_events"]], ["UNAVAILABLE"] * 2)
        self.assertEqual([r["unknown_clinical_valid_at"] for r in
                          result["conditional_comparisons"]], [True] * 5)


if __name__ == "__main__":
    import unittest
    unittest.main()
