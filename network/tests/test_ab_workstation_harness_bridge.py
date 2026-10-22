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
        self.workstation_dir = self.data / "workstation"
        self.workers = {
            "finite-required-edge-prefilter": "source-edition:finite-prefilter-v1",
            "relation-connector": "source-edition:relation-connector-v1",
        }
        self.verifier = ABClusterWitnessVerifier(self.journal, self.workstation_dir)
        self.harness = self.make_harness()

    def make_harness(self):
        return WorkstationContinuationHarness(
            self.workstation_dir,
            verify_observation=self.verifier.verify_observation,
            verify_connection=self.verifier.verify_connection,
            worker_editions=self.workers,
        )

    def test_verified_branch_creates_only_a_ready_coordination_lane(self):
        advance(self.cluster_dir, execute=True)
        row = replayed_rows(self.journal)[0]
        movement = next(m for m in row["movements"] if m["kind"] == "BRANCH")
        self.harness.seed_lane("root", "finite A/B root")
        self.verifier.bind_lane(movement["from"], "root")
        self.harness.observe(
            lane_id="root", kind="BRANCH", relation=movement["word"],
            witness_ref=movement_ref(row["entry_hash"], movement),
            capability="finite-required-edge-prefilter",
        )
        result = self.harness.tick()
        self.assertEqual(len(result["born_coordination_lanes"]), 1)
        self.assertFalse(result["execution_started"])
        self.assertFalse(result["native_checkpoint_pass"])
        child_handoff_id = result["born_coordination_lanes"][0]
        child = self.harness._runtime().get(child_handoff_id)
        self.assertEqual(child.metadata["parents"], ["root"])
        self.verifier.bind_lane(movement["word"], child_handoff_id)
        self.assertEqual(self.harness.tick()["born_coordination_lanes"], [])

        # The next mathematical wave can now address the actual coordination lane
        # created for this path; it does not need a fabricated worker identity.
        advance(self.cluster_dir, execute=True, workers=3)
        next_rows = replayed_rows(self.journal)
        next_movement = next(m for row2 in next_rows for m in row2["movements"]
                             if m["from"] == movement["word"])
        self.assertEqual(self.verifier.lane_to_path[child.metadata["lane_id"]],
                         movement["word"])
        if next_movement["kind"] == "BRANCH":
            from systems.workspace.workstation_continuation import Observation
            obs = Observation("next-branch", child.metadata["lane_id"], "BRANCH",
                              next_movement["word"],
                              movement_ref(next(row2 for row2 in next_rows
                                                if next_movement in row2["movements"])["entry_hash"],
                                           next_movement),
                              "finite-required-edge-prefilter", 99)
        else:
            from systems.workspace.workstation_continuation import Observation
            obs = Observation("next-relation", child.metadata["lane_id"], "RELATION",
                              "state:" + ",".join(map(str, next_movement["to"])),
                              movement_ref(next(row2 for row2 in next_rows
                                                if next_movement in row2["movements"])["entry_hash"],
                                           next_movement), "", 99)
        self.assertTrue(self.verifier.verify_observation(obs))

    def test_real_collision_joins_only_after_both_witnesses_verify(self):
        selected = None
        for _ in range(12):
            result = advance(self.cluster_dir, execute=True, workers=3)
            rows = replayed_rows(self.journal)
            for row in rows:
                for collision in row["movements"]:
                    if (collision["kind"] != "CONNECTION" or not collision["existing_word"]
                            or collision["from"] == collision["existing_word"]):
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
        left_lane, right_lane = "path-left", "path-right"
        self.harness.seed_lane(left_lane, "A/B trajectory " + collision["from"])
        self.harness.seed_lane(right_lane, "A/B trajectory " + prior["word"])
        self.verifier.bind_lane(collision["from"], left_lane)
        self.verifier.bind_lane(prior["word"], right_lane)
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

    def test_restart_restores_bindings_and_rechecks_observation(self):
        advance(self.cluster_dir, execute=True)
        row = replayed_rows(self.journal)[0]
        movement = next(m for m in row["movements"] if m["kind"] == "BRANCH")
        self.harness.seed_lane("root", "finite A/B root")
        self.verifier.bind_lane(movement["from"], "root")
        witness = movement_ref(row["entry_hash"], movement)
        self.harness.observe(lane_id="root", kind="BRANCH", relation=movement["word"],
                             witness_ref=witness,
                             capability="finite-required-edge-prefilter")
        restarted_verifier = ABClusterWitnessVerifier(self.journal, self.workstation_dir)
        restarted_harness = WorkstationContinuationHarness(
            self.workstation_dir,
            verify_observation=restarted_verifier.verify_observation,
            verify_connection=restarted_verifier.verify_connection,
            worker_editions=self.workers,
        )
        inspected = restarted_harness.inspect()
        self.assertEqual(len(inspected["proposals"]), 1)
        self.assertEqual(inspected["proposals"][0]["kind"], "BIRTH")
        self.assertEqual(restarted_verifier.path_to_lane, {movement["from"]: "root"})
        self.assertFalse(inspected["execution_started"])


if __name__ == "__main__":
    unittest.main()
