"""ARC3 Gen-1: generic first-contact object/world-model agent.

No public game IDs. No banked solutions. No game-source assumptions.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys
from typing import Any

from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from state import StateView, grid_from_frame_data, perceive
from model import ActionToken, TransitionModel


def legal_actions(latest: FrameData) -> list[GameAction]:
    raw = set(getattr(latest, "available_actions", []) or [])
    out: list[GameAction] = []
    for action in GameAction:
        if action is GameAction.RESET:
            continue
        if not raw or action in raw or action.value in raw:
            out.append(action)
    return out


def token_for(action: GameAction, data: tuple[int, int] | None = None) -> ActionToken:
    if data is None:
        return (int(action.value),)
    return (int(action.value), int(data[0]), int(data[1]))


class MyAgent(Agent):
    MAX_ACTIONS = 700

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.model = TransitionModel()
        self.last_state: StateView | None = None
        self.last_token: ActionToken | None = None
        self.last_level = 0
        self.level_steps = 0
        self.path: list[ActionToken] = []
        self.progress_paths: dict[int, list[ActionToken]] = {}

    @property
    def name(self) -> str:
        return f"{super().name}.first-contact-gen1"

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN

    def _observe(self, latest: FrameData) -> StateView:
        cur = perceive(latest)
        level = int(getattr(latest, "levels_completed", self.last_level))

        if self.last_state is not None and self.last_token is not None:
            dl = level - self.last_level
            bad = latest.state is GameState.GAME_OVER and dl <= 0
            self.model.update(
                self.last_state,
                self.last_token,
                cur,
                level_delta=dl,
                terminal_bad=bad,
            )
            self.level_steps += 1

            if dl > 0:
                self.progress_paths[level] = list(self.path)
                self.level_steps = 0

        self.last_level = level
        return cur

    def _click_candidates(self, latest: FrameData, state: StateView) -> list[tuple[int, int]]:
        g = grid_from_frame_data(latest)
        freq = Counter(int(v) for v in g.ravel())
        ranked: list[tuple[float, int, int]] = []

        for c in state.components:
            if c.size > 192:
                continue
            rarity = 1.0 / max(1, freq[c.color])
            compact = c.size / max(1, c.width * c.height)
            score = 20.0 * rarity + 2.0 / max(1, c.size) + compact
            ranked.append((score, c.cx2 // 2, c.cy2 // 2))

        ranked.sort(reverse=True)
        out: list[tuple[int, int]] = []
        seen = set()
        for _, x, y in ranked:
            p = (max(0, min(63, x)), max(0, min(63, y)))
            if p not in seen:
                seen.add(p)
                out.append(p)
        return out[:32]

    def _candidate_tokens(
        self,
        latest: FrameData,
        state: StateView,
    ) -> list[tuple[GameAction, ActionToken]]:
        result: list[tuple[GameAction, ActionToken]] = []
        for action in legal_actions(latest):
            if action is GameAction.ACTION6:
                for xy in self._click_candidates(latest, state):
                    result.append((action, token_for(action, xy)))
            else:
                result.append((action, token_for(action)))
        return result

    def _pick(self, latest: FrameData, state: StateView) -> tuple[GameAction, ActionToken]:
        candidates = self._candidate_tokens(latest, state)
        if not candidates:
            return GameAction.RESET, (int(GameAction.RESET.value),)

        tokens = [tok for _, tok in candidates]
        plan = self.model.plan_to_known_progress(state, tokens)
        if plan:
            first = plan[0]
            for action, tok in candidates:
                if tok == first:
                    return action, tok

        scored: list[tuple[float, int, int, GameAction, ActionToken]] = []
        for action, tok in candidates:
            score = self.model.score_action(state, tok)
            complexity = 1 if len(tok) > 1 else 0
            scored.append((score, -complexity, -tok[0], action, tok))
        scored.sort(reverse=True, key=lambda x: (x[0], x[1], x[2]))
        _, _, _, action, tok = scored[0]
        return action, tok

    def choose_action(
        self,
        frames: list[FrameData],
        latest_frame: FrameData,
    ) -> GameAction:
        cur = self._observe(latest_frame)

        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            self.path = []
            self.last_state = None
            self.last_token = None
            action = GameAction.RESET
            action.reasoning = {"policy": "gen1", "why": "start/recover level"}
            return action

        action, tok = self._pick(latest_frame, cur)
        self.last_state = cur
        self.last_token = tok
        self.path.append(tok)

        if action is GameAction.ACTION6 and len(tok) == 3:
            _, x, y = tok
            action.set_data({"x": int(x), "y": int(y)})
            action.reasoning = {
                "policy": "gen1",
                "why": "model-ranked salient click",
                "x": int(x),
                "y": int(y),
            }
        else:
            action.reasoning = {
                "policy": "gen1",
                "why": "known-progress plan or model-ranked first-contact action",
                "model_confidence": round(self.model.confidence(cur, tok), 3),
            }
        return action
