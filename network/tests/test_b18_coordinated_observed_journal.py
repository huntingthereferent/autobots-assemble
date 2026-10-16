"""B18 lower-level observed journal native admission and interprocess safety.

Ephemeral signer and the B3 native subprocess below are fixtures; production
identity, external ownership, and full B9 route evidence are never inferred.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import HandoffEvent
from runtime.journal import RuntimeJournal
from systems.workspace.b11_native_local_delivery import ACTOR, PROTOCOL
from systems.workspace.b16_delivery_coordination import coordinated_operator_entry
from systems.workspace.b18_coordinated_observed_journal import (
    B18CoordinatedObservedJournal, B18CoordinatedBridge,
)
from systems.workspace.observed_event_journal import (
    LOCAL_PASS, START, OBSERVED,
)


class B18LowLevelAdmissionTests(unittest.TestCase):
    def setUp(self):
        from network.tests.test_b11_native_local_delivery import B11SourceOwnedDeliveryTests
        self.fixture = B11SourceOwnedDeliveryTests(
            "test_preparing_b11_request_does_not_run_any_worker"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fx = self.fixture

    def setup_proof(self):
        first = self.fx.make()
        request = self.fx.prepare(first)
        proof = self.fx.proof(request)
        return first, request, proof, self.fx.sign(proof)

    def test_b11_lower_level_uses_b18_journal_and_bridge(self):
        first, request, proof, signature = self.setup_proof()
        self.assertIsInstance(first.journal, B18CoordinatedObservedJournal)
        self.assertIsInstance(first.bridge, B18CoordinatedBridge)
        self.assertEqual(first.bridge.projection(request)["state"], "OPEN")

    def test_stale_b11_instance_finds_fresh_direct_b9_request(self):
        stale = self.fx.make()
        second = self.fx.make()
        request = self.fx.prepare(second)
        proof = self.fx.proof(request)
        signed = self.fx.sign(proof)
        delivered = stale.deliver(proof, signature_hex=signed)
        self.assertEqual(delivered.handoff_id, request)
        self.assertEqual(stale.bridge.projection(request)["state"], "CROSSED")
        self.assertEqual(len(self.fx.calls), 1)

    def test_stale_b11_instances_only_admit_one_native_attempt(self):
        first, request, proof, signature = self.setup_proof()
        other = self.fx.make()
        a = first.deliver(proof, signature_hex=signature)
        b = other.deliver(proof, signature_hex=signature)
        self.assertEqual(a.event_id, b.event_id)
        persisted = RuntimeJournal(self.fx.journal_path).for_handoff(request)
        self.assertEqual(sum(e.event_type == LOCAL_PASS for e in persisted), 1)
        self.assertEqual(sum(e.event_type == START for e in persisted), 1)
        self.assertEqual(sum(e.event_type == OBSERVED for e in persisted), 1)
        self.assertEqual(len(self.fx.calls), 1)

    def test_direct_b11_concurrent_threads_do_not_duplicate_start(self):
        first, request, proof, signature = self.setup_proof()
        second = self.fx.make()
        barrier = Barrier(2)

        def invoke(obj):
            barrier.wait(timeout=10)
            try:
                return obj.deliver(proof, signature_hex=signature).event_id
            except PermissionError as exc:
                if "busy" not in str(exc):
                    raise
                return "busy"

        with ThreadPoolExecutor(max_workers=2) as pool:
            work = [pool.submit(invoke, d) for d in (first, second)]
            outcome = [x.result(timeout=15) for x in work]
        self.assertTrue(any(x.startswith("evt_b11_") for x in outcome), outcome)
        self.assertTrue(all(x == "busy" or x.startswith("evt_b11_") for x in outcome))
        recorded = RuntimeJournal(self.fx.journal_path).for_handoff(request)
        self.assertEqual(sum(e.event_type == START for e in recorded), 1)
        self.assertEqual(sum(e.event_type == LOCAL_PASS for e in recorded), 1)

    def test_direct_b11_constructor_cannot_recover_under_busy_lock(self):
        first, request, proof, signature = self.setup_proof()
        with coordinated_operator_entry(trust_ledger=self.fx.journal_path):
            with ThreadPoolExecutor(max_workers=1) as pool:
                fut = pool.submit(self.fx.make)
                with self.assertRaisesRegex(PermissionError, "busy"):
                    fut.result()
        self.assertEqual(first.bridge.projection(request)["state"], "OPEN")

    def test_direct_observed_submission_blocks_competing_writer(self):
        first = self.fx.make()
        other = self.fx.make()
        with coordinated_operator_entry(trust_ledger=self.fx.journal_path):
            with ThreadPoolExecutor(max_workers=1) as pool:
                fut = pool.submit(self.fx.prepare, other)
                with self.assertRaisesRegex(PermissionError, "busy"):
                    fut.result()
        self.assertEqual(self.fx.prepare(first), self.fx.prepare(other))

    def test_direct_append_cannot_bypass_observed_lock(self):
        first, request, proof, signature = self.setup_proof()
        bad_pass = HandoffEvent.create(
            handoff_id=request, event_type=LOCAL_PASS, actor_id="not-source",
            data={"suite": "claimed"},
        )
        with coordinated_operator_entry(trust_ledger=self.fx.journal_path):
            with ThreadPoolExecutor(max_workers=1) as pool:
                fut = pool.submit(first.journal.append, bad_pass)
                with self.assertRaisesRegex(PermissionError, "busy"):
                    fut.result()
        self.assertEqual(first.bridge.projection(request)["state"], "OPEN")
        self.assertFalse(any(e.event_type == START for e in
                             RuntimeJournal(self.fx.journal_path).for_handoff(request)))

    def test_low_level_restart_recovers_pass_before_native_start(self):
        first, request, proof, signature = self.setup_proof()
        payload = {"protocol": PROTOCOL, "receipt": vars(proof),
                   "signature": signature}
        saved = HandoffEvent.create(
            handoff_id=request, event_type=LOCAL_PASS, actor_id=ACTOR,
            data=payload,
        )
        # Inject an interrupted append using the raw storage primitive;
        # B18 must not trust the event without B11 native admission.
        RuntimeJournal.append(first.journal, saved)
        later = self.fx.make()
        self.assertEqual(later.bridge.projection(request)["state"], "CROSSED")
        self.assertEqual(sum(e.event_type == START for e in
                             RuntimeJournal(self.fx.journal_path).for_handoff(request)), 1)
        self.assertEqual(len(self.fx.calls), 1)

    def test_low_level_restart_refuses_replay_after_native_start(self):
        first, request, proof, signature = self.setup_proof()
        first.deliver(proof, signature_hex=signature)
        new = self.fx.make()
        new.journal.refresh()
        self.assertEqual(sum(e.event_type == START for e in
                             RuntimeJournal(self.fx.journal_path).for_handoff(request)), 1)
        self.assertEqual(len(self.fx.calls), 1)

    def test_forged_native_pass_remains_unadmitted(self):
        first, request, proof, signature = self.setup_proof()
        with self.assertRaises(ValueError):
            first.deliver(proof, signature_hex="0" * 128)
        self.assertEqual(first.bridge.projection(request)["state"], "OPEN")
        self.assertFalse(any(e.event_type == START for e in
                             RuntimeJournal(self.fx.journal_path).for_handoff(request)))


class B18RealNativeB3Tests(unittest.TestCase):
    def setUp(self):
        from network.tests.test_b12_b3_native_delivery import B12NativeB3SourceTests
        self.fixture = B12NativeB3SourceTests(
            "test_end_to_end_native_B3_signed_delivery_crosses_only_candidate"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.complete_native()
        self.fx = self.fixture

    def test_existing_real_b3_return_delivers_via_coordinated_b11(self):
        old = self.fx.make()
        new = self.fx.make()
        request = old.prepare(self.fx.goal, self.fx.candidate, route=self.fx.route)
        native_before = (self.fx.native.data / "runtime.jsonl").read_bytes()
        event = new.deliver(request, confirm_request=request, allow_native_local_delivery=True)
        self.assertEqual(event.handoff_id, request)
        self.assertEqual(new.bridge.projection(request)["state"], "CROSSED")
        self.assertEqual(native_before, (self.fx.native.data / "runtime.jsonl").read_bytes())
        persisted = RuntimeJournal(self.fx.root / "observed.jsonl").for_handoff(request)
        self.assertEqual(sum(e.event_type == START for e in persisted), 1)

    def test_two_direct_real_b3_services_share_one_attempt(self):
        first = self.fx.make()
        second = self.fx.make()
        request = first.prepare(self.fx.goal, self.fx.candidate, route=self.fx.route)
        a = first.deliver(request, confirm_request=request, allow_native_local_delivery=True)
        b = second.deliver(request, confirm_request=request, allow_native_local_delivery=True)
        self.assertEqual(a.event_id, b.event_id)
        persisted = RuntimeJournal(self.fx.root / "observed.jsonl").for_handoff(request)
        self.assertEqual(sum(e.event_type == START for e in persisted), 1)
        self.assertFalse(second.bridge.projection(request)["whole_route_verified"])


if __name__ == "__main__":
    unittest.main()
