"""Read-only ARC native frame provider for the existing A/B evaluator.

Native game movement must happen *outside* evaluation. Captures are scoped to
their referent; the provider does not call game.step or attest who performed it.
A capture is a measurement of the supplied native SDK frames, not proof of
whole-game or task completion.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any

from .observed_evaluator import ObservedTransition


def _flatten(values: Any):
    if hasattr(values, "tolist"):
        values = values.tolist()
    if isinstance(values, (tuple, list)):
        for value in values:
            yield from _flatten(value)
    else:
        yield int(values)


def _native_grid(observation: Any) -> tuple[int, ...]:
    frames = getattr(observation, "frame", None)
    if frames is None or len(frames) == 0:
        raise ValueError("ARC native observation has no frame")
    colors = tuple(_flatten(frames[-1]))
    if len(colors) != 64 * 64 or any(c < 0 or c > 15 for c in colors):
        raise ValueError("ARC native frame must be 64x64 palette values")
    return colors


def _locator(game_id: str, colors: tuple[int, ...]) -> str:
    digest = sha256(bytes(colors)).hexdigest()
    return f"arc://{game_id}/native-frame/sha256:{digest}"


class ARCFrameObservationProvider:
    """Collect completed *native* ARC steps; never execute steps in evaluate.

    A trusted ARC worker supplies before/after GameObservation objects after
    its own step. Merely storing snapshots cannot independently certify the
    action metadata. No public HTTP endpoint admits captures.
    """

    def __init__(self, game_id: str):
        if not game_id or not game_id.strip():
            raise ValueError("ARC game id is required")
        self.game_id = game_id.strip().lower()
        self._captured: dict[str, ObservedTransition] = {}

    def has_capture(self, handoff_id: str) -> bool:
        return handoff_id in self._captured

    def record_native_step(
        self, *, handoff_id: str, referent: str, before: Any, after: Any,
        action: str, x: int, y: int,
        predicted_after: dict[str, Any] | None = None,
    ) -> ObservedTransition:
        if not handoff_id.strip() or not referent.strip() or not action.strip() or not 0 <= x < 64 or not 0 <= y < 64:
            raise ValueError("handoff, referent, native action, and in-bounds cell are required")
        if handoff_id in self._captured:
            raise ValueError("native step already captured for this handoff")
        old = _native_grid(before)
        new = _native_grid(after)
        old_ref, new_ref = _locator(self.game_id, old), _locator(self.game_id, new)
        observation = ObservedTransition(
            referent=referent,
            before={"cell_color": old[y * 64 + x], "levels_completed": int(before.levels_completed)},
            after={"cell_color": new[y * 64 + x], "levels_completed": int(after.levels_completed)},
            predicted_after=predicted_after,
            before_ref=old_ref, after_ref=new_ref,
            source=f"arc-agi-3:{self.game_id}:native-sdk-frames",
            action=action,
            evidence_kind="measurement",
        )
        # Distinct full-frame locators prevent pretending a recycled snapshot moved.
        self._captured[handoff_id] = observation
        return observation

    def __call__(self, handoff, state) -> ObservedTransition | None:
        return self._captured.get(handoff.handoff_id)
