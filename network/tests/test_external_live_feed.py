import unittest
from unittest.mock import patch

from runtime.external_feed import FETCHERS, MAX_SNIPPET, SOURCE_META, LiveFeed, _item


def _row(source_id, provider, roles, medium, title, published):
    return _item(
        item_id=source_id + ":" + title,
        source_id=source_id,
        provider=provider,
        provider_surface="test_surface",
        medium=medium,
        roles=roles,
        title=title,
        url="https://example.com/" + source_id + "/" + title,
        published_at=published,
    )


class ExternalLiveFeedTests(unittest.TestCase):
    def test_snapshot_combines_unlike_live_sources(self):
        fake_fetchers = {
            "social_a": lambda: [
                _row(
                    "social_a",
                    "Social A",
                    ["social", "community"],
                    "post",
                    "a1",
                    "2026-10-06T19:10:00Z",
                ),
                _row(
                    "social_a",
                    "Social A",
                    ["social", "community"],
                    "post",
                    "a2",
                    "2026-10-06T19:08:00Z",
                ),
            ],
            "news_a": lambda: [
                _row(
                    "news_a",
                    "News A",
                    ["news"],
                    "article",
                    "n1",
                    "2026-10-06T19:09:00Z",
                ),
            ],
        }
        fake_meta = {
            "social_a": {"name": "Social A", "surface": "social_platform", "access": "test"},
            "news_a": {"name": "News A", "surface": "news_site", "access": "test"},
        }
        with patch("runtime.external_feed.FETCHERS", fake_fetchers), patch(
            "runtime.external_feed.SOURCE_META", fake_meta
        ):
            snapshot = LiveFeed(cache_seconds=0).snapshot(force=True)

        self.assertEqual([x["title"] for x in snapshot["items"]], ["a1", "n1", "a2"])
        self.assertIn("social", snapshot["items"][0]["roles"])
        self.assertIn("news", snapshot["items"][1]["roles"])
        self.assertEqual(sum(x["count"] for x in snapshot["sources"]), 3)

    def test_one_item_can_be_youtube_reuters_video_and_news(self):
        item = _item(
            item_id="youtube:test",
            source_id="youtube_reuters",
            provider="YouTube",
            provider_surface="video_platform",
            publisher="Reuters",
            medium="video",
            roles=("news",),
            topics=("politics",),
            title="Example report",
            url="https://youtube.com/watch?v=test",
        )

        self.assertEqual(item["provider"], "YouTube")
        self.assertEqual(item["publisher"], "Reuters")
        self.assertEqual(item["medium"], "video")
        self.assertIn("news", item["roles"])
        self.assertIn("politics", item["topics"])
        self.assertEqual(item["source_name"], "YouTube · Reuters")
        self.assertNotIn("source_kind", item)

    def test_source_excerpt_budget_is_dense_but_substantive(self):
        self.assertGreaterEqual(MAX_SNIPPET, 640)
        long_text = "x" * 900
        item = _item(
            item_id="dense:test",
            source_id="dense",
            provider="Dense Source",
            provider_surface="test",
            medium="article",
            roles=("news",),
            title="Dense test",
            url="https://example.com/dense",
            snippet=long_text,
        )
        self.assertEqual(len(item["snippet"]), MAX_SNIPPET)
        self.assertTrue(item["snippet"].endswith("…"))

    def test_source_failure_is_visible_and_not_fabricated(self):
        def broken():
            raise RuntimeError("provider unavailable")

        fake_fetchers = {"broken": broken}
        fake_meta = {
            "broken": {"name": "Broken", "surface": "social_platform", "access": "test"},
            "auth_only": {
                "name": "Auth only",
                "surface": "social_platform",
                "access": "account",
                "enabled": False,
                "reason": "requires account access",
            },
        }
        with patch("runtime.external_feed.FETCHERS", fake_fetchers), patch(
            "runtime.external_feed.SOURCE_META", fake_meta
        ):
            snapshot = LiveFeed(cache_seconds=0).snapshot(force=True)

        self.assertEqual(snapshot["items"], [])
        statuses = {x["id"]: x for x in snapshot["sources"]}
        self.assertFalse(statuses["broken"]["ok"])
        self.assertIn("provider unavailable", statuses["broken"]["error"])
        self.assertFalse(statuses["auth_only"]["ok"])
        self.assertEqual(statuses["auth_only"]["reason"], "requires account access")

    def test_lemmy_is_not_a_live_source(self):
        self.assertNotIn("lemmy", FETCHERS)
        self.assertNotIn("lemmy", SOURCE_META)

    def test_live_feed_projection_has_no_persistence_path(self):
        feed = LiveFeed()
        self.assertFalse(hasattr(feed, "path"))
        self.assertFalse(hasattr(feed, "store"))


if __name__ == "__main__":
    unittest.main()
