"""Source-scoped A/B observations for the existing editable Workflow Workstation.

This bridge calls the actual installable A/B tool, not a new inverse-math bot.
All links are to existing worker source observations. The read-only projection
must not become an execution, native result, quality claim, or new pin.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re

from runtime.ab_tool_worker import ABToolWorkerBridge
from .workflow_draft import build_preview
from .workflow_pins import WorkflowPins

SCHEMA = "workstation-ab-workflow-source/v1"
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
MAX_LEDGER_BYTES = 8_000_000
MAX_ENTRIES = 4000


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      allow_nan=False, ensure_ascii=False).encode("utf-8")


def digest(value):
    return sha256(canonical(value)).hexdigest()


class ABWorkflowSourceError(ValueError):
    pass


class ABWorkflowSources:
    def __init__(self, repository: str | Path, data_dir: str | Path):
        self.repository = Path(repository).resolve()
        self.data_dir = Path(data_dir).resolve()
        self.path = self.data_dir / "workflow_ab_source_links.jsonl"

    def recorded_native_pool_sources(self) -> dict:
        """Read the original locally journaled bot records; no synthetic tasks.

        A locally saved agent event is useful lineage, not authenticated actor
        identity. Exact source bytes are rechecked before exposing any record.
        """
        from runtime.journal import RuntimeJournal
        path = self.data_dir / "runtime.jsonl"
        if not path.exists():
            return {"source_records": [], "source_events": [],
                    "journal_present": False, "actor_identity_authenticated": False}
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_LEDGER_BYTES:
            raise ABWorkflowSourceError("native runtime journal missing or unsafe")
        store = RuntimeJournal(path)
        seen: dict[str, dict] = {}
        events = []
        for root in store.handoffs():
            if (root.from_actor != "continuity-agent-pool"
                    or root.metadata.get("birth_reason") != "continuity_pool_task_seed"
                    or root.metadata.get("agent_lineage") is not True):
                continue
            if not isinstance(root.inputs.get("task_handoffs"), list):
                continue
            for event in store.for_handoff(root.handoff_id):
                if event.event_type != "AGENT_AB_OBSERVED" or event.actor_id != "agent-ab":
                    continue
                output = event.data.get("output") or {}
                if output.get("task_results") != "NOT_EXECUTED":
                    continue
                native = output.get("task_source_relations")
                if not isinstance(native, list) or not 1 <= len(native) <= 32:
                    continue
                for entry in native:
                    if not isinstance(entry, dict) or not isinstance(entry.get("task_id"), str):
                        raise ABWorkflowSourceError("native worker event contains malformed task ID")
                    record = {"task_id": entry["task_id"],
                              "native_sources": entry.get("native_sources")}
                    prior = seen.get(record["task_id"])
                    if prior is not None and prior != record:
                        raise ABWorkflowSourceError("conflicting native task source histories")
                    seen[record["task_id"]] = record
                events.append(event.event_id)
        rows = [seen[k] for k in sorted(seen)]
        if rows:
            ABToolWorkerBridge(self.repository).inspect_task_sources(rows)
        return {"source_records": rows, "source_events": events,
                "journal_present": True, "actor_identity_authenticated": False,
                "native_result_verified": False, "source_bytes_rechecked": bool(rows)}

    def inspect(self, draft: dict, task_source_records: list[dict],
                step_bindings: dict[str, str]) -> dict:
        """Observe already recorded source relationships; never infer a task result."""
        preview = build_preview(draft, self.repository)
        if not isinstance(step_bindings, dict) or not step_bindings:
            raise ABWorkflowSourceError("explicit step-to-native-task bindings required")
        steps = {s["id"] for s in preview["draft"]["steps"]}
        if not set(step_bindings) <= steps or any(
            not isinstance(v, str) or not v.strip() or len(v) > 160
            for v in step_bindings.values()
        ):
            raise ABWorkflowSourceError("step bindings must reference known steps and bounded native tasks")
        # The packaged A/B tool reopens and hashes each original source file,
        # preserving shared source nodes and independently unresolved walls.
        observed = ABToolWorkerBridge(self.repository).inspect_task_sources(task_source_records)
        available = set(observed["task_ids"])
        if not set(step_bindings.values()) <= available:
            raise ABWorkflowSourceError("step binding refers to native task absent from source observations")
        sources_by_task: dict[str, list[str]] = {x: [] for x in available}
        for row in task_source_records:
            for source in row["native_sources"]:
                sources_by_task[row["task_id"]].append(
                    "repository:" + source["source"] + "@sha256:" + source["sha256"])
        mapped = [
            {"step_id": step_id, "native_task_id": step_bindings[step_id],
             "source_references": sorted(sources_by_task[step_bindings[step_id]])}
            for step_id in sorted(step_bindings)
        ]
        unbound = sorted(steps - set(step_bindings))
        record = {
            "schema": SCHEMA,
            "draft_revision": preview["revision"],
            "step_bindings": mapped,
            "unbound_steps": unbound,
            "source_references": observed["source_references"],
            "ab_capability": observed["capability"],
            "ab_graph_sha256": digest(observed["graph"]),
            "ab_graph_summary": observed["graph_summary"],
            "relation_scope": "SOURCE_REFERENCES_ONLY",
            "input_origin": "CALLER_SUPPLIED_SOURCE_RECORDS",
            "native_actor_identity_authenticated": False,
            "source_bytes_rechecked": True,
            "native_worker_executed": False,
            "native_result_verified": False,
            "branch_quality_verified": False,
            "execution_authorized": False,
        }
        return {"record": record, "ab_graph": observed["graph"],
                "unresolved_steps": unbound, "draft": preview["draft"]}

    def _replay(self) -> list[dict]:
        if not self.path.exists():
            return []
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_size > MAX_LEDGER_BYTES:
            raise ABWorkflowSourceError("unsafe or overlarge A/B source-link journal")
        results = []
        previous = ""
        for number, line in enumerate(self.path.read_text(encoding="utf-8").splitlines(), 1):
            if number > MAX_ENTRIES or not line:
                raise ABWorkflowSourceError("malformed A/B source-link history")
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ABWorkflowSourceError("malformed source-link JSON") from exc
            if not isinstance(row, dict) or set(row) != {"data", "parent", "hash"}:
                raise ABWorkflowSourceError("source-link journal envelope invalid")
            if row["parent"] != previous or digest({"parent": previous, "data": row["data"]}) != row["hash"]:
                raise ABWorkflowSourceError("source-link journal ancestry or content changed")
            data = row["data"]
            if not isinstance(data, dict) or data.get("schema") != SCHEMA or not _DIGEST.fullmatch(str(data.get("draft_revision", ""))):
                raise ABWorkflowSourceError("unrecognized source-link journal entry")
            if (data.get("native_result_verified") is not False
                    or data.get("branch_quality_verified") is not False
                    or data.get("execution_authorized") is not False):
                raise ABWorkflowSourceError("source-link journal cannot record claimed execution or quality")
            results.append(data)
            previous = row["hash"]
        return results

    def list_records(self, revision: str | None = None) -> list[dict]:
        if revision is not None and (not isinstance(revision, str) or not _DIGEST.fullmatch(revision)):
            raise ABWorkflowSourceError("revision must be an exact SHA-256")
        return [x for x in self._replay() if revision is None or x["draft_revision"] == revision]

    def record_for_pinned_branch(self, draft: dict, task_source_records: list[dict],
                                 step_bindings: dict[str, str]) -> dict:
        observation = self.inspect(draft, task_source_records, step_bindings)
        record = observation["record"]
        pins = WorkflowPins(self.data_dir).list_pins()
        pinned = next((p for p in pins if p["revision"] == record["draft_revision"]), None)
        if pinned is None or pinned["draft"] != observation["draft"]:
            raise ABWorkflowSourceError("source association requires this exact pinned workflow edition")
        old = self._replay()
        if record in old:
            return {"recorded": False, "record": record, "already_present": True}
        if len(old) >= MAX_ENTRIES:
            raise ABWorkflowSourceError("source-link event budget exhausted")
        previous = ""
        if self.path.exists():
            previous = json.loads(self.path.read_text(encoding="utf-8").splitlines()[-1])["hash"]
        envelope = {"parent": previous, "data": record,
                    "hash": digest({"parent": previous, "data": record})}
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(canonical(envelope).decode("utf-8") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        return {"recorded": True, "record": record, "already_present": False}
