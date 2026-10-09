"""Real in-repository interface checks of the domain-neutral A/B constructor.

No hand-coded construction generator and no invented execution semantics.
Uses two independent EXISTING production interfaces with temporary/local
inputs: ActivationRegistry.resolve/run_activation and the work-ledger parser.

These are in-process code observations, NOT live-world measurements or
native ARC witnesses. No real repo TASKS, personal data, work queues or
agent lineage are modified.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from runtime.ab_information import ABOccurrence, information_closure
from runtime.ab_relation_generator import derive_relation_constructions
from runtime.activation import ActivationRegistry, ActivationRoute, run_activation
from runtime.handoff import Handoff, HandoffState
from runtime.repository_tasks import read_active_work, admit_active_work
from runtime.engine import HandoffRuntime


def locator(domain: str, relations: dict) -> str:
    payload = json.dumps(relations, sort_keys=True, separators=(",", ":"))
    return f"local-test:{domain}:sha256:{sha256(payload.encode()).hexdigest()}"


def admission(relations: dict, root: Path):
    """Existing native code, fresh local input; no production ledger touched."""
    path = root / "research-ledger-fixture.md"
    path.write_text(
        "# Test-only work ledger\n"
        "## Active ALL WORK\n"
        "| Work | Lane | State | Next movement |\n"
        "|---|---|---|---|\n"
        "| [Review](research/ARC.md) | {lane} | {state} | {next_movement} |\n"
        "## Archived\n".format(**relations),
        encoding="utf-8",
    )
    rows = read_active_work(path)
    return bool(rows), path


def activation(relations: dict) -> tuple[bool, ActivationRoute | None]:
    """First probe observes only registered actor+surface recognition."""
    route = ActivationRoute(
        activation_id="sample",
        surfaces=("begin review",),
        actor_id=relations["route_actor"],
        referent="independent source",
        projection="task_queue",
        selectors={
            "assignee": relations["selector_assignee"],
            "required_relation": relations["selector_relation"],
        },
    )
    return (
        (match := ActivationRegistry((route,)).resolve(
            "begin review", actor_id="tester"
        )) is not None,
        match,
    )


def activation_holdout(route: ActivationRoute | None) -> int:
    if route is None:
        return 0
    handoff = Handoff(
        handoff_id="fixture-handoff",
        referent="independent review",
        from_actor="fixture",
        to_actor="james",
        required_relation="review",
        metadata={"title": "fixture handoff"},
    )
    state = HandoffState(handoff_id=handoff.handoff_id, status="READY")
    return len(run_activation(route, surface="begin review",
                              handoffs=((handoff, state),)).items)


def case_rows(domain: str):
    if domain == "work-ledger":
        return tuple(
            {
                "state": state,
                "lane": lane,
                "next_movement": next_move,
            }
            for state in ("FROZEN", "MOVE")
            for lane, next_move in (
                ("Research", "Compare witnesses"),
                ("Operations", "Check validation"),
            )
        )
    if domain == "activation":
        return tuple(
            {
                "route_actor": actor,
                "selector_assignee": assignee,
                "selector_relation": relation,
            }
            for actor in ("other", "tester")
            for assignee, relation in (
                ("james", "review"),
                ("other", "study"),
            )
        )
    raise ValueError(domain)


class ActualSubsystemABTests(unittest.TestCase):
    def originals_and_proposals(self, domain: str, *, root: Path | None = None):
        values = case_rows(domain)
        if domain == "work-ledger":
            assert root is not None
            original_futures = tuple(
                (int(admission(row, root)[0]),) for row in values
            )
        else:
            original_futures = tuple(
                (int(activation(row)[0]),) for row in values
            )
        original = tuple(
            ABOccurrence.create(
                referent=domain,
                relations=relations,
                continuation=future,
            )
            for relations, future in zip(values, original_futures)
        )
        sources = tuple(locator(domain, row) for row in values)
        state = information_closure(original)
        proposals = derive_relation_constructions(
            original, state,
            source_locators=sources,
            witness_contract="LOCAL API: initial one-call continuation",
            horizon=1,
            intent="construct",
        )
        return values, original, sources, state, proposals

    def test_real_work_ledger_parser_cross_combination(self):
        with TemporaryDirectory() as temp:
            values, originals, sources, state, proposals = (
                self.originals_and_proposals("work-ledger", root=Path(temp))
            )
            self.assertEqual(len(proposals), 4)
            self.assertEqual(len(state.continuation_partition), 2)
            witnessed = {json.dumps(v, sort_keys=True) for v in values}
            next_observations = []
            for proposal in proposals:
                row = proposal.structure["relation_values"]
                self.assertNotIn(json.dumps(row, sort_keys=True), witnessed)
                self.assertEqual(proposal.status, "PROPOSED")
                self.assertEqual(
                    set(proposal.structure["component_source_locators"].values())
                    .difference(sources), set()
                )
                matched, file_path = admission(row, Path(temp))
                self.assertEqual(int(matched), int(row["state"] == "MOVE"))
                self.assertEqual(int(matched), proposal.category)
                # Second independent native operation (handoff admission),
                # deliberately isolated from the service/task data.
                isolated = HandoffRuntime()
                ids = admit_active_work(isolated, file_path)
                self.assertEqual(len(ids), int(matched))
                self.assertEqual(len(isolated.snapshot()), int(matched))
                next_observations.append(ABOccurrence.create(
                    referent="work-ledger",
                    relations=row,
                    continuation=(int(matched), len(ids)),
                ))
            self.assertEqual(len(
                information_closure(next_observations).continuation_partition
            ), 2)

    def test_real_activation_registry_recombination(self):
        values, originals, sources, state, proposals = (
            self.originals_and_proposals("activation")
        )
        self.assertEqual(len(proposals), 4)
        self.assertEqual(len(state.continuation_partition), 2)
        old = {json.dumps(v, sort_keys=True) for v in values}
        observed = []
        for proposal in proposals:
            relations = proposal.structure["relation_values"]
            self.assertNotIn(json.dumps(relations, sort_keys=True), old)
            accepted, route = activation(relations)
            self.assertEqual(int(accepted), int(relations["route_actor"] == "tester"))
            self.assertEqual(int(accepted), proposal.category)
            selection = activation_holdout(route)
            self.assertEqual(selection, 0)  # crossed selectors do not match
            observed.append(ABOccurrence.create(
                referent="activation",
                relations=relations,
                continuation=(int(accepted), selection),
            ))
        self.assertEqual(len(
            information_closure(observed).continuation_partition
        ), 2)

    def test_native_holdout_splits_first_step_activation_category(self):
        # First resolve() ignored selectors, so both accepted routes were
        # equivalent. The actual run_activation() checks BOTH selectors,
        # and exposes an additional continuation class. This is directly
        # the kind of horizon-dependent split A/B must preserve.
        values, originals, sources, first, proposals = (
            self.originals_and_proposals("activation")
        )
        self.assertEqual(len(first.continuation_partition), 2)
        combined = []
        for relations in (*values, *(
                p.structure["relation_values"] for p in proposals)):
            matched, route = activation(relations)
            combined.append(ABOccurrence.create(
                referent="activation",
                relations=relations,
                continuation=(int(matched), activation_holdout(route)),
            ))
        new = information_closure(combined)
        self.assertEqual(len(new.continuation_partition), 3)
        self.assertTrue(any(
            item.continuation == (1, 1) for item in combined
        ))
        self.assertTrue(any(
            item.continuation == (1, 0) for item in combined
        ))
        self.assertTrue(any(
            "selector_relation" in source or "selector_assignee" in source
            for proof in new.proofs for source in proof.sources
        ))

    def test_relabeling_and_source_conservation(self):
        values_a, _old_a, sources_a, state_a, props_a = (
            self.originals_and_proposals("activation")
        )
        with TemporaryDirectory() as temp:
            values_b, _old_b, sources_b, state_b, props_b = (
                self.originals_and_proposals("work-ledger", root=Path(temp))
            )
        self.assertEqual([len(state_a.continuation_partition),
                          len(state_b.continuation_partition)], [2, 2])
        self.assertEqual(len(props_a), len(props_b))
        self.assertEqual(len(props_a), 4)
        self.assertEqual(sorted(p.category for p in props_a),
                         sorted(p.category for p in props_b))
        self.assertTrue(all(
            set(p.structure["component_source_locators"].values())
                .issubset(sources_a)
            for p in props_a
        ))
        self.assertTrue(all(
            set(p.structure["component_source_locators"].values())
                .issubset(sources_b)
            for p in props_b
        ))

    def test_no_proposals_cross_native_control_category(self):
        for domain in ("activation", "work-ledger"):
            with TemporaryDirectory() as temp:
                originals = self.originals_and_proposals(
                    domain, root=Path(temp)
                )[4]
                control = "route_actor" if domain == "activation" else "state"
                values = case_rows(domain)
                witnessed_controls = {
                    (d[control], d["selector_assignee"] if domain == "activation" else d["lane"])
                    for d in values
                }
                for proposal in originals:
                    attrs = proposal.structure["relation_values"]
                    self.assertEqual(
                        attrs[control],
                        ("other", "tester")[proposal.category] if domain == "activation"
                        else ("FROZEN", "MOVE")[proposal.category],
                    )
                    self.assertIn(
                        (attrs[control], attrs["selector_assignee"]
                            if domain == "activation" else attrs["lane"]),
                        witnessed_controls,
                    )


if __name__ == "__main__":
    unittest.main()
