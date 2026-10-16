"""B9: forward-compatible candidate construction, not source-native execution.

B9 records candidate graph edges before native evidence exists. Any accepted
observation in these tests uses an explicitly marked fixture verifier, NEVER
purports to authenticate a physical source, owner, or real correspondence.
"""
from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.engine import HandoffRuntime
from runtime.handoff import Handoff, HandoffEvent
from runtime.journal import RuntimeJournal
from systems.workspace.workstation_construction import (
    LINK, OBSERVED, SOURCE, SOURCE_SUGGESTED, Receipt, ObservationalDetermination,
    WorkstationConstruction, _digest,
)
from systems.workspace.workstation_harness import WorkstationContinuationHarness


class ConstructionTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.data = Path(temp.name)
        self.graph = WorkstationConstruction(self.data)
        self.goal = self.graph.goal("Playable game reaches shipped", provenance="request:demo-001")
        self.trust = True
        self.allowed_refs = {"fixture:process:1", "fixture:process:2", "fixture:later:3"}
        self.observer = ObservationalDetermination(
            self.graph, verify_native_receipt=lambda r: self.trust and
            r.native_source == "fixture:local-evaluator" and
            r.witness_ref in self.allowed_refs and
            r.relation_scope == "specific proposed prerequisite")

    def child(self, *, downstream=None, requirement="Obtain runnable game build",
              role="REQUIRED", capability="", provenance="proposal:operator"):
        return self.graph.candidate(
            downstream or self.goal, requirement, provenance=provenance,
            path_role=role, capability_hint=capability)

    def report(self, candidate_id, verdict="UNRESOLVED", witness="fixture:process:1"):
        return self.observer.receipt_for(
            candidate_id, verdict=verdict, witness_ref=witness,
            native_source="fixture:local-evaluator",
            relation_scope="specific proposed prerequisite",
            source_report_sha256="a" * 64)

    def events(self):
        return self.graph._runtime().event_store.all()

    def test_goal_keeps_required_result_and_origin(self):
        view = self.graph.inspect(self.goal)
        self.assertEqual(len(view["nodes"]), 1)
        self.assertEqual(view["nodes"][0]["historical_verdict"], "UNDETERMINED")
        self.assertFalse(view["claims_native_completion"])
        self.assertFalse(view["execution_started"])
        self.assertEqual(self.graph._runtime().get(self.goal).provenance, ("request:demo-001",))

    def test_goal_replay_is_idempotent(self):
        before = (self.data / "runtime.jsonl").read_bytes()
        self.assertEqual(self.graph.goal("Playable game reaches shipped", provenance="request:demo-001"), self.goal)
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)

    def test_same_goal_other_origin_keeps_independent_identity(self):
        other = self.graph.goal("Playable game reaches shipped", provenance="request:other")
        self.assertNotEqual(other, self.goal)
        self.assertEqual(self.graph.inspect(self.goal)["nodes"][0]["id"], self.goal)

    def test_goal_requirement_cannot_be_blank(self):
        with self.assertRaises(ValueError):
            self.graph.goal("  ", provenance="x")

    def test_candidate_can_open_missing_capability_without_native_witness(self):
        child = self.child(capability="unknown-renderer-worker")
        view = self.graph.inspect(self.goal)
        self.assertIn((child, self.goal), view["candidate_links"])
        self.assertEqual(view["next_possible_upstream_nodes"], [child])
        self.assertEqual(next(n for n in view["nodes"] if n["id"] == child)["historical_verdict"], "UNDETERMINED")
        self.assertFalse(any(e.event_type in ("STARTED", "RESULT", "WORKSTATION_NATIVE_HELP_ASSIGNED")
                             for e in self.events()))

    def test_candidate_is_idempotent_without_new_submission(self):
        first = self.child()
        before = (self.data / "runtime.jsonl").read_bytes()
        self.assertEqual(self.child(), first)
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)

    def test_two_alternatives_remain_separate_paths(self):
        a = self.child(requirement="Use recovered engine", role="ALTERNATIVE", provenance="branch:a")
        b = self.child(requirement="Implement minimal engine", role="ALTERNATIVE", provenance="branch:b")
        self.assertNotEqual(a, b)
        self.assertEqual(len(self.graph.inspect(self.goal)["candidate_links"]), 2)
        self.assertEqual(set(self.graph.inspect(self.goal)["next_possible_upstream_nodes"]), {a, b})

    def test_continues_backward_through_unresolved_middle(self):
        middle = self.child(requirement="Game renderer is runnable", capability="unknown-worker")
        upstream = self.child(downstream=middle, requirement="Determine build inputs", capability="")
        view = self.graph.inspect(self.goal)
        self.assertEqual(set(view["candidate_links"]), {(middle, self.goal), (upstream, middle)})
        self.assertEqual(view["next_possible_upstream_nodes"], [upstream])

    def test_refuted_candidate_remains_explorable_without_false_support(self):
        mid = self.child(requirement="Potential rendering route")
        self.observer.record(self.report(mid, verdict="CONTRADICTED"))
        later = self.child(downstream=mid, requirement="Investigate why route failed")
        self.assertIn((later, mid), self.graph.inspect(self.goal)["candidate_links"])
        self.assertEqual(next(n for n in self.graph.inspect(self.goal)["nodes"] if n["id"] == mid)["historical_verdict"], "CONTRADICTED")

    def test_required_and_alternative_are_distinct_contracts(self):
        a = self.child(requirement="Use engine", role="ALTERNATIVE")
        b = self.child(requirement="Use engine", role="REQUIRED")
        self.assertNotEqual(a, b)

    def test_missing_provenance_refused(self):
        with self.assertRaises(ValueError):
            self.child(provenance="")

    def test_unknown_role_refused(self):
        with self.assertRaises(ValueError):
            self.child(role="PROVED")

    def test_node_from_other_system_refused(self):
        self.graph._runtime().submit(Handoff("external-job", "external", "x", "y", "z",
                                              metadata={"source_system": "process-workstation"}))
        with self.assertRaisesRegex(ValueError, "not a B9 candidate"):
            self.child(downstream="external-job")

    def test_link_adds_only_proposal_and_no_native_join(self):
        a = self.child(requirement="Build manifest", role="ALTERNATIVE")
        b = self.child(requirement="Bundle assets", role="ALTERNATIVE")
        lid = self.graph.propose_connection(a, b, reason="Maybe asset bundle consumes manifest")
        self.assertTrue(lid.startswith("whlink-"))
        self.assertIn((a, b), self.graph.inspect(self.goal)["candidate_links"])
        self.assertFalse(any(e.event_type in ("WORKSTATION_HELP_OPEN", "WORKSTATION_NATIVE_HELP_ASSIGNED")
                             for e in self.events()))
        self.assertTrue(any(e.event_type == LINK and e.data["relation_state"] == "PROPOSED_NOT_OBSERVED"
                            for e in self.events()))

    def test_link_repeat_does_not_append_events(self):
        a, b = self.child(requirement="A"), self.child(requirement="B")
        first = self.graph.propose_connection(a, b, reason="possible relationship")
        previous = (self.data / "runtime.jsonl").read_bytes()
        self.assertEqual(self.graph.propose_connection(a, b, reason="possible relationship"), first)
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), previous)

    def test_known_source_suggestion_is_not_native_admission(self):
        node = self.child(capability="finite-required-edge-prefilter")
        source_id = self.graph.suggest_source(
            node, worker_id="finite-correspondence-process", edition_ref="source-edition:base",
            source_locator="repo:existing-worker-source", reason="possible native helper")
        self.assertTrue(source_id.startswith("whsource-"))
        item = next(x for x in self.graph.inspect(self.goal)["nodes"] if x["id"] == node)
        self.assertEqual(item["source_options"][0]["capability_fit"], "UNDETERMINED")
        self.assertEqual(item["source_options"][0]["source_presence"], "NOT_VERIFIED_HERE")
        self.assertFalse(item["source_options"][0]["execution_authorized"])
        self.assertFalse(any(e.event_type == "WORKSTATION_NATIVE_HELP_ASSIGNED" for e in self.events()))

    def test_source_suggestion_is_restart_safe(self):
        node = self.child()
        args = dict(worker_id="worker-a", edition_ref="version-1",
                    source_locator="provenance:tool", reason="might fit")
        first = self.graph.suggest_source(node, **args)
        before = (self.data / "runtime.jsonl").read_bytes()
        again = WorkstationConstruction(self.data).suggest_source(node, **args)
        self.assertEqual(first, again)
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)

    def test_source_suggestion_does_not_implicitly_create_b2_observation(self):
        node = self.child()
        self.graph.suggest_source(node, worker_id="worker-a", edition_ref="version-1",
                                  source_locator="existing:source", reason="explore")
        harness = WorkstationContinuationHarness(self.data,
            verify_observation=lambda o: True, verify_connection=lambda x, y: True,
            worker_editions={"worker-a": "version-1"})
        self.assertEqual(harness.inspect()["proposals"], [])
        self.assertEqual(harness.tick()["born_coordination_lanes"], [])

    def test_source_suggestion_rejects_missing_locator(self):
        node = self.child()
        with self.assertRaises(ValueError):
            self.graph.suggest_source(node, worker_id="worker", edition_ref="v1",
                                      source_locator="", reason="might fit")

    def test_link_self_refused(self):
        with self.assertRaises(ValueError):
            self.graph.propose_connection(self.goal, self.goal, reason="self")

    def test_link_cycle_refused(self):
        a = self.child()
        b = self.child(downstream=a, requirement="Upstream prerequisite")
        with self.assertRaisesRegex(ValueError, "cycle"):
            self.graph.propose_connection(a, b, reason="back edge")

    def test_link_cross_goal_refused(self):
        a = self.child()
        second = self.graph.goal("Different destination", provenance="other")
        with self.assertRaisesRegex(ValueError, "one goal"):
            self.graph.propose_connection(a, second, reason="cross source guess")

    def test_link_rejects_unsupported_source(self):
        with self.assertRaises(ValueError):
            self.graph.propose_connection(self.goal, "unknown-id", reason="unknown")

    def test_observation_requires_actual_verifier(self):
        with self.assertRaises(ValueError):
            ObservationalDetermination(self.graph, verify_native_receipt=None)

    def test_receipt_cannot_be_admitted_as_label_only(self):
        node = self.child()
        before = (self.data / "runtime.jsonl").read_bytes()
        self.trust = False
        with self.assertRaisesRegex(ValueError, "independent native"):
            self.observer.record(self.report(node, verdict="SUPPORTED"))
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)

    def test_scoped_supported_claim_keeps_proposal_not_execution(self):
        node = self.child()
        receipt = self.report(node, verdict="SUPPORTED")
        oid = self.observer.record(receipt)
        self.assertTrue(oid.startswith("whdetermination-"))
        view = self.graph.inspect(self.goal)
        state = next(n for n in view["nodes"] if n["id"] == node)
        self.assertEqual(state["historical_verdict"], "SUPPORTED")
        self.assertFalse(state["current_native_verification"])
        self.assertFalse(state["native_execution_admitted"])
        self.assertFalse(view["claims_native_completion"])
        self.assertTrue(self.observer.recheck(node)["determinations"][0]["verified_now"])

    def test_recheck_after_revocation_marks_historical_not_current(self):
        node = self.child()
        self.observer.record(self.report(node, verdict="SUPPORTED"))
        self.trust = False
        self.assertFalse(self.observer.recheck(node)["determinations"][0]["verified_now"])
        self.assertEqual(next(n for n in self.graph.inspect(self.goal)["nodes"] if n["id"] == node)["historical_verdict"], "SUPPORTED")

    def test_replay_of_receipt_idempotent_but_rechecks_native(self):
        node = self.child()
        rec = self.report(node)
        self.observer.record(rec)
        before = (self.data / "runtime.jsonl").read_bytes()
        self.assertEqual(self.observer.record(rec), self.observer.record(rec))
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)
        self.trust = False
        with self.assertRaises(ValueError):
            self.observer.record(rec)

    def test_contradiction_keeps_prior_support_not_rewrite(self):
        node = self.child()
        self.observer.record(self.report(node, verdict="SUPPORTED", witness="fixture:process:1"))
        self.observer.record(self.report(node, verdict="CONTRADICTED", witness="fixture:process:2"))
        report = self.observer.recheck(node)
        self.assertEqual([d["verdict"] for d in report["determinations"]], ["SUPPORTED", "CONTRADICTED"])
        self.assertEqual(len([e for e in self.events() if e.event_type == OBSERVED]), 2)

    def test_unresolved_receipt_can_be_stored_without_inventing_support(self):
        node = self.child()
        self.observer.record(self.report(node))
        self.assertEqual(next(n for n in self.graph.inspect(self.goal)["nodes"] if n["id"] == node)["historical_verdict"], "UNRESOLVED")

    def test_unsupported_verdict_is_rejected_before_callback(self):
        node = self.child()
        with self.assertRaises(ValueError):
            self.observer.record(self.report(node, verdict="VERIFIED_COMPLETE"))

    def test_wrong_report_digest_is_rejected(self):
        node = self.child()
        receipt = replace(self.report(node), source_report_sha256="wrong")
        with self.assertRaises(ValueError):
            self.observer.record(receipt)

    def test_candidate_spec_mismatch_is_rejected(self):
        node = self.child()
        receipt = replace(self.report(node), candidate_spec_sha256="0" * 64)
        with self.assertRaises(ValueError):
            self.observer.record(receipt)

    def test_real_b2_harness_sees_none_of_b9_proposals(self):
        self.child(requirement="Can use existing worker?", capability="finite-required-edge-prefilter")
        harness = WorkstationContinuationHarness(
            self.data, verify_observation=lambda obs: False,
            verify_connection=lambda a,b: False,
            worker_editions={"finite-required-edge-prefilter": "existing-edition"})
        view = harness.inspect()
        self.assertEqual(view["lanes"], [])
        self.assertEqual(view["proposals"], [])
        self.assertEqual(harness.tick()["born_coordination_lanes"], [])

    def test_b2_seed_and_b9_candidate_recover_from_same_journal(self):
        harness = WorkstationContinuationHarness(self.data, verify_observation=lambda o: False,
                                                  verify_connection=lambda a,b: False)
        seeded = harness.seed_lane("A", "independent A/B observed referent")
        node = self.child()
        self.assertEqual(self.graph.inspect(self.goal)["next_possible_upstream_nodes"], [node])
        self.assertEqual([x["id"] for x in harness.inspect()["lanes"]], ["A"])
        self.assertEqual(self.graph._runtime().get(seeded).metadata["source_system"], "workstation-continuation-lane/v1")

    def test_unrelated_native_job_result_does_not_approve_candidates(self):
        node = self.child()
        runtime = self.graph._runtime()
        runtime.submit(Handoff("native-job", "unrelated", "a", "b", "c",
                               metadata={"source_system": "process-workstation"}))
        runtime.event_store.append(HandoffEvent.create(handoff_id="native-job", event_type="RESULT",
                                                       actor_id="worker", data={"status": "COMPLETE"}))
        view = self.graph.inspect(self.goal)
        self.assertEqual(next(x for x in view["nodes"] if x["id"] == node)["historical_verdict"], "UNDETERMINED")

    def test_dangling_persisted_link_detected(self):
        node = self.child()
        runtime = self.graph._runtime()
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=node, event_type=LINK, actor_id="test-malicious",
            data={"upstream_id": "nonexistent-link", "link_id": "bad-link"}))
        with self.assertRaisesRegex(ValueError, "unavailable source"):
            self.graph.inspect(self.goal)

    def test_readonly_inspect_does_not_write(self):
        self.child()
        before = (self.data / "runtime.jsonl").read_bytes()
        self.graph.inspect(self.goal)
        self.observer.recheck(self.goal)
        self.assertEqual((self.data / "runtime.jsonl").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
