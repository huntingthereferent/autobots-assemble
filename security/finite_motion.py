"""Finite bipolar movement: an observation harness, not a cipher or sandbox.

A probe can continue cycling in a separate bounded view without writing to
protected state. This models movement/noninterference, not malicious intent.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class MotionObservation:
    view: str
    orientation: int
    step: int


class BipolarBoundary:
    """Two independent, finite trajectories with no shared write access."""

    def __init__(self):
        self._protected = 1
        self._probe = -1
        self._protected_steps = 0
        self._probe_steps = 0

    def move(self, *, admitted: bool) -> MotionObservation:
        # Admission must come from an external, authenticated authorization
        # decision. Oscillation alone is not evidence of maliciousness.
        if type(admitted) is not bool:
            raise TypeError("admitted must be a trusted boolean decision")
        if admitted:
            self._protected *= -1
            self._protected_steps += 1
            return MotionObservation("protected", self._protected, self._protected_steps)
        self._probe *= -1
        self._probe_steps += 1
        return MotionObservation("bounded-probe", self._probe, self._probe_steps)

    def protected_snapshot(self) -> tuple[int, int]:
        """Operator-only inspection, not an externally exposed endpoint."""
        return self._protected, self._protected_steps
