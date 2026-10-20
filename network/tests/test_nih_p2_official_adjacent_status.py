"""Negative controls for exact adjacent original ClinicalTrials.gov versions."""
from __future__ import annotations

from copy import deepcopy
from unittest import TestCase

from systems.workspace import nih_p2_official_adjacent_status as p

STAMP = "2026-10-20T13:00:00+00:00"


def page(version: int, observed_status: str) -> str:
    submitted = p.VERSIONS[version]
    updated = "2022-10-27" if version == 259 else "2022-11-07"
    return f"""NCT00001756 {p.source.TITLE}
Current Study
Overall Status
Completed
Last Update Posted
2024-01-01 [Actual]
Record History
Study Record Versions
259 2022-10-26 Study Status
260 2022-11-04 Recruitment Status
Viewing V{version} ({submitted})
Study Details
Study Identification
Protocol ID
NCT00001756
Study Status
Overall Status
{observed_status}
Last Update Submitted that Met QC Criteria
{submitted}
Last Update Posted
{updated} [Actual]
Sponsor/Collaborators
STOP
"""


def original(version: int, status: str) -> dict:
    return p.admit_source(
        version=version, url=p.version_url(version),
        body=page(version, status), status=200,
        retrieved_utc=STAMP,
    )


class AdjacentOriginalStatusTests(TestCase):
    def test_01_exact_pair_observed_and_no_public_time_assumed(self):
        result = p.summarize([original(259, "Recruiting"), original(260, "Completed")])
        self.assertEqual([r["version"] for r in result["records"]], [259, 260])
        self.assertTrue(result["adjacent_version_pair_checked"])
        self.assertTrue(result["observed_status_changed"])
        self.assertFalse(result["known_at_admitted_to_W13"])
        self.assertEqual(result["first_public_version_timestamp"], "UNAVAILABLE")
        self.assertFalse(result["historical_temporal_benchmark_completed"])

    def test_02_equal_status_is_a_supported_result(self):
        result = p.summarize([original(259, "Completed"), original(260, "Completed")])
        self.assertTrue(result["two_original_version_fields_witnessed"])
        self.assertFalse(result["observed_status_changed"])
        self.assertFalse(result["original_twelve_job_W13_modified"])

    def test_03_current_summary_is_not_selected_history(self):
        row = original(259, "Recruiting")
        self.assertEqual(row["observed_overall_status"], "Recruiting")
        self.assertEqual(row["observed_version_local_last_update_posted"], "2022-10-27")
        self.assertNotEqual(row["observed_version_local_last_update_posted"], "2024-01-01")

    def test_04_wrong_or_missing_source_is_not_admitted(self):
        body = page(259, "Recruiting")
        for url in (
            "https://clinicaltrials.gov/study/NCT00001756?a=260&tab=history",
            "https://clinicaltrials.gov/study/NCT00001756?a=259&a=260&tab=history",
            "https://clinicaltrials.gov/study/NCT00001756?a=259&tab=details",
            "https://other.example/study/NCT00001756?a=259&tab=history",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                p.admit_source(version=259, url=url, body=body, status=200,
                               retrieved_utc=STAMP)
        with self.assertRaises(ValueError):
            p.admit_source(version=259, url=p.version_url(259), body=body,
                           status=403, retrieved_utc=STAMP)

    def test_05_changed_submission_or_duplicate_status_is_refused(self):
        body = page(259, "Recruiting")
        variants = (
            body.replace("Viewing V259 (2022-10-26)", "Viewing V259 (2022-10-25)"),
            body.replace("Viewing V259 (", "Viewing V2590 ("),
            body.replace("Study Status\nOverall Status\nRecruiting",
                         "Study Status\nOverall Status\nRecruiting\nOverall Status\nCompleted"),
            body.replace("2022-10-27 [Actual]", "2022-10-25 [Actual]"),
        )
        for changed in variants:
            with self.subTest(change=changed[-90:]), self.assertRaises(ValueError):
                p.admit_source(version=259, url=p.version_url(259),
                               body=changed, status=200, retrieved_utc=STAMP)

    def test_06_missing_pair_or_imaginary_first_public_date_is_rejected(self):
        a, b = original(259, "Recruiting"), original(260, "Completed")
        with self.assertRaises(ValueError):
            p.summarize([a])
        with self.assertRaises(ValueError):
            p.summarize([a, a])
        forged = deepcopy(b)
        forged["first_public_version_timestamp_independently_authenticated"] = True
        with self.assertRaises(ValueError):
            p.summarize([a, forged])
        unavailable = p.summarize([a, {
            "version": 260, "original_version_fields_witnessed": False,
            "first_public_version_timestamp_independently_authenticated": False,
            "result": "UNAVAILABLE",
        }])
        self.assertFalse(unavailable["two_original_version_fields_witnessed"])
        self.assertIsNone(unavailable["observed_status_changed"])


if __name__ == "__main__":
    import unittest
    unittest.main()
