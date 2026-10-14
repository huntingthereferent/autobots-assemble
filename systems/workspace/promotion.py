"""Compare source editions and explicitly prefer a *verified-for-one-job* version.

Preference is a local append-only selection, not a merge, deployment,
new witness, scheduler, or upgrade of the original research.
"""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from uuid import uuid4
from .workstation import ProcessWorkstation, _safe_id, _tree_fingerprint

_HASH = re.compile(r"[a-f0-9]{64}\Z")
_FIELDS = {"schema_version", "event_id", "previous_event_id", "occurred_at",
           "worker_id", "version_id", "source_fingerprint", "supporting_job_id",
           "required_relation", "native_verifier", "actor_id", "evidence_scope"}


def compare_editions(desk: ProcessWorkstation, *, worker_id: str,
                     left_version: str, right_version: str) -> dict:
    """Compare CURRENT source inventories, not inherited baseline test reports."""
    _safe_id(worker_id)
    if left_version == right_version:
        raise ValueError("select two different editions for comparison")
    left, la = desk._read(worker_id, left_version)
    right, ra = desk._read(worker_id, right_version)
    a, b = desk._inventory_edition(left), desk._inventory_edition(right)
    return {
        "worker_id": worker_id,
        "left_version": left_version, "right_version": right_version,
        "left_parent": la["parent_version"], "right_parent": ra["parent_version"],
        "left_fingerprint": _tree_fingerprint(a), "right_fingerprint": _tree_fingerprint(b),
        "modified": sorted(p for p in a.keys() & b.keys() if a[p] != b[p]),
        "only_left": sorted(a.keys() - b.keys()),
        "only_right": sorted(b.keys() - a.keys()),
        "unchanged_count": sum(a[k] == b[k] for k in a.keys() & b.keys()),
        "same_contents": a == b,
        "tests_transferred": False, "evidence_transferred": False,
    }


class PreferredEditions:
    """Private append-only selection ledger. No automatic job admission."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def history(self) -> list[dict]:
        if not self.path.exists():
            return []
        events, seen, latest = [], set(), {}
        for line_number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                raise ValueError(f"blank preferred edition record at line {line_number}")
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError("invalid preferred-edition journal") from exc
            if not isinstance(item, dict) or set(item) != _FIELDS or item["schema_version"] != 1:
                raise ValueError("invalid preferred-edition record structure")
            for key in ("event_id", "worker_id", "version_id", "supporting_job_id", "actor_id"):
                _safe_id(item[key])
            if not isinstance(item["required_relation"], str) or not item["required_relation"].strip():
                raise ValueError("preferred edition missing relation")
            if not isinstance(item["native_verifier"], str) or not item["native_verifier"].strip():
                raise ValueError("preferred edition missing verifier")
            if item["evidence_scope"] != "one-native-reverified-job":
                raise ValueError("unrecognized preference evidence scope")
            if not isinstance(item["source_fingerprint"], str) or not _HASH.fullmatch(item["source_fingerprint"]):
                raise ValueError("invalid preferred edition fingerprint")
            if not isinstance(item["occurred_at"], str) or not item["occurred_at"].strip():
                raise ValueError("missing preference timestamp")
            if item["event_id"] in seen or item["previous_event_id"] != latest.get(item["worker_id"]):
                raise ValueError("preferred edition history has invalid ancestry")
            seen.add(item["event_id"])
            latest[item["worker_id"]] = item["event_id"]
            events.append(item)
        return events

    def current(self) -> dict[str, dict]:
        result = {}
        for row in self.history():
            result[row["worker_id"]] = row
        return result

    def select(self, *, worker_id: str, version_id: str, source_fingerprint: str,
               supporting_job_id: str, required_relation: str, native_verifier: str,
               actor_id: str) -> dict:
        """Append a local preference after caller has performed native revalidation."""
        for name in (worker_id, version_id, supporting_job_id, actor_id):
            _safe_id(name)
        if not isinstance(source_fingerprint, str) or not _HASH.fullmatch(source_fingerprint):
            raise ValueError("invalid selected fingerprint")
        if not required_relation.strip() or not native_verifier.strip():
            raise ValueError("selection needs bounded native capability")
        previous = self.current().get(worker_id)
        if previous and all(previous[k] == v for k, v in {
            "version_id": version_id, "source_fingerprint": source_fingerprint,
            "supporting_job_id": supporting_job_id}.items()):
            return {**previous, "already_selected": True}
        record = {"schema_version": 1, "event_id": uuid4().hex,
                  "previous_event_id": previous["event_id"] if previous else None,
                  "occurred_at": datetime.now(timezone.utc).isoformat(),
                  "worker_id": worker_id, "version_id": version_id,
                  "source_fingerprint": source_fingerprint,
                  "supporting_job_id": supporting_job_id,
                  "required_relation": required_relation,
                  "native_verifier": native_verifier,
                  "actor_id": actor_id,
                  "evidence_scope": "one-native-reverified-job"}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return {**record, "already_selected": False}


def preference_view(store: PreferredEditions, desk: ProcessWorkstation) -> list[dict]:
    """Read only: stale selections stay visible, never silently fall back."""
    items = []
    for worker_id, row in sorted(store.current().items()):
        try:
            info = desk.inspect(worker_id=worker_id, version_id=row["version_id"])
            source_state = ("MATCHES_SELECTION" if info["current_fingerprint"] == row["source_fingerprint"]
                            else "SOURCE_CHANGED")
        except (OSError, KeyError, ValueError, TypeError):
            source_state = "EDITION_UNAVAILABLE"
        items.append({"worker_id": worker_id, "version_id": row["version_id"],
                      "source_fingerprint": row["source_fingerprint"],
                      "supporting_job_id": row["supporting_job_id"],
                      "required_relation": row["required_relation"],
                      "evidence_scope": row["evidence_scope"],
                      "source_state": source_state, "selected_at": row["occurred_at"]})
    return items
