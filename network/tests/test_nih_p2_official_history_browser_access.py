"""Falsification controls for the official per-version ClinicalTrials.gov UI.

These mocked browser texts are NOT original clinical records. Only the
independent headless Chromium run may assert that exact original version
pages actually rendered in a live official public site.
"""
from __future__ import annotations

from copy import deepcopy
from unittest import TestCase

from systems.workspace import nih_p2_official_history_browser_access as h


def text_for(version):
    return (
        "ClinicalTrials.gov NCT00001756 Study of Mast Cell Precursors\n"
        "Record History Study Record Versions\n"
        f"Viewing V{version} (2019-08-03)\n"
        "Study Details\nRecruitment Status\nCompleted\n"
    )


def sample(version):
    return h.validate_observed_page(
        requested_version=version,requested_url=h.version_url(version),
        effective_url=h.version_url(version),body_text=text_for(version),
        title="Record History | NCT00001756 | ClinicalTrials.gov",
        status=200,retrieved_utc="2026-10-18T00:00:00+00:00")


class OriginalVersionPageTests(TestCase):
    def test_00_selected_url_is_bounded_exact_original_nct_and_version(self):
        self.assertEqual(h.version_url(94),
                         "https://clinicaltrials.gov/study/NCT00001756?a=94&tab=history")
        for version in (0,1,93,106,999,"94",None):
            with self.subTest(version=version),self.assertRaises(ValueError):
                h.version_url(version)

    def test_01_true_render_requires_explicit_selected_version_banner(self):
        for version in h.VERSIONS:
            r=sample(version)
            self.assertTrue(r["actual_original_version_rendered"])
            self.assertEqual(r["result"],"EXPLICIT_ORIGINAL_VERSION_VIEW")
            self.assertFalse(r["historic_status_field_authenticated"])
            self.assertFalse(r["public_version_post_date_authenticated"])

    def test_02_current_study_title_or_query_parameter_cannot_authenticate_old_version(self):
        orig=text_for(94)
        changes=(
            orig.replace("Viewing V94","Viewing V105"),
            orig.replace("Viewing V94",""),
            orig.replace("NCT00001756","NCT11111111"),
            orig.replace("Study Record Versions","Current Study Details"),
            orig.replace("Study Details","Current Record"),
            orig+" are you a robot",
        )
        for changed in changes:
            with self.subTest(change=changed[:140]):
                res=h.validate_observed_page(
                    requested_version=94,requested_url=h.version_url(94),
                    effective_url=h.version_url(94),
                    body_text=changed,title="ClinicalTrials.gov",status=200,
                    retrieved_utc="2026-10-18T00:00:00+00:00")
                self.assertFalse(res["actual_original_version_rendered"])
                self.assertFalse(res["historic_status_field_authenticated"])
        r=h.validate_observed_page(
            requested_version=94,requested_url=h.version_url(94),
            effective_url=h.version_url(94),body_text=orig,
            title="Record History",status=403,
            retrieved_utc="2026-10-18T00:00:00+00:00")
        self.assertFalse(r["actual_original_version_rendered"])

    def test_02a_reject_wrong_same_origin_route_with_correct_visible_banner(self):
        for changed_url in (
            "https://clinicaltrials.gov/study/NCT00001756?tab=history",
            "https://clinicaltrials.gov/study/NCT00001756?a=105&tab=history",
            "https://clinicaltrials.gov/study/NCT00001756?a=94&a=105&tab=history",
            "https://clinicaltrials.gov/study/NCT00001756?a=94&tab=history&extra=1",
            "https://clinicaltrials.gov/study/NCT00001756?a=94&tab=details",
            "https://clinicaltrials.gov/study/NCT00001757?a=94&tab=history",
            "https://clinicaltrials.gov/study/NCT00001756/other?a=94&tab=history",
        ):
            with self.subTest(effective_url=changed_url):
                r=h.validate_observed_page(
                    requested_version=94,requested_url=h.version_url(94),
                    effective_url=changed_url,body_text=text_for(94),
                    title="Record History",status=200,
                    retrieved_utc="2026-10-18T00:00:00+00:00")
                self.assertFalse(r["selected_exact_original_route"])
                self.assertFalse(r["actual_original_version_rendered"])
                self.assertFalse(r["historic_status_field_authenticated"])

    def test_02b_version_banner_must_have_exact_number_boundary(self):
        for fake in ("Viewing V940", "Viewing V941", "Viewing V94x"):
            with self.subTest(fake=fake):
                r=h.validate_observed_page(
                    requested_version=94,requested_url=h.version_url(94),
                    effective_url=h.version_url(94),
                    body_text=text_for(94).replace("Viewing V94",fake),
                    title="Record History",status=200,
                    retrieved_utc="2026-10-18T00:00:00+00:00")
                self.assertFalse(r["selected_version_view_banner_visible"])
                self.assertFalse(r["actual_original_version_rendered"])

    def test_04a_summarizer_rejects_inconsistent_success_receipts(self):
        r=sample(94)
        r["selected_exact_original_route"]=False
        with self.assertRaises(ValueError):
            h.summarize([r,sample(105)])
        r=sample(94)
        r["result"]="VERSION_VIEW_NOT_INDEPENDENTLY_RENDERED"
        with self.assertRaises(ValueError):
            h.summarize([r,sample(105)])
        incomplete=sample(94)
        incomplete["actual_original_version_rendered"]=False
        outcome=h.summarize([incomplete,sample(105)])
        self.assertEqual(outcome["actual_version_view_count"],1)
        self.assertFalse(outcome["both_original_version_views_witnessed"])

    def test_03_cross_origin_redirect_cannot_be_claimed_original_version(self):
        result=h.validate_observed_page(
            requested_version=94,requested_url=h.version_url(94),
            effective_url="https://login.example.org/gate?next=clinicaltrials.gov",
            body_text=text_for(94),title="Record History",status=200,
            retrieved_utc="2026-10-18T00:00:00+00:00")
        self.assertEqual(result["result"],"CROSS_ORIGIN_REDIRECT")
        self.assertFalse(result["actual_original_version_rendered"])

    def test_04_exact_two_distinct_actual_pages_required(self):
        r=h.summarize([sample(94),sample(105)])
        self.assertEqual(r["actual_version_view_count"],2)
        self.assertTrue(r["both_original_version_views_witnessed"])
        self.assertFalse(r["historical_source_fields_verified"])
        self.assertFalse(r["per_version_public_posting_date_verified"])
        self.assertFalse(r["original_twelve_native_jobs_modified"])
        with self.assertRaises(ValueError):
            h.summarize([sample(94),sample(94)])
        with self.assertRaises(ValueError):
            h.summarize([sample(94)])
        tampered=sample(105)
        tampered["public_version_post_date_authenticated"]=True
        with self.assertRaises(ValueError):
            h.summarize([sample(94),tampered])

    def test_05_bounded_source_response_and_no_fabricated_version_content(self):
        self.assertEqual(h.MAX_BODY,1200000)
        with self.assertRaises(ValueError):
            h.validate_observed_page(
                requested_version=94,requested_url=h.version_url(94),
                effective_url=h.version_url(94),body_text="x"*(h.MAX_BODY+1),
                title="",status=200,retrieved_utc="2026-10-18T00:00:00Z")


if __name__=="__main__":
    import unittest
    unittest.main()
