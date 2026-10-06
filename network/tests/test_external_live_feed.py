import unittest
from unittest.mock import patch

from runtime.external_feed import LiveFeed


def _row(source_id, source_name, source_kind, title, published):
    return {
        "id": source_id + ":" + title,
        "source_id": source_id,
        "source_name": source_name,
        "source_kind": source_kind,
        "native_type": "post",
        "title": title,
        "url": "https://example.com/" + source_id + "/" + title,
        "published_at": published,
        "author": "",
        "context": "",
        "snippet": "",
        "metrics": {},
    }


class ExternalLiveFeedTests(unittest.TestCase):
    def test_snapshot_combines_unlike_live_sources(self):
        fake_fetchers = {
            "social_a": lambda: [
                _row("social_a", "Social A", "social", "a1", "2026-10-06T19:10:00Z"),
                _row("social_a", "Social A", "social", "a2", "2026-10-06T19:08:00Z"),
            ],
            "news_a": lambda: [
                _row("news_a", "News A", "news", "n1", "2026-10-06T19:09:00Z"),
            ],
        }
        fake_meta = {
            "social_a": {"name": "Social A", "kind": "social", "access": "test"},
            "news_a": {"name": "News A", "kind": "news", "access": "test"},
        }
        with patch("runtime.external_feed.FETCHERS", fake_fetchers), patch(
            "runtime.external_feed.SOURCE_META", fake_meta
        ):
            snapshot = LiveFeed(cache_seconds=0).snapshot(force=True)

        self.assertEqual([x["title"] for x in snapshot["items"]], ["a1", "n1", "a2"])
        self.assertEqual({x["source_kind"] for x in snapshot["items"]}, {"social", "news"})
        self.assertEqual(sum(x["count"] for x in snapshot["sources"]), 3)

    def test_source_failure_is_visible_and_not_fabricated(self):
        def broken():
            raise RuntimeError("provider unavailable")

        fake_fetchers = {"broken": broken}
        fake_meta = {
            "broken": {"name": "Broken", "kind": "social", "access": "test"},
            "auth_only": {
                "name": "Auth only",
                "kind": "social",
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

    def test_live_feed_projection_has_no_persistence_path(self):
        feed = LiveFeed()
        self.assertFalse(hasattr(feed, "path"))
        self.assertFalse(hasattr(feed, "store"))


if __name__ == "__main__":
    unittest.main()
