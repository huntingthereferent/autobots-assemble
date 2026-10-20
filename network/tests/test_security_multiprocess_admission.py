"""Independent-process signed native ingress, not an in-process thread test.

Each spawned process constructs its OWN HandoffRuntime and SealedRuntimeJournal
from the same pre-existing SQLite history before a synchronized start. One
commits and the stale instance MUST fail closed without consuming admission.
These tests establish single-host filesystem/SQLite behavior only.
"""
from __future__ import annotations

import multiprocessing
import os
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey

from runtime.engine import HandoffRuntime
from runtime.handoff import ExecutionResult, Handoff
from security.continuation import ReplayLedger
from security.runtime_ingress import (
    AuthenticatedHandoffIngress, IngressAuthority, seal_handoff, seal_result,
)
from security.sealed_journal import SealedRuntimeJournal, SealedJournalError


def _independent_process_worker(base, journal_key, mode, suffix,
                                ready, start, responses):
    """Spawn importable process target; errors are reported, never ignored."""
    try:
        root = Path(base)
        runtime = HandoffRuntime(event_store=SealedRuntimeJournal(
            root / "history.sealed.sqlite", key=journal_key))
        ledger = ReplayLedger(root / ("unused-replay-" + suffix + ".sqlite"))
        signer = Ed25519PrivateKey.generate()
        recipient = X25519PrivateKey.generate()
        actor, peer = (("owner", "worker") if mode == "submit"
                       else ("worker", "owner"))
        ingress = AuthenticatedHandoffIngress(
            runtime, ledger,
            IngressAuthority("multiprocess", actor, peer,
                             signer.public_key(), recipient))
        if mode == "submit":
            handoff = Handoff(handoff_id="job-" + suffix,
                              referent="bounded-movement",
                              from_actor="owner", to_actor="worker",
                              required_relation="observe")
            envelope = seal_handoff(
                handoff, lane="multiprocess", parent_sha256=None,
                sender_private_key=signer,
                recipient_public_key=recipient.public_key())
        else:
            parent_id = runtime.state("shared").last_event_id
            envelope = seal_result(
                "shared", parent_id, ExecutionResult(status="UNKNOWN",
                                                     output={"source": suffix}),
                event_id="result-" + suffix,
                lane="multiprocess", parent_sha256=None,
                sender_private_key=signer,
                recipient_public_key=recipient.public_key())
        # Parent releases both ONLY after both runtimes have replayed history.
        ready.put(("ready", suffix))
        if not start.wait(timeout=25):
            responses.put(("error", suffix, "synchronization timeout"))
            return
        try:
            if mode == "submit":
                state = ingress.submit(envelope)
            else:
                state = ingress.return_result(envelope, handoff_id="shared")
            responses.put(("committed", suffix, state.status))
        except SealedJournalError as exc:
            responses.put(("stale", suffix, str(exc)))
        except Exception as exc:
            responses.put(("error", suffix, type(exc).__name__ + ": " + str(exc)))
    except BaseException as exc:
        responses.put(("error", suffix, type(exc).__name__ + ": " + str(exc)))


class SeparateProcessNativeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.key = os.urandom(32)
        self.path = self.base / "history.sealed.sqlite"
        SealedRuntimeJournal(self.path, key=self.key)

    def _counts(self):
        with sqlite3.connect(self.path) as db:
            return (db.execute("SELECT COUNT(*) FROM records").fetchone()[0],
                    db.execute("SELECT COUNT(*) FROM admitted").fetchone()[0])

    def _race(self, mode):
        # Use spawn, not fork: no parent runtime objects, locks or SQLite
        # connections can be inherited into either competing process.
        ctx = multiprocessing.get_context("spawn")
        ready = ctx.Queue()
        answers = ctx.Queue()
        gate = ctx.Event()
        processes = [
            ctx.Process(target=_independent_process_worker,
                        args=(str(self.base), self.key, mode, suffix,
                              ready, gate, answers))
            for suffix in ("a", "b")
        ]
        try:
            for proc in processes:
                proc.start()
            loaded = [ready.get(timeout=25), ready.get(timeout=25)]
            self.assertEqual({x[1] for x in loaded}, {"a", "b"})
            self.assertTrue(all(x[0] == "ready" for x in loaded))
            gate.set()
            output = [answers.get(timeout=25), answers.get(timeout=25)]
            for proc in processes:
                proc.join(timeout=25)
                self.assertFalse(proc.is_alive(), "spawned worker failed to stop")
                self.assertEqual(proc.exitcode, 0)
            return output
        finally:
            gate.set()
            for proc in processes:
                if proc.is_alive():
                    proc.terminate()
                    proc.join(timeout=5)
                if proc.pid is not None:
                    proc.close()
            for queue in (ready, answers):
                queue.close()
                queue.join_thread()

    def test_two_independent_processes_cannot_both_advance_one_snapshot(self):
        decisions = self._race("submit")
        self.assertEqual(sorted(x[0] for x in decisions), ["committed", "stale"])
        self.assertEqual(self._counts(), (1, 1))
        self.assertTrue(any("restart required" in x[2] for x in decisions
                            if x[0] == "stale"))
        rebuilt = HandoffRuntime(event_store=SealedRuntimeJournal(
            self.path, key=self.key))
        self.assertEqual(len(rebuilt.snapshot()), 1)
        self.assertEqual(len(rebuilt.event_store.all()), 1)

    def test_independent_results_cannot_both_extend_same_native_parent(self):
        runtime = HandoffRuntime(event_store=SealedRuntimeJournal(
            self.path, key=self.key))
        runtime.submit(Handoff(handoff_id="shared", referent="finite test",
                               from_actor="owner", to_actor="worker",
                               required_relation="observe"))
        decisions = self._race("result")
        self.assertEqual(sorted(x[0] for x in decisions), ["committed", "stale"])
        self.assertEqual(self._counts(), (2, 1))
        rebuilt = HandoffRuntime(event_store=SealedRuntimeJournal(
            self.path, key=self.key))
        history = rebuilt.event_store.for_handoff("shared")
        self.assertEqual(len(history), 2)
        self.assertEqual([x.event_type for x in history], ["CREATED", "RESULT"])
        self.assertEqual(rebuilt.state("shared").status, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
