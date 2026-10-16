"""B12 actual persisted B3 source -> signed B11 delivery (native CI tests).

Each fixture runs the repository's real B3 subprocess to produce the source
return. The CP observation used to first build its lane is a marked fixture;
the private Ed25519 signer here is ephemeral and not a production identity.
"""
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from runtime.engine import HandoffRuntime
from runtime.handoff import HandoffEvent
from systems.workspace.b12_b3_native_delivery import (
    B12B3LocalDelivery, B3NativeLocalSource, RELATION, SOURCE_NAME,
)
from systems.workspace.workstation_construction import WorkstationConstruction
from systems.workspace.observed_event_journal import LOCAL_PASS, START, OBSERVED


class B12NativeB3SourceTests(unittest.TestCase):
    def setUp(self):
        # Import inside setup so unittest does not collect B3's own TestCase
        # as part of the B12 suite. Those tests run in their native suite.
        from network.tests.test_workstation_native_feedback_integration import (
            RealNativeFeedbackTests,
        )
        self.native = RealNativeFeedbackTests(
            "test_true_native_worker_executes_and_return_is_recorded_on_original_lane"
        )
        self.native.setUp()
        self.addCleanup(self.native.doCleanups)
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.signer = Ed25519PrivateKey.generate()
        self.public = self.signer.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        self.calls = 0
        self.source = B3NativeLocalSource(
            data_dir=self.native.data, lane_handoff_id=self.native.lane_id,
            opening_id=self.native.harness.admit_native_help(
                self.native.lane_id
            )["native_help"]["opening_id"],
            job_id=self.native.job_id,
        )
        self.graph = WorkstationConstruction(self.root / "construction")
        self.goal = self.graph.goal("Deliver real native B3 result", provenance="requested:B12")
        self.candidate = self.graph.candidate(
            self.goal, RELATION, provenance="candidate:source-owning-B3"
        )
        self.route = (self.candidate, self.goal)
        self.edition = self.native.runtime().get(
            self.native.job_id).metadata["edition_fingerprint"]
        self.graph.suggest_source(
            self.candidate, worker_id=SOURCE_NAME,
            edition_ref=self.edition,
            source_locator="b3-native://" + self.native.job_id,
            reason="native source must be reverified; suggestion not authorization",
        )
        self.native_result = None

    def complete_native(self):
        if self.native_result is None:
            self.native_result = self.native.advance()
        return self.native_result

    def signer_callback(self, content):
        self.calls += 1
        return self.signer.sign(content)

    def make(self, *, key=None, signer=None, confirm=None):
        return B12B3LocalDelivery(
            construction=self.graph, source=self.source,
            observed_journal_path=self.root / "observed.jsonl",
            pinned_public_key=self.public if key is None else key,
            sign_native_proof=signer if signer is not None else self.signer_callback,
            confirm_source_job=self.native.job_id if confirm is None else confirm,
        )

    def test_source_refuses_worker_that_has_not_executed(self):
        with self.assertRaises(ValueError):
            self.source.inspect()
        self.assertEqual(self.calls, [])

    def test_original_native_return_rechecked_without_new_worker_execution(self):
        self.complete_native()
        before = self.native.runtime().state(self.native.job_id)
        observed = self.source.inspect()
        self.assertEqual(observed.job_id, self.native.job_id)
        self.assertEqual(observed.edition_fingerprint, self.edition)
        self.assertEqual(observed.output_sha256, self.native_result.output_sha256)
        self.assertEqual(observed.evidence_sha256, self.native_result.evidence_sha256)
        self.assertEqual(len(observed.native_receipt_sha256), 64)
        self.assertEqual(self.native.runtime().state(self.native.job_id).output, before.output)
        self.assertFalse(self.graph.next_construction_handoffs(self.goal)["whole_chain_verified"])

    def test_end_to_end_native_B3_signed_delivery_crosses_only_candidate(self):
        self.complete_native()
        source_journal = self.native.data / "runtime.jsonl"
        service = self.make()
        req = service.prepare(self.goal, self.candidate, route=self.route)
        self.assertEqual(self.calls, [])
        self.assertEqual(service.bridge.projection(req)["state"], "OPEN")
        old = source_journal.read_bytes()
        service.deliver(req, confirm_request=req, allow_native_local_delivery=True)
        self.assertEqual(self.calls, 1)
        self.assertEqual(service.bridge.projection(req)["state"], "CROSSED")
        self.assertFalse(service.bridge.projection(req)["whole_route_verified"])
        self.assertFalse(service.bridge.projection(req)["join_observed"])
        self.assertFalse(self.graph.next_construction_handoffs(self.goal)["whole_chain_verified"])
        self.assertEqual(old, source_journal.read_bytes())
        self.assertEqual(self.native.runtime().state(self.native.job_id).status, "COMPLETE")
        events = service.delivery.journal.for_handoff(req)
        self.assertEqual(sum(x.event_type == LOCAL_PASS for x in events), 1)
        self.assertEqual(sum(x.event_type == START for x in events), 1)
        self.assertEqual(sum(x.event_type == OBSERVED for x in events), 1)

    def test_preparation_remains_inert(self):
        self.complete_native()
        service = self.make()
        req = service.prepare(self.goal, self.candidate, route=self.route)
        self.assertEqual(self.calls, [])
        self.assertEqual(service.bridge.projection(req)["state"], "OPEN")

    def test_exact_request_and_explicit_delivery_authorization_required(self):
        self.complete_native()
        service = self.make()
        req = service.prepare(self.goal, self.candidate, route=self.route)
        with self.assertRaises(PermissionError):
            service.deliver(req, confirm_request=req)
        with self.assertRaises(PermissionError):
            service.deliver(req, confirm_request="wrong", allow_native_local_delivery=True)
        self.assertEqual(self.calls, [])
        self.assertEqual(service.bridge.projection(req)["state"], "OPEN")

    def test_exact_native_source_job_authorization_required(self):
        self.complete_native()
        with self.assertRaises(PermissionError):
            self.make(confirm="someone-else")
        self.assertEqual(self.calls, [])

    def test_malformed_signer_callback_or_signature_fails_closed(self):
        self.complete_native()
        with self.assertRaises(TypeError):
            self.make(signer=1234)
        service = self.make(signer=lambda raw: b"short")
        req = service.prepare(self.goal, self.candidate, route=self.route)
        with self.assertRaisesRegex(ValueError, "Ed25519 signature"):
            service.deliver(req, confirm_request=req, allow_native_local_delivery=True)
        self.assertEqual(service.bridge.projection(req)["state"], "OPEN")

    def test_wrong_externally_pinned_key_cannot_admit_delivery(self):
        self.complete_native()
        wrong = Ed25519PrivateKey.generate().public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        service = self.make(key=wrong)
        req = service.prepare(self.goal, self.candidate, route=self.route)
        with self.assertRaisesRegex(ValueError, "not independently admitted"):
            service.deliver(req, confirm_request=req, allow_native_local_delivery=True)
        self.assertEqual(service.bridge.projection(req)["state"], "OPEN")

    def test_incorrect_b3_job_or_opening_is_not_equivalent_source(self):
        self.complete_native()
        for kwargs in (
            {"job_id": "someone-else"},
            {"opening_id": "someone-else"},
            {"lane_handoff_id": "someone-else"},
        ):
            with self.subTest(kwargs=kwargs):
                another = B3NativeLocalSource(
                    data_dir=self.native.data,
                    lane_handoff_id=kwargs.get("lane_handoff_id", self.source.lane_id),
                    opening_id=kwargs.get("opening_id", self.source.opening_id),
                    job_id=kwargs.get("job_id", self.source.job_id),
                )
                with self.assertRaises((ValueError, KeyError)):
                    another.inspect()

    def test_unmatched_b9_source_hint_is_not_delivery_authorization(self):
        self.complete_native()
        service = self.make()
        alternative = self.graph.candidate(
            self.goal, RELATION, provenance="candidate:other"
        )
        with self.assertRaisesRegex(ValueError, "not present"):
            service.prepare(self.goal, alternative, route=(alternative, self.goal))
        self.assertEqual(self.calls, [])

    def test_wrong_candidate_relation_fails_before_signing(self):
        self.complete_native()
        other = self.graph.candidate(
            self.goal, "a different unproven relation", provenance="candidate:other"
        )
        self.graph.suggest_source(
            other, worker_id=SOURCE_NAME, edition_ref=self.edition,
            source_locator="b3-native://" + self.native.job_id,
            reason="unproven source suggestion",
        )
        service = self.make()
        with self.assertRaisesRegex(ValueError, "does not claim"):
            service.prepare(self.goal, other, route=(other, self.goal))
        self.assertEqual(self.calls, [])

    def test_source_edition_mutation_revokes_live_B3_result(self):
        self.complete_native()
        service = self.make()
        req = service.prepare(self.goal, self.candidate, route=self.route)
        job = self.native.runtime().get(self.native.job_id)
        version = job.metadata["worker_version"]
        folder, _ = self.native.desk._read("finite-required-edge-prefilter", version)
        file = folder / "finite_required_edge_guard.py"
        file.write_text(file.read_text(encoding="utf8") + "\n# post-verification change\n",
                        encoding="utf8")
        with self.assertRaises(ValueError):
            service.deliver(req, confirm_request=req, allow_native_local_delivery=True)
        self.assertEqual(self.calls, [])
        self.assertEqual(service.bridge.projection(req)["state"], "OPEN")

    def test_source_cannot_be_rebound_to_other_native_edition(self):
        self.complete_native()
        service = self.make()
        req = service.prepare(self.goal, self.candidate, route=self.route)
        handoff = HandoffRuntime(event_store=service.delivery.journal).get(req)
        self.assertEqual(handoff.metadata["continuation_source_binding"],
                         {"name": SOURCE_NAME, "edition": self.edition})
        self.assertNotEqual(req, self.native.job_id)

    def test_duplicate_signed_delivery_never_duplicates_native_attempt(self):
        self.complete_native()
        service = self.make()
        req = service.prepare(self.goal, self.candidate, route=self.route)
        first = service.deliver(req, confirm_request=req, allow_native_local_delivery=True)
        second = service.deliver(req, confirm_request=req, allow_native_local_delivery=True)
        self.assertEqual(first.event_id, second.event_id)
        self.assertEqual(sum(e.event_type == START
                             for e in service.delivery.journal.for_handoff(req)), 1)
        restarted = self.make()
        self.assertEqual(restarted.prepare(self.goal, self.candidate, route=self.route), req)
        self.assertEqual(restarted.bridge.projection(req)["state"], "CROSSED")

    def test_stale_B9_route_is_not_promoted_by_fresh_native_B3_result(self):
        self.complete_native()
        service = self.make()
        req = service.prepare(self.goal, self.candidate, route=self.route)
        self.graph.candidate(
            self.candidate, "new missing upstream requirement", provenance="new:scope",
        )
        with self.assertRaisesRegex(ValueError, "not independently admitted"):
            service.deliver(req, confirm_request=req, allow_native_local_delivery=True)
        self.assertEqual(service.bridge.projection(req)["state"], "OPEN")

    def test_false_local_pass_is_rejected_without_native_observation(self):
        self.complete_native()
        service = self.make()
        req = service.prepare(self.goal, self.candidate, route=self.route)
        service.delivery.journal.append(HandoffEvent.create(
            handoff_id=req, event_type=LOCAL_PASS,
            actor_id="claimed-B3", data={"status": "PASS"},
        ))
        self.assertEqual(service.bridge.projection(req)["state"], "OPEN")
        self.assertFalse(any(e.event_type == START for e in
                             service.delivery.journal.for_handoff(req)))


if __name__ == "__main__":
    unittest.main()
