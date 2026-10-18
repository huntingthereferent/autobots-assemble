"""Falsify changed-status discovery before consuming actual original snapshots.

Every fixture in this file is invented solely to test failure boundaries;
only the dedicated CI may assert results from BOTH real whole archives.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

from systems.workspace import nih_p2_historical_status_difference_search as s

HEAD = "nct_id|overall_status|last_update_posted_date\n"
A = "NCT00000001"
B = "NCT00000002"
C = "NCT00000003"
D = "NCT00000004"
E = "NCT00000005"


@contextmanager
def fake_sources(rows22, rows23):
    with TemporaryDirectory() as td:
        folder = Path(td)
        old = folder / "2022.zip"
        new = folder / "2023.txt"
        with ZipFile(old, "w", compression=ZIP_DEFLATED) as z:
            z.writestr(s.OLD_STUDIES, HEAD + "".join(rows22))
        new.write_text(HEAD + "".join(rows23), encoding="utf8")
        with patch.object(s, "MIN_SOURCE_ROWS", 2):
            yield old, new


class HistoricalStatusDifferenceTests(unittest.TestCase):
    def test_00_normalize_only_spelling_not_semantics(self):
        self.assertEqual(s.normalize_status(" Completed "), "completed")
        self.assertNotEqual(s.normalize_status("Completed"), "Recruiting".casefold())
        for bad in ("", "  ", "invalid\nnewline", 5, "a"*100):
            with self.subTest(status=repr(bad)), self.assertRaises(ValueError):
                s.normalize_status(bad)

    def test_01_different_status_has_real_source_pair_not_version_date(self):
        with fake_sources(
            [f"{A}|Completed|2021-01-01\n", f"{B}|Recruiting|2022-03-03\n",
             f"{C}|Completed|2021-11-04\n", f"{D}|Withdrawn|2022-02-02\n"],
            [f"{A}|COMPLETED|2021-01-01\n", f"{B}|Completed|2023-06-06\n",
             f"{C}|Completed|2021-11-04\n", f"{E}|Recruiting|2023-08-05\n"]
        ) as (old,new):
            report = s.scan_verified_tables(old,new)
        self.assertEqual(report["rows_export_2022"],4)
        self.assertEqual(report["rows_export_2023"],4)
        self.assertEqual(report["common_nct_ids"],3)
        self.assertEqual(report["ids_only_2022"],1)
        self.assertEqual(report["ids_only_2023"],1)
        self.assertEqual(report["same_normalized_status_count"],2)
        self.assertEqual(report["spelling_only_difference_count"],1)
        self.assertEqual(report["different_normalized_status_count"],1)
        self.assertFalse(report["archive_collection_chronological_order_proven"])
        self.assertEqual(report["temporal_direction_of_status_field_differences"],"UNRESOLVED")
        self.assertFalse(report["underlying_extraction_date_of_2023_deposited_file_authenticated"])
        self.assertEqual(report["recorded_update_dates_comparable"],3)
        self.assertEqual(report["recorded_update_date_in_2023_deposit_is_earlier_count"],0)
        self.assertEqual([r["nct_id"] for r in report["selected_status_difference_anchors"]],[B])
        row=report["selected_status_difference_anchors"][0]
        self.assertEqual(row["overall_status_source_dated_2022_nov09"],"Recruiting")
        self.assertEqual(row["overall_status_source_deposited_2023_oct31"],"Completed")
        self.assertFalse(row["exact_original_registry_version_post_time_proven"])
        self.assertFalse(row["intervening_revisions_excluded"])
        self.assertFalse(row["actual_clinical_event_time_proven"])

    def test_02_lexical_anchor_order_frozen_not_discovery_sequence(self):
        with fake_sources(
            [f"{C}|Withdrawn|2022-03-01\n", f"{B}|Recruiting|2022-03-02\n",
             f"{A}|Not yet recruiting|2022-03-03\n"],
            [f"{C}|Completed|2023-03-01\n", f"{B}|Completed|2023-03-02\n",
             f"{A}|Recruiting|2023-03-03\n"]
        ) as (old,new):
            rows=s.scan_verified_tables(old,new,max_anchors=2)
        self.assertEqual(
            [r["nct_id"] for r in rows["selected_status_difference_anchors"]],[A,B])
        self.assertEqual(rows["different_normalized_status_count"],3)
        self.assertFalse(rows["archive_collection_chronological_order_proven"])
        self.assertEqual(sum(x["observed_paired_rows"] for x in rows["status_change_field_groups"]),3)

    def test_03_missing_duplicate_and_malformed_rows_fail(self):
        invalid=[
            ([f"{A}|Completed|2022-01-01\n",f"{A}|Recruiting|2022-03-03\n"],
             [f"{A}|Completed|2023-03-03\n",f"{B}|Recruiting|2023-03-03\n"]),
            ([f"{A}|Completed|2022-01-01\n",f"{B}|Recruiting|2022-03-03\n"],
             [f"{A}|Completed|2023-03-03\n",f"{A}|Recruiting|2023-03-03\n"]),
            ([f"{A}|Completed|2022-01-01\n",f"{B}|Recruiting|2022-03-03\n"],
             [f"{A}|Completed|2023-03-03\n",f"BADID|Recruiting|2023-03-03\n"]),
            ([f"{A}|Completed|2022-01-01\n",f"{B}|Recruiting|2022-03-03\n"],
             [f"{A}|Completed|2023-03-03\n",f"{B}|Recruiting\n"]),
        ]
        for i,(oldrows,newrows) in enumerate(invalid):
            with fake_sources(oldrows,newrows) as (old,new):
                with self.subTest(case=i),self.assertRaises(ValueError):
                    s.scan_verified_tables(old,new)
        with fake_sources([f"{A}|Completed|1\n",f"{B}|Completed|1\n"],
                          [f"{C}|Recruiting|1\n",f"{D}|Recruiting|1\n"]) as (old,new):
            with self.assertRaises(ValueError):
                s.scan_verified_tables(old,new)

    def test_04_no_two_source_check_bypasses(self):
        self.assertEqual(s.OLD_SHA,"d1d4fb04a121e03f2ac08bacef708a896f7240d5ff025104ed7512b60408d755")
        self.assertEqual(s.NEW_SHA,"bed698312a04292fc31f7ea71130731acc9b57723399ab1b45c0f6d70a304d49")
        self.assertEqual(s.ANCHOR_COUNT,8)
        self.assertGreaterEqual(s.MIN_SOURCE_ROWS,100_000)
        self.assertEqual(s.SCHEMA,"nih-p2-original-aact-two-snapshot-status-difference-search/v1")


if __name__ == "__main__":
    unittest.main()
