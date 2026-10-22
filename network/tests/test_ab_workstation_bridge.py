"""Integration contract for the A/B-to-workstation evidence boundary."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.ab_relational_cluster import advance
from systems.workspace.ab_workstation_bridge import (
    ABClusterWitnessVerifier, movement_ref, replayed_rows,
)
from systems.workspace.workstation_continuation import Observation


class ABWorkstationBridgeTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.data = Path(temp.name)
        self.journal = self.data / "ab_relational_cluster.jsonl"
        self.verifier = ABClusterWitnessVerifier(self.journal)

    def fill_until_connection(self):
        for _ in range(12):
            result = advance(self.data, execute=True, workers=3)
            rows = replayed_rows(self.journal)
            for row in rows:
                for collision in row["movements"]:
                    if (collision["kind"] != "CONNECTION" or not collision["existing_word"]
                            or collision["from"] == collision["existing_word"]):
                        continue
                    prior = next((m for candidate in rows for m in candidate["movements"]
                                  if m["kind"] == "BRANCH"
                                  and m["word"] == collision["existing_word"]
                                  and m["to"] == collision["to"]), None)
                    if prior is not None:
                        return rows
            if result["status"] == "QUIET":
                break
        self.fail("finite A/B cluster did not produce a cross-trajectory collision")

    def test_exact_replayed_branch_witness_is_accepted_only_for_bound_parent_lane(self):
        advance(self.data, execute=True)
        row = replayed_rows(self.journal)[0]
        movement = next(m for m in row["movements"] if m["kind"] == "BRANCH")
        self.verifier.bind_lane(movement["from"], "root")
        obs = Observation("o1", "root", "BRANCH", movement["word"],
                          movement_ref(row["entry_hash"], movement),
                          "finite-required-edge-prefilter", 1)
        self.assertTrue(self.verifier.verify_observation(obs))
        wrong_lane = Observation("o2", "unbound", "BRANCH", movement["word"],
                                 obs.witness_ref, obs.capability, 2)
        self.assertFalse(self.verifier.verify_observation(wrong_lane))

    def test_wrong_relation_and_fabricated_reference_fail_closed(self):
        advance(self.data, execute=True)
        row = replayed_rows(self.journal)[0]
        movement = next(m for m in row["movements"] if m["kind"] == "BRANCH")
        self.verifier.bind_lane(movement["from"], "root")
        ref = movement_ref(row["entry_hash"], movement)
        wrong = Observation("o1", "root", "BRANCH", "not-the-observed-word",
                            ref, "finite-required-edge-prefilter", 1)
        fake = Observation("o2", "root", "BRANCH", movement["word"],
                           ref[:-1] + ("x" if ref[-1] != "x" else "y"),
                           "finite-required-edge-prefilter", 2)
        self.assertFalse(self.verifier.verify_observation(wrong))
        self.assertFalse(self.verifier.verify_observation(fake))

    def test_collision_needs_two_distinct_bound_path_witnesses_for_same_state(self):
        rows = self.fill_until_connection()
        found = None
        for row in rows:
            for collision in row["movements"]:
                if collision["kind"] != "CONNECTION" or not collision["existing_word"]:
                    continue
                for prior_row in rows:
                    for prior in prior_row["movements"]:
                        if (prior["kind"] == "BRANCH"
                                and prior["word"] == collision["existing_word"]
                                and prior["to"] == collision["to"]
                                and collision["from"] != prior["word"]):
                            found = (row, collision, prior_row, prior)
                            break
                    if found:
                        break
                if found:
                    break
            if found:
                break
        self.assertIsNotNone(found)
        row, collision, prior_row, prior = found
        self.verifier.bind_lane(collision["from"], "lane-left")
        self.verifier.bind_lane(prior["word"], "lane-right")
        relation = "state:" + ",".join(map(str, collision["to"]))
        left = Observation("left", "lane-left", "RELATION", relation,
                           movement_ref(row["entry_hash"], collision), "", 1)
        right = Observation("right", "lane-right", "RELATION", relation,
                            movement_ref(prior_row["entry_hash"], prior), "", 2)
        self.assertTrue(self.verifier.verify_observation(left))
        self.assertTrue(self.verifier.verify_observation(right))
        self.assertTrue(self.verifier.verify_connection(left, right))
        same_lane = Observation("right2", "lane-left", "RELATION", relation,
                                right.witness_ref, "", 3)
        self.assertFalse(self.verifier.verify_connection(left, same_lane))
        mismatched = Observation("right3", "lane-right", "RELATION", "state:9,9,9",
                                 right.witness_ref, "", 4)
        self.assertFalse(self.verifier.verify_connection(left, mismatched))

    def test_journal_tamper_invalidates_existing_witness(self):
        advance(self.data, execute=True)
        row = replayed_rows(self.journal)[0]
        movement = next(m for m in row["movements"] if m["kind"] == "BRANCH")
        self.verifier.bind_lane(movement["from"], "root")
        obs = Observation("o1", "root", "BRANCH", movement["word"],
                          movement_ref(row["entry_hash"], movement),
                          "finite-required-edge-prefilter", 1)
        self.assertTrue(self.verifier.verify_observation(obs))
        saved = json.loads(self.journal.read_text().splitlines()[0])
        saved["movements"][0]["to"] = [2, 2, 2]
        self.journal.write_text(json.dumps(saved) + "\n")
        self.assertFalse(self.verifier.verify_observation(obs))


if __name__ == "__main__":
    unittest.main()
