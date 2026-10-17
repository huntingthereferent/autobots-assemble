"""Native source projection regression tests; no network or database required."""
import unittest
from datetime import datetime, timezone

from app.platform import SourceObservation
from render import compose, render_svg, render_markdown


UTC = datetime(2026, 10, 17, 13, 0, tzinfo=timezone.utc)


def sources():
    quake = SourceObservation(
        source="live_json_api", source_id="usgs-test",
        observed_at=UTC, source_updated_at=UTC,
        source_url="https://earthquake.usgs.gov/earthquakes/eventpage/usgs-test",
        entity_type="event", canonical_key="event:usgs-test",
        payload={"magnitude": 2.7, "place": "Test", "occurred_at": UTC.isoformat()},
    )
    github = SourceObservation(
        source="github_api", source_id="1362490", observed_at=UTC,
        source_url="https://github.com/psf/requests",
        entity_type="repository", canonical_key="github_repo:1362490",
        payload={"full_name": "psf/requests", "stargazers_count": 5,
                 "default_branch": "main", "forks_count": 2},
    )
    pypi = SourceObservation(
        source="pypi_api", source_id="requests", observed_at=UTC,
        source_url="https://pypi.org/project/requests/",
        entity_type="package", canonical_key="pypi_package:requests",
        payload={"name": "requests", "version": "2.0",
                 "project_urls": {"Source": "https://github.com/psf/requests"}},
    )
    return [quake], github, pypi


class WorldViewTests(unittest.TestCase):
    def test_scoped_metadata_relation_but_not_usgs_join(self):
        quakes, github, pypi = sources()
        snap = compose(quakes, github, pypi, UTC)
        self.assertTrue(snap["relationship"]["matched_by_declared_url_rule"])
        self.assertEqual(snap["relationship"]["score"], 120)
        self.assertEqual(snap["sources"]["usgs"]["count"], 1)
        self.assertEqual(snap["sources"]["usgs"]["max_magnitude"], 2.7)
        self.assertIn("USGS", snap["unjoined"][0])
        self.assertEqual(snap["changes"]["github"]["kind"], "new")
        self.assertIn("No inferred USGS/software link", render_svg(snap))
        self.assertIn("not independently verified ownership", render_markdown(snap))

    def test_replay_and_changed_native_payload(self):
        quakes, github, pypi = sources()
        earlier = compose(quakes, github, pypi, UTC)
        same = compose(quakes, github, pypi, UTC, earlier)
        self.assertEqual(same["changes"]["github"]["kind"], "unchanged")
        self.assertEqual(same["content_sha256"], earlier["content_sha256"])
        github.payload["stargazers_count"] = 6
        changed = compose(quakes, github, pypi, UTC, earlier)
        self.assertEqual(changed["changes"]["github"]["kind"], "changed")
        self.assertEqual(changed["changes"]["github"]["changed_fields"], ["stargazers_count"])
        self.assertNotEqual(changed["content_sha256"], earlier["content_sha256"])

    def test_no_match_without_explicit_url(self):
        quakes, github, pypi = sources()
        pypi.payload["project_urls"] = {}
        snap = compose(quakes, github, pypi, UTC)
        self.assertFalse(snap["relationship"]["matched_by_declared_url_rule"])
        self.assertIn("No supported metadata match", render_svg(snap))

    def test_same_feed_content_has_order_independent_digest(self):
        quakes, github, pypi = sources()
        other = quakes[0].model_copy(deep=True)
        other.source_id = "usgs-test-2"
        other.canonical_key = "event:usgs-test-2"
        a = compose([quakes[0], other], github, pypi, UTC)
        b = compose([other, quakes[0]], github, pypi, UTC)
        self.assertEqual(a["content_sha256"], b["content_sha256"])

    def test_bad_source_and_previous_schema_rejected(self):
        quakes, github, pypi = sources()
        github.source = "unknown"
        with self.assertRaises(ValueError):
            compose(quakes, github, pypi, UTC)
        github.source = "github_api"
        with self.assertRaises(ValueError):
            compose(quakes, github, pypi, UTC, {"schema": "unknown"})

    def test_empty_earthquake_window_not_artificial_failure(self):
        _, github, pypi = sources()
        snap = compose([], github, pypi, UTC)
        self.assertEqual(snap["sources"]["usgs"]["count"], 0)
        self.assertIsNone(snap["sources"]["usgs"]["max_magnitude"])


if __name__ == "__main__":
    unittest.main()
