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
        self.assertEqual({topic for spec in REPORT_FEEDS.values() for topic in spec["topics"]},
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
        self.assertEqual(len(snapshot["items"]), 16)
        self.assertTrue(all("topic_basis" in item for item in snapshot["items"]))


if __name__ == "__main__":
    unittest.main()
