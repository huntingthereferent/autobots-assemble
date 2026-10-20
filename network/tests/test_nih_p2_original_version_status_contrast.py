"""Falsify false changed status and contemporary-header contamination."""
from __future__ import annotations

from copy import deepcopy
from unittest import TestCase
from systems.workspace import nih_p2_original_version_status_contrast as p

OBSERVED = "2026-10-20T12:00:00+00:00"


def body(version, status):
    submitted = p.VERSIONS[version]
    posted = "2019-11-25" if version == 105 else "2022-11-07"
    return f"""NCT00001756 {p.source.TITLE}
Completed
Current Study Status
Overall Status
Completed
Last Update Posted
2022-11-07 [Actual]
Record History
Study Record Versions
Version Date submitted
105 2019-11-22 Study Status
260 2022-11-04 Recruitment Status
Viewing V{version} ({submitted})
Study Details
Study Identification
Protocol ID
123456
Study Status
Overall Status
{status}
Last Update Submitted that Met QC Criteria
{submitted}
Last Update Posted
{posted} [Actual]
Sponsor/Collaborators
No copied sponsor details
"""


def record(version, status):
    return p.admit_source(version=version, url=p.version_url(version),
                          body=body(version, status), status=200,
                          retrieved_utc=OBSERVED)


class RealSourceContrastControls(TestCase):
    def test_01_two_original_versions_differ_in_declared_positive_control(self):
        result = p.summarize([record(105, "Recruiting"), record(260, "Completed")])
        self.assertTrue(result["two_original_version_fields_witnessed"])
        self.assertTrue(result["observed_status_changed"])
        self.assertFalse(result["known_at_admitted_to_W13"])
        self.assertEqual(result["first_public_version_timestamp"], "UNAVAILABLE")
        self.assertFalse(result["historical_temporal_benchmark_completed"])

    def test_02_same_status_is_not_declared_different(self):
        x = p.summarize([record(105, "Recruiting"), record(260, "Recruiting")])
        self.assertFalse(x["observed_status_changed"])
        self.assertNotEqual(x["records"][0]["source_url"], x["records"][1]["source_url"])

    def test_03_current_header_does_not_override_selected_version(self):
        row = record(105, "Recruiting")
        self.assertEqual(row["observed_overall_status"], "Recruiting")
        self.assertEqual(row["observed_version_local_last_update_posted"], "2019-11-25")
        self.assertEqual(row["submitted_in_original_selected_version"], "2019-11-22")
        self.assertFalse(row["first_public_version_timestamp_independently_authenticated"])

    def test_04_wrong_original_route_and_status_cannot_be_admitted(self):
        for bad in (
            "https://clinicaltrials.gov/study/NCT00001756?a=260&a=105&tab=history",
            "https://clinicaltrials.gov/study/NCT00001756?a=105&tab=details",
            "https://attacker.example/study/NCT00001756?a=105&tab=history",
            "https://clinicaltrials.gov/study/NCT00001756?tab=history",
        ):
            with self.subTest(url=bad), self.assertRaises(ValueError):
                p.admit_source(version=105, url=bad, body=body(105, "Recruiting"),
                               status=200, retrieved_utc=OBSERVED)
        for version in (0, 94, 261, "105", None):
            with self.subTest(version=version), self.assertRaises(ValueError):
                p.version_url(version)
        with self.assertRaises(ValueError):
            p.admit_source(version=105, url=p.version_url(105),
                           body=body(105, "Recruiting"), status=403,
                           retrieved_utc=OBSERVED)

    def test_05_wrong_banner_and_submitted_version_are_rejected(self):
        original = body(260, "Completed")
        for changed in (
            original.replace("Viewing V260 (", "Viewing V2600 ("),
            original.replace("Viewing V260 (2022-11-04)", "Viewing V260 (2022-11-05)"),
            original + "\nViewing V260 (2022-11-04)",
        ):
            with self.subTest(change=changed[-100:]), self.assertRaises(ValueError):
                p.admit_source(version=260, url=p.version_url(260),
                               body=changed, status=200, retrieved_utc=OBSERVED)

    def test_06_duplicate_status_or_missing_selected_status_rejected(self):
        orig = body(105, "Recruiting")
        for value in (
            orig.replace("Study Status\nOverall Status\nRecruiting",
                         "Study Status\nOverall Status\nRecruiting\nOverall Status\nCompleted"),
            orig.replace("Study Status\nOverall Status\nRecruiting",
                         "Study Status\nRecruiting"),
            orig.replace("Study Status\nOverall Status\nRecruiting",
                         "Study Status\nOverall Status\nUnknown made-up status"),
        ):
            with self.subTest(value=value[-80:]), self.assertRaises(ValueError):
                p.admit_source(version=105, url=p.version_url(105),
                               body=value, status=200, retrieved_utc=OBSERVED)

    def test_07_invalid_dates_cannot_become_known_at(self):
        original = body(105, "Recruiting")
        for changed in (
            original.replace("2019-11-25 [Actual]", "2019-11-21 [Actual]"),
            original.replace("2019-11-25 [Actual]", "2019-02-30 [Actual]"),
            original.replace("2019-11-25 [Actual]", "2027-01-01 [Actual]"),
            original.replace("2019-11-25 [Actual]", "2019-11-25"),
        ):
            with self.subTest(value=changed[-100:]), self.assertRaises(ValueError):
                p.admit_source(version=105, url=p.version_url(105),
                               body=changed, status=200, retrieved_utc=OBSERVED)

    def test_08_missing_source_or_forged_first_public_time_cannot_pass(self):
        old = record(105, "Recruiting")
        future = record(260, "Completed")
        forged = deepcopy(future)
        forged["first_public_version_timestamp_independently_authenticated"] = True
        with self.assertRaises(ValueError):
            p.summarize([old, forged])
        with self.assertRaises(ValueError):
            p.summarize([old, old])
        with self.assertRaises(ValueError):
            p.summarize([old])
        blocked = p.summarize([
            old, {"version": 260, "original_version_fields_witnessed": False,
                  "first_public_version_timestamp_independently_authenticated": False,
                  "result": "UNAVAILABLE"},
        ])
        self.assertFalse(blocked["two_original_version_fields_witnessed"])
        self.assertIsNone(blocked["observed_status_changed"])


if __name__ == "__main__":
    import unittest
    unittest.main()
