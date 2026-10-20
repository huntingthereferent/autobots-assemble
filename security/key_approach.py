"""A/B bipolar movement at the *approach to key use*, not inside the keys.

This is an operator-observable finite noninterference harness. It has no
credential/key parameters, derives no key material, and never determines
authorization. Established signature, pinned-actor and native witness rules
still make the decision; no oscillation is asserted to be a cipher.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import RLock

from .finite_motion import BipolarBoundary, MotionObservation


@dataclass(frozen=True)
class KeyApproachSnapshot:
    """No private keys, key digests, submitted data or identities."""
    protected_orientation: int
    protected_movements: int
    approach_movements: int
    admitted_movements: int


class KeyApproachBoundary:
    """Finite approach/protected trajectories; only trusted native success
    advances the protected trajectory.

    The two trajectories are independent. An external approach never chooses
    admission by providing a boolean; the native ingress invokes `admitted`
    only *after* verifying and durably recording a movement.
    """

    def __init__(self):
        self._motion = BipolarBoundary()
        self._lock = RLock()
        self._approaches = 0
        self._admissions = 0

    def approach(self) -> MotionObservation:
        """Record bounded approach without changing the protected movement."""
        with self._lock:
            self._approaches += 1
            return self._motion.move(admitted=False)

    def admitted(self) -> MotionObservation:
        """Invoked by trusted code only after actual native commit succeeds."""
        with self._lock:
            self._admissions += 1
            return self._motion.move(admitted=True)

    def snapshot(self) -> KeyApproachSnapshot:
        """Privileged local observation; never serialize in HTTP receipts."""
        with self._lock:
            orientation, steps = self._motion.protected_snapshot()
            return KeyApproachSnapshot(
                protected_orientation=orientation,
                protected_movements=steps,
                approach_movements=self._approaches,
                admitted_movements=self._admissions,
            )
