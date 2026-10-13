"""One existing AgentLineage.evaluate; route native evidence by task owner.

No new agent, event journal, executor, or comparison semantics are created.
The owner-scoped task referent and independently captured native transitions
share the same callback and preserve their own evidence/witness contracts.
"""
from __future__ import annotations

from typing import Any

from .observed_evaluator import NativeABEvaluator


class RoutedEvaluator:
    def __init__(self, runtime: Any, primary: Any, native: NativeABEvaluator) -> None:
        actors = getattr(primary, "supported_actors", None)
        if not actors:
            raise ValueError("combined referent registration requires explicit primary actor scope")
        self.runtime = runtime
        self.primary = primary
        self.native = native
        self.primary_actors = frozenset(str(actor).strip().casefold() for actor in actors)
        if not all(self.primary_actors):
            raise ValueError("primary referent actors must be nonblank")

    def _primary_for(self, handoff: Any) -> bool:
        # Ancestor and descendant movements share the original root owner.
        root_id = handoff.metadata.get("lineage_root") or handoff.handoff_id
        root = self.runtime.get(root_id)
        return root.from_actor.strip().casefold() in self.primary_actors

    def has_observation(self, handoff_id: str) -> bool:
        handoff = self.runtime.get(handoff_id)
        if self._primary_for(handoff):
            return True
        return self.native.has_observation(handoff_id)

    def __call__(self, handoff: Any, state: Any) -> Any:
        return (self.primary if self._primary_for(handoff) else self.native)(handoff, state)
