"""B9: native-journal-backed observational scope across *all* route steps.

Only controlled fixture observer callbacks are used; successful assertions never
claim current source-native proof or authorize execution.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from systems.workspace.workstation_construction import (
    ObservationalDetermination, WorkstationConstruction,
)


class RouteScopedConstructionTests(unittest.TestCase):
    def setUp(self):
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name)
        self.graph = WorkstationConstruction(self.data)
        self.goal = self.graph.goal("Ship verified playable output", provenance="user:result")
        self.observer = ObservationalDetermination(
            self.graph, verify_native_receipt=lambda receipt: receipt.native_source == "fixture")

    def candidate(self, downstream, label, *, role="REQUIRED", origin="fixture:construction"):
        return self.graph.candidate(downstream, label, provenance=origin, path_role=role)

    def observe(self, node, verdict, *, scope, ref):
        return self.observer.record(self.observer.receipt_for(
            node, verdict=verdict, witness_ref=ref, native_source="fixture",
            relation_scope=scope, source_report_sha256="9" * 64))

    def route(self):
        front = self.graph.next_construction_handoffs(self.goal)
        self.assertEqual(len(front["construction_handoffs"]), 1)
        return front["construction_handoffs"][0]

    def test_intermediate_contradiction_is_visible_not_flattened_into_leaf(self):
        mid = self.candidate(self.goal, "Translate canonical receipt")
        leaf = self.candidate(mid, "Find parser schema")
        self.observe(mid, "CONTRADICTED", scope="parser v1 did not translate", ref="fixture:mid-1")
        report = self.route()
        self.assertEqual(report["historical_observation"], "UNDETERMINED")
        scoped = report["routes_with_observational_context"][0]
        self.assertEqual(scoped["candidate_ids"], (leaf, mid, self.goal))
        self.assertEqual([s["contract_state"] for s in scoped["steps"]],
                         ["PROPOSED", "CONTRADICTED"])
        self.assertEqual(scoped["historical_route_state"], "HISTORICAL_CONTRADICTION_PRESENT")
        self.assertEqual(scoped["next_construction_movement"], "REVISE_OR_EXPLORE_ALTERNATIVE")
        self.assertEqual(scoped["steps"][1]["historical_determinations"][0]["relation_scope"],
                         "parser v1 did not translate")
        self.assertFalse(scoped["whole_route_verified"])
        self.assertFalse(scoped["join_observed"])
        self.assertFalse(scoped["execution_authorized"])

    def test_shared_upstream_two_routes_keep_independent_observational_contexts(self):
        left = self.candidate(self.goal, "Verifier direct", role="ALTERNATIVE", origin="fixture:left")
        right = self.candidate(self.goal, "Adapter", role="ALTERNATIVE", origin="fixture:right")
        shared = self.candidate(left, "Source receipt", origin="fixture:shared")
        self.graph.propose_connection(shared, right, reason="candidate alternate adapter link")
        self.observe(left, "CONTRADICTED", scope="left old edition", ref="fixture:left-1")
        self.observe(right, "SUPPORTED", scope="right native-local trial", ref="fixture:right-1")
        scoped = self.route()["routes_with_observational_context"]
        by_middle = {r["candidate_ids"][1]: r for r in scoped}
        self.assertEqual(set(by_middle), {left, right})
        self.assertEqual(by_middle[left]["historical_route_state"],
                         "HISTORICAL_CONTRADICTION_PRESENT")
        self.assertEqual(by_middle[right]["historical_route_state"], "HISTORICALLY_UNDETERMINED")
        self.assertEqual(by_middle[right]["next_construction_movement"], "OBSERVE_OR_DECOMPOSE_FURTHER")
        connector = by_middle[right]["steps"][0]
        self.assertEqual(connector["relation_origin"], "PROPOSED_CONNECTION")
        self.assertEqual(connector["proposal_reasons"], ("candidate alternate adapter link",))
        self.assertEqual(by_middle[left]["steps"][0]["relation_origin"], "DECLARED_CANDIDATE")
        self.assertEqual(by_middle[left]["steps"][1]["provenance"], ("fixture:left", "candidate-downstream:" + self.goal))
        self.assertTrue(all(not r["whole_route_verified"] for r in scoped))

    def test_prior_contradiction_survives_later_supported_middle_report(self):
        middle = self.candidate(self.goal, "Intermediate relation")
        self.candidate(middle, "Missing child input")
        old = self.observe(middle, "CONTRADICTED", scope="edition 1", ref="fixture:first")
        new = self.observe(middle, "SUPPORTED", scope="edition 2", ref="fixture:second")
        route = self.route()["routes_with_observational_context"][0]
        step = route["steps"][1]
        self.assertEqual([e["observation_id"] for e in step["historical_determinations"]], [old, new])
        self.assertEqual([e["verdict"] for e in step["historical_determinations"]],
                         ["CONTRADICTED", "SUPPORTED"])
        self.assertEqual(step["contract_state"], "SUPPORTED")
        self.assertEqual(route["historical_route_state"], "HISTORICAL_CONTRADICTION_PRESENT")
        self.assertTrue(all(not e["current_native_verification"] for e in step["historical_determinations"]))

    def test_intermediate_source_suggestion_retains_exact_locator_and_reason(self):
        middle = self.candidate(self.goal, "Transform unbound source")
        self.candidate(middle, "Inspect source code")
        pid = self.graph.suggest_source(middle, worker_id="some-worker", edition_ref="review@one",
                                        source_locator="repo:source-location", reason="possible, not proven")
        route = self.route()["routes_with_observational_context"][0]
        hint = route["steps"][1]["suggested_sources"][0]
        self.assertEqual(hint["worker_id"], "some-worker")
        self.assertEqual(hint["source_locator"], "repo:source-location")
        self.assertEqual(hint["reason"], "possible, not proven")
        self.assertEqual(hint["capability_fit"], "UNDETERMINED")
        self.assertFalse(hint["execution_authorized"])
        self.assertTrue(pid.startswith("whsource-"))

    def test_historical_support_never_upgrades_whole_route_to_verified(self):
        middle = self.candidate(self.goal, "Observationally supported middle")
        leaf = self.candidate(middle, "Observationally supported input")
        self.observe(middle, "SUPPORTED", scope="only node middle", ref="fixture:middle")
        self.observe(leaf, "SUPPORTED", scope="only node leaf", ref="fixture:leaf")
        scoped = self.route()["routes_with_observational_context"][0]
        self.assertEqual(scoped["historical_route_state"], "HISTORICAL_LOCAL_SUPPORT_ONLY")
        self.assertEqual(scoped["next_construction_movement"], "RECHECK_OR_CONSTRUCT_REMAINDER")
        self.assertFalse(scoped["whole_route_verified"])
        self.assertFalse(scoped["join_observed"])
        self.assertFalse(self.graph.next_construction_handoffs(self.goal)["execution_authorized"])

    def test_legacy_unknown_at_middle_keeps_original_spelling_and_scope(self):
        mid = self.candidate(self.goal, "Unknown source")
        self.candidate(mid, "Proposed earlier input")
        self.observe(mid, "UNRESOLVED", scope="legacy bounded trial", ref="fixture:legacy")
        step = self.route()["routes_with_observational_context"][0]["steps"][1]
        self.assertEqual(step["historical_verdict"], "UNRESOLVED")
        self.assertEqual(step["contract_state"], "UNKNOWN")
        self.assertEqual(step["historical_determinations"][0]["contract_verdict"], "UNKNOWN")
        self.assertEqual(step["historical_determinations"][0]["relation_scope"], "legacy bounded trial")

    def test_route_steps_budget_refuses_full_projection_without_mutating_history(self):
        mid = self.candidate(self.goal, "Second step")
        self.candidate(mid, "First step")
        before = (self.data / "runtime.jsonl").read_bytes()
        with self.assertRaisesRegex(ValueError, "route step bound"):
            self.graph.next_construction_handoffs(self.goal, max_total_route_steps=1)
        self.assertEqual(len(self.route()["routes_with_observational_context"][0]["steps"]), 2)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())

    def test_invalid_route_budget_types_fail_closed(self):
        for n in (0, True, -1, 65537, 1.5, "10"):
            with self.subTest(value=n), self.assertRaisesRegex(ValueError, "route step bound"):
                self.graph.next_construction_handoffs(self.goal, max_total_route_steps=n)

    def test_empty_root_is_still_a_construction_opening(self):
        single = self.route()
        self.assertEqual(single["possible_routes_to_result"], ((self.goal,),))
        scoped = single["routes_with_observational_context"][0]
        self.assertEqual(scoped["steps"], ())
        self.assertEqual(scoped["historical_route_state"], "REQUIRES_CONSTRUCTION")
        self.assertEqual(scoped["next_construction_movement"], "DECOMPOSE_REQUIRED_RESULT")
        self.assertFalse(scoped["whole_route_verified"])

    def test_scoped_projection_is_readonly_and_stable_across_restarts(self):
        mid = self.candidate(self.goal, "Requirement to inspect")
        self.candidate(mid, "Find a candidate")
        self.observe(mid, "UNKNOWN", scope="trial", ref="fixture:unknown")
        before = (self.data / "runtime.jsonl").read_bytes()
        expected = self.graph.next_construction_handoffs(self.goal)
        restarted = WorkstationConstruction(self.data).next_construction_handoffs(self.goal)
        self.assertEqual(expected, restarted)
        self.assertEqual(before, (self.data / "runtime.jsonl").read_bytes())


if __name__ == "__main__":
    unittest.main()
