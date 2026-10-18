"""ARC-AGI-3 experimental agent: ORIGINAL 48-law marked F3 window.

Mathematical source: work.arc_like_maze.window_combined.CombinedWorld,
branch_rule, and WindowProcess. Forty-eight B tables form 16 ROOTED and
14 FULL-STATE labeled classes; a nonrooted conjugacy is NOT an admissible
root-preserving witness. The former nine-phi experiment is archived.

This is a self-contained official MyAgent file. Native inputs are unchanged
64x64 color frames and explicitly advertised legal actions. An ARC action
is NEVER intrinsically the mathematical A or B: assigning two simple native
actions below is a provisional direct-realization FALSIFICATION experiment.
If the candidate family fails, do not reset it or promote a saved route.
No native-F3 relation, universal solver, or game win is claimed.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
from itertools import combinations, product
from typing import Any

import numpy as np
from agents.agent import Agent
from arcengine import FrameData, GameAction, GameState


# EXACT parameter ordering from window_combined.family():
# CombinedWorld(k, c, e, t) for k,e,t,c in 4 x 2 x 2 x 3.
WINDOW48 = tuple((k, c, e, t) for k, e, t, c in
                 product(range(4), range(2), range(2), range(3)))
ORIGIN = (0, 0, 0)
ROOTED_CLASS_COUNT = 16
FULL_STATE_CLASS_COUNT = 14


def window48_q(u: int, v: int, law: tuple[int, int, int, int]) -> int:
    """Literal window_combined.combined_rule source formula at q0(u,v)."""
    k, c, e, t = law
    if (k not in range(4) or c not in range(3)
            or e not in (0, 1) or t not in (0, 1)):
        raise ValueError("law is not a member of the original 48")
    return (int(u == 2 and v < k)
            + e * int(u == 0 and v == 0)
            + t * (int(u == 1 and v == 0) - int(u == 1 and v == 1))
            + c * ((v + u + 1) ** 2 - v ** 2)) % 3


def window48_step(state: tuple[int, int, int], letter: str,
                  law: tuple[int, int, int, int]) -> tuple[int, int, int]:
    """Exact source depth-3 A/B transitions, with PRE-ACTION x0 and x1."""
    if len(state) != 3 or any(v not in range(3) for v in state):
        raise ValueError("the declared finite check is at depth three")
    u, v, z = state
    if letter == "A":
        return ((u + 1) % 3, v, z)
    if letter == "B":
        return (u, (v + u + 1) % 3, (z + window48_q(u, v, law)) % 3)
    raise ValueError("only source mathematical A/B letters are admitted")


def window48_inverse(state: tuple[int, int, int], letter: str,
                     law: tuple[int, int, int, int]) -> tuple[int, int, int]:
    """Independent check of the original B triangular inverse."""
    if len(state) != 3 or any(v not in range(3) for v in state):
        raise ValueError("the declared finite check is at depth three")
    u, v, z = state
    if letter == "A":
        return ((u - 1) % 3, v, z)
    if letter == "B":
        old_v = (v - u - 1) % 3
        return (u, old_v, (z - window48_q(u, old_v, law)) % 3)
    raise ValueError("only source mathematical A/B letters are admitted")


def window48_endpoint(word: str, law: tuple[int, int, int, int],
                      origin: tuple[int, int, int] = ORIGIN
                      ) -> tuple[int, int, int]:
    state = origin
    for letter in word:
        state = window48_step(state, letter, law)
    return state


def observation_key(frame: FrameData) -> bytes:
    grid = np.asarray(frame.frame)
    if grid.ndim == 3:
        grid = grid[-1]
    if grid.size != 64 * 64:
        raise ValueError("not a complete native 64x64 observation")
    values = grid.reshape(64, 64)
    if np.any(values < 0) or np.any(values > 15):
        raise ValueError("native colors outside 0..15")
    return blake2b(np.ascontiguousarray(values, dtype=np.uint8).tobytes(),
                   digest_size=16).digest()


@dataclass(frozen=True)
class Window48Report:
    status: str
    candidate_indices: tuple[int, ...]
    rooted_class_keys: tuple[tuple[int, int, int], ...]
    observed_word_count: int
    visible_collisions: int
    visible_distinctions: int


class Window48Evidence:
    """One rooted native trajectory, under an EXPLICITLY PROVISIONAL A/B pair.

    Source F3 state-equality => equal observed native frames is a necessary
    consequence of a direct action-preserving observable-state map. Violating
    it removes the proposed law. Native frames being equal NEVER proves the
    full native hidden states (or mathematical states) are equal.

    The fourteen full-state class count is mathematical classification over
    ALL states, and may NOT be inferred from these rooted observations.
    """

    def __init__(self, native_a: int, native_b: int, root: bytes):
        if native_a == native_b:
            raise ValueError("A and B require distinct provisional native controls")
        self.native_actions = (native_a, native_b)
        self.words: dict[str, bytes] = {"": root}
        self.current_word = ""
        self.candidates = tuple(range(len(WINDOW48)))
        self.visible_collisions = 0
        self.visible_distinctions = 0

    def record(self, letter: str, observed_frame: bytes) -> Window48Report:
        if letter not in ("A", "B"):
            raise ValueError("invalid candidate generator label")
        next_word = self.current_word + letter
        remaining = []
        for i in self.candidates:
            law = WINDOW48[i]
            end = window48_endpoint(next_word, law)
            if all(window48_endpoint(old_word, law) != end
                   or old_frame == observed_frame
                   for old_word, old_frame in self.words.items()):
                remaining.append(i)
        self.visible_collisions += sum(
            frame == observed_frame for frame in self.words.values())
        self.visible_distinctions += sum(
            frame != observed_frame for frame in self.words.values())
        self.current_word = next_word
        self.words[next_word] = observed_frame
        self.candidates = tuple(remaining)
        return self.report()

    def report(self) -> Window48Report:
        rooted = tuple(sorted({(WINDOW48[i][0], WINDOW48[i][2], WINDOW48[i][3])
                               for i in self.candidates}))
        return Window48Report(
            "CONDITIONAL_ROOTED_WINDOW48" if self.candidates
            else "WALL_NO_DIRECT_ROOTED_WINDOW48_MATCH",
            self.candidates, rooted, len(self.words)-1,
            self.visible_collisions, self.visible_distinctions,
        )

    def rank_letters(self) -> tuple[str, str]:
        """Use source endpoint-collision differences, never a game heuristic."""
        def measure(letter: str):
            word = self.current_word + letter
            patterns = [tuple(window48_endpoint(word, WINDOW48[i]) ==
                              window48_endpoint(old, WINDOW48[i])
                              for old in self.words)
                        for i in self.candidates]
            discrimination = sum(a != b for a, b in combinations(patterns, 2))
            predicted_returns = sum(any(p) for p in patterns)
            change = int(bool(self.current_word) and
                         self.current_word[-1] != letter)
            return (discrimination, predicted_returns, change)
        return tuple(sorted("AB", key=lambda x: (measure(x), x), reverse=True))


def allowed_actions(frame: FrameData) -> list[GameAction]:
    advertised = getattr(frame, "available_actions", None)
    if not advertised:
        return []
    values = {int(getattr(a, "value", a)) for a in advertised}
    return [a for a in GameAction
            if a is not GameAction.RESET and a.value in values]


class MyAgent(Agent):
    """Single executable interface; F3-48 investigation, NOT goal-solving."""

    MAX_ACTIONS = 40

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.f3_48: Window48Evidence | None = None
        self.pending_letter: str | None = None
        self.last_level: int | None = None
        self.stopped_at_wall = False

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        if latest_frame.state is GameState.WIN:
            return True
        if self.stopped_at_wall:
            return True
        available = allowed_actions(latest_frame)
        # Coordinate-click ACTION6 needs observed coordinates; invented
        # midpoint clicks or fake A/B generators are not admissible.
        if latest_frame.state not in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            if len([a for a in available if a.value in (1, 2, 3, 4, 5)]) < 2:
                return True
        return False

    def choose_action(self, frames: list[FrameData], latest_frame: FrameData
                      ) -> GameAction:
        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            self.f3_48 = None
            self.pending_letter = None
            self.last_level = None
            self.stopped_at_wall = False
            return GameAction.RESET

        legal = allowed_actions(latest_frame)
        simple = [a for a in legal if a.value in (1, 2, 3, 4, 5)]
        pair = tuple(a.value for a in simple[:2]) if len(simple) >= 2 else None
        if pair is None:
            # is_done will stop before this on the official SDK runner.
            self.stopped_at_wall = True
            raise RuntimeError("WALL: no grounded pair of simple native controls")
        try:
            native_frame = observation_key(latest_frame)
        except ValueError:
            self.stopped_at_wall = True
            raise RuntimeError("WALL: native frame unavailable")
        level = int(getattr(latest_frame, "levels_completed", 0))
        if self.f3_48 is not None and (
                pair != self.f3_48.native_actions or level != self.last_level):
            self.f3_48 = None
            self.pending_letter = None
        if self.f3_48 is None:
            self.f3_48 = Window48Evidence(*pair, root=native_frame)
        elif self.pending_letter is not None:
            self.f3_48.record(self.pending_letter, native_frame)
            self.pending_letter = None
        self.last_level = level
        result = self.f3_48.report()
        if not result.candidate_indices:
            self.stopped_at_wall = True
            # A comparison has just contradicted the entire proposed family.
            # Do not reset and start over with a new ungrounded native pair.
            raise RuntimeError("WALL: all 48 direct rooted native-law proposals refuted")
        letter = self.f3_48.rank_letters()[0]
        control = self.f3_48.native_actions[0 if letter == "A" else 1]
        action = next(a for a in simple if a.value == control)
        self.pending_letter = letter
        action.reasoning = {
            "policy": "WINDOW48_SOURCE_ROOTED_EVIDENCE",
            "status": result.status,
            "provisional_native_action_roles": list(pair),
            "role": letter,
            "rooted_conjugacy_not_full_state_claim": True,
            "48_source_laws_remaining": len(result.candidate_indices),
            "rooted_class_keys_remaining": [
                list(x) for x in result.rooted_class_keys],
            "full_state_classes_not_inferred": FULL_STATE_CLASS_COUNT,
            "word_before": self.f3_48.current_word,
            "word_next": self.f3_48.current_word+letter,
            "native_colors_not_reduced_modulo_three": True,
            "hypothesis_only_no_arc_goal_model": True,
        }
        return action
