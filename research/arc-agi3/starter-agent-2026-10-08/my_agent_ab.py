"""Minimal ARC A/B branch.

No inherited ARC solver, game IDs, object ontology, action semantics, scores,
planner, or game-source knowledge.

The environment supplies the current observation, legal actions, and win state.
The branch retains only witnessed action -> next-observation relations.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Any
import numpy as np

from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent


def key(frame: FrameData) -> bytes:
    a = np.asarray(frame.frame)
    return a.tobytes()


def legal(frame: FrameData) -> list[GameAction]:
    vals = set(getattr(frame, "available_actions", []) or [])
    return [a for a in GameAction
            if a is not GameAction.RESET and not a.is_complex()
            and (not vals or a.value in vals or a in vals)]


class MyAgent(Agent):
    MAX_ACTIONS = 600

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.support: dict[tuple[bytes, int], bytes] = {}
        self.tried: defaultdict[bytes, set[int]] = defaultdict(set)
        self.last: tuple[bytes, int] | None = None

    @property
    def name(self) -> str:
        return f"{super().name}.ab-minimal"

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN

    def choose_action(self, frames: list[FrameData], latest: FrameData) -> GameAction:
        if self.last is not None and np.asarray(latest.frame).size:
            self.support[self.last] = key(latest)
            self.tried[self.last[0]].add(self.last[1])

        if latest.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            self.last = None
            return GameAction.RESET

        k = key(latest)
        acts = legal(latest)
        if not acts:
            self.last = None
            return GameAction.RESET

        # The only admitted next movement is an available relation not yet
        # witnessed from this exact current observation. No action meaning,
        # visual interpretation, score, or future route is supplied.
        untried = [a for a in acts if a.value not in self.tried[k]]
        action = untried[0] if untried else acts[0]
        self.last = (k, action.value)
        action.reasoning = {
            "operation": "ab-minimal",
            "support": "available action from current observation",
            "prior_witness": action.value in self.tried[k],
        }
        return action
