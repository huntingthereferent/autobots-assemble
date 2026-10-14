"""Read-only, type-agnostic projection of process editions and admitted jobs.

Worker code, task admission, computation and source verifiers belong elsewhere.
No file or directory is created by this module and no worker is executed.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .workstation import ProcessWorkstation, _safe_id
from .store import WorkspaceStore
from .projection import workspace_view
from .inspections import inspect_handoff


def _editions(workstation: ProcessWorkstation) -> list[dict[str, Any]]:
    """Source-owned editions; no source text or private file paths are returned."""
    root = workstation.root
    if not root.is_dir() or root.is_symlink():
        return []
    records = []
    for worker in sorted(root.iterdir(), key=lambda x: x.name):
        if not worker.is_dir() or worker.is_symlink():
            continue
        try:
            _safe_id(worker.name)
        except ValueError:
            continue
        for edition in sorted(worker.iterdir(), key=lambda x: x.name):
            if not edition.is_dir() or edition.is_symlink():
                continue
            try:
                _safe_id(edition.name)
            except ValueError:
                continue
            item = {"worker_id": worker.name, "version_id": edition.name}
            try:
                folder, original = workstation._read(worker.name, edition.name)
                now = workstation.inspect(worker_id=worker.name, version_id=edition.name)
                item.update({
                    "parent_version": original["parent_version"],
                    "source_fingerprint": original["source_fingerprint"],
                    "current_fingerprint": now["current_fingerprint"],
                    "file_count": len(workstation._inventory_edition(folder)),
                    "modified": now["modified"], "added": now["added"],
                    "deleted": now["deleted"],
                    "source_modified": bool(now["modified"] or now["added"] or now["deleted"]),
                    "state": "AVAILABLE",
                    "executed": False,
                    "verified": False,
                })
            except (OSError, KeyError, TypeError, ValueError) as exc:
                item.update({"state": "UNREADABLE", "reason": type(exc).__name__,
                             "executed": False, "verified": False})
            records.append(item)
    return records


def workstation_snapshot(*, root: str | Path, runtime: Any,
                         workspace_journal: str | Path | None = None) -> dict[str, Any]:
    """Project registered process editions and only genuinely admitted workstation work.

    The payload is intended for an authorized, loopback-only viewer. It never
    upgrades an event-store result to independently reverified evidence.
    """
    desk = ProcessWorkstation(root)
    editions = _editions(desk)
    known = {(row["worker_id"], row["version_id"]): row for row in editions}
    jobs = []
    for handoff in runtime._handoffs.values():
        metadata = handoff.metadata
        if metadata.get("source_system") != "process-workstation" and metadata.get("workstation_worker") is not True:
            continue
        state = runtime.state(handoff.handoff_id)
        worker_id = str(metadata.get("worker_id") or "")
        version_id = str(metadata.get("worker_version") or "")
        edition = known.get((worker_id, version_id))
        pinned = metadata.get("edition_fingerprint")
        if edition is None:
            source_state = "EDITION_NOT_REGISTERED"
        elif edition["state"] != "AVAILABLE":
            source_state = "EDITION_UNREADABLE"
        elif not pinned:
            source_state = "NO_PIN"
        elif edition["current_fingerprint"] != pinned:
            source_state = "SOURCE_CHANGED"
        else:
            source_state = "MATCHES_ADMISSION"
        events = runtime.event_store.for_handoff(handoff.handoff_id)
        jobs.append({
            "job_id": handoff.handoff_id,
            "worker_id": worker_id, "version_id": version_id,
            "title": metadata.get("title") or handoff.required_relation,
            "referent": handoff.referent,
            "required_relation": handoff.required_relation,
            "source_system": metadata.get("source_system"),
            "realization": "simulated" if metadata.get("source_system") == "factory" else "computed",
            "actor_id": handoff.to_actor,
            "status": state.status,
            "source_state": source_state,
            "edition_fingerprint": pinned,
            "missing_witnesses": list(state.missing_witnesses),
            "blocked_by": list(getattr(state, "blocked_by", ())),
            "lane_refs": [p.removeprefix("workspace-lane:") for p in handoff.provenance
                          if p.startswith("workspace-lane:")],
            "result": state.output,
            "inspection": inspect_handoff(handoff, state),
            "evidence": [asdict(item) for item in state.evidence],
            "verification": "recorded-not-reverified" if state.status == "COMPLETE"
                            else "not-complete",
            "events": [{"event_id": getattr(e, "event_id", ""), "event_type": e.event_type,
                        "actor_id": getattr(e, "actor_id", ""), "at": getattr(e, "occurred_at", None),
                        "status": getattr(e, "data", {}).get("status") if e.event_type == "RESULT" else None}
                       for e in events[-20:]],
            "last_event_at": getattr(events[-1], "occurred_at", None) if events else None,
        })
    jobs.sort(key=lambda j: ((j["last_event_at"] or ""), j["job_id"]), reverse=True)
    lanes = {"focused_lane": None, "lanes": [], "connections": []}
    if workspace_journal is not None and Path(workspace_journal).is_file():
        lanes = workspace_view(WorkspaceStore(workspace_journal))
    return {
        "schema_version": 1,
        "read_only": True,
        "worker_execution_triggered": False,
        "runtime_execution_connected_by_view": False,
        "notes": "COMPLETE means a recorded result; this page does not reverify native sources or prove an active process.",
        "editions": editions,
        "jobs": jobs,
        "workspace": lanes,
        "counts": {"workers": len({e["worker_id"] for e in editions}),
                   "editions": len(editions), "jobs": len(jobs),
                   "ready": sum(j["status"] == "READY" for j in jobs),
                   "recorded_complete": sum(j["status"] == "COMPLETE" for j in jobs),
                   "source_changed": sum(j["source_state"] == "SOURCE_CHANGED" for j in jobs)},
    }
