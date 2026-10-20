"""Pure source-admission controls; no mocked bytes are source evidence."""
from __future__ import annotations

from copy import deepcopy
import unittest

from systems.workspace import nih_aact_archival_source as owner04
from systems.workspace import nih_aact_second_2022_archive as owner09
from systems.workspace import nih_p2_independent_aact_registry_corroboration as testee
from systems.workspace import nih_p2_source_reported_posting_gate as pinned


def owner04_fixture(status="Recruiting", posted="2022-10-27"):
    return {
        "dataset_sha256": testee.NOV04_SHA,
        "dataset_md5": owner04.ARCHIVE_MD5,
        "dataset_size_bytes": 289643332,
        "observed_source_rows": {
            testee.STUDY: {
                "nct_id": testee.STUDY,
                "overall_status": status,
                "last_update_posted_date": posted,
            }
        },
    }


def owner09_fixture(status="Completed", posted="2022-11-07"):
    return {
        "entire_archive_sha256": testee.NOV09_SHA,
        "entire_archive_md5": owner09.PUBLISHED_MD5,
        "entire_archive_bytes": owner09.EXPECTED_BYTES,
        "source_study_rows": {
            testee.STUDY: {
                "nct_id": testee.STUDY,
                "overall_status": status,
                "last_update_posted_date": posted,
            }
        },
    }


class OriginalAACTCrossSourceControls(unittest.TestCase):
    def setUp(self):
        self.previous = pinned.authenticate_receipt(pinned.EVIDENCE.read_bytes())

    def test_01_pure_probe_preserves_source_owner_and_not_physical_clinical_time(self):
        result = testee.audit_source_pair(
            owner04_fixture(), owner09_fixture(), self.previous)
        self.assertEqual(result["study"], testee.STUDY)
        self.assertTrue(result["archival_status_values_differ"])
        self.assertTrue(result["archived_and_registry_status_correspondence"])
        self.assertEqual([r["owner_attested_collection_date"]
                          for r in result["original_archive_sources"]],
                         ["2022-11-04", "2022-11-09"])
        self.assertEqual(result["original_version_status_as_of_independent_archive_collection_claims"],
                         "SOURCE_OWNER_ATTESTED_ONLY")
        self.assertFalse(result["first_public_version_post_times_independently_witnessed"])
        self.assertFalse(result["archive_collection_order_independently_timestamped"])
        self.assertFalse(result["clinical_event_valid_at_authenticated"])
        self.assertFalse(result["real_historical_W13_query_admitted"])
        self.assertFalse(result["nih_phase2_completed"])
        self.assertFalse(result["original_twelve_job_runtime_modified"])
        self.assertFalse(result["third_party_archive_bodies_published"])

    def test_02_unchanged_archival_pair_does_not_invent_changed_status(self):
        r = testee.audit_source_pair(
            owner04_fixture("Completed", "2022-11-07"),
            owner09_fixture(), self.previous)
        self.assertFalse(r["archival_status_values_differ"])
        self.assertFalse(r["archived_and_registry_status_correspondence"])
        self.assertFalse(r["source_status_comparisons"][0]["status_matches_original_registry_version"])

    def test_03_archived_status_mismatch_is_preserved_not_relabelled(self):
        result = testee.audit_source_pair(
            owner04_fixture("Suspended"), owner09_fixture("Completed"), self.previous)
        self.assertTrue(result["archival_status_values_differ"])
        self.assertFalse(result["archived_and_registry_status_correspondence"])

    def test_04_wrong_identifiers_or_source_hashes_are_rejected(self):
        for field, bad in (("dataset_sha256", "0" * 64),
                           ("dataset_md5", "0" * 32),
                           ("dataset_size_bytes", 17)):
            payload = owner04_fixture()
            payload[field] = bad
            with self.subTest(source="04", field=field), self.assertRaises(ValueError):
                testee.audit_source_pair(payload, owner09_fixture(), self.previous)
        for field, bad in (("entire_archive_sha256", "0" * 64),
                           ("entire_archive_md5", "0" * 32),
                           ("entire_archive_bytes", 5)):
            payload = owner09_fixture()
            payload[field] = bad
            with self.subTest(source="09", field=field), self.assertRaises(ValueError):
                testee.audit_source_pair(owner04_fixture(), payload, self.previous)
        for which in ("04", "09"):
            a, b = owner04_fixture(), owner09_fixture()
            rows = a["observed_source_rows"] if which == "04" else b["source_study_rows"]
            row = rows.pop(testee.STUDY)
            rows["NCT99999999"] = row
            with self.subTest(source=which), self.assertRaises(ValueError):
                testee.audit_source_pair(a, b, self.previous)

    def test_05_missing_or_spoofed_version_source_rejected(self):
        prior = deepcopy(self.previous)
        prior[1]["version"] = 261
        with self.assertRaises(ValueError):
            testee.audit_source_pair(owner04_fixture(), owner09_fixture(), prior)
        prior = deepcopy(self.previous)
        prior[1]["first_public_version_timestamp_independently_authenticated"] = True
        with self.assertRaises(ValueError):
            testee.audit_source_pair(owner04_fixture(), owner09_fixture(), prior)
        prior = deepcopy(self.previous)
        prior[0]["observed_overall_status"] = "Completed"
        with self.assertRaises(ValueError):
            testee.audit_source_pair(owner04_fixture(), owner09_fixture(), prior)

    def test_06_dates_and_invalid_archive_rows_do_not_pass(self):
        for changed in ("", "2022-13-20", "2022-11-09T12:00", "2022-11-09"):
            a = owner04_fixture(posted=changed)
            with self.subTest(value=changed):
                if changed == "2022-11-09":
                    # An archived value may differ from its adjacent registry
                    # counterpart; do not throw or silently rewrite it.
                    result = testee.audit_source_pair(a, owner09_fixture(), self.previous)
                    self.assertFalse(result["source_status_comparisons"][0]["update_posted_fields_match"])
                else:
                    with self.assertRaises(ValueError):
                        testee.audit_source_pair(a, owner09_fixture(), self.previous)

    def test_07_actual_minimal_registry_receipt_has_source_ancestry(self):
        r = pinned.authenticate_receipt(pinned.EVIDENCE.read_bytes())
        self.assertEqual([a["version"] for a in r], [259, 260])
        self.assertEqual([a["observed_version_local_last_update_posted"] for a in r],
                         ["2022-10-27", "2022-11-07"])
        self.assertEqual(testee.STUDY, "NCT00001756")


if __name__ == "__main__":
    unittest.main()
