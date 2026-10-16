"""B18: lock-coordinated B10 observed journal for direct B11 native delivery.

This is a purpose-built subclass of the existing append-only event journal.
It uses B16's exact observed-journal sidecar lease and reloads durable
records *while the lock is held* before submission, LOCAL_PASS, or recovery.
It does not alter native source verification, signature checks, native
START/OBSERVED ordering or unresolved-effect recovery semantics.

The generic RuntimeJournal and opt-in ObservedEventJournal remain separate,
uncoordinated contracts: direct RuntimeJournal.append(...) bypasses hooks.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from runtime.handoff import Handoff, HandoffEvent
from runtime.journal import RuntimeJournal
from systems.workspace.b16_delivery_coordination import coordinated_operator_entry
from systems.workspace.observed_event_journal import ObservedEventJournal


class B18CoordinatedObservedJournal(ObservedEventJournal):
    """Single-host cooperative observed-journal lock and durable-snapshot refresh.

    As with B16, the sidecar lock is advisory and may not be deleted or
    replaced. The lock must be acquired by the same thread that runs the
    observed native adapter; never allow a second writer with stale state.
    """

    def __init__(self, path: str | Path, **kwargs):
        self._initializing_b18 = True
        self._b18_path = Path(path)
        try:
            with self.coordinated():
                super().__init__(path, **kwargs)
        finally:
            self._initializing_b18 = False

    @contextmanager
    def coordinated(self) -> Iterator[None]:
        # Reenter the B13/B14 trust+observed lease when present, or take the
        # same observed-journal lock for a direct B11 native caller.
        with coordinated_operator_entry(trust_ledger=self._b18_path):
            yield

    def _reload_locked(self) -> tuple[str, ...]:
        """Reconstruct persisted state under a caller-owned journal lease."""
        if self._processing:
            raise RuntimeError("B18 cannot reload during a running native adapter")
        RuntimeJournal.__init__(self, self.path)
        return ObservedEventJournal.recover_pending(self)

    def refresh(self) -> tuple[str, ...]:
        """Reconcile any previous, not-yet-started native results safely."""
        with self.coordinated():
            return self._reload_locked()

    def recover_pending(self) -> tuple[str, ...]:
        # ObservedEventJournal.__init__ already owns the B18 lease. Avoid
        # reading the journal twice while its own constructor is initializing.
        with self.coordinated():
            if self._initializing_b18:
                return ObservedEventJournal.recover_pending(self)
            return self._reload_locked()

    def append_submission(self, handoff: Handoff, created_event: HandoffEvent) -> HandoffEvent:
        with self.coordinated():
            self._reload_locked()
            return RuntimeJournal.append_submission(self, handoff, created_event)

    def append(self, event: HandoffEvent) -> HandoffEvent:
        with self.coordinated():
            self._reload_locked()
            return ObservedEventJournal.append(self, event)
