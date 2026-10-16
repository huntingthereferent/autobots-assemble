"""B16 interprocess delivery coordination, tested against actual native B3.

The B13 and B14 CLIs both acquire the same local advisory locks before
constructing the B10 journal, which can recover a durable LOCAL_PASS. The
test signer here remains an ephemeral external CI fixture.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.b16_delivery_coordination import (
    coordinated_operator_entry, _lock_path,
)
from systems.workspace.observed_event_journal import LOCAL_PASS, START


class B16CoordinationPrimitiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.trust = self.root / "policy.jsonl"
        self.observed = self.root / "observed.jsonl"

    def test_missing_trust_path_is_not_accepted(self):
        with self.assertRaises(PermissionError):
            with coordinated_operator_entry(trust_ledger=None):
                pass

    def test_policy_file_lock_is_exclusive(self):
        with coordinated_operator_entry(trust_ledger=self.trust):
            with self.assertRaisesRegex(PermissionError, "busy"):
                with coordinated_operator_entry(trust_ledger=self.trust):
                    pass

    def test_different_policies_same_observed_journal_exclude_each_other(self):
        other = self.root / "other-policy.jsonl"
        with coordinated_operator_entry(trust_ledger=self.trust,
                                        observed_journal=self.observed):
            with self.assertRaisesRegex(PermissionError, "busy"):
                with coordinated_operator_entry(trust_ledger=other,
                                                observed_journal=self.observed):
                    pass

    def test_cross_entry_lock_order_never_changes_with_argument_order(self):
        one = self.root / "z-trust"
        two = self.root / "a-observed"
        with coordinated_operator_entry(trust_ledger=one, observed_journal=two):
            with self.assertRaises(PermissionError):
                with coordinated_operator_entry(trust_ledger=two, observed_journal=one):
                    pass

    def test_shared_trust_and_observed_path_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "different"):
            with coordinated_operator_entry(trust_ledger=self.trust,
                                            observed_journal=self.trust):
                pass

    def test_symlinked_journal_is_rejected(self):
        self.trust.write_text("", encoding="utf8")
        alias = self.root / "trust-alias"
        alias.symlink_to(self.trust)
        with self.assertRaisesRegex(ValueError, "symlinked"):
            with coordinated_operator_entry(trust_ledger=alias):
                pass

    def test_lock_file_symlink_is_rejected(self):
        lock = _lock_path(self.trust)
        lock.parent.mkdir(parents=True, exist_ok=True)
        target = self.root / "target"
        target.write_text("unrelated", encoding="utf8")
        lock.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            with coordinated_operator_entry(trust_ledger=self.trust):
                pass
        self.assertEqual(target.read_text(encoding="utf8"), "unrelated")

    def test_persistent_lock_file_is_reusable_without_unlinking(self):
        path = _lock_path(self.trust)
        with coordinated_operator_entry(trust_ledger=self.trust):
            initial = path.stat().st_ino
        self.assertTrue(path.exists())
        with coordinated_operator_entry(trust_ledger=self.trust):
            self.assertEqual(initial, path.stat().st_ino)
        self.assertEqual(initial, path.stat().st_ino)

    def test_lock_file_hardlink_is_rejected(self):
        lock = _lock_path(self.trust)
        lock.write_text("locked", encoding="utf8")
        os.link(lock, self.root / "another-name")
        with self.assertRaisesRegex(ValueError, "ordinary file"):
            with coordinated_operator_entry(trust_ledger=self.trust):
                pass


class B16NativeDeliveryConcurrencyTests(unittest.TestCase):
    def setUp(self):
        from network.tests.test_b13_offline_owner_delivery import B13OfflineSourceTests
        self.fixture = B13OfflineSourceTests(
            "test_cross_process_prepare_external_sign_deliver_native"
        )
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.execute_b3()
        self.fx = self.fixture.fx
        self.trust = self.fixture.trust_path
        self.observed = self.fx.root / "observed.jsonl"
        self.b14_base = [
            sys.executable, "-m", "systems.workspace.b14_operator_cli",
            "--trust-ledger", str(self.trust),
        ]

    def prepare(self):
        return self.fixture.cli(
            "prepare", "--goal-id", self.fx.goal,
            "--candidate-id", self.fx.candidate,
            "--route-node", self.fx.candidate, "--route-node", self.fx.goal,
        )["request_id"]

    def write_signed(self, request):
        unsigned = self.fixture.cli("signing-request", "--request-id", request)
        self.fixture.envelope_path.write_text(
            json.dumps(self.fixture.envelope(unsigned)), encoding="utf8"
        )

    def cmd_b13(self, *args, success=True):
        return self.fixture.cli(*args, ok=success)

    def cmd_b14(self, *args, success=True):
        p = subprocess.run(
            [*self.b14_base, *args], capture_output=True, text=True,
            timeout=20, cwd=Path(__file__).resolve().parents[2],
        )
        if success:
            self.assertEqual(p.returncode, 0, p.stderr)
            return json.loads(p.stdout)
        self.assertNotEqual(p.returncode, 0)
        return p.stderr

    def test_b13_prepare_refuses_busy_trust_before_journal_creation(self):
        with coordinated_operator_entry(trust_ledger=self.trust):
            stderr = self.cmd_b13(
                "prepare", "--goal-id", self.fx.goal,
                "--candidate-id", self.fx.candidate,
                "--route-node", self.fx.candidate,
                "--route-node", self.fx.goal, success=False,
            )
            self.assertIn("busy", stderr)
            self.assertFalse(self.observed.exists())

    def test_b13_prepare_refuses_busy_observed_journal(self):
        with coordinated_operator_entry(
                trust_ledger=self.fx.root / "different-policy.jsonl",
                observed_journal=self.observed):
            stderr = self.cmd_b13(
                "prepare", "--goal-id", self.fx.goal,
                "--candidate-id", self.fx.candidate,
                "--route-node", self.fx.candidate,
                "--route-node", self.fx.goal, success=False,
            )
            self.assertIn("busy", stderr)
            self.assertFalse(self.observed.exists())

    def test_b14_pin_policy_mutation_refuses_busy_native_session(self):
        with coordinated_operator_entry(trust_ledger=self.trust,
                                        observed_journal=self.observed):
            stderr = self.cmd_b14(
                "pin", "--source-edition", self.fx.edition, "revoke",
                "--confirm-prior-sha256", self.fixture.pin_digest,
                "--operator-ref", "operator-test", "--verification-ref",
                "B16-explicit-revocation", success=False,
            )
            self.assertIn("busy", stderr)
            self.assertEqual(self.fixture.trust.current(
                "finite-source-native", self.fx.edition), self.fixture.pin_digest)

    def test_b14_native_cli_refuses_busy_observed_journal(self):
        alternate = self.fx.root / "different-policy.jsonl"
        with coordinated_operator_entry(trust_ledger=alternate,
                                        observed_journal=self.observed):
            stderr = self.cmd_b14(
                "native",
                "--construction-dir", str(self.fx.graph.data_dir),
                "--native-data-dir", str(self.fx.native.data),
                "--observed-journal", str(self.observed),
                "--lane-id", self.fx.source.lane_id,
                "--opening-id", self.fx.source.opening_id,
                "--job-id", self.fx.source.job_id,
                "--confirm-source-job", self.fx.source.job_id,
                "--pinned-public-key", str(self.fixture.pin_file),
                "--expected-public-key-sha256", self.fixture.pin_digest,
                "prepare", "--goal-id", self.fx.goal, "--candidate-id",
                self.fx.candidate, "--route-node", self.fx.candidate,
                "--route-node", self.fx.goal, success=False,
            )
            self.assertIn("busy", stderr)

    def test_concurrent_signed_delivery_one_native_attempt(self):
        request = self.prepare()
        self.write_signed(request)
        args = [
            *self.fixture.cli_base, "deliver", "--request-id", request,
            "--confirm-request", request, "--approve-native-delivery",
            "--signed-envelope", str(self.fixture.envelope_path),
        ]
        commands = [subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            cwd=Path(__file__).resolve().parents[2],
        ) for _ in range(2)]
        outputs = [p.communicate(timeout=20) for p in commands]
        exitcodes = [p.returncode for p in commands]
        # If one loses the race it fails fast. If both run in sequence, the
        # second must find the durable result and return idempotently.
        self.assertIn(0, exitcodes, outputs)
        self.assertTrue(all(code in (0, 1) for code in exitcodes), outputs)
        self.assertTrue(all(
            code == 0 or "busy" in err
            for code, (_, err) in zip(exitcodes, outputs)
        ), outputs)
        host = self.fixture.host()
        events = host.b12.delivery.journal.for_handoff(request)
        self.assertEqual(sum(e.event_type == LOCAL_PASS for e in events), 1)
        self.assertEqual(sum(e.event_type == START for e in events), 1)
        self.assertEqual(host.b12.bridge.projection(request)["state"], "CROSSED")
        self.assertFalse(host.b12.bridge.projection(request)["whole_route_verified"])

    def test_replay_waits_for_same_operator_lock(self):
        from runtime.handoff import HandoffEvent
        from runtime.journal import RuntimeJournal
        from systems.workspace.b11_native_local_delivery import ACTOR
        host = self.fixture.host()
        request = self.fixture.request(host)
        unsigned = host.signing_request(request)
        signed = self.fixture.envelope(unsigned)
        event = HandoffEvent.create(
            handoff_id=request, event_type=LOCAL_PASS, actor_id=ACTOR, data=signed,
        )
        RuntimeJournal.append(host.b12.delivery.journal, event)
        with coordinated_operator_entry(trust_ledger=self.trust,
                                        observed_journal=self.observed):
            stderr = self.cmd_b13("inspect", success=False)
            self.assertIn("busy", stderr)
            current = host.b12.delivery.journal.for_handoff(request)
            self.assertFalse(any(e.event_type == START for e in current))
        self.cmd_b13("inspect")
        reopened = self.fixture.host()
        self.assertEqual(sum(e.event_type == START for e in
                             reopened.b12.delivery.journal.for_handoff(request)), 1)

    def test_revoke_between_commands_blocks_next_delivery(self):
        req = self.prepare()
        self.write_signed(req)
        self.cmd_b14(
            "pin", "--source-edition", self.fx.edition, "revoke",
            "--confirm-prior-sha256", self.fixture.pin_digest,
            "--operator-ref", "operator-test",
            "--verification-ref", "B16-operator-revoked",
        )
        stderr = self.cmd_b13(
            "deliver", "--request-id", req, "--confirm-request", req,
            "--approve-native-delivery", "--signed-envelope",
            str(self.fixture.envelope_path), success=False,
        )
        self.assertIn("revoked", stderr)
        self.assertFalse(any(e.event_type == START for e in
                             self.fixture.host().b12.delivery.journal.for_handoff(req)))


if __name__ == "__main__":
    unittest.main()
