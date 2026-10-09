"""AR25 -> reflection_orbit_kernel adapter.

This is the only layer that knows AR25's obfuscated engine fields/tags.
"""

from dataclasses import dataclass
from typing import Optional

from reflection_orbit_kernel import Axes, Placement, Point

VERTICAL_AXIS_TAG = "0054kgxrvfihgm"
HORIZONTAL_AXIS_TAG = "0002nuguepuujf"

@dataclass(frozen=True)
class AxisSpec:
    coord: int
    movable: bool
    selection_index: Optional[int]

@dataclass(frozen=True)
class PayloadSpec:
    shape: tuple[Point, ...]
    at: Placement
    selection_index: int

@dataclass(frozen=True)
class ReflectionInstance:
    width: int
    height: int
    target: frozenset[Point]
    vertical: Optional[AxisSpec]
    horizontal: Optional[AxisSpec]
    payloads: tuple[PayloadSpec, ...]

def _shape_cells(sprite) -> tuple[Point, ...]:
    return tuple(
        (dx, dy)
        for dy, row in enumerate(sprite.pixels)
        for dx, value in enumerate(row)
        if int(value) >= 0
    )

def _selection_index(game, sprite) -> Optional[int]:
    try:
        return game.ayyvxqrhnzw.index(sprite)
    except ValueError:
        return None

def extract(game) -> ReflectionInstance:
    vertical_sprite = next(
        (s for s in game.jtkyjqznbnp if VERTICAL_AXIS_TAG in s.tags),
        None,
    )
    horizontal_sprite = next(
        (s for s in game.jtkyjqznbnp if HORIZONTAL_AXIS_TAG in s.tags),
        None,
    )

    vertical = None
    if vertical_sprite is not None:
        idx = _selection_index(game, vertical_sprite)
        vertical = AxisSpec(
            coord=vertical_sprite.x,
            movable=idx is not None,
            selection_index=idx,
        )

    horizontal = None
    if horizontal_sprite is not None:
        idx = _selection_index(game, horizontal_sprite)
        horizontal = AxisSpec(
            coord=horizontal_sprite.y,
            movable=idx is not None,
            selection_index=idx,
        )

    payloads = tuple(
        PayloadSpec(
            shape=_shape_cells(sprite),
            at=Placement(sprite.x, sprite.y),
            selection_index=game.ayyvxqrhnzw.index(sprite),
        )
        for sprite in game.ouurgkpbbjj
    )

    return ReflectionInstance(
        width=game.dqwpuqcubca,
        height=game.height,
        target=frozenset((t.x, t.y) for t in game.fswikrcrdmx),
        vertical=vertical,
        horizontal=horizontal,
        payloads=payloads,
    )

def current_axes(instance: ReflectionInstance) -> Axes:
    return Axes(
        x=None if instance.vertical is None else instance.vertical.coord,
        y=None if instance.horizontal is None else instance.horizontal.coord,
    )
