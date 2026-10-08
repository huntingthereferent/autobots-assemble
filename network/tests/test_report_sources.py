import unittest
from unittest.mock import patch

from runtime.external_feed import REPORT_FEEDS, FETCHERS, SOURCE_META, LiveFeed, fetch_report_feed


RSS = b"""<rss version="2.0"><channel><title>Source</title>
<item><guid>native-1</guid><title>Original source claim</title>
<link>https://example.org/report/1</link>
<pubDate>Wed, 07 Oct 2026 12:00:00 GMT</pubDate>
<description>Separate claim &amp; useful detail</description>
<category>Source category</category></item>
<item><title>Undated claim</title><link>https://example.org/report/2</link></item>
<item><title>Bad locator</title><link>javascript:alert(1)</link></item>
</channel></rss>"""


class ReportSourcesTests(unittest.TestCase):
    def test_registry_covers_nine_domains_with_documented_feed_scope(self):
        self.assertEqual({topic for spec in REPORT_FEEDS.values() for topic in spec["topics"] if ":" not in topic},
                         {"world", "sports", "learning", "industry", "work", "markets",
                          "research", "culture", "household"})
        for key, spec in REPORT_FEEDS.items():
            self.assertIn(key, FETCHERS)
            self.assertEqual(SOURCE_META[key]["feed_url"], spec["url"])
            self.assertEqual(SOURCE_META[key]["documentation"], spec["documentation"])

    def test_rss_preserves_claim_categories_date_and_admission_provenance(self):
        with patch("runtime.external_feed._fetch", return_value=RSS):
            rows = fetch_report_feed("bls_productivity")
        self.assertEqual(len(rows), 2)
        first = rows[0]
        self.assertEqual(first["title"], "Original source claim")
        self.assertEqual(first["snippet"], "Separate claim & useful detail")
        self.assertEqual(first["native_categories"], ["Source category"])
        self.assertEqual(first["published_at"], "2026-10-07T12:00:00+00:00")
        self.assertEqual(rows[1]["published_at"], "")
        self.assertEqual(first["topics"], ["industry"])
        self.assertEqual(first["topic_basis"]["kind"], "publisher_feed_scope")
        self.assertEqual(first["topic_basis"]["feed_url"], REPORT_FEEDS["bls_productivity"]["url"])

    def test_each_fetcher_binds_its_own_source_and_scope(self):
        with patch("runtime.external_feed._fetch", return_value=RSS):
            for key in REPORT_FEEDS:
                item = FETCHERS[key]()[0]
                self.assertEqual(item["source_id"], key)
                self.assertEqual(item["topics"], list(REPORT_FEEDS[key]["topics"]))
                self.assertTrue(item["id"].startswith(key + ":"))

    def test_atom_preserves_alternate_locator_author_and_native_categories(self):
        atom = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry>
        <id>native:atom</id><title>Claim</title><link rel="self" href="https://example.org/api"/>
        <link href="https://example.org/article"/><published>2026-10-07T12:00:00Z</published>
        <summary>Native excerpt</summary><author><name>Witness author</name></author>
        <category term="Native topic"/></entry></feed>"""
        with patch("runtime.external_feed._fetch", return_value=atom):
            item = fetch_report_feed("nsf_news")[0]
        self.assertEqual(item["url"], "https://example.org/article")
        self.assertEqual(item["author"], "Witness author")
        self.assertEqual(item["native_categories"], ["Native topic"])

    def test_country_scope_and_language_survive_without_rewriting_claims(self):
        body = RSS.replace(b"Original source claim", "Original 日本語 claim".encode())
        with patch("runtime.external_feed._fetch", return_value=body):
            for key in ("ca_labour", "au_releases", "de_latest"):
                row = fetch_report_feed(key)[0]
                self.assertEqual(row["title"], "Original 日本語 claim")
                self.assertEqual(row["country_basis"], "publisher_jurisdiction")
                self.assertEqual(row["language"], "en")
                self.assertIn("world:countries:" + row["country"].lower(), row["topics"])
                self.assertEqual(SOURCE_META[key]["country_code"], row["country_code"])

    def test_country_editions_preserve_native_text_and_independent_witnesses(self):
        for key, title, language in [("jp_boj_ja", "日本銀行の発表", "ja"),
                                     ("br_education", "Educação e ciência", "pt-BR")]:
            body = RSS.replace(b"Original source claim", title.encode())
            with patch("runtime.external_feed._fetch", return_value=body):
                row = fetch_report_feed(key)[0]
            self.assertEqual(row["title"], title)
            self.assertEqual(row["language"], language)
            self.assertEqual(SOURCE_META[key]["language"], language)
        with patch("runtime.external_feed._fetch", return_value=RSS):
            english = fetch_report_feed("jp_boj_en")[0]
            japanese = fetch_report_feed("jp_boj_ja")[0]
        self.assertNotEqual(english["id"], japanese["id"])
        self.assertEqual(english["country_code"], japanese["country_code"])
        self.assertEqual(english["language"], "en")
        self.assertEqual(japanese["language"], "ja")

    def test_atom_xhtml_keeps_nested_claim_text(self):
        body = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml">Payroll <span>July 2026</span></div></title><link href="https://example.org/report"/><summary type="xhtml"><div xmlns="http://www.w3.org/1999/xhtml">Original <b>detail</b></div></summary></entry></feed>'
        with patch("runtime.external_feed._fetch", return_value=body):
            row = fetch_report_feed("ca_labour")[0]
        self.assertEqual(row["title"], "Payroll July 2026")
        self.assertEqual(row["snippet"], "Original detail")

    def test_rdf_rss_preserves_claim_locator_and_dc_date(self):
        body = b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://purl.org/rss/1.0/" xmlns:dc="http://purl.org/dc/elements/1.1/"><item rdf:about="native-id"><title>RBA claim</title><link>https://example.org/report</link><description>Native detail</description><dc:date>2026-10-01T11:30:00+10:00</dc:date><dc:subject>Economy</dc:subject></item></rdf:RDF>'
        with patch("runtime.external_feed._fetch", return_value=body):
            row = fetch_report_feed("au_releases")[0]
        self.assertEqual(row["title"], "RBA claim")
        self.assertEqual(row["id"], "au_releases:native-id")
        self.assertEqual(row["published_at"], "2026-10-01T11:30:00+10:00")
        self.assertEqual(row["native_categories"], ["Economy"])

    def test_limit_and_empty_feed_do_not_generate_reports(self):
        with patch("runtime.external_feed._fetch", return_value=RSS):
            self.assertEqual(len(fetch_report_feed("bbc_world", 1)), 1)
            self.assertEqual(fetch_report_feed("bbc_world", 0), [])
        with patch("runtime.external_feed._fetch", return_value=b"<rss><channel/></rss>"):
            self.assertEqual(fetch_report_feed("bbc_world"), [])

    def test_non_feed_and_transport_errors_stay_failures(self):
        for body in [b"<html>Access denied</html>", b"malformed"]:
            with patch("runtime.external_feed._fetch", return_value=body):
                with self.assertRaises(Exception):
                    fetch_report_feed("sec_releases")
        with patch("runtime.external_feed._fetch", side_effect=TimeoutError("bounded timeout")):
            with self.assertRaises(TimeoutError):
                fetch_report_feed("sec_releases")

    def test_snapshot_preserves_domain_source_statuses_when_one_provider_fails(self):
        def broken():
            raise TimeoutError("bounded timeout")
        fetchers = {key: (lambda key=key: fetch_report_feed(key)) for key in REPORT_FEEDS}
        fetchers["sec_releases"] = broken
        with patch("runtime.external_feed.FETCHERS", fetchers), patch("runtime.external_feed._fetch", return_value=RSS):
            snapshot = LiveFeed(cache_seconds=0).snapshot()
        statuses = {source["id"]: source for source in snapshot["sources"]}
        self.assertFalse(statuses["sec_releases"]["ok"])
        self.assertEqual(statuses["sec_releases"]["topics"], ["markets"])
        self.assertEqual(statuses["sec_releases"]["count"], 0)
        self.assertEqual(len(snapshot["items"]), 2 * (len(REPORT_FEEDS) - 1))
        self.assertTrue(all("topic_basis" in item for item in snapshot["items"]))


if __name__ == "__main__":
    unittest.main()
