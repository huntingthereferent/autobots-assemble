"""Negative witnesses for cross-source time claims, independent of live fetch.

Mock reports exercise strict rejection; only separate CI network downloads can
verify actual third-party archives, official current observations and hashes.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace import nih_aact_archival_source as aact
from systems.workspace import nih_derived_history_receipt as derived
from systems.workspace.nih_cross_source_relations import SCHEMA, STUDY, compare, execute


def archival():
    return {
        "schema": aact.SCHEMA,
        "entire_archive_verified_md5": aact.ARCHIVE_MD5,
        "entire_archive_sha256": "bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49",
        "archive_published_on": "2023-10-31",
        "case_count": 2,
        "exact_per_study_version_number_proven": False,
        "original_workstation_modified": False,
        "retrieved_at_utc": "2026-10-18T04:00:00Z",
        "cases": [
            {
                "nct_id": STUDY, "archive_2023_overall_status": "RECRUITING",
                "current_observed_overall_status": "COMPLETED",
                "status_values_differ": True,
                "official_current_response_sha256": "a" * 64,
            },
            {
                "nct_id": "NCT03280849", "archive_2023_overall_status": "ACTIVE_NOT_RECRUITING",
                "current_observed_overall_status": "ACTIVE_NOT_RECRUITING",
                "status_values_differ": False,
                "official_current_response_sha256": "b" * 64,
            },
        ],
    }


def history():
    return {
        "schema": derived.SCHEMA,
        "upstream_commit": derived.UPSTREAM_COMMIT,
        "source_sha256": dict(derived.EXPECTED_SHA256),
        "original_historical_payloads_available": False,
        "individual_public_posting_dates_established": False,
        "derived_corpus_is_second_archival_snapshot": False,
        "original_twelve_job_workstation_modified": False,
        "nct_id": STUDY,
        "derived_transition_count": 2,
        "upstream_author": "Byungwoong Yoo, TrialTrace",
        "upstream_data_license": "CC BY 4.0",
        "derived_transitions": [
            {"version": 1, "version_date_as_derived": "2022-01-01",
             "before_overall_status_as_derived": "RECRUITING",
             "after_overall_status_as_derived": "ACTIVE_NOT_RECRUITING"},
            {"version": 2, "version_date_as_derived": "2025-01-01",
             "before_overall_status_as_derived": "ACTIVE_NOT_RECRUITING",
             "after_overall_status_as_derived": "COMPLETED"},
        ],
    }


class CrossSourceRelationTests(unittest.TestCase):
    def test_00_descriptive_join_must_not_assert_temporal_identity(self):
        report = compare(archival(), history())
        self.assertEqual(report["schema"], SCHEMA)
        self.assertEqual(report["nct_id"], STUDY)
        self.assertTrue(report["current_status_differs_from_archived"])
        self.assertEqual(report["spelling_matches"]["historical_2023_to_derived_count"], 1)
        self.assertEqual(report["spelling_matches"]["current_to_derived_count"], 1)
        self.assertFalse(report["historical_status_corresponds_to_unique_version"])
        self.assertFalse(report["public_posting_time_of_change_known"])
        self.assertFalse(report["two_independent_original_historical_snapshots_available"])
        self.assertFalse(report["historical_record_contents_independently_authenticated"])
        self.assertFalse(report["official_NIH_submission"])
        self.assertTrue(all(not x["public_posting_of_this_version_independently_verified"]
                            for x in report["derived_history_status_occurrences"]))

    def test_01_reject_changed_archival_hash_and_witnesses(self):
        for key, change in (
            ("entire_archive_sha256", "0" * 64),
            ("archive_published_on", "2022-01-01"),
            ("original_workstation_modified", True),
            ("exact_per_study_version_number_proven", True),
        ):
            a = archival()
            a[key] = change
            with self.subTest(field=key), self.assertRaises(ValueError):
                compare(a, history())

    def test_02_reject_changed_derived_digest_and_false_source_claim(self):
        for key, value in (
            ("source_sha256", {"raw_event_ledger.csv": "0" * 64}),
            ("original_historical_payloads_available", True),
            ("individual_public_posting_dates_established", True),
            ("derived_corpus_is_second_archival_snapshot", True),
            ("nct_id", "NCT12345678"),
        ):
            d = history()
            d[key] = value
            with self.subTest(field=key), self.assertRaises(ValueError):
                compare(archival(), d)

    def test_03_refuse_duplicate_or_missing_study_id_and_false_diff(self):
        a = archival()
        a["cases"][1]["nct_id"] = STUDY
        with self.assertRaises(ValueError):
            compare(a, history())
        a = archival()
        a["cases"][0]["nct_id"] = "NCT99999999"
        with self.assertRaises(ValueError):
            compare(a, history())
        a = archival()
        a["cases"][0]["status_values_differ"] = False
        with self.assertRaises(ValueError):
            compare(a, history())

    def test_04_wrong_derived_version_and_absent_status_rejected(self):
        d = history()
        d["derived_transitions"][1]["version"] = 1
        with self.assertRaises(ValueError):
            compare(archival(), d)
        d = history()
        for item in d["derived_transitions"]:
            item["before_overall_status_as_derived"] = None
            item["after_overall_status_as_derived"] = None
        with self.assertRaises(ValueError):
            compare(archival(), d)

    def test_05_execution_preserves_receipt_and_never_creates_on_failure(self):
        def source(*, output_dir, now):
            return archival()
        def from_history(*, output_dir, now):
            return history()
        with TemporaryDirectory() as td:
            report = execute(output_dir=td, aact_runner=source,
                             derived_runner=from_history,
                             now=datetime(2026, 10, 18, tzinfo=timezone.utc))
            self.assertEqual(report["schema"], SCHEMA)
            self.assertTrue((Path(td) / "nih-p2-cross-source-relations.json").is_file())
        with TemporaryDirectory() as td:
            def bad(*, output_dir, now):
                data = history()
                data["source_sha256"] = {}
                return data
            with self.assertRaises(ValueError):
                execute(output_dir=td, aact_runner=source, derived_runner=bad)
            self.assertFalse((Path(td) / "nih-p2-cross-source-relations.json").exists())


if __name__ == "__main__":
    unittest.main()
