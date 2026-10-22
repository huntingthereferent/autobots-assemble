"""Verified adapter from the finite A/B journal into workstation observations.

This adapter carries exact journal-entry/movement identities across the boundary.
The A/B journal remains the source of truth; workstation callbacks replay it on
each pass. A coordination lane is not a worker and a collision is not a general
cross-domain proof.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ab_relational_cluster import _strict_object, read_history
from .workstation_continuation import Observation


_PREFIX = "abcluster/v1"


def _ref(entry_hash: str, movement: dict[str, Any]) -> str:
    return ":".join((_PREFIX, entry_hash, movement["word"],
                     movement["action"], movement["kind"]))


def _journal_rows(path: str | Path) -> list[dict[str, Any]]:
    journal = Path(path)
    if not journal.exists():
        return []
    # read_history independently replays every row and fails closed on tampering.
    read_history(journal)
    return [json.loads(line, object_pairs_hook=_strict_object)
            for line in journal.read_text(encoding="utf-8").splitlines()]


def _resolve_ref(journal_path: str | Path, ref: str) -> tuple[dict, dict]:
    parts = ref.split(":")
    if len(parts) != 5 or parts[0] != "abcluster/v1":
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
    """Caller-supplied workstation verifiers grounded in independently replayed A/B rows."""

    def __init__(self, journal_path: str | Path):
        self.journal_path = Path(journal_path)

    def verify_observation(self, observation: Observation) -> bool:
        try:
            _, movement = _resolve_ref(self.journal_path, observation.witness_ref)
        except (ValueError, OSError, KeyError, TypeError):
            return False
        if observation.kind == "BRANCH":
            return movement["kind"] == "BRANCH" and observation.relation == movement["word"]
        if observation.kind == "RELATION":
            return movement["kind"] in ("BRANCH", "CONNECTION") and (
                observation.relation == "state:" + ",".join(map(str, movement["to"]))
            )
        return False

    def verify_connection(self, left: Observation, right: Observation) -> bool:
        if left.kind != "RELATION" or right.kind != "RELATION" or left.lane_id == right.lane_id:
            return False
        try:
            _, a = _resolve_ref(self.journal_path, left.witness_ref)
            _, b = _resolve_ref(self.journal_path, right.witness_ref)
        except (ValueError, OSError, KeyError, TypeError):
            return False
        # Both witnesses must independently describe distinct paths reaching
        # the exact same state. A shared label by itself never authorizes a join.
        return (a["word"] != b["word"] and a["to"] == b["to"]
                and left.relation == right.relation
                and left.relation == "state:" + ",".join(map(str, a["to"]))
                and a["kind"] in ("BRANCH", "CONNECTION")
                and b["kind"] in ("BRANCH", "CONNECTION"))


def movement_ref(entry_hash: str, movement: dict[str, Any]) -> str:
    """Public stable witness identity for one independently replayed movement."""
    return _ref(entry_hash, movement)


def replayed_rows(journal_path: str | Path) -> list[dict[str, Any]]:
    """Return rows only after the full append-only history passes independent replay."""
    return _journal_rows(journal_path)
