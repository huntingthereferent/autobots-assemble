"""Integration tests for actual W13 CP evidence entering continuation policy."""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from systems.workspace.game_w13_continuation_bridge import (
    CAPABILITY, RELATION, WITNESS_PREFIX, GameW13ContinuationVerifier,
)
from systems.workspace.game_w13_native import validate_game_request
from systems.workspace.game_w13_native_bridge import GameW13NativeBridge, WORKER_ID, copy_game_source
from systems.workspace.workstation import ProcessWorkstation
from systems.workspace.controls import run_job
from systems.workspace.workstation_harness import WorkstationContinuationHarness

ROOT = Path(__file__).resolve().parents[2]
REQUEST = json.loads(
    (ROOT / "network/tests/fixtures/game_w13_native_cp_example.json").read_text()
)


class GameW13ContinuationBridgeTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name) / "data"
        self.data.mkdir()
        self.job_id = "w13-continuation-test"
        self.lane_id = "w13-parent"
        self.desk = ProcessWorkstation(self.data / "workstation")
        copy_game_source(self.data, version_id="world-v1", allow_copy=True)
        runtime = HandoffRuntime(event_store=RuntimeJournal(self.data / "runtime.jsonl"))
        self.native = GameW13NativeBridge(runtime=runtime, workstation=self.desk)
        self.native.admit(
            version_id="world-v1", inputs=validate_game_request(REQUEST),
            from_actor="local-test-operator", job_id=self.job_id, lane_id=self.lane_id,
        )
        self.verifier = GameW13ContinuationVerifier(self.data)

    def observation(self, lane_id=None, witness_ref=None):
        from systems.workspace.workstation_continuation import Observation
        return Observation(
            id="w13-observation",
            lane_id=lane_id or self.lane_id,
            kind="BRANCH",
            relation=RELATION,
            witness_ref=witness_ref or WITNESS_PREFIX + self.job_id,
            capability=CAPABILITY,
            sequence=0,
        )

    def test_ready_native_job_is_not_continuation_evidence(self):
        self.assertFalse(self.verifier.verify_observation(self.observation()))

    def test_complete_job_is_freshly_reverified_before_lane_birth(self):
        run_job(data_dir=self.data, job_id=self.job_id, confirm_execute=self.job_id)
        self.assertTrue(self.verifier.verify_observation(self.observation()))
        harness = WorkstationContinuationHarness(
            self.data,
            verify_observation=self.verifier.verify_observation,
            verify_connection=self.verifier.verify_connection,
            worker_editions={CAPABILITY: "source-edition:game-w13-continuation-v1"},
        )
        harness.seed_lane(self.lane_id, "verified WORLD W13 native result")
        harness.observe(
            lane_id=self.lane_id, kind="BRANCH", relation=RELATION,
            witness_ref=WITNESS_PREFIX + self.job_id, capability=CAPABILITY,
        )
        result = harness.tick()
        self.assertEqual(len(result["born_coordination_lanes"]), 1)
        self.assertFalse(result["execution_started"])
        self.assertFalse(result["native_checkpoint_pass"])

    def test_wrong_lane_and_unrelated_job_reference_fail_closed(self):
        run_job(data_dir=self.data, job_id=self.job_id, confirm_execute=self.job_id)
        self.assertFalse(self.verifier.verify_observation(self.observation(lane_id="other-lane")))
        self.assertFalse(self.verifier.verify_observation(
            self.observation(witness_ref=WITNESS_PREFIX + "not-a-real-job")
        ))

    def test_two_native_runs_are_not_automatically_a_join_witness(self):
        left, right = self.observation(), self.observation()
        right.id = "second-observation"
        right.lane_id = "another-lane"
        self.assertFalse(self.verifier.verify_connection(left, right))


if __name__ == "__main__":
    unittest.main()
