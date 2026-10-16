"""B11 source-owned, pinned-key local-result delivery to B10.

The test signer is ephemeral and must never be treated as a production source
owner. A separate independent native-state verifier is always consulted.
"""
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from runtime.handoff import HandoffEvent
from runtime.journal import RuntimeJournal
from systems.workspace.b11_native_local_delivery import (
    ACTOR, PROTOCOL, NativeLocalProof, SourceOwnedAdmission,
    SourceOwnedLocalDelivery, canonical_proof_bytes,
)
from systems.workspace.main_referent_selector import Capability, Witness
from systems.workspace.observed_event_journal import (
    LOCAL_PASS, START, OPEN, STOP, SourceAdapter,
)
from systems.workspace.workstation_construction import WorkstationConstruction


def raw_public_key(secret):
    return secret.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )


class B11SourceOwnedDeliveryTests(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.data = Path(folder.name)
        self.graph = WorkstationConstruction(self.data / "construction")
        self.goal = self.graph.goal("Deliver checked native output", provenance="user:goal")
        self.middle = self.graph.candidate(
            self.goal, "receive source-owned native result",
            provenance="candidate:local-result",
        )
        self.leaf = self.graph.candidate(
            self.middle, "retrieve an input", provenance="candidate:input",
        )
        self.route = (self.leaf, self.middle, self.goal)
        self.graph.suggest_source(
            self.middle, worker_id="native-owner", edition_ref="sha-v1",
            source_locator="native-source://one", reason="hint only, never owner proof",
        )
        self.signer = Ed25519PrivateKey.generate()
        self.pins = {("native-owner", "sha-v1"): raw_public_key(self.signer)}
        self.source_records = {}
        self.calls = []
        self.accept_attempts = True
        self.journal_path = self.data / "observed.jsonl"

    def verify_native_current(self, proof):
        return self.source_records.get(proof.native_receipt_ref) == (
            proof.native_receipt_sha256, proof.handoff_id,
            proof.source_name, proof.source_edition,
        )

    def adapter(self, *, name="native-owner", edition="sha-v1", authorized=True):
        relation = "receive source-owned native result"
        def execute(cap):
            self.calls.append((cap.name, cap.edition))
            return "native-attempt://validated"
        def observe(cap, result):
            valid = (
                self.accept_attempts and cap.name == "native-owner"
                and cap.edition == "sha-v1"
                and result == "native-attempt://validated"
            )
            return Witness(
                "SUPPORTED" if valid else "UNKNOWN", cap.edition,
                (relation,) if valid else (),
                result if valid else "", valid,
            )
        return SourceAdapter(
            Capability(name, edition, (relation,), authorized), execute, observe,
        )

    def make(self, *, adapters=None, pins=None, current=None):
        return SourceOwnedLocalDelivery(
            construction=self.graph, journal_path=self.journal_path,
            adapters=tuple(adapters) if adapters is not None else (self.adapter(),),
            pinned_public_keys=self.pins if pins is None else pins,
            verify_native_current=current or self.verify_native_current,
        )

    def prepare(self, delivery):
        return delivery.bridge.prepare(
            self.goal, self.middle, route=self.route,
            worker_id="native-owner", edition_ref="sha-v1",
            source_locator="native-source://one",
        )

    def proof(self, handoff_id, *, ref="native-result://one"):
        result_digest = sha256(("verified:" + ref).encode()).hexdigest()
        proof = NativeLocalProof(
            handoff_id=handoff_id, source_name="native-owner", source_edition="sha-v1",
            required_relation="receive source-owned native result",
            candidate_spec_sha256=delivery_spec(self.graph, self.middle),
            source_locator="native-source://one",
            native_receipt_ref=ref, native_receipt_sha256=result_digest,
        )
        self.source_records[ref] = (
            result_digest, handoff_id, "native-owner", "sha-v1",
        )
        return proof

    def sign(self, proof, *, signer=None):
        return (signer or self.signer).sign(canonical_proof_bytes(proof)).hex()

    def test_preparing_b11_request_does_not_run_any_worker(self):
        delivery = self.make()
        before = (self.graph.data_dir / "runtime.jsonl").read_bytes()
        request = self.prepare(delivery)
        self.assertEqual(self.calls, [])
        self.assertEqual(delivery.bridge.projection(request)["state"], "OPEN")
        self.assertEqual(before, (self.graph.data_dir / "runtime.jsonl").read_bytes())

    def test_signature_and_current_native_evidence_start_only_bound_adapter(self):
        competing = self.adapter(name="a-other", edition="v2")
        delivery = self.make(adapters=(competing, self.adapter()))
        request = self.prepare(delivery)
        proof = self.proof(request)
        event = delivery.deliver(proof, signature_hex=self.sign(proof))
        self.assertEqual(event.event_type, LOCAL_PASS)
        self.assertEqual(self.calls, [("native-owner", "sha-v1")])
        self.assertEqual(delivery.bridge.projection(request)["state"], "CROSSED")
        self.assertFalse(delivery.bridge.projection(request)["whole_route_verified"])
        self.assertFalse(self.graph.next_construction_handoffs(self.goal)["execution_authorized"])

    def test_forged_signature_rejected_before_persistence(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        wrong = Ed25519PrivateKey.generate()
        with self.assertRaisesRegex(ValueError, "not independently admitted"):
            delivery.deliver(proof, signature_hex=self.sign(proof, signer=wrong))
        self.assertEqual(self.calls, [])
        self.assertEqual(len([e for e in delivery.journal.for_handoff(request)
                              if e.event_type == LOCAL_PASS]), 0)

    def test_forged_actor_cannot_use_raw_journal_to_execute(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        delivery.journal.append(HandoffEvent.create(
            handoff_id=request, event_type=LOCAL_PASS, actor_id="local-runner",
            data={"protocol": PROTOCOL, "receipt": asdict(proof),
                  "signature": self.sign(proof)},
        ))
        self.assertEqual(self.calls, [])
        self.assertEqual(delivery.bridge.projection(request)["state"], "OPEN")

    def test_replayed_signed_receipt_withdrawn_from_source_fails(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        signature = self.sign(proof)
        self.source_records.clear()
        with self.assertRaisesRegex(ValueError, "not independently admitted"):
            delivery.deliver(proof, signature_hex=signature)
        self.assertEqual(self.calls, [])

    def test_source_can_revoke_after_journal_persistence_before_recovery(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        RuntimeJournal.append(delivery.journal, HandoffEvent.create(
            handoff_id=request, event_type=LOCAL_PASS, actor_id=ACTOR,
            data={"protocol": PROTOCOL, "receipt": asdict(proof),
                  "signature": self.sign(proof)},
        ))
        self.source_records.clear()
        recovered = self.make()
        self.assertEqual(self.calls, [])
        self.assertEqual(recovered.bridge.projection(request)["state"], "OPEN")

    def test_signature_is_bound_to_exact_candidate_handoff(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        other = self.graph.candidate(
            self.goal, "other source requirement", provenance="another:branch",
        )
        changed = NativeLocalProof(**{**asdict(proof), "handoff_id": other})
        with self.assertRaisesRegex(ValueError, "not independently admitted"):
            delivery.deliver(changed, signature_hex=self.sign(proof))
        self.assertEqual(self.calls, [])

    def test_tampering_the_native_receipt_digest_rejected(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        changed = NativeLocalProof(**{
            **asdict(proof), "native_receipt_sha256": "0" * 64,
        })
        with self.assertRaisesRegex(ValueError, "not independently admitted"):
            delivery.deliver(changed, signature_hex=self.sign(proof))
        self.assertEqual(self.calls, [])

    def test_changing_source_edition_or_locator_rejected(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        for field, value in (
            ("source_edition", "sha-v2"), ("source_locator", "native-source://two"),
            ("required_relation", "something unrelated"),
            ("candidate_spec_sha256", "a" * 64),
        ):
            with self.subTest(field=field):
                altered = NativeLocalProof(**{**asdict(proof), field: value})
                with self.assertRaisesRegex(ValueError, "not independently admitted"):
                    delivery.deliver(altered, signature_hex=self.sign(altered))
        self.assertEqual(self.calls, [])

    def test_incorrect_pin_refuses_valid_otherwise_signed_proof(self):
        wrong = Ed25519PrivateKey.generate()
        delivery = self.make(pins={("native-owner", "sha-v1"): raw_public_key(wrong)})
        request = self.prepare(delivery)
        proof = self.proof(request)
        with self.assertRaisesRegex(ValueError, "not independently admitted"):
            delivery.deliver(proof, signature_hex=self.sign(proof))
        self.assertEqual(self.calls, [])

    def test_missing_or_malformed_pins_refused(self):
        for pins in ({}, {("native-owner", "sha-v1"): b"x"},
                     {("native-owner",): raw_public_key(self.signer)}):
            with self.subTest(pins=pins), self.assertRaises(ValueError):
                self.make(pins=pins)

    def test_independent_native_verifier_required(self):
        with self.assertRaisesRegex(TypeError, "independent"):
            SourceOwnedAdmission(
                pinned_public_keys=self.pins, verify_native_current=None
            )

    def test_native_verifier_error_fails_closed(self):
        delivery = self.make(current=lambda proof: (_ for _ in ()).throw(OSError("offline")))
        request = self.prepare(delivery)
        proof = self.proof(request)
        with self.assertRaisesRegex(ValueError, "not independently admitted"):
            delivery.deliver(proof, signature_hex=self.sign(proof))
        self.assertEqual(self.calls, [])

    def test_valid_proof_does_not_claim_crossing_if_native_attempt_fails(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        self.accept_attempts = False
        delivery.deliver(proof, signature_hex=self.sign(proof))
        self.assertEqual(self.calls, [("native-owner", "sha-v1")])
        self.assertEqual(delivery.bridge.projection(request)["state"], "OPEN")
        self.assertFalse(delivery.bridge.projection(request)["whole_route_verified"])

    def test_identical_delivery_is_idempotent_and_durable(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        sig = self.sign(proof)
        first = delivery.deliver(proof, signature_hex=sig)
        second = delivery.deliver(proof, signature_hex=sig)
        self.assertEqual(first.event_id, second.event_id)
        self.assertEqual(self.calls, [("native-owner", "sha-v1")])
        self.assertEqual(sum(e.event_type == LOCAL_PASS
                             for e in delivery.journal.for_handoff(request)), 1)
        restarted = self.make()
        third = restarted.deliver(proof, signature_hex=sig)
        self.assertEqual(first.event_id, third.event_id)
        self.assertEqual(self.calls, [("native-owner", "sha-v1")])

    def test_persisted_signed_pass_recovers_without_duplicate_side_effect(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        RuntimeJournal.append(delivery.journal, HandoffEvent.create(
            handoff_id=request, event_type=LOCAL_PASS, actor_id=ACTOR,
            data={"protocol": PROTOCOL, "receipt": asdict(proof),
                  "signature": self.sign(proof)},
        ))
        self.assertEqual(self.calls, [])
        recovered = self.make()
        self.assertEqual(self.calls, [("native-owner", "sha-v1")])
        self.assertEqual(recovered.bridge.projection(request)["state"], "CROSSED")
        self.make()
        self.assertEqual(self.calls, [("native-owner", "sha-v1")])

    def test_started_external_effect_never_replayed_automatically(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        local = HandoffEvent.create(
            handoff_id=request, event_type=LOCAL_PASS, actor_id=ACTOR,
            data={"protocol": PROTOCOL, "receipt": asdict(proof),
                  "signature": self.sign(proof)},
        )
        RuntimeJournal.append(delivery.journal, local)
        RuntimeJournal.append(delivery.journal, HandoffEvent.create(
            handoff_id=request, event_type=START, actor_id="observed-continuation",
            data={"name": "native-owner", "edition": "sha-v1",
                  "trigger_id": local.event_id},
        ))
        recovered = self.make()
        self.assertEqual(self.calls, [])
        self.assertEqual(recovered.bridge.projection(request)["state"], "RECOVERY_REQUIRED")
        self.assertTrue(any(e.event_type == START for e in recovered.journal.for_handoff(request)))

    def test_stale_construction_route_blocks_signed_result(self):
        delivery = self.make()
        request = self.prepare(delivery)
        proof = self.proof(request)
        self.graph.candidate(
            self.leaf, "new upstream requirement", provenance="new:scope",
        )
        with self.assertRaisesRegex(ValueError, "not independently admitted"):
            delivery.deliver(proof, signature_hex=self.sign(proof))
        self.assertEqual(self.calls, [])


def delivery_spec(graph, candidate_id):
    from dataclasses import asdict
    from systems.workspace.workstation_construction import _digest
    return _digest(asdict(graph._node(graph._runtime(), candidate_id)))


class B11RealNativeLocalProofTests(unittest.TestCase):
    """An actual B3 subprocess produces the local result before B11 delivery.

    The test key is ephemeral; source ownership outside this fixture is NOT
    inferred from the signature.
    """

    def test_real_b3_local_result_is_independently_rechecked_before_delivery(self):
        from network.tests.test_workstation_native_feedback_integration import (
            RealNativeFeedbackTests,
        )
        from systems.workspace.branch_help import verify_return
        from systems.workspace.workstation_native_feedback import canonical_digest

        native = RealNativeFeedbackTests(
            "test_true_native_worker_executes_and_return_is_recorded_on_original_lane"
        )
        native.setUp()
        self.addCleanup(native.doCleanups)
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        graph = WorkstationConstruction(root / "construction")
        goal = graph.goal("Check native B3 return", provenance="user:goal")
        relation = "read and independently verify source-owned B3 return"
        candidate = graph.candidate(goal, relation, provenance="candidate:native")
        job = native.runtime().get(native.job_id)
        edition = job.metadata["edition_fingerprint"]
        graph.suggest_source(
            candidate, worker_id="finite-source-native", edition_ref=edition,
            source_locator="b3-source://" + native.job_id,
            reason="an actual B3 worker needs its own native verification",
        )
        # This is the actual existing native B3 subprocess, not a simulated
        # result callback. It finishes before any B11 event is emitted.
        result = native.feedback.advance(
            native.lane_id, confirm_execute=native.job_id, allow_local_execution=True,
        )
        self.assertEqual(native.runtime().state(native.job_id).status, "COMPLETE")
        signer = Ed25519PrivateKey.generate()
        calls = []

        def live(proof):
            native_state = native.runtime().state(native.job_id)
            checked = verify_return(
                data_dir=native.harness.data_dir, opening_id=result.opening_id,
            )
            return (
                proof.native_receipt_ref == "b3-return://" + result.opening_id
                and proof.native_receipt_sha256 == result.output_sha256
                and checked.get("state") == "RETURN_RECORDED_REVERIFY_BEFORE_USE"
                and checked.get("child", {}).get("job_id") == native.job_id
                and result.job_id == native.job_id
                and native_state.status == "COMPLETE"
                and canonical_digest(native_state.output) == result.output_sha256
                and native.runtime().get(native.job_id).metadata.get(
                    "edition_fingerprint"
                ) == edition
                and not result.checkpoint_pass
            )

        def execute(cap):
            calls.append("read-only-b3")
            return result

        def observe(cap, returned):
            valid = live(proof) and returned.job_id == native.job_id
            return Witness(
                "SUPPORTED" if valid else "UNKNOWN", cap.edition,
                (relation,) if valid else (),
                "b3-verified://" + native.job_id if valid else "", valid,
            )

        delivery = SourceOwnedLocalDelivery(
            construction=graph, journal_path=root / "observed.jsonl",
            adapters=(SourceAdapter(
                Capability("finite-source-native", edition, (relation,), True),
                execute, observe,
            ),),
            pinned_public_keys={
                ("finite-source-native", edition): raw_public_key(signer)
            },
            verify_native_current=live,
        )
        request = delivery.bridge.prepare(
            goal, candidate, route=(candidate, goal),
            worker_id="finite-source-native", edition_ref=edition,
            source_locator="b3-source://" + native.job_id,
        )
        proof = NativeLocalProof(
            handoff_id=request, source_name="finite-source-native",
            source_edition=edition, required_relation=relation,
            candidate_spec_sha256=delivery_spec(graph, candidate),
            source_locator="b3-source://" + native.job_id,
            native_receipt_ref="b3-return://" + result.opening_id,
            native_receipt_sha256=result.output_sha256,
        )
        self.assertEqual(calls, [])
        delivery.deliver(proof, signature_hex=signer.sign(canonical_proof_bytes(proof)).hex())
        self.assertEqual(calls, ["read-only-b3"])
        self.assertEqual(delivery.bridge.projection(request)["state"], "CROSSED")
        self.assertFalse(delivery.bridge.projection(request)["whole_route_verified"])


if __name__ == "__main__":
    unittest.main()
