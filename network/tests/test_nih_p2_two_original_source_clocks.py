"""Independent original source-clock admission and negative controls.

Mocked selectors here are ONLY tests. The original-source integration uses
actual successful GitHub Actions receipts fetched from runs 39421372666 and
39424382213. No clinical valid_at is created from a posted date.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import unittest

from systems.workspace import nih_p2_two_original_source_clocks as source
from systems.workspace import nih_p2_source_reported_posting_gate as old

REGISTRY = os.environ.get("NIH_P2_ORIGINAL_REGISTRY_JSON")
AACT = os.environ.get("NIH_P2_ORIGINAL_AACT_JSON")


def actual_bytes():
    if not REGISTRY or not AACT:
        raise RuntimeError("dedicated CI must supply both original source artifacts")
    return Path(REGISTRY).read_bytes(), Path(AACT).read_bytes()


class SourceClockTest(unittest.TestCase):
    def test_01_original_registry_records_are_distinct_real_versions(self):
        v = old.authenticate_receipt(old.EVIDENCE.read_bytes())
        self.assertEqual([x["version"] for x in v], [259, 260])
        self.assertEqual([x["observed_overall_status"] for x in v],
                         ["Recruiting", "Completed"])
        self.assertEqual([x["observed_version_local_last_update_posted"] for x in v],
                         ["2022-10-27", "2022-11-07"])

    def test_02_conditional_not_clinical_source_as_of(self):
        v = old.authenticate_receipt(old.EVIDENCE.read_bytes())
        got = [source.conditional_source_status(v, at) for at in source.CUTOFFS]
        self.assertEqual([x["conditional_recorded_status"] for x in got], [
            "UNAVAILABLE", "Recruiting", "Recruiting", "Recruiting",
            "Completed", "Completed",
        ])
        self.assertEqual([x["conditional_visible_registry_version"] for x in got],
                         [None, 259, 259, 259, 260, 260])
        self.assertEqual([x["static_latest_leaks_future_source_version"] for x in got],
                         [True, True, True, True, False, False])
        self.assertTrue(all(x["clinical_valid_at"] == "UNAVAILABLE" for x in got))
        self.assertTrue(all(x["original_version_first_public_authentication"] ==
                            "UNAVAILABLE" for x in got))

    def test_03_invalid_time_and_missing_version_are_rejected(self):
        original = old.authenticate_receipt(old.EVIDENCE.read_bytes())
        for d in ("2022-02-30", "2022-11-07T00:00:00", "2022-11", "", None):
            with self.subTest(cutoff=d), self.assertRaises((ValueError, TypeError)):
                source.conditional_source_status(original, d)
        for changes in (
            list(reversed(original)),
            original[:1],
            [{**original[0], "version": 260}, original[1]],
        ):
            with self.assertRaises(ValueError):
                source.conditional_source_status(changes, "2022-11-07")

    @unittest.skipUnless(REGISTRY and AACT, "needs original GitHub source artifacts")
    def test_04_two_original_artifact_bytes_and_source_lineage(self):
        registry, aact = actual_bytes()
        self.assertEqual(source._sha(registry), source.REGISTRY_JSON_SHA256)
        self.assertEqual(source._sha(aact), source.AACT_JSON_SHA256)
        a, b = source.admit(registry, aact)
        self.assertEqual(len(a), 2)
        self.assertTrue(b["archived_and_registry_status_correspondence"])
        self.assertEqual([r["overall_status"] for r in
                          b["observed_original_archival_rows"]],
                         ["Recruiting", "Completed"])
        self.assertEqual(b["registry_version_source"]["artifact_id"], 12264180158)

    @unittest.skipUnless(REGISTRY and AACT, "needs original GitHub source artifacts")
    def test_05_original_artifact_mutations_refused(self):
        registry, archive = actual_bytes()
        bad = (
            (registry + b" ", archive),
            (registry.replace(b"Recruiting", b"Completed "), archive),
            (registry, archive + b" "),
            (registry, archive.replace(b"2022-11-07", b"2022-11-06")),
            (registry, archive.replace(b"NCT00001756", b"NCT99999999")),
        )
        for i, item in enumerate(bad):
            with self.subTest(case=i), self.assertRaises(ValueError):
                source.admit(*item)

    @unittest.skipUnless(REGISTRY and AACT, "needs original GitHub source artifacts")
    def test_06_two_independent_source_oracle_controls_match(self):
        registry, archive = actual_bytes()
        result = source.observe(registry, archive)
        controls = result["independent_aact_owner_attested_archive_checks"]
        self.assertEqual([r["owner_attested_collection_day"] for r in controls],
                         ["2022-11-04", "2022-11-09"])
        # Independent AACT archive rows—not the registry projection—supply
        # the oracle statuses for the two source-owner-claimed collection days.
        self.assertEqual([r["actual_original_deposited_archive_status"] for r in controls],
                         ["Recruiting", "Completed"])
        self.assertEqual([r["source_reported_clock_selected_status"] for r in controls],
                         ["Recruiting", "Completed"])
        self.assertTrue(result["archive_controls_match_both_source_statuses"])
        self.assertTrue(all(r["source_families_agree_on_recorded_status"] for r in controls))
        self.assertTrue(all(r["original_archive_is_time_authority"] is False
                            for r in controls))

    @unittest.skipUnless(REGISTRY and AACT, "needs original GitHub source artifacts")
    def test_07_no_real_w13_or_clinical_validity_promotion(self):
        result = source.observe(*actual_bytes())
        for key in (
            "real_as_known_at_independently_authenticated",
            "real_clinical_valid_at_known",
            "historical_NIH_P2_benchmark_completed",
            "original_W13_journal_modified",
            "World48_required",
            "source_archive_bodies_redistributed",
        ):
            self.assertIs(result[key], False, key)
        self.assertIs(result["this_is_not_original_W13_temporal_python_execution"], True)
        self.assertEqual(result["conditional_assumption"],
                         "source-reported-last-update-posted-only")
        for version in result["original_source_version_observations"]:
            self.assertEqual(version["clinical_valid_at"], "UNAVAILABLE")
            self.assertEqual(version["first_public_version_at"], "UNAVAILABLE")

    @unittest.skipUnless(REGISTRY and AACT, "needs original GitHub source artifacts")
    def test_08_clinical_and_source_observation_clocks_do_not_collapse(self):
        result = source.observe(*actual_bytes())
        original_v = result["original_source_version_observations"]
        self.assertTrue(all(r["source_retrieved_utc"].startswith("2026-10-20T")
                            for r in original_v))
        self.assertTrue(all(r["source_reported_posted_date"][:4] == "2022"
                            for r in original_v))
        self.assertTrue(all(r["clinical_valid_at"] == "UNAVAILABLE"
                            for r in original_v))
        self.assertFalse(result["real_as_known_at_independently_authenticated"])


if __name__ == "__main__":
    unittest.main()
