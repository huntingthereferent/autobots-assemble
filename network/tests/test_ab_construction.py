"""Tests of the opt-in construction direction against the real A/B contracts."""
from __future__ import annotations

import unittest
from itertools import product, repeat

from runtime.ab_information import (
    ABOccurrence, information_closure, synthesize_continuation_relation,
)
from runtime.ab_loop import ABAgent, ABFrame, ABLoop, ABMove
from runtime.ab_construction import (
    WorldEdge, check_composition, frame_for_candidate,
    inverse_fibers, project_candidates,
)


def step(state, action):
    """Synthetic nested chamber: separate gates at rooms 0 and 1."""
    room, left, right = state
    if action == "advance":
        gate = left if room == 0 else right if room == 1 else 0
        return (min(2, room + 1) if gate else room, left, right)
    if action == "toggle":
        if room == 0:
            return (room, 1 - left, right)
        if room == 1:
            return (room, left, 1 - right)
        return state
    raise KeyError(action)


STATES = tuple((0, left, right) for left, right in product((0, 1), repeat=2))
LOCATORS = ("witness:closed-closed", "witness:closed-open",
            "witness:open-closed", "witness:open-open")


def group(horizon):
    items = []
    for idx, initial in enumerate(STATES):
        state = initial
        future = []
        for _ in range(horizon):
            state = step(state, "advance")
            future.append(state[0])
        items.append(ABOccurrence.create(
            referent="nested-maze",
            relations={
                "gate0": initial[1],
                "gate1": initial[2],
                "irrelevant_id": idx,
            },
            continuation=tuple(future),
        ))
    return tuple(items)


def fibers(horizon=1):
    observations = group(horizon)
    return inverse_fibers(
        observations, information_closure(observations),
        source_locators=LOCATORS,
        witness_contract="synthetic two-chamber forward action tests",
        horizon=horizon,
    )


class InverseConstructionTests(unittest.TestCase):
    def test_recover_all_witness_occurrences(self):
        result = fibers()
        self.assertEqual(tuple(len(f.source_indices) for f in result), (2, 2))
        self.assertEqual(
            sorted(i for fiber in result for i in fiber.source_indices),
            [0, 1, 2, 3],
        )
        self.assertEqual(result[0].source_locators, LOCATORS[:2])
        self.assertEqual(result[1].source_locators, LOCATORS[2:])

    def test_witness_contract_survives_inverse(self):
        self.assertEqual(
            {f.witness_contract for f in fibers(2)},
            {"synthetic two-chamber forward action tests"},
        )
        self.assertEqual({f.horizon for f in fibers(2)}, {2})

    def test_later_horizon_splits_fiber(self):
        one, two = fibers(1), fibers(2)
        self.assertEqual(len(one), 2)
        self.assertEqual(len(two), 3)
        self.assertEqual(tuple(len(f.source_indices) for f in two), (2, 1, 1))
        st = information_closure(group(2))
        syn = synthesize_continuation_relation(st)
        self.assertIsNotNone(syn)
        self.assertEqual(len(syn.proof_partition), 4)
        self.assertEqual(len(syn.continuation_partition), 3)

    def test_wrong_state_rejected(self):
        with self.assertRaises(ValueError):
            inverse_fibers(
                group(2), information_closure(group(1)),
                source_locators=LOCATORS, witness_contract="test", horizon=2,
            )

    def test_wrong_locator_count_rejected(self):
        with self.assertRaises(ValueError):
            inverse_fibers(
                group(1), information_closure(group(1)),
                source_locators=LOCATORS[:2], witness_contract="test", horizon=1,
            )

    def test_unlocatable_source_rejected(self):
        with self.assertRaises(ValueError):
            inverse_fibers(
                group(1), information_closure(group(1)),
                source_locators=("", *LOCATORS[1:]),
                witness_contract="test", horizon=1,
            )

    def test_zero_horizon_rejected(self):
        with self.assertRaises(ValueError):
            inverse_fibers(
                group(1), information_closure(group(1)),
                source_locators=LOCATORS,
                witness_contract="test", horizon=0,
            )

    def test_explicit_construction_mode(self):
        with self.assertRaises(ValueError):
            project_candidates(fibers(), lambda f: ({"room": f.category},),
                               intent="observe")
        self.assertEqual(
            project_candidates(fibers(), lambda f: ({"room": f.category},),
                               intent="construct")[0].status,
            "PROPOSED",
        )

    def test_round_robin_fairness(self):
        proposed = project_candidates(
            fibers(2), lambda f: ({"variant": j} for j in range(100)),
            intent="construct", max_candidates=5,
        )
        self.assertEqual(tuple(p.category for p in proposed), (0, 1, 2, 0, 1))
        self.assertTrue(all(p.status == "PROPOSED" for p in proposed))

    def test_candidate_identity_deterministic(self):
        def generator(fiber):
            return ({"object": "gateway", "from": fiber.category},)
        a = project_candidates(fibers(), generator, intent="construct")
        b = project_candidates(fibers(), generator, intent="construct")
        self.assertEqual(a, b)
        self.assertEqual(len({x.proposal_id for x in a}), 2)

    def test_candidates_never_acquire_live_evidence(self):
        proposal = project_candidates(
            fibers(), lambda f: ({"gate": "new", "status": "MOVE"},),
            intent="construct",
        )[0]
        self.assertEqual(proposal.status, "PROPOSED")
        self.assertNotIn("measurement", proposal.__dict__)
        frame = frame_for_candidate(proposal)
        self.assertEqual(frame.current["construction_status"], "PROPOSED")
        self.assertEqual(frame.provenance, proposal.source_locators)
        self.assertEqual(frame.current["prediction_horizon"], 1)

    def test_proposal_frame_enters_existing_ab_loop_as_unknown(self):
        proposal = project_candidates(
            fibers(), lambda f: ({"room": f.category},),
            intent="construct",
        )[0]
        def evaluator(frame):
            return ABMove(
                state="UNKNOWN", reached=frame.current,
                survived=frame.survives, changed=(),
                edge=frame.edge, note="await native verification",
            )
        result = ABLoop((ABAgent("existing-ab", evaluator),), max_steps=2).run(
            frame_for_candidate(proposal)
        )
        self.assertEqual(result.move_count, 0)
        self.assertEqual(result.final_frame.current["stopped_state"], "UNKNOWN")

    def test_unserializable_candidate_rejected(self):
        with self.assertRaises(TypeError):
            project_candidates(
                fibers(), lambda f: ({"not_json": object()},),
                intent="construct",
            )

    def test_missing_source_is_unknown_not_movement(self):
        edge = WorldEdge((0, 1, 1), "advance", (1, 1, 1))
        got = check_composition(
            (edge,), project=lambda s: s[0],
            parent_step=lambda x, a: x + 1,
            translate_action=lambda a: a,
        )[0]
        self.assertEqual(got.status, "UNKNOWN")

    def test_parent_projection_loses_gate(self):
        # Same parent room, different future because a child gate differs.
        e0 = WorldEdge((0, 0, 0), "advance", step((0, 0, 0), "advance"), "synthetic:a")
        e1 = WorldEdge((0, 1, 0), "advance", step((0, 1, 0), "advance"), "synthetic:b")
        check = check_composition(
            (e0, e1),
            project=lambda s: s[0],
            parent_step=lambda room, action: min(room + 1, 2),
            translate_action=lambda a: a,
        )
        self.assertEqual(tuple(r.status for r in check),
                         ("MODEL_SPLIT", "MODEL_COMMUTES"))
        self.assertEqual(check[0].projected_after, 0)
        self.assertEqual(check[0].parent_after, 1)

    def test_full_parent_state_preserves_both_actions(self):
        edges = tuple(
            WorldEdge(s, a, step(s, a), f"synthetic:{i}:{a}")
            for i, s in enumerate(STATES)
            for a in ("advance", "toggle")
        )
        check = check_composition(
            edges, project=lambda x: x, parent_step=step,
            translate_action=lambda a: a,
        )
        self.assertEqual(len(check), 8)
        self.assertTrue(all(r.status == "MODEL_COMMUTES" for r in check))

    def test_unknown_parent_rule_remains_unknown(self):
        e = WorldEdge((0, 1, 0), "advance", (1, 1, 0), "synthetic:s")
        got = check_composition(
            (e,), project=lambda s: s[0],
            parent_step=lambda s, a: (_ for _ in ()).throw(KeyError("missing")),
            translate_action=lambda a: a,
        )[0]
        self.assertEqual(got.status, "UNKNOWN")

    def test_candidate_budget_validation(self):
        with self.assertRaises(ValueError):
            project_candidates(fibers(), lambda f: ({"x": 1},),
                               intent="construct", max_candidates=0)

    def test_duplicate_only_generator_terminates(self):
        # This test guards against non-terminating degenerate generators.
        proposed = project_candidates(
            fibers(), lambda f: repeat({"same": f.category}),
            intent="construct", max_candidates=5,
        )
        self.assertEqual(len(proposed), 2)


if __name__ == "__main__":
    unittest.main()
