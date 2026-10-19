"""Pinned workflow revisions and bounded quality discoveries.

Pins are review selections, not workflow executions. A machine-observed quality
claim remains unverified unless a source-native verifier is explicitly supplied.
Historical pin events are append-only, chained, revision-specific and never
silently replaced by newer branches. No telemetry or network collection.
"""
from __future__ import annotations

from hashlib import sha256
import json
import math
import os
from pathlib import Path
from typing import Callable, Any

from .workflow_draft import build_preview

SCHEMA = "workstation-workflow-pin/v1"
_MAX_EVENTS = 20000
_MAX_BYTES = 20_000_000


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def _digest(value: object) -> str:
    return sha256(_canonical(value)).hexdigest()


def _text(value: object, label: str, length: int = 240) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > length:
        raise ValueError(f"{label} must be bounded nonempty text")
    return value.strip()


class WorkflowPins:
    """Append-only, single-writer local pinned-branch history."""

    def __init__(self, data_dir: str | Path):
        self.path = Path(data_dir) / "workflow_pins.jsonl"

    def _read(self) -> list[dict]:
        if not self.path.exists():
            return []
        if not self.path.is_file() or self.path.stat().st_size > _MAX_BYTES:
            raise ValueError("pin ledger exceeds bounded regular-file budget")
        events = []
        prev = ""
        for number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if number > _MAX_EVENTS or not line.strip():
                raise ValueError("pin ledger invalid length or empty row")
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError("pin ledger malformed JSON") from exc
            if not isinstance(item, dict) or set(item) != {"data", "parent", "hash"}:
                raise ValueError("pin ledger invalid envelope")
            if item["parent"] != prev or not isinstance(item["data"], dict):
                raise ValueError("pin ledger ancestry mismatch")
            if _digest({"parent": prev, "data": item["data"]}) != item["hash"]:
                raise ValueError("pin ledger content mismatch")
            data = item["data"]
            if (data.get("schema") != SCHEMA or
                    data.get("kind") not in {"PIN", "DISCOVERED_PIN"} or
                    data.get("status") not in {"CANDIDATE", "QUALITY_OBSERVATION_VERIFIED"} or
                    not isinstance(data.get("revision"), str) or
                    len(data["revision"]) != 64 or
                    not isinstance(data.get("draft"), dict) or
                    data.get("revision") != _digest(data["draft"])):
                raise ValueError("pin ledger unrecognized record or source revision")
            events.append(item)
            prev = item["hash"]
        return events

    def _append(self, data: dict) -> dict:
        events = self._read()
        if len(events) >= _MAX_EVENTS:
            raise ValueError("pin ledger event budget exceeded")
        for row in events:
            prev = row["data"]
            if prev["revision"] == data["revision"]:
                if prev == data:
                    return dict(row["data"])
                raise ValueError("this exact revision is already pinned; do not overwrite its evidence")
        parent = events[-1]["hash"] if events else ""
        entry = {"parent": parent, "data": data,
                 "hash": _digest({"parent": parent, "data": data})}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(_canonical(entry).decode("utf-8") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return dict(data)

    def list_pins(self) -> list[dict]:
        return [dict(e["data"]) for e in self._read()]

    def compare_branch(self, spec: dict, repo_root: str | Path) -> dict:
        """Diff a candidate against its pinned ancestor without executing it."""
        preview = build_preview(spec, repo_root)
        current = preview["draft"]
        parent = current["parent_revision"]
        if not parent:
            raise ValueError("branch comparison requires a pinned parent revision")
        historical = next((row for row in self.list_pins() if row["revision"] == parent), None)
        if historical is None:
            raise ValueError("pinned parent revision unavailable")
        before = historical["draft"]
        old_nodes = {s["id"]: s for s in before["steps"]}
        new_nodes = {s["id"]: s for s in current["steps"]}
        old_edges = {_canonical(x).decode("utf-8") for x in before["links"]}
        new_edges = {_canonical(x).decode("utf-8") for x in current["links"]}
        changed = sorted(s for s in old_nodes.keys() & new_nodes.keys()
                         if old_nodes[s] != new_nodes[s])
        return {
            "parent_revision": parent,
            "branch_revision": preview["revision"],
            "added_steps": sorted(new_nodes.keys() - old_nodes.keys()),
            "removed_steps": sorted(old_nodes.keys() - new_nodes.keys()),
            "changed_steps": changed,
            "added_links": [json.loads(x) for x in sorted(new_edges - old_edges)],
            "removed_links": [json.loads(x) for x in sorted(old_edges - new_edges)],
            "unresolved_inputs": preview["unresolved_inputs"],
            "ambiguous_links": preview["ambiguous_links"],
            "graph_validated_only": True,
            "execution_authorized": False,
            "native_verified": False,
        }

    def pin_candidate(self, spec: dict, repo_root: str | Path, *, reason: str) -> dict:
        preview = build_preview(spec, repo_root)
        revision = preview["revision"]
        data = {"schema": SCHEMA, "kind": "PIN", "status": "CANDIDATE",
                "revision": revision, "parent_revision": preview["draft"]["parent_revision"],
                "draft": preview["draft"], "reason": _text(reason, "pin reason"),
                "assessment": None, "native_verification": False,
                "whole_workflow_verified": False, "execution_authorized": False}
        return self._append(data)

    def consider_discovery(
        self, spec: dict, repo_root: str | Path, *, assessment: dict,
        verify_observation: Callable[[dict, dict], bool] | None = None,
    ) -> dict:
        """Automatically PIN only when evidence proposes a comparable improvement.

        Assessment is a bounded source-scoped metric comparison. The callback
        rechecks the SAME assessment against its original source. Even if it
        passes, the status certifies the observed metric only; never a complete
        workflow, native job, or execution authorization.
        """
        preview = build_preview(spec, repo_root)
        draft = preview["draft"]
        parent = draft["parent_revision"]
        if not parent or not any(x["revision"] == parent for x in self.list_pins()):
            raise ValueError("discovery requires a previously pinned parent revision")
        if not isinstance(assessment, dict) or set(assessment) != {
            "metric", "parent_value", "branch_value", "direction",
            "comparison_scope", "source_ref", "witness_ref",
        }:
            raise ValueError("discovery assessment must include scoped metric and source evidence")
        metric = _text(assessment["metric"], "metric")
        scope = _text(assessment["comparison_scope"], "comparison scope")
        source = _text(assessment["source_ref"], "source reference", 400)
        witness = _text(assessment["witness_ref"], "witness reference", 400)
        direction = assessment["direction"]
        if direction not in ("HIGHER", "LOWER"):
            raise ValueError("comparison direction must be HIGHER or LOWER")
        a, b = assessment["parent_value"], assessment["branch_value"]
        if (type(a) not in (int, float) or type(b) not in (int, float) or
                not math.isfinite(a) or not math.isfinite(b)):
            raise ValueError("comparison values must be finite numbers")
        better = (b > a if direction == "HIGHER" else b < a)
        if not better:
            return {"pinned": False, "reason": "NO_MEASURED_IMPROVEMENT",
                    "revision": preview["revision"]}
        observation = {"metric": metric, "comparison_scope": scope, "source_ref": source,
                       "witness_ref": witness, "parent_value": a, "branch_value": b,
                       "direction": direction}
        checked = False
        if verify_observation is not None:
            # Fail closed: the caller must supply an independent source-native
            # observer. A reported hash alone is not verification.
            if verify_observation(preview, observation) is not True:
                raise ValueError("independent observation verification failed")
            checked = True
        data = {"schema": SCHEMA, "kind": "DISCOVERED_PIN",
                "status": "QUALITY_OBSERVATION_VERIFIED" if checked else "CANDIDATE",
                "revision": preview["revision"], "parent_revision": parent,
                "draft": draft, "reason": "Comparable observed improvement in " + metric,
                "assessment": observation, "native_verification": checked,
                "whole_workflow_verified": False, "execution_authorized": False}
        saved = self._append(data)
        return {"pinned": True, **saved}
