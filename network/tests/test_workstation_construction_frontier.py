"""B9 construction frontier, preserving possibility without native admission.

Uses the canonical repository runtime, journal, B2 harness, and a marked
fixture observation callback. No external owner or worker proof is claimed.
"""
from dataclasses import asdict
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime.handoff import Handoff, HandoffEvent
from systems.workspace.workstation_construction import (
    ObservationalDetermination, WorkstationConstruction, LINK, _digest,
)
from systems.workspace.workstation_harness import WorkstationContinuationHarness


class ConstructionFrontierTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.data = Path(temp.name)
        self.g = WorkstationConstruction(self.data)
        self.goal = self.g.goal("Deliver a tested browser game", provenance="user:result")

    def handoffs(self):
        return self.g.next_construction_handoffs(self.goal)

    def node(self, requirement, downstream=None, role="REQUIRED", origin="proposal:user"):
        return self.g.candidate(downstream or self.goal, requirement,
                                path_role=role, provenance=origin)

    def test_root_itself_is_first_construction_handoff(self):
        h = self.handoffs()
        self.assertEqual(h["required_result"], "Deliver a tested browser game")
        self.assertEqual(h["construction_handoffs"][0]["candidate_id"], self.goal)
        self.assertEqual(h["construction_handoffs"][0]["possible_routes_to_result"], ((self.goal,),))
        self.assertFalse(h["execution_authorized"])
        self.assertFalse(h["whole_chain_verified"])

    def test_unknown_middle_carries_route_to_required_result(self):
        middle = self.node("Obtain native compatibility receipt")
        need = self.node("Determine required canonical input", downstream=middle)
        h = self.handoffs()["construction_handoffs"]
        self.assertEqual(len(h), 1)
        self.assertEqual(h[0]["possible_routes_to_result"], ((need, middle, self.goal),))
        self.assertEqual(h[0]["next_construction_movement"], "OBSERVE_OR_DECOMPOSE_FURTHER")

    def test_two_alternatives_are_preserved_as_separate_handoffs(self):
        a = self.node("Existing source", role="ALTERNATIVE", origin="option:a")
        b = self.node("Fresh adapter", role="ALTERNATIVE", origin="option:b")
        h = self.handoffs()["construction_handoffs"]
        self.assertEqual({x["candidate_id"] for x in h}, {a, b})
        self.assertTrue(all(x["path_role"] == "ALTERNATIVE" for x in h))
        self.assertTrue(all(x["native_admission"] is False for x in h))

    def test_links_preserve_multiple_possible_routes_without_join_claim(self):
        a = self.node("Build native adapter", role="ALTERNATIVE")
        b = self.node("Prove receipt contents", role="ALTERNATIVE")
        src = self.node("Recover source shape", downstream=a)
        self.g.propose_connection(src, b, reason="possible shared prerequisite")
        hs = self.handoffs()["construction_handoffs"]
        self.assertEqual(len(hs), 1)
        self.assertEqual(set(hs[0]["possible_routes_to_result"]),
                         {(src, a, self.goal), (src, b, self.goal)})
        self.assertFalse(self.handoffs()["whole_chain_verified"])

    def test_path_bound_fails_closed_rather_than_dropping_routes(self):
        a = self.node("Path A", role="ALTERNATIVE")
        b = self.node("Path B", role="ALTERNATIVE")
        c = self.node("Upstream", downstream=a)
        self.g.propose_connection(c, b, reason="might serve both")
        with self.assertRaisesRegex(ValueError, "bounded path"):
            self.g.next_construction_handoffs(self.goal, max_paths_per_leaf=1)
        self.assertEqual(len(self.handoffs()["construction_handoffs"][0]["possible_routes_to_result"]),2)

    def test_empty_or_boolean_path_limit_is_not_accepted(self):
        for number in (0, True, -2, 257, 1.5):
            with self.subTest(number=number), self.assertRaises(ValueError):
                self.g.next_construction_handoffs(self.goal, max_paths_per_leaf=number)

    def test_global_path_bound_refuses_many_independent_leaves(self):
        # Every leaf is locally within its per-leaf bound, but the whole
        # frontier exceeds a global cap. Returning a subset would erase paths.
        for i in range(4):
            self.node(f"Independent potential prerequisite {i}")
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "total path bound"):
            self.g.next_construction_handoffs(self.goal, max_total_paths=3)
        self.assertEqual(len(self.g.next_construction_handoffs(
            self.goal, max_total_paths=4)["construction_handoffs"]), 4)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_depth_bound_refuses_unknown_middle_without_partial_return(self):
        a = self.node("First missing step")
        b = self.node("Second missing step", downstream=a)
        self.node("Third missing step", downstream=b)
        with self.assertRaisesRegex(ValueError, "depth bound"):
            self.g.next_construction_handoffs(self.goal, max_path_depth=3)
        recovered = self.g.next_construction_handoffs(self.goal, max_path_depth=4)
        self.assertEqual(len(recovered["construction_handoffs"][0]["possible_routes_to_result"][0]), 4)

    def test_max_total_and_depth_budgets_validate_types(self):
        for value in (0, True, -1, 4097, 1.25, "100"):
            for name in ("max_total_paths", "max_path_depth"):
                with self.subTest(value=value, name=name), self.assertRaisesRegex(ValueError, "bound"):
                    self.g.next_construction_handoffs(self.goal, **{name: value})

    def test_bounded_global_frontier_preserves_all_shared_routes(self):
        a = self.node("Path A", role="ALTERNATIVE")
        b = self.node("Path B", role="ALTERNATIVE")
        src = self.node("Shared prerequisite", downstream=a)
        self.g.propose_connection(src, b, reason="possible secondary route")
        result = self.g.next_construction_handoffs(self.goal, max_total_paths=2)
        routes = result["construction_handoffs"][0]["possible_routes_to_result"]
        self.assertEqual(set(routes), {(src, a, self.goal), (src, b, self.goal)})
        self.assertFalse(result["whole_chain_verified"])
        self.assertFalse(result["execution_authorized"])

    def test_depth_budget_one_permits_root_only(self):
        self.assertEqual(self.g.next_construction_handoffs(
            self.goal, max_path_depth=1)["construction_handoffs"][0]["candidate_id"],
            self.goal)

    def test_contradicted_route_remains_constructible_but_not_supported(self):
        x = self.node("Maybe reuse old game output")
        observer = ObservationalDetermination(self.g, verify_native_receipt=lambda r: r.native_source == "fixture")
        receipt = observer.receipt_for(x, verdict="CONTRADICTED", witness_ref="fixture:1",
                                       native_source="fixture", relation_scope="one candidate",
                                       source_report_sha256="a"*64)
        observer.record(receipt)
        h = self.handoffs()["construction_handoffs"][0]
        self.assertEqual(h["historical_observation"], "CONTRADICTED")
        self.assertEqual(h["next_construction_movement"], "REVISE_OR_EXPLORE_ALTERNATIVE")
        self.assertFalse(h["current_source_verified"])
        alt = self.node("Investigate contradiction", downstream=x)
        self.assertEqual(self.handoffs()["construction_handoffs"][0]["possible_routes_to_result"],
                         ((alt, x, self.goal),))

    def test_historical_support_cannot_become_current_proof(self):
        x = self.node("Maybe reuse old game output")
        owner_alive = [True]
        obs = ObservationalDetermination(self.g, verify_native_receipt=lambda r: owner_alive[0])
        obs.record(obs.receipt_for(x, verdict="SUPPORTED", witness_ref="fixture:2",
                                   native_source="fixture", relation_scope="candidate",
                                   source_report_sha256="b"*64))
        owner_alive[0] = False
        h = self.handoffs()["construction_handoffs"][0]
        self.assertEqual(h["historical_observation"], "SUPPORTED")
        self.assertEqual(h["next_construction_movement"], "RECHECK_OR_CONSTRUCT_REMAINDER")
        self.assertFalse(h["current_source_verified"])
        self.assertFalse(obs.recheck(x)["determinations"][0]["verified_now"])

    def test_source_hint_is_not_authorized_and_provenance_is_retained(self):
        x = self.node("Maybe a native source can help", origin="operator:choice")
        self.g.suggest_source(x, worker_id="sample-worker", edition_ref="v7",
                              source_locator="repo:example", reason="candidate only")
        h = self.handoffs()["construction_handoffs"][0]
        self.assertEqual(h["provenance"][0], "operator:choice")
        self.assertEqual(h["suggested_sources"][0]["capability_fit"], "UNDETERMINED")
        self.assertFalse(h["suggested_sources"][0]["execution_authorized"])
        native = self.g._runtime().get(x)
        self.assertEqual(h["candidate_spec_sha256"], _digest(asdict(native)))

    def test_frontier_is_readonly_across_restart(self):
        self.node("Missing intermediate renderer")
        old = (self.data / "runtime.jsonl").read_bytes()
        before = self.handoffs()
        after = WorkstationConstruction(self.data).next_construction_handoffs(self.goal)
        self.assertEqual(before, after)
        self.assertEqual(old, (self.data / "runtime.jsonl").read_bytes())

    def test_other_domain_cannot_satisfy_construction_handoff(self):
        x = self.node("Missing worker")
        runtime = self.g._runtime()
        runtime.submit(Handoff("native-job", "other process", "a", "b", "independent",
                               metadata={"source_system": "process-workstation"}))
        runtime.event_store.append(HandoffEvent.create(
            handoff_id="native-job", event_type="RESULT", actor_id="native-worker",
            data={"status":"COMPLETE", "output": {"not_this_candidate": True}}))
        self.assertEqual(self.handoffs()["construction_handoffs"][0]["candidate_id"], x)
        self.assertFalse(self.handoffs()["execution_authorized"])

    def test_multiple_historical_determinations_retain_both_scopes(self):
        x = self.node("Candidate with evolving observational context")
        obs = ObservationalDetermination(self.g, verify_native_receipt=lambda r: True)
        old = obs.receipt_for(x, verdict="SUPPORTED", witness_ref="fixture:old",
                              native_source="fixture", relation_scope="initial local trial",
                              source_report_sha256="1"*64)
        new = obs.receipt_for(x, verdict="CONTRADICTED", witness_ref="fixture:new",
                              native_source="fixture", relation_scope="later changed conditions",
                              source_report_sha256="2"*64)
        obs.record(old)
        obs.record(new)
        report = self.handoffs()["construction_handoffs"][0]
        records = report["historical_determinations"]
        self.assertEqual(report["historical_receipt_count"], 2)
        self.assertEqual([r["verdict"] for r in records], ["SUPPORTED", "CONTRADICTED"])
        self.assertEqual([r["relation_scope"] for r in records],
                         ["initial local trial", "later changed conditions"])
        self.assertTrue(all(r["current_native_verification"] is False for r in records))
        self.assertEqual(report["next_construction_movement"], "REVISE_OR_EXPLORE_ALTERNATIVE")
        self.assertFalse(report["native_admission"])

    def test_prior_contradiction_survives_later_supported_report(self):
        x = self.node("Questionable old dependency")
        obs = ObservationalDetermination(self.g, verify_native_receipt=lambda r: True)
        for verdict, ref in (("CONTRADICTED", "fixture:first"),
                             ("SUPPORTED", "fixture:later")):
            obs.record(obs.receipt_for(x, verdict=verdict, witness_ref=ref,
                                       native_source="fixture", relation_scope="bounded trial",
                                       source_report_sha256="f"*64))
        result = self.handoffs()["construction_handoffs"][0]
        self.assertEqual(result["historical_observation"], "SUPPORTED")
        self.assertEqual(tuple(x["verdict"] for x in result["historical_determinations"]),
                         ("CONTRADICTED", "SUPPORTED"))
        self.assertFalse(result["current_source_verified"])

    def test_canonical_unknown_observation_matches_repository_contract(self):
        x = self.node("Native proof not yet determined")
        obs = ObservationalDetermination(self.g, verify_native_receipt=lambda r: True)
        obs.record(obs.receipt_for(x, verdict="UNKNOWN", witness_ref="fixture:unknown",
                                   native_source="fixture", relation_scope="bounded condition",
                                   source_report_sha256="9"*64))
        entry = self.handoffs()["construction_handoffs"][0]
        self.assertEqual(entry["historical_observation"], "UNKNOWN")
        self.assertEqual(entry["contract_state"], "UNKNOWN")
        self.assertEqual(entry["next_construction_movement"], "OBSERVE_OR_DECOMPOSE_FURTHER")
        self.assertFalse(entry["current_source_verified"])

    def test_legacy_unresolved_record_keeps_identity_and_projects_as_unknown(self):
        x = self.node("Legacy unresolved observation")
        obs = ObservationalDetermination(self.g, verify_native_receipt=lambda r: True)
        report = obs.receipt_for(x, verdict="UNRESOLVED", witness_ref="fixture:legacy",
                                 native_source="fixture", relation_scope="old boundary",
                                 source_report_sha256="e"*64)
        oid = obs.record(report)
        entry = self.handoffs()["construction_handoffs"][0]
        self.assertEqual(entry["historical_observation"], "UNRESOLVED")
        self.assertEqual(entry["contract_state"], "UNKNOWN")
        self.assertEqual(entry["historical_determinations"][0]["verdict"], "UNRESOLVED")
        self.assertEqual(entry["historical_determinations"][0]["contract_verdict"], "UNKNOWN")
        self.assertEqual(entry["historical_determinations"][0]["observation_id"], oid)
        self.assertEqual(obs.record(report), oid)
        self.assertFalse(entry["current_source_verified"])

    def test_no_observation_is_proposed_in_canonical_contract(self):
        node = self.node("Constructive source candidate")
        h = self.handoffs()["construction_handoffs"][0]
        self.assertEqual(h["candidate_id"], node)
        self.assertEqual(h["historical_observation"], "UNDETERMINED")
        self.assertEqual(h["contract_state"], "PROPOSED")
        self.assertFalse(h["native_admission"])

    def test_b2_remains_isolated_from_every_construction_handoff(self):
        self.node("Construct possible helper", role="ALTERNATIVE")
        harness = WorkstationContinuationHarness(
            self.data, verify_observation=lambda o: True,
            verify_connection=lambda a, b: True,
            worker_editions={"sample-worker":"v1"})
        self.assertEqual(harness.tick()["born_coordination_lanes"], [])
        self.assertEqual(harness.inspect()["proposals"], [])

    def test_invalid_persisted_cross_domain_link_fails_closed(self):
        x = self.node("One candidate")
        self.g._runtime().event_store.append(HandoffEvent.create(
            handoff_id=x, event_type=LINK, actor_id="malformed-fixture",
            data={"upstream_id":"unknown", "link_id":"spurious"}))
        with self.assertRaisesRegex(ValueError, "unavailable source"):
            self.handoffs()

    def test_frontier_requires_goal_not_child(self):
        x = self.node("One candidate")
        with self.assertRaisesRegex(ValueError, "root goal"):
            self.g.next_construction_handoffs(x)


if __name__ == "__main__":
    unittest.main()
