"""Negative controls for two independently checksum-authenticated AACT archives.

Mocks are ONLY falsification controls. Live CI must re-download and independently
reverify both entire 236 MB/289 MB sources before admitting paired observations.
"""
from __future__ import annotations

from copy import deepcopy
import unittest

from systems.workspace import nih_aact_second_2022_archive as a22
from systems.workspace import nih_aact_archival_source as a23
from systems.workspace.nih_p2_two_aact_snapshot_comparison import (
    SCHEMA, OLD_SHA, NEW_SHA, compare, IDS,
)


def old_report():
    return {
        "schema": a22.SCHEMA,
        "entire_archive_md5": a22.PUBLISHED_MD5,
        "entire_archive_sha256": OLD_SHA,
        "entire_archive_bytes": a22.EXPECTED_BYTES,
        "upstream_stated_dataset_date": "2022-11-09",
        "deposit_publication_date": "2023-11-09",
        "deposit_doi": a22.DEPOSIT_DOI,
        "archive_member_layout": "direct-studies-table",
        "direct_studies_table_member": "AACT-2022-11-09/studies.txt",
        "study_rows_examined": 432983,
        "per_version_original_public_posting_date_proven": False,
        "original_twelve_job_workstation_modified": False,
        "selected_study_records": {
            "NCT03280849": {
                "nct_id": "NCT03280849", "overall_status_2022": "Completed",
                "study_last_update_posted_date_2022": "2019-03-14",
            },
            "NCT04153409": {
                "nct_id": "NCT04153409", "overall_status_2022": "Completed",
                "study_last_update_posted_date_2022": "2021-04-28",
            },
        },
    }


def new_report():
    return {
        "dataset_md5": a23.ARCHIVE_MD5,
        "dataset_sha256": NEW_SHA,
        "dataset_size_bytes": 289643332,
        "scanned_physical_csv_rows": 400000,
        "observed_source_rows": {
            "NCT03280849": {
                "nct_id": "NCT03280849", "overall_status": "Completed",
                "last_update_posted_date": "2019-03-14",
            },
            "NCT04153409": {
                "nct_id": "NCT04153409", "overall_status": "Completed",
                "last_update_posted_date": "2021-04-28",
            },
        },
    }


class PairwiseSourceTests(unittest.TestCase):
    def test_00_exact_join_does_not_invent_intervening_version_history(self):
        r = compare(old_report(), new_report())
        self.assertEqual(r["schema"], SCHEMA)
        self.assertEqual(r["cross_source_nct_count"], 2)
        self.assertEqual(r["same_recorded_status_count"], 2)
        self.assertEqual(r["different_recorded_status_count"], 0)
        self.assertFalse(r["missing_intervening_record_changes_ruled_out"])
        self.assertFalse(r["historical_per_study_first_publication_time_authenticated"])
        self.assertFalse(r["historical_per_study_source_version_contents_authenticated"])
        self.assertFalse(r["original_twelve_job_workstation_modified"])
        self.assertFalse(r["official_NIH_submission"])

    def test_01_reject_modified_source_hashes_identifiers_and_dated_claims(self):
        for key, value in (
            ("entire_archive_md5", "0" * 32),
            ("entire_archive_sha256", "0" * 64),
            ("entire_archive_bytes", 10),
            ("upstream_stated_dataset_date", "2023-11-09"),
            ("deposit_publication_date", "2022-11-09"),
            ("direct_studies_table_member", "imagined/studies.txt"),
            ("per_version_original_public_posting_date_proven", True),
        ):
            a = old_report()
            a[key] = value
            with self.subTest(field=key), self.assertRaises(ValueError):
                compare(a, new_report())
        for key, value in (
            ("dataset_md5", "0" * 32),
            ("dataset_sha256", "0" * 64),
            ("dataset_size_bytes", 1),
        ):
            b = new_report()
            b[key] = value
            with self.subTest(field=key), self.assertRaises(ValueError):
                compare(old_report(), b)

    def test_02_no_missing_extra_or_misassigned_nct_ids(self):
        for side in ("old", "new"):
            a, b = old_report(), new_report()
            field = "selected_study_records" if side == "old" else "observed_source_rows"
            source = a if side == "old" else b
            del source[field][IDS[0]]
            with self.subTest(side=side), self.assertRaises(ValueError):
                compare(a, b)
        a = old_report()
        a["selected_study_records"][IDS[0]]["nct_id"] = IDS[1]
        with self.assertRaises(ValueError):
            compare(a, new_report())

    def test_03_true_changed_status_not_silently_marked_same(self):
        b = new_report()
        b["observed_source_rows"][IDS[0]]["overall_status"] = "Recruiting"
        report = compare(old_report(), b)
        self.assertEqual(report["different_recorded_status_count"], 1)
        case = next(x for x in report["observations"] if x["nct_id"] == IDS[0])
        self.assertTrue(case["status_value_difference_between_exports"])
        self.assertFalse(case["exact_date_of_intervening_change_proven"])

    def test_04_same_status_does_not_claim_no_intervening_changes(self):
        a, b = old_report(), new_report()
        b["observed_source_rows"][IDS[0]]["last_update_posted_date"] = "2023-08-21"
        report = compare(a, b)
        row = next(x for x in report["observations"] if x["nct_id"] == IDS[0])
        self.assertTrue(row["status_spelling_equal"])
        self.assertFalse(row["recorded_last_update_posted_value_equal"])
        self.assertFalse(row["any_intervening_status_revisions_excluded"])

    def test_05_empty_status_is_not_an_observation(self):
        b = new_report()
        b["observed_source_rows"][IDS[0]]["overall_status"] = ""
        with self.assertRaises(ValueError):
            compare(old_report(), b)


if __name__ == "__main__":
    unittest.main()
