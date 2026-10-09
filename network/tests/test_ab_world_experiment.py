"""End-to-end inverse A/B -> constructed chambers -> observed SIMULATION -> A/B."""
import unittest
from dataclasses import replace
from itertools import count
from tempfile import TemporaryDirectory

from runtime.ab_information import ABOccurrence, information_closure
from runtime.ab_construction import inverse_fibers, project_candidates
from runtime.ab_world_experiment import SimulationWorld, run_simulation_probe
from runtime.service import EcosystemService


def chamber_step(state, action):
    room, gate0, gate1 = state
    if action == "advance":
        gate = gate0 if room == 0 else gate1 if room == 1 else 0
        return (min(room + 1, 2) if gate else room, gate0, gate1)
    if action == "toggle":
        if room == 0:
            return (room, 1 - gate0, gate1)
        if room == 1:
            return (room, gate0, 1 - gate1)
        return state
    raise KeyError(action)


def simulation(**overrides):
    options = {
        "source": "synthetic://nested-chambers/test-engine",
        "initial": lambda s: (s["room"], s["gate0"], s["gate1"]),
        "step": chamber_step,
        "observe": lambda s: s[0],
        "relations": lambda s: {
            "gate0": s["gate0"],
            "gate1": s["gate1"],
            "irrelevant_variant": s["irrelevant_variant"],
        },
    }
    options.update(overrides)
    return SimulationWorld(**options)


def generated():
    # Base *witnessed* one-action quotient had only two sources. Create
    # four proposed systems with an extra gate1 distinction not tested
    # by the old single-action witness.
    original = (
        ABOccurrence.create(referent="nested-chamber-world",
                            relations={"gate0": 0}, continuation=(0,)),
        ABOccurrence.create(referent="nested-chamber-world",
                            relations={"gate0": 1}, continuation=(1,)),
    )
    fibers = inverse_fibers(
        original, information_closure(original),
        source_locators=("source:room0-blocked", "source:room0-open"),
        witness_contract="prior one-action chamber experiment",
        horizon=1,
    )
    return project_candidates(
        fibers,
        lambda f: (
            {"room": 0, "gate0": f.category, "gate1": g,
             "irrelevant_variant": 2 * f.category + g}
            for g in (0, 1)
        ),
        intent="construct",
        max_candidates=4,
    )


class SimulatedWorldExperiments(unittest.TestCase):
    def test_executed_one_step_agrees_with_source_category(self):
        proposal = generated()
        experiment = run_simulation_probe(
            proposal, world=simulation(),
            action_path=("advance",),
            predict=lambda p, a: (p.category,),
        )
        self.assertTrue(experiment.complete)
        self.assertEqual([x.status for x in experiment.trials],
                         ["SIMULATED_MATCH"] * 4)
        self.assertEqual([x.observed for x in experiment.trials],
                         [(0,), (0,), (1,), (1,)])
        self.assertEqual(
            [tuple(b) for b in experiment.information.continuation_partition],
            [(0, 1), (2, 3)],
        )
        self.assertEqual(len(experiment.information.proofs), 1)
        self.assertIn(("gate0",), experiment.information.proofs[0].sources)
        self.assertEqual(experiment.evidence_kind, "simulation")

    def test_second_step_discovers_genuinely_new_distinction(self):
        experiment = run_simulation_probe(
            generated(), world=simulation(),
            action_path=("advance", "advance"),
            predict=lambda p, path: (p.category, p.category),
        )
        self.assertTrue(experiment.complete)
        self.assertEqual([x.observed for x in experiment.trials],
                         [(0, 0), (0, 0), (1, 1), (1, 2)])
        self.assertEqual([x.status for x in experiment.trials],
                         ["SIMULATED_MATCH", "SIMULATED_MATCH",
                          "SIMULATED_MATCH", "SIMULATED_COUNTEREXAMPLE"])
        self.assertEqual(
            experiment.information.continuation_partition,
            ((0, 1), (2,), (3,)),
        )
        self.assertIsNotNone(experiment.synthesized)
        self.assertEqual(len(experiment.synthesized.proof_partition), 4)
        self.assertTrue(all(t.trace_locator.startswith("simulation://")
                            for t in experiment.trials))
        self.assertEqual(experiment.trials[3].source_locators,
                         ("source:room0-open",))

    def test_missing_action_is_unknown_and_no_partial_quotient(self):
        experiment = run_simulation_probe(
            generated(), world=simulation(),
            action_path=("no-such-action",),
        )
        self.assertFalse(experiment.complete)
        self.assertIsNone(experiment.information)
        self.assertIsNone(experiment.synthesized)
        self.assertTrue(all(t.status == "UNKNOWN" for t in experiment.trials))

    def test_one_failed_candidate_blocks_whole_ab_promotion(self):
        def selective_step(state, action):
            if state[1] == 1 and state[2] == 1:
                raise KeyError("unavailable child rule")
            return chamber_step(state, action)
        experiment = run_simulation_probe(
            generated(), world=simulation(step=selective_step),
            action_path=("advance",),
        )
        self.assertEqual([t.status for t in experiment.trials],
                         ["SIMULATED_UNPREDICTED"] * 3 + ["UNKNOWN"])
        self.assertFalse(experiment.complete)
        self.assertIsNone(experiment.information)

    def test_nondeterminism_cannot_become_witness(self):
        steps = count()
        def different_every_time(state, action):
            next(steps)
            return state
        def observer(state):
            return next(steps)
        experiment = run_simulation_probe(
            generated(), world=simulation(step=different_every_time, observe=observer),
            action_path=("advance",),
        )
        self.assertFalse(experiment.complete)
        self.assertTrue(all(t.status == "UNKNOWN" for t in experiment.trials))

    def test_simulation_never_promotes_native_agent(self):
        proposal = generated()
        with TemporaryDirectory(prefix="world-experiment_") as folder:
            svc = EcosystemService(data_dir=folder)
            old = svc.runtime.snapshot()
            exp = run_simulation_probe(proposal, world=simulation(),
                                       action_path=("advance", "advance"))
            self.assertEqual(old, svc.runtime.snapshot())
            self.assertEqual(svc.agent_lineage.roots_for_actor("james"), ())
            self.assertEqual(exp.evidence_kind, "simulation")

    def test_candidate_source_contract_required(self):
        bad = replace(generated()[0], witness_contract="")
        with self.assertRaises(ValueError):
            run_simulation_probe(
                (bad, *generated()[1:]), world=simulation(),
                action_path=("advance",),
            )

    def test_reject_undeclared_native_world(self):
        bad = replace(simulation(), kind="measurement")
        with self.assertRaises(ValueError):
            run_simulation_probe(generated(), world=bad,
                                 action_path=("advance",))

    def test_bounded_actions_and_count(self):
        with self.assertRaises(ValueError):
            run_simulation_probe(generated(), world=simulation(),
                                 action_path=("advance",) * 13)
        with self.assertRaises(ValueError):
            run_simulation_probe(generated(), world=simulation(),
                                 action_path=())
        with self.assertRaises(ValueError):
            run_simulation_probe(generated(), world=simulation(),
                                 action_path=("advance",), max_candidates=2)

    def test_identical_worlds_still_retain_separate_sources(self):
        same = tuple(replace(p, structure={**p.structure, "gate1": 0})
                     for p in generated())
        exp = run_simulation_probe(same, world=simulation(),
                                   action_path=("advance",))
        self.assertEqual(exp.information.continuation_partition,
                         ((0, 1), (2, 3)))
        self.assertEqual(len({t.proposal_id for t in exp.trials}), 4)
        self.assertEqual(len({t.trace_locator for t in exp.trials}), 4)


if __name__ == "__main__":
    unittest.main()
