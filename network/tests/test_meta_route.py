"""Evidence-oriented regression tests for shared A/B routing advice."""
import datetime as dt
import unittest

from systems.workspace.meta_route import decide


T = dt.datetime(2026, 10, 22, 18, 0, tzinfo=dt.timezone.utc)


def sample(minutes_ago, a, b, a_seen=True, b_seen=True):
    def item(wait, seen):
        return {"observed": seen, "in_progress": 2,
                "queued": wait, "pending": 0, "waiting": 0}
    return {
        "ts": (T - dt.timedelta(minutes=minutes_ago)).isoformat().replace("+00:00", "Z"),
        "nodes": {"A": item(a, a_seen), "B": item(b, b_seen)},
    }


REGISTRY = {
    "schema": "meta-workstation/registry-v1",
    "lane_rules": [
        {"id": "SOURCE-CONTRACT", "node": "A", "admitted_nodes": ["A", "B"], "transferable": True},
        {"id": "ARC", "node": "A", "admitted_nodes": ["A"], "transferable": False},
        {"id": "B-CONTRACT", "node": "B", "admitted_nodes": ["B"], "transferable": False},
    ],
}


def history(*items):
    return {"schema": "ab-meta-observations/v1", "samples": list(items)}


class MetaRouteTests(unittest.TestCase):
    def test_rising_backlog_suggests_only_admitted_equivalent_on_b(self):
        result = decide(history(sample(40, 1, 0), sample(20, 2, 0),
                                sample(0, 5, 0)), REGISTRY, T)
        self.assertEqual(result["signal"], "A_BACKLOG")
        advice = {l["id"]: l for l in result["lane_advice"]}
        self.assertEqual(advice["SOURCE-CONTRACT"]["recommended"], "B")
        self.assertEqual(advice["SOURCE-CONTRACT"]["action"], "CANDIDATE_SWITCH")
        self.assertEqual(advice["ARC"]["recommended"], "A")
        self.assertEqual(advice["ARC"]["action"], "NO_ADMITTED_ALTERNATE")
        self.assertEqual(advice["B-CONTRACT"]["recommended"], "B")

    def test_one_snapshot_cannot_claim_pressure(self):
        result = decide(history(sample(0, 25, 0)), REGISTRY, T)
        self.assertEqual(result["signal"], "OBSERVING")
        self.assertEqual(result["lane_advice"][0]["action"], "VERIFY_SOURCE")

    def test_repeated_seconds_cannot_fake_distinct_observation_window(self):
        result = decide(history(sample(3, 1, 0), sample(2, 2, 0),
                                sample(1, 5, 0)), REGISTRY, T)
        self.assertEqual(result["signal"], "OBSERVING")

    def test_stale_snapshot_fails_closed(self):
        result = decide(history(sample(180, 0, 0), sample(150, 3, 0),
                                sample(120, 7, 0)), REGISTRY, T)
        self.assertEqual(result["signal"], "STALE")
        self.assertEqual(result["lane_advice"][0]["recommended"], "A")

    def test_missing_second_node_is_not_zero(self):
        result = decide(history(sample(40, 1, 0), sample(20, 2, 0),
                                sample(0, 5, 0, b_seen=False)), REGISTRY, T)
        self.assertNotEqual(result["signal"], "A_BACKLOG")

    def test_flat_waiting_queue_cannot_be_called_congestion(self):
        result = decide(history(sample(40, 7, 0), sample(20, 7, 0),
                                sample(0, 7, 0)), REGISTRY, T)
        self.assertEqual(result["signal"], "NO_CLEAR_PRESSURE")

    def test_b_waiting_grows_and_no_transfer_eligible(self):
        result = decide(history(sample(40, 0, 1), sample(20, 0, 2),
                                sample(0, 0, 7)), REGISTRY, T)
        self.assertEqual(result["signal"], "B_BACKLOG")
        self.assertEqual(result["lane_advice"][2]["recommended"], "B")

    def test_missing_all_observations_is_unknown(self):
        result = decide(history(), REGISTRY, T)
        self.assertEqual(result["signal"], "UNKNOWN")
        self.assertIsNone(result["last_paired_observation"])


if __name__ == "__main__":
    unittest.main()
