"""Paired, finite WORLD48 runner comparison. No official ARC evaluation.

Runner policies receive only law IDs, identical rooted starts, labeled A/B
transitions, identical observation caps and depth bounds. Published example
solutions are not input to the runners. Source-owned replay alone admits
a found witness. A budget wall is never promoted into a negative proof.
"""
from __future__ import annotations

from collections import deque
from typing import Any

from work.arc3.window48_challenges import check_rooted_paths
from work.arc_like_maze.window_combined import family

ROOT = (0, 0, 0)
POLICIES = ("breadth", "depth")


def _challenge(challenge_id: int) -> tuple[int, int]:
    if type(challenge_id) is not int or not 0 <= challenge_id < 48:
        raise ValueError("challenge_id must be in 0..47")
    # Derive law IDs directly from the declared family. This path never
    # loads the source roster or generates any saved answer words.
    chart, position = divmod(challenge_id, 16)
    reps = [i for i, world in enumerate(family()) if world.coefficient == chart]
    first, second = reps[position], reps[(position + 1) % len(reps)]
    if position == 15:
        first, second = second, first
    return first, second


def _limits(budget: int, depth_bound: int, policy: str) -> None:
    if type(budget) is not int or not 0 <= budget <= 100000:
        raise ValueError("budget must be 0..100000 individual observations")
    if type(depth_bound) is not int or not 1 <= depth_bound <= 64:
        raise ValueError("depth bound must be 1..64")
    if policy not in POLICIES:
        raise ValueError("unknown runner policy")


def run_runner(challenge_id: int, policy: str, *,
               budget: int = 100, depth_bound: int = 8) -> dict[str, Any]:
    """Run a fixed-order frontier policy; two law-step observations per expansion."""
    _limits(budget, depth_bound, policy)
    ids = _challenge(challenge_id)
    laws = family()
    source, target = laws[ids[0]], laws[ids[1]]
    frontier = deque([("", ROOT, ROOT)])
    seen_pairs = {(ROOT, ROOT)}
    seen_left = {ROOT: ("", ROOT)}
    trace = []
    observations = 0
    depth_hit = False

    def result(status: str, witness: tuple[str, str] | None = None) -> dict[str, Any]:
        return {
            "scope": "declared-world48-rooted-runner-comparison/v1",
            "challenge_id": challenge_id,
            "law_ids": list(ids),
            "policy": policy,
            "budget": budget,
            "depth_bound": depth_bound,
            "observations": observations,
            "expanded_edges": observations // 2,
            "status": status,
            "witness_words": list(witness) if witness is not None else None,
            "trace": trace,
        }

    while frontier:
        word, left_state, right_state = (
            frontier.popleft() if policy == "breadth" else frontier.pop()
        )
        if len(word) >= depth_bound:
            depth_hit = True
            continue
        for action in "AB":
            if observations + 2 > budget:
                return result("BUDGET_WALL")
            next_left = source.step(left_state, action)
            next_right = target.step(right_state, action)
            observations += 2
            next_word = word + action
            trace.append({
                "word": next_word, "action": action,
                "source_before": left_state, "target_before": right_state,
                "source_after": next_left, "target_after": next_right,
            })
            previous = seen_left.get(next_left)
            if previous is not None and previous[1] != next_right:
                witness = previous[0], next_word
                # Replay each submitted path from the marked origin against
                # the source transition laws. Never trust a runner's verdict.
                verified = check_rooted_paths(list(ids), *witness)
                if not verified["passed"]:
                    raise AssertionError("runner witness failed original source replay")
                return result("VERIFIED_ROOTED_SPLIT", witness)
            if previous is None:
                seen_left[next_left] = (next_word, next_right)
            pair = (next_left, next_right)
            if pair not in seen_pairs:
                seen_pairs.add(pair)
                frontier.append((next_word, next_left, next_right))
    return result("DEPTH_WALL" if depth_hit else "EXHAUSTED_DECLARED_STATES")


def compare_runners(challenge_id: int, *, budget: int = 100,
                    depth_bound: int = 8) -> dict[str, Any]:
    """Paired trials: same pinned task, budgets and allowed observations."""
    left, right = _challenge(challenge_id)
    return {
        "scope": "declared-world48-paired-comparison/v1",
        "challenge_id": challenge_id,
        "law_ids": [left, right],
        "same_budget": budget,
        "same_depth_bound": depth_bound,
        "runners": {
            policy: run_runner(challenge_id, policy, budget=budget, depth_bound=depth_bound)
            for policy in POLICIES
        },
        "boundary": "finite constructed A/B laws; no general agent or official ARC ranking",
    }
