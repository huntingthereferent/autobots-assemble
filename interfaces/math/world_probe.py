"""Exploratory finite world-to-world drift projection.

Uses the existing World construction; not an AI-behavior predictor.
"""
from dataclasses import dataclass
from typing import Iterable
from work.arc_like_maze.math import World


@dataclass(frozen=True)
class Comparison:
    actions: str
    reference: tuple[tuple[int, ...], ...]
    candidate: tuple[tuple[int, ...], ...]
    first_divergence: int | None
    divergent_steps: tuple[int, ...]
    return_steps: tuple[int, ...]


def compare_paths(reference: World, candidate: World, actions: str) -> Comparison:
    """Replay identical actions in both worlds, including the initial state.

    A return step is equality following an unequal state; it is not proof of
    global world equivalence or recovery of a semantic referent.
    """
    if reference.depth != candidate.depth:
        raise ValueError("world dimensions must agree for literal state comparison")
    if any(action not in "AB" for action in actions):
        raise ValueError("only A and B actions are admitted")
    left, right = reference.origin, candidate.origin
    ls, rs = [left], [right]
    for action in actions:
        left = reference.step(left, action)
        right = candidate.step(right, action)
        ls.append(left)
        rs.append(right)
    differences = tuple(i for i, (a, b) in enumerate(zip(ls, rs)) if a != b)
    returns = tuple(i for i in range(1, len(ls)) if ls[i] == rs[i] and ls[i - 1] != rs[i - 1])
    return Comparison(actions, tuple(ls), tuple(rs),
                      differences[0] if differences else None, differences, returns)


def oscillate(reference: World, candidate: World, action_sequences: Iterable[str]) -> tuple[Comparison, ...]:
    """Evaluate independent action probes; no inferred or learned controller."""
    return tuple(compare_paths(reference, candidate, actions) for actions in action_sequences)
