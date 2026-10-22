"""Verified adapter from the finite A/B journal into workstation observations.

Exact A/B movement identities cross the boundary as witness refs. Trajectory
bindings are persisted as events in the workstation's existing RuntimeJournal,
not in a competing sidecar file. Every verifier call replays the A/B source.
The empty trajectory string is the actual root path in the finite cluster.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runtime.engine import HandoffRuntime
from runtime.handoff import HandoffEvent
from runtime.journal import RuntimeJournal

from .ab_relational_cluster import _strict_object, read_history
from .workstation_continuation import Observation

_PREFIX = "abcluster/v1"
_BINDING_EVENT = "AB_CLUSTER_TRAJECTORY_BOUND"
_LANE_SOURCE = "workstation-continuation-lane/v1"


def _ref(entry_hash: str, movement: dict[str, Any]) -> str:
    return ":".join((_PREFIX, entry_hash, movement["word"],
                     movement["action"], movement["kind"]))


def _journal_rows(path: str | Path) -> list[dict[str, Any]]:
    journal = Path(path)
    if not journal.exists():
        return []
    read_history(journal)
    return [json.loads(line, object_pairs_hook=_strict_object)
            for line in journal.read_text(encoding="utf-8").splitlines()]


def _resolve_ref(journal_path: str | Path, ref: str) -> tuple[dict, dict]:
    parts = ref.split(":")
    if len(parts) != 5 or parts[0] != _PREFIX:
        raise ValueError("unsupported A/B witness reference")
    _, entry_hash, word, action, kind = parts
    for row in _journal_rows(journal_path):
        if row["entry_hash"] != entry_hash:
            continue
        matches = [m for m in row["movements"]
                   if m["word"] == word and m["action"] == action and m["kind"] == kind]
        if len(matches) != 1:
            raise ValueError("witness movement is absent or ambiguous")
        return row, matches[0]
    raise ValueError("witness journal entry is absent")


class ABClusterWitnessVerifier:
    """Workstation verifiers backed by A/B replay and native journal bindings.

    workstation_data_dir must point at the same data directory used by
    WorkstationContinuationHarness. Binding events are replayed on construction,
    so a verifier recreated after restart recovers the exact lane identities.
    """
    def __init__(self, journal_path: str | Path,
                 workstation_data_dir: str | Path | None = None):
        self.journal_path = Path(journal_path)
        self.workstation_data_dir = Path(workstation_data_dir) if workstation_data_dir else None
        self.path_to_lane: dict[str, str] = {}
        self.lane_to_path: dict[str, str] = {}
        if self.workstation_data_dir is not None:
            self._restore_bindings()

    def _runtime(self) -> HandoffRuntime:
        if self.workstation_data_dir is None:
            raise ValueError("workstation data directory required for durable lane binding")
        return HandoffRuntime(event_store=RuntimeJournal(self.workstation_data_dir / "runtime.jsonl"))

    def _restore_bindings(self) -> None:
        runtime = self._runtime()
        for event in runtime.event_store.all():
            if event.event_type != _BINDING_EVENT:
                continue
            handoff = runtime._handoffs.get(event.handoff_id)
            if handoff is None or handoff.metadata.get("source_system") != _LANE_SOURCE:
                raise ValueError("trajectory binding references an unknown workstation lane")
            path = event.data.get("trajectory_path")
            lane_id = handoff.metadata.get("lane_id")
            if not isinstance(path, str) or not isinstance(lane_id, str):
                raise ValueError("malformed persisted trajectory binding")
            self._apply_binding(path, lane_id)

    def _apply_binding(self, path: str, lane_id: str) -> None:
        prior_lane = self.path_to_lane.get(path)
        prior_path = self.lane_to_path.get(lane_id)
        if (prior_lane is not None and prior_lane != lane_id) or (
                prior_path is not None and prior_path != path):
            raise ValueError("trajectory/lane identity binding conflicts")
        self.path_to_lane[path] = lane_id
        self.lane_to_path[lane_id] = path

    def bind_lane(self, path: str, lane_id: str) -> None:
        # path may be "" because the finite cluster represents its root that way.
        if not isinstance(path, str) or not isinstance(lane_id, str) or not lane_id.strip():
            raise ValueError("trajectory path and lane identity are required")
        if self.workstation_data_dir is None:
            raise ValueError("workstation data directory required for durable lane binding")
        runtime = self._runtime()
        # Accept either the durable logical lane_id or the handoff ID returned
        # by tick()/seed_lane(); normalize to the logical identity used by observations.
        matches = [h for h in runtime._handoffs.values()
                   if h.metadata.get("source_system") == _LANE_SOURCE
                   and (h.metadata.get("lane_id") == lane_id or h.handoff_id == lane_id)]
        if len(matches) != 1:
            raise ValueError("bind trajectory only after its workstation lane is seeded")
        handoff = matches[0]
        logical_lane_id = handoff.metadata.get("lane_id")
        if not isinstance(logical_lane_id, str) or not logical_lane_id:
            raise ValueError("workstation lane has no logical identity")
        self._restore_bindings()
        existing = self.path_to_lane.get(path)
        if existing == logical_lane_id:
            return
        if existing is not None or logical_lane_id in self.lane_to_path:
            raise ValueError("trajectory/lane identity binding conflicts")
        state = runtime.state(handoff.handoff_id)
        runtime.event_store.append(HandoffEvent.create(
            handoff_id=handoff.handoff_id,
            event_type=_BINDING_EVENT,
            actor_id="ab-workstation-bridge",
            data={"trajectory_path": path},
            parents=(state.last_event_id,) if state.last_event_id else (),
        ))
        self._apply_binding(path, logical_lane_id)

    def _lane_matches(self, path: str, lane_id: str) -> bool:
        return self.path_to_lane.get(path) == lane_id and self.lane_to_path.get(lane_id) == path

    @staticmethod
    def _trajectory_for(movement: dict[str, Any]) -> str:
        # A branch's resulting word names the child trajectory; a collision's
        # "from" names the trajectory whose attempted edge collided.
        return movement["word"] if movement["kind"] == "BRANCH" else movement["from"]

    def verify_observation(self, observation: Observation) -> bool:
        try:
            _, movement = _resolve_ref(self.journal_path, observation.witness_ref)
        except (ValueError, OSError, KeyError, TypeError):
            return False
        if observation.kind == "BRANCH":
            return (movement["kind"] == "BRANCH"
                    and observation.relation == movement["word"]
                    and self._lane_matches(movement["from"], observation.lane_id))
        if observation.kind == "RELATION":
            if movement["kind"] not in ("BRANCH", "CONNECTION"):
                return False
            return (observation.relation == "state:" + ",".join(map(str, movement["to"]))
                    and self._lane_matches(self._trajectory_for(movement), observation.lane_id))
        return False

    def verify_connection(self, left: Observation, right: Observation) -> bool:
        if left.kind != "RELATION" or right.kind != "RELATION" or left.lane_id == right.lane_id:
            return False
        try:
            _, a = _resolve_ref(self.journal_path, left.witness_ref)
            _, b = _resolve_ref(self.journal_path, right.witness_ref)
        except (ValueError, OSError, KeyError, TypeError):
            return False
        if a["kind"] not in ("BRANCH", "CONNECTION") or b["kind"] not in ("BRANCH", "CONNECTION"):
            return False
        return (a["word"] != b["word"] and a["to"] == b["to"]
                and left.relation == right.relation
                and left.relation == "state:" + ",".join(map(str, a["to"]))
                and self._lane_matches(self._trajectory_for(a), left.lane_id)
                and self._lane_matches(self._trajectory_for(b), right.lane_id))


def movement_ref(entry_hash: str, movement: dict[str, Any]) -> str:
    """Stable witness identity for one independently replayed movement."""
    return _ref(entry_hash, movement)


def replayed_rows(journal_path: str | Path) -> list[dict[str, Any]]:
    """Return rows only after the full append-only history passes independent replay."""
    return _journal_rows(journal_path)
