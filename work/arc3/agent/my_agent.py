"""F3-first native ARC-AGI-3 experimental agent; one-file Kaggle entry.

The F3 laws are transcribed from work.arc_like_maze.math.World(depth=3).
Native ARC actions have no intrinsic mathematical A/B identity: two advertised
simple actions are assigned provisional roles for a bounded falsification test.
This is not a proved correspondence, general solver, or replay policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
from itertools import combinations, product
from typing import Any

import numpy as np

from agents.agent import Agent
from arcengine import FrameData, GameAction, GameState


PHIS = tuple((0, a, b) for a, b in product(range(3), repeat=2))


def f3_step(state: tuple[int, int, int], letter: str,
            phi: tuple[int, int, int]) -> tuple[int, int, int]:
    """Exactly the depth-three F3 transformations in the source research."""
    x0, x1, x2 = state
    if letter == "A":
        return ((x0 + 1) % 3, x1, x2)
    if letter == "B":
        return (x0, (x1 + x0 + 1) % 3, (x2 + phi[x1]) % 3)
    raise ValueError("only mathematically declared A and B")


def f3_endpoint(word: str, phi: tuple[int, int, int]) -> tuple[int, int, int]:
    state = (0, 0, 0)
    for letter in word:
        state = f3_step(state, letter, phi)
    return state


def observation_key(frame: FrameData) -> bytes:
    """Keep all 16 native colors; do not map observations modulo three."""
    grid = np.asarray(frame.frame)
    if grid.ndim == 3:
        grid = grid[-1]
    if grid.size != 64 * 64:
        raise ValueError("native 64x64 observation unavailable")
    arr = grid.reshape(64, 64)
    if np.any(arr < 0) or np.any(arr > 15):
        raise ValueError("unexpected ARC color outside 0..15")
    return blake2b(np.ascontiguousarray(arr, dtype=np.uint8).tobytes(), digest_size=16).digest()


@dataclass(frozen=True)
class CandidateReport:
    candidate_indices: tuple[int, ...]
    status: str
    observed_distinctions: int
    visible_equalities: int


class F3Evidence:
    """Compare a rooted native action-word trace against the nine F3 laws.

    Native A/B roles are provisional, not ARC action semantics. Distinct
    observed full frames refute a predicted state equality. Equal visible
    frames do NOT establish equal hidden states or full-state conjugacy.
    """

    def __init__(self, native_a: int, native_b: int, root_key: bytes):
        if native_a == native_b:
            raise ValueError("A and B require distinct native action IDs")
        self.native_actions = (native_a, native_b)
        self.words: dict[str, bytes] = {"": root_key}
        self.word = ""
        self.candidates = tuple(range(len(PHIS)))
        self.observed_distinctions = 0
        self.visible_equalities = 0

    def record(self, letter: str, after: bytes) -> CandidateReport:
        if letter not in ("A", "B"):
            raise ValueError("unrecognized mathematical action letter")
        new_word = self.word + letter
        admitted = []
        for index in self.candidates:
            predicted = f3_endpoint(new_word, PHIS[index])
            if all(f3_endpoint(old_word, PHIS[index]) != predicted or old_key == after
                   for old_word, old_key in self.words.items()):
                admitted.append(index)
        self.observed_distinctions += sum(old_key != after for old_key in self.words.values())
        self.visible_equalities += sum(old_key == after for old_key in self.words.values())
        self.word = new_word
        self.words[new_word] = after
        self.candidates = tuple(admitted)
        return self.report()

    def report(self) -> CandidateReport:
        return CandidateReport(
            self.candidates,
            "CONDITIONAL_F3_CANDIDATES" if self.candidates else "OUTSIDE_DECLARED_F3_FAMILY",
            self.observed_distinctions,
            self.visible_equalities,
        )

    def rank_letters(self) -> tuple[str, str]:
        """Choose finite-field endpoint-collision questions, not ARC heuristics."""
        def score(letter: str) -> tuple[int, int, int]:
            word = self.word + letter
            signatures = [
                tuple(f3_endpoint(word, PHIS[i]) == f3_endpoint(old, PHIS[i])
                      for old in self.words)
                for i in self.candidates
            ]
            separated = sum(left != right for left, right in combinations(signatures, 2))
            predicted_returns = sum(any(sig) for sig in signatures)
            alternate = int(not self.word or self.word[-1] != letter)
            return separated, predicted_returns, alternate
        return tuple(sorted(("A", "B"), key=lambda a: (score(a), a), reverse=True))


def allowed_actions(frame: FrameData) -> list[GameAction]:
    available = getattr(frame, "available_actions", None)
    if not available:
        return []  # Missing affordances are not permission to invent actions.
    values = {int(getattr(a, "value", a)) for a in available}
    return [a for a in GameAction if a is not GameAction.RESET and a.value in values]


class MyAgent(Agent):
    """One ARC entry point, with F3 evidence as the investigative basis."""

    MAX_ACTIONS = 120  # bounded prototype; not a score-optimized action budget

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.f3: F3Evidence | None = None
        self.last_letter: str | None = None
        self.last_level: int | None = None

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN

    def choose_action(self, frames: list[FrameData], latest_frame: FrameData) -> GameAction:
        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            self.f3 = None
            self.last_letter = None
            self.last_level = None
            return GameAction.RESET

        legal = allowed_actions(latest_frame)
        if not legal:
            action = GameAction.RESET
            action.reasoning = {"policy": "F3", "status": "NO_ADVERTISED_ACTIONS"}
            return action

        level = int(getattr(latest_frame, "levels_completed", 0))
        simple = [a for a in legal if a.value in (1, 2, 3, 4, 5)]
        native_pair = tuple(a.value for a in simple[:2]) if len(simple) >= 2 else None
        try:
            key = observation_key(latest_frame)
        except ValueError:
            key = None

        if self.f3 is not None and (self.last_level != level or
                                     native_pair != self.f3.native_actions or key is None):
            self.f3 = None
            self.last_letter = None

        if self.f3 is None and native_pair is not None and key is not None:
            self.f3 = F3Evidence(*native_pair, root_key=key)
        elif self.f3 is not None and self.last_letter is not None and key is not None:
            self.f3.record(self.last_letter, key)
            self.last_letter = None

        self.last_level = level
        if self.f3 is not None and self.f3.candidates:
            letter = self.f3.rank_letters()[0]
            action_id = self.f3.native_actions[0 if letter == "A" else 1]
            action = next(a for a in legal if a.value == action_id)
            self.last_letter = letter
            action.reasoning = {
                "policy": "F3-rooted-relations",
                "role": letter,
                "hypothesis_only": True,
                "native_roles": list(self.f3.native_actions),
                "candidate_count": len(self.f3.candidates),
                "word_before": self.f3.word,
                "next_probe": self.f3.word + letter,
                "visible_equalities_not_state_proof": True,
            }
            return action

        # No fictitious successor law is created when the F3 hypothesis fails.
        action = simple[0] if simple else legal[0]
        if action is GameAction.ACTION6:
            action.set_data({"x": 32, "y": 32})  # interface placeholder, not F3 evidence
        action.reasoning = {
            "policy": "F3",
            "status": "WALL_NO_ADMITTED_F3_CORRESPONDENCE",
            "candidate_count": len(self.f3.candidates) if self.f3 else 0,
            "fallback_is_not_F3_inference": True,
        }
        return action
