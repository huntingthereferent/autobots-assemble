"""A/B bipolar movement at the *approach to key use*, not inside the keys.

This is an operator-observable finite noninterference harness. It has no
credential/key parameters, derives no key material, and never determines
authorization. Established signature, pinned-actor and native witness rules
still make the decision; no oscillation is asserted to be a cipher.
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import Event, RLock, Thread
from time import monotonic_ns

from .finite_motion import BipolarBoundary, MotionObservation


@dataclass(frozen=True)
class KeyApproachSnapshot:
    """No private keys, key digests, submitted data or identities."""
    protected_orientation: int
    protected_movements: int
    approach_movements: int
    admitted_movements: int
    presence_orientation: int
    presence_movements: int


class KeyApproachBoundary:
    """Finite approach/protected trajectories; only trusted native success
    advances the protected trajectory.

    The two trajectories are independent. An external approach never chooses
    admission by providing a boolean; the native ingress invokes `admitted`
    only *after* verifying and durably recording a movement.
    """

    def __init__(self):
        self._motion = BipolarBoundary()
        # Presence is a third, separately owned finite relationship; a clock
        # must never be confused with durable native handoff evidence.
        self._presence = BipolarBoundary()
        self._lock = RLock()
        self._approaches = 0
        self._admissions = 0
        self._presence_movements = 0

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

    def _presence_tick(self) -> MotionObservation:
        """Local trusted driver movement; not an authorization event."""
        with self._lock:
            self._presence_movements += 1
            return self._presence.move(admitted=True)

    def snapshot(self) -> KeyApproachSnapshot:
        """Privileged local observation; never serialize in HTTP receipts."""
        with self._lock:
            orientation, steps = self._motion.protected_snapshot()
            presence_orientation, presence_steps = self._presence.protected_snapshot()
            return KeyApproachSnapshot(
                protected_orientation=orientation,
                protected_movements=steps,
                approach_movements=self._approaches,
                admitted_movements=self._admissions,
                presence_orientation=presence_orientation,
                presence_movements=presence_steps,
            )


class NativePresenceRunner:
    """Explicit host-owned, monotonic-clock bipolar presence driver.

    A real native thread advances the bounded presence trajectory even when
    there are no incoming requests. It never handles secrets, admits work,
    starts workers, or makes crypto decisions. Construction is inert;
    start()/stop() are trusted-local lifecycle operations, not HTTP actions.
    """

    def __init__(self, boundary: KeyApproachBoundary, *, interval_seconds: float = 0.02):
        if not isinstance(boundary, KeyApproachBoundary):
            raise TypeError("native key approach boundary required")
        if (type(interval_seconds) not in (int, float)
                or not 0.005 <= interval_seconds <= 10):
            raise ValueError("finite 5ms–10s observation interval required")
        self.boundary = boundary
        self.interval_seconds = float(interval_seconds)
        self._stop = Event()
        self._lock = RLock()
        self._thread: Thread | None = None
        self._last_tick_ns = 0
        self._error: BaseException | None = None

    def _run(self) -> None:
        try:
            interval_ns = int(self.interval_seconds * 1_000_000_000)
            next_due = monotonic_ns() + interval_ns
            while not self._stop.is_set():
                delay_ns = next_due - monotonic_ns()
                if delay_ns > 0 and self._stop.wait(delay_ns / 1_000_000_000):
                    break
                if self._stop.is_set():
                    break
                self.boundary._presence_tick()
                self._last_tick_ns = monotonic_ns()
                # No catch-up burst after pause: avoid synthesizing motion
                # for intervals during which the driver was not running.
                next_due = self._last_tick_ns + interval_ns
        except BaseException as exc:
            self._error = exc
            self._stop.set()

    def start(self) -> None:
        with self._lock:
            if self._thread is not None:
                raise RuntimeError("presence driver already started; explicit stop required")
            self._stop.clear()
            self._error = None
            self._thread = Thread(target=self._run, name="ab-key-presence", daemon=True)
            self._thread.start()

    def stop(self, *, timeout: float = 3.0) -> None:
        with self._lock:
            self._stop.set()
            thread = self._thread
            if thread is None:
                return
            thread.join(timeout=timeout)
            if thread.is_alive():
                raise RuntimeError("presence driver did not stop")
            self._thread = None
            if self._error is not None:
                raise RuntimeError("presence driver failed") from self._error

    @property
    def running(self) -> bool:
        with self._lock:
            return (self._thread is not None and self._thread.is_alive()
                    and not self._stop.is_set() and self._error is None)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.stop()
