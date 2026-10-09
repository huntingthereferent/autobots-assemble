"""Controlled comparison: evidence-only A/B replay vs inverse A/B construction.

This is an explicitly *limited* baseline. Ordinary A/B uses only its
witnessed source occurrences as implementation choices; it is NOT a
comparison against every possible human/software synthesis strategy.

Both arms share the same first-step native API observations, goals, budget,
and held-out real in-process API executor. Goals never enter the generator.
No external accounts, live work, or native ARC engine are invoked.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
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


MAX_CHECKS = 8


def witnessed_rows(domain: str) -> tuple[dict[str, str], ...]:
    if domain == "activation":
        return tuple({
            "route_actor": actor,
            "selector_assignee": who,
            "selector_relation": relation,
        } for actor in ("other", "tester")
          for who, relation in (("james", "study"), ("other", "review")))
    if domain == "work-ledger":
        return tuple({
            "state": state,
            "lane": lane,
            "next_movement": movement,
        } for state in ("FROZEN", "MOVE")
          for lane, movement in (
              ("Research", "Compare witnesses"),
              ("Operations", "Check validation"),
          ))
    raise ValueError(domain)


def activation_test(row: dict[str, str], goal: tuple[str, str]) -> bool:
    """Two real Continuity operations: resolve -> render selected handoff."""
    route = ActivationRoute(
        activation_id="controlled-native-api-fixture",
        surfaces=("begin review",),
        actor_id=row["route_actor"],
        referent="controlled activation fixture",
        projection="task_queue",
        selectors={
            "assignee": row["selector_assignee"],
            "required_relation": row["selector_relation"],
        },
    )
    resolved = ActivationRegistry((route,)).resolve(
        "begin review", actor_id="tester",
    )
    if resolved is None:
        return False
    target = Handoff(
        handoff_id="fixture",
        referent="fixed goal",
        from_actor="fixture",
        to_actor=goal[0],
        required_relation=goal[1],
        metadata={"title": "held-out task"},
    )
    state = HandoffState(handoff_id=target.handoff_id, status="READY")
    selected = run_activation(
        resolved, surface="begin review", handoffs=((target, state),),
    )
    return len(selected.items) == 1


def ledger_test(row: dict[str, str], goal: tuple[str, str]) -> bool:
    """Two real Continuity operations: parse -> admit isolated handoff."""
    with TemporaryDirectory(prefix="ab_comparison_ledger_") as temp:
        path = Path(temp) / "synthetic-ledger.md"
        path.write_text(
            "# Synthetic test only\n"
            "## Active ALL WORK\n"
            "| Work | Lane | State | Next movement |\n"
            "|---|---|---|---|\n"
            f"| [Evaluate](research/probe.md) | {row['lane']} | {row['state']} | {row['next_movement']} |\n"
            "## Archive\n",
            encoding="utf-8",
        )
        parsed = read_active_work(path)
        handoffs = HandoffRuntime()
        ids = admit_active_work(handoffs, path, actor_id="tester")
        if not parsed or len(ids) != 1:
            return False
        stored = handoffs.get(ids[0])
        return (
            handoffs.state(ids[0]).status == "READY"
            and stored.inputs["lane"] == goal[0]
            and stored.inputs["next_movement"] == goal[1]
        )


NATIVE = {"activation": activation_test, "work-ledger": ledger_test}


def first_step(domain: str, row: dict[str, str]) -> int:
    if domain == "activation":
        route = ActivationRoute(
            activation_id="initial-probe",
            surfaces=("begin review",),
            actor_id=row["route_actor"],
            referent="controlled activation fixture",
            projection="task_queue",
        )
        return int(
            ActivationRegistry((route,)).resolve(
                "begin review", actor_id="tester",
            ) is not None
        )
    with TemporaryDirectory(prefix="ab_comparison_source_") as temp:
        path = Path(temp) / "synthetic-ledger.md"
        path.write_text(
            "# Synthetic test only\n"
            "## Active ALL WORK\n"
            "| Work | Lane | State | Next movement |\n"
            "|---|---|---|---|\n"
            f"| [Evaluate](research/probe.md) | {row['lane']} | {row['state']} | {row['next_movement']} |\n"
            "## Archive\n",
            encoding="utf-8",
        )
        return int(bool(read_active_work(path)))


def options_from_shared_sources(domain: str):
    rows = witnessed_rows(domain)
    witnessed = tuple(
        ABOccurrence.create(
            referent=domain,
            relations=dict(row),
            continuation=(first_step(domain, row),),
        )
        for row in rows
    )
    state = information_closure(witnessed)
    proposals = derive_relation_constructions(
        witnessed, state,
        source_locators=tuple(f"fixture://{domain}/{i}" for i in range(len(rows))),
        witness_contract=f"controlled {domain} one-step native API observations",
        horizon=1,
        intent="construct",
        max_candidates=MAX_CHECKS,
    )
    return rows, witnessed, state, proposals


def blind_cartesian_options(domain: str) -> tuple[dict[str, str], ...]:
    """Naive non-A/B recombination from the EXACT SAME witnessed values.

    No forward quotient and no proof-block restriction. The generator
    cannot inspect held-out goals or native acceptance behavior.
    """
    rows = witnessed_rows(domain)
    names = tuple(sorted(rows[0]))
    values = tuple(
        tuple(sorted(set(row[name] for row in rows))) for name in names
    )
    originals = {json.dumps(row, sort_keys=True) for row in rows}
    novel = tuple(
        dict(zip(names, valueset))
        for valueset in product(*values)
        if json.dumps(dict(zip(names, valueset)), sort_keys=True) not in originals
    )
    return novel


def blind_comparison(domain: str, goal: tuple[str, str], *,
                     max_checks: int = MAX_CHECKS) -> Result:
    """One additional non-A/B search baseline under identical API cap."""
    if not 1 <= max_checks <= MAX_CHECKS:
        raise ValueError("bounded equal holdout-check budget required")
    rows = witnessed_rows(domain)
    novel = blind_cartesian_options(domain)
    winner = None
    checks = 0
    for row in (*rows, *novel)[:max_checks]:
        checks += 1
        if NATIVE[domain](row, goal):
            winner = tuple(sorted(row.items()))
            break
    return Result(
        arm="blind_cartesian", domain=domain, goal=goal,
        success=winner is not None, calls=checks,
        winner=winner, proposals_in_inventory=len(novel),
    )


@dataclass(frozen=True)
class Result:
    arm: str
    domain: str
    goal: tuple[str, str]
    success: bool
    calls: int
    winner: tuple[tuple[str, str], ...] | None
    proposals_in_inventory: int


def compare(domain: str, goal: tuple[str, str], *,
            max_checks: int = MAX_CHECKS) -> tuple[Result, Result]:
    """Equal cap; evidence-only inventory versus same evidence + proposals.

    The completion oracle executes the *existing native interface* and
    never appears in the constructor input. Iteration order is fixed
    independent of the goal; cost counts exact holdout checks.
    """
    if not 1 <= max_checks <= MAX_CHECKS:
        raise ValueError("bounded equal holdout-check budget required")
    rows, observed, closure, proposals = options_from_shared_sources(domain)
    assert len(closure.continuation_partition) == 2
    originals = tuple(dict(row) for row in rows)
    novel = tuple(dict(p.structure["relation_values"]) for p in proposals)
    assert len(set(json.dumps(x, sort_keys=True) for x in (*originals, *novel))) == len(originals) + len(novel)
    arms = (
        ("evidence_only", originals),
        ("ab_with_construction", originals + novel),
    )
    outputs = []
    for name, choices in arms:
        winner = None
        checks = 0
        for row in choices[:max_checks]:
            checks += 1
            if NATIVE[domain](row, goal):
                winner = tuple(sorted(row.items()))
                break
        outputs.append(Result(
            arm=name, domain=domain, goal=goal,
            success=winner is not None, calls=checks,
            winner=winner, proposals_in_inventory=(0 if name == "evidence_only" else len(novel)),
        ))
    return tuple(outputs)


class HeldOutCompletionComparisonTests(unittest.TestCase):
    """Predeclared native-interface scenarios; both arms see identical data."""

    GOALS = {
        "activation": {
            "requires_new": ("james", "review"),
            "already_witnessed": ("james", "study"),
            "unreachable": ("missing-user", "review"),
        },
        "work-ledger": {
            "requires_new": ("Research", "Check validation"),
            "already_witnessed": ("Research", "Compare witnesses"),
            "unreachable": ("Research", "Unwitnessed validation"),
        },
    }

    def test_predeclared_completion_outcomes(self):
        for domain, goals in self.GOALS.items():
            for label, goal in goals.items():
                with self.subTest(domain=domain, goal=label):
                    baseline, inverse = compare(domain, goal)
                    self.assertEqual(baseline.proposals_in_inventory, 0)
                    self.assertEqual(inverse.proposals_in_inventory, 4)
                    self.assertLessEqual(baseline.calls, MAX_CHECKS)
                    self.assertLessEqual(inverse.calls, MAX_CHECKS)
                    if label == "requires_new":
                        self.assertFalse(baseline.success)
                        self.assertTrue(inverse.success)
                        self.assertGreater(inverse.calls, baseline.calls)
                    elif label == "already_witnessed":
                        self.assertTrue(baseline.success)
                        self.assertTrue(inverse.success)
                        self.assertEqual(baseline.calls, inverse.calls)
                        self.assertEqual(baseline.winner, inverse.winner)
                    else:
                        self.assertFalse(baseline.success)
                        self.assertFalse(inverse.success)
                        self.assertEqual(baseline.calls, 4)
                        self.assertEqual(inverse.calls, 8)

    def test_inventory_is_goal_blind_and_source_conserving(self):
        for domain in self.GOALS:
            originals, witnessed, closure, proposals = options_from_shared_sources(domain)
            self.assertEqual(len(originals), 4)
            self.assertEqual(len(proposals), 4)
            source_refs = {f"fixture://{domain}/{i}" for i in range(4)}
            for p in proposals:
                self.assertEqual(p.status, "PROPOSED")
                self.assertEqual(p.horizon, 1)
                self.assertTrue(all(ref in source_refs for ref in p.source_locators))
                self.assertTrue(all(
                    ref in source_refs for ref in
                    p.structure["component_source_locators"].values()
                ))
                self.assertNotIn(
                    p.structure["relation_values"],
                    originals,
                )
            # Candidate ordering cannot depend on which held-out task wins.
            first = tuple(p.proposal_id for p in proposals)
            for _goal in self.GOALS[domain].values():
                self.assertEqual(
                    tuple(p.proposal_id for p in options_from_shared_sources(domain)[3]),
                    first,
                )


    def test_non_ab_cartesian_baseline_has_same_novel_candidate_coverage(self):
        """A/B is NOT entitled to a win just for making combinations."""
        for domain in self.GOALS:
            originals, _observed, _state, proposals = options_from_shared_sources(domain)
            inverse_set = {
                json.dumps(p.structure["relation_values"], sort_keys=True)
                for p in proposals
            }
            blind_set = {
                json.dumps(candidate, sort_keys=True)
                for candidate in blind_cartesian_options(domain)
            }
            self.assertEqual(len(originals), 4)
            self.assertEqual(len(inverse_set), 4)
            self.assertEqual(inverse_set, blind_set)

    def test_cartesian_can_also_finish_recombination_goals(self):
        """Measure whether the observed gain is A/B-specific or merely search."""
        results = []
        for domain, goals in self.GOALS.items():
            for label, goal in goals.items():
                original, inverse = compare(domain, goal)
                blind = blind_comparison(domain, goal)
                results.append((label, original, inverse, blind))
                self.assertEqual(blind.proposals_in_inventory, 4)
                self.assertEqual(blind.success, inverse.success)
                self.assertLessEqual(blind.calls, MAX_CHECKS)
                if label == "unreachable":
                    self.assertFalse(blind.success)
                if label == "already_witnessed":
                    self.assertEqual(blind.calls, original.calls)
                if label == "requires_new":
                    self.assertTrue(blind.success)
                    self.assertFalse(original.success)
        self.assertEqual(sum(x[1].success for x in results), 2)
        self.assertEqual(sum(x[2].success for x in results), 4)
        self.assertEqual(sum(x[3].success for x in results), 4)
        print("AB_CONSTRUCTION_THREE_ARM_CONTROL " + json.dumps({
            "evidence_only_api_successes": sum(x[1].success for x in results),
            "ab_construction_api_successes": sum(x[2].success for x in results),
            "blind_cartesian_api_successes": sum(x[3].success for x in results),
            "control_meaning": "No A/B-specific lift over blind Cartesian at full 8-check budget",
            "costs": {
                "evidence_only": sum(x[1].calls for x in results),
                "ab_construction": sum(x[2].calls for x in results),
                "blind_cartesian": sum(x[3].calls for x in results),
            },
            "predeclared_fixtures": True,
            "native_interface": "isolated in-process; not external work",
        }, sort_keys=True), flush=True)

    def test_equal_evaluation_budget_cap(self):
        for domain, goal_set in self.GOALS.items():
            for goal in goal_set.values():
                a, b = compare(domain, goal, max_checks=4)
                self.assertLessEqual(a.calls, 4)
                self.assertLessEqual(b.calls, 4)
                self.assertEqual(a.success, b.success)
                self.assertEqual(a.winner, b.winner)
            with self.assertRaises(ValueError):
                compare(domain, next(iter(goal_set.values())), max_checks=0)

    def test_overall_six_task_score_is_not_unconditional_gain(self):
        overall = []
        for domain, goals in self.GOALS.items():
            for label, goal in goals.items():
                left, right = compare(domain, goal)
                overall.append((domain, label, left, right))
        self.assertEqual(
            sum(a.success for _, _, a, _ in overall), 2
        )
        self.assertEqual(
            sum(b.success for _, _, _, b in overall), 4
        )
        # Extra tests are an explicit cost of wider search.
        self.assertGreater(
            sum(b.calls for _, _, _, b in overall),
            sum(a.calls for _, _, a, _ in overall),
        )
        print("AB_CONSTRUCTION_HELD_OUT_COMPARISON " + json.dumps({
            "source": "local-native-api-fixtures",
            "baseline": "evidence-only replay, NOT every possible standard A/B planner",
            "holdout_budget_per_arm": MAX_CHECKS,
            "cases": [
                {
                    "domain": domain,
                    "goal_class": label,
                    "evidence_only_success": a.success,
                    "construction_success": b.success,
                    "evidence_only_checks": a.calls,
                    "construction_checks": b.calls,
                }
                for domain, label, a, b in overall
            ],
            "baseline_completed": sum(a.success for _, _, a, _ in overall),
            "construction_completed": sum(b.success for _, _, _, b in overall),
            "baseline_checks": sum(a.calls for _, _, a, _ in overall),
            "construction_checks": sum(b.calls for _, _, _, b in overall),
            "native_api_observations_not_external_live_work": True,
        }, sort_keys=True), flush=True)

    def test_real_code_and_state_are_untouched(self):
        with TemporaryDirectory(prefix="compare_state_") as temp:
            from runtime.service import EcosystemService
            service = EcosystemService(data_dir=temp)
            old = service.runtime.snapshot()
            for domain, goals in self.GOALS.items():
                for goal in goals.values():
                    compare(domain, goal)
            self.assertEqual(service.runtime.snapshot(), old)
            self.assertEqual(service.agent_lineage.roots_for_actor("james"), ())


if __name__ == "__main__":
    unittest.main()
