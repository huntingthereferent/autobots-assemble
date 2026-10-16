"""Native B3 subprocess -> event journal continuation, not a simulated worker.

The initial LOCAL_PASS is a bounded test fixture. B3 execution and return
reverification are the repository's real source-owned implementations.
This tests a native finite helper only, not B9 deployment, W13, or owner CP.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from network.tests.test_workstation_native_feedback_integration import RealNativeFeedbackTests
from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff, HandoffEvent
from systems.workspace.branch_help import verify_return
from systems.workspace.workstation_native_feedback import canonical_digest
from systems.workspace.main_referent_selector import Capability, Witness
from systems.workspace.observed_event_journal import (
    ObservedEventJournal, SourceAdapter, LOCAL_PASS, START, OBSERVED
)

RELATION = 'source-owned native finite return reverified'


class NativeEventIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Reuse the same canonical ProcessWorkstation + B2 + B3 test construction
        # as the existing native B3 suite, not a synthetic run_job callback.
        self.native = RealNativeFeedbackTests(
            'test_true_native_worker_executes_and_return_is_recorded_on_original_lane'
        )
        self.native.setUp()
        self.addCleanup(self.native.doCleanups)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        native_job = self.native.runtime().get(self.native.job_id)
        self.edition = native_job.metadata['edition_fingerprint']
        self.execution_calls = 0
        cap = Capability('finite-source-native', self.edition, (RELATION,), True)

        def execute(c):
            self.execution_calls += 1
            return self.native.feedback.advance(
                self.native.lane_id,
                confirm_execute=self.native.job_id,
                allow_local_execution=True
            )

        def observe(c, native_return):
            # Verify AGAIN using the original source-owner verifier, from
            # native persisted state. Do not trust a returned success label.
            native_state = self.native.runtime().state(self.native.job_id)
            independently_checked = verify_return(
                data_dir=self.native.harness.data_dir,
                opening_id=native_return.opening_id
            )
            accepted = (
                independently_checked.get('state') == 'RETURN_RECORDED_REVERIFY_BEFORE_USE'
                and independently_checked.get('parent_cp_witnessed') is False
                and independently_checked.get('child', {}).get('job_id') == self.native.job_id
                and native_return.job_id == self.native.job_id
                and native_return.coordination_handoff_id == self.native.lane_id
                and native_state.status == 'COMPLETE'
                and canonical_digest(native_state.output) == native_return.output_sha256
                and canonical_digest([getattr(e, '__dict__', {}) for e in native_state.evidence])
                    == native_return.evidence_sha256
                and self.native.runtime().get(self.native.job_id).metadata.get(
                    'edition_fingerprint') == c.edition
                and not native_return.checkpoint_pass
            )
            return Witness(
                'SUPPORTED' if accepted else 'UNKNOWN',
                c.edition, (RELATION,) if accepted else (),
                'source-native://' + self.native.job_id if accepted else '',
                accepted
            )

        self.handoff_id = 'event-native-integration'
        self.journal = ObservedEventJournal(
            Path(self.temp.name) / 'observed.jsonl',
            adapters=(SourceAdapter(cap, execute, observe),),
            verify_local_pass=lambda h, e: (
                h.handoff_id == self.handoff_id
                and e.actor_id == 'bounded-local-test'
                and e.data.get('suite') == 'passed'
            )
        )
        rt = HandoffRuntime(event_store=self.journal)
        rt.submit(Handoff(
            handoff_id=self.handoff_id, referent='native B3 execution observation',
            from_actor='native-test', to_actor='finite-source-native',
            required_relation=RELATION
        ))

    def emit_local_pass(self):
        return self.journal.append(HandoffEvent.create(
            handoff_id=self.handoff_id, event_type=LOCAL_PASS,
            actor_id='bounded-local-test', data={'suite': 'passed'}
        ))

    def test_local_pass_triggers_real_native_subprocess_and_independent_reverification(self):
        self.assertEqual(self.native.runtime().state(self.native.job_id).status, 'READY')
        self.emit_local_pass()
        self.assertEqual(self.execution_calls, 1)
        self.assertEqual(self.native.runtime().state(self.native.job_id).status, 'COMPLETE')
        self.assertEqual(self.journal.projection(self.handoff_id)['state'], 'CROSSED')
        recorded = self.journal.for_handoff(self.handoff_id)
        self.assertEqual(sum(e.event_type == START for e in recorded), 1)
        self.assertEqual(sum(e.event_type == OBSERVED for e in recorded), 1)
        self.assertFalse(self.native.feedback.historical_returns(self.native.lane_id)[0][
            'parent_cp_witnessed'])
        self.emit_local_pass()
        self.assertEqual(self.execution_calls, 1)

    def test_invalidated_native_source_observation_preserves_failure(self):
        # B3's own native preflight must refuse withdrawn branch evidence.
        self.native.witness_allowed = False
        self.emit_local_pass()
        self.assertEqual(self.execution_calls, 1)
        self.assertEqual(self.native.runtime().state(self.native.job_id).status, 'READY')
        self.assertEqual(self.journal.projection(self.handoff_id)['state'], 'OPEN')
        outcomes = [e.data['observed'] for e in self.journal.for_handoff(self.handoff_id)
                    if e.event_type == OBSERVED]
        self.assertEqual(outcomes, ['ATTEMPT_ERROR'])
        self.emit_local_pass()
        self.assertEqual(self.execution_calls, 1)


if __name__ == '__main__':
    unittest.main()
