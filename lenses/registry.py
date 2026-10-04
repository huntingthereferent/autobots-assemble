from __future__ import annotations

from collections.abc import Callable

from network import Snapshot
from .raw import render_raw
from .json_view import render_json
from .english import render_english

Lens = Callable[[Snapshot], str]

_LENSES: dict[str, Lens] = {
    "raw": render_raw,
    "json": render_json,
    "english": render_english,
}


def available_lenses() -> tuple[str, ...]:
    return tuple(sorted(_LENSES))


def render(snapshot: Snapshot, lens: str = "raw") -> str:
    try:
        fn = _LENSES[lens]
    except KeyError as exc:
        raise KeyError(f"unknown lens {lens!r}; choose from {available_lenses()}") from exc
    return fn(snapshot)
