"""Capacity observation is multi-node, fail-closed and never a scheduler."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import unittest

from systems.workspace.factory_capacity_observer import SCHEMA, evaluate


NOW = datetime(2026, 10, 22, 18, 15, tzinfo=timezone.utc)


def obs(minutes_ago: int, *, active=3, queued=2, limit=None) -> dict:
    stamp = (NOW - timedelta(minutes=minutes_ago)).isoformat()
    row = {
        "captured_at": stamp, "active": active, "queued": queued,
        "historical_total": 1234,
        "source_refs": {
            "active": "https://api.github.com/repos/example/research/actions/runs?status=in_progress",
            "queued": "https://api.github.com/repos/example/research/actions/runs?status=queued",
        },
    }
    if limit is not None:
        row["declared_concurrency_limit"] = limit
        row["limit_evidence_ref"] = "operator-supplied-source-reference"
    return row


def payload(*nodes):
    return {"schema": SCHEMA, "nodes": list(nodes)}


def node(identifier, observations):
    return {"node_id": identifier, "provider": "github-actions",
            "observations": observations}


class FactoryCapacityObserverTests(unittest.TestCase):
    def test_one_observation_never_proves_saturation(self):
        result = evaluate(payload(node("A", [obs(1, active=40, queued=250)])),
                          now=NOW)
        self.assertEqual(result["nodes"][0]["state"],
                         "QUEUE_OBSERVED_NOT_SATURATION")
        self.assertEqual(result["totals"]["scale_review_candidates"], 0)
        self.assertFalse(result["nodes"][0]["expansion_authorized"])

    def test_repeated_queue_without_verified_limit_stays_open(self):
        result = evaluate(payload(node("A", [obs(12), obs(7), obs(1)])),
                          now=NOW)
        self.assertEqual(result["nodes"][0]["state"],
                         "SUSTAINED_QUEUE_CAPACITY_UNKNOWN")
        self.assertIsNone(result["nodes"][0]["concurrency_limit"])

    def test_declared_limit_only_produces_review_candidate(self):
        result = evaluate(payload(node("A", [obs(12, limit=3),
                                           obs(7, limit=3),
                                           obs(1, limit=3)])), now=NOW)
        self.assertEqual(result["nodes"][0]["state"],
                         "SCALE_REVIEW_CANDIDATE")
        self.assertEqual(result["nodes"][0]["limit_status"],
                         "OPERATOR_DECLARED_NOT_INDEPENDENTLY_VERIFIED")
        self.assertFalse(result["nodes"][0]["expansion_authorized"])
        self.assertEqual(result["nodes"][0]["research_results_verified"], 0)

    def test_limit_not_reached_is_not_scale_candidate(self):
        result = evaluate(payload(node("A", [obs(12, limit=4),
                                           obs(7, limit=4),
                                           obs(1, limit=4)])), now=NOW)
        self.assertEqual(result["nodes"][0]["state"],
                         "SUSTAINED_QUEUE_CAPACITY_UNKNOWN")

    def test_stale_node_excluded_from_current_totals(self):
        result = evaluate(payload(
            node("A", [obs(1, active=2, queued=4)]),
            node("B", [obs(60, active=50, queued=90)])), now=NOW)
        self.assertEqual(result["totals"]["fresh_nodes"], 1)
        self.assertEqual(result["totals"]["active"], 2)
        self.assertEqual(result["totals"]["queued"], 4)
        self.assertEqual(result["nodes"][1]["state"], "STALE")

    def test_no_fixed_node_count_or_cross_node_merging(self):
        many = [node(f"node-{i:04d}", [obs(1, active=1, queued=0)])
                for i in range(1024)]
        result = evaluate(payload(*many), now=NOW)
        self.assertEqual(result["measured_node_count"], 1024)
        self.assertEqual(result["totals"]["active"], 1024)
        self.assertEqual(result["totals"]["scale_review_candidates"], 0)
        self.assertTrue(result["read_only"])

    def test_duplicate_identity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate node"):
            evaluate(payload(node("A", [obs(1)]), node("A", [obs(2)])),
                     now=NOW)

    def test_wrong_order_and_future_observation_rejected(self):
        with self.assertRaisesRegex(ValueError, "chronologically"):
            evaluate(payload(node("A", [obs(1), obs(12)])), now=NOW)
        with self.assertRaisesRegex(ValueError, "future"):
            evaluate(payload(node("A", [obs(-1)])), now=NOW)

    def test_missing_source_and_boolean_counts_fail_closed(self):
        bad = obs(1)
        del bad["source_refs"]["queued"]
        with self.assertRaisesRegex(ValueError, "queued source"):
            evaluate(payload(node("A", [bad])), now=NOW)
        bad = obs(1)
        bad["queued"] = True
        with self.assertRaisesRegex(ValueError, "nonnegative integer"):
            evaluate(payload(node("A", [bad])), now=NOW)

    def test_empty_nodes_are_not_an_implicit_success(self):
        result = evaluate(payload(), now=NOW)
        self.assertEqual(result["measured_node_count"], 0)
        self.assertEqual(result["totals"]["fresh_nodes"], 0)
        self.assertFalse(any(n["expansion_authorized"]
                             for n in result["nodes"]))


if __name__ == "__main__":
    unittest.main()
