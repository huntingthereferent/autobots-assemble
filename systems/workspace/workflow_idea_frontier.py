"""Bounded idea checklist and strictly local, source-grounded worker perspectives.

Ideas are the existing active MOVE items in TASKS.md, not a new task generator.
A worker can inspect a step and its declared graph neighbors; it can reach
only explicitly associated pinned parent/child/sibling branches of the SAME
idea. Movement backward and cross-worker help are proposals, not execution
or claims of improvement. No scheduler, global worker inventory or telemetry.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import re

from runtime.repository_tasks import read_active_work
from .workflow_pins import WorkflowPins
from .workflow_draft import build_preview

SCHEMA = "workstation-idea-frontier/v1"
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
MAX_IDEAS = 64
MAX_BRANCHES = 256
MAX_EVENTS = 4096
MAX_BYTES = 8_000_000
MAX_FRONTIER = 12


def _sha(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             allow_nan=False, separators=(",", ":")).encode("utf-8")).hexdigest()


def _word(value: object, label: str, max_len: int = 240) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > max_len:
        raise ValueError(f"{label} must be bounded nonempty text")
    return value.strip()


class IdeaFrontier:
    """Local provenance-checked review capability for the existing workflow editor.

    Only the host-facing ideas() result contains all checklist entries. A
    worker_frontier() result cannot enumerate unrelated ideas or branches.
    Caller identity is a local *label*, not cryptographic authentication.
    """

    def __init__(self, repository: str | Path, data_dir: str | Path):
        self.repository = Path(repository).resolve()
        self.data_dir = Path(data_dir).resolve()
        self.path = self.data_dir / "workflow_idea_frontier.jsonl"

    def _active(self) -> dict[str, object]:
        tasks_path = self.repository / "TASKS.md"
        if tasks_path.is_symlink() or not tasks_path.is_file() or tasks_path.stat().st_size > 200_000:
            raise ValueError("existing repository task source unavailable")
        tasks = read_active_work(tasks_path)
        if len(tasks) > MAX_IDEAS:
            raise ValueError("active work exceeds bounded idea view")
        return {x.source_id: x for x in tasks}

    def _pins(self) -> dict[str, dict]:
        pins = WorkflowPins(self.data_dir).list_pins()
        if len(pins) > MAX_BRANCHES:
            raise ValueError("too many pinned workflow branches")
        return {x["revision"]: x for x in pins}

    def _fresh(self, pin: dict) -> None:
        """Current source manifests must still match this exact pinned draft."""
        if build_preview(pin["draft"], self.repository)["revision"] != pin["revision"]:
            raise ValueError("pinned workflow source manifest differs from recorded revision")

    def _read(self) -> list[dict]:
        if not self.path.exists():
            return []
        if self.path.is_symlink() or not self.path.is_file() or self.path.stat().st_size > MAX_BYTES:
            raise ValueError("unsafe or overlarge idea relationship journal")
        parent = ""
        events = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if len(events) >= MAX_EVENTS or not line:
                raise ValueError("invalid idea relationship history length")
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError("malformed idea relationship event") from exc
            if (not isinstance(row, dict) or set(row) != {"parent", "data", "hash"}
                or row["parent"] != parent or not isinstance(row["data"], dict)
                or _sha({"parent": parent, "data": row["data"]}) != row["hash"]):
                raise ValueError("idea relationship journal ancestry/content mismatch")
            data = row["data"]
            if (data.get("schema") != SCHEMA or data.get("type") not in
                    {"BIND", "BACKTRACK_PROPOSED", "HELP_PROPOSED"}):
                raise ValueError("unknown idea journal event type")
            events.append(data)
            parent = row["hash"]
        return events

    def _append(self, item: dict) -> dict:
        events = self._read()
        if item in events:
            return {"recorded": False, "event": item}
        if len(events) >= MAX_EVENTS:
            raise ValueError("idea relationship event budget exceeded")
        parent = ""
        if self.path.exists():
            parent = json.loads(self.path.read_text(encoding="utf-8").splitlines()[-1])["hash"]
        envelope = {"parent": parent, "data": item,
                    "hash": _sha({"parent": parent, "data": item})}
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(envelope, sort_keys=True, ensure_ascii=False,
                                allow_nan=False, separators=(",", ":")) + "\n")
            fp.flush()
            os.fsync(fp.fileno())
        return {"recorded": True, "event": item}

    def _bindings(self) -> dict[str, dict]:
        bindings: dict[str, dict] = {}
        for record in self._read():
            if record["type"] == "BIND":
                rev = record["revision"]
                if rev in bindings and bindings[rev] != record:
                    raise ValueError("conflicting worker/idea binding for pinned revision")
                bindings[rev] = record
        return bindings

    def ideas(self) -> list[dict]:
        """Human checklist: exactly the active recorded tasks, no invented ideas."""
        bindings = self._bindings()
        known_pins = self._pins()
        result = []
        for id_, idea in self._active().items():
            connected = [record for revision, record in bindings.items()
                         if record["idea_id"] == id_ and revision in known_pins]
            result.append({"idea_id": id_, "title": idea.title,
                           "lane": idea.lane, "state": idea.state,
                           "source_link": idea.link, "source_row": idea.row_number,
                           "next_movement": idea.next_movement,
                           "bound_branches": len(connected),
                           "status": "SOURCE_RECORDED_NOT_COMPLETED"})
        return result

    def idea_branches_for_operator(self, idea_id: str) -> list[dict]:
        """Human editor view of just ONE source-recorded idea's bound branches.

        Never wire this inventory method into native workers; workers use only
        worker_frontier(), which reveals first-hop relations.
        """
        if idea_id not in self._active():
            raise ValueError("requested idea is not in current source ledger")
        pins = self._pins()
        bindings = self._bindings()
        result = [
            {"revision": rev, "parent_revision": row["pinned_parent"],
             "worker": row["worker"], "pin_status": pins[rev]["status"],
             "title": pins[rev]["draft"]["title"]}
            for rev, row in bindings.items()
            if row["idea_id"] == idea_id and rev in pins
        ]
        return result[:MAX_BRANCHES]

    def bind(self, *, idea_id: str, revision: str, worker: str, reason: str) -> dict:
        """Explicit association only. Textual similarity NEVER infers a link."""
        idea_id = _word(idea_id, "idea ID", 40)
        if idea_id not in self._active():
            raise ValueError("idea must be a CURRENT source-recorded MOVE row")
        if not isinstance(revision, str) or not _SHA.fullmatch(revision):
            raise ValueError("exact pinned workflow revision required")
        pins = self._pins()
        if revision not in pins:
            raise ValueError("branch must be an existing pinned revision")
        self._fresh(pins[revision])
        worker = _word(worker, "worker label", 64)
        if not _ID.fullmatch(worker):
            raise ValueError("bounded native worker label required")
        reason = _word(reason, "operator's source binding reason")
        bindings = self._bindings()
        parent = pins[revision]["parent_revision"]
        if parent:
            if parent not in pins:
                raise ValueError("pinned ancestor missing")
            self._fresh(pins[parent])
            if parent not in bindings or bindings[parent]["idea_id"] != idea_id:
                raise ValueError("pin's exact parent must be bound to the same idea first")
        record = {"schema": SCHEMA, "type": "BIND", "idea_id": idea_id,
                  "revision": revision, "pinned_parent": parent, "worker": worker,
                  "reason": reason, "relation": "OPERATOR_SELECTED_NOT_VERIFIED",
                  "actor_identity_authenticated": False,
                  "execution_authorized": False}
        if revision in bindings:
            if bindings[revision] != record:
                raise ValueError("pinned revision already bound; cannot silently change idea/owner")
            return {"recorded": False, "event": record}
        return self._append(record)

    def _position(self, *, idea_id: str, revision: str, step_id: str, worker: str):
        active = self._active()
        if idea_id not in active:
            raise ValueError("current idea not present in active source ledger")
        pins = self._pins()
        bindings = self._bindings()
        if revision not in pins or revision not in bindings:
            raise ValueError("current worker branch not explicitly pinned and bound")
        current = bindings[revision]
        if current["idea_id"] != idea_id or current["worker"] != worker:
            raise ValueError("worker has no explicit current task/branch association")
        self._fresh(pins[revision])
        steps = {x["id"]: x for x in pins[revision]["draft"]["steps"]}
        if step_id not in steps:
            raise ValueError("current step not in pinned workflow revision")
        return active[idea_id], pins, bindings, current, steps

    def worker_frontier(self, *, idea_id: str, revision: str,
                        step_id: str, worker: str) -> dict:
        """Only the visible first-hop relations; never an all-workers graph."""
        idea, pins, bindings, current, steps = self._position(
            idea_id=idea_id, revision=revision, step_id=step_id, worker=worker)
        graph = pins[revision]["draft"]
        adjacent = sorted({x["from"] for x in graph["links"] if x["to"] == step_id}
                          | {x["to"] for x in graph["links"] if x["from"] == step_id})
        parent = current["pinned_parent"]
        visible = []
        for related_revision, record in bindings.items():
            if related_revision == revision or record["idea_id"] != idea_id:
                continue
            rel = ("DIRECT_PARENT" if related_revision == parent
                   else "DIRECT_CHILD" if record["pinned_parent"] == revision
                   else "SHARED_PARENT" if parent and record["pinned_parent"] == parent
                   else None)
            if not rel:
                continue
            related = pins.get(related_revision)
            if related is None:
                raise ValueError("bound related revision no longer pinned")
            self._fresh(related)
            # A neighboring worker is visible only through an actual pinned
            # parent/child relation. Return the *boundary*, not its full graph.
            has_step = any(s["id"] == step_id for s in related["draft"]["steps"])
            visible.append({
                "revision": related_revision,
                "relationship": rel, "worker": record["worker"],
                "same_step_id_present": has_step,
                "pin_status": related["status"],
                "quality_superiority_proven": False,
                "execution_authorized": False,
            })
        visible.sort(key=lambda x: (x["relationship"], x["revision"]))
        visible_revisions = {x["revision"] for x in visible[:MAX_FRONTIER]}
        # A peer's help proposal is visible to its TARGET only if the
        # originating branch is directly related and belongs to the same
        # source-recorded idea. Never broadcast to unrelated workers.
        incoming = [
            {"from_worker": e["worker"], "from_revision": e["source_revision"],
             "source_step_id": e["source_step_id"], "reason": e["reason"],
             "relationship": e["witnessed_relation"],
             "state": "PROPOSED_NOT_EXECUTED"}
            for e in self._read()
            if e["type"] == "HELP_PROPOSED" and e["idea_id"] == idea_id
            and e["target_revision"] == revision
            and e["source_revision"] in visible_revisions
        ][:MAX_FRONTIER]
        return {
            "idea": {"idea_id": idea_id, "title": idea.title,
                     "source_link": idea.link, "source_row": idea.row_number},
            "position": {"revision": revision, "worker": worker,
                         "step_id": step_id, "step_label": steps[step_id]["label"],
                         "pinned_parent": parent},
            "visible_steps": [{"id": key, "label": steps[key]["label"]}
                              for key in adjacent[:MAX_FRONTIER]],
            "visible_branches": visible[:MAX_FRONTIER],
            "incoming_peer_help": incoming,
            "other_branches_hidden": max(0, len(visible) - MAX_FRONTIER),
            "claimed_global_worker_visibility": False,
            "current_view_authenticated_as_worker": False,
            "native_relationships_verified": False,
            "only_recorded_first_hop": True,
        }

    def propose(self, *, kind: str, idea_id: str, revision: str,
                step_id: str, worker: str, target_revision: str,
                reason: str) -> dict:
        """Help/backtrack is an explicit movement proposal, never an auto-merge."""
        if kind not in {"HELP", "BACKTRACK"}:
            raise ValueError("unsupported proposal")
        reason = _word(reason, "specific observed reason")
        view = self.worker_frontier(idea_id=idea_id, revision=revision,
                                    step_id=step_id, worker=worker)
        matches = [v for v in view["visible_branches"] if v["revision"] == target_revision]
        if len(matches) != 1:
            raise ValueError("proposed target not visible at this exact worker frontier")
        related = matches[0]
        if kind == "BACKTRACK" and related["relationship"] != "DIRECT_PARENT":
            raise ValueError("backtracking must go to the directly witnessed parent")
        if kind == "HELP" and (
                related["relationship"] not in {"SHARED_PARENT", "DIRECT_CHILD"}
                or related["worker"] == worker):
            raise ValueError("help requires another recorded worker at a visible branch")
        record = {
            "schema": SCHEMA, "type": kind + "_PROPOSED",
            "idea_id": idea_id, "source_revision": revision,
            "source_step_id": step_id, "worker": worker,
            "target_revision": target_revision, "target_worker": related["worker"],
            "witnessed_relation": related["relationship"],
            "reason": reason,
            "branch_superiority_verified": False,
            "worker_help_executed": False,
            "rewind_executed": False,
            "execution_authorized": False,
        }
        return self._append(record)
