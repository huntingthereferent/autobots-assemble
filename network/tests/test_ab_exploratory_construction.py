"""Opt-in cross-category construction uses the SAME A/B agent.

A previously witnessed quotient does not authorize continuation claims for
crossed relations. Generated hypotheses remain category-UNASSIGNED and
require independent tests. This suite includes real in-process native APIs.
"""
from __future__ import annotations

import unittest
from dataclasses import replace
from tempfile import TemporaryDirectory
from itertools import product

from runtime.ab_information import ABOccurrence, information_closure
from runtime.ab_construction import frame_for_candidate, proposal_from_frame
from runtime.ab_relation_generator import (
    derive_relation_constructions, derive_exploratory_constructions,
)
from runtime.activation import ActivationRegistry, ActivationRoute, run_activation
from runtime.handoff import Handoff, HandoffState
from runtime.service import EcosystemService
from runtime.ab_world_experiment import SimulationWorld, run_simulation_probe


def witnessed():
    # Correlated route and assignee; relation varies inside each category.
    return tuple(ABOccurrence.create(
        referent="activation-cross-proof",
        relations={
            "route_actor": actor,
            "selector_assignee": assignee,
            "selector_relation": relation,
        },
        continuation=(int(actor == "tester"),),
    ) for actor, assignee in (("other", "other"), ("tester", "james"))
      for relation in ("study", "review"))


def candidates(*, max_candidates=32, max_scan=4096, intent="construct"):
    o = witnessed()
    return derive_exploratory_constructions(
        o, information_closure(o),
        source_locators=tuple(f"native-fixture:{i}" for i in range(len(o))),
        witness_contract="only actor+surface resolution witnessed",
        horizon=1,
        intent=intent,
        max_candidates=max_candidates,
        max_scan=max_scan,
    )


def native_accept(relations, *, target_assignee="other", target_relation="review"):
    """Existing native registry and selector; no custom rule evaluator."""
    route = ActivationRoute(
        activation_id="real-api-test",
        surfaces=("begin review",),
        actor_id=relations["route_actor"],
        referent="held-out",
        projection="task_queue",
        selectors={
            "assignee": relations["selector_assignee"],
            "required_relation": relations["selector_relation"],
        },
    )
    resolved = ActivationRegistry((route,)).resolve(
        "begin review", actor_id="tester"
    )
    if resolved is None:
        return False
    handoff = Handoff(
        handoff_id="fixture", referent="held-out",
        from_actor="fixture", to_actor=target_assignee,
        required_relation=target_relation,
        metadata={"title": "held-out"},
    )
    state = HandoffState(handoff_id="fixture", status="READY")
    return len(run_activation(
        resolved, surface="begin review",
        handoffs=((handoff, state),),
    ).items) == 1


class ExplorationTests(unittest.TestCase):
    def test_one_forward_ab_two_valid_construction_directions(self):
        o = witnessed()
        state = information_closure(o)
        self.assertEqual(len(state.continuation_partition), 2)
        preserved = derive_relation_constructions(
            o, state,
            source_locators=tuple(f"native-fixture:{i}" for i in range(4)),
            witness_contract="only actor+surface resolution witnessed",
            horizon=1, intent="construct",
        )
        self.assertEqual(preserved, ())
        explored = candidates()
        self.assertEqual(len(explored), 4)
        self.assertTrue(all(p.status == "PROPOSED" and p.category is None
                            for p in explored))

    def test_new_cross_category_proposal_can_pass_actual_second_api(self):
        originals = tuple(dict(o.relations) for o in witnessed())
        new = candidates()
        self.assertFalse(any(native_accept(x) for x in originals))
        winners = [p for p in new
                   if native_accept(p.structure["relation_values"])]
        self.assertEqual(len(winners), 1)
        self.assertEqual(winners[0].structure["relation_values"][
            "selector_assignee"], "other")
        self.assertIsNone(winners[0].category)
        self.assertTrue(winners[0].structure["requires_independent_observation"])

    def test_no_prior_equivalence_or_prediction_is_inherited(self):
        for p in candidates():
            d = p.structure
            self.assertEqual(d["prior_continuation_category"], "UNASSIGNED")
            self.assertEqual(d["kind"], "cross-category-recombination")
            self.assertEqual(d["source_categories_touched"], [0, 1])
            self.assertNotIn("predicted_continuation", d)
            self.assertEqual(p.witness_contract,
                             "only actor+surface resolution witnessed")

    def test_every_component_has_exact_original_witness_source(self):
        sources = {f"native-fixture:{i}" for i in range(4)}
        originals = {tuple(o.relations) for o in witnessed()}
        for p in candidates():
            self.assertNotIn(tuple(sorted(p.structure["relation_values"].items())),
                             originals)
            self.assertGreaterEqual(len(p.source_indices), 2)
            self.assertTrue(set(p.source_locators).issubset(sources))
            self.assertEqual(set(p.structure["component_source_locators"]),
                             set(dict(witnessed()[0].relations)))
            self.assertTrue(
                set(p.structure["component_source_locators"].values()).issubset(sources)
            )
            self.assertTrue(
                {dict(witnessed()[i].relations)[name]
                 for i in p.source_indices for name in ["route_actor"]}
            )

    def test_explore_mode_is_read_only_on_existing_service(self):
        o = witnessed()
        with TemporaryDirectory(prefix="ab_explore_service_") as tmp:
            svc = EcosystemService(data_dir=tmp)
            before = svc.runtime.snapshot()
            common = dict(
                occurrences=o, state=information_closure(o),
                source_locators=tuple(f"native-fixture:{i}" for i in range(4)),
                witness_contract="only actor+surface resolution witnessed",
                horizon=1, intent="construct",
            )
            self.assertEqual(svc.propose_ab_constructions(**common), ())
            frames = svc.propose_ab_constructions(**common, mode="explore")
            self.assertEqual(len(frames), 4)
            self.assertEqual(before, svc.runtime.snapshot())
            self.assertEqual(svc.agent_lineage.roots_for_actor("james"), ())
            self.assertTrue(all(
                p.current["category"] is None
                and p.current["construction_status"] == "PROPOSED"
                for p in frames
            ))

    def test_round_trip_identity_preserves_unassigned_category(self):
        for candidate in candidates():
            f = frame_for_candidate(candidate)
            recovered = proposal_from_frame(f)
            self.assertEqual(recovered, candidate)
            self.assertIsNone(f.current["category"])
            self.assertIn("UNASSIGNED", f.current["structure"]["prior_continuation_category"])

    def test_tampered_exploration_does_not_pass_frame_contract(self):
        from runtime.ab_loop import ABFrame
        original = frame_for_candidate(candidates()[0])
        current = dict(original.current)
        current["category"] = 0
        tampered = ABFrame(
            referent=original.referent, direction=original.direction,
            current=current, survives=original.survives,
            edge=original.edge, provenance=original.provenance,
        )
        with self.assertRaisesRegex(ValueError, "identity"):
            proposal_from_frame(tampered)
        current2 = dict(original.current)
        current2["structure"] = {
            **current2["structure"], "kind": "relation-recombination"
        }
        tampered2 = ABFrame(
            referent=original.referent, direction=original.direction,
            current=current2, survives=original.survives,
            edge=original.edge, provenance=original.provenance,
        )
        with self.assertRaisesRegex(ValueError, "unassigned category"):
            proposal_from_frame(tampered2)

    def test_one_source_category_cannot_claim_boundary_exploration(self):
        o = tuple(
            ABOccurrence.create(referent="single-class",
                relations={"x": i, "y": i}, continuation="same")
            for i in range(3)
        )
        self.assertEqual(derive_exploratory_constructions(
            o, information_closure(o),
            source_locators=("x:0", "x:1", "x:2"),
            witness_contract="one tested future", horizon=1,
            intent="construct",
        ), ())

    def test_missing_source_and_wrong_intent_are_rejected(self):
        o = witnessed()
        common = dict(
            occurrences=o, state=information_closure(o),
            source_locators=tuple(f"native-fixture:{i}" for i in range(4)),
            witness_contract="one witnessed step", horizon=1,
        )
        with self.assertRaises(ValueError):
            derive_exploratory_constructions(**common, intent="observe")
        with self.assertRaises(ValueError):
            derive_exploratory_constructions(**{**common,
                "source_locators": ("", "one", "two", "three")}, intent="construct")
        with self.assertRaises(ValueError):
            derive_exploratory_constructions(**common, intent="construct", max_scan=0)

    def test_explore_rejects_user_generator_or_invalid_mode(self):
        with TemporaryDirectory(prefix="ab_explore_invalid_") as tmp:
            svc = EcosystemService(data_dir=tmp)
            o = witnessed()
            common = dict(
                occurrences=o, state=information_closure(o),
                source_locators=tuple(f"native-fixture:{i}" for i in range(4)),
                witness_contract="one witnessed step", horizon=1,
                intent="construct",
            )
            with self.assertRaises(ValueError):
                svc.propose_ab_constructions(**common, mode="observe")
            with self.assertRaises(ValueError):
                svc.propose_ab_constructions(**common, mode="explore",
                    generator=lambda fiber: ({"x": "unverified"},))

    def test_bounded_deterministic_cross_category_generation(self):
        first = candidates()
        self.assertEqual(first, candidates())
        self.assertEqual(len({p.proposal_id for p in first}), len(first))
        self.assertEqual(len(candidates(max_candidates=1)), 1)
        self.assertLessEqual(len(candidates(max_scan=2)), 2)

    def test_simulator_retains_unassigned_and_does_not_admit_native_move(self):
        # A synthetic test returns observed traces but never invents the
        # missing native witness or assigns an old category to a proposal.
        world = SimulationWorld(
            source="simulation://cross-category-fixture",
            initial=lambda s: dict(s["relation_values"]),
            step=lambda state, action: state,
            observe=lambda state: int(
                state["route_actor"] == "tester"
                and state["selector_assignee"] == "other"
            ),
            relations=lambda s: dict(s["relation_values"]),
        )
        observed = run_simulation_probe(
            candidates(), world=world, action_path=("read",)
        )
        self.assertTrue(observed.complete)
        self.assertTrue(all(t.original_category is None for t in observed.trials))
        self.assertEqual(observed.evidence_kind, "simulation")
        self.assertEqual(len(observed.observed_locators), 4)
        self.assertTrue(all(t.trace_locator.startswith("simulation://")
                            for t in observed.trials))


if __name__ == "__main__":
    unittest.main()
