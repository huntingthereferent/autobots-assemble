"""B2 integration tests: existing native RuntimeJournal, not an in-memory mock.

Verifier decisions below are synthetic fixtures. They do NOT claim real
domain-native branch or collision evidence. No worker source is executed.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.workstation_harness import WorkstationContinuationHarness


class WorkstationHarnessIntegrationTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name)
        self.allowed = set()
        self.joins = set()
        self.workers = {
            "finite-required-edge-prefilter": "source-edition:fixture-v1",
            "relation-connector": "source-edition:join-fixture-v1",
        }
        self.harness = self.make()
        self.harness.seed_lane("A", "initial independent A")
        self.harness.seed_lane("B", "initial independent B")

    def make(self, workers=None):
        return WorkstationContinuationHarness(
            self.data,
            worker_editions=self.workers if workers is None else workers,
            verify_observation=lambda o: o.witness_ref in self.allowed,
            verify_connection=lambda a, b: frozenset((a.witness_ref, b.witness_ref)) in self.joins,
        )

    def native(self):
        return HandoffRuntime(event_store=RuntimeJournal(self.data / "runtime.jsonl"))

    def branch(self, lane="A", ref="native:branch-1", relation="new reachable direction"):
        return self.harness.observe(lane_id=lane, kind="BRANCH",
                                    relation=relation, witness_ref=ref,
                                    capability="finite-required-edge-prefilter")

    def relation(self, lane, ref, target="shared relation"):
        return self.harness.observe(lane_id=lane, kind="RELATION",
                                    relation=target, witness_ref=ref)

    def test_initial_pair_persisted_with_no_fabricated_workers(self):
        status = self.harness.inspect()
        self.assertEqual({x["id"] for x in status["lanes"]}, {"A", "B"})
        self.assertEqual(status["proposals"], [])
        self.assertFalse(status["execution_started"])
        self.assertEqual(len(self.native().snapshot()), 2)

    def test_intake_claim_does_not_authorize_a_branch_without_verification(self):
        self.branch()
        self.assertEqual(self.harness.tick()["born_coordination_lanes"], [])
        self.assertEqual(len(self.native().snapshot()), 2)

    def test_witnessed_branch_moves_to_its_own_persisted_coordination_lane(self):
        self.branch()
        self.allowed.add("native:branch-1")
        result = self.harness.tick()
        self.assertEqual(len(result["born_coordination_lanes"]), 1)
        child = self.native().get(result["born_coordination_lanes"][0])
        self.assertEqual(child.metadata["parents"], ["A"])
        self.assertEqual(child.metadata["worker_registration"], "source-edition:fixture-v1")
        self.assertEqual(child.to_actor, "workstation-source-admission")
        self.assertEqual(self.native().state(child.handoff_id).status, "READY")
        self.assertFalse(result["execution_started"])
        self.assertFalse(result["native_checkpoint_pass"])

    def test_restart_and_repeated_tick_do_not_duplicate_or_rewrite_history(self):
        self.branch()
        self.allowed.add("native:branch-1")
        self.harness.tick()
        before = (self.data / "runtime.jsonl").read_bytes()
        after = self.make().tick()
        self.assertEqual(after["born_coordination_lanes"], [])
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)
        self.assertEqual(len(self.native().snapshot()), 3)

    def test_unstaffed_opening_remains_until_worker_registration_changes(self):
        self.branch()
        self.allowed.add("native:branch-1")
        missing = self.make(workers={})
        report = missing.tick()
        self.assertEqual(report["born_coordination_lanes"], [])
        self.assertEqual(len(report["open_unstaffed"]), 1)
        before_count = len(self.native().event_store.all())
        self.assertEqual(missing.tick()["open_unstaffed"], [])
        self.assertEqual(len(self.native().event_store.all()), before_count)
        completed = self.make().tick()
        self.assertEqual(len(completed["born_coordination_lanes"]), 1)

    def test_similarity_cannot_join_without_separately_verified_connection(self):
        self.relation("A", "native:relation-A")
        self.relation("B", "native:relation-B")
        self.allowed.update(("native:relation-A", "native:relation-B"))
        self.assertEqual(self.harness.tick()["born_coordination_lanes"], [])
        self.joins.add(frozenset(("native:relation-A", "native:relation-B")))
        created = self.harness.tick()
        self.assertEqual(len(created["born_coordination_lanes"]), 1)
        join = self.native().get(created["born_coordination_lanes"][0])
        self.assertEqual(join.metadata["parents"], ["A", "B"])
        self.assertEqual(join.inputs["parent_lane_ids"], ["A", "B"])

    def test_join_requires_both_fresh_individual_witnesses(self):
        self.relation("A", "native:relation-A")
        self.relation("B", "native:relation-B")
        self.allowed.add("native:relation-A")
        self.joins.add(frozenset(("native:relation-A", "native:relation-B")))
        self.assertEqual(self.harness.tick()["born_coordination_lanes"], [])

    def test_revoked_source_evidence_cannot_cause_future_birth(self):
        self.branch(ref="native:revoked")
        self.allowed.add("native:revoked")
        self.allowed.remove("native:revoked")
        self.assertEqual(self.harness.tick()["born_coordination_lanes"], [])

    def test_unchanged_observation_is_idempotent(self):
        first = self.branch()
        count = len(self.native().event_store.all())
        self.assertEqual(self.branch(), first)
        self.assertEqual(len(self.native().event_store.all()), count)

    def test_second_branch_can_be_born_without_disturbing_first(self):
        self.branch("A", "native:branch-A")
        self.branch("B", "native:branch-B")
        self.allowed.update(("native:branch-A", "native:branch-B"))
        got = self.harness.tick()
        self.assertEqual(len(got["born_coordination_lanes"]), 2)
        children = [self.native().get(h) for h in got["born_coordination_lanes"]]
        self.assertEqual({tuple(x.metadata["parents"]) for x in children},
                         {("A",), ("B",)})

    def test_malformed_intake_fails_closed(self):
        with self.assertRaises(ValueError):
            self.harness.observe(lane_id="missing", kind="BRANCH", relation="x",
                                 witness_ref="ref", capability="x")
        with self.assertRaises(ValueError):
            self.harness.observe(lane_id="A", kind="RELATION", relation="x",
                                 witness_ref="ref", capability="incorrect")
        with self.assertRaises(ValueError):
            self.harness.seed_lane("A", "changed referent")
        with self.assertRaises(ValueError):
            self.harness.seed_lane("../../danger", "unsafe lane")

    def test_missing_verifier_is_not_a_permissive_default(self):
        with self.assertRaises(ValueError):
            WorkstationContinuationHarness(
                self.data, verify_observation=None, verify_connection=lambda a,b: True)

    def test_new_movement_is_part_of_same_runtime_journal(self):
        self.branch()
        self.allowed.add("native:branch-1")
        born = self.harness.tick()["born_coordination_lanes"][0]
        original = self.native()
        self.assertIn(born, original.snapshot())
        self.assertIn(self.harness._handoff_id("A"), original.snapshot())
        self.assertIn(self.harness._handoff_id("B"), original.snapshot())


if __name__ == "__main__":
    unittest.main()
