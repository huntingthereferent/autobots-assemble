"""Same A/B-derived construction operator across unrelated referent families.

No domain-specific candidate generator is supplied in any test. The
domain's *actual behavior* still requires its own witness/evaluator.
"""
from __future__ import annotations

import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from runtime.ab_information import ABOccurrence, information_closure
from runtime.ab_construction import proposal_from_frame, inverse_fibers
from runtime.ab_relation_generator import derive_relation_constructions
from runtime.service import EcosystemService
from runtime.ab_world_experiment import SimulationWorld, run_simulation_probe


DOMAINS = (
    ("room-world", "exit", "gate", "barrier"),
    ("approval-workflow", "decision", "review", "delivery"),
    ("feed-layout", "section", "ticker", "overlay"),
)


def examples(label: str, anchor: str, left: str, right: str):
    observations = []
    locators = []
    for mode in (0, 1):
        for variant in (0, 1):
            observations.append(ABOccurrence.create(
                referent=label,
                relations={anchor: mode, left: variant, right: variant},
                continuation=(mode,),
            ))
            locators.append(f"witness:{label}:{mode}:{variant}")
    return tuple(observations), tuple(locators)


def derive(label, anchor, left, right, **kwargs):
    group, locators = examples(label, anchor, left, right)
    return derive_relation_constructions(
        group, information_closure(group),
        source_locators=locators,
        witness_contract="one-step witnessed category",
        horizon=1,
        intent="construct",
        **kwargs,
    )


def two_step_model(anchor: str, left: str, right: str, label: str):
    def step(state, action):
        if action not in ("read-class", "read-interaction"):
            raise KeyError(action)
        relations = state["relations"]
        current = (
            relations[anchor]
            if action == "read-class"
            else int(relations[left] != relations[right])
        )
        return {"relations": relations, "observed": current}
    return SimulationWorld(
        source=f"simulation://{label}/generic-observer",
        initial=lambda structure: {
            "relations": dict(structure["relation_values"]),
            "observed": None,
        },
        step=step,
        observe=lambda state: state["observed"],
        relations=lambda structure: dict(structure["relation_values"]),
    )


class GenericConstructionTests(unittest.TestCase):
    def test_same_generator_operates_on_three_unrelated_domains(self):
        for domain in DOMAINS:
            with self.subTest(referent=domain[0]):
                group, locators = examples(*domain)
                candidates = derive(*domain)
                self.assertEqual(len(candidates), 4)
                self.assertEqual({p.category for p in candidates}, {0, 1})
                originals = {tuple(item.relations) for item in group}
                for candidate in candidates:
                    self.assertEqual(candidate.status, "PROPOSED")
                    self.assertEqual(candidate.witness_contract,
                                     "one-step witnessed category")
                    self.assertEqual(candidate.horizon, 1)
                    structure = candidate.structure
                    self.assertEqual(structure["kind"], "relation-recombination")
                    self.assertEqual(structure["proof_source_names"], [domain[1]])
                    proposed = structure["relation_values"]
                    self.assertNotIn(tuple(sorted(proposed.items())), originals)
                    self.assertEqual(proposed[domain[1]], candidate.category)
                    self.assertNotEqual(proposed[domain[2]], proposed[domain[3]])
                    self.assertEqual(set(structure["component_source_locators"]), set(proposed))
                    self.assertTrue(
                        set(structure["component_source_locators"].values()).issubset(locators)
                    )
                    self.assertTrue(set(candidate.source_locators).issubset(locators))
                    self.assertEqual(len(candidate.source_locators), 2)

    def test_generic_candidates_expose_longer_horizon_splits_in_all_domains(self):
        for label, anchor, left, right in DOMAINS:
            with self.subTest(referent=label):
                candidates = derive(label, anchor, left, right)
                future = run_simulation_probe(
                    candidates,
                    world=two_step_model(anchor, left, right, label),
                    action_path=("read-class", "read-interaction"),
                    predict=lambda proposal, actions: (proposal.category, 0),
                )
                self.assertTrue(future.complete)
                self.assertEqual(len(future.trials), 4)
                self.assertTrue(all(
                    trial.status == "SIMULATED_COUNTEREXAMPLE"
                    for trial in future.trials
                ))
                # The original two categories were only proved for one
                # action. The second action found an interaction.
                self.assertEqual(len(future.information.continuation_partition), 2)
                self.assertTrue(all(trial.observed[1] == 1 for trial in future.trials))
                self.assertEqual(future.evidence_kind, "simulation")

    def test_corrected_information_refines_original_categories(self):
        for label, anchor, left, right in DOMAINS:
            with self.subTest(referent=label):
                original, locators = examples(label, anchor, left, right)
                candidates = derive(label, anchor, left, right)
                model = two_step_model(anchor, left, right, label)
                future = run_simulation_probe(
                    candidates, world=model,
                    action_path=("read-class", "read-interaction"),
                )
                combined = tuple(
                    ABOccurrence.create(
                        referent=label,
                        relations=dict(item.relations),
                        continuation=(dict(item.relations)[anchor], 0),
                    )
                    for item in original
                ) + future.observed_occurrences
                current = information_closure(combined)
                self.assertEqual(len(current.continuation_partition), 4)
                self.assertTrue(all(
                    set(block).issubset(set(range(4))) or
                    set(block).issubset(set(range(4, 8)))
                    for block in current.continuation_partition
                ))
                self.assertNotEqual(current.continuation_partition,
                                    information_closure(original).continuation_partition)
                next_fibers = inverse_fibers(
                    combined, current,
                    source_locators=(*locators, *future.observed_locators),
                    witness_contract="SIMULATION ONLY: 2-step tested",
                    horizon=2,
                )
                self.assertEqual(len(next_fibers), 4)

    def test_nested_dicts_lists_and_boolean_relations_use_same_generator(self):
        # Unlike the three binary referents, this one carries genuinely
        # heterogeneous JSON values and non-numeric category labels.
        group = []
        for route in ("automatic", "manual"):
            for variant in (False, True):
                group.append(ABOccurrence.create(
                    referent="document-review",
                    relations={
                        "route": route,
                        "recipients": ["owner", "legal"] if variant else ["owner"],
                        "policy": {"audit_required": variant, "level": None},
                    },
                    continuation=(route,),
                ))
        observations = tuple(group)
        result = derive_relation_constructions(
            observations, information_closure(observations),
            source_locators=tuple(f"review-source:{i}" for i in range(4)),
            witness_contract="only initial routing tested",
            horizon=1, intent="construct",
        )
        self.assertEqual(len(result), 4)
        for p in result:
            relations = p.structure["relation_values"]
            self.assertIn(relations["route"], ("automatic", "manual"))
            self.assertIsNone(relations["policy"]["level"])
            self.assertNotEqual(
                len(relations["recipients"]) == 2,
                relations["policy"]["audit_required"],
            )
            self.assertEqual(p.witness_contract, "only initial routing tested")
            self.assertEqual(p.status, "PROPOSED")

    def test_single_category_can_expose_multiple_relation_dimensions(self):
        observations = tuple(
            ABOccurrence.create(
                referent="three-options",
                relations={"shape": i, "color": f"c{i}"},
                continuation="same tested future",
            )
            for i in range(3)
        )
        result = derive_relation_constructions(
            observations, information_closure(observations),
            source_locators=("s:0", "s:1", "s:2"),
            witness_contract="one equal finite-horizon continuation",
            horizon=1, intent="alternatives", max_candidates=20,
        )
        self.assertEqual(len(result), 6)
        self.assertTrue(all(p.category == 0 for p in result))
        self.assertTrue(all(p.structure["proof_source_names"] == [] for p in result))

    def test_nonportable_relation_values_are_rejected_not_fabricated(self):
        value = object()
        group = (
            ABOccurrence.create(
                referent="opaque",
                relations={"x": value, "y": 0},
                continuation="same",
            ),
            ABOccurrence.create(
                referent="opaque",
                relations={"x": 1, "y": 1},
                continuation="same",
            ),
        )
        with self.assertRaises(TypeError):
            derive_relation_constructions(
                group, information_closure(group),
                source_locators=("opaque:0", "opaque:1"),
                witness_contract="opaque values are unportable",
                horizon=1, intent="construct",
            )

    def test_native_arc_histories_do_not_license_unseen_mechanics(self):
        # These are actual archived SK48 alternative action histories.
        # The finite native suffix tests support one continuation class
        # *within each phase*, not arbitrary new world mechanics.
        root = Path(__file__).resolve().parents[2]
        source = (
            root / "research" / "arc-agi3" / "desktop-evidence-2026-10-08"
            / "sk48_l2_directional_phase_cross_source_ab.json"
        )
        record = json.loads(source.read_text(encoding="utf-8"))
        self.assertEqual(record["tested_suffixes"], 64)
        self.assertEqual(record["same_phase_counterexamples"], [])
        histories = tuple(record["source_variants"]["1"])
        self.assertEqual(histories, ([2], [1, 7], [4, 7]))
        group = tuple(
            ABOccurrence.create(
                referent="native-sk48-L2-phase-1",
                relations={"native_action_history": history},
                continuation=("equivalent under 64 tested suffixes",),
            )
            for history in histories
        )
        candidates = derive_relation_constructions(
            group, information_closure(group),
            source_locators=tuple(
                f"repository:sk48_phase_1/source_{i}"
                for i in range(3)
            ),
            witness_contract="native SK48 phase-1; 64 finite suffixes",
            horizon=3, intent="construct",
        )
        self.assertEqual(candidates, ())
        # Two directions of A/B are present, but the native witnesses only
        # expose one variable action-history field: no sound recombination
        # across independent dimensions is available here.

    def test_no_novel_structure_when_only_one_relation_varies(self):
        group = (
            ABOccurrence.create(
                referent="single-axis", relations={"mode": 1, "option": "a"},
                continuation="same",
            ),
            ABOccurrence.create(
                referent="single-axis", relations={"mode": 1, "option": "b"},
                continuation="same",
            ),
        )
        self.assertEqual(
            derive_relation_constructions(
                group, information_closure(group),
                source_locators=("w:a", "w:b"),
                witness_contract="one-step witnessed",
                horizon=1, intent="construct",
            ),
            (),
        )

    def test_no_novel_structure_when_proof_block_singleton(self):
        group = tuple(
            ABOccurrence.create(
                referent="singleton", relations={"a": i, "b": i},
                continuation=i,
            )
            for i in range(3)
        )
        self.assertEqual(
            derive_relation_constructions(
                group, information_closure(group),
                source_locators=("w0", "w1", "w2"),
                witness_contract="one-step witnessed",
                horizon=1, intent="construct",
            ),
            (),
        )

    def test_incomplete_relation_vocabulary_is_not_filled_in(self):
        group = (
            ABOccurrence.create(referent="unknown",
                                relations={"mode": 0, "extra": 1},
                                continuation=(0,)),
            ABOccurrence.create(referent="unknown",
                                relations={"mode": 0},
                                continuation=(0,)),
        )
        with self.assertRaisesRegex(ValueError, "missing relation"):
            derive_relation_constructions(
                group, information_closure(group),
                source_locators=("w0", "w1"),
                witness_contract="one-step witnessed",
                horizon=1, intent="construct",
            )

    def test_bounded_result_and_bounded_combinations(self):
        domain = DOMAINS[0]
        self.assertEqual(len(derive(*domain, max_candidates=1)), 1)
        self.assertEqual(len(derive(*domain, max_scan_per_block=1)), 0)
        with self.assertRaises(ValueError):
            derive(*domain, max_scan_per_block=0)

    def test_intent_required_even_without_user_generator(self):
        domain = DOMAINS[0]
        group, locators = examples(*domain)
        with self.assertRaises(ValueError):
            derive_relation_constructions(
                group, information_closure(group),
                source_locators=locators,
                witness_contract="one-step witnessed category",
                horizon=1, intent="observe",
            )

    def test_service_uses_no_caller_written_generator(self):
        for domain in DOMAINS:
            with self.subTest(referent=domain[0]):
                group, locators = examples(*domain)
                with TemporaryDirectory(prefix="generic-ab_") as tmp:
                    service = EcosystemService(data_dir=tmp)
                    old = service.runtime.snapshot()
                    frames = service.propose_ab_constructions(
                        occurrences=group,
                        state=information_closure(group),
                        source_locators=locators,
                        witness_contract="one-step witnessed category",
                        horizon=1,
                        intent="construct",
                    )
                    self.assertEqual(len(frames), 4)
                    self.assertEqual(len({frame.current["proposal_id"]
                                          for frame in frames}), 4)
                    self.assertTrue(all(frame.current["construction_status"] == "PROPOSED"
                                        for frame in frames))
                    self.assertTrue(all(
                        proposal_from_frame(frame).structure["kind"]
                        == "relation-recombination" for frame in frames
                    ))
                    self.assertEqual(service.runtime.snapshot(), old)
                    self.assertEqual(service.agent_lineage.roots_for_actor("james"), ())

    def test_result_deterministic_and_relabel_invariant(self):
        domain = DOMAINS[0]
        first = derive(*domain)
        second = derive(*domain)
        self.assertEqual(first, second)
        self.assertEqual(len({p.proposal_id for p in first}), len(first))
        third = derive(*DOMAINS[1])
        # The referent and relation names differ, but category structure
        # and source preservation law should remain unchanged.
        self.assertEqual(
            sorted(p.category for p in first),
            sorted(p.category for p in third),
        )
        self.assertEqual(
            sorted(len(p.source_locators) for p in first),
            sorted(len(p.source_locators) for p in third),
        )


if __name__ == "__main__":
    unittest.main()
