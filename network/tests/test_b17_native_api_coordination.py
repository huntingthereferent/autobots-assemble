"""B17 direct-Python operator coordination across old objects and concurrent calls.

Ephemeral source-owner signing keys and B3 native subprocess are test fixtures.
No production key, outside authority, remote lock, or universal RuntimeJournal
serialization is inferred from these tests.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Barrier, Thread
import unittest

from runtime.handoff import HandoffEvent
from runtime.journal import RuntimeJournal
from systems.workspace.b11_native_local_delivery import ACTOR, PROTOCOL
from systems.workspace.b14_operator_pin_ledger import (
    B14OperatorTrustedDelivery, OperatorPinLedger,
)
from systems.workspace.b16_delivery_coordination import coordinated_operator_entry
from systems.workspace.observed_event_journal import LOCAL_PASS, START


class B17NativeAPICoordinationTests(unittest.TestCase):
    def setUp(self):
        from network.tests.test_b13_offline_owner_delivery import B13OfflineSourceTests
        self.fixture = B13OfflineSourceTests(
            "test_cross_process_prepare_external_sign_deliver_native"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.execute_b3()
        self.fx = self.fixture.fx

    def host(self):
        return self.fixture.host()

    def b14(self):
        return B14OperatorTrustedDelivery(
            trust_ledger_path=self.fixture.trust_path,
            public_key_path=self.fixture.pin_file,
            expected_public_key_sha256=self.fixture.pin_digest,
            construction_dir=self.fx.graph.data_dir,
            native_data_dir=self.fx.native.data,
            observed_journal_path=self.fx.root / "observed.jsonl",
            lane_handoff_id=self.fx.source.lane_id,
            opening_id=self.fx.source.opening_id,
            job_id=self.fx.source.job_id,
            confirm_source_job=self.fx.source.job_id,
        )

    def envelope(self, request):
        return self.fixture.envelope(request)

    def prepare(self, host):
        return host.prepare(
            goal_id=self.fx.goal, candidate_id=self.fx.candidate,
            route=self.fx.route,
        )

    def test_direct_b13_stale_instance_finds_handoff_written_by_other_instance(self):
        a = self.host()
        b = self.host()  # snapshots before request exists
        request = self.prepare(a)
        signed = self.envelope(b.signing_request(request))
        event = b.deliver(request_id=request, confirm_request=request,
                          approved=True, signed_envelope=signed)
        self.assertEqual(event.handoff_id, request)
        self.assertEqual(b.b12.bridge.projection(request)["state"], "CROSSED")
        self.assertFalse(b.b12.bridge.projection(request)["whole_route_verified"])

    def test_two_stale_direct_b13_hosts_same_signed_proof_only_once(self):
        first = self.host()
        second = self.host()
        request = self.prepare(first)
        signed = self.envelope(first.signing_request(request))
        a = first.deliver(request_id=request, confirm_request=request,
                          approved=True, signed_envelope=signed)
        b = second.deliver(request_id=request, confirm_request=request,
                           approved=True, signed_envelope=signed)
        self.assertEqual(a.event_id, b.event_id)
        observed = RuntimeJournal(self.fx.root / "observed.jsonl").for_handoff(request)
        self.assertEqual(sum(e.event_type == LOCAL_PASS for e in observed), 1)
        self.assertEqual(sum(e.event_type == START for e in observed), 1)

    def test_direct_b14_stale_instances_replay_latest_journal(self):
        one = self.b14()
        two = self.b14()
        request = self.prepare(one)
        signed = self.envelope(two.signing_request(request))
        one.deliver(request_id=request, confirm_request=request,
                    approved=True, signed_envelope=signed)
        two.deliver(request_id=request, confirm_request=request,
                    approved=True, signed_envelope=signed)
        events = RuntimeJournal(self.fx.root / "observed.jsonl").for_handoff(request)
        self.assertEqual(sum(e.event_type == START for e in events), 1)

    def test_direct_api_busy_trust_lock_fails_before_constructor_recovery(self):
        with coordinated_operator_entry(trust_ledger=self.fixture.trust_path):
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self.host)
                with self.assertRaisesRegex(PermissionError, "busy"):
                    future.result()
        # No native B10 journal was created by the rejected direct caller.
        self.assertFalse((self.fx.root / "observed.jsonl").exists())

    def test_direct_b14_constructor_cannot_start_under_busy_observed_lock(self):
        other = self.fx.root / "another-operator-trust.jsonl"
        with coordinated_operator_entry(trust_ledger=other,
                                        observed_journal=self.fx.root / "observed.jsonl"):
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self.b14)
                with self.assertRaisesRegex(PermissionError, "busy"):
                    future.result()
        self.assertFalse((self.fx.root / "observed.jsonl").exists())

    def test_direct_b13_prepare_cannot_ignore_existing_policy_lease(self):
        host = self.host()
        with coordinated_operator_entry(trust_ledger=self.fixture.trust_path):
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self.prepare, host)
                with self.assertRaisesRegex(PermissionError, "busy"):
                    future.result()
        self.assertFalse((self.fx.root / "observed.jsonl").exists())

    def test_direct_operator_policy_revoke_blocked_by_native_session(self):
        with coordinated_operator_entry(trust_ledger=self.fixture.trust_path,
                                        observed_journal=self.fx.root / "observed.jsonl"):
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(
                    self.fixture.trust.revoke,
                    source_name="finite-source-native",
                    source_edition=self.fx.edition,
                    pin_sha256=self.fixture.pin_digest,
                    operator_ref="operator-test",
                    verification_ref="B17-concurrent-policy-lock",
                    confirm_pin_sha256=self.fixture.pin_digest,
                )
                with self.assertRaisesRegex(PermissionError, "busy"):
                    future.result()
        self.assertTrue(self.fixture.trust.is_current(
            "finite-source-native", self.fx.edition, self.fixture.pin_digest))

    def test_direct_policy_serializes_against_concurrent_cli_style_lease(self):
        with coordinated_operator_entry(trust_ledger=self.fixture.trust_path):
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(
                    self.fixture.trust.revoke,
                    source_name="finite-source-native",
                    source_edition=self.fx.edition,
                    pin_sha256=self.fixture.pin_digest,
                    operator_ref="operator-test",
                    verification_ref="B17-cross-interface",
                    confirm_pin_sha256=self.fixture.pin_digest,
                )
                with self.assertRaises(PermissionError):
                    future.result()
        self.assertIsNotNone(self.fixture.trust.current(
            "finite-source-native", self.fx.edition))

    def test_reentrant_same_thread_uses_existing_complete_lock_set(self):
        with coordinated_operator_entry(trust_ledger=self.fixture.trust_path,
                                        observed_journal=self.fx.root / "observed.jsonl"):
            with coordinated_operator_entry(trust_ledger=self.fixture.trust_path,
                                            observed_journal=self.fx.root / "observed.jsonl"):
                request = self.prepare(self.host())
        self.assertIsInstance(request, str)

    def test_nested_lock_set_cannot_expand_and_invert_order(self):
        with coordinated_operator_entry(trust_ledger=self.fixture.trust_path):
            with self.assertRaisesRegex(RuntimeError, "cannot extend"):
                with coordinated_operator_entry(
                        trust_ledger=self.fixture.trust_path,
                        observed_journal=self.fx.root / "observed.jsonl"):
                    pass

    def test_direct_api_concurrent_threads_do_not_repeat_native_attempt(self):
        first, second = self.host(), self.host()
        request = self.prepare(first)
        signed = self.envelope(first.signing_request(request))
        barrier = Barrier(2)

        def deliver(host):
            barrier.wait(timeout=10)
            try:
                return host.deliver(
                    request_id=request, confirm_request=request,
                    approved=True, signed_envelope=signed,
                ).event_id
            except PermissionError as exc:
                if "busy" not in str(exc):
                    raise
                return "busy"

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(deliver, h) for h in (first, second)]
            result = [f.result(timeout=15) for f in futures]
        self.assertTrue(any(x != "busy" for x in result), result)
        self.assertTrue(all(x == "busy" or x.startswith("evt_b11_") for x in result))
        events = RuntimeJournal(self.fx.root / "observed.jsonl").for_handoff(request)
        self.assertEqual(sum(e.event_type == START for e in events), 1)
        self.assertEqual(sum(e.event_type == LOCAL_PASS for e in events), 1)

    def test_direct_constructor_recovers_saved_pass_only_under_lease(self):
        first = self.host()
        request = self.prepare(first)
        signed = self.envelope(first.signing_request(request))
        event = HandoffEvent.create(
            handoff_id=request, event_type=LOCAL_PASS, actor_id=ACTOR,
            data=signed,
        )
        RuntimeJournal.append(first.b12.delivery.journal, event)
        with coordinated_operator_entry(
                trust_ledger=self.fixture.trust_path,
                observed_journal=self.fx.root / "observed.jsonl"):
            with ThreadPoolExecutor(max_workers=1) as pool:
                future = pool.submit(self.host)
                with self.assertRaisesRegex(PermissionError, "busy"):
                    future.result()
            self.assertFalse(any(e.event_type == START for e in
                                 RuntimeJournal(self.fx.root / "observed.jsonl").for_handoff(request)))
        recovered = self.host()
        self.assertEqual(recovered.b12.bridge.projection(request)["state"], "CROSSED")
        self.assertEqual(sum(e.event_type == START for e in
                             RuntimeJournal(self.fx.root / "observed.jsonl").for_handoff(request)), 1)

    def test_direct_host_reloads_source_trust_after_revocation(self):
        host = self.host()
        request = self.prepare(host)
        signed = self.envelope(host.signing_request(request))
        self.fixture.trust.revoke(
            source_name="finite-source-native", source_edition=self.fx.edition,
            pin_sha256=self.fixture.pin_digest, operator_ref="operator-test",
            verification_ref="B17-revoked-current-policy",
            confirm_pin_sha256=self.fixture.pin_digest,
        )
        with self.assertRaises(PermissionError):
            host.deliver(request_id=request, confirm_request=request,
                         approved=True, signed_envelope=signed)
        self.assertFalse(any(e.event_type == START for e in
                             RuntimeJournal(self.fx.root / "observed.jsonl").for_handoff(request)))

    def test_direct_policy_ledger_persists_exact_sequence(self):
        initial = self.fixture.trust.history()
        self.assertEqual(len(initial), 1)
        self.fixture.trust.revoke(
            source_name="finite-source-native", source_edition=self.fx.edition,
            pin_sha256=self.fixture.pin_digest, operator_ref="operator-test",
            verification_ref="B17-sequenced-policy",
            confirm_pin_sha256=self.fixture.pin_digest,
        )
        self.assertEqual([e["kind"] for e in self.fixture.trust.history()],
                         ["ENROLL", "REVOKE"])


if __name__ == "__main__":
    unittest.main()
