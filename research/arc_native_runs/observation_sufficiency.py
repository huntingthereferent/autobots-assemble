"""Finite A/B observation-quotient checker, requiring no game SDK or model.

For deterministic total actions A and B, a deterministic observation-only
transition exists precisely when observations are stable under BOTH actions.
The module checks a finite declared state family and emits an exact witness
when the criterion fails. It does not solve ARC games or inspect private state.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, TypeVar

S = TypeVar("S", bound=Hashable)
O = TypeVar("O", bound=Hashable)
ACTIONS = ("A", "B")


def finite_observation_quotient(
    states: Iterable[S],
    observe: Callable[[S], O],
    transitions: dict[str, Callable[[S], S]],
) -> dict:
    """Exhaustively test the observation congruence condition.

    The caller supplies the *entire* finite state domain, with transitions
    closed on it. A pass establishes a well-defined observation transition
    for every declared action, not generalization to unexamined game states.
    """
    ordered = tuple(states)
    if not ordered or len(set(ordered)) != len(ordered):
        raise ValueError("states must be nonempty and distinct")
    if set(transitions) != set(ACTIONS):
        raise ValueError("exactly A and B transition maps are required")
    domain = set(ordered)
    outputs = {state: observe(state) for state in ordered}
    candidate: dict[tuple[O, str], O] = {}
    owner: dict[tuple[O, str], S] = {}
    for action in ACTIONS:
        fn = transitions[action]
        for state in ordered:
            successor = fn(state)
            if successor not in domain:
                raise ValueError(f"action {action} leaves declared state domain")
            key = (outputs[state], action)
            next_output = outputs[successor]
            if key in candidate and candidate[key] != next_output:
                prev = owner[key]
                return {
                    "sufficient": False,
                    "state_count": len(ordered),
                    "observed_state_count": len(set(outputs.values())),
                    "witness": {
                        "same_observation": outputs[state],
                        "action": action,
                        "first_state": prev,
                        "second_state": state,
                        "first_successor_observation": candidate[key],
                        "second_successor_observation": next_output,
                    },
                }
            candidate[key] = next_output
            owner.setdefault(key, state)
    return {
        "sufficient": True,
        "state_count": len(ordered),
        "observed_state_count": len(set(outputs.values())),
        "quotient_transitions": candidate,
        "witness": None,
    }


@dataclass(frozen=True)
class ExampleState:
    """Illustrative hidden history; this is NOT SP80 game state."""

    position: int
    interacted: int
    win: int


def example_actions() -> dict[str, Callable[[ExampleState], ExampleState]]:
    def move(s: ExampleState) -> ExampleState:
        return ExampleState(1 - s.position, s.interacted, s.win)

    def interact(s: ExampleState) -> ExampleState:
        if s.win:
            return s
        if s.interacted:
            return ExampleState(s.position, 1, 1)
        return ExampleState(s.position, 1, 0)

    return {"A": move, "B": interact}


def example_states() -> tuple[ExampleState, ...]:
    """Full action-closed reachable domain from ExampleState(0,0,0)."""
    transitions = example_actions()
    start = ExampleState(0, 0, 0)
    queue, seen = [start], {start}
    for state in queue:
        for fn in transitions.values():
            next_state = fn(state)
            if next_state not in seen:
                queue.append(next_state)
                seen.add(next_state)
    return tuple(queue)


def visible_feedback(s: ExampleState) -> tuple[int, int]:
    """Position and present win status; interaction count is hidden."""
    return (s.position, s.win)
