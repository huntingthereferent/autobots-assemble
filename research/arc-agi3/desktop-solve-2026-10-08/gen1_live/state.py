"""Generic ARC3 perception for the first-contact solver.

Keeps two simultaneous lenses:
- exact pixels: never loses a timer, one-cell indicator, animation bit, etc.
- object state: compact enough for transition reuse and planning.

No game-specific labels are assigned.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import blake2b
from typing import Iterable

import numpy as np


@dataclass(frozen=True, order=True)
class Component:
    color: int
    size: int
    x0: int
    y0: int
    x1: int
    y1: int

    @property
    def width(self) -> int:
        return self.x1 - self.x0 + 1

    @property
    def height(self) -> int:
        return self.y1 - self.y0 + 1

    @property
    def cx2(self) -> int:
        return self.x0 + self.x1

    @property
    def cy2(self) -> int:
        return self.y0 + self.y1

    @property
    def shape_signature(self) -> tuple[int, int, int, int]:
        return (self.color, self.size, self.width, self.height)

    @property
    def absolute_signature(self) -> tuple[int, int, int, int, int, int]:
        return (self.color, self.size, self.x0, self.y0, self.x1, self.y1)


@dataclass(frozen=True)
class StateView:
    exact_key: bytes
    object_key: tuple[tuple[int, int, int, int, int, int], ...]
    shape_key: tuple[tuple[int, int, int, int], ...]
    components: tuple[Component, ...]
    background: int
    color_counts: tuple[tuple[int, int], ...]


def grid_from_frame_data(frame) -> np.ndarray:
    a = np.asarray(frame.frame)
    if a.ndim == 3:
        a = a[-1]
    return a.reshape(64, 64).astype(np.int8, copy=False)


def exact_key(grid: np.ndarray) -> bytes:
    return blake2b(np.ascontiguousarray(grid).tobytes(), digest_size=16).digest()


def _neighbors(y: int, x: int, h: int, w: int) -> Iterable[tuple[int, int]]:
    if y:
        yield y - 1, x
    if y + 1 < h:
        yield y + 1, x
    if x:
        yield y, x - 1
    if x + 1 < w:
        yield y, x + 1


def components(grid: np.ndarray) -> tuple[Component, ...]:
    g = np.asarray(grid, dtype=np.int16)
    h, w = g.shape
    seen = np.zeros((h, w), dtype=bool)
    raw: list[Component] = []

    for y in range(h):
        for x in range(w):
            if seen[y, x]:
                continue
            color = int(g[y, x])
            stack = [(y, x)]
            seen[y, x] = True
            pts: list[tuple[int, int]] = []
            while stack:
                cy, cx = stack.pop()
                pts.append((cy, cx))
                for ny, nx in _neighbors(cy, cx, h, w):
                    if not seen[ny, nx] and int(g[ny, nx]) == color:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
            ys = [p[0] for p in pts]
            xs = [p[1] for p in pts]
            raw.append(
                Component(
                    color=color,
                    size=len(pts),
                    x0=min(xs),
                    y0=min(ys),
                    x1=max(xs),
                    y1=max(ys),
                )
            )

    if not raw:
        return ()
    dominant_i = max(range(len(raw)), key=lambda i: raw[i].size)
    kept = [c for i, c in enumerate(raw) if i != dominant_i]
    kept.sort(key=lambda c: c.absolute_signature)
    return tuple(kept)


def perceive_grid(grid: np.ndarray) -> StateView:
    g = np.asarray(grid, dtype=np.int16)
    vals, counts = np.unique(g, return_counts=True)
    cc = tuple(sorted((int(v), int(n)) for v, n in zip(vals, counts)))
    bg = max(cc, key=lambda p: p[1])[0] if cc else 0
    comps = components(g)
    return StateView(
        exact_key=exact_key(g),
        object_key=tuple(c.absolute_signature for c in comps),
        shape_key=tuple(sorted(c.shape_signature for c in comps)),
        components=comps,
        background=bg,
        color_counts=cc,
    )


def perceive(frame) -> StateView:
    return perceive_grid(grid_from_frame_data(frame))


DIR_SIGNS = {
    1: (0, -1),
    2: (0, +1),
    3: (-1, 0),
    4: (+1, 0),
}


def infer_directional_translation(
    before: StateView,
    after: StateView,
    action_id: int,
) -> tuple[tuple[int, int, int, int], int, int] | None:
    sign = DIR_SIGNS.get(action_id)
    if sign is None:
        return None

    by_shape_before: dict[tuple[int, int, int, int], list[Component]] = {}
    by_shape_after: dict[tuple[int, int, int, int], list[Component]] = {}
    for c in before.components:
        by_shape_before.setdefault(c.shape_signature, []).append(c)
    for c in after.components:
        by_shape_after.setdefault(c.shape_signature, []).append(c)

    candidates: list[tuple[int, tuple[int, int, int, int], int, int]] = []
    sx, sy = sign
    for sig in set(by_shape_before) & set(by_shape_after):
        for a in by_shape_before[sig]:
            for b in by_shape_after[sig]:
                dx2 = b.cx2 - a.cx2
                dy2 = b.cy2 - a.cy2
                if dx2 == 0 and dy2 == 0:
                    continue
                if sx and (dx2 * sx <= 0 or abs(dy2) > abs(dx2)):
                    continue
                if sy and (dy2 * sy <= 0 or abs(dx2) > abs(dy2)):
                    continue
                candidates.append((abs(dx2) + abs(dy2), sig, dx2, dy2))

    if not candidates:
        return None
    _, sig, dx2, dy2 = min(candidates, key=lambda t: (t[0], t[1]))
    return sig, dx2, dy2
