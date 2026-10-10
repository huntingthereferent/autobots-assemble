"""Continuity Engine: explicit, replay-verifiable research handoffs.

Only the existing finite cyclic B-action is admitted by this version.
This layer preserves question identity, scope, and observation ancestry; it
neither invents mathematical laws nor claims automatic cross-area research.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

from work.arc_like_maze.cyclic_action_engine import CyclicActionEngine
from work.arc_like_maze.window_two import WindowProcess

SCHEMA = "continuity_engine.v1"
CYCLIC = "cyclic_action/B"
SCOPE = "B_ONLY_ON_DECLARED_INVARIANT_CARRIER"


def _wire(obj: Any) -> str:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True)


def _hash(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


def _entry(payload: str, parent: str | None) -> dict:
    return {"payload": payload, "sha256": _hash(payload), "previous_sha256": parent}


@dataclass(frozen=True)
class ContinuityRecord:
    """Immutable serialized handoff. Nested mathematical witnesses are replayed."""

    area: str
    question_id: str
    scope: str
    snapshots: tuple[dict, ...]

    @property
    def status(self) -> str:
        return json.loads(self.snapshots[-1]["payload"])["status"]

    @property
    def powers_examined(self) -> int:
        return len(json.loads(self.snapshots[-1]["payload"])["observations"])

    @property
    def witness(self) -> list:
        return json.loads(self.snapshots[-1]["payload"])["B_bijection"]

    @property
    def research_question(self) -> dict:
        return json.loads(self.snapshots[-1]["payload"])["question"]

    def serialize(self) -> str:
        return _wire({"schema": SCHEMA, "area": self.area,
                      "question_id": self.question_id, "scope": self.scope,
                      "snapshots": list(self.snapshots)})


class ContinuityEngine:
    """Evidence-preserving entry/continuation; no autonomous scheduling.

    New areas require separate mathematical adapters with equally strong
    replay contracts. Unsupported areas are rejected, not silently approximated.
    """

    def __init__(self) -> None:
        self._cyclic = CyclicActionEngine()

    @staticmethod
    def supported_areas() -> tuple[str, ...]:
        return (CYCLIC,)

    def start_cyclic(self, source: WindowProcess, target: WindowProcess,
                     carrier: tuple[tuple[int, ...], ...],
                     max_power: int) -> ContinuityRecord:
        result = self._cyclic.start(source, target, carrier, max_power)
        return ContinuityRecord(CYCLIC, result.record["question_id"],
                                SCOPE, (_entry(result.serialize(), None),))

    def verify(self, serialized: str, *,
               expected_question_id: str | None = None) -> ContinuityRecord:
        """Replay *each* recorded checkpoint against its original laws."""
        try:
            raw = json.loads(serialized)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("invalid research handoff") from exc
        if (not isinstance(raw, dict) or
            set(raw) != {"schema", "area", "question_id", "scope", "snapshots"} or
            raw["schema"] != SCHEMA or raw["area"] != CYCLIC or
            raw["scope"] != SCOPE or
            type(raw["question_id"]) is not str or
            (expected_question_id is not None and
             raw["question_id"] != expected_question_id)):
            raise ValueError("unsupported area, schema, scope, or anchored question")
        entries = raw["snapshots"]
        if not isinstance(entries, list) or not entries:
            raise ValueError("empty research history")
        previous_hash = None
        previous_payload = None
        previous_budget = 0
        for entry in entries:
            if (not isinstance(entry, dict) or
                set(entry) != {"payload", "sha256", "previous_sha256"} or
                not isinstance(entry["payload"], str) or
                entry["sha256"] != _hash(entry["payload"]) or
                entry["previous_sha256"] != previous_hash):
                raise ValueError("invalid observation ancestry")
            try:
                observed = json.loads(entry["payload"])
                budget = observed["max_power"]
                if type(budget) is not int or budget < previous_budget:
                    raise ValueError("continuation budget was reversed")
                replayed = self._cyclic.resume(entry["payload"], budget,
                    expected_question_id=raw["question_id"])
            except (KeyError, TypeError, json.JSONDecodeError) as exc:
                raise ValueError("invalid nested mathematical witness") from exc
            if replayed.serialize() != entry["payload"]:
                raise ValueError("saved record disagrees with replay")
            if observed["question"]["relation"] != SCOPE:
                raise ValueError("mathematical question scope changed")
            if previous_payload is not None:
                previous = json.loads(previous_payload)
                old = previous["observations"]
                if observed["question"] != previous["question"] or \
                   observed["observations"][:len(old)] != old or \
                   len(observed["observations"]) < len(old):
                    raise ValueError("saved mathematical ancestry was replaced")
            previous_budget = budget
            previous_payload = entry["payload"]
            previous_hash = entry["sha256"]
        return ContinuityRecord(raw["area"], raw["question_id"],
                                raw["scope"], tuple(entries))

    def resume(self, serialized: str, max_power: int, *,
               expected_question_id: str | None = None) -> ContinuityRecord:
        prior = self.verify(serialized, expected_question_id=expected_question_id)
        earlier = json.loads(prior.snapshots[-1]["payload"])
        if type(max_power) is not int or max_power < earlier["max_power"]:
            raise ValueError("new continuation budget must not decrease")
        result = self._cyclic.resume(prior.snapshots[-1]["payload"], max_power,
                                     expected_question_id=prior.question_id)
        payload = result.serialize()
        if payload == prior.snapshots[-1]["payload"]:
            return prior
        candidate = ContinuityRecord(prior.area, prior.question_id,
                                     prior.scope, prior.snapshots +
                                     (_entry(payload, prior.snapshots[-1]["sha256"]),))
        return self.verify(candidate.serialize(),
                           expected_question_id=prior.question_id)
