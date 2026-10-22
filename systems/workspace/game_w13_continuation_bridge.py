"""W13 native CP evidence as a workstation observation provider.

This adapter accepts only a COMPLETE, freshly replayed GAME-W13-WORLDS job
whose own provenance binds it to the observed workstation lane. It never treats
a READY coordination lane as execution, and it does not infer cross-domain joins.
"""
from __future__ import annotations

from pathlib import Path

from runtime.engine import HandoffRuntime
from runtime.journal import RuntimeJournal
from .game_w13_native import CP_ID
from .game_w13_native_bridge import GameW13NativeBridge, WORKER_ID
from .workstation import ProcessWorkstation
from .workstation_continuation import Observation

CAPABILITY = "game-engine-build"
RELATION = "continue from independently verified WORLD W13 native result"
WITNESS_PREFIX = "w13-native-job:"


class GameW13ContinuationVerifier:
    """Re-open the native runtime and freshly verify exact W13 job evidence."""

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)

    def _runtime(self) -> HandoffRuntime:
        return HandoffRuntime(event_store=RuntimeJournal(self.data_dir / "runtime.jsonl"))

    def verify_observation(self, observation: Observation) -> bool:
        # This is a public verifier callback: reject malformed objects and
        # field types before dereferencing or interpolating untrusted values.
        if not isinstance(observation, Observation):
            return False
        if (not isinstance(observation.lane_id, str)
                or not observation.lane_id
                or len(observation.lane_id) > 80
                or not isinstance(observation.witness_ref, str)
                or observation.kind != "BRANCH"
                or observation.capability != CAPABILITY
                or observation.relation != RELATION
                or not observation.witness_ref.startswith(WITNESS_PREFIX)):
            return False
        job_id = observation.witness_ref[len(WITNESS_PREFIX):]
        if not job_id or len(job_id) > 200:
            return False
        try:
            runtime = self._runtime()
            handoff = runtime.get(job_id)
            meta = handoff.metadata
            state = runtime.state(job_id)
            if (state.status != "COMPLETE"
                    or meta.get("source_system") != "process-workstation"
                    or meta.get("worker_id") != WORKER_ID
                    or meta.get("checkpoint_contract") != CP_ID
                    or f"workspace-lane:{observation.lane_id}" not in handoff.provenance):
                return False
            desk = ProcessWorkstation(self.data_dir / "workstation")
            return GameW13NativeBridge(runtime=runtime, workstation=desk).reverify(job_id)
        except (AttributeError, KeyError, ValueError, TypeError, OSError):
            return False

    def verify_connection(self, left: Observation, right: Observation) -> bool:
        # Two successful runs of the same finite CP are not a join witness.
        return False
