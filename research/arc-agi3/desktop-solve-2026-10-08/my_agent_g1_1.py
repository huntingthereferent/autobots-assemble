"""Solve the Whole Thing â€” direct G1 generic ARC-AGI-3 agent.

Evidence-driven correction after G0.1:
- never repeat the same candidate action from the same exact state;
- infer only a coarse control regime from available actions;
- systematically explore branches;
- use official ACTION7 undo as a backtracking primitive when available;
- treat level-up as the only strong progress witness;
- no game ids, public solutions, or per-game branches.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

import numpy as np

from arcengine import FrameData, GameAction, GameState
from agents.agent import Agent


DIRS = (GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4)
UNDO = GameAction.ACTION7


def grid(frame: FrameData) -> np.ndarray:
    a = np.asarray(frame.frame)
    if a.size == 0:
        return np.empty((0, 0), dtype=np.int8)
    if a.ndim == 3:
        a = a[-1]
    return a.reshape(64, 64).astype(np.int8, copy=False)


def key(frame: FrameData) -> bytes:
    return grid(frame).tobytes()


def action_from_value(value: int) -> GameAction:
    for action in GameAction:
        if action.value == value:
            return action
    raise ValueError(f"Unknown GameAction value: {value}")


def legal(frame: FrameData) -> list[GameAction]:
    vals = set(getattr(frame, "available_actions", []) or [])
    out = []
    for a in GameAction:
        if a is GameAction.RESET:
            continue
        if not vals or a.value in vals or a in vals:
            out.append(a)
    return out


def components(g: np.ndarray) -> list[dict[str, Any]]:
    if g.size == 0:
        return []
    h, w = g.shape
    seen = np.zeros_like(g, dtype=bool)
    out = []
    for y in range(h):
        for x in range(w):
            if seen[y, x]:
                continue
            c = int(g[y, x])
            todo = [(y, x)]
            seen[y, x] = True
            pts = []
            while todo:
                cy, cx = todo.pop()
                pts.append((cy, cx))
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and not seen[ny, nx] and int(g[ny, nx]) == c:
                        seen[ny, nx] = True
                        todo.append((ny, nx))
            ys = [p[0] for p in pts]
            xs = [p[1] for p in pts]
            out.append({
                "color": c,
                "size": len(pts),
                "x0": min(xs), "x1": max(xs),
                "y0": min(ys), "y1": max(ys),
                "cx": sum(xs) / len(xs),
                "cy": sum(ys) / len(ys),
            })
    return out


class MyAgent(Agent):
    MAX_ACTIONS = 600

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.tried: defaultdict[bytes, set[tuple[int, tuple[int, int] | None]]] = defaultdict(set)
        self.edges: dict[tuple[bytes, int, tuple[int, int] | None], dict[str, Any]] = {}
        self.visits: Counter[bytes] = Counter()
        self.action_use: Counter[int] = Counter()
        self.last_choice: tuple[int, tuple[int, int] | None] | None = None
        self.last_level = 0
        self.force_undo = False
        self.known_progress: dict[bytes, tuple[int, tuple[int, int] | None]] = {}
        self.level_epoch = 0
        self.momentum_action: int | None = None
        self.last_changed = False

    @property
    def name(self) -> str:
        return f"{super().name}.solve-whole-g1"

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN

    def regime(self, frame: FrameData) -> str:
        acts = set(legal(frame))
        has_click = GameAction.ACTION6 in acts
        has_dirs = any(a in acts for a in DIRS)
        has_interact = GameAction.ACTION5 in acts
        if has_click and not has_dirs and not has_interact:
            return "click"
        if has_dirs and not has_click:
            return "directional"
        if has_interact and not has_click and not has_dirs:
            return "interaction"
        return "hybrid"

    def click_candidates(self, frame: FrameData) -> list[tuple[int, int]]:
        g = grid(frame)
        comps = components(g)
        if not comps:
            return []
        total = g.size
        freq = Counter(int(v) for v in g.ravel())
        ranked = []
        for c in comps:
            # Ignore only truly background-scale connected regions.
            if c["size"] >= int(0.55 * total):
                continue
            rarity = 1.0 / max(1, freq[c["color"]])
            compact = 1.0 / max(1, c["size"])
            salience = 50.0 * rarity + 4.0 * compact
            pts = [
                (int(round(c["cx"])), int(round(c["cy"]))),
            ]
            # Large controls may have meaningful subregions; add interior corners.
            if c["size"] >= 12:
                pts.extend([
                    (c["x0"], c["y0"]),
                    (c["x1"], c["y0"]),
                    (c["x0"], c["y1"]),
                    (c["x1"], c["y1"]),
                ])
            for x, y in pts:
                ranked.append((salience, max(0,min(63,x)), max(0,min(63,y))))
        ranked.sort(reverse=True)
        seen = set()
        out = []
        for _, x, y in ranked:
            p = (x, y)
            if p not in seen:
                seen.add(p)
                out.append(p)
        return out[:48]

    def candidates(self, frame: FrameData) -> list[tuple[GameAction, tuple[int, int] | None]]:
        acts = legal(frame)
        regime = self.regime(frame)
        out: list[tuple[GameAction, tuple[int, int] | None]] = []

        # Order by coarse control regime only; this is not game-specific.
        if regime == "click":
            if GameAction.ACTION6 in acts:
                out.extend((GameAction.ACTION6, p) for p in self.click_candidates(frame))
        else:
            for a in DIRS:
                if a in acts:
                    out.append((a, None))
            if GameAction.ACTION5 in acts:
                out.append((GameAction.ACTION5, None))
            if GameAction.ACTION6 in acts:
                out.extend((GameAction.ACTION6, p) for p in self.click_candidates(frame))

        # ACTION7 is reserved for deliberate backtracking, never normal exploration.
        return out

    def learn(self, frames: list[FrameData], latest: FrameData) -> None:
        if self.last_choice is None or len(frames) < 2:
            self.last_level = int(getattr(latest, "levels_completed", 0))
            return
        prev = frames[-2]
        pg, cg = grid(prev), grid(latest)
        if pg.size == 0 or cg.size == 0:
            self.last_level = int(getattr(latest, "levels_completed", self.last_level))
            return

        pk, ck = key(prev), key(latest)
        level = int(getattr(latest, "levels_completed", self.last_level))
        dl = level - self.last_level
        changed = pk != ck
        aid, data = self.last_choice

        # Undo is navigation of the search tree, not a candidate mechanic edge.
        if aid != UNDO.value:
            self.tried[pk].add((aid, data))
            self.edges[(pk, aid, data)] = {
                "dst": ck,
                "changed": changed,
                "level_delta": dl,
                "terminal": latest.state in (GameState.GAME_OVER, GameState.WIN),
            }
            self.last_changed = changed
            if dl > 0:
                self.known_progress[pk] = (aid, data)
                self.level_epoch += 1
                self.force_undo = False
                self.momentum_action = None
            elif changed and self.visits[ck] > 0:
                self.force_undo = True
                self.momentum_action = None
            elif changed:
                # Generic persistence prior: if a directional move opened a genuinely
                # new state, continue that direction once before cancelling it out.
                self.force_undo = False
                self.momentum_action = aid if aid in {1, 2, 3, 4} else None
            else:
                self.force_undo = False
                self.momentum_action = None

        self.last_level = level

    def choose(self, frame: FrameData) -> tuple[GameAction, tuple[int, int] | None, str]:
        k = key(frame)
        acts = legal(frame)
        self.visits[k] += 1

        # If exact evidence says this state has a level-up edge, take it.
        if k in self.known_progress:
            aid, data = self.known_progress[k]
            return action_from_value(aid), data, "known exact level-up edge"

        # A cycle was just entered. Undo it before spending more exploration.
        if self.force_undo and UNDO in acts:
            self.force_undo = False
            return UNDO, None, "backtrack from known state cycle"

        cand = self.candidates(frame)

        # Generic editâ†’commit hypothesis: in interfaces exposing click + ACTION5,
        # a click often edits/selects while ACTION5 evaluates/commits the edited state.
        if (
            self.last_choice is not None
            and self.last_choice[0] == GameAction.ACTION6.value
            and self.last_changed
            and GameAction.ACTION5 in acts
            and (GameAction.ACTION5.value, None) not in self.tried[k]
        ):
            return GameAction.ACTION5, None, "test commit after visible edit"

        # Directional persistence: do not immediately cancel a move that reached
        # a genuinely new state. Try the same direction once more if it is untried.
        if self.momentum_action is not None:
            ma = action_from_value(self.momentum_action)
            if ma in acts and (ma.value, None) not in self.tried[k]:
                return ma, None, "continue productive directional displacement"

        untried = [(a,d) for a,d in cand if (a.value,d) not in self.tried[k]]

        if untried:
            # Prefer globally less-used action types; then actions whose learned edges
            # have changed frames before. This prevents G0.1's one-action fixation.
            def score(item):
                a, d = item
                global_cost = self.action_use[a.value]
                prior_changed = sum(
                    1 for (sk, aid, dat), e in self.edges.items()
                    if aid == a.value and e["changed"] and not e["terminal"]
                )
                type_bonus = 2 if a in DIRS else (1 if a is GameAction.ACTION5 else 0)
                return (-global_cost, prior_changed, type_bonus)
            untried.sort(key=score, reverse=True)
            a, d = untried[0]
            return a, d, f"untried branch in {self.regime(frame)} regime"

        # Exact state exhausted: use official undo if available.
        if UNDO in acts:
            return UNDO, None, "state exhausted; DFS backtrack"

        # No undo. Choose least-used candidate whose known edge is not terminal/no-op.
        viable = []
        for a, d in cand:
            e = self.edges.get((k, a.value, d))
            penalty = 0
            if e is not None:
                if e["terminal"] and e["level_delta"] <= 0:
                    penalty += 1000
                if not e["changed"]:
                    penalty += 100
                penalty += 10 * self.visits[e["dst"]]
            viable.append((penalty + self.action_use[a.value], a, d))
        if viable:
            viable.sort(key=lambda x: x[0])
            _, a, d = viable[0]
            return a, d, "no untried branch; least-cost continuation"

        return GameAction.RESET, None, "no viable candidates"

    def choose_action(self, frames: list[FrameData], latest_frame: FrameData) -> GameAction:
        self.learn(frames, latest_frame)

        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            self.last_choice = None
            self.force_undo = False
            return GameAction.RESET

        action, data, why = self.choose(latest_frame)
        self.last_choice = (action.value, data)
        self.action_use[action.value] += 1

        if action is GameAction.ACTION6 and data is not None:
            x, y = data
            action.set_data({"x": int(x), "y": int(y)})
            action.reasoning = {
                "policy": "solve-whole-g1",
                "regime": self.regime(latest_frame),
                "why": why,
                "x": int(x),
                "y": int(y),
            }
        else:
            action.reasoning = {
                "policy": "solve-whole-g1",
                "regime": self.regime(latest_frame),
                "why": why,
            }
        return action
