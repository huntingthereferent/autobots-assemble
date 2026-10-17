"""Real bounded mathematical process source -> existing B2, no fake worker."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.ab_relational_cluster import advance, read_history
from systems.workspace.ab_finite_b2_bridge import FiniteABSource
from systems.workspace.workstation_harness import WorkstationContinuationHarness


class NativeFiniteB2BridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._suite_temp = TemporaryDirectory()
        cls.math_data = Path(cls._suite_temp.name)/"finite-native"
        for _ in range(24):
            wave = advance(cls.math_data, execute=True, workers=3)
            if wave["status"] == "QUIET":
                break
        else:
            raise AssertionError("source native worker failed to reach quiet")
        cls.original = cls.math_data/"ab_relational_cluster.jsonl"
        cls.original_head = read_history(cls.original)[1]

    @classmethod
    def tearDownClass(cls):
        cls._suite_temp.cleanup()

    def setUp(self):
        t = TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.data = Path(t.name)/"existing-workstation"

    def witness(self, source=None, head=None):
        return FiniteABSource(source or self.original,
                              expected_head=head or self.original_head)

    def test_01_native_workers_cross_into_real_B2_journal(self):
        source=self.witness()
        result=source.import_into_workstation(self.data,origin="fixture source-native worker")
        self.assertEqual(result["math_states_verified"],27)
        self.assertEqual(result["math_transitions_verified"],54)
        self.assertEqual(result["math_connections_verified"],28)
        self.assertEqual(result["source_native_cross_trajectory_connections"],8)
        self.assertEqual(result["B2_new_unstaffed_openings"],8)
        self.assertEqual(result["B2_relations_exposed"],8)
        self.assertFalse(result["native_connector_available"])
        self.assertFalse(result["bounded_workers_executed_by_bridge"])
        self.assertEqual(set(result["workstation_handoff_ids"]),{"finite-A","finite-B"})
        runtime=HandoffRuntime(event_store=RuntimeJournal(self.data/"runtime.jsonl"))
        self.assertEqual(len(runtime._handoffs),2)
        self.assertEqual(sum(e.event_type=="WORKSTATION_HELP_OPEN"
                             for e in runtime.event_store.all()),8)
        self.assertTrue((self.data/"finite-sources"/"ab_relational_cluster.jsonl").is_file())

    def test_02_replay_returns_only_old_evidence_and_never_borns_worker(self):
        source=self.witness()
        first=source.import_into_workstation(self.data,origin="test")
        journal=self.data/"runtime.jsonl"
        before=journal.read_bytes()
        again=source.import_into_workstation(self.data,origin="test")
        self.assertEqual(again["B2_new_unstaffed_openings"],0)
        self.assertEqual(first["B2_relations_exposed"],again["B2_relations_exposed"])
        self.assertEqual(before,journal.read_bytes())
        runtime=HandoffRuntime(event_store=RuntimeJournal(journal))
        self.assertTrue(all(h.metadata["source_system"]=="workstation-continuation-lane/v1"
                            for h in runtime._handoffs.values()))

    def test_03_no_fake_connection_from_same_lane_or_similar_labels(self):
        source=self.witness()
        source.import_into_workstation(self.data,origin="test")
        saved=self.data/"finite-sources"/"ab_relational_cluster.jsonl"
        evidence=self.witness(saved)
        harness=WorkstationContinuationHarness(
            self.data, verify_observation=evidence.verify_observation,
            verify_connection=evidence.verify_connection, worker_editions={})
        _,_,_,observations,_=harness._snapshot()
        self.assertEqual(len(observations),16)
        valid=[o for o in observations if evidence.verify_observation(o)]
        self.assertEqual(len(valid),16)
        # Different mathematically witnessed final states cannot be linked merely
        # by renaming their relation text in a fabricated observation object.
        from dataclasses import replace
        mismatched=replace(valid[0],relation=valid[-1].relation)
        self.assertFalse(evidence.verify_observation(mismatched))
        self.assertFalse(evidence.verify_connection(valid[0],mismatched))

    def test_04_revoke_native_source_after_intake(self):
        source=self.witness()
        source.import_into_workstation(self.data,origin="test")
        saved=self.data/"finite-sources"/"ab_relational_cluster.jsonl"
        evidence=self.witness(saved)
        saved.write_text(saved.read_text()+"\nnot-a-native-event\n")
        harness=WorkstationContinuationHarness(
            self.data, verify_observation=evidence.verify_observation,
            verify_connection=evidence.verify_connection, worker_editions={})
        self.assertEqual(harness.inspect()["proposals"],[])
        # The original append-only B2 record remains historic rather than
        # turning a revoked journal into a new authority.
        self.assertEqual(len(HandoffRuntime(event_store=RuntimeJournal(
            self.data/"runtime.jsonl"))._handoffs),2)

    def test_05_refuse_incomplete_or_mismatched_native_journal(self):
        with self.assertRaisesRegex(ValueError,"head differs"):
            FiniteABSource(self.original,expected_head="0"*64)
        bad=Path(self.data.parent)/"truncated-native.jsonl"
        bad.write_text(self.original.read_text().splitlines()[0]+"\n")
        with self.assertRaisesRegex(ValueError,"complete witnessed frontier"):
            FiniteABSource(bad,expected_head=read_history(bad)[1])


if __name__ == "__main__":
    unittest.main()
