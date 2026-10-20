"""Reject false history fields, wrong source identity, and invented posting times."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from unittest import TestCase

from systems.workspace import nih_p2_official_history_browser_access as ui
from systems.workspace import nih_p2_official_history_status_fields as h


def source_text(v: int, status: str = "Recruiting",
                posted: str = "2019-08-02 [Actual]",
                qc: str = "2019-08-01") -> str:
    return f"""ClinicalTrials.gov {ui.NCT} {ui.TITLE}
Current Study Status
Overall Status
Completed
Last Update Posted
2022-11-07 [Actual]
Record History
Study Record Versions
Version Date submitted
94 2019-08-01 Study Status
105 2019-11-01 Study Status
Viewing V{v} (2019-08-01)
Study Details
Study Identification
Unique Protocol ID
12345
Study Status
Record Verification
2019-07
Overall Status
{status}
Study Start
2008-01-01 [Actual]
Last Update Submitted that Met QC Criteria
{qc}
Last Update Posted
{posted}
Sponsor/Collaborators
Sponsor
Original institution
"""


def receipt(v: int, source: str) -> dict:
    return ui.validate_observed_page(
        requested_version=v, requested_url=ui.version_url(v),
        effective_url=ui.version_url(v), body_text=source,
        title=f"Record History | {ui.NCT} | ClinicalTrials.gov",
        status=200, retrieved_utc="2026-10-20T12:00:00+00:00",
    )


def parse(v: int, **kwargs) -> dict:
    body = source_text(v, **kwargs)
    return h.extract_version_field(receipt=receipt(v, body), body_text=body)


class HistoricalStatusFieldTests(TestCase):
    def test_01_extract_exact_version_status_not_current_header(self):
        r = parse(94, status="Recruiting")
        self.assertEqual(r["status_value_in_selected_version"], "Recruiting")
        self.assertEqual(r["last_update_posted_day_in_selected_version"], "2019-08-02")
        self.assertEqual(r["last_update_posted_precision"], "Actual")
        self.assertTrue(r["qc_date_equals_version_banner_date"])
        self.assertFalse(r["original_version_first_public_day_independently_proved"])
        self.assertNotIn("2022-11-07", str(r))

    def test_02_two_versions_keep_actual_status_difference_as_observation_only(self):
        result = h.report_pair([parse(94, status="Recruiting"),
                                parse(105, status="Completed")])
        self.assertTrue(result["two_exact_version_status_fields_observed"])
        self.assertTrue(result["different_status_values_observed"])
        self.assertFalse(result["public_known_at_admitted_for_temporal_program"])
        self.assertEqual(result["historical_first_publication_attribution"],
                         "UNAVAILABLE")
        self.assertFalse(result["original_w13_journals_modified"])

    def test_03_only_selected_version_after_banner_is_used(self):
        body = source_text(94)
        transformed = body.replace("Viewing V94 (2019-08-01)", "Viewing V940 (2019-08-01)")
        with self.assertRaises(ValueError):
            h.extract_version_field(receipt=receipt(94, body), body_text=transformed)
        with self.assertRaises(ValueError):
            h.extract_version_field(receipt=receipt(94, body), body_text=body + "\nspoof")

    def test_04_duplicate_and_absent_version_status_are_rejected(self):
        original = source_text(94)
        wrong = original.replace("Overall Status\nRecruiting\n",
                                 "Overall Status\nRecruiting\nOverall Status\nCompleted\n")
        for payload in (wrong, original.replace("Overall Status\nRecruiting\n", "")):
            with self.subTest(payload=payload[-100:]):
                with self.assertRaises(ValueError):
                    h.extract_version_field(receipt=receipt(94, payload), body_text=payload)

    def test_05_forged_or_impossible_posting_field_refused(self):
        bad = ("2019-07-31 [Actual]", "2027-01-01 [Actual]", "2019-08-02",
               "2019-08-02 [Verified]", "2019-02-30 [Actual]")
        for date_text in bad:
            with self.subTest(text=date_text), self.assertRaises(ValueError):
                parse(94, posted=date_text)
        estimated = parse(94, posted="2019-08-02 [Estimated]")
        self.assertEqual(estimated["last_update_posted_precision"], "Estimated")
        self.assertFalse(estimated["original_version_first_public_day_independently_proved"])

    def test_06_wrong_route_and_false_original_version_rejected(self):
        body = source_text(94)
        r = receipt(94, body)
        r["selected_exact_original_route"] = False
        with self.assertRaises(ValueError):
            h.extract_version_field(receipt=r, body_text=body)
        r = receipt(94, body)
        r["actual_original_version_rendered"] = False
        with self.assertRaises(ValueError):
            h.extract_version_field(receipt=r, body_text=body)

    def test_07_unavailable_or_forged_publication_cannot_pass_pair(self):
        first = parse(94)
        second = parse(105)
        with self.assertRaises(ValueError):
            h.report_pair([first, first])
        with self.assertRaises(ValueError):
            h.report_pair([first])
        forged = deepcopy(second)
        forged["original_version_first_public_day_independently_proved"] = True
        with self.assertRaises(ValueError):
            h.report_pair([first, forged])
        blocked = h.report_pair([first, {
            "requested_version": 105, "version_local_status_observed": False,
            "original_version_first_public_day_independently_proved": False,
            "result": "UNAVAILABLE",
        }])
        self.assertFalse(blocked["two_exact_version_status_fields_observed"])
        self.assertIsNone(blocked["different_status_values_observed"])


if __name__ == "__main__":
    import unittest
    unittest.main()
