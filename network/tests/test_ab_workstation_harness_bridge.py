"""Run the replay-backed A/B verifier through the workstation harness."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.ab_relational_cluster import advance
from systems.workspace.ab_workstation_bridge import ABClusterWitnessVerifier, movement_ref, replayed_rows
from systems.workspace.workstation_harness import WorkstationContinuationHarness


class ABWorkstationHarnessBridgeTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.data = Path(temp.name)
        self.cluster_dir = self.data / "cluster"
        self.journal = self.cluster_dir / "ab_relational_cluster.jsonl"
        self.verifier = ABClusterWitnessVerifier(self.journal)
        self.workers = {
            "finite-required-edge-prefilter": "source-edition:finite-prefilter-v1",
            "relation-connector": "source-edition:relation-connector-v1",
        }
        self.harness = self.make_harness()

    def make_harness(self):
        return WorkstationContinuationHarness(
            self.data / "workstation",
            verify_observation=self.verifier.verify_observation,
            verify_connection=self.verifier.verify_connection,
            worker_editions=self.workers,
        )

    def test_verified_branch_creates_only_a_ready_coordination_lane(self):
        advance(self.cluster_dir, execute=True)
        row = replayed_rows(self.journal)[0]
        movement = next(m for m in row["movements"] if m["kind"] == "BRANCH")
        self.harness.seed_lane("root", "finite A/B root")
        self.harness.observe(
            lane_id="root", kind="BRANCH", relation=movement["word"],
            witness_ref=movement_ref(row["entry_hash"], movement),
            capability="finite-required-edge-prefilter",
        )
        result = self.harness.tick()
        self.assertEqual(len(result["born_coordination_lanes"]), 1)
        self.assertFalse(result["execution_started"])
        self.assertFalse(result["native_checkpoint_pass"])
        child = self.harness._runtime().get(result["born_coordination_lanes"][0])
        self.assertEqual(child.metadata["parents"], ["root"])
        self.assertEqual(self.harness.tick()["born_coordination_lanes"], [])

    def test_real_collision_joins_only_after_both_witnesses_verify(self):
        selected = None
        for _ in range(12):
            result = advance(self.cluster_dir, execute=True, workers=3)
            rows = replayed_rows(self.journal)
            for row in rows:
                for collision in row["movements"]:
                    if collision["kind"] != "CONNECTION" or not collision["existing_word"]:
                        continue
                    prior_row = next((candidate for candidate in rows
                                      if any(m["kind"] == "BRANCH"
                                             and m["word"] == collision["existing_word"]
                                             and m["to"] == collision["to"]
                                             for m in candidate["movements"])), None)
                    if prior_row is not None:
                        prior = next(m for m in prior_row["movements"]
                                     if m["kind"] == "BRANCH"
                                     and m["word"] == collision["existing_word"]
                                     and m["to"] == collision["to"])
                        selected = (row, collision, prior_row, prior)
                        break
                if selected:
                    break
            if selected or result["status"] == "QUIET":
                break
        self.assertIsNotNone(selected)
        row, collision, prior_row, prior = selected
        left_lane = "path-" + collision["from"]
        right_lane = "path-" + collision["existing_word"]
        self.harness.seed_lane(left_lane, "A/B trajectory " + collision["from"])
        self.harness.seed_lane(right_lane, "A/B trajectory " + collision["existing_word"])
        relation = "state:" + ",".join(map(str, collision["to"]))
        self.harness.observe(lane_id=left_lane, kind="RELATION", relation=relation,
                             witness_ref=movement_ref(row["entry_hash"], collision))
        self.harness.observe(lane_id=right_lane, kind="RELATION", relation=relation,
                             witness_ref=movement_ref(prior_row["entry_hash"], prior))
        result = self.harness.tick()
        self.assertEqual(len(result["born_coordination_lanes"]), 1)
        joined = self.harness._runtime().get(result["born_coordination_lanes"][0])
        self.assertEqual(joined.metadata["parents"], sorted((left_lane, right_lane)))
        self.assertFalse(result["execution_started"])
        self.assertFalse(result["native_checkpoint_pass"])


if __name__ == "__main__":
    unittest.main()
