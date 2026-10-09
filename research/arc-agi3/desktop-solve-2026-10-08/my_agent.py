"""Generic ARC-AGI-3 first-contact agent.

Drop-in body for the official ARC-AGI-3 Kaggle Starter's agent/my_agent.py.

Design goals:
- no per-game ids or hard-coded public solutions;
- exploit official ACTION1..4 directional priors;
- ground game-specific consequences from frame deltas;
- avoid repeating actions that already no-op in equivalent states;
- prefer progress-producing actions over pure experimentation;
- keep enough transition memory for later planning.

This is an engineering baseline, not a claim of 100% performance.
"""
from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from typing import Any, Hashable

import numpy as np

from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent


DIR_ACTIONS = (
    GameAction.ACTION1,  # official semantic prior: up
    GameAction.ACTION2,  # down
    GameAction.ACTION3,  # left
    GameAction.ACTION4,  # right
)


def _grid(frame: FrameData) -> np.ndarray:
    a = np.asarray(frame.frame)
    if a.ndim == 3:
        a = a[-1]
    return a.reshape(64, 64).astype(np.int8, copy=False)


def _state_key(frame: FrameData) -> bytes:
    """Exact frame key. Safe baseline; later versions can add object-relative abstraction."""
    return _grid(frame).tobytes()


def _delta(prev: FrameData, cur: FrameData) -> tuple[int, tuple[int, int, int, int] | None]:
    a, b = _grid(prev), _grid(cur)
    ys, xs = np.where(a != b)
    n = int(len(xs))
    if n == 0:
        return 0, None
    return n, (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))


def _components(g: np.ndarray) -> list[dict[str, Any]]:
    """4-connected same-color components, excluding large background-like regions."""
    h, w = g.shape
    seen = np.zeros_like(g, dtype=bool)
    out: list[dict[str, Any]] = []
    for y in range(h):
        for x in range(w):
            if seen[y, x]:
                continue
            color = int(g[y, x])
            q = [(y, x)]
            seen[y, x] = True
            pts = []
            while q:
                cy, cx = q.pop()
                pts.append((cy, cx))
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny, nx = cy+dy, cx+dx
                    if 0 <= ny < h and 0 <= nx < w and not seen[ny, nx] and int(g[ny, nx]) == color:
                        seen[ny, nx] = True
                        q.append((ny, nx))
            if len(pts) >= int(0.40 * h * w):
                continue
            ys = [p[0] for p in pts]
            xs = [p[1] for p in pts]
            out.append({
                "color": color,
                "size": len(pts),
                "x0": min(xs), "x1": max(xs),
                "y0": min(ys), "y1": max(ys),
                "cx": sum(xs) / len(xs),
                "cy": sum(ys) / len(ys),
            })
    return out


def _legal(latest: FrameData) -> list[GameAction]:
    vals = set(getattr(latest, "available_actions", []) or [])
    actions = []
    for a in GameAction:
        if a is GameAction.RESET:
            continue
        if not vals or a.value in vals or a in vals:
            actions.append(a)
    return actions


@dataclass
class Transition:
    next_key: bytes
    changed: int
    bbox: tuple[int, int, int, int] | None
    level_delta: int
    terminal: bool


class MyAgent(Agent):
    """Stateful first-contact explorer/planner with no game-specific branches."""

    MAX_ACTIONS = 600

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.transitions: dict[tuple[bytes, int, tuple[int, int] | None], Transition] = {}
        self.tried: defaultdict[bytes, set[tuple[int, tuple[int, int] | None]]] = defaultdict(set)
        self.level_best_path: dict[int, list[tuple[int, tuple[int, int] | None]]] = {}
        self.path: list[tuple[int, tuple[int, int] | None]] = []
        self.last_choice: tuple[int, tuple[int, int] | None] | None = None
        self.last_level = 0
        self.action_effects: defaultdict[int, Counter[str]] = defaultdict(Counter)
        self.recent_keys: deque[bytes] = deque(maxlen=24)

    @property
    def name(self) -> str:
        return f"{super().name}.first-contact"

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN

    def _learn_previous(self, frames: list[FrameData], latest: FrameData) -> None:
        if len(frames) < 2 or self.last_choice is None:
            self.last_level = int(getattr(latest, "levels_completed", 0))
            return

        prev = frames[-2]
        # The official Agent seeds history with a synthetic FrameData(levels_completed=0)
        # whose frame is empty. It is bookkeeping, not an observable 64x64 state.
        if np.asarray(prev.frame).size == 0 or np.asarray(latest.frame).size == 0:
            self.last_level = int(getattr(latest, "levels_completed", self.last_level))
            return
        pk = _state_key(prev)
        ck = _state_key(latest)
        changed, bbox = _delta(prev, latest)
        level = int(getattr(latest, "levels_completed", self.last_level))
        dl = level - self.last_level
        terminal = latest.state in (GameState.WIN, GameState.GAME_OVER)

        aid, data = self.last_choice
        self.transitions[(pk, aid, data)] = Transition(
            next_key=ck,
            changed=changed,
            bbox=bbox,
            level_delta=dl,
            terminal=terminal,
        )
        self.tried[pk].add((aid, data))

        if dl > 0:
            # Bank the path that actually produced progress.
            self.level_best_path[level] = list(self.path)
            # Progress is stronger evidence than novelty.
            self.action_effects[aid]["progress"] += 1
        elif changed == 0:
            self.action_effects[aid]["noop"] += 1
        else:
            self.action_effects[aid]["changed"] += 1

        if latest.state is GameState.GAME_OVER:
            self.action_effects[aid]["death"] += 1

        self.last_level = level

    def _score_simple_action(self, key: bytes, action: GameAction) -> float:
        rec = self.action_effects[action.value]
        score = 0.0
        score += 40.0 * rec["progress"]
        score += 2.0 * rec["changed"]
        score -= 6.0 * rec["noop"]
        score -= 30.0 * rec["death"]

        if (action.value, None) not in self.tried[key]:
            score += 12.0  # local information / novelty
        else:
            tr = self.transitions.get((key, action.value, None))
            if tr is not None and tr.level_delta > 0:
                score += 100.0
            if tr is not None and tr.changed == 0:
                score -= 20.0

        # Official prior: cardinal moves are usually the cheapest safe grounding actions.
        if action in DIR_ACTIONS:
            score += 3.0
        elif action is GameAction.ACTION5:
            score += 1.5
        return score

    def _click_candidates(self, latest: FrameData) -> list[tuple[int, int]]:
        g = _grid(latest)
        comps = _components(g)

        # Human-like click prior: small, rare, spatially distinct components first.
        freq = Counter(int(v) for v in g.ravel())
        ranked = []
        for c in comps:
            if c["size"] > 128:
                continue
            rarity = 1.0 / max(1, freq[c["color"]])
            salience = 10.0 * rarity + 1.0 / max(1, c["size"])
            ranked.append((salience, int(round(c["cx"])), int(round(c["cy"]))))
        ranked.sort(reverse=True)

        seen = set()
        out = []
        for _, x, y in ranked:
            p = (max(0, min(63, x)), max(0, min(63, y)))
            if p not in seen:
                seen.add(p)
                out.append(p)
        return out[:24]

    def _choose(self, latest: FrameData) -> tuple[GameAction, tuple[int, int] | None]:
        key = _state_key(latest)
        legal = _legal(latest)

        # If a known transition from exactly this state already advances a level, use it.
        for action in legal:
            if action.is_complex():
                continue
            tr = self.transitions.get((key, action.value, None))
            if tr is not None and tr.level_delta > 0:
                return action, None

        choices: list[tuple[float, GameAction, tuple[int, int] | None]] = []

        for action in legal:
            if action is GameAction.ACTION6:
                for x, y in self._click_candidates(latest):
                    data = (x, y)
                    score = 0.0
                    if (action.value, data) not in self.tried[key]:
                        score += 10.0
                    tr = self.transitions.get((key, action.value, data))
                    if tr is not None:
                        score += 50.0 * tr.level_delta
                        score += 1.0 if tr.changed else -8.0
                        score -= 20.0 if tr.terminal and tr.level_delta <= 0 else 0.0
                    choices.append((score, action, data))
            else:
                choices.append((self._score_simple_action(key, action), action, None))

        if not choices:
            return GameAction.RESET, None

        choices.sort(key=lambda t: t[0], reverse=True)
        return choices[0][1], choices[0][2]

    def choose_action(self, frames: list[FrameData], latest_frame: FrameData) -> GameAction:
        self._learn_previous(frames, latest_frame)

        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            self.path = []
            self.last_choice = None
            return GameAction.RESET

        key = _state_key(latest_frame)
        self.recent_keys.append(key)

        action, data = self._choose(latest_frame)
        encoded = (action.value, data)
        self.last_choice = encoded
        self.path.append(encoded)

        if action is GameAction.ACTION6 and data is not None:
            x, y = data
            action.set_data({"x": int(x), "y": int(y)})
            action.reasoning = {
                "policy": "first-contact",
                "why": "salient untried click candidate",
                "x": int(x),
                "y": int(y),
            }
        else:
            action.reasoning = {
                "policy": "first-contact",
                "why": "highest supported progress/novelty score",
            }
        return action
