"""Observation-driven finite-world runner.

The executor is an external boundary: only its returned observation is used
to eliminate candidates. This module does not simulate an AI client.
"""
from dataclasses import dataclass
from typing import Callable
from work.arc_like_maze.math import World
from interfaces.math.probe_selector import select_probe, record_observation

Executor = Callable[[str], tuple[int, ...]]


@dataclass(frozen=True)
class Round:
    probe: str
    observed: tuple[int, ...]
    predictions: tuple[tuple[int, ...], ...]
    surviving_count: int
    eliminated_count: int


@dataclass(frozen=True)
class Run:
    status: str
    survivors: tuple[World, ...]
    rounds: tuple[Round, ...]


def run(worlds: tuple[World, ...], execute: Executor, *,
        max_rounds: int = 10, max_depth: int = 12) -> Run:
    """Select -> execute -> observe -> filter -> repeat.

    Each probe starts from the executor's reset/origin state. The caller must
    supply an executor that guarantees that reset contract. Failure to do so
    invalidates model comparisons; no hidden reset is assumed.
    """
    if not worlds:
        raise ValueError("candidate worlds required")
    if max_rounds < 0:
        raise ValueError("max_rounds must be nonnegative")
    candidates = worlds
    history = []
    for _ in range(max_rounds):
        selected = select_probe(candidates, max_depth)
        if selected.actions is None:
            return Run("INDISTINGUISHABLE_WITHIN_HORIZON", candidates, tuple(history))
        actions = selected.actions
        predictions = tuple(w.apply(actions) for w in candidates)
        observed = tuple(execute(actions))
        if len(observed) != candidates[0].depth:
            raise ValueError("executor returned a state of incorrect dimension")
        outcome = record_observation(candidates, actions, observed)
        history.append(Round(actions, observed, predictions,
                             len(outcome.surviving), len(outcome.eliminated)))
        if not outcome.surviving:
            return Run("MODEL_SET_EXHAUSTED", (), tuple(history))
        candidates = outcome.surviving
    return Run("ROUND_LIMIT", candidates, tuple(history))


def finite_world_executor(world: World) -> Executor:
    """Explicit in-memory test double; not a live-world adapter."""
    return world.apply
