"""Finite distinguishing-probe selection and observation-driven candidate updates.

A probe is selected from candidate-world transitions, not chosen by an LLM.
This is a finite experiment planner, not yet a live AI adapter.
"""
from collections import deque
from dataclasses import dataclass
from work.arc_like_maze.math import World


@dataclass(frozen=True)
class Probe:
    actions: str | None
    explored: int
    reason: str


@dataclass(frozen=True)
class Observation:
    actions: str
    observed: tuple[int, ...]
    surviving: tuple[World, ...]
    eliminated: tuple[World, ...]


def select_probe(worlds: tuple[World, ...], max_depth: int = 12) -> Probe:
    """Find shortest action string producing different terminal states.

    BFS guarantees shortest distinguishing sequence within the finite horizon.
    Identical terminal predictions are deduplicated as product states. Returns
    no probe when worlds are observationally indistinguishable at this horizon.
    """
    if not worlds:
        raise ValueError("at least one world required")
    if max_depth < 0:
        raise ValueError("max_depth must be nonnegative")
    if len({w.depth for w in worlds}) != 1:
        raise ValueError("world dimensions must agree")
    initial = tuple(w.origin for w in worlds)
    queue = deque([(initial, "")])
    seen = {initial}
    while queue:
        states, actions = queue.popleft()
        if len(set(states)) > 1:
            return Probe(actions, len(seen), "distinguishing terminal states")
        if len(actions) >= max_depth:
            continue
        for action in "AB":
            following = tuple(w.step(s, action) for w, s in zip(worlds, states))
            if following not in seen:
                seen.add(following)
                queue.append((following, actions + action))
    return Probe(None, len(seen), "no distinction within search horizon")


def record_observation(worlds: tuple[World, ...], actions: str,
                       observed: tuple[int, ...]) -> Observation:
    """Retain worlds predicting the observed terminal state.

    An empty survivor set is an explicit model-set failure, not a license to
    select the nearest candidate or claim a real-world result.
    """
    if any(a not in "AB" for a in actions):
        raise ValueError("only A and B actions are admitted")
    survivors = tuple(w for w in worlds if w.apply(actions) == observed)
    eliminated = tuple(w for w in worlds if w.apply(actions) != observed)
    return Observation(actions, observed, survivors, eliminated)


def next_probe(worlds: tuple[World, ...], actions: str,
               observed: tuple[int, ...], max_depth: int = 12
               ) -> tuple[Observation, Probe | None]:
    """Observation -> candidate update -> next finite discriminating probe."""
    result = record_observation(worlds, actions, observed)
    return result, select_probe(result.surviving, max_depth) if result.surviving else None
