"""Fail-closed tests for CTTI original public archive catalog inspection.

All HTML fixtures here are invented failure tests, never evidence that a
2022 owner archive link or original registry version was accessed.
"""
from __future__ import annotations

from io import BytesIO
from unittest import TestCase
from urllib.error import HTTPError

from systems.workspace import nih_p2_ctti_owner_catalog_2022 as m


class FakeResponse:
    def __init__(self, url, content, *, status=200, final=None, content_type="text/html"):
        self.url=url
        self.body=BytesIO(content)
        self.status=status
        self.final=final or url
        self.headers={"Content-Type":content_type,"Content-Length":str(len(content))}
    def __enter__(self):
        return self
    def __exit__(self,*args):
        self.body.close()
    def geturl(self):
        return self.final
    def read(self,n=-1):
        return self.body.read(n)


class OriginalCTTI2022CatalogTests(TestCase):
    def test_00_only_real_owner_html_links_witness_candidates(self):
        html=b'''<html><title>AACT snapshots</title><body>
          <a href="/static/static_db_copies/2022/20221101_export.zip">Nov 2022</a>
          <a href="https://aact.ctti-clinicaltrials.org/static/static_db_copies/2022/20221201_export.zip">Dec</a>
          <a href="/static/static_db_copies/2023/20230102_export.zip">wrong year</a>
          </body></html>'''
        result=m.catalog_candidates(html.decode(),base_url=m.CATALOG_URLS[0])
        self.assertEqual([x["archive_filename"] for x in result["candidate_archive_links"]],
                         ["20221101_export.zip","20221201_export.zip"])
        self.assertIn("AACT snapshots",result["source_page_title"])
        self.assertFalse(result["login_or_access_banner_seen"])

    def test_01_ignore_guesstimates_cross_site_and_signed_links(self):
        html='''<a href="https://evil.example/downloads/20221101_export.zip">wrong host</a>
          <a href="/static/20221101_export.zip?sig=private">signed</a>
          <a href="/static/20221101_export.zip?download=1">not direct file link</a>
          <a href="/static/20221131_export.zip">not true calendar</a>
          <a href="/static/20221201_export.txt">not zip</a>'''
        result=m.catalog_candidates(html,base_url=m.CATALOG_URLS[0])
        # Invalid calendar dates are not promoted to historical archive rows.
        self.assertEqual(result["candidate_archive_links"],[])

    def test_02_absent_or_login_only_page_is_not_claimed_as_archive(self):
        seen=[]
        def opener(req, timeout):
            seen.append(req.full_url)
            return FakeResponse(req.full_url,
                b"<html><title>Sign in to AACT</title>Create account</html>")
        report=m.inspect(opener=opener,checked_at="2026-10-18T00:00:00Z")
        self.assertEqual(seen,list(m.CATALOG_URLS))
        self.assertFalse(report["public_2022_archive_url_discovered"])
        self.assertTrue(report["catalog_access_or_linkage_unresolved"])
        self.assertTrue(all(x["login_or_access_banner_seen"]
                            for x in report["unauthenticated_public_catalog_checks"]))
        self.assertEqual(report["archive_bytes_downloaded"],0)
        self.assertFalse(report["historical_primary_record_version_content_witnessed"])
        self.assertFalse(report["original_twelve_job_workstation_modified"])

    def test_03_http_403_and_404_are_recorded_as_failure_not_empty_historical_data(self):
        def opener(req, timeout):
            raise HTTPError(req.full_url,403 if "downloads/" in req.full_url else 404,
                            "Unavailable",{},None)
        report=m.inspect(opener=opener)
        self.assertEqual([x["http_status"] for x in report["unauthenticated_public_catalog_checks"]],
                         [403,404,404])
        self.assertFalse(report["public_2022_archive_url_discovered"])
        self.assertTrue(report["catalog_access_or_linkage_unresolved"])
        self.assertTrue(report["not_attempted_to_bypass_authentication"])

    def test_04_actual_server_link_only_not_inferred_or_downloaded(self):
        html=b'<a href="/static/20221101_export.zip">2022 original archive link</a>'
        def opener(req,timeout):
            self.assertEqual(req.get_method(),"GET")
            self.assertTrue("aact.ctti-clinicaltrials.org" in req.full_url)
            self.assertNotIn("20221101_export",req.full_url)
            return FakeResponse(req.full_url,html)
        report=m.inspect(opener=opener)
        self.assertTrue(report["public_2022_archive_url_discovered"])
        self.assertEqual(len(report["candidate_archive_links_from_actual_owner_html"]),1)
        self.assertEqual(report["archive_bytes_downloaded"],0)
        self.assertFalse(report["archive_whole_file_sha256_verified"])
        self.assertFalse(report["source_2022_record_contents_witnessed"])
        self.assertFalse(report["original_registry_per_version_public_posting_time_witnessed"])

    def test_05_bounded_page_size_and_origin_checked(self):
        self.assertEqual(m.MAX_RESPONSE_BYTES,2_000_000)
        with self.assertRaises(ValueError):
            m.catalog_candidates("x"*(m.MAX_RESPONSE_BYTES+1),base_url=m.CATALOG_URLS[0])
        with self.assertRaises(ValueError):
            m._open_bounded("https://different-host.example/x",opener=lambda **kw:None)
        def opener(req,timeout):
            return FakeResponse(req.full_url,b"X"*(m.MAX_RESPONSE_BYTES+1))
        with self.assertRaises(ValueError):
            m._open_bounded(m.CATALOG_URLS[0],opener=opener)


if __name__=="__main__":
    import unittest
    unittest.main()
