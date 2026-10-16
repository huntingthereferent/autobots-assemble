"""B10 bounded integration: B9 route construction -> native event journal.

Native source return verification is a marked, independent fixture here. The
existing B3 native subprocess suite independently verifies the real B3 adapter;
this suite tests the NEW route-scoped joining boundary.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff, HandoffEvent
from runtime.journal import RuntimeJournal
from systems.workspace.main_referent_selector import Capability, Witness
from systems.workspace.observed_event_journal import (
    LOCAL_PASS, OBSERVED, OPEN, START, STOP, ObservedEventJournal, SourceAdapter,
)
from systems.workspace.b9_continuation_bridge import (
    B9ContinuationBridge, scoped_local_verifier,
)
from systems.workspace.workstation_construction import WorkstationConstruction


class B9EventBridgeTests(unittest.TestCase):
    def setUp(self):
        self.folder = TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.data = Path(self.folder.name)
        self.graph = WorkstationConstruction(self.data / "construction")
        self.goal = self.graph.goal("Deliver the requested output", provenance="user:goal")
        self.middle = self.graph.candidate(
            self.goal, "independently observe intermediate relation",
            provenance="proposed:middle",
        )
        self.leaf = self.graph.candidate(
            self.middle, "inspect required native input", provenance="proposed:leaf",
        )
        self.route = (self.leaf, self.middle, self.goal)
        self.graph.suggest_source(
            self.middle, worker_id="z-native", edition_ref="v1",
            source_locator="source://native-v1", reason="candidate source, not proof",
        )
        self.actions = []
        self.receipts = {"receipt://source-observed"}
        self.native_verified = True
        self.journal_path = self.data / "observed.jsonl"
        self.adapter = self.source("z-native", "v1")

    def source(self, name, edition, *, authorized=True, result="receipt://source-observed"):
        relation = "independently observe intermediate relation"
        def execute(cap):
            self.actions.append((cap.name, cap.edition))
            return result
        def observe(cap, native_return):
            checked = (
                self.native_verified
                and native_return in self.receipts
                and cap.name == "z-native"
                and cap.edition == "v1"
            )
            return Witness(
                "SUPPORTED" if checked else "UNKNOWN",
                cap.edition,
                (relation,) if checked else (),
                native_return if checked else "",
                checked,
            )
        return SourceAdapter(
            Capability(name, edition, (relation,), authorized), execute, observe
        )

    def trusted(self, handoff, event):
        return (
            event.actor_id == "independent-native-local-verifier"
            and event.data.get("local_receipt") == "fresh-verified-local"
        )

    def make(self, *adapters, verifier=None, path=None):
        sources = adapters or (self.adapter,)
        journal = ObservedEventJournal(
            path or self.journal_path,
            adapters=tuple(sources),
            verify_local_pass=scoped_local_verifier(self.graph, verifier or self.trusted),
        )
        return B9ContinuationBridge(self.graph, journal), journal

    def prepare(self, bridge, *, route=None, worker="z-native", edition="v1",
                locator="source://native-v1", candidate=None):
        return bridge.prepare(
            self.goal, candidate or self.middle,
            route=self.route if route is None else route,
            worker_id=worker, edition_ref=edition, source_locator=locator,
        )

    def emit(self, journal, handoff_id, *, actor="independent-native-local-verifier",
             receipt="fresh-verified-local"):
        return journal.append(HandoffEvent.create(
            handoff_id=handoff_id, event_type=LOCAL_PASS, actor_id=actor,
            data={"local_receipt": receipt},
        ))

    def test_prepare_keeps_proposal_inert_and_separate(self):
        original = (self.graph.data_dir / "runtime.jsonl").read_bytes()
        bridge, journal = self.make()
        request = self.prepare(bridge)
        self.assertEqual(self.actions, [])
        self.assertEqual(journal.projection(request)["state"], "OPEN")
        self.assertEqual(bridge.projection(request)["route"], self.route)
        self.assertFalse(bridge.projection(request)["whole_route_verified"])
        self.assertFalse(bridge.projection(request)["join_observed"])
        self.assertEqual(original, (self.graph.data_dir / "runtime.jsonl").read_bytes())
        self.assertEqual(HandoffRuntime(event_store=journal).get(request).required_relation,
                         "independently observe intermediate relation")

    def test_trusted_local_result_uses_independent_source_observation(self):
        bridge, journal = self.make()
        request = self.prepare(bridge)
        self.emit(journal, request)
        self.assertEqual(self.actions, [("z-native", "v1")])
        self.assertEqual(journal.projection(request)["state"], "CROSSED")
        self.assertFalse(bridge.projection(request)["whole_route_verified"])
        self.assertEqual(HandoffRuntime(event_store=journal).state(request).status, "READY")
        self.assertFalse(self.graph.next_construction_handoffs(self.goal)["whole_chain_verified"])

    def test_forged_or_unverified_local_pass_never_executes(self):
        bridge, journal = self.make()
        request = self.prepare(bridge)
        self.emit(journal, request, actor="impostor")
        self.emit(journal, request, receipt="copied-local-PASS")
        self.assertEqual(self.actions, [])
        self.assertEqual(journal.projection(request)["state"], "OPEN")

    def test_source_hint_does_not_authorize_unapproved_adapter(self):
        bridge, journal = self.make(self.source("z-native", "v1", authorized=False))
        with self.assertRaisesRegex(ValueError, "does not authorize"):
            self.prepare(bridge)
        self.assertEqual(journal.handoffs(), ())
        self.assertEqual(self.actions, [])

    def test_unhinted_edition_is_rejected_even_if_authorized(self):
        bridge, journal = self.make(self.source("z-native", "v2"))
        with self.assertRaisesRegex(ValueError, "not present"):
            self.prepare(bridge, edition="v2")

    def test_other_authorized_edition_with_same_relation_cannot_steal_attempt(self):
        # Alphabetical source would win without the edition filter.
        competing = self.source("a-unauthorized-for-route", "v2")
        bridge, journal = self.make(competing, self.adapter)
        request = self.prepare(bridge)
        self.emit(journal, request)
        self.assertEqual(self.actions, [("z-native", "v1")])

    def test_unverified_native_return_keeps_candidate_open(self):
        bridge, journal = self.make()
        request = self.prepare(bridge)
        self.native_verified = False
        self.emit(journal, request)
        self.assertEqual(journal.projection(request)["state"], "OPEN")
        self.assertFalse(bridge.projection(request)["whole_route_verified"])
        self.assertEqual(journal.projection(request)["source_evidence"], [])

    def test_nonexistent_route_and_unhinted_candidate_rejected(self):
        bridge, journal = self.make()
        with self.assertRaisesRegex(ValueError, "not present"):
            self.prepare(bridge, route=(self.middle, self.goal))
        with self.assertRaisesRegex(ValueError, "not present"):
            self.prepare(bridge, locator="source://changed")
        with self.assertRaisesRegex(ValueError, "not present"):
            bridge.prepare(self.goal, self.leaf, route=self.route,
                           worker_id="z-native", edition_ref="v1",
                           source_locator="source://native-v1")
        self.assertEqual(self.actions, [])

    def test_other_goal_is_not_a_substitute_for_the_requested_goal(self):
        bridge, journal = self.make()
        another = self.graph.goal("Different result", provenance="user:other")
        with self.assertRaises(ValueError):
            bridge.prepare(another, self.middle, route=self.route,
                           worker_id="z-native", edition_ref="v1",
                           source_locator="source://native-v1")

    def test_historical_supported_middle_is_not_a_fresh_local_pass(self):
        from systems.workspace.workstation_construction import ObservationalDetermination
        witness = ObservationalDetermination(
            self.graph, verify_native_receipt=lambda receipt: True
        )
        witness.record(witness.receipt_for(
            self.middle, verdict="SUPPORTED", witness_ref="fixture-history",
            native_source="fixture", relation_scope="middle",
            source_report_sha256="9" * 64,
        ))
        bridge, journal = self.make()
        request = self.prepare(bridge)
        self.assertEqual(self.actions, [])
        self.assertEqual(journal.projection(request)["state"], "OPEN")

    def test_new_upstream_changes_frontier_and_requires_a_new_scope_check(self):
        bridge, journal = self.make()
        request = self.prepare(bridge)
        self.graph.candidate(
            self.leaf, "new earlier missing input", provenance="new:upstream"
        )
        self.emit(journal, request)
        self.assertEqual(self.actions, [])
        self.assertEqual(journal.projection(request)["state"], "OPEN")

    def test_restart_preserves_result_and_never_executes_twice(self):
        bridge, journal = self.make()
        request = self.prepare(bridge)
        self.emit(journal, request)
        bridge2, reopened = self.make()
        self.assertEqual(self.prepare(bridge2), request)
        self.emit(reopened, request)
        self.assertEqual(self.actions, [("z-native", "v1")])
        self.assertEqual(reopened.projection(request)["state"], "CROSSED")

    def test_restart_recovers_saved_local_pass_without_started_attempt(self):
        bridge, journal = self.make()
        request = self.prepare(bridge)
        event = HandoffEvent.create(
            handoff_id=request, event_type=LOCAL_PASS,
            actor_id="independent-native-local-verifier",
            data={"local_receipt": "fresh-verified-local"},
        )
        RuntimeJournal.append(journal, event)
        self.assertEqual(self.actions, [])
        bridge2, reopened = self.make()
        self.assertEqual(self.actions, [("z-native", "v1")])
        self.assertEqual(reopened.projection(request)["state"], "CROSSED")
        bridge3, reopened2 = self.make()
        self.assertEqual(self.actions, [("z-native", "v1")])

    def test_restart_blocks_uncertain_native_side_effect(self):
        bridge, journal = self.make()
        request = self.prepare(bridge)
        event = HandoffEvent.create(
            handoff_id=request, event_type=LOCAL_PASS,
            actor_id="independent-native-local-verifier",
            data={"local_receipt": "fresh-verified-local"},
        )
        RuntimeJournal.append(journal, event)
        RuntimeJournal.append(journal, HandoffEvent.create(
            handoff_id=request, event_type=START, actor_id="observed-continuation",
            data={"name": "z-native", "edition": "v1", "trigger_id": event.event_id},
        ))
        _, reopened = self.make()
        self.assertEqual(self.actions, [])
        self.assertEqual(reopened.projection(request)["state"], "RECOVERY_REQUIRED")
        self.emit(reopened, request)
        self.assertEqual(self.actions, [])
        self.assertTrue(any(e.event_type == STOP for e in reopened.for_handoff(request)))

    def test_repeated_prepare_does_not_create_a_second_request(self):
        bridge, journal = self.make()
        first = self.prepare(bridge)
        second = self.prepare(bridge)
        self.assertEqual(first, second)
        self.assertEqual(len(journal.handoffs()), 1)

    def test_missing_scope_wrapper_refused_before_submission(self):
        plain = ObservedEventJournal(
            self.journal_path, adapters=(self.adapter,),
            verify_local_pass=lambda h, e: True,
        )
        with self.assertRaisesRegex(ValueError, "B9-scoped"):
            B9ContinuationBridge(self.graph, plain)
        self.assertEqual(self.actions, [])

    def test_construction_and_attempt_journals_cannot_share_path(self):
        path = self.graph.data_dir / "runtime.jsonl"
        observed = ObservedEventJournal(
            path, adapters=(self.adapter,),
            verify_local_pass=scoped_local_verifier(self.graph, self.trusted),
        )
        with self.assertRaisesRegex(ValueError, "separate"):
            B9ContinuationBridge(self.graph, observed)

    def test_source_binding_malformed_fails_closed(self):
        bridge, journal = self.make()
        request = self.prepare(bridge)
        # A separate malformed spec would need an independent trusted event to
        # reach the journal; the reactor must still refuse its bad binding.
        bad = Handoff(
            handoff_id="malformed-binding", referent="x",
            from_actor="test", to_actor="test",
            required_relation="independently observe intermediate relation",
            metadata={"continuation_source_binding": {"name": "z-native"}},
        )
        HandoffRuntime(event_store=journal).submit(bad)
        journal.append(HandoffEvent.create(
            handoff_id=bad.handoff_id, event_type=LOCAL_PASS, actor_id="impostor"
        ))
        self.assertEqual(self.actions, [])
        self.assertEqual(journal.projection(request)["state"], "OPEN")

    def test_callback_failure_is_not_authorization(self):
        def failing(handoff, event):
            raise RuntimeError("independent local verification unavailable")
        bridge, journal = self.make(verifier=failing)
        request = self.prepare(bridge)
        self.emit(journal, request)
        self.assertEqual(self.actions, [])
        self.assertEqual(journal.projection(request)["state"], "OPEN")


if __name__ == "__main__":
    unittest.main()
